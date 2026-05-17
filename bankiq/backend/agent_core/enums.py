"""Shared agent protocol enums."""

from enum import Enum


class MessageRole(str, Enum):
    """Chat message roles passed between the orchestrator and LLM providers."""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


class PipelineEventStatus(str, Enum):
    """Statuses emitted over the agent pipeline event stream."""

    QUEUED = "queued"
    STARTED = "started"
    COMPLETED = "completed"
    FINISHED = "finished"
    FAILED = "failed"


class ToolName(str, Enum):
    """Registered agent tools exposed to the LLM."""

    SEARCH_CUSTOMERS = "search_customers"
    GET_TRANSACTION_HISTORY = "get_transaction_history"
    CALCULATE_CONVERSION_SCORE = "calculate_conversion_score"
    CHECK_REGULATORY_COMPLIANCE = "check_regulatory_compliance"
    GENERATE_MESSAGES = "generate_messages"
    FINALIZE_RESULTS = "finalize_results"


class PipelineError(str, Enum):
    """Machine-readable pipeline error codes."""

    GUARD_ERROR = "PIPELINE_GUARD_ERROR"
    ERROR_STAGE = "ERROR"


class MessageField(str, Enum):
    """Keys used in chat message payloads."""

    ROLE = "role"
    CONTENT = "content"
    MESSAGE = "message"
    TOOL_CALL_ID = "tool_call_id"
    NAME = "name"


class ToolCallField(str, Enum):
    """Keys received from LLM tool-call payloads."""

    ID = "id"
    NAME = "name"
    ARGUMENTS = "arguments"


class ToolInputKey(str, Enum):
    """Tool input payload keys."""

    RM_ID = "rm_id"
    CAMPAIGN_ID = "campaign_id"
    CUSTOMER_IDS = "customer_ids"
    APPROVED_CUSTOMER_IDS = "approved_customer_ids"
    MESSAGES = "messages"
    REJECTED_COUNT = "rejected_count"
    MIN_INCOME = "min_income"
    MIN_CREDIT_SCORE = "min_credit_score"
    MAX_EMI_RATIO = "max_emi_ratio"
    LIMIT = "limit"


class ToolOutputKey(str, Enum):
    """Tool result payload keys."""

    APPROVED = "approved"
    APPROVED_COUNT = "approved_count"
    COUNT = "count"
    CURRENT_STAGE = "current_stage"
    CUSTOMERS = "customers"
    ERROR = "error"
    FALLBACK = "fallback"
    HISTORY = "history"
    MESSAGE = "message"
    PREVIEW = "preview"
    RECORDS_CREATED = "records_created"
    REJECTED = "rejected"
    REJECTED_COUNT = "rejected_count"
    REQUIRED_STAGE = "required_stage"
    SCORES = "scores"
    TOOL = "tool"
    TRUNCATED = "truncated"


class CustomerPayloadKey(str, Enum):
    """Serialized customer payload keys used by agent tools."""

    AADHAAR = "aadhaar"
    ACCOUNT_NUMBER = "account_number"
    AGE = "age"
    ANNUAL_INCOME = "annual_income"
    CREDIT_SCORE = "credit_score"
    DO_NOT_CONTACT = "do_not_contact"
    EMAIL = "email"
    EMI_RATIO = "emi_ratio"
    HAS_ACTIVE_DISPUTE = "has_active_dispute"
    ID = "id"
    KYC_STATUS = "kyc_status"
    LAST_LOGIN = "last_login"
    MARKETING_CONSENT = "marketing_consent"
    NAME = "name"
    PAN = "pan"
    PHONE = "phone"
    SAVINGS_BALANCE = "savings_balance"


class TransactionPayloadKey(str, Enum):
    """Serialized transaction payload keys used by agent tools."""

    AVG_BALANCE = "avg_balance"
    MONTH = "month"
    TOTAL_CREDIT = "total_credit"
    TOTAL_DEBIT = "total_debit"


class ComplianceCheckName(str, Enum):
    """Machine-readable compliance check identifiers."""

    ACTIVE_DISPUTE = "active_dispute"
    CONSENT_FLAG = "consent_flag"
    DNC_REGISTRY = "dnc_registry"
    KYC_COMPLETE = "kyc_complete"
    MIN_AGE = "min_age"


class ComplianceFailureKey(str, Enum):
    """Keys for a failed compliance check result."""

    CHECK = "check"
    CUSTOMER_ID = "customer_id"
    REASON = "reason"


class PipelinePayloadKey(str, Enum):
    """Keys used in pipeline event and task result payloads."""

    DATA = "data"
    ERROR = "error"
    FINAL_STAGE = "final_stage"
    MESSAGE = "message"
    PROVIDER = "provider"
    STAGE = "stage"
    STATUS = "status"
    SUCCESS = "success"
    TIMESTAMP = "timestamp"


class ChannelEventField(str, Enum):
    """Django Channels group event keys."""

    PAYLOAD = "payload"
    TYPE = "type"


class ChannelEventType(str, Enum):
    """Django Channels event type names."""

    PIPELINE_STAGE = "pipeline.stage"


class ScopeKey(str, Enum):
    """ASGI scope keys used by the websocket stack."""

    KWARGS = "kwargs"
    QUERY_STRING = "query_string"
    URL_ROUTE = "url_route"
    USER = "user"


class QueryParam(str, Enum):
    """Query-string parameter names."""

    TOKEN = "token"


class JwtClaim(str, Enum):
    """JWT claim names."""

    USER_ID = "user_id"


class PIIField(str, Enum):
    """PII customer fields that require masking."""

    AADHAAR = "aadhaar"
    ACCOUNT_NUMBER = "account_number"
    EMAIL = "email"
    NAME = "name"
    PAN = "pan"
    PHONE = "phone"


class PIIMaskStrategy(str, Enum):
    """Masking algorithms for PII fields."""

    AADHAAR = "aadhaar"
    ACCOUNT = "account"
    EMAIL = "email"
    PAN = "pan"
    PARTIAL = "partial"
    PHONE = "phone"


class LLMProvider(str, Enum):
    """Supported LLM provider identifiers."""

    GEMINI = "gemini"
    GROQ = "groq"
    OLLAMA = "ollama"


class LLMRequestKey(str, Enum):
    """Provider request payload keys."""

    MESSAGES = "messages"
    MODEL = "model"
    STREAM = "stream"


class HttpHeader(str, Enum):
    """HTTP header names used by internal clients."""

    CONTENT_TYPE = "Content-Type"


class HttpContentType(str, Enum):
    """HTTP content types used by internal clients."""

    JSON = "application/json"


class HttpMethod(str, Enum):
    """HTTP methods used by internal clients."""

    POST = "POST"


class ToolChoice(str, Enum):
    """LLM tool-choice modes."""

    AUTO = "auto"
