"""Main agentic loop — stateless, PipelineGuard-enforced, LLM-driven tool execution."""

import json
import logging
from dataclasses import dataclass, field
from typing import Any, Callable, Optional

from agent_core.enums import (
    ComplianceFailureKey,
    CustomerPayloadKey,
    MessageField,
    MessageRole,
    PipelineEventStatus,
    ToolCallField,
    ToolInputKey,
    ToolName,
    ToolOutputKey,
)
from agent_core.input_sanitizer import InputSanitizer
from agent_core.llm_selector import LLMSelector
from agent_core.pipeline_guard import PipelineGuard, Stage
from agent_core.tools.definitions import TOOL_DEFINITIONS
from agent_core.tools.executor import execute_tool

logger = logging.getLogger(__name__)

MAX_ITERATIONS = 20
MAX_TOOL_RESULT_CHARS = 12_000

_sanitizer = InputSanitizer()


@dataclass
class OrchestratorResult:
    """Structured result returned by orchestrator.run()."""

    success: bool
    messages: list[dict[str, Any]]
    final_stage: str
    provider: str = ""
    error: Optional[str] = None
    data: dict[str, Any] = field(default_factory=dict)


def _truncate(result: dict) -> dict:
    serialized = json.dumps(result)
    if len(serialized) <= MAX_TOOL_RESULT_CHARS:
        return result
    return {
        ToolOutputKey.TRUNCATED.value: True,
        ToolOutputKey.PREVIEW.value: serialized[:MAX_TOOL_RESULT_CHARS] + " [TRUNCATED]",
    }


class Orchestrator:
    """Runs the agent pipeline loop for a single RM query."""

    def __init__(
        self,
        llm_selector: Optional[LLMSelector] = None,
        stage_callback: Optional[Callable[[str, str, dict], None]] = None,
    ) -> None:
        self._llm = llm_selector or LLMSelector()
        self._stage_callback = stage_callback

    def run(
        self,
        query: str,
        rm_id: str,
        campaign_id: Optional[str] = None,
    ) -> OrchestratorResult:
        """
        Execute the agent pipeline for an RM query.

        Parameters:
            query: Raw RM natural-language query.
            rm_id: UUID string of the authenticated RM.
            campaign_id: Optional campaign UUID for finalize_results.

        Returns:
            OrchestratorResult with pipeline outcome.
        """
        sanitized = _sanitizer.sanitize(query)
        if not sanitized.ok:
            return OrchestratorResult(
                success=False,
                messages=[],
                final_stage=Stage.INIT.name,
                error=sanitized.error,
            )

        guard = PipelineGuard()
        messages: list[dict[str, Any]] = [
            {
                MessageField.ROLE.value: MessageRole.SYSTEM.value,
                MessageField.CONTENT.value: (
                    "You are BankIQ, a premium AI CRM assistant for banking Relationship Managers (RMs).\n\n"
                    "Core Guidelines:\n"
                    "1. Process target queries by utilizing our backend pipeline stages in order: search_customers → get_transaction_history → calculate_conversion_score → check_regulatory_compliance → generate_messages → finalize_results.\n"
                    "2. Enforce regulatory compliance strictly. Never draft outreach messages or finalize results without verifying compliance (KYC, DNC, active disputes, and consent flags).\n"
                    "3. Professional Style: Always speak in polished, professional, natural banking and business language. NEVER output Python code blocks, raw markdown code snippets, placeholder function signatures (like `search_customers(...)`), or technical logging. RM users are finance professionals, not programmers. Present all workflows, explanations, and summaries as structured, high-level business briefings, elegant bullet lists, or tables.\n"
                    "4. Conversational Queries: If asked conversational questions (e.g. who you are, how you can help), introduce yourself warmly as BankIQ, and describe your automated analysis capabilities (Search, Portfolio History, Credit Scoring, Compliance Screening, and Draft Message Generation) using clear executive-level business language."
                ),
            },
            {MessageField.ROLE.value: MessageRole.USER.value, MessageField.CONTENT.value: sanitized.text},
        ]

        self._emit_stage(Stage.INIT.name, PipelineEventStatus.STARTED, {})
        provider = ""
        tool_context: dict[str, Any] = {
            ToolInputKey.RM_ID.value: rm_id,
            ToolInputKey.CAMPAIGN_ID.value: campaign_id,
        }
        collected_ids: list[str] = []
        approved_ids: list[str] = []
        scores: dict[str, float] = {}
        generated_messages: dict[str, str] = {}

        for iteration in range(MAX_ITERATIONS):
            if guard.current == Stage.DONE:
                break

            try:
                response = self._llm.complete_with_failover(messages, TOOL_DEFINITIONS)
                provider = response.provider
            except RuntimeError as exc:
                return OrchestratorResult(
                    success=False,
                    messages=messages,
                    final_stage=guard.current.name,
                    error=str(exc),
                )

            if response.content:
                messages.append(
                    {
                        MessageField.ROLE.value: MessageRole.ASSISTANT.value,
                        MessageField.CONTENT.value: response.content,
                    }
                )

            if not response.tool_calls:
                if guard.current == Stage.INIT:
                    query_lower = query.lower()
                    campaign_keywords = [
                        "find", "search", "get", "target", "filter", "select", "leads", "customer", 
                        "income", "cibil", "credit", "score", "emi", "kyc", "dnc", "consent", 
                        "dispute", "loan", "portfolio", "campaign"
                    ]
                    if any(kw in query_lower for kw in campaign_keywords):
                        final_text = self._run_full_deterministic_pipeline(guard, tool_context, query)
                        if (
                            messages
                            and messages[-1][MessageField.ROLE.value] == MessageRole.ASSISTANT.value
                        ):
                            messages[-1][MessageField.CONTENT.value] = final_text
                        else:
                            messages.append(
                                {
                                    MessageField.ROLE.value: MessageRole.ASSISTANT.value,
                                    MessageField.CONTENT.value: final_text,
                                }
                            )
                        guard.current = Stage.DONE
                        break
                    else:
                        guard.current = Stage.DONE
                        break
                elif guard.current.value >= Stage.COMPLIANCE.value:
                    self._run_deterministic_pipeline(guard, tool_context, collected_ids)
                break

            for tc in response.tool_calls:
                raw_tool_name = tc[ToolCallField.NAME.value]
                try:
                    tool_name = ToolName(raw_tool_name)
                except ValueError:
                    messages.append(
                        {
                            MessageField.ROLE.value: MessageRole.TOOL.value,
                            MessageField.TOOL_CALL_ID.value: tc.get(
                                ToolCallField.ID.value,
                                raw_tool_name,
                            ),
                            MessageField.NAME.value: raw_tool_name,
                            MessageField.CONTENT.value: json.dumps(
                                {ToolOutputKey.ERROR.value: f"Unknown tool: {raw_tool_name}"}
                            ),
                        }
                    )
                    continue
                try:
                    tool_input = json.loads(tc.get(ToolCallField.ARGUMENTS.value, "{}"))
                except json.JSONDecodeError:
                    tool_input = {}
                tool_input.setdefault(ToolInputKey.RM_ID.value, rm_id)
                if campaign_id:
                    tool_input.setdefault(ToolInputKey.CAMPAIGN_ID.value, campaign_id)

                if tool_name == ToolName.GET_TRANSACTION_HISTORY and collected_ids:
                    tool_input.setdefault(ToolInputKey.CUSTOMER_IDS.value, collected_ids)
                if tool_name in (
                    ToolName.CALCULATE_CONVERSION_SCORE,
                    ToolName.CHECK_REGULATORY_COMPLIANCE,
                ):
                    tool_input.setdefault(ToolInputKey.CUSTOMER_IDS.value, collected_ids)
                if tool_name == ToolName.GENERATE_MESSAGES:
                    tool_input.setdefault(ToolInputKey.APPROVED_CUSTOMER_IDS.value, approved_ids)
                    tool_input.setdefault(ToolOutputKey.SCORES.value, scores)
                if tool_name == ToolName.FINALIZE_RESULTS:
                    tool_input.setdefault(ToolInputKey.APPROVED_CUSTOMER_IDS.value, approved_ids)
                    tool_input.setdefault(ToolInputKey.MESSAGES.value, generated_messages)

                result = execute_tool(tool_name, tool_input, guard=guard)
                result = _truncate(result)
                logger.info(
                    "Tool result tool=%s stage=%s iteration=%d",
                    tool_name.value,
                    guard.current.name,
                    iteration,
                )
                self._emit_stage(
                    guard.current.name,
                    PipelineEventStatus.COMPLETED,
                    {ToolOutputKey.TOOL.value: tool_name.value},
                )

                if (
                    tool_name == ToolName.SEARCH_CUSTOMERS
                    and ToolOutputKey.CUSTOMERS.value in result
                ):
                    collected_ids = [
                        c[CustomerPayloadKey.ID.value]
                        for c in result[ToolOutputKey.CUSTOMERS.value]
                    ]
                    tool_context[ToolInputKey.CUSTOMER_IDS.value] = collected_ids
                if (
                    tool_name == ToolName.CALCULATE_CONVERSION_SCORE
                    and ToolOutputKey.SCORES.value in result
                ):
                    scores = result[ToolOutputKey.SCORES.value]
                if (
                    tool_name == ToolName.CHECK_REGULATORY_COMPLIANCE
                    and ToolOutputKey.APPROVED.value in result
                ):
                    approved_ids = result[ToolOutputKey.APPROVED.value]
                if (
                    tool_name == ToolName.GENERATE_MESSAGES
                    and ToolInputKey.MESSAGES.value in result
                ):
                    generated_messages = result[ToolInputKey.MESSAGES.value]

                messages.append(
                    {
                        MessageField.ROLE.value: MessageRole.TOOL.value,
                        MessageField.TOOL_CALL_ID.value: tc.get(
                            ToolCallField.ID.value,
                            tool_name.value,
                        ),
                        MessageField.NAME.value: tool_name.value,
                        MessageField.CONTENT.value: json.dumps(result),
                    }
                )

        self._emit_stage(Stage.DONE.name, PipelineEventStatus.COMPLETED, {})
        if guard.current == Stage.FINALIZE:
            guard.advance(Stage.DONE)

        return OrchestratorResult(
            success=True,
            messages=messages,
            final_stage=guard.current.name,
            provider=provider,
            data={ToolInputKey.CUSTOMER_IDS.value: collected_ids},
        )

    def _run_deterministic_pipeline(
        self,
        guard: PipelineGuard,
        ctx: dict[str, Any],
        customer_ids: list[str],
    ) -> None:
        """Fallback deterministic tool chain when LLM returns no tool calls."""
        if not customer_ids:
            return
        steps = [
            (ToolName.GET_TRANSACTION_HISTORY, {ToolInputKey.CUSTOMER_IDS.value: customer_ids, **ctx}),
            (
                ToolName.CALCULATE_CONVERSION_SCORE,
                {ToolInputKey.CUSTOMER_IDS.value: customer_ids, **ctx},
            ),
            (
                ToolName.CHECK_REGULATORY_COMPLIANCE,
                {ToolInputKey.CUSTOMER_IDS.value: customer_ids, **ctx},
            ),
        ]
        approved: list[str] = []
        scores: dict[str, float] = {}
        for name, inputs in steps:
            result = execute_tool(name, inputs, guard=guard)
            self._emit_stage(
                guard.current.name,
                PipelineEventStatus.COMPLETED,
                {ToolOutputKey.TOOL.value: name.value, ToolOutputKey.FALLBACK.value: True},
            )
            if name == ToolName.CALCULATE_CONVERSION_SCORE:
                scores = result.get(ToolOutputKey.SCORES.value, {})
            if name == ToolName.CHECK_REGULATORY_COMPLIANCE:
                approved = result.get(ToolOutputKey.APPROVED.value, [])

        if approved and Stage.COMPLIANCE in guard.visited:
            message_result = execute_tool(
                ToolName.GENERATE_MESSAGES,
                {
                    **ctx,
                    ToolInputKey.APPROVED_CUSTOMER_IDS.value: approved,
                    ToolOutputKey.SCORES.value: scores,
                },
                guard=guard,
            )
            self._emit_stage(
                guard.current.name,
                PipelineEventStatus.COMPLETED,
                {
                    ToolOutputKey.TOOL.value: ToolName.GENERATE_MESSAGES.value,
                    ToolOutputKey.FALLBACK.value: True,
                },
            )
            finalize_inputs = {
                **ctx,
                ToolInputKey.APPROVED_CUSTOMER_IDS.value: approved,
                ToolInputKey.MESSAGES.value: message_result.get(ToolInputKey.MESSAGES.value, {}),
            }
            execute_tool(ToolName.FINALIZE_RESULTS, finalize_inputs, guard=guard)
            self._emit_stage(
                guard.current.name,
                PipelineEventStatus.COMPLETED,
                {ToolOutputKey.TOOL.value: ToolName.FINALIZE_RESULTS.value},
            )

    def _emit_stage(self, stage: str, status: PipelineEventStatus | str, data: dict) -> None:
        if self._stage_callback:
            event_status = status.value if isinstance(status, PipelineEventStatus) else status
            self._stage_callback(stage, event_status, data)

    def _parse_search_criteria(self, query: str) -> dict[str, Any]:
        criteria = {
            ToolInputKey.MIN_INCOME.value: 1200000.0,
            ToolInputKey.MIN_CREDIT_SCORE.value: 720,
            ToolInputKey.MAX_EMI_RATIO.value: 0.35,
        }
        
        import re
        
        # Match income (e.g. "12 lakh", "12 lakhs", "1200000", "12,000,000", "15 lakhs")
        income_match = re.search(
            r'(?:income\s+(?:above|>=|>)\s*(?:₹|rs\.?)?\s*(\d+(?:\.\d+)?)\s*(?:lakh|lakhs|l)?|min(?:imum)?\s+income\s+of\s*(?:₹|rs\.?)?\s*(\d+(?:\.\d+)?)\s*(?:lakh|lakhs|l)?)',
            query,
            re.IGNORECASE,
        )
        if income_match:
            val = income_match.group(1) or income_match.group(2)
            try:
                criteria[ToolInputKey.MIN_INCOME.value] = float(val) * 100_000.0
            except ValueError:
                pass
        else:
            # Check raw digits like "1200000" or "1,200,000"
            digits_match = re.search(
                r'income\s+(?:above|>=|>)\s*(?:₹|rs\.?)?\s*(\d{2,3}(?:,\d{2,3})*(?:,\d{3})*)',
                query,
                re.IGNORECASE,
            )
            if digits_match:
                try:
                    criteria[ToolInputKey.MIN_INCOME.value] = float(
                        digits_match.group(1).replace(",", "")
                    )
                except ValueError:
                    pass

        # Match CIBIL/credit score (e.g. "cibil score of 720+", "720 or higher", "cibil >= 720")
        credit_match = re.search(
            r'(?:cibil|credit|score).*?(\d{3})',
            query,
            re.IGNORECASE,
        )
        if credit_match:
            try:
                criteria[ToolInputKey.MIN_CREDIT_SCORE.value] = int(credit_match.group(1))
            except ValueError:
                pass

        # Match EMI ratio (e.g. "emi below 35%", "emi below 0.35", etc.)
        emi_match = re.search(
            r'(?:emi|debt|installment).*?(\d{2}(?:\.\d+)?)\s*%',
            query,
            re.IGNORECASE,
        )
        if emi_match:
            try:
                criteria[ToolInputKey.MAX_EMI_RATIO.value] = float(emi_match.group(1)) / 100.0
            except ValueError:
                pass
        else:
            emi_decimal = re.search(
                r'(?:emi|debt|installment).*?(?:below|<=|<)\s*(0\.\d+)',
                query,
                re.IGNORECASE,
            )
            if emi_decimal:
                try:
                    criteria[ToolInputKey.MAX_EMI_RATIO.value] = float(emi_decimal.group(1))
                except ValueError:
                    pass

        return criteria

    def _run_full_deterministic_pipeline(
        self,
        guard: PipelineGuard,
        ctx: dict[str, Any],
        query: str,
    ) -> str:
        """Run the full tool chain deterministically starting from search_customers."""
        # 1. Parse search criteria from the query
        criteria = self._parse_search_criteria(query)
        criteria[ToolInputKey.RM_ID.value] = ctx[ToolInputKey.RM_ID.value]

        # 2. Search customers
        self._emit_stage(Stage.SEARCH.name, PipelineEventStatus.STARTED, {})
        search_result = execute_tool(ToolName.SEARCH_CUSTOMERS, criteria, guard=guard)
        customers = search_result.get(ToolOutputKey.CUSTOMERS.value, [])
        self._emit_stage(
            Stage.SEARCH.name,
            PipelineEventStatus.COMPLETED,
            {
                ToolOutputKey.TOOL.value: ToolName.SEARCH_CUSTOMERS.value,
                ToolOutputKey.FALLBACK.value: True,
            },
        )

        if not customers:
            return (
                "**No eligible customers found**\n\n"
                "I searched your portfolio but found no customers matching these criteria:\n"
                f"* Minimum Income: ₹{criteria[ToolInputKey.MIN_INCOME.value]/100000:.1f} Lakhs\n"
                f"* Minimum CIBIL Score: {criteria[ToolInputKey.MIN_CREDIT_SCORE.value]}\n"
                f"* Maximum EMI Ratio: {criteria[ToolInputKey.MAX_EMI_RATIO.value]*100:.1f}%\n"
            )

        customer_ids = [c[CustomerPayloadKey.ID.value] for c in customers]

        # 3. Get transaction history
        self._emit_stage(Stage.FETCH_HISTORY.name, PipelineEventStatus.STARTED, {})
        execute_tool(
            ToolName.GET_TRANSACTION_HISTORY,
            {ToolInputKey.CUSTOMER_IDS.value: customer_ids, **ctx},
            guard=guard,
        )
        self._emit_stage(
            Stage.FETCH_HISTORY.name,
            PipelineEventStatus.COMPLETED,
            {
                ToolOutputKey.TOOL.value: ToolName.GET_TRANSACTION_HISTORY.value,
                ToolOutputKey.FALLBACK.value: True,
            },
        )

        # 4. Calculate conversion score
        self._emit_stage(Stage.SCORE.name, PipelineEventStatus.STARTED, {})
        scores_result = execute_tool(
            ToolName.CALCULATE_CONVERSION_SCORE,
            {ToolInputKey.CUSTOMER_IDS.value: customer_ids, **ctx},
            guard=guard,
        )
        scores = scores_result.get(ToolOutputKey.SCORES.value, {})
        self._emit_stage(
            Stage.SCORE.name,
            PipelineEventStatus.COMPLETED,
            {
                ToolOutputKey.TOOL.value: ToolName.CALCULATE_CONVERSION_SCORE.value,
                ToolOutputKey.FALLBACK.value: True,
            },
        )

        # 5. Check regulatory compliance
        self._emit_stage(Stage.COMPLIANCE.name, PipelineEventStatus.STARTED, {})
        compliance_result = execute_tool(
            ToolName.CHECK_REGULATORY_COMPLIANCE,
            {ToolInputKey.CUSTOMER_IDS.value: customer_ids, **ctx},
            guard=guard,
        )
        approved_ids = compliance_result.get(ToolOutputKey.APPROVED.value, [])
        rejected = compliance_result.get(ToolOutputKey.REJECTED.value, [])
        self._emit_stage(
            Stage.COMPLIANCE.name,
            PipelineEventStatus.COMPLETED,
            {
                ToolOutputKey.TOOL.value: ToolName.CHECK_REGULATORY_COMPLIANCE.value,
                ToolOutputKey.FALLBACK.value: True,
            },
        )

        # 6. Generate messages
        self._emit_stage(Stage.GENERATE_MESSAGES.name, PipelineEventStatus.STARTED, {})
        approved_customers = [c for c in customers if c[CustomerPayloadKey.ID.value] in approved_ids]
        message_result = execute_tool(
            ToolName.GENERATE_MESSAGES,
            {
                **ctx,
                ToolInputKey.APPROVED_CUSTOMER_IDS.value: approved_ids,
                ToolOutputKey.SCORES.value: scores,
            },
            guard=guard,
        )
        messages_dict = message_result.get(ToolInputKey.MESSAGES.value, {})
        recommendations = message_result.get("recommendations", {})
        self._emit_stage(
            Stage.GENERATE_MESSAGES.name,
            PipelineEventStatus.COMPLETED,
            {
                ToolOutputKey.TOOL.value: ToolName.GENERATE_MESSAGES.value,
                ToolOutputKey.FALLBACK.value: True,
            },
        )

        # 7. Finalize results
        self._emit_stage(Stage.FINALIZE.name, PipelineEventStatus.STARTED, {})
        finalize_inputs = {
            **ctx,
            ToolInputKey.APPROVED_CUSTOMER_IDS.value: approved_ids,
            ToolInputKey.MESSAGES.value: messages_dict,
            ToolInputKey.REJECTED_COUNT.value: len(rejected),
        }
        execute_tool(ToolName.FINALIZE_RESULTS, finalize_inputs, guard=guard)
        self._emit_stage(
            Stage.FINALIZE.name,
            PipelineEventStatus.COMPLETED,
            {
                ToolOutputKey.TOOL.value: ToolName.FINALIZE_RESULTS.value,
                ToolOutputKey.FALLBACK.value: True,
            },
        )

        # Build a highly structured, data-dense GFM Markdown dashboard programmatically to guarantee 100% accuracy and prevent any LLM laziness or truncations.
        output = []
        output.append("### Premium Campaign Report")
        output.append(
            "\nWe are thrilled to present your high-value campaign leads! After carefully reviewing your portfolio "
            "using the requested target criteria, our multi-stage compliance and analysis engine selected a "
            "highly qualified group of candidate relationship profiles. These leads possess strong credit ratings, "
            "manageable debt profiles, and high conversion likelihoods."
        )
        
        output.append("\n#### Campaign Execution Summary")
        output.append(f"* **Total Leads Screened:** **{len(customer_ids)}**")
        output.append(f"* **Compliant & Approved Leads:** **{len(approved_ids)}**")
        output.append(f"* **Excluded Leads (Failed Compliance/DNC):** **{len(rejected)}**")
        
        output.append("\n#### Approved Customer Campaign Dashboard")
        output.append("")
        output.append("| Candidate Details | Financial Profile | Debt & Score | Actionable Outreach Message Draft |")
        output.append("| :--- | :--- | :--- | :--- |")
        
        for c in approved_customers:
            cid = c[CustomerPayloadKey.ID.value]
            score = scores.get(cid, 75.0)
            rec = recommendations.get(cid, {})
            msg = messages_dict.get(cid, "")
            
            cand_details = f"**{c[CustomerPayloadKey.NAME.value]}**<br><span style='font-size: 10px; color: #64748b;'>Age: {c[CustomerPayloadKey.AGE.value]} · KYC: {c[CustomerPayloadKey.KYC_STATUS.value]}</span>"
            fin_profile = f"Income: ₹{float(c[CustomerPayloadKey.ANNUAL_INCOME.value])/100000:.1f}L<br>CIBIL: **{c[CustomerPayloadKey.CREDIT_SCORE.value]}**"
            debt_score = f"EMI: {float(c[CustomerPayloadKey.EMI_RATIO.value])*100:.1f}%<br>Score: **{score:.1f}**"
            draft_msg = f"**{rec.get('product', 'Personal Loan')}**<br><span style='font-size: 11px; color: #475569;'>*\"{msg}\"*</span>"
            
            output.append(f"| {cand_details} | {fin_profile} | {debt_score} | {draft_msg} |")
            
        if rejected:
            output.append("\n#### Excluded Candidates (Failed Compliance)")
            for i, r in enumerate(rejected, 1):
                cust = next(
                    (
                        c
                        for c in customers
                        if c[CustomerPayloadKey.ID.value]
                        == r[ComplianceFailureKey.CUSTOMER_ID.value]
                    ),
                    None,
                )
                name = cust[CustomerPayloadKey.NAME.value] if cust else "Unknown Customer"
                output.append(
                    f"{i}. **{name}** — Rejected: *{r[ComplianceFailureKey.REASON.value]}* (Check: {r[ComplianceFailureKey.CHECK.value]})"
                )
        else:
            output.append("\n#### Excluded Candidates (Failed Compliance)")
            output.append("No candidates were excluded. 100% of targeted portfolio leads met all compliance and regulatory criteria.")

        output.append(
            "\n*All message drafts are tailored to each customer's specific profile and compliance consent parameters. "
            "Please copy the drafts directly to send outreach or discuss next steps with your Relationship Manager team.*"
        )
        
        return "\n".join(output)


def run(
    query: str,
    rm_id: str,
    campaign_id: Optional[str] = None,
    stage_callback: Optional[Callable[[str, str, dict], None]] = None,
) -> OrchestratorResult:
    """Module-level entry point for the agent pipeline."""
    return Orchestrator(stage_callback=stage_callback).run(
        query=query,
        rm_id=rm_id,
        campaign_id=campaign_id,
    )
