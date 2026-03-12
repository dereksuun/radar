import hashlib


def generate_job_hash(
    *,
    source_type: str,
    external_id: str | None,
    title: str,
    company: str,
    url: str,
) -> str:
    base_value = external_id or f"{title.strip()}::{company.strip()}::{url.strip()}"
    composed = f"{source_type.strip()}::{base_value}"
    return hashlib.sha256(composed.encode("utf-8")).hexdigest()
