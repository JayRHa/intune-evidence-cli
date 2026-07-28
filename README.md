<!-- jr-brand:start -->
<div align="center">
  <a href="https://jannikreinhard.com/">
    <img src="https://raw.githubusercontent.com/JayRHa/.github/main/assets/readme/tool.svg" alt="Jannik Reinhard — Driving AI with passion" width="100%">
  </a>
  <h1>Intune Evidence CLI</h1>
  <p><strong>Agent-friendly Microsoft Intune evidence collection for devices, policies, compliance and apps.</strong></p>
  <p>
  <a href="https://jannikreinhard.com/"><img src="https://img.shields.io/badge/Website-146CDD?style=flat-square&amp;logo=wordpress&amp;logoColor=white" alt="Website"></a>
  <a href="https://github.com/JayRHa"><img src="https://img.shields.io/badge/GitHub-081427?style=flat-square&amp;logo=github&amp;logoColor=white" alt="GitHub"></a>
  <a href="https://www.linkedin.com/in/jannik-r/"><img src="https://img.shields.io/badge/LinkedIn-0795FF?style=flat-square&amp;logo=linkedin&amp;logoColor=white" alt="LinkedIn"></a>
  <a href="https://x.com/jannik_reinhard"><img src="https://img.shields.io/badge/X-081427?style=flat-square&amp;logo=x&amp;logoColor=white" alt="X"></a>
  <a href="https://www.youtube.com/@jannikreinhard"><img src="https://img.shields.io/badge/YouTube-146CDD?style=flat-square&amp;logo=youtube&amp;logoColor=white" alt="YouTube"></a>
  </p>
  <p><sub>Driving AI with passion · Microsoft Foundry · Intune · Azure</sub></p>
</div>
<!-- jr-brand:end -->

Agent-friendly Microsoft Intune evidence collection for devices, policies, compliance and apps.

Collect. Normalize. Explain.


Microsoft Intune | Microsoft Graph | Python CLI | Agent Ready


## Overview

Intune Evidence CLI collects focused Microsoft Intune evidence through Microsoft Graph and returns stable JSON for humans, scripts and AI agents. It is designed for troubleshooting workflows where an agent needs to prove what is assigned, what is compliant, what is stale and which raw Graph requests were used.

The CLI can resolve a managed device by ID, device name or user principal name, normalize the most important device fields, and build an evidence bundle with compliance policy states, configuration states and detected apps.

## How It Works

```mermaid
flowchart LR
    Selector[Device ID, name or user] --> CLI[intune-evidence CLI]
    CLI --> Plan[Dry-run request plan]
    CLI --> Graph[Microsoft Graph Intune APIs]
    Graph --> Raw[Raw Intune evidence]
    Raw --> Normalize[Normalize and summarize]
    Normalize --> Bundle[Evidence bundle JSON]
```

## Quickstart

```bash
git clone https://github.com/JayRHa/IntuneEvidenceCLI.git
cd IntuneEvidenceCLI
python -m pip install -e .

export MSGRAPH_ACCESS_TOKEN="<access-token>"
intune-evidence device --device-name "WIN-001" --dry-run
intune-evidence bundle --device-id "<managed-device-id>"
```

Use client credentials instead of a prebuilt token:

```bash
export AZURE_TENANT_ID="<tenant-id>"
export AZURE_CLIENT_ID="<app-registration-client-id>"
export AZURE_CLIENT_SECRET="<client-secret>"

intune-evidence user-devices --user alex@example.com
```

## Commands

| Command | Purpose |
| --- | --- |
| `intune-evidence device` | Resolve one Intune managed device and return a normalized summary. |
| `intune-evidence bundle` | Build a device evidence bundle with compliance, configuration and detected app evidence. |
| `intune-evidence user-devices` | List normalized Intune managed devices for a user principal name. |

## Examples

```bash
intune-evidence device --device-name "WIN-001"
intune-evidence device --user alex@example.com --stale-after-days 3
intune-evidence bundle --device-id "<managed-device-id>" --include compliance,configuration
intune-evidence user-devices --user alex@example.com --dry-run
```

## Microsoft Graph Permissions

| Evidence | Graph permission |
| --- | --- |
| Managed devices | `DeviceManagementManagedDevices.Read.All` |
| Compliance states | `DeviceManagementConfiguration.Read.All` |
| Configuration states | `DeviceManagementConfiguration.Read.All` |
| Detected apps | `DeviceManagementManagedDevices.Read.All` |

## Output Contract

All commands write JSON to stdout. `--dry-run` returns the exact Graph request plan, which is useful before giving an automation or AI agent tenant access.

## License

MIT License. See [LICENSE](LICENSE).

<!-- jr-brand-footer:start -->

---

<div align="center">
  <p><sub>Built and maintained by <a href="https://jannikreinhard.com/">Jannik Reinhard</a> · Microsoft MVP for Security and AI Platform.</sub></p>
  <p><a href="https://www.buymeacoffee.com/jannikreinf">Support the open-source work</a></p>
  <p><strong>Stay healthy, Cheers Jannik</strong></p>
</div>

<!-- jr-brand-footer:end -->
