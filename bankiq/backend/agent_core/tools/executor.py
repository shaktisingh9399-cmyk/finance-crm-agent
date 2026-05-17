"""Agent tool implementations — all accept dict input and return dict output."""

import logging
from decimal import Decimal
from typing import Any, Callable
from uuid import UUID

from agent_core.enums import (
    ComplianceCheckName,
    ComplianceFailureKey,
    CustomerPayloadKey,
    ToolInputKey,
    ToolName,
    ToolOutputKey,
    TransactionPayloadKey,
)
from agent_core.pipeline_guard import PipelineGuard
from agent_core.tools.pii_masker import PIIMasker

logger = logging.getLogger(__name__)

_masker = PIIMasker()
BATCH_SIZE = 500

_COMPLIANCE_CHECKS: list[tuple[ComplianceCheckName, Callable[[Any], tuple[bool, str]]]] = []


def _chunk(ids: list[str], size: int = BATCH_SIZE) -> list[list[str]]:
    return [ids[i : i + size] for i in range(0, len(ids), size)]


def _stable_id(customer_id: str) -> str:
    return PIIMasker.stable_id(customer_id)


def _customer_to_dict(customer: Any) -> dict[str, Any]:
    return {
        CustomerPayloadKey.ID.value: str(customer.id),
        CustomerPayloadKey.NAME.value: customer.name,
        CustomerPayloadKey.PHONE.value: customer.phone,
        CustomerPayloadKey.EMAIL.value: customer.email,
        CustomerPayloadKey.PAN.value: customer.pan,
        CustomerPayloadKey.AADHAAR.value: customer.aadhaar,
        CustomerPayloadKey.ACCOUNT_NUMBER.value: customer.account_number,
        CustomerPayloadKey.ANNUAL_INCOME.value: str(customer.annual_income),
        CustomerPayloadKey.CREDIT_SCORE.value: customer.credit_score,
        CustomerPayloadKey.EMI_RATIO.value: str(customer.emi_ratio),
        CustomerPayloadKey.AGE.value: customer.age,
        CustomerPayloadKey.KYC_STATUS.value: customer.kyc_status,
        CustomerPayloadKey.MARKETING_CONSENT.value: customer.marketing_consent,
        CustomerPayloadKey.DO_NOT_CONTACT.value: customer.do_not_contact,
        CustomerPayloadKey.HAS_ACTIVE_DISPUTE.value: customer.has_active_dispute,
        CustomerPayloadKey.SAVINGS_BALANCE.value: str(customer.savings_balance),
        CustomerPayloadKey.LAST_LOGIN.value: (
            customer.last_login.isoformat() if customer.last_login else None
        ),
    }


def search_customers(inputs: dict) -> dict:
    """
    Search customers in RM portfolio by indexed filters.

    Parameters:
        inputs: Dict with rm_id, optional min_income, min_credit_score, max_emi_ratio, limit.

    Returns:
        Dict with customers list (PII masked) and count.
    """
    from apps.customers.models import Customer

    rm_id = inputs.get(ToolInputKey.RM_ID.value)
    if not rm_id:
        return {ToolOutputKey.ERROR.value: "rm_id is required"}

    qs = Customer.objects.filter(rm_id=rm_id, do_not_contact=False)
    min_income = inputs.get(ToolInputKey.MIN_INCOME.value)
    if min_income is not None:
        qs = qs.filter(annual_income__gte=Decimal(str(min_income)))
    min_credit = inputs.get(ToolInputKey.MIN_CREDIT_SCORE.value)
    if min_credit is not None:
        qs = qs.filter(credit_score__gte=int(min_credit))
    max_emi = inputs.get(ToolInputKey.MAX_EMI_RATIO.value)
    if max_emi is not None:
        qs = qs.filter(emi_ratio__lte=Decimal(str(max_emi)))

    limit = min(int(inputs.get(ToolInputKey.LIMIT.value, 50)), 500)
    records = [_customer_to_dict(c) for c in qs.select_related("rm")[:limit]]
    masked = _masker.mask_records(records)
    return {ToolOutputKey.CUSTOMERS.value: masked, ToolOutputKey.COUNT.value: len(masked)}


def get_transaction_history(inputs: dict) -> dict:
    """
    Fetch transaction summaries for customer IDs.

    Parameters:
        inputs: Dict with customer_ids list and optional rm_id for scoping.

    Returns:
        Dict mapping customer_id to transaction list.
    """
    from apps.customers.models import Transaction

    customer_ids: list[str] = inputs.get(ToolInputKey.CUSTOMER_IDS.value, [])
    rm_id = inputs.get(ToolInputKey.RM_ID.value)
    history: dict[str, list[dict]] = {}

    for chunk in _chunk(customer_ids):
        qs = Transaction.objects.filter(customer_id__in=chunk).select_related("customer")
        if rm_id:
            qs = qs.filter(customer__rm_id=rm_id)
        for txn in qs.iterator(chunk_size=500):
            cid = str(txn.customer_id)
            history.setdefault(cid, []).append(
                {
                    TransactionPayloadKey.MONTH.value: txn.month.isoformat(),
                    TransactionPayloadKey.TOTAL_DEBIT.value: str(txn.total_debit),
                    TransactionPayloadKey.TOTAL_CREDIT.value: str(txn.total_credit),
                    TransactionPayloadKey.AVG_BALANCE.value: str(txn.avg_balance),
                }
            )
    return {ToolOutputKey.HISTORY.value: history}


def calculate_conversion_score(inputs: dict) -> dict:
    """
    Calculate conversion scores for customer IDs.

    Parameters:
        inputs: Dict with customer_ids and optional rm_id.

    Returns:
        Dict with scores keyed by customer_id.
    """
    from apps.customers.models import Customer

    customer_ids: list[str] = inputs.get(ToolInputKey.CUSTOMER_IDS.value, [])
    rm_id = inputs.get(ToolInputKey.RM_ID.value)
    scores: dict[str, float] = {}

    for chunk in _chunk(customer_ids):
        qs = Customer.objects.filter(id__in=chunk)
        if rm_id:
            qs = qs.filter(rm_id=rm_id)
        for customer in qs.iterator(chunk_size=500):
            income_factor = min(float(customer.annual_income) / 1_200_000, 1.0)
            credit_factor = (customer.credit_score - 300) / 600
            emi_factor = 1.0 - float(customer.emi_ratio)
            score = round((income_factor * 0.3 + credit_factor * 0.4 + emi_factor * 0.3) * 100, 2)
            scores[str(customer.id)] = score

    return {ToolOutputKey.SCORES.value: scores}


def _build_compliance_checks() -> list[tuple[ComplianceCheckName, Callable[[Any], tuple[bool, str]]]]:
    from apps.customers.models import KYCStatus

    return [
        (
            ComplianceCheckName.DNC_REGISTRY,
            lambda c: (not c.do_not_contact, "Customer is on Do-Not-Contact registry"),
        ),
        (
            ComplianceCheckName.ACTIVE_DISPUTE,
            lambda c: (not c.has_active_dispute, "Customer has an active dispute"),
        ),
        (
            ComplianceCheckName.KYC_COMPLETE,
            lambda c: (c.kyc_status == KYCStatus.COMPLETE, "KYC is not complete"),
        ),
        (
            ComplianceCheckName.MIN_AGE,
            lambda c: (c.age >= 18, "Customer is below minimum age"),
        ),
        (
            ComplianceCheckName.CONSENT_FLAG,
            lambda c: (c.marketing_consent, "Marketing consent not granted"),
        ),
    ]


def check_regulatory_compliance(inputs: dict) -> dict:
    """
    Run regulatory compliance checks on customers.

    Parameters:
        inputs: Dict with customer_ids and optional rm_id.

    Returns:
        Dict with approved and rejected customer lists.
    """
    from apps.customers.models import Customer

    customer_ids: list[str] = inputs.get(ToolInputKey.CUSTOMER_IDS.value, [])
    rm_id = inputs.get(ToolInputKey.RM_ID.value)
    checks = _build_compliance_checks()
    approved: list[str] = []
    rejected: list[dict[str, str]] = []

    for chunk in _chunk(customer_ids):
        qs = Customer.objects.filter(id__in=chunk)
        if rm_id:
            qs = qs.filter(rm_id=rm_id)
        for customer in qs.iterator(chunk_size=500):
            cid = str(customer.id)
            passed_all = True
            for check_name, check_fn in checks:
                passed, reason = check_fn(customer)
                if not passed:
                    passed_all = False
                    logger.warning(
                        "Compliance rejected masked_id=%s check=%s",
                        _stable_id(cid),
                        check_name.value,
                    )
                    rejected.append(
                        {
                            ComplianceFailureKey.CUSTOMER_ID.value: cid,
                            ComplianceFailureKey.REASON.value: reason,
                            ComplianceFailureKey.CHECK.value: check_name.value,
                        }
                    )
                    break
            if passed_all:
                approved.append(cid)

    return {ToolOutputKey.APPROVED.value: approved, ToolOutputKey.REJECTED.value: rejected}


def _loan_product_for(customer: Any, score: float) -> dict[str, str]:
    """Choose a personal-loan offer variant from customer profile signals."""
    emi_ratio = float(customer.emi_ratio)
    income = float(customer.annual_income)
    balance = float(customer.savings_balance)

    if score >= 82 and customer.credit_score >= 760 and emi_ratio <= 0.25:
        return {
            "product": "Premium pre-approved personal loan",
            "reason": "strong credit profile, low EMI burden, and high conversion score",
        }
    if balance >= 1_000_000 and income >= 1_200_000:
        return {
            "product": "High-value personal loan with priority processing",
            "reason": "healthy savings balance and high annual income",
        }
    if emi_ratio <= 0.35:
        return {
            "product": "Pre-approved personal loan",
            "reason": "manageable EMI ratio and eligible income profile",
        }
    return {
        "product": "Personal loan eligibility discussion",
        "reason": "eligible profile after compliance checks",
    }


def generate_messages(inputs: dict) -> dict:
    """
    Generate product recommendations and personalized WhatsApp messages.

    Parameters:
        inputs: Dict with approved_customer_ids, optional scores, and optional rm_id.

    Returns:
        Dict with messages and recommendations keyed by customer_id.
    """
    from apps.customers.models import Customer

    approved_ids: list[str] = inputs.get(ToolInputKey.APPROVED_CUSTOMER_IDS.value) or inputs.get(
        ToolInputKey.CUSTOMER_IDS.value,
        [],
    )
    rm_id = inputs.get(ToolInputKey.RM_ID.value)
    raw_scores: dict[str, Any] = inputs.get(ToolOutputKey.SCORES.value, {})
    messages: dict[str, str] = {}
    recommendations: dict[str, dict[str, str | float]] = {}

    for chunk in _chunk(approved_ids):
        qs = Customer.objects.filter(id__in=chunk)
        if rm_id:
            qs = qs.filter(rm_id=rm_id)
        for customer in qs.iterator(chunk_size=500):
            cid = str(customer.id)
            score = float(raw_scores.get(cid, 75.0))
            offer = _loan_product_for(customer, score)
            income_lakh = float(customer.annual_income) / 100_000
            emi_percent = float(customer.emi_ratio) * 100
            messages[cid] = (
                f"Hi {customer.name}, based on your banking relationship with BankIQ, "
                f"annual income of about ₹{income_lakh:.1f} lakh, CIBIL score of "
                f"{customer.credit_score}, and current EMI ratio near {emi_percent:.1f}%, "
                f"you may be eligible for our {offer['product']}. Reply YES and your "
                "Relationship Manager will share the next steps. Standard terms apply."
            )
            recommendations[cid] = {
                "product": offer["product"],
                "reason": offer["reason"],
                "conversion_score": score,
            }

    return {ToolInputKey.MESSAGES.value: messages, "recommendations": recommendations}


def finalize_results(inputs: dict) -> dict:
    """
    Finalize campaign results after compliance and message generation.

    Parameters:
        inputs: Dict with approved_customer_ids, messages, campaign_id, rm_id.

    Returns:
        Dict with summary counts and record IDs.
    """
    from apps.campaigns.models import DispatchStatus, OutreachRecord

    approved_ids: list[str] = inputs.get(ToolInputKey.APPROVED_CUSTOMER_IDS.value, [])
    messages: dict[str, str] = inputs.get(ToolInputKey.MESSAGES.value, {})
    campaign_id = inputs.get(ToolInputKey.CAMPAIGN_ID.value)
    records_created = 0

    if campaign_id:
        for chunk in _chunk(approved_ids):
            outreach_batch = []
            for cid in chunk:
                outreach_batch.append(
                    OutreachRecord(
                        campaign_id=campaign_id,
                        customer_id=UUID(cid),
                        message_text=messages.get(cid, ""),
                        dispatch_status=DispatchStatus.APPROVED,
                    )
                )
            OutreachRecord.objects.bulk_create(outreach_batch)
            records_created += len(outreach_batch)

    return {
        ToolOutputKey.APPROVED_COUNT.value: len(approved_ids),
        ToolOutputKey.REJECTED_COUNT.value: int(inputs.get(ToolInputKey.REJECTED_COUNT.value, 0)),
        ToolOutputKey.RECORDS_CREATED.value: records_created,
    }


def execute_tool(
    name: ToolName | str,
    inputs: dict,
    guard: PipelineGuard | None = None,
) -> dict:
    """
    Execute a registered tool by name with pipeline guard enforcement.

    Parameters:
        name: Tool name from TOOL_REGISTRY.
        inputs: Tool input dict.
        guard: Optional PipelineGuard instance.

    Returns:
        Tool result dict or PIPELINE_GUARD_ERROR.
    """
    try:
        tool_name = ToolName(name)
    except ValueError:
        return {ToolOutputKey.ERROR.value: f"Unknown tool: {name}"}

    if guard is not None:
        error = guard.validate_tool(tool_name)
        if error is not None:
            error[ToolOutputKey.CURRENT_STAGE.value] = guard.current.name
            return error

    fn = TOOL_REGISTRY.get(tool_name)
    if fn is None:
        return {ToolOutputKey.ERROR.value: f"Unknown tool: {tool_name.value}"}

    result = fn(inputs)
    if guard is not None and ToolOutputKey.ERROR.value not in result:
        guard.complete_tool(tool_name)
    logger.info(
        "Tool executed name=%s stage=%s",
        tool_name.value,
        guard.current.name if guard else "N/A",
    )
    return result


TOOL_REGISTRY: dict[ToolName, Callable[[dict], dict]] = {
    ToolName.SEARCH_CUSTOMERS: search_customers,
    ToolName.GET_TRANSACTION_HISTORY: get_transaction_history,
    ToolName.CALCULATE_CONVERSION_SCORE: calculate_conversion_score,
    ToolName.CHECK_REGULATORY_COMPLIANCE: check_regulatory_compliance,
    ToolName.GENERATE_MESSAGES: generate_messages,
    ToolName.FINALIZE_RESULTS: finalize_results,
}
