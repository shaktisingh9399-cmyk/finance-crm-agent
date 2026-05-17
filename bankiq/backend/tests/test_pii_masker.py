"""Unit tests for PIIMasker field masking."""

from agent_core.tools.pii_masker import PIIMasker


def test_mask_phone() -> None:
    masker = PIIMasker()
    result = masker.mask_record({"phone": "9876543210"})
    assert result["phone"].endswith("3210")
    assert "9876543210" not in result["phone"]


def test_mask_email() -> None:
    masker = PIIMasker()
    result = masker.mask_record({"email": "user@bank.com"})
    assert "@" in result["email"]
    assert "user@bank.com" not in result["email"]


def test_stable_id_is_deterministic() -> None:
    assert PIIMasker.stable_id("abc") == PIIMasker.stable_id("abc")
    assert PIIMasker.stable_id("abc") != PIIMasker.stable_id("xyz")
