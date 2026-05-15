from datetime import datetime, timezone
from typing import Any
from urllib.parse import parse_qsl, quote, urlencode, urlsplit, urlunsplit

def graph_quote(value: str) -> str:
    return value.replace("'", "''")

def merge_query(url_or_path: str, values: dict[str, str]) -> str:
    if not values:
        return url_or_path
    parts = urlsplit(url_or_path)
    query = dict(parse_qsl(parts.query, keep_blank_values=True))
    query.update(values)
    return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(query), parts.fragment))

def apply_path_params(path: str, values: dict[str, str]) -> str:
    result = path
    for key, value in values.items():
        result = result.replace("{" + key + "}", quote(value, safe=""))
    if "{" in result or "}" in result:
        raise ValueError(f"Missing path parameter for {path!r}")
    return result

def parse_include(value: str | None, allowed: set[str]) -> list[str]:
    if not value:
        return sorted(allowed)
    requested = [item.strip() for item in value.split(",") if item.strip()]
    unknown = sorted(set(requested) - allowed)
    if unknown:
        raise ValueError(f"Unknown include value(s): {', '.join(unknown)}")
    return requested

def parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)

def days_since(value: str | None, now: datetime | None = None) -> int | None:
    parsed = parse_datetime(value)
    if parsed is None:
        return None
    now = now or datetime.now(timezone.utc)
    return max(0, int((now - parsed).total_seconds() // 86400))

def normalize_managed_device(raw: dict[str, Any], stale_after_days: int = 7, now: datetime | None = None) -> dict[str, Any]:
    age = days_since(raw.get("lastSyncDateTime"), now)
    return {
        "id": raw.get("id"),
        "device_name": raw.get("deviceName"),
        "user_principal_name": raw.get("userPrincipalName"),
        "operating_system": raw.get("operatingSystem"),
        "os_version": raw.get("osVersion"),
        "compliance_state": raw.get("complianceState"),
        "management_agent": raw.get("managementAgent"),
        "last_sync_date_time": raw.get("lastSyncDateTime"),
        "last_sync_age_days": age,
        "stale_sync": age is None or age > stale_after_days,
        "azure_ad_device_id": raw.get("azureADDeviceId"),
        "serial_number": raw.get("serialNumber"),
        "manufacturer": raw.get("manufacturer"),
        "model": raw.get("model"),
    }

def collection_items(payload: Any) -> list[Any]:
    if isinstance(payload, dict) and isinstance(payload.get("value"), list):
        return payload["value"]
    return payload if isinstance(payload, list) else []

def summarize_states(items: list[dict[str, Any]]) -> dict[str, int]:
    summary: dict[str, int] = {}
    for item in items:
        state = str(item.get("state") or item.get("complianceState") or "unknown")
        summary[state] = summary.get(state, 0) + 1
    return summary

def build_evidence_bundle(device: dict[str, Any], evidence: dict[str, Any], stale_after_days: int = 7) -> dict[str, Any]:
    normalized = normalize_managed_device(device, stale_after_days=stale_after_days)
    compliance = collection_items(evidence.get("compliance"))
    configuration = collection_items(evidence.get("configuration"))
    apps = collection_items(evidence.get("detected-apps"))
    return {
        "metadata": {"kind": "intune-device-evidence", "device_id": normalized["id"], "device_name": normalized["device_name"]},
        "summary": {
            "compliance_state": normalized["compliance_state"],
            "stale_sync": normalized["stale_sync"],
            "last_sync_age_days": normalized["last_sync_age_days"],
            "compliance_state_counts": summarize_states(compliance),
            "configuration_state_counts": summarize_states(configuration),
            "detected_app_count": len(apps),
        },
        "device": normalized,
        "evidence": evidence,
    }
