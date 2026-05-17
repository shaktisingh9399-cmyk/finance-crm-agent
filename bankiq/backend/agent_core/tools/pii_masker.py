"""PII masking singleton — all customer records must pass through before return."""

import hashlib
import re
from typing import Any

from agent_core.enums import PIIField, PIIMaskStrategy


class PIIMasker:
    """Mask sensitive customer fields using declarative _MASK_MAP rules."""

    _MASK_MAP: dict[PIIField, PIIMaskStrategy] = {
        PIIField.PHONE: PIIMaskStrategy.PHONE,
        PIIField.EMAIL: PIIMaskStrategy.EMAIL,
        PIIField.PAN: PIIMaskStrategy.PAN,
        PIIField.AADHAAR: PIIMaskStrategy.AADHAAR,
        PIIField.ACCOUNT_NUMBER: PIIMaskStrategy.ACCOUNT,
    }

    def mask_record(self, record: dict[str, Any]) -> dict[str, Any]:
        """
        Mask PII fields in a single customer record dict.

        Parameters:
            record: Customer field dict (may be partial).

        Returns:
            Copy of record with masked PII values.
        """
        result = dict(record)
        for field, strategy in self._MASK_MAP.items():
            field_name = field.value
            if field_name not in result or result[field_name] is None:
                continue
            value = str(result[field_name])
            result[field_name] = self._apply(strategy, value)
        return result

    def mask_records(self, records: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Mask PII in a list of customer record dicts."""
        return [self.mask_record(r) for r in records]

    @staticmethod
    def stable_id(raw_id: str) -> str:
        """Deterministic masked identifier for logging."""
        digest = hashlib.sha256(raw_id.encode()).hexdigest()[:12]
        return f"masked_{digest}"

    def _apply(self, strategy: PIIMaskStrategy, value: str) -> str:
        if strategy == PIIMaskStrategy.PARTIAL:
            parts = value.split()
            if len(parts) >= 2:
                return f"{parts[0][0]}*** {parts[-1][0]}***"
            return f"{value[0]}***" if value else "***"
        if strategy == PIIMaskStrategy.PHONE:
            return f"******{value[-4:]}" if len(value) >= 4 else "******"
        if strategy == PIIMaskStrategy.EMAIL:
            local, _, domain = value.partition("@")
            return f"{local[0]}***@{domain}" if domain else "***@***"
        if strategy == PIIMaskStrategy.PAN:
            return f"****{value[-4:]}" if len(value) >= 4 else "****"
        if strategy == PIIMaskStrategy.AADHAAR:
            return f"XXXX-XXXX-{value[-4:]}" if len(value) >= 4 else "XXXX-XXXX-****"
        if strategy == PIIMaskStrategy.ACCOUNT:
            return f"****{value[-4:]}" if len(value) >= 4 else "****"
        return re.sub(r"\S", "*", value)
