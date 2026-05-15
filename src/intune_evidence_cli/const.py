APP_NAME = "Intune Evidence CLI"
DEFAULT_AUTHORITY_HOST = "https://login.microsoftonline.com"
DEFAULT_GRAPH_HOST = "https://graph.microsoft.com"
DEFAULT_SCOPE = "https://graph.microsoft.com/.default"
DEFAULT_VERSION = "v1.0"
ENV_ACCESS_TOKEN = "MSGRAPH_ACCESS_TOKEN"
DEFAULT_DEVICE_FIELDS = ["id", "deviceName", "userPrincipalName", "operatingSystem", "osVersion", "complianceState", "managementAgent", "lastSyncDateTime", "azureADDeviceId", "serialNumber", "manufacturer", "model"]
EVIDENCE_RELATIONSHIPS = {
    "compliance": "/deviceManagement/managedDevices/{id}/deviceCompliancePolicyStates",
    "configuration": "/deviceManagement/managedDevices/{id}/deviceConfigurationStates",
    "detected-apps": "/deviceManagement/managedDevices/{id}/detectedApps",
}
