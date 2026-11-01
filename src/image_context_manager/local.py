"""Strict local demonstration schema, NOT a provider API or network client.

The host must call this on its complete canonical message copy just before
mapping/sending. Unknown formats and source drift abort; nothing is sent here.
"""
import base64
import copy
import hashlib
import re

LOCAL_SCHEMA = "icm.integration-demo.v1"


class RequestPlanError(ValueError):
    """Do not send this request until the host resolves the mismatch."""


def _images(messages):
    if not isinstance(messages, list):
        raise RequestPlanError("Expected a list of local messages")
    result = []
    for message in messages:
        if not isinstance(message, dict) or not isinstance(message.get("role"), str) or not isinstance(message.get("content"), list):
            raise RequestPlanError("Invalid local message")
        for content in message["content"]:
            if not isinstance(content, dict):
                raise RequestPlanError("Invalid local content")
            if content.get("type") == "input_text" and set(content) == {"type", "text"} and isinstance(content["text"], str):
                continue
            if content.get("type") != "input_image" or set(content) != {"type", "image_url"}:
                raise RequestPlanError("Unsupported content; map your provider format explicitly")
            url = content["image_url"]
            if not isinstance(url, str) or not re.fullmatch(r"data:image/(png|jpeg);base64,[A-Za-z0-9+/]+={0,2}", url):
                raise RequestPlanError("Only inline PNG/JPEG data URLs are supported")
            try:
                base64.b64decode(url.split(",", 1)[1], validate=True)
            except ValueError as exc:
                raise RequestPlanError("Invalid base64 image") from exc
            result.append(content)
    return result


def inspect_images(messages):
    """Ordered hashes of exact local image URLs, before any replacement."""
    return [{"ordinal": i, "url_sha256": hashlib.sha256(c["image_url"].encode()).hexdigest()}
            for i, c in enumerate(_images(messages))]


def apply_plan(messages, plan, *, generation):
    """Validate the entire plan, then return a deep request copy.

    Plan matches HistoricalImages.plan(). Canonical input is never edited.
    Hashes identify complete inline URLs, not AssetStore original-file hashes.
    No implicit fallback to an unverified input; raise RequestPlanError instead.
    """
    before = inspect_images(messages)
    if not isinstance(plan, dict) or set(plan) != {"generation", "expected_images", "replacements"}:
        raise RequestPlanError("Invalid plan shape")
    if not isinstance(generation, str) or not generation or plan["generation"] != generation:
        raise RequestPlanError("Stale or wrong plan generation")
    if type(plan["expected_images"]) is not int or plan["expected_images"] != len(before):
        raise RequestPlanError("Image count mismatch")
    if not isinstance(plan["replacements"], list):
        raise RequestPlanError("Invalid replacements")
    seen = set()
    for replacement in plan["replacements"]:
        if not isinstance(replacement, dict) or set(replacement) != {"ordinal", "expected_sha256", "reference"}:
            raise RequestPlanError("Invalid replacement shape")
        ordinal = replacement["ordinal"]
        if type(ordinal) is not int or ordinal < 0 or ordinal >= len(before) or ordinal in seen:
            raise RequestPlanError("Invalid or duplicate image ordinal")
        if before[ordinal]["url_sha256"] != replacement["expected_sha256"]:
            raise RequestPlanError("Image source hash mismatch")
        if not isinstance(replacement["reference"], str) or not replacement["reference"].strip():
            raise RequestPlanError("Empty reference")
        seen.add(ordinal)
    output = copy.deepcopy(messages)
    contents = _images(output)
    for replacement in plan["replacements"]:
        content = contents[replacement["ordinal"]]
        content.clear()
        content.update(type="input_text", text=replacement["reference"])
    return output
