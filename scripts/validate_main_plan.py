#!/usr/bin/env python3
"""Validate an evidence-linked JSON main-image plan before production."""

import argparse
import datetime as dt
import json
import sys
from pathlib import Path


EXPECTED_ROLES = {
    "identity", "usp", "evidence", "trust", "scene", "decision", "promotion"
}
SOURCE_TYPES = {
    "image-visible", "packaging", "user-material", "test-report",
    "certificate", "promotion-terms"
}
CLAIM_STATUSES = {"visible", "confirmed", "pending", "rejected"}
CLAIM_CATEGORIES = {
    "identity", "attribute", "specification", "scene", "performance",
    "efficacy", "certification", "ranking", "promotion"
}
RATIOS = {"1:1": (1, 1), "3:4": (3, 4), "4:5": (4, 5), "9:16": (9, 16), "16:9": (16, 9)}
ABSOLUTE_TERMS = {
    "第一", "全网第一", "顶级", "最好", "绝对", "永久", "100%", "包治", "治疗"
}
PERFORMANCE_HINTS = {
    "防摔", "抗摔", "耐高温", "耐热", "耐温差", "承重", "防水",
    "抗菌", "除菌", "隔热", "无铅", "食品级", "低盐", "低钠",
    "高蛋白", "零添加"
}
PROMOTION_HINTS = {
    "买一送一", "满减", "优惠", "折扣", "券", "限时", "到手价", "秒杀",
    "特价", "赠品", "立减"
}


def visible_length(text: str) -> int:
    return sum(1 for char in text.strip() if not char.isspace())


def parse_date(value: object, field: str, errors: list[str]):
    try:
        return dt.date.fromisoformat(str(value))
    except ValueError:
        errors.append(f"promotion.{field} must use YYYY-MM-DD")
        return None


def validate_claim(claim: dict, image_index, errors: list[str]) -> None:
    claim_id = str(claim.get("id", "")).strip()
    text = str(claim.get("claim", "")).strip()
    category = str(claim.get("category", "")).strip()
    status = str(claim.get("claim_status", "")).strip()
    source_type = str(claim.get("source_type", "")).strip()
    source_ref = str(claim.get("source_ref", "")).strip()
    supported_copy = claim.get("supported_copy", [])

    if not claim_id:
        errors.append(f"image {image_index}: claim id is required")
    if not text:
        errors.append(f"image {image_index}: claim '{claim_id}' text is required")
    if category not in CLAIM_CATEGORIES:
        errors.append(f"image {image_index}: claim '{claim_id}' has invalid category")
    if status not in CLAIM_STATUSES:
        errors.append(f"image {image_index}: claim '{claim_id}' has invalid claim_status")
    if source_type not in SOURCE_TYPES:
        errors.append(f"image {image_index}: claim '{claim_id}' has invalid source_type")
    if status in {"visible", "confirmed"} and not source_ref:
        errors.append(f"image {image_index}: claim '{claim_id}' requires source_ref")
    if not isinstance(supported_copy, list) or not all(
        isinstance(value, str) and value.strip() for value in supported_copy
    ):
        errors.append(f"image {image_index}: claim '{claim_id}' supported_copy must be a string array")
        supported_copy = []
    if status in {"visible", "confirmed"} and not supported_copy:
        errors.append(f"image {image_index}: approved claim '{claim_id}' requires supported_copy")
    normalized_claim = "".join(text.split())
    for value in supported_copy:
        normalized_copy = "".join(value.split())
        if normalized_claim and normalized_copy and (
            normalized_copy not in normalized_claim and normalized_claim not in normalized_copy
        ):
            errors.append(
                f"image {image_index}: supported_copy '{value}' is not directly supported by claim '{claim_id}'"
            )

    if category in {"performance", "efficacy"}:
        if status != "confirmed" or source_type not in {"test-report", "certificate"}:
            errors.append(
                f"image {image_index}: {category} claim '{claim_id}' requires "
                "confirmed test-report/certificate evidence"
            )
    if category == "certification" and (
        status != "confirmed" or source_type not in {"certificate", "packaging"}
    ):
        errors.append(
            f"image {image_index}: certification claim '{claim_id}' requires "
            "confirmed certificate/packaging evidence"
        )
    if category == "ranking" and status in {"visible", "confirmed"}:
        errors.append(f"image {image_index}: ranking claim '{claim_id}' cannot be display-approved")
    if category == "promotion" and (
        status != "confirmed" or source_type != "promotion-terms"
    ):
        errors.append(
            f"image {image_index}: promotion claim '{claim_id}' requires "
            "confirmed promotion-terms evidence"
        )


def validate_display_item(item, field: str, claims_by_id: dict, errors: list[str]):
    if not isinstance(item, dict):
        errors.append(f"{field} must be an object with text and claim_id")
        return "", None
    text = str(item.get("text", "")).strip()
    claim_id = str(item.get("claim_id", "")).strip()
    if not text:
        errors.append(f"{field}.text is required")
    if not claim_id:
        errors.append(f"{field}.claim_id is required")
        return text, None
    claim = claims_by_id.get(claim_id)
    if claim is None:
        errors.append(f"{field} references unknown claim_id '{claim_id}'")
        return text, None
    if claim.get("claim_status") not in {"visible", "confirmed"}:
        errors.append(f"{field} references unapproved claim_id '{claim_id}'")
    supported = [str(value).strip() for value in claim.get("supported_copy", []) if isinstance(value, str)]
    if text not in supported:
        errors.append(f"{field}.text is not an exact supported_copy for claim_id '{claim_id}'")
    return text, claim


def validate_promotion(plan: dict, displayed_promotions: list[tuple[dict, str]], errors: list[str]) -> None:
    if not displayed_promotions:
        return
    promotion = plan.get("promotion")
    required = {"offer", "source_ref", "start_date", "end_date", "scope"}
    if not isinstance(promotion, dict) or promotion.get("verified") is not True:
        errors.append("displayed promotion requires promotion.verified=true and full terms")
        return
    for key in required:
        if not str(promotion.get(key, "")).strip():
            errors.append(f"promotion.{key} is required")
    start = parse_date(promotion.get("start_date"), "start_date", errors)
    end = parse_date(promotion.get("end_date"), "end_date", errors)
    if start and end and end < start:
        errors.append("promotion.end_date must not be earlier than start_date")
    offer = str(promotion.get("offer", "")).strip()
    source_ref = str(promotion.get("source_ref", "")).strip()
    if offer and source_ref and not any(
        text == offer and str(claim.get("source_ref", "")).strip() == source_ref
        for claim, text in displayed_promotions
    ):
        errors.append(
            "promotion.offer and source_ref must match the same actually displayed promotion claim"
        )


def validate(plan: dict) -> list[str]:
    errors: list[str] = []
    images = plan.get("main_images")
    if not isinstance(images, list) or not images:
        return ["main_images must be a non-empty array"]

    expected_count = plan.get("expected_count", 6)
    if not isinstance(expected_count, int) or expected_count < 1:
        errors.append("expected_count must be a positive integer")
    elif len(images) != expected_count:
        errors.append(f"expected {expected_count} main images, found {len(images)}")

    canvas = plan.get("canvas")
    if not isinstance(canvas, dict):
        errors.append("canvas must specify width, height, and required_ratio")
    else:
        width = canvas.get("width")
        height = canvas.get("height")
        ratio = canvas.get("required_ratio")
        if not isinstance(width, int) or not isinstance(height, int) or width < 1 or height < 1:
            errors.append("canvas width and height must be positive integers")
        elif ratio not in RATIOS:
            errors.append(f"canvas.required_ratio must be one of {sorted(RATIOS)}")
        else:
            rw, rh = RATIOS[ratio]
            if width * rh != height * rw:
                errors.append(f"canvas dimensions do not match required_ratio {ratio}")

    seen_indices: set[int] = set()
    seen_focuses: set[str] = set()
    global_claim_ids: set[str] = set()
    displayed_promotions: list[tuple[dict, str]] = []

    for position, image in enumerate(images, start=1):
        if not isinstance(image, dict):
            errors.append(f"main_images[{position}] must be an object")
            continue
        index = image.get("index")
        role = image.get("role")
        focus = str(image.get("focus", "")).strip()

        if not isinstance(index, int) or index < 1:
            errors.append(f"main_images[{position}].index must be a positive integer")
        elif index in seen_indices:
            errors.append(f"duplicate image index: {index}")
        else:
            seen_indices.add(index)
        if role not in EXPECTED_ROLES:
            errors.append(f"image {index}: unknown role '{role}'")
        if not focus:
            errors.append(f"image {index}: focus is required")
        elif focus in seen_focuses:
            errors.append(f"image {index}: duplicate focus '{focus}'")
        else:
            seen_focuses.add(focus)

        claims = image.get("claims")
        if not isinstance(claims, list) or not claims:
            errors.append(f"image {index}: claims must be a non-empty array")
            claims = []
        claims_by_id = {}
        for claim in claims:
            if not isinstance(claim, dict):
                errors.append(f"image {index}: every claim must be an object")
                continue
            validate_claim(claim, index, errors)
            claim_id = str(claim.get("id", "")).strip()
            if claim_id:
                if claim_id in global_claim_ids:
                    errors.append(f"duplicate claim id: {claim_id}")
                global_claim_ids.add(claim_id)
                claims_by_id[claim_id] = claim

        headline_text, headline_claim = validate_display_item(
            image.get("headline"), f"image {index}.headline", claims_by_id, errors
        )
        if headline_text and visible_length(headline_text) > 10:
            errors.append(f"image {index}: headline exceeds 10 visible characters: {headline_text}")

        copy = image.get("copy", [])
        if not isinstance(copy, list):
            errors.append(f"image {index}.copy must be an array")
            copy = []
        display_pairs = [(headline_text, headline_claim)]
        for copy_index, copy_item in enumerate(copy):
            display_pairs.append(validate_display_item(
                copy_item, f"image {index}.copy[{copy_index}]", claims_by_id, errors
            ))

        for text, claim in display_pairs:
            if not text:
                continue
            for term in ABSOLUTE_TERMS:
                if term in text:
                    errors.append(f"image {index}: displayed text contains prohibited term '{term}'")
            if any(term in text for term in PERFORMANCE_HINTS):
                if not claim or claim.get("category") not in {"performance", "efficacy"}:
                    errors.append(
                        f"image {index}: performance-like display text must reference a performance/efficacy claim"
                    )
            if any(term in text for term in PROMOTION_HINTS):
                if not claim or claim.get("category") != "promotion":
                    errors.append(
                        f"image {index}: promotion-like display text must reference a promotion claim"
                    )
            if claim and claim.get("category") == "promotion":
                displayed_promotions.append((claim, text))

        if role == "promotion" and not any(
            claim.get("category") == "promotion" for claim in claims if isinstance(claim, dict)
        ):
            errors.append(f"image {index}: promotion role requires a promotion claim")

    if 1 not in seen_indices:
        errors.append("image index 1 is required for the primary product identity image")
    first = next((image for image in images if image.get("index") == 1), None)
    if first and first.get("role") != "identity":
        errors.append("image 1 should use role 'identity' so the product is clear first")

    validate_promotion(plan, displayed_promotions, errors)
    return sorted(set(errors))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("plan", type=Path, help="Path to a UTF-8 JSON main-image plan")
    args = parser.parse_args()
    try:
        plan = json.loads(args.plan.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: cannot read plan: {exc}", file=sys.stderr)
        return 2
    errors = validate(plan)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(f"OK: validated {len(plan['main_images'])} main-image entries")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
