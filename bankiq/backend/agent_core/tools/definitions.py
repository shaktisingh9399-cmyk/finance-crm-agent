"""Tool JSON schemas exposed to the LLM via LLMSelector."""

from agent_core.enums import ToolInputKey, ToolName

TOOL_DEFINITIONS: list[dict] = [
    {
        "type": "function",
        "function": {
            "name": ToolName.SEARCH_CUSTOMERS.value,
            "description": "Search RM portfolio customers by filters.",
            "parameters": {
                "type": "object",
                "properties": {
                    ToolInputKey.MIN_INCOME.value: {"type": "number"},
                    ToolInputKey.MIN_CREDIT_SCORE.value: {"type": "integer"},
                    ToolInputKey.MAX_EMI_RATIO.value: {"type": "number"},
                    ToolInputKey.LIMIT.value: {"type": "integer", "default": 50},
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": ToolName.GET_TRANSACTION_HISTORY.value,
            "description": "Fetch transaction history for customer IDs.",
            "parameters": {
                "type": "object",
                "properties": {
                    ToolInputKey.CUSTOMER_IDS.value: {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                },
                "required": [ToolInputKey.CUSTOMER_IDS.value],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": ToolName.CALCULATE_CONVERSION_SCORE.value,
            "description": "Score customers for campaign conversion likelihood.",
            "parameters": {
                "type": "object",
                "properties": {
                    ToolInputKey.CUSTOMER_IDS.value: {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                },
                "required": [ToolInputKey.CUSTOMER_IDS.value],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": ToolName.CHECK_REGULATORY_COMPLIANCE.value,
            "description": "Run RBI/TRAI compliance checks on customer IDs.",
            "parameters": {
                "type": "object",
                "properties": {
                    ToolInputKey.CUSTOMER_IDS.value: {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                },
                "required": [ToolInputKey.CUSTOMER_IDS.value],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": ToolName.GENERATE_MESSAGES.value,
            "description": (
                "Recommend a suitable banking product and generate personalized "
                "WhatsApp outreach for compliance-approved customers."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    ToolInputKey.APPROVED_CUSTOMER_IDS.value: {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                    ToolInputKey.CUSTOMER_IDS.value: {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                    "scores": {
                        "type": "object",
                        "description": "Optional precomputed scores keyed by customer ID.",
                        "additionalProperties": {"type": "number"},
                    },
                },
                "required": [ToolInputKey.APPROVED_CUSTOMER_IDS.value],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": ToolName.FINALIZE_RESULTS.value,
            "description": "Finalize approved candidates and messages for the campaign.",
            "parameters": {
                "type": "object",
                "properties": {
                    ToolInputKey.APPROVED_CUSTOMER_IDS.value: {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                    ToolInputKey.MESSAGES.value: {
                        "type": "object",
                        "additionalProperties": {"type": "string"},
                    },
                },
                "required": [ToolInputKey.APPROVED_CUSTOMER_IDS.value],
            },
        },
    },
]
