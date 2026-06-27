import hashlib
import json
from typing import Any

import httpx
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.llm.ollama_client import ask_ollama
from app.models.email import Email
from app.models.enums import EmailStatus, ExtractionSourceType, ExtractionStatus
from app.models.extraction_run import ExtractionRun
from app.models.job_ad import JobAd
from app.repositories import emails as email_repository
from app.repositories import extraction_runs as extraction_run_repository
from app.repositories import job_ads as job_ad_repository

EMAIL_PROMPT_VERSION = "email_v1"
JOB_AD_PROMPT_VERSION = "job_ad_v1"
EMAIL_REQUIRED_FIELDS = {"status", "company", "role_title", "confidence", "evidence"}
JOB_AD_REQUIRED_FIELDS = {"title", "company", "location", "description", "confidence", "evidence"}


def list_extraction_runs(db: Session) -> list[ExtractionRun]:
    return extraction_run_repository.list_extraction_runs(db)


def extract_email_with_ollama(db: Session, email_id: int) -> ExtractionRun:
    email = email_repository.get_email(db, email_id)
    input_text = _email_input(email)
    prompt = _email_prompt(input_text)
    return _run_ollama_extraction(
        db=db,
        source_type=ExtractionSourceType.EMAIL,
        source_id=email.id,
        prompt_version=EMAIL_PROMPT_VERSION,
        input_text=input_text,
        prompt=prompt,
        apply_result=lambda parsed: _apply_email_result(db, email, parsed),
    )


def extract_job_ad_with_ollama(db: Session, job_ad_id: int) -> ExtractionRun:
    job_ad = job_ad_repository.get_job_ad(db, job_ad_id)
    input_text = _job_ad_input(job_ad)
    prompt = _job_ad_prompt(input_text)
    return _run_ollama_extraction(
        db=db,
        source_type=ExtractionSourceType.JOB_AD,
        source_id=job_ad.id,
        prompt_version=JOB_AD_PROMPT_VERSION,
        input_text=input_text,
        prompt=prompt,
        apply_result=lambda parsed: _apply_job_ad_result(db, job_ad, parsed),
    )


def _run_ollama_extraction(
    *,
    db: Session,
    source_type: ExtractionSourceType,
    source_id: int,
    prompt_version: str,
    input_text: str,
    prompt: str,
    apply_result: Any,
) -> ExtractionRun:
    settings = get_settings()
    input_hash = hashlib.sha256(input_text.encode("utf-8")).hexdigest()

    try:
        raw_output = ask_ollama(prompt)
        parsed = _parse_json_response(raw_output)
        _validate_extraction_payload(parsed, source_type)
        confidence = _optional_float(parsed.get("confidence"))
        apply_result(parsed)
        return extraction_run_repository.create_extraction_run(
            db,
            ExtractionRun(
                source_type=source_type,
                source_id=source_id,
                extractor="ollama",
                model=settings.ollama_model,
                prompt_version=prompt_version,
                raw_input_hash=input_hash,
                raw_output=raw_output,
                parsed_json=parsed,
                confidence=confidence,
                status=ExtractionStatus.SUCCESS,
            ),
        )
    except (httpx.HTTPError, ValueError, KeyError, TypeError) as error:
        extraction_run_repository.create_extraction_run(
            db,
            ExtractionRun(
                source_type=source_type,
                source_id=source_id,
                extractor="ollama",
                model=settings.ollama_model,
                prompt_version=prompt_version,
                raw_input_hash=input_hash,
                raw_output=locals().get("raw_output"),
                parsed_json=None,
                confidence=None,
                status=ExtractionStatus.FAILED,
                error_message=str(error),
            ),
        )
        raise HTTPException(status_code=503, detail=f"Ollama extraction failed: {error}") from error


def _parse_json_response(raw_output: str) -> dict:
    cleaned = raw_output.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`").strip()
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:].strip()

    if not cleaned.startswith("{") or not cleaned.endswith("}"):
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise ValueError("LLM response did not contain a JSON object.")
        cleaned = cleaned[start : end + 1]

    parsed = json.loads(cleaned)
    if not isinstance(parsed, dict):
        raise ValueError("LLM response JSON must be an object.")
    return parsed


def _validate_extraction_payload(parsed: dict, source_type: ExtractionSourceType) -> None:
    required_fields = (
        EMAIL_REQUIRED_FIELDS if source_type == ExtractionSourceType.EMAIL else JOB_AD_REQUIRED_FIELDS
    )
    missing_fields = sorted(required_fields.difference(parsed))
    if missing_fields:
        raise ValueError(f"LLM response is missing required fields: {', '.join(missing_fields)}")

    confidence = _optional_float(parsed.get("confidence"))
    if confidence is None:
        raise ValueError("LLM response confidence must be a number from 0 to 1.")

    evidence = _optional_str(parsed.get("evidence"))
    if evidence is None:
        raise ValueError("LLM response evidence must be a non-empty string.")

    if source_type == ExtractionSourceType.EMAIL:
        status = _optional_str(parsed.get("status"))
        if status not in {item.value for item in EmailStatus}:
            raise ValueError(
                "LLM response status must be one of: pending, rejected, accepted, unknown."
            )

    for field in required_fields - {"confidence", "evidence", "status"}:
        value = parsed.get(field)
        if value is not None and not isinstance(value, str):
            raise ValueError(f"LLM response {field} must be a string or null.")


def _apply_email_result(db: Session, email: Email, parsed: dict) -> None:
    status = _optional_str(parsed.get("status"))
    if status in {item.value for item in EmailStatus}:
        email.email_status = EmailStatus(status)

    company = _optional_str(parsed.get("company"))
    role_title = _optional_str(parsed.get("role_title"))
    confidence = _optional_float(parsed.get("confidence"))

    if company:
        email.extracted_company = company
    if role_title:
        email.extracted_role_title = role_title
    if confidence is not None:
        email.extraction_confidence = confidence

    email_repository.update_email(db, email)


def _apply_job_ad_result(db: Session, job_ad: JobAd, parsed: dict) -> None:
    title = _optional_str(parsed.get("title"))
    company = _optional_str(parsed.get("company"))
    location = _optional_str(parsed.get("location"))
    description = _optional_str(parsed.get("description"))

    if title and _is_blank(job_ad.title):
        job_ad.title = title
    if company and _is_blank(job_ad.company):
        job_ad.company = company
    if location and _is_blank(job_ad.location):
        job_ad.location = location
    if description and _is_blank(job_ad.description):
        job_ad.description = description

    job_ad_repository.update_job_ad(db, job_ad)


def _email_prompt(input_text: str) -> str:
    return f"""
Extract job application facts from this email.
Return exactly one JSON object and no other text.
Required schema:
{{
  "status": "pending" | "rejected" | "accepted" | "unknown",
  "company": string | null,
  "role_title": string | null,
  "confidence": number,
  "evidence": string
}}

Email:
{input_text}
""".strip()


def _job_ad_prompt(input_text: str) -> str:
    return f"""
Extract job advertisement facts from this captured page.
Return exactly one JSON object and no other text.
Required schema:
{{
  "title": string | null,
  "company": string | null,
  "location": string | null,
  "description": string | null,
  "confidence": number,
  "evidence": string
}}

Captured page:
{input_text}
""".strip()


def _email_input(email: Email) -> str:
    return "\n".join(
        [
            f"Subject: {email.subject}",
            f"Sender: {email.sender or ''}",
            "Body:",
            email.body,
        ]
    )


def _job_ad_input(job_ad: JobAd) -> str:
    return "\n".join(
        [
            f"URL: {job_ad.url or ''}",
            f"Page title: {job_ad.page_title or ''}",
            f"Title: {job_ad.title}",
            f"Company: {job_ad.company or ''}",
            f"Location: {job_ad.location or ''}",
            "Selected text:",
            job_ad.selected_text or "",
            "Description:",
            job_ad.description or "",
            "Raw text:",
            (job_ad.raw_text or "")[:8000],
        ]
    )


def _optional_str(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    value = value.strip()
    return value or None


def _optional_float(value: Any) -> float | None:
    if isinstance(value, int | float):
        return max(0.0, min(float(value), 1.0))
    return None


def _is_blank(value: str | None) -> bool:
    return value is None or value.strip() == ""
