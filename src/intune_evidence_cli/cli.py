import argparse
import json
import os
import sys
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .const import DEFAULT_AUTHORITY_HOST, DEFAULT_DEVICE_FIELDS, DEFAULT_GRAPH_HOST, DEFAULT_SCOPE, DEFAULT_VERSION, ENV_ACCESS_TOKEN, EVIDENCE_RELATIONSHIPS
from .transform import apply_path_params, build_evidence_bundle, collection_items, graph_quote, merge_query, normalize_managed_device, parse_include

class CliError(RuntimeError):
    pass

def print_json(payload: Any) -> None:
    print(json.dumps(payload, indent=2, sort_keys=True))

def request_json(method: str, url: str, headers: dict[str, str]) -> Any:
    try:
        with urlopen(Request(url=url, method=method, headers=headers), timeout=60) as response:
            text = response.read().decode("utf-8")
            return json.loads(text) if text else {"status": response.status}
    except HTTPError as exc:
        raise CliError(f"HTTP {exc.code}: {exc.read().decode('utf-8', errors='replace')}") from exc
    except URLError as exc:
        raise CliError(f"Request failed: {exc.reason}") from exc

def token(args: argparse.Namespace) -> str:
    direct = args.access_token or os.getenv(ENV_ACCESS_TOKEN) or os.getenv("AZURE_ACCESS_TOKEN")
    if direct:
        return direct
    tenant = args.tenant_id or os.getenv("AZURE_TENANT_ID")
    client = args.client_id or os.getenv("AZURE_CLIENT_ID")
    secret = args.client_secret or os.getenv("AZURE_CLIENT_SECRET")
    if not all([tenant, client, secret]):
        raise CliError("Set MSGRAPH_ACCESS_TOKEN or AZURE_TENANT_ID, AZURE_CLIENT_ID and AZURE_CLIENT_SECRET.")
    body = urlencode({"client_id": client, "client_secret": secret, "grant_type": "client_credentials", "scope": args.scope}).encode("utf-8")
    req = Request(f"{args.authority_host.rstrip('/')}/{tenant}/oauth2/v2.0/token", method="POST", headers={"Content-Type": "application/x-www-form-urlencoded"}, data=body)
    try:
        with urlopen(req, timeout=60) as response:
            return json.loads(response.read().decode("utf-8"))["access_token"]
    except Exception as exc:
        raise CliError(f"Could not acquire Microsoft Graph token: {exc}") from exc

def graph_url(args: argparse.Namespace, path: str, query: dict[str, str] | None = None) -> str:
    path = path if path.startswith("/") else f"/{path}"
    return merge_query(f"{args.graph_host.rstrip('/')}/{args.version}{path}", query or {})

def headers(args: argparse.Namespace) -> dict[str, str]:
    return {"Accept": "application/json", "Authorization": f"Bearer {token(args)}"}

def selector(args: argparse.Namespace) -> tuple[str, dict[str, str]]:
    if args.device_id:
        return f"/deviceManagement/managedDevices/{args.device_id}", {}
    filters: list[str] = []
    if args.device_name:
        filters.append(f"deviceName eq '{graph_quote(args.device_name)}'")
    if args.user:
        filters.append(f"userPrincipalName eq '{graph_quote(args.user)}'")
    if not filters:
        raise CliError("Use --device-id, --device-name or --user.")
    return "/deviceManagement/managedDevices", {"$filter": " and ".join(filters), "$select": ",".join(DEFAULT_DEVICE_FIELDS), "$top": str(args.top)}

def plan(args: argparse.Namespace, name: str, path: str, query: dict[str, str] | None = None) -> dict[str, str]:
    return {"name": name, "method": "GET", "url": graph_url(args, path, query)}

def resolve_device(args: argparse.Namespace, auth_headers: dict[str, str]) -> dict[str, Any]:
    path, query = selector(args)
    payload = request_json("GET", graph_url(args, path, query), auth_headers)
    if args.device_id:
        return payload
    items = collection_items(payload)
    if not items:
        raise CliError("No managed device matched the selector.")
    if len(items) > 1 and not args.allow_multiple:
        names = ", ".join(str(item.get("deviceName")) for item in items[:5])
        raise CliError(f"Selector matched multiple devices ({names}). Refine the selector or use --allow-multiple.")
    return items[0]

def cmd_device(args: argparse.Namespace) -> int:
    path, query = selector(args)
    request_plan = plan(args, "device", path, query)
    if args.dry_run:
        print_json({"requests": [request_plan]})
        return 0
    print_json(normalize_managed_device(resolve_device(args, headers(args)), stale_after_days=args.stale_after_days))
    return 0

def cmd_bundle(args: argparse.Namespace) -> int:
    includes = parse_include(args.include, set(EVIDENCE_RELATIONSHIPS))
    path, query = selector(args)
    requests = [plan(args, "device", path, query)]
    placeholder = args.device_id or "resolved-managed-device-id"
    for include in includes:
        requests.append(plan(args, include, apply_path_params(EVIDENCE_RELATIONSHIPS[include], {"id": placeholder})))
    if args.dry_run:
        print_json({"requests": requests})
        return 0
    auth = headers(args)
    device = resolve_device(args, auth)
    device_id = device.get("id")
    if not device_id:
        raise CliError("Resolved device does not include an id.")
    evidence = {include: request_json("GET", graph_url(args, apply_path_params(EVIDENCE_RELATIONSHIPS[include], {"id": device_id})), auth) for include in includes}
    print_json(build_evidence_bundle(device, evidence, stale_after_days=args.stale_after_days))
    return 0

def cmd_user_devices(args: argparse.Namespace) -> int:
    query = {"$filter": f"userPrincipalName eq '{graph_quote(args.user)}'", "$select": ",".join(DEFAULT_DEVICE_FIELDS), "$top": str(args.top)}
    request_plan = plan(args, "managed-devices", "/deviceManagement/managedDevices", query)
    if args.dry_run:
        print_json({"requests": [request_plan]})
        return 0
    payload = request_json("GET", request_plan["url"], headers(args))
    print_json({"devices": [normalize_managed_device(item, stale_after_days=args.stale_after_days) for item in collection_items(payload)]})
    return 0

def add_auth(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--access-token", help=f"Access token. Defaults to {ENV_ACCESS_TOKEN} or AZURE_ACCESS_TOKEN.")
    parser.add_argument("--tenant-id", help="Tenant ID. Defaults to AZURE_TENANT_ID.")
    parser.add_argument("--client-id", help="Client ID. Defaults to AZURE_CLIENT_ID.")
    parser.add_argument("--client-secret", help="Client secret. Defaults to AZURE_CLIENT_SECRET.")
    parser.add_argument("--scope", default=DEFAULT_SCOPE)
    parser.add_argument("--authority-host", default=DEFAULT_AUTHORITY_HOST)
    parser.add_argument("--graph-host", default=DEFAULT_GRAPH_HOST)
    parser.add_argument("--version", default=DEFAULT_VERSION, choices=["v1.0", "beta"])

def add_selector(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--device-id")
    parser.add_argument("--device-name")
    parser.add_argument("--user")
    parser.add_argument("--top", type=int, default=10)
    parser.add_argument("--allow-multiple", action="store_true")
    parser.add_argument("--stale-after-days", type=int, default=7)
    parser.add_argument("--dry-run", action="store_true")

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Collect Intune device, app, policy and compliance evidence for humans and agents.")
    add_auth(parser)
    subs = parser.add_subparsers(dest="command", required=True)
    device = subs.add_parser("device", help="Resolve and summarize one Intune managed device.")
    add_selector(device)
    device.set_defaults(func=cmd_device)
    bundle = subs.add_parser("bundle", help="Collect a device evidence bundle.")
    add_selector(bundle)
    bundle.add_argument("--include", help="Comma-separated evidence: compliance,configuration,detected-apps. Defaults to all.")
    bundle.set_defaults(func=cmd_bundle)
    user_devices = subs.add_parser("user-devices", help="List normalized Intune managed devices for one user.")
    user_devices.add_argument("--user", required=True)
    user_devices.add_argument("--top", type=int, default=50)
    user_devices.add_argument("--stale-after-days", type=int, default=7)
    user_devices.add_argument("--dry-run", action="store_true")
    user_devices.set_defaults(func=cmd_user_devices)
    return parser

def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except (CliError, ValueError) as exc:
        parser.exit(2, f"error: {exc}\n")

if __name__ == "__main__":
    sys.exit(main())
