"""Prepare structured fee display data for templates."""

from __future__ import annotations

import re


def _parse_amount(amount: str) -> int:
    return int(re.sub(r"[^\d]", "", amount))


def _split_amount(amount: str) -> dict:
    m = re.match(r"₹\s*([\d,]+)", (amount or "").strip())
    if m:
        return {"raw": amount, "symbol": "₹", "value": m.group(1)}
    return {"raw": amount, "symbol": "", "value": amount}


def _combined_text(fees: dict) -> str:
    parts: list[str] = []
    for key in ("notes", "plans", "amount_notes"):
        parts.extend(fees.get(key) or [])
    return " ".join(parts).lower()


def _is_dual_plan(fees: dict, text: str) -> bool:
    if any(
        k in text
        for k in (
            "post-placement",
            "post placement",
            "once you secure",
            "once placed",
        )
    ):
        return True
    return any("now and" in (p or "").lower() for p in fees.get("plans") or [])


def _is_discount(fees: dict, text: str) -> bool:
    if any(
        k in text
        for k in (
            "discount",
            " off",
            "minus",
            "limited-time",
            "limited time",
        )
    ):
        return True
    return any(
        re.search(r"flat\s+₹[\d,]+\s+off", p or "", re.I) for p in fees.get("plans") or []
    )


def _plan_amounts(fees: dict) -> tuple[dict | None, dict | None]:
    for plan in fees.get("plans") or []:
        m = re.search(r"pay\s+₹([\d,]+)\s+now\s+and\s+₹([\d,]+)", plan, re.I)
        if m:
            return _split_amount(f"₹{m.group(1)}"), _split_amount(f"₹{m.group(2)}")
    return None, None


def prepare_fee_display(fees: dict | None) -> dict | None:
    """Return fees dict with a ``display`` key describing render mode and parts."""
    if not fees:
        return None

    amounts = fees.get("amounts") or []
    text = _combined_text(fees)
    parsed = [(_split_amount(a), _parse_amount(a)) for a in amounts]

    display: dict = {
        "mode": "notes_only",
        "amounts": [],
    }

    if len(parsed) == 1:
        display["mode"] = "single"
        display["current"] = parsed[0][0]
        return {**fees, "display": display}

    if len(parsed) == 2:
        (a1, n1), (a2, n2) = parsed[0], parsed[1]
        low = a1 if n1 <= n2 else a2
        high = a2 if n1 <= n2 else a1
        low_n, high_n = min(n1, n2), max(n1, n2)

        dual_plan = _is_dual_plan(fees, text)
        discount = _is_discount(fees, text)

        if dual_plan and not discount:
            upfront, post = _plan_amounts(fees)
            if not upfront:
                upfront = a1 if n1 >= n2 else a2
                post = a2 if n1 >= n2 else a1
            display["mode"] = "dual_plan"
            display["upfront"] = upfront
            display["post"] = post
            return {**fees, "display": display}

        if discount and low_n < high_n:
            display["mode"] = "discount"
            display["current"] = low
            display["original"] = high
            display["save"] = _split_amount(f"₹{high_n - low_n:,}")
            return {**fees, "display": display}

        display["mode"] = "dual_tier"
        display["tier_a"] = a1
        display["tier_b"] = a2
        return {**fees, "display": display}

    if len(parsed) > 2:
        display["mode"] = "multi"
        display["amounts"] = [p[0] for p in parsed]
        return {**fees, "display": display}

    return {**fees, "display": display}
