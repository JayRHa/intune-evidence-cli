# Intune Evidence CLI

Agent-friendly Microsoft Intune evidence collection for devices, policies, compliance and apps.

Collect. Normalize. Explain.

[![GitHub stars](https://img.shields.io/github/stars/JayRHa/IntuneEvidenceCLI?style=for-the-badge&logo=github&color=f4c542)](https://github.com/JayRHa/IntuneEvidenceCLI/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/JayRHa/IntuneEvidenceCLI?style=for-the-badge&logo=github&color=4078c0)](https://github.com/JayRHa/IntuneEvidenceCLI/network/members)
[![GitHub issues](https://img.shields.io/github/issues/JayRHa/IntuneEvidenceCLI?style=for-the-badge&logo=github&color=d73a4a)](https://github.com/JayRHa/IntuneEvidenceCLI/issues)
[![Contributors](https://img.shields.io/github/contributors/JayRHa/IntuneEvidenceCLI?style=for-the-badge&logo=github&color=28a745)](https://github.com/JayRHa/IntuneEvidenceCLI/graphs/contributors)

Microsoft Intune | Microsoft Graph | Python CLI | Agent Ready

<p>
  <a href="https://jannikreinhard.com/">Blog</a> ·
  <a href="https://www.linkedin.com/in/jannik-r/">LinkedIn</a> ·
  <a href="https://x.com/jannik_reinhard">X</a>
</p>

## What is this?

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

## Quick Start

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
