"""Tools for the DaaS MCP Server."""

import json
import urllib.parse
import httpx
from daas_mcp_server.constants import CC_API_ENDPOINT, UNKNOWN, WEBSTUDIO_API_ENDPOINT
from daas_mcp_server.utils.auth import get_token
from daas_mcp_server.utils.environment import get_customer_id
from daas_mcp_server.utils.logging import get_logger

logger = get_logger(__name__)

client = httpx.AsyncClient()


async def get_delivery_groups() -> str:
    """Get the full list of delivery groups from the site.

    This tool is designed to retrieve the real data from the customers' DDC or site.

    Use this tool when the user wants to:
        - Get the list of delivery groups in the site.
        - Get the list of delivery groups in the site with a filter.

    Args:
        filter (str): optional.

    Returns:
        list: A list of delivery groups.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/DeliveryGroupsV2"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url, headers=headers)

        if result.status_code == 200:
            delivery_groups = result.json().get("Items", [])
            delivery_groups = [
                {
                    "full_name": group.get("FullName", UNKNOWN),
                    "description": group.get("Description", "N/A"),
                    "is_maintenance_mode": group.get("InMaintenanceMode", False),
                }
                for group in delivery_groups
            ]
            return json.dumps(delivery_groups, ensure_ascii=False)
        else:
            return f"Failed to get delivery groups. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get delivery groups. Error: {err}")
        return f"Failed to get delivery groups. Error: {err}"


async def get_machine_catalogs() -> str:
    """Get the full list of machine catalogs from the site.

    This tool is designed to retrieve the real machine catalogs from the customers' DDC or site.

    Use this tool when the user wants to:
        - Get the list of machine catalogs in the site.
        - Get the list of machine catalogs in the site with a filter.

    Args:
        filter (str): optional.

    Returns:
        list: A list of machine catalogs.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/MachineCatalogsV2"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url, headers=headers)

        if result.status_code == 200:
            machine_catalogs = result.json().get("Items", [])
            machine_catalogs = [
                {
                    "full_name": catalog.get("Name", UNKNOWN),
                    "description": catalog.get("Description", UNKNOWN),
                    "session_support": catalog.get("SessionSupport", UNKNOWN),
                }
                for catalog in machine_catalogs
            ]
            return json.dumps(machine_catalogs, ensure_ascii=False)
        else:
            return f"Failed to get machine catalogs. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get machine catalogs. Error: {err}")
        return f"Failed to get machine catalogs. Error: {err}"


async def check_ddc_power_state() -> str:
    """Check the power state of the DDC.

    This tool is designed to check the power state of the DDC.

    Use this tool when the user wants to:
        - Check if the DDC is powered on or off.

    Returns:
        str: The power state of the DDC.
    """
    try:
        customer_id = get_customer_id()

        url = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/ping"

        result = await client.get(url)

        if result.status_code == 200:
            response = result.text
            if response == "true":
                return "DDC is powered on."
            else:
                return "DDC is powered off."
        else:
            return f"Failed to check DDC power state. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to check DDC power state. Error: {err}")
        return f"Failed to check DDC power state. Error: {err}"


async def get_site_id(customerId: str, bearerToken: str) -> str:
    """Get the site id for the given customer id and bearer token."""
    try:
        logger.info(f"Getting site id for customer: {customerId}")
        cc_url = f"{CC_API_ENDPOINT}/resourceprovider/{customerId}/customerrole"
        cc_headers = {
            "Authorization": f"CWSAuth bearer={bearerToken}",
        }

        response = await client.get(cc_url, headers=cc_headers)
        if response.status_code != 200:
            raise Exception(
                f"Failed to get the customer role from CC. Status code: {response.status_code}, Response: {response.text}"
            )

        return response.json()["VirtualSiteId"]
    except Exception as err:
        logger.error(f"Failed to get the site id. Error: {err}")
        raise err


async def getSites() -> str:
    """
    Get the list of sites that are available to the customer and visible to the admin.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return List of sites.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/Sites"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getSite() -> str:
    """
    Get the details about a single site.
    @param nameOrId Name or ID of the site.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return Site details.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/Sites/{virtual_site_id}"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getCeipParticipation() -> str:
    """
    Get the Customer Experience Improvement Program Participation for the site.
    @param nameOrId Name or ID of the site.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return The result indicating if Customer Experience Improvement Program is participated.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/Sites/{virtual_site_id}/CustomerExperienceImprovementProgram"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getDnsResolution() -> str:
    """
    Get the DNS Resolution for the site.
    @param nameOrId Name or ID of the site.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return The result indicating if DNS Resolution is enabled.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/Sites/{virtual_site_id}/DnsResolution"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getSiteErrorWarning(fields: str) -> str:
    """
    Get number of errors and warnings for the specified objects in the site.
    @param nameOrId Name or ID of the site.
    @param fields (optional) To specify the object for which the number of the errors and warnings are reported.
                        Otherwise, the number of errors and warning will be reported for all objects.
                        The value should be a comma-separated list of object types.
                        Supported object types are: MachineCatalog, DeliveryGroup, Machine, Hypervisor, Image, Zone, Site
    @param async (optional) If `true`, to get the number of error and warning will be done as a background task.
                        The task will have JobType GetSiteErrorWarning
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/Sites/{virtual_site_id}/ErrorWarning?"
        if fields:
            url_ += "fields=" + urllib.parse.quote(str(fields))
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getSiteLicense() -> str:
    """
    Get the license in use for a site.
    @param nameOrId Name or ID of the site.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return The license response model.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/Sites/{virtual_site_id}/License"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getSiteLoadBalancingOption() -> str:
    """
    Get the load balancing option for the site.
    @param nameOrId Name or ID of the site.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return The result indicating if Vertical Load Balancing is used.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/Sites/{virtual_site_id}/LoadBalancingOption"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getLocalAppAccessConfig() -> str:
    """
    Get Local App Access Config.
    @param nameOrId Name or ID of the site.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return True or False.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/Sites/{virtual_site_id}/LocalAppAccessConfig"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getSiteMisconfigurationReport() -> str:
    """
    Get the misconfiguration report.
    @param nameOrId ID of the site.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return Last misconfiguration report. If no misconfiguration, returns a 404 Not Found.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/Sites/{virtual_site_id}/MisconfigurationReport"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getMultipleRemotePCAssignments() -> str:
    """
    Get multi-user auto-assignment for Remote PC Access.
    @param nameOrId Name or ID of the site.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return The result indicating if allow multi-user auto-assignment for Remote PC Access.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/Sites/{virtual_site_id}/MultipleRemotePCAssignments"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getNewSiteSecurityKey() -> str:
    """
    Get a new security key for a site.
    @param nameOrId Name or ID of the site.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return A new site security key.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/Sites/{virtual_site_id}/NewSecurityKey"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getSiteSecurityKeyConfiguration() -> str:
    """
    Get the security key configuration for a site.
    @param nameOrId Name or ID of the site.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return Site security key configuration.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/Sites/{virtual_site_id}/SecurityKeyConfiguration"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getSiteSecurityKeyManagementConfig() -> str:
    """
    Get security key management config for a site.
    @param nameOrId Name or ID of the site.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return Site security key management config, enabled: true if feature enabled, false otherwise.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/Sites/{virtual_site_id}/SecurityKeyManagementConfig"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getSessionsTrend(startDate: str, endDate: str, intervalLength: int) -> str:
    """
    Get the sessions trend
    @param customerid The customer ID.
    @param nameOrId The site name or ID.
    @param startDate The start date of sessions trend to query, for example '2021-11-01T12:00:00'.
    @param endDate The end date of sessions trend to query, for example '2021-11-08T12:00:00'.
    @param intervalLength The minutes interval to query.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/Sites/{virtual_site_id}/SessionsTrend?"
        if startDate:
            url_ += "startDate=" + urllib.parse.quote(str(startDate))
        if endDate:
            url_ += "&endDate=" + urllib.parse.quote(str(endDate)) 
        if intervalLength:
            url_ += "&intervalLength=" + urllib.parse.quote(str(intervalLength)) 
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }
        print(f"URL: {url_}")
        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getSiteSettings(fields: str) -> str:
    """
    Get the settings for the site.
    @param nameOrId Name or ID of the site.
    @param fields (optional) To specify the object for which the settings are returned.
            The value should be a comma-separated list of object types.
            Supported object types are: DnsResolutionEnabled, TrustRequestsSentToTheXmlServicePort, UseVerticalScalingForRdsLaunches, WebUiPolicySetEnabled, ConsoleInactivityTimeoutMinutes
            Cloud-Only: MultiTenantServicesAccess
            OnPrem-Only: SupportedAuthenticators, AllowedCorsOriginsForIwa, MultiSites, DefaultDomain, XmlServicesSslConfigurations
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return The result of site settings.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/Sites/{virtual_site_id}/Settings?"
        if fields:
            url_ += "fields=" + urllib.parse.quote(str(fields))
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getSiteStatus() -> str:
    """
    Get the status of a site.
    @param nameOrId Name or ID of the site.
    @param async (optional) If `true`, the site status query will be executed as a background task.
            The task will have JobType GetSiteStatus.
            When the task is complete it will redirect to
            GetJobResults.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return The site status.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/Sites/{virtual_site_id}/Status?"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getSiteTestReport() -> str:
    """
    Get the most recent test report.
    @param nameOrId Name or ID of the site.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return Last test report.  If no tests have been run, returns a 404 Not Found.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/Sites/{virtual_site_id}/TestReport"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getUpgradePackageVersions() -> str:
    """
    Get the latest released VDA upgrade package versions in the site.
    @param nameOrId Name or ID of the site.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return The latest released VDA upgrade package version of each upgrade package type.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/Sites/{virtual_site_id}/UpgradePackageVersions"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getSiteValidLicenses() -> str:
    """
    Get valid licenses for a site.
    @param nameOrId Name or ID of the site.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return The list of valid licenses in the site.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/Sites/{virtual_site_id}/ValidLicenses"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getMachineCatalogs(adminFolder: str, limit: int, fields: str) -> str:
    """
    Get all machine catalogs.
    @param adminFolder (optional) Admin folder path or Id.
    @param async (optional) If `true`, it will be queried as a background task.
    @param limit (optional) The max number of machine catalogs returned by this query.
            If not specified, the server might use a default limit of 250 items.
            If the specified value is larger than 1000, the server might reject the call.
            The default and maximum values depend on server settings.
    @param continuationToken (optional) If a query cannot be completed, the response will have a
            ContinuationToken set.
            To obtain more results from the query, pass the
            continuation token back into the query to get the next
            batch of results.
    @param fields (optional) Optional. A filter string containing object fields requested to be returned, the requested fields are separated by comma','.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return List of machine catalogs.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/MachineCatalogs?"
        if limit:
            url_ += "limit=" + urllib.parse.quote(str(limit))
        if adminFolder:
            url_ += "&adminFolder=" + urllib.parse.quote(str(adminFolder)) 
        if fields:
            url_ += "&fields=" + urllib.parse.quote(str(fields)) 
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getMachineCatalog(nameOrId: str, fields: str) -> str:
    """
    Get details about a single machine catalog.
    @param nameOrId Name or ID of the machine catalog. If the catalog is present in a catalog folder,
                        specify the name in this format: {catalog folder path plus catalog name}.
                        For example, FolderName1|FolderName2|CatalogName.
    @param async (optional) If `true`, it will be queried as a background task.
    @param fields (optional) Optional parameters, removing unspecified properties that otherwise would have been sent by the server.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return Details of machine catalog.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/MachineCatalogs/{nameOrId}?"
        if fields:
            url_ += "fields=" + urllib.parse.quote(str(fields))
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getMachineCatalogsAdministrators(nameOrId: str) -> str:
    """
    Get administrators who can administer a machine catalog.
    @param nameOrId Name or ID of the machine catalog. If the catalog is present in a catalog folder,
                        specify the name in this format: {catalog folder path plus catalog name}.
                        For example, FolderName1|FolderName2|CatalogName.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return List of administrators.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/MachineCatalogs/{nameOrId}/Administrators"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getMachineCatalogCostSummary(nameOrId: str, start: str, end: str, summaryType: str) -> str:
    """
    Get the machine catalog's cost summary.
    @param nameOrId The name or ID of the machine catalog.
    @param start The start date of the cost summary, the date format is `yyyy-MM-ddT00:00:00Z`.
    @param end The end date of the cost summary, the date format is `yyyy-MM-ddT00:00:00Z`.
    @param summaryType (optional) The summary type of the cost, Currently only `VM` and `Disk` are supported.
    @param async (optional) if the value is `true`, the machine catalog's cost summary will be calculated asynchronously.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return The machine catalog's cost summary.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/MachineCatalogs/{nameOrId}/CostSummary?"
        if start:
            url_ += "start=" + urllib.parse.quote(str(start))
        if end:
            url_ += "&end=" + urllib.parse.quote(str(end)) 
        if summaryType:
            url_ += "&summaryType=" + urllib.parse.quote(str(summaryType)) 
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getMachineCatalogDailyCost(nameOrId: str, start: str, end: str) -> str:
    """
    Get the machine catalog's daily cost.
    @param nameOrId The name or ID of the machine catalog.
    @param start The start date of the daily cost, the date format is `yyyy-MM-ddT00:00:00Z`.
    @param end The end date of the daily cost, the date format is `yyyy-MM-ddT00:00:00Z`.
    @param async (optional) If the value is `true`, the machine catalog's daily cost will be calculated asynchronously.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return The machine catalog's daily cost.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/MachineCatalogs/{nameOrId}/DailyCost?"
        if start:
            url_ += "start=" + urllib.parse.quote(str(start))
        if end:
            url_ += "&end=" + urllib.parse.quote(str(end)) 
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getMachineCatalogDeliveryGroupAssociations(nameOrId: str, limit: int) -> str:
    """
    Get delivery group associations of a machine catalog.
    @param nameOrId Name or ID of the machine catalog. If the catalog is present in a catalog folder,
                        specify the name in this format: {catalog folder path plus catalog name}.
                        For example, FolderName1|FolderName2|CatalogName.
    @param limit (optional) The max number of delivery group associations returned by this query.
            If not specified, the server might use a default limit of 250 items.
            If the specified value is larger than 1000, the server might reject the call.
            The default and maximum values depend on server settings.
    @param continuationToken (optional) If a query cannot be completed, the response will have a
            ContinuationToken set.
            To obtain more results from the query, pass the
            continuation token back into the query to get the next
            batch of results.
    @param async (optional) If `true`, it will be queried as a background task.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return The delivery group associations of the given machine catalog identifier
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/MachineCatalogs/{nameOrId}/DeliveryGroupAssociations?"
        if limit:
            url_ += "limit=" + urllib.parse.quote(str(limit))
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getMachineCatalogEnrollments(nameOrId: str) -> str:
    """
    Get the list of enrollments in the machine catalog.
    @param nameOrId Name or ID of the machine catalog.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return List of enrollments.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/MachineCatalogs/{nameOrId}/Enrollments"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getMachineCatalogLastMasterImage(nameOrId: str) -> str:
    """
    Get the last master VM images used by the machine catalog.
    @param nameOrId Name or ID of the machine catalog. If the catalog is present in a catalog folder,
                        specify the name in this format: {catalog folder path plus catalog name}.
                        For example, FolderName1|FolderName2|CatalogName.
    @param async (optional) If `true`, it will be queried as a background task.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return Last image used by the machine catalog to provision VMs.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/MachineCatalogs/{nameOrId}/LastMasterImage?"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getMachineCatalogMachineAccounts(nameOrId: str, limit: int, accountState: str) -> str:
    """
    Get all machine accounts associated with a machine catalog.
    @param nameOrId Name or ID of the machine catalog to get machine accounts for.
                        If the catalog is present in a catalog folder,
                        specify the name in this format: {catalog folder path plus catalog name}.
                        For example, FolderName1|FolderName2|CatalogName.
    @param limit (optional) The max number of machine accounts returned by this query.
            If not specified, the server might use a default limit of 250 items.
            If the specified value is larger than 1000, the server might reject the call.
            The default and maximum values depend on server settings.
    @param continuationToken (optional) If a query cannot be completed, the response will have a
            ContinuationToken set.
            To obtain more results from the query, pass the
            continuation token back into the query to get the next
            batch of results.
    @param async (optional) If `true`, the machine accounts will be queried as a background task.
            The task will have JobType GetMachineCatalogMachineAccounts.
            When the task is complete it will redirect to GetJobResults.
    @param accountState (optional) The state of accounts for query.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return List of machine accounts.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/MachineCatalogs/{nameOrId}/MachineAccounts?"
        if limit:
            url_ += "limit=" + urllib.parse.quote(str(limit))
        if accountState:
            url_ += "&accountState=" + urllib.parse.quote(str(accountState)) 
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getMachineCatalogMachines(nameOrId: str, limit: int, fields: str) -> str:
    """
    GET the machines of a catalog
    @param nameOrId Name or ID of the machine catalog. If the catalog is present in a catalog folder,
                        specify the name in this format: {catalog folder path plus catalog name}.
                        For example, FolderName1|FolderName2|CatalogName.
    @param limit (optional) The max number of machines returned by this query.
            If not specified, the server might use a default limit of 250 items.
            If the specified value is larger than 1000, the server might reject the call.
            The default and maximum values depend on server settings.
    @param continuationToken (optional) If a query cannot be completed, the response will have a
            ContinuationToken set.
            To obtain more results from the query, pass the
            continuation token back into the query to get the next
            batch of results.
    @param async (optional) If `true`, it will be queried as a background task.
    @param fields (optional) Optional parameters, only the specified properties in the fields are required.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return The machines of the given machine catalog identifier
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/MachineCatalogs/{nameOrId}/Machines?"
        if limit:
            url_ += "limit=" + urllib.parse.quote(str(limit))
        if fields:
            url_ += "&fields=" + urllib.parse.quote(str(fields)) 
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getMachineCatalogMasterImageHistory(nameOrId: str) -> str:
    """
    Get the history of master VM images used by the machine catalog.
    @param nameOrId Name or ID of the machine catalog.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return List of images used by the machine catalog to provision VMs.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/MachineCatalogs/{nameOrId}/MasterImageHistory"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getMachineCatalogStartMenuApplications(nameOrId: str, machines: list) -> str:
    """
    Get the start menu applications from a machine in the machine catalog.
    @param nameOrId Name or ID of the machine catalog. If the catalog is present in a catalog folder,
                        specify the name in this format: {catalog folder path plus catalog name}.
                        For example, FolderName1|FolderName2|CatalogName.
    @param machines (optional) The machines to get start menu applications
    @param async (optional) If `true`, the start menu applications will be queried as a background task.
            This is recommended as this operation may cause a power
            action, turning on a machine in order to gather the data.
            This may take some time to run,
            and if it exceeds 90 seconds the request may time out.
            The task will have JobType GetStartMenuApplications.
            When the task is complete it will redirect to
            "JobsControllerTP.GetJobResults(string)".
            The job's Parameters will contain properties:
    
    _Id_ - ID of the machine catalog from which start menu applications are being obtained,
    _Name_ - Name of the machine catalog from which start menu applications are being obtained.
    _MachineId_ - ID of the machine selected, from which the start menu applications are being obtained; will be present in Parameters only after a machine is selected.
    _MachineName_ - Name of the machine selected, from which the start menu applications are being obtained; will be present in Parameters only after a machine is selected.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return List of start menu applications.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/MachineCatalogs/{nameOrId}/StartMenuApplications?"
        if machines:
            url_ += "machines=" + urllib.parse.quote(str(machines))
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getMachineCatalogTags(nameOrId: str, fields: str) -> str:
    """
    Get tags associated with a machine catalog.
    @param nameOrId Name or ID of the machine catalog. If the catalog is present in a catalog folder,
                        specify the name in this format: {catalog folder path plus catalog name}.
                        For example, FolderName1|FolderName2|CatalogName.
    @param fields (optional) Optional parameters, removing unspecified properties that otherwise would have been sent by the server.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return List of tags.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/MachineCatalogs/{nameOrId}/Tags?"
        if fields:
            url_ += "fields=" + urllib.parse.quote(str(fields))
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getMachineCatalogTestReport(nameOrId: str) -> str:
    """
    Get the most recent test report of a machine catalog.
    @param nameOrId Name or ID of the machine catalog. If the catalog is present in a catalog folder,
                        specify the name in this format: {catalog folder path plus catalog name}.
                        For example, FolderName1|FolderName2|CatalogName.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return Last test report.  If no tests have been run,
            returns a 404 Not Found.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/MachineCatalogs/{nameOrId}/TestReport"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getMachineCatalogVDAComponentsAndFeatures(nameOrId: str, upgradeVersion: str) -> str:
    """
    Get the components and features of VDAs associated with a machine catalog.
    @param nameOrId Name or ID of the machine catalog.
                        If the catalog is present in a catalog folder,
                        specify the name in this format: {catalog folder path plus catalog name}.
                        For example, FolderName1|FolderName2|CatalogName.
    @param upgradeVersion (optional) The version of the VDA to upgrade to.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return Components and features of VDAs associated with a machine catalog.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/MachineCatalogs/{nameOrId}/VDAComponentsAndFeatures?"
        if upgradeVersion:
            url_ += "upgradeVersion=" + urllib.parse.quote(str(upgradeVersion))
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getMachineCatalogVDAUpgradeVersions(nameOrId: str) -> str:
    """
    Get the available VDA upgrade versions associated with a machine catalog.
    @param nameOrId Name or ID of the machine catalog.
                        If the catalog is present in a catalog folder,
                        specify the name in this format: {catalog folder path plus catalog name}.
                        For example, FolderName1|FolderName2|CatalogName.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return The list of available VDA upgrade versions associated with a machine catalog.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/MachineCatalogs/{nameOrId}/VDAUpgradeVersions"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getMachineCatalogsV2(adminFolder: str, limit: int, fields: str) -> str:
    """
    The V2  version of get all machine catalogs.
    @param adminFolder (optional) Admin folder path or Id.
    @param async (optional) If `true`, it will be queried as a background task.
    @param limit (optional) The max number of machine catalogs returned by this query.
            If not specified, the server might use a default limit of 250 items.
            If the specified value is larger than 1000, the server might reject the call.
            The default and maximum values depend on server settings.
    @param continuationToken (optional) If a query cannot be completed, the response will have a
            ContinuationToken set.
            To obtain more results from the query, pass the
            continuation token back into the query to get the next
            batch of results.
    @param fields (optional) Optional. A filter string containing object fields requested to be returned, the requested fields are separated by comma','.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return List of machine catalogs.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/MachineCatalogsV2?"
        if limit:
            url_ += "limit=" + urllib.parse.quote(str(limit))
        if adminFolder:
            url_ += "&adminFolder=" + urllib.parse.quote(str(adminFolder)) 
        if fields:
            url_ += "&fields=" + urllib.parse.quote(str(fields)) 
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getHypervisorResourcePoolAllAvailableNetworks() -> str:
    """
    Get all available networks among hypervisors and resource pools.
    @param async (optional) If execute this API asynchronous.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return List of available networks.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/hypervisorResourcePoolAllAvailableNetworks?"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getHypervisors() -> str:
    """
    Get the hypervisors.
    @param async (optional) Async request to hypervisor.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return List of hypervisors.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/hypervisors?"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getHypervisor(nameOrId: str) -> str:
    """
    Get the details for a single hypervisor.
    @param nameOrId Name or ID of the hypervisor.
    @param async (optional) Async request to hypervisor.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return Hypervisor response object for AWS.
            or
            Hypervisor response object for Azure.
            or
            Hypervisor response object for GCP.
            or
            Hypervisor response object for SCCM.
            or
            Hypervisor response object.
            or
            Hypervisor response object for OCI.
            or
            Hypervisor response object for Azure Arc.
            or
            Hypervisor response object for OpenShift.
            or
            Hypervisor details.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/hypervisors/{nameOrId}?"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getHypervisorAdministrators(nameOrId: str, limit: int) -> str:
    """
    Get administrators who can administer a hypervisor.
    @param nameOrId Name or ID of the hypervisor.
    @param async (optional) If async execute.
    @param limit (optional) The max number of administrators returned by this query.
            If not specified, the server might use a default limit of 250 items.
            If the specified value is larger than 1000, the server might reject the call.
            The default and maximum values depend on server settings.
    @param continuationToken (optional) If a query cannot be completed, the response will have a
            ContinuationToken set.
            To obtain more results from the query, pass the
            continuation token back into the query to get the next
            batch of results.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return List of administrators.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/hypervisors/{nameOrId}/administrators?"
        if limit:
            url_ += "limit=" + urllib.parse.quote(str(limit))
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getHypervisorAllResources(nameOrId: str, path: str, children: int, type: list, showTagged: bool, detail: bool) -> str:
    """
    Get all resources within a hypervisor.
    @param nameOrId Name or ID of the hypervisor.
    @param path (optional) Path to the resource container within the hypervisor. The path may
            either be a relative path as specified by
            RelativePath, or
            may be a URL-encoded XenApp & XenDesktop resource path starting
            with `XDHyp:`; for example, as specified by
            XDPath.
    @param children (optional) Specifies the number of levels of children to enumerate.
            Default is `0`, meaning that only the object referred to by `path`
            is returned and its
            Children array will be left
            null.
            A special value of `-1` indicates that the entire resource hierarchy
            should be enumerated.  Use with care!  It may take a very long time
            to enumerate a large number of resources from a hypervisor, and the
            call may time out before completing.
    @param type (optional) If specified, limits the results to the specified resource type(s).
    @param showTagged (optional) By default, items which are tagged by XenDesktop are not shown. Set
            this to `true` to override that behavior.
    @param detail (optional) If `true`, full details of VMs, snapshots, and templates will be
            retrieved. This can be very time consuming and will reduce the
            performance of the call. May only be used if `path` refers to a VM,
            snapshot, or template resource.
            <!-- Internally this calls Get-HypConfigurationObjectForItem -->
    @param async (optional) Async request to get the resources with *path.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return Cloud-based hypervisor's availability zone.
            or
            Hypervisor GPU type resource.
            or
            Hypervisor security group resource.
            or
            Cloud-based hypervisor service offering.
            or
            Hypervisor storage information.
            or
            Cloud-based machine template.
            or
            Virtual machine.
            or
            VM/snapshot/template configuration.
            or
            Cloud-based virtual private cloud.
            or
            Hypervisor connection region.
            or
            A list of hypervisor resources.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/hypervisors/{nameOrId}/allResources?"
        if path:
            url_ += "path=" + urllib.parse.quote(str(path))
        if children:
            url_ += "&children=" + urllib.parse.quote(str(children)) 
        if type:
            url_ += "&type=" + urllib.parse.quote(str(type)) 
        if showTagged:
            url_ += "&showTagged=" + urllib.parse.quote(str(showTagged)) 
        if detail:
            url_ += "&detail=" + urllib.parse.quote(str(detail)) 
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getHypervisorDeletePreview(nameOrId: str) -> str:
    """
    Get the hypervisor delete preview.
    @param nameOrId Name or ID of the hypervisor.
    @param async (optional) If execute this API asynchronous.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return HypervisorDeletePreviewResponseModel object.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/hypervisors/{nameOrId}/deletePreview?"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getHypervisorJobs(nameOrId: str) -> str:
    """
    Get the currently active jobs that are using a hypervisor.
    @param nameOrId Name or ID of the hypervisor.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return List of machine catalogs that are using a hypervisor.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/hypervisors/{nameOrId}/jobs"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getHypervisorMachineCatalogs(nameOrId: str, limit: int) -> str:
    """
    Get the machine catalogs that are using a hypervisor.
    @param nameOrId Name or ID of the hypervisor.
    @param async (optional) If async execute.
    @param limit (optional) The max number of machine catalogs returned by this query.
            If not specified, the server might use a default limit of 250 items.
            If the specified value is larger than 1000, the server might reject the call.
            The default and maximum values depend on server settings.
    @param continuationToken (optional) If a query cannot be completed, the response will have a
            ContinuationToken set.
            To obtain more results from the query, pass the
            continuation token back into the query to get the next
            batch of results.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return List of machine catalogs that are using a hypervisor.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/hypervisors/{nameOrId}/machineCatalogs?"
        if limit:
            url_ += "limit=" + urllib.parse.quote(str(limit))
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getHypervisorOrphanedResources(nameOrId: str) -> str:
    """
    Run detect on a hypervisor and retrieve orphaned resources.
    @param nameOrId Name or ID of the hypervisor to detect.
    @param async (optional) If `true`, the tests will run as a background task. This is recommended as the
            tests may take some time to run, and if it exceeds 90 seconds the request may
            time out.
    
    _Id_ - ID of the hypervisor being detected,
    _Name_ - Name of the hypervisor being detected.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return Detect orphaned resource response.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/Hypervisors/{nameOrId}/OrphanedResources?"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getHypervisorResourcePools(nameOrId: str) -> str:
    """
    Get the list of hypervisor resource pools.
    @param nameOrId Name or ID of the hypervisor.
    @param async (optional) Async request to get the resource pool.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return List of hypervisor resource pools.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/hypervisors/{nameOrId}/resourcePools?"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getHypervisorResourcePool(nameOrId: str, poolId: str) -> str:
    """
    Get details about a hypervisor resource pool.
    @param nameOrId Name or ID of the hypervisor.
    @param poolId Name or ID of the resource pool.
    @param async (optional) Async request to get the resource pool.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return Pool of resources available on AWS hypervisor.
            or
            Pool of resources available on Azure hypervisor.
            or
            Pool of resources available on GCP hypervisor.
            or
            Pool of resources available on traditional hypervisor.
            or
            Details about the hypervisor resource pool.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/hypervisors/{nameOrId}/resourcePools/{poolId}?"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getHypervisorResourcePoolAdministrators(nameOrId: str, poolId: str, limit: int) -> str:
    """
    Get administrators who can administer a resource pool.
    @param nameOrId Name or ID of the hypervisor.
    @param poolId Name or ID of the resource pool.
    @param async (optional) If async execute.
    @param limit (optional) The max number of administrators returned by this query.
            If not specified, the server might use a default limit of 250 items.
            If the specified value is larger than 1000, the server might reject the call.
            The default and maximum values depend on server settings.
    @param continuationToken (optional) If a query cannot be completed, the response will have a
            ContinuationToken set.
            To obtain more results from the query, pass the
            continuation token back into the query to get the next
            batch of results.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return List of administrators.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/hypervisors/{nameOrId}/resourcePools/{poolId}/administrators?"
        if limit:
            url_ += "limit=" + urllib.parse.quote(str(limit))
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getHypervisorResourcePoolDeletePreview(nameOrId: str, poolId: str) -> str:
    """
    Get the hypervisor resource pool delete preview.
    @param nameOrId Name or ID of the hypervisor.
    @param poolId Name or ID of the resource pool.
    @param async (optional) If execute this API asynchronous.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return HypervisorDeletePreviewResponseModel object.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/hypervisors/{nameOrId}/resourcePools/{poolId}/deletePreview?"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getHypervisorResourcePoolJobs(nameOrId: str, poolId: str) -> str:
    """
    Get the currently active jobs that are using a resource pool.
    @param nameOrId Name or ID of the hypervisor.
    @param poolId Name or ID of the resource pool.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return List of machine catalogs that are using a hypervisor.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/hypervisors/{nameOrId}/resourcePools/{poolId}/jobs"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getHypervisorResourcePoolMachineCatalogs(nameOrId: str, poolId: str, limit: int) -> str:
    """
    Get the machine catalogs that are using a resource pool.
    @param nameOrId Name or ID of the hypervisor.
    @param poolId Name or ID of the resource pool.
    @param async (optional) If async execute.
    @param limit (optional) The max number of machine catalogs returned by this query.
            If not specified, the server might use a default limit of 250 items.
            If the specified value is larger than 1000, the server might reject the call.
            The default and maximum values depend on server settings.
    @param continuationToken (optional) If a query cannot be completed, the response will have a
            ContinuationToken set.
            To obtain more results from the query, pass the
            continuation token back into the query to get the next
            batch of results.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return List of machine catalogs that are using a hypervisor.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/hypervisors/{nameOrId}/resourcePools/{poolId}/machineCatalogs?"
        if limit:
            url_ += "limit=" + urllib.parse.quote(str(limit))
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getHypervisorResourcePoolResources(nameOrId: str, poolId: str, path: str, children: int, type: list, showTagged: bool, detail: bool) -> str:
    """
    Get the resources within a hypervisor resource pool.
    @param nameOrId Name or ID of the hypervisor.
    @param poolId Name or ID of the resource pool.
    @param path (optional) Path to the resource container within the resource pool. The path may either
            be a relative path as specified by
            RelativePath, or may be a
            URL-encoded XenApp & XenDesktop resource path starting with `XDHyp:`; for
            example, as specified by
            XDPath.
    @param children (optional) Specifies the number of levels of children to enumerate.
            Default is `0`, meaning that only the object referred to by `path` is returned
            and its Children array will be
            left null.
            A special value of `-1` indicates that the entire resource hierarchy should be
            enumerated.  Use with care!  It may take a very long time to enumerate a large
            number of resources from a hypervisor, and the call may time out before
            completing.
    @param type (optional) If specified, limits the results to the specified resource type(s).
    @param showTagged (optional) By default, items which are tagged by XenDesktop are not shown. Set this to
            `true` to override that behavior.
    @param detail (optional) If `true`, full details of VMs, snapshots, and templates will be retrieved.
            This can be very time consuming and will reduce the performance of the call.
            May only be used if `path` refers to a VM, snapshot, or template resource.
            <!-- Internally this calls Get-HypConfigurationObjectForItem -->
    @param async (optional) Async request to get the resources with *path.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return Cloud-based hypervisor's availability zone.
            or
            Hypervisor GPU type resource.
            or
            Hypervisor security group resource.
            or
            Cloud-based hypervisor service offering.
            or
            Hypervisor storage information.
            or
            Cloud-based machine template.
            or
            Virtual machine.
            or
            VM/snapshot/template configuration.
            or
            Cloud-based virtual private cloud.
            or
            Hypervisor connection region.
            or
            A list of hypervisor resources.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/hypervisors/{nameOrId}/resourcePools/{poolId}/resources?"
        if path:
            url_ += "path=" + urllib.parse.quote(str(path))
        if children:
            url_ += "&children=" + urllib.parse.quote(str(children)) 
        if type:
            url_ += "&type=" + urllib.parse.quote(str(type)) 
        if showTagged:
            url_ += "&showTagged=" + urllib.parse.quote(str(showTagged)) 
        if detail:
            url_ += "&detail=" + urllib.parse.quote(str(detail)) 
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getHypervisorResourcePoolTestReport(nameOrId: str, poolId: str) -> str:
    """
    Get the most recent test report for a resource pool.
    @param nameOrId Name or ID of the hypervisor.
    @param poolId Name or ID of the resource pool.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return Last test report.  If no tests have been run, returns a 404 Not Found.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/Hypervisors/{nameOrId}/ResourcePools/{poolId}/TestReport"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getHypervisorServerHAAddresses(nameOrId: str) -> str:
    """
    Get hypervisor server HA addresses. Currently, it only valid for Citrix hypervisors.
    @param nameOrId The hypervisor connection name or id.
    @param async (optional) If the execution with async model.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return HypervisorServerHAAddressesResponseModel object.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/hypervisors/{nameOrId}/serverHAAddresses?"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getHypervisorTestReport(nameOrId: str) -> str:
    """
    Get the most recent test report for a hypervisor.
    @param nameOrId Name or ID of the hypervisor.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return Last test report.  If no tests have been run, returns a 404 Not Found.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/Hypervisors/{nameOrId}/TestReport"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getSupportHypervisors(zoneNameOrId: str, includeUnavailable: bool) -> str:
    """
    Get current server support hypervisors.
    @param async (optional) If execute this API asynchronous.
    @param zoneNameOrId (optional) The zone name or id.
    @param includeUnavailable (optional) Flag to show all supported hypervisor plugins.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return List of Hypervisor Plugin response model.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/hypervisors/supportedPlugins?"
        if zoneNameOrId:
            url_ += "zoneNameOrId=" + urllib.parse.quote(str(zoneNameOrId))
        if includeUnavailable:
            url_ += "&includeUnavailable=" + urllib.parse.quote(str(includeUnavailable)) 
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getHypervisorsAndResourcePools() -> str:
    """
    Get hypervisors and resource pools.
            This API is used for the hosting main view.
    @param async (optional) If execute this API asynchronous.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return List of Hypervisor Main View Response Model.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/hypervisorsAndResourcePools?"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getAbout() -> str:
    """
    Get About info of this Orchestration instance.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return About info.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/About"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getAdminAdministrators(limit: int) -> str:
    """
    Get administrators.
    @param limit (optional) The max number of administrators returned by this query.
            If not specified, the server might use a default limit of 250 items.
            If the specified value is larger than 1000, the server might reject the call.
            The default and maximum values depend on server settings.
    @param continuationToken (optional) If a query cannot be completed, the response will have a
            ContinuationToken set.
            To obtain more results from the query, pass the
            continuation token back into the query to get the next
            batch of results.
    @param async (optional) If `true`, the administrators will be fetched as a background task.
            The task will have the JobTypeGetAdminAdministrators
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return Collection of administrators in the site.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/Admin/Administrators?"
        if limit:
            url_ += "limit=" + urllib.parse.quote(str(limit))
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getAdministratorNamePreview(name: str, ignoreFormatCheck: bool) -> str:
    """
    Get preview report of the administrator user name.
    @param name Example: domain\\username or domain\\group
    @param ignoreFormatCheck (optional) Ignore name format check. If true,
                        will only check whether AD account available and not conflicting to existing administrators.
                        Note, invalid name will still be reported, only report error message will be changed.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/Admin/Administrators/{name}/NamePreview?"
        if ignoreFormatCheck:
            url_ += "ignoreFormatCheck=" + urllib.parse.quote(str(ignoreFormatCheck))
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getAdminAdministrator(nameOrId: str) -> str:
    """
    Get a single administrator
    @param nameOrId Name or id of the administrator.
                         May be specified as:
    
    The SID of the admin user or group.  Note: in directory types
                         other than Active Directory, the SID is a
                         computed property, and is not related to any representation of that
                         user within Active Directory.  However it can still be useful if the
                         user already has a generated SID; for example, if copying users from
                         one object to another.
    
    `Domain\\User` format.  This implies the directory type
                         Active Directory. If the Domain\\User is not
                         unique across AD Forests, the call will fail with an ambiguous name
                         error, status code 400.
    
    `Forest\\Domain\\User` format.  This implies the directory type
                         Active Directory. This is the preferred form
                         of specifying an Active Directory user by name, as the name is
                         guaranteed to be unambiguous.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return Response Model of this administrator.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/Admin/Administrators/{nameOrId}"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getDeleteAdministratorConsequence(nameOrId: str) -> str:
    """
    Preview the consequence of deleting an administrator.
    @param nameOrId Name or Id of the admin to delete.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/Admin/Administrators/{nameOrId}/PreviewDeleteConsequence"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getAdministratorReport(nameOrId: str) -> str:
    """
    Get report of the administrator.
    @param nameOrId Name or Id of the admin to report.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/Admin/Administrators/{nameOrId}/Report"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getAdminEffectiveRights(limit: int, if_None_Match: str) -> str:
    """
    Get the effective rights of the current user.  This is the union of
            all rights of the enabled administrators that the current user matches,
            taking into account group membership.
    @param limit (optional) The max number of admin rights returned by this query.
            If not specified, the server might use a default limit of 250 items.
            If the specified value is larger than 1000, the server might reject the call.
            The default and maximum values depend on server settings.
    @param continuationToken (optional) The continuationToken returned by the previous query.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param if_None_Match (optional) Optional ETag response header that was returned on the previous query.
    @param x_ActionName (optional) Orchestration Action Name
    @return List of admin rights.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/Admin/EffectiveRights?"
        if limit:
            url_ += "limit=" + urllib.parse.quote(str(limit))
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getPredefinedPermissionGroups(limit: int) -> str:
    """
    Get all permission groups.
    @param limit (optional) The max number of predefined permission groups returned by this query.
            If not specified, the server might use a default limit of 250 items.
            If the specified value is larger than 1000, the server might reject the call.
            The default and maximum values depend on server settings.
    @param continuationToken (optional) The continuationToken returned by the previous query.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return List of permission groups.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/Admin/PermissionGroups?"
        if limit:
            url_ += "limit=" + urllib.parse.quote(str(limit))
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getPredefinedPermissionsForGroups(id: str, limit: int) -> str:
    """
    Get all permissions for a permission group.
    @param id ID of the admin permission group to query.
    @param limit (optional) The max number of predefined permissions returned by this query.
            If not specified, the server might use a default limit of 250 items.
            If the specified value is larger than 1000, the server might reject the call.
            The default and maximum values depend on server settings.
    @param continuationToken (optional) The continuationToken returned by the previous query.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return The list of permissions in a permission group.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/Admin/PermissionGroups/{id}/Permissions?"
        if limit:
            url_ += "limit=" + urllib.parse.quote(str(limit))
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getPredefinedPermissions(limit: int) -> str:
    """
    Get all predefined permissions.
    @param limit (optional) The max number of predefined permissions returned by this query.
            If not specified, the server might use a default limit of 250 items.
            If the specified value is larger than 1000, the server might reject the call.
            The default and maximum values depend on server settings.
    @param continuationToken (optional) The continuationToken returned by the previous query.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return List of predefined permissions.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/Admin/Permissions?"
        if limit:
            url_ += "limit=" + urllib.parse.quote(str(limit))
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getAdminRoles(limit: int) -> str:
    """
    Get admin roles.
    @param limit (optional) The max number of admin roles returned by this query.
            If not specified, the server might use a default limit of 250 items.
            If the specified value is larger than 1000, the server might reject the call.
            The default and maximum values depend on server settings.
    @param continuationToken (optional) The continuationToken returned by the previous query.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return List of admin roles.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/Admin/Roles?"
        if limit:
            url_ += "limit=" + urllib.parse.quote(str(limit))
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getAdminRole(nameOrId: str) -> str:
    """
    Get details about a single admin role.
    @param nameOrId Name or ID of the admin role.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return The admin role details.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/Admin/Roles/{nameOrId}"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getAdminScopes(limit: int) -> str:
    """
    Get admin scopes.
    @param limit (optional) The max number of admin scopes returned by this query.
            If not specified, the server might use a default limit of 250 items.
            If the specified value is larger than 1000, the server might reject the call.
            The default and maximum values depend on server settings.
    @param continuationToken (optional) The continuationToken returned by the previous query.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return List of admin scopes.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/Admin/Scopes?"
        if limit:
            url_ += "limit=" + urllib.parse.quote(str(limit))
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getAdminScope(nameOrId: str) -> str:
    """
    Get details about a single admin scope.
    @param nameOrId Name or ID of the admin scope.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return The admin scope details.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/Admin/Scopes/{nameOrId}"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getAdminScopedObjects(nameOrId: str, limit: int) -> str:
    """
    Get the objects in an admin scope.
    @param nameOrId Name or ID of the admin scope.
    @param limit (optional) The max number of objects returned by this query.
            If not specified, the server might use a default limit of 250 items.
            If the specified value is larger than 1000, the server might reject the call.
            The default and maximum values depend on server settings.
    @param continuationToken (optional) The continuationToken returned by the previous query.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return List of scoped objects.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/Admin/Scopes/{nameOrId}/ScopedObjects?"
        if limit:
            url_ += "limit=" + urllib.parse.quote(str(limit))
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getAdminFolders(limit: int) -> str:
    """
    Get admin folders.
    @param async (optional) If `true`, the admin folders will be fetched as a background task.
            The task will have JobType GetAdminFolders.
    @param limit (optional) The max number of admin folders returned by this query.
            If not specified, the server might use a default limit of 250 items.
            If the specified value is larger than 1000, the server might reject the call.
            The default and maximum values depend on server settings.
    @param continuationToken (optional) The continuationToken returned by the previous query.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return List of admin folders.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/AdminFolders?"
        if limit:
            url_ += "limit=" + urllib.parse.quote(str(limit))
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getAdminFolder(pathOrId: str) -> str:
    """
    Get details about a single admin folder.
    @param pathOrId Path (URL-encoded) or ID of the admin folder.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return Admin folder details.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/AdminFolders/{pathOrId}"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getAdminFolderApplications(pathOrId: str, limit: int, fields: str) -> str:
    """
    Get the applications in an admin folder.
    @param pathOrId Path (URL-encoded) or ID of the admin folder.
    @param limit (optional) The max number of applications returned by this query.
            If not specified, the server might use a default limit of 250 items.
            If the specified value is larger than 1000, the server might reject the call.
            The default and maximum values depend on server settings.
    @param continuationToken (optional) If a query cannot be completed, the response will have a
            ContinuationToken set.
            To obtain more results from the query, pass the
            continuation token back into the query to get the next
            batch of results.
    @param fields (optional) Optional filter, removing unspecified properties that otherwise would
            have been sent by the server.
    @param async (optional) If `true`, Fetch applications under admin folder will be a background task.
            The task will have JobType GetAdminFolderApplications
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return List of applications in the folder.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/AdminFolders/{pathOrId}/Applications?"
        if limit:
            url_ += "limit=" + urllib.parse.quote(str(limit))
        if fields:
            url_ += "&fields=" + urllib.parse.quote(str(fields)) 
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getAdminFolderMachineCatalogs(pathOrId: str, limit: int, fields: str) -> str:
    """
    Get the machineCatalogs in an admin folder.
    @param pathOrId Path (URL-encoded) or ID of the admin folder.
    @param limit (optional) The max number of machine catalogs returned by this query.
            If not specified, the server might use a default limit of 250 items.
            If the specified value is larger than 1000, the server might reject the call.
            The default and maximum values depend on server settings.
    @param continuationToken (optional) The continuationToken returned by the previous query.
    @param fields (optional) Optional filter, removing unspecified properties that otherwise would
            have been sent by the server.
    @param async (optional) If `true`, Fetch machineCatalogs under admin folder will be a background task.
            The task will have JobType GetAdminFolderMachineCatalogs
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return List of machineCatalogs in the folder.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/AdminFolders/{pathOrId}/MachineCatalogs?"
        if limit:
            url_ += "limit=" + urllib.parse.quote(str(limit))
        if fields:
            url_ += "&fields=" + urllib.parse.quote(str(fields)) 
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getAdvisorRecommendations() -> str:
    """
    Get advisor recommendations.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/Advisor/Recommendations"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getAppLibPackageDiscoveryProfiles() -> str:
    """
    Get a list of AppLib Package Discovery profiles.
    @param async (optional) If `true`, the appLib package discovery profiles will be fetched as a background task.
            The task will have JobType GetAppLibPackageDiscoveryProfiles.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return A list of appLib package discovery profiles.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/AppLibPackageDiscovery/Profiles?"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getAppLibPackageDiscoveryProfile(uid: int) -> str:
    """
    Get details of an AppLib Package Discovery profile.
    @param uid Uid of the appLib package discovery profile that need to be fetched.
    @param async (optional) If `true`, the appLib package discovery profile will be fetched as a background task.
            The task will have JobType GetAppLibPackageDiscoveryProfile.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return One appLib package discovery profile details.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/AppLibPackageDiscovery/Profiles/{uid}?"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getAppLibPackageDiscoveryLatestSessionByProfileId(uid: int) -> str:
    """
    Get the latest AppLib Package Discovery session for the specified profile id.
    @param uid The profile id.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return The latest session for the specified profile
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/AppLibPackageDiscovery/Profiles/{uid}/LatestSession"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getAppLibPackageDiscoverySessions() -> str:
    """
    Get a list of AppLib Package Discovery sessions.
    @param async (optional) If `true`, the appLib package discovery sessions will be fetched as a background task.
            The task will have JobType GetAppLibPackageDiscoveries.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return A list of AppLib package discovery sessions.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/AppLibPackageDiscovery/Sessions?"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getAppLibPackageDiscovery(id: str) -> str:
    """
    Get details of an AppLib Package Discovery session.
    @param id Guid of the applib package discovery session that need to be fetched.
    @param async (optional) If `true`, the appLib package discovery session will be created as a background task.
            The task will have jobType GetAppLibPackageDiscovery>
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/AppLibPackageDiscovery/Sessions/{id}?"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getApplicationFolders() -> str:
    """
    Get application folders.
    @param async (optional) If `true`, the application folders will be fetched as a background task.
            The task will have JobType GetApplicationFolders.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return List of application folders.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/ApplicationFolders?"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getApplicationFolder(pathOrId: str) -> str:
    """
    Get details about a single application folder.
    @param pathOrId Path (URL-encoded) or ID of the application folder.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return Application folder details.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/ApplicationFolders/{pathOrId}"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getApplicationFolderApplications(pathOrId: str, limit: int, fields: str) -> str:
    """
    Get the applications in an application folder.
    @param pathOrId Path (URL-encoded) or ID of the application folder.
    @param limit (optional) The max number of applications returned by this query.
            If not specified, the server might use a default limit of 250 items.
            If the specified value is larger than 1000, the server might reject the call.
            The default and maximum values depend on server settings.
    @param continuationToken (optional) If a query cannot be completed, the response will have a
            ContinuationToken set.
            To obtain more results from the query, pass the
            continuation token back into the query to get the next
            batch of results.
    @param fields (optional) Optional filter, removing unspecified properties that otherwise would
            have been sent by the server.
    @param async (optional) If `true`, Fetch applications under application folder will be a background task.
            The task will have JobType GetApplicationFolderApplications
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return List of applications in the folder.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/ApplicationFolders/{pathOrId}/Applications?"
        if limit:
            url_ += "limit=" + urllib.parse.quote(str(limit))
        if fields:
            url_ += "&fields=" + urllib.parse.quote(str(fields)) 
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getApplicationGroups(adminFolder: str, limit: int, fields: str) -> str:
    """
    Get application groups.
    @param adminFolder (optional) Optional folder path (URL-encoded) or ID.  If not specified, all applications will
            be returned from all folders.
    @param limit (optional) The max number of application groups returned by this query.
            If not specified, the server might use a default limit of 250 items.
            If the specified value is larger than 1000, the server might reject the call.
            The default and maximum values depend on server settings.
    @param continuationToken (optional) If a query cannot be completed, the response will have a
            ContinuationToken set.
            To obtain more results from the query, pass the
            continuation token back into the query to get the next
            batch of results.
    @param fields (optional) Optional. A filter string containing object fields requested to be returned, the requested fields are separated by comma','.
    @param async (optional) If `true`, the application groups will be fetched as a background task.
            The task will have JobType GetApplicationGroups.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return List of application groups.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/ApplicationGroups?"
        if limit:
            url_ += "limit=" + urllib.parse.quote(str(limit))
        if adminFolder:
            url_ += "&adminFolder=" + urllib.parse.quote(str(adminFolder)) 
        if fields:
            url_ += "&fields=" + urllib.parse.quote(str(fields)) 
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getApplicationGroup(nameOrId: str, fields: str) -> str:
    """
    Get details of a single application group.
    @param nameOrId Name or ID of the application group. If the application group is present in an application group folder,
                         specify the name in this format: {application group folder path plus application group name}.
                         For example, FolderName1|FolderName2|ApplicationGroupName.
    @param fields (optional) Optional filter, removing unspecified properties that otherwise would
            have been sent by the server
    @param async (optional) If `true`, the application group details will be fetched as a background task.
            The task will have JobType GetApplicationGroup.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return Details of the application group.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/ApplicationGroups/{nameOrId}?"
        if fields:
            url_ += "fields=" + urllib.parse.quote(str(fields))
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getApplicationGroupApplications(nameOrId: str, limit: int, fields: str) -> str:
    """
    Get applications in an application group.
    @param nameOrId Name or ID of the application group. If the application group is present in an application group folder,
                        specify the name in this format: {application group folder path plus application group name}.
                        For example, FolderName1|FolderName2|ApplicationGroupName.
    @param limit (optional) The max number of applications returned by this query.
            If not specified, the server might use a default limit of 250 items.
            If the specified value is larger than 1000, the server might reject the call.
            The default and maximum values depend on server settings.
    @param continuationToken (optional) If a query cannot be completed, the response will have a
            ContinuationToken set.
            To obtain more results from the query, pass the
            continuation token back into the query to get the next
            batch of results.
    @param fields (optional) Optional filter, removing unspecified properties that otherwise would
            have been sent by the server.
    @param async (optional) If "true", the applications under the application group will be fetched as a background task.
            The task will have JobType GetApplicationGroupApplications
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return List of applications.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/ApplicationGroups/{nameOrId}/Applications?"
        if limit:
            url_ += "limit=" + urllib.parse.quote(str(limit))
        if fields:
            url_ += "&fields=" + urllib.parse.quote(str(fields)) 
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getApplicationGroupDeliveryGroups(nameOrId: str, limit: int) -> str:
    """
    Get delivery groups for an application group.
    @param nameOrId Name or ID of the application group. If the application group is present in an application group folder,
                        specify the name in this format: {application group folder path plus application group name}.
                        For example, FolderName1|FolderName2|ApplicationGroupName.
    @param limit (optional) The max number of delivery groups returned by this query.
            If not specified, the server might use a default limit of 250 items.
            If the specified value is larger than 1000, the server might reject the call.
            The default and maximum values depend on server settings.
    @param continuationToken (optional) If a query cannot be completed, the response will have a
            ContinuationToken set.
            To obtain more results from the query, pass the
            continuation token back into the query to get the next
            batch of results.
    @param async (optional) If `true`, the delivery groups fetch will run as a background task.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return List of delivery groups.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/ApplicationGroups/{nameOrId}/DeliveryGroups?"
        if limit:
            url_ += "limit=" + urllib.parse.quote(str(limit))
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getApplicationGroupTags(nameOrId: str, fields: str) -> str:
    """
    Get the tags for an application group.
    @param nameOrId Name or ID of the application group. If the application group is present in an application group folder,
                        specify the name in this format: {application group folder path plus application group name}.
                        For example, FolderName1|FolderName2|ApplicationGroupName.
    @param fields (optional) field to filter response model.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return List of tags.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/ApplicationGroups/{nameOrId}/Tags?"
        if fields:
            url_ += "fields=" + urllib.parse.quote(str(fields))
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getApplicationGroupsV2(adminFolder: str, limit: int, fields: str) -> str:
    """
    The V2  version of get application groups.
    @param adminFolder (optional) Optional folder path (URL-encoded) or ID.  If not specified, all applications will
            be returned from all folders.
    @param limit (optional) The max number of application groups returned by this query.
            If not specified, the server might use a default limit of 250 items.
            If the specified value is larger than 1000, the server might reject the call.
            The default and maximum values depend on server settings.
    @param continuationToken (optional) If a query cannot be completed, the response will have a
            ContinuationToken set.
            To obtain more results from the query, pass the
            continuation token back into the query to get the next
            batch of results.
    @param fields (optional) Optional. A filter string containing object fields requested to be returned, the requested fields are separated by comma','.
    @param async (optional) If `true`, the application groups will be fetched as a background task.
            The task will have JobType GetApplicationGroups.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return List of application groups.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/ApplicationGroupsV2?"
        if limit:
            url_ += "limit=" + urllib.parse.quote(str(limit))
        if adminFolder:
            url_ += "&adminFolder=" + urllib.parse.quote(str(adminFolder)) 
        if fields:
            url_ += "&fields=" + urllib.parse.quote(str(fields)) 
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getApplications(applicationFolder: str, limit: int, fields: str) -> str:
    """
    Get all applications.
    @param applicationFolder (optional) Optional folder path (URL-encoded) or ID.  If not specified, all applications will
            be returned from all folders.
    @param limit (optional) The max number of applications returned by this query.
            If not specified, the server might use a default limit of 250 items.
            If the specified value is larger than 1000, the server might reject the call.
            The default and maximum values depend on server settings.
    @param continuationToken (optional) If a query cannot be completed, the response will have a
            ContinuationToken set.
            To obtain more results from the query, pass the
            continuation token back into the query to get the next
            batch of results.
    @param fields (optional) Optional. A filter string containing object fields requested to be returned, the requested fields are separated by comma','.
    @param async (optional) If `true`, the applications will be fetched as a background task.
            The task will have JobType GetApplications.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return List of applications.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/Applications?"
        if limit:
            url_ += "limit=" + urllib.parse.quote(str(limit))
        if applicationFolder:
            url_ += "&applicationFolder=" + urllib.parse.quote(str(applicationFolder)) 
        if fields:
            url_ += "&fields=" + urllib.parse.quote(str(fields)) 
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getApplication(nameOrId: str, fields: str) -> str:
    """
    Get details of a single application.
    @param nameOrId Name or ID of the application. If the application is present in an application folder,
                        specify the name in this format: {application folder path plus application name}.
                        For example, FolderName1|FolderName2|ApplicationName.
    @param fields (optional)
    @param async (optional)
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return Application details.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/Applications/{nameOrId}?"
        if fields:
            url_ += "fields=" + urllib.parse.quote(str(fields))
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getApplicationAdministrators(nameOrId: str, limit: int) -> str:
    """
    Get administrators authorized to administer an application.
    @param nameOrId Name or ID of the application. If the application is present in an application folder,
                        specify the name in this format: {application folder path plus application name}.
                        For example, FolderName1|FolderName2|ApplicationName.
    @param limit (optional) The max number of administrators returned by this query.
            If not specified, the server might use a default limit of 250 items.
            If the specified value is larger than 1000, the server might reject the call.
            The default and maximum values depend on server settings.
    @param continuationToken (optional) If a query cannot be completed, the response will have a
            ContinuationToken set.
            To obtain more results from the query, pass the
            continuation token back into the query to get the next
            batch of results.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return List of administrators.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/Applications/{nameOrId}/Administrators?"
        if limit:
            url_ += "limit=" + urllib.parse.quote(str(limit))
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getApplicationApplicationGroups(nameOrId: str, limit: int) -> str:
    """
    Get application groups associated with an application.
    @param nameOrId Name or ID of the application. If the application is present in an application folder,
                        specify the name in this format: {application folder path plus application name}.
                        For example, FolderName1|FolderName2|ApplicationName.
    @param limit (optional) The max number of application groups returned by this query.
            If not specified, the server might use a default limit of 250 items.
            If the specified value is larger than 1000, the server might reject the call.
            The default and maximum values depend on server settings.
    @param continuationToken (optional) If a query cannot be completed, the response will have a
            ContinuationToken set.
            To obtain more results from the query, pass the
            continuation token back into the query to get the next
            batch of results.
    @param async (optional) If `true`, the application groups associated with the application will be fetched as a background task.
            The task will have JobType GetApplicationApplicationGroups.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return List of application groups.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/Applications/{nameOrId}/ApplicationGroups?"
        if limit:
            url_ += "limit=" + urllib.parse.quote(str(limit))
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getApplicationDeliveryGroups(nameOrId: str, limit: int, fields: str) -> str:
    """
    Get delivery groups associated with an application.
    @param nameOrId Name or ID of the application. If the application is present in an application folder,
                        specify the name in this format: {application folder path plus application name}.
                        For example, FolderName1|FolderName2|ApplicationName.
    @param limit (optional) The max number of delivery groups returned by this query.
            If not specified, the server might use a default limit of 250 items.
            If the specified value is larger than 1000, the server might reject the call.
            The default and maximum values depend on server settings.
    @param continuationToken (optional) If a query cannot be completed, the response will have a
            ContinuationToken set.
            To obtain more results from the query, pass the
            continuation token back into the query to get the next
            batch of results.
    @param fields (optional) Optional filter, removing unspecified properties that otherwise would
            have been sent by the server
    @param async (optional) If `true`, the delivery groups associated with the application will be fetched as a background task.
            The task will have JobType GetApplicationDeliveryGroups.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return List of delivery groups.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/Applications/{nameOrId}/DeliveryGroups?"
        if limit:
            url_ += "limit=" + urllib.parse.quote(str(limit))
        if fields:
            url_ += "&fields=" + urllib.parse.quote(str(fields)) 
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getApplicationFtas(nameOrId: str, skipVdaChecking: bool) -> str:
    """
    Get all file-types for an application.
    @param nameOrId Name or ID of the application. If the application is present in an application folder,
                        specify the name in this format: {application folder path plus application name}.
                        For example, FolderName1|FolderName2|ApplicationName.
    @param skipVdaChecking (optional) If true, don't check the status of VDAs before
                        getting the file-type association for the application.
    @param async (optional) If 'true', the file types will be gotten as a background task.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return List of file-type associations.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/Applications/{nameOrId}/FileTypes?"
        if skipVdaChecking:
            url_ += "skipVdaChecking=" + urllib.parse.quote(str(skipVdaChecking))
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getApplicationFta(nameOrId: str, extensionName: str) -> str:
    """
    Get a single file-type for an application.
    @param nameOrId Name or ID of the application. If the application is present in an application folder,
                        specify the name in this format: {application folder path plus application name}.
                        For example, FolderName1|FolderName2|ApplicationName.
    @param extensionName Extension name of the file-type.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return A single file-type association.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/Applications/{nameOrId}/FileTypes/{extensionName}"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getApplicationRecommendName(nameOrId: str, applicationFolder: str) -> str:
    """
    Get an application's recommend name.
    @param nameOrId Name or ID of the application. If the application is present in an application folder,
                        specify the name in this format: {application folder path plus application name}.
                        For example, FolderName1|FolderName2|ApplicationName.
    @param applicationFolder (optional) Name or ID of the application Folder
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return The recommend name of the application
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/Applications/{nameOrId}/RecommendName?"
        if applicationFolder:
            url_ += "applicationFolder=" + urllib.parse.quote(str(applicationFolder))
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getApplicationSessions(nameOrId: str, limit: int) -> str:
    """
    Get sessions in which the application is currently running.
    @param nameOrId Name or ID of the application. If the application is present in an application folder,
                        specify the name in this format: {application folder path plus application name}.
                        For example, FolderName1|FolderName2|ApplicationName.
    @param limit (optional) The max number of sessions returned by this query.
            If not specified, the server might use a default limit of 250 items.
            If the specified value is larger than 1000, the server might reject the call.
            The default and maximum values depend on server settings.
    @param continuationToken (optional) If a query cannot be completed, the response will have a
            ContinuationToken set.
            To obtain more results from the query, pass the
            continuation token back into the query to get the next
            batch of results.
    @param async (optional) If `true`, the application sessions will be fetched as a background task.
            The task will have JobType GetApplicationSessions.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return List of sessions.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/Applications/{nameOrId}/Sessions?"
        if limit:
            url_ += "limit=" + urllib.parse.quote(str(limit))
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getApplicationTags(nameOrId: str, fields: str) -> str:
    """
    Get tags associated with an application.
    @param nameOrId Name or ID of the application. If the application is present in an application folder,
                        specify the name in this format: {application folder path plus application name}.
                        For example, FolderName1|FolderName2|ApplicationName.
    @param fields (optional) field to filter response model.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return List of tags.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/Applications/{nameOrId}/Tags?"
        if fields:
            url_ += "fields=" + urllib.parse.quote(str(fields))
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def refreshAppVApplications() -> str:
    """
    Refresh the AppV Applications.
    @param async (optional) If `true`, the refresh operation will run as a background task.
            The task will have JobType RefreshAppVApplications.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return The applications that need to be deleted.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/Applications/RefreshAppVApplications?"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getApplicationsV2(applicationFolder: str, limit: int, fields: str) -> str:
    """
    The V2 of get all applications.
    @param applicationFolder (optional) Optional folder path (URL-encoded) or ID.  If not specified, all applications will
            be returned from all folders.
    @param limit (optional) The max number of applications returned by this query.
            If not specified, the server might use a default limit of 250 items.
            If the specified value is larger than 1000, the server might reject the call.
            The default and maximum values depend on server settings.
    @param continuationToken (optional) If a query cannot be completed, the response will have a
            ContinuationToken set.
            To obtain more results from the query, pass the
            continuation token back into the query to get the next
            batch of results.
    @param fields (optional) Optional. A filter string containing object fields requested to be returned, the requested fields are separated by comma','.
    @param async (optional) If `true`, the applications will be fetched as a background task.
            The task will have JobType GetApplications.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return List of applications.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/ApplicationsV2?"
        if limit:
            url_ += "limit=" + urllib.parse.quote(str(limit))
        if applicationFolder:
            url_ += "&applicationFolder=" + urllib.parse.quote(str(applicationFolder)) 
        if fields:
            url_ += "&fields=" + urllib.parse.quote(str(fields)) 
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getAppVIsolationGroups() -> str:
    """
    Get the App-V IsolationGroups configured in the site
    @param async (optional)
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return List of App-V IsolationGroups.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/AppVIsolationGroups?"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getAppVIsolationGroup(nameOrId: str) -> str:
    """
    Get the specified App-V IsolationGroups configured in the site
    @param nameOrId Name or UID of an isolationGroup.
    @param async (optional) If `true`, the tags will be modified as a background task.
            The task will have JobType GetAppVIsolationGroup.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return List of App-V IsolationGroups.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/AppVIsolationGroups/{nameOrId}?"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getAppVPackages(fields: str) -> str:
    """
    Get the App-V packages configured in the site
    @param async (optional) If `true`, the packages will be fetched as a background task.
            The task will have JobType GetAppVPackages.
    @param fields (optional) Optional. A filter string containing object fields requested to be returned, the requested fields are separated by comma','.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return List of App-V packages.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/AppVPackages?"
        if fields:
            url_ += "fields=" + urllib.parse.quote(str(fields))
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getAppVPackage(id: str, libraryUid: int, versionId: str, fields: str) -> str:
    """
    Get the details for a single App-V package within the site
    @param id ID of the App-V package.
    @param libraryUid (optional) ID of the library where the package is present.
    @param versionId (optional) Package version guid. If not specified, return the first
                        package with id.
    @param fields (optional) Optional. A filter string containing object fields requested to be returned, the requested fields are separated by comma','.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return App-V package details.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/AppVPackages/{id}?"
        if libraryUid:
            url_ += "libraryUid=" + urllib.parse.quote(str(libraryUid))
        if versionId:
            url_ += "&versionId=" + urllib.parse.quote(str(versionId)) 
        if fields:
            url_ += "&fields=" + urllib.parse.quote(str(fields)) 
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getAppVPackageApplications(id: str) -> str:
    """
    Get App-V applications within an App-V package
    @param id ID of the App-V package.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return App-V applications.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/AppVPackages/{id}/Applications"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getAppVPackageApplication(id: str, appId: str) -> str:
    """
    Get details for a single App-V application within an App-V package
    @param id ID of the App-V package.
    @param appId ID of the App-V application within the package.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return Details of the App-V application.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/AppVPackages/{id}/Applications/{appId}"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getPackageApplicationFileTypes(id: str, appId: str, libraryUid: int) -> str:
    """
    Get the fileTypes for an application within a package within the site.
    @param id ID of the package.
    @param appId Identifier of the application within the package.
    @param libraryUid ID of the library where the package is present.
    @param async (optional)
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return File types details.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/AppVPackages/{id}/Applications/{appId}/FileTypes?"
        if libraryUid:
            url_ += "libraryUid=" + urllib.parse.quote(str(libraryUid))
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getAppVPackageApplicationIcon(id: str, appId: str, iconFormat: str) -> str:
    """
    Get the icon for a single App-V application within an App-V package
            within the site.
    @param id ID of the App-V package.
    @param appId ID of the App-V application within the package.
    @param iconFormat (optional) Icon format.  Must be:
            `{mime-type};{width}x{height}x{colordepth}`
    
            where:
    
    _mime-type_ must be `image/png`.  (Other formats may be supported in future.)
    _width_ and _height_ are specified in pixels.
    _colordepth_ (optional) is either `8` or `24`.
    
            Optional. If not specified, only the raw icon data will be returned.
            Note that this is typically in ICO format, which some clients cannot
            display properly.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return Icon details.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/AppVPackages/{id}/Applications/{appId}/Icon?"
        if iconFormat:
            url_ += "iconFormat=" + urllib.parse.quote(str(iconFormat))
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getAppVPackageBrokerApplications(id: str, libraryUid: int, versionId: str, limit: int, fields: str) -> str:
    """
    Get Broker applications delivered from the App-V package
    @param id ID of the App-V package.
    @param libraryUid (optional) ID of the library where the package is present.
    @param versionId (optional) Package version Id.
    @param limit (optional) The max number of applications returned by this query.
            If not specified, the server might use a default limit of 250 items.
            If the specified value is larger than 1000, the server might reject the call.
            The default and maximum values depend on server settings.
    @param continuationToken (optional) If a query cannot be completed, the response will have a
            ContinuationToken set.
            To obtain more results from the query, pass the
            continuation token back into the query to get the next
            batch of results.
    @param fields (optional) The required fields.
    @param async (optional) If `true`, the applications will be fetched as a background task.
            The task will have JobType GetAppVPackageBrokerApplications.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return Broker applications.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/AppVPackages/{id}/BrokerApplications?"
        if limit:
            url_ += "limit=" + urllib.parse.quote(str(limit))
        if libraryUid:
            url_ += "&libraryUid=" + urllib.parse.quote(str(libraryUid)) 
        if versionId:
            url_ += "&versionId=" + urllib.parse.quote(str(versionId)) 
        if fields:
            url_ += "&fields=" + urllib.parse.quote(str(fields)) 
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getAppVPackageDeliveryGroups(id: str, libraryUid: int, versionId: str, limit: int, fields: str) -> str:
    """
    Get delivery groups which contain applications in the App-V package
    @param id ID of the App-V package.
    @param libraryUid (optional) ID of the library where the package is present.
    @param versionId (optional) Package version Id. If not specified, all delivery groups
                        that associated with id will be fetched.
    @param limit (optional) The max number of delivery groups returned by this query.
            If not specified, the server might use a default limit of 250 items.
            If the specified value is larger than 1000, the server might reject the call.
            The default and maximum values depend on server settings.
    @param continuationToken (optional) If a query cannot be completed, the response will have a
            ContinuationToken set.
            To obtain more results from the query, pass the
            continuation token back into the query to get the next
            batch of results.
    @param fields (optional) The required fields.
    @param async (optional) If `true`, the delivery groups will be fetched as a background task.
            The task will have JobType GetAppVPackageDelveryGroups.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return The delivery groups.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/AppVPackages/{id}/DeliveryGroups?"
        if limit:
            url_ += "limit=" + urllib.parse.quote(str(limit))
        if libraryUid:
            url_ += "&libraryUid=" + urllib.parse.quote(str(libraryUid)) 
        if versionId:
            url_ += "&versionId=" + urllib.parse.quote(str(versionId)) 
        if fields:
            url_ += "&fields=" + urllib.parse.quote(str(fields)) 
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getAppVPackageIcon(id: str, iconFormat: str) -> str:
    """
    Get the icon for a single App-V package within the site
    @param id ID of the App-V package.
    @param iconFormat (optional) Icon format.  Must be:
            `{mime-type};{width}x{height}x{colordepth}`
    
            where:
    
    _mime-type_ must be `image/png`.  (Other formats may be supported in future.)
    _width_ and _height_ are specified in pixels.
    _colordepth_ (optional) is either `8` or `24`.
    
            Optional. If not specified, only the raw icon data will be returned.
            Note that this is typically in ICO format, which some clients cannot
            display properly.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return Icon details.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/AppVPackages/{id}/Icon?"
        if iconFormat:
            url_ += "iconFormat=" + urllib.parse.quote(str(iconFormat))
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getAppVServers() -> str:
    """
    Get all App-V servers configured in the site
    @param async (optional)
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return List of App-V servers.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/AppVServers?"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getAppVServerPackages(server: str) -> str:
    """
    Get the packages from a single App-V server
    @param server Management Server address of the App-V server.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return List of App-V packages.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/AppVServers/{server}/Packages"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getAppVServerPackage(server: str, id: str) -> str:
    """
    Get the details for a single App-V package on a server.
    @param server ManagementServer address of
            the App-V server.
    @param id ID of the App-V package.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return App-V package details.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/AppVServers/{server}/Packages/{id}"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getAppVServerPackageApplications(server: str, id: str) -> str:
    """
    Get App-V applications within an App-V package on a server.
    @param server Management Server address of the App-V server.
    @param id ID of the App-V package.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return App-V applications.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/AppVServers/{server}/Packages/{id}/Applications"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getAppVServerPackageApplication(server: str, id: str, appId: str) -> str:
    """
    Get details for a single App-V application on a server.
    @param server Management Server address of the App-V server.
    @param id ID of the App-V package.
    @param appId ID of the App-V application within the package.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return Details of the App-V application.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/AppVServers/{server}/Packages/{id}/Applications/{appId}"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getAppVServerPackageApplicationIcon(server: str, id: str, appId: str, iconFormat: str) -> str:
    """
    Get the icon for a App-V application
    @param server Management Server address of the App-V server.
    @param id ID of the App-V package.
    @param appId ID of the App-V application within the package.
    @param iconFormat (optional) Icon format.  Must be:
            `{mime-type};{width}x{height}x{colordepth}`
    
            where:
    
    _mime-type_ must be `image/png`.  (Other formats may be supported in future.)
    _width_ and _height_ are specified in pixels.
    _colordepth_ (optional) is either `8` or `24`.
    
            Optional. If not specified, only the raw icon data will be returned.
            Note that this is typically in ICO format, which some clients cannot
            display properly.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return Icon details.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/AppVServers/{server}/Packages/{id}/Applications/{appId}/Icon?"
        if iconFormat:
            url_ += "iconFormat=" + urllib.parse.quote(str(iconFormat))
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getAppVServerPackageIcon(server: str, id: str, iconFormat: str) -> str:
    """
    Get the icon for a single App-V package on a server.
    @param server Management Server address of the App-V server.
    @param id ID of the App-V package.
    @param iconFormat (optional) Icon format.  Must be:
            `{mime-type};{width}x{height}x{colordepth}`
    
            where:
    
    _mime-type_ must be `image/png`.  (Other formats may be supported in future.)
    _width_ and _height_ are specified in pixels.
    _colordepth_ (optional) is either `8` or `24`.
    
            Optional. If not specified, only the raw icon data will be returned.
            Note that this is typically in ICO format, which some clients cannot
            display properly.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return Icon details.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/AppVServers/{server}/Packages/{id}/Icon?"
        if iconFormat:
            url_ += "iconFormat=" + urllib.parse.quote(str(iconFormat))
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getBackups(allFiles: bool) -> str:
    """
    Get backups
    @param async (optional) If `true`, it will be queried as a background task.
    @param allFiles (optional)
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return List of backups
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/BackupRestore?"
        if allFiles:
            url_ += "allFiles=" + urllib.parse.quote(str(allFiles))
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def downloadSingleBackup(backupName: str) -> str:
    """
    Download single backup
    @param backupName Name of the backp to download
    @param continuationToken (optional)
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/BackupRestore/{backupName}/Download?"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getHistoryForSpecificBackup(backupName: str) -> str:
    """
    Get all backup history for specific backup
    @param async (optional) If `true`, it will be queried as a background task.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return List of operational history
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/BackupRestore/{backupName}/History/All?"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getAllBackupHistory() -> str:
    """
    Get all backup history
    @param async (optional) If `true`, it will be queried as a background task.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return List of operational history
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/BackupRestore/History?"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getBackupHistoryForSpecificHistory(uid: str) -> str:
    """
    Get backup history for a single specific backup
    @param async (optional) If `true`, it will be queried as a background task.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return List of operational history
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/BackupRestore/History/{uid}?"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getInformation() -> str:
    """
    Get backup / restore information
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return BackupRestoreInformationRequestModel
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/BackupRestore/Information"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getBackupRestoreOptions() -> str:
    """
    Get backup / restore options
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return BackupRestoreStatusResponseModel
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/BackupRestore/Options"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getBackupSchedules() -> str:
    """
    Get backup schedules
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return BackupRestoreStatusResponseModel
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/BackupRestore/Schedules"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getBackupSchedule(uid: int) -> str:
    """
    Get single backup schedule
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return BackupRestoreScheduleModel
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/BackupRestore/Schedules/{Uid}"
        if uid:
            url_ += "uid=" + urllib.parse.quote(str(uid))
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getCurrentActionStatus() -> str:
    """
    Get backup / restore status
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return BackupRestoreStatusResponseModel
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/BackupRestore/Status"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getBlobStorage() -> str:
    """
    Get Blob Storage Information
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/BackupRestore/Storage"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def validateStorage() -> str:
    """
    Validate Storage
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/BackupRestore/Storage/Validate"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getFirstLogDate() -> str:
    """
    Get first log date
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return LogSiteResponseModel
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/ConfigLog/GetFirstLogDate"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getLogSite() -> str:
    """
    Get logging site details.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return LogSiteResponseModel
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/ConfigLog/LoggingSite"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getOperations(text: str, days: int, searchDateOption: str, timeDiff: int, limit: int, x_TimeZone: str) -> str:
    """
    Get configuration log operations.
    @param text (optional) Optional; Text pattern to match, which is case-insensitive and may include the wildcard "*".
            If specified, only return records which Text matched pattern.
            Otherwise, all records will be returned.
    @param days (optional) Optional; Number of days of history to retrieve.
            Note: This parameter is exclusive with parameter searchDateOption.
            If neither is specified, all records will be returned.
    @param searchDateOption (optional) Optional; Specific time filters for searching operations.
            Note: This parameter is exclusive with parameter days.
            If neither is specified, all records will be returned.
    @param timeDiff (optional) [DEPRECATED]
            This parameter is deprecated, please use "X-TimeZone" header instead.
            Optional; The time difference in seconds between client time and UTC time.
            Note: The value must be a valid UTC offset, e.g. UTC+8, timeDiff=28800; UTC-5, timeDiff=-18000.
            If not specified, server local time will be referenced.
    @param limit (optional) Optional; The max number of operations returned by this query.
            If not specified, the server might use a default limit of 250 items.
            If the specified value is larger than 1000, the server might reject the call.
            The default and maximum values depend on server settings.
    @param continuationToken (optional) If a query cannot be completed, the response will have a ContinuationToken set.
            To obtain more results from the query, pass the continuation token back into the query to get the next batch of results.
    @param async (optional) If 'true', the get operations will be executed as a background task.
            The task wil have JobTypeGetOperations.
            When the task is complete it will redirect to GetJobResults.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_TimeZone (optional) Time zone of the client. If specified, must be a valid Windows Id or Utc Offset from IANA (https://www.iana.org/time-zones) time zones.
            Example: UTC or +00:00
    @param x_ActionName (optional) Orchestration Action Name
    @return List of configuration log operations.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/ConfigLog/Operations?"
        if limit:
            url_ += "limit=" + urllib.parse.quote(str(limit))
        if text:
            url_ += "&text=" + urllib.parse.quote(str(text)) 
        if days:
            url_ += "&days=" + urllib.parse.quote(str(days)) 
        if searchDateOption:
            url_ += "&searchDateOption=" + urllib.parse.quote(str(searchDateOption)) 
        if timeDiff:
            url_ += "&timeDiff=" + urllib.parse.quote(str(timeDiff)) 
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getOperation(id: str) -> str:
    """
    Get a high level log operation.
    @param id ID of the operation.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return The high level log operation.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/ConfigLog/Operations/{id}"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getLowLevelOperations(id: str, limit: int) -> str:
    """
    Get the detailed low level operations of a high level operation.
    @param id id of specified high level operation
    @param limit (optional) The max number of low level operations returned by this query.
            If not specified, the server might use a default limit of 250 items.
            If the specified value is larger than 1000, the server might reject the call.
            The default and maximum values depend on server settings.
    @param continuationToken (optional) The continuationToken returned by the previous query.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return A list of low level operations.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/ConfigLog/Operations/{id}/LowLevelOperations?"
        if limit:
            url_ += "limit=" + urllib.parse.quote(str(limit))
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getPowerShellHistory() -> str:
    """
    The history of executed PowerShell
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return The executed PowerShell history.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/ConfigLog/PowerShellHistory"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getConfigurationSlots(limit: int) -> str:
    """
    Get the list of configuration slots.
    @param limit (optional) The max number of configuration slots returned by this query.
            If not specified, the server might use a default limit of 250 items.
            If the specified value is larger than 1000, the server might reject the call.
            The default and maximum values depend on server settings.
    @param continuationToken (optional) The continuationToken returned by the previous query.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return List of configuration slots.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/ConfigurationSlots?"
        if limit:
            url_ += "limit=" + urllib.parse.quote(str(limit))
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getConfigurationSlot(nameOrId: str) -> str:
    """
    Get a single configuration slot.
    @param nameOrId Name or id of the configuration slot.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return Details of the configuration slot.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/ConfigurationSlots/{nameOrId}"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getConfigurationSlotMachineConfigurations(nameOrId: str, limit: int) -> str:
    """
    Get machine configurations associated with a configuration slot.
    @param nameOrId Name or id of the configuration slot.
    @param limit (optional) The max number of machine configurations returned by this query.
            If not specified, the server might use a default limit of 250 items.
            If the specified value is larger than 1000, the server might reject the call.
            The default and maximum values depend on server settings.
    @param continuationToken (optional) The continuationToken returned by the previous query.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return List of machine configurations.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/ConfigurationSlots/{nameOrId}/MachineConfigurations?"
        if limit:
            url_ += "limit=" + urllib.parse.quote(str(limit))
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getMachineConfigurations(limit: int) -> str:
    """
    Get the list of machine configurations.
    @param limit (optional) The max number of machine configurations returned by this query.
            If not specified, the server might use a default limit of 250 items.
            If the specified value is larger than 1000, the server might reject the call.
            The default and maximum values depend on server settings.
    @param continuationToken (optional) The continuationToken returned by the previous query.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return List of machine configurations.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/MachineConfigurations?"
        if limit:
            url_ += "limit=" + urllib.parse.quote(str(limit))
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getMachineConfiguration(uid: int) -> str:
    """
    Get a single machine configuration.
    @param uid Unique id of the machine configuration.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return Details of the machine configuration.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/MachineConfigurations/{uid}"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getDatabases() -> str:
    """
    Get the list of all databases.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return List of databases.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/Databases"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getDatabase(dataStore: str) -> str:
    """
    Get a single database.
    @param dataStore Datastore.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return Database info.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/Databases/{dataStore}"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getDeliveryControllers() -> str:
    """
    Get the list of delivery controllers that are available to the customer and visible to the admin.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return List of delivery controllers.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/DeliveryControllers"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getDeliveryController(nameOrId: str) -> str:
    """
    Get the details about a single delivery controller.
    @param nameOrId Name or ID of the delivery controller.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return delivery controller details.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/DeliveryControllers/{nameOrId}"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getDeliveryGroups(adminFolder: str, limit: int, fields: str) -> str:
    """
    Get all delivery groups.
    @param adminFolder (optional) Optional folder path (URL-encoded) or ID.  If not specified, all delivery groups will
            be returned from all folders.
    @param async (optional)
    @param limit (optional) The max number of delivery groups returned by this query.
            If not specified, the server might use a default limit of 250 items.
            If the specified value is larger than 1000, the server might reject the call.
            The default and maximum values depend on server settings.
    @param continuationToken (optional) If a query cannot be completed, the response will have a
            ContinuationToken set.
            To obtain more results from the query, pass the
            continuation token back into the query to get the next
            batch of results.
    @param fields (optional) Optional. A filter string containing object fields requested to be returned, the requested fields are separated by comma','.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return List of all delivery groups.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/DeliveryGroups?"
        if limit:
            url_ += "limit=" + urllib.parse.quote(str(limit))
        if adminFolder:
            url_ += "&adminFolder=" + urllib.parse.quote(str(adminFolder)) 
        if fields:
            url_ += "&fields=" + urllib.parse.quote(str(fields)) 
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getDeliveryGroup(nameOrId: str, fields: str) -> str:
    """
    Get details of a single delivery group.
    @param nameOrId Name or ID of the delivery group. If the delivery group is present in a delivery group folder,
                        specify the name in this format: {delivery group folder path plus delivery group name}.
                        For example, FolderName1|FolderName2|DeliveryGroupName.
    @param fields (optional) Optional parameter, removing unspecified properties that otherwise would have been sent by the server.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return Detail model of the delivery group.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/DeliveryGroups/{nameOrId}?"
        if fields:
            url_ += "fields=" + urllib.parse.quote(str(fields))
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getDeliveryGroupsAdministrators(nameOrId: str, limit: int) -> str:
    """
    Get administrators who can administer a delivery group.
    @param nameOrId Name or ID of the delivery group. If the delivery group is present in a delivery group folder,
                        specify the name in this format: {delivery group folder path plus delivery group name}.
                        For example, FolderName1|FolderName2|DeliveryGroupName.
    @param limit (optional) The max number of administrators returned by this query.
            If not specified, the server might use a default limit of 250 items.
            If the specified value is larger than 1000, the server might reject the call.
            The default and maximum values depend on server settings.
    @param continuationToken (optional) If a query cannot be completed, the response will have a
            ContinuationToken set.
            To obtain more results from the query, pass the
            continuation token back into the query to get the next
            batch of results.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return List of administrators.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/DeliveryGroups/{nameOrId}/Administrators?"
        if limit:
            url_ += "limit=" + urllib.parse.quote(str(limit))
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getDeliveryGroupAdvancedAccessPolicies(nameOrId: str, limit: int) -> str:
    """
    Get the advanced access policies associated with a delivery group.
    @param nameOrId Name or ID of the delivery group. If the delivery group is present in a delivery group folder,
                        specify the name in this format: {delivery group folder path plus delivery group name}.
                        For example, FolderName1|FolderName2|DeliveryGroupName.
    @param limit (optional) The max number of advanced access policies returned by this query.
            If not specified, the server might use a default limit of 250 items.
            If the specified value is larger than 1000, the server might reject the call.
            The default and maximum values depend on server settings.
    @param continuationToken (optional) If a query cannot be completed, the response will have a
            ContinuationToken set.
            To obtain more results from the query, pass the
            continuation token back into the query to get the next
            batch of results.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return List of advanced access policies associated with the delivery group.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/DeliveryGroups/{nameOrId}/AdvancedAccessPolicies?"
        if limit:
            url_ += "limit=" + urllib.parse.quote(str(limit))
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getDeliveryGroupAdvancedAccessPolicy(nameOrId: str, policyId: str) -> str:
    """
    Get the details of a single advanced access policy associated with a delivery group.
    @param nameOrId Name or ID of the delivery group. If the delivery group is present in a delivery group folder,
                        specify the name in this format: {delivery group folder path plus delivery group name}.
                        For example, FolderName1|FolderName2|DeliveryGroupName.
    @param policyId ID of the advanced access policy.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return Details of the access policy.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/DeliveryGroups/{nameOrId}/AdvancedAccessPolicies/{policyId}"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getDeliveryGroupsApplicationGroups(nameOrId: str, limit: int) -> str:
    """
    Get the application groups associated with a delivery group.
    @param nameOrId Name or ID of the delivery group. If the delivery group is present in a delivery group folder,
                        specify the name in this format: {delivery group folder path plus delivery group name}.
                        For example, FolderName1|FolderName2|DeliveryGroupName.
    @param limit (optional) The max number of application groups returned by this query.
            If not specified, the server might use a default limit of 250 items.
            If the specified value is larger than 1000, the server might reject the call.
            The default and maximum values depend on server settings.
    @param continuationToken (optional) If a query cannot be completed, the response will have a
            ContinuationToken set.
            To obtain more results from the query, pass the
            continuation token back into the query to get the next
            batch of results.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return List of application groups.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/DeliveryGroups/{nameOrId}/ApplicationGroups?"
        if limit:
            url_ += "limit=" + urllib.parse.quote(str(limit))
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getDeliveryGroupApplications(nameOrId: str, limit: int) -> str:
    """
    Get the applications associated with a delivery group.
    @param nameOrId Name or ID of the delivery group. If the delivery group is present in a delivery group folder,
                        specify the name in this format: {delivery group folder path plus delivery group name}.
                        For example, FolderName1|FolderName2|DeliveryGroupName.
    @param async (optional)
    @param limit (optional) The max number of applications returned by this query.
            If not specified, the server might use a default limit of 250 items.
            If the specified value is larger than 1000, the server might reject the call.
            The default and maximum values depend on server settings.
    @param continuationToken (optional) If a query cannot be completed, the response will have a
            ContinuationToken set.
            To obtain more results from the query, pass the
            continuation token back into the query to get the next
            batch of results.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return List of applications.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/DeliveryGroups/{nameOrId}/Applications?"
        if limit:
            url_ += "limit=" + urllib.parse.quote(str(limit))
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getDeliveryGroupAutoscaleGroupPlugins(nameOrId: str, type: str) -> str:
    """
    Get the autoscale group plugins for the specified delivery group.
    @param nameOrId Name or ID of the delivery group. If the delivery group is present in an admin folder,
                        specify the name in this format: {admin folder path plus delivery group name}.
                        For example, FolderName1|FolderName2|DeliveryGroupName.
    @param type (optional) The type of the plugin.
                        The supported types are: "Holiday", "Intelligent"
    @param async (optional) If 'true', the autoscale group plugins will be gotten asynchronously.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/DeliveryGroups/{nameOrId}/AutoscaleGroupPlugins?"
        if type:
            url_ += "type=" + urllib.parse.quote(str(type))
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getDeliveryGroupsDesktops(nameOrId: str, limit: int) -> str:
    """
    Get the published desktops associated with a delivery group.
    @param nameOrId Name or ID of the delivery group. If the delivery group is present in a delivery group folder,
                        specify the name in this format: {delivery group folder path plus delivery group name}.
                        For example, FolderName1|FolderName2|DeliveryGroupName.
    @param async (optional)
    @param limit (optional) The max number of desktops returned by this query.
            If not specified, the server might use a default limit of 250 items.
            If the specified value is larger than 1000, the server might reject the call.
            The default and maximum values depend on server settings.
    @param continuationToken (optional) If a query cannot be completed, the response will have a
            ContinuationToken set.
            To obtain more results from the query, pass the
            continuation token back into the query to get the next
            batch of results.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return List of desktops.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/DeliveryGroups/{nameOrId}/Desktops?"
        if limit:
            url_ += "limit=" + urllib.parse.quote(str(limit))
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getDeliveryGroupsMachineCatalogs(nameOrId: str, limit: int, fields: str) -> str:
    """
    Get machine catalogs associated with a delivery group.
    @param nameOrId Name or ID of the delivery group. If the delivery group is present in a delivery group folder,
                        specify the name in this format: {delivery group folder path plus delivery group name}.
                        For example, FolderName1|FolderName2|DeliveryGroupName.
    @param limit (optional) The max number of machine catalogs returned by this query.
            If not specified, the server might use a default limit of 250 items.
            If the specified value is larger than 1000, the server might reject the call.
            The default and maximum values depend on server settings.
    @param continuationToken (optional) If a query cannot be completed, the response will have a
            ContinuationToken set.
            To obtain more results from the query, pass the
            continuation token back into the query to get the next
            batch of results.
    @param fields (optional) Optional parameters, removing unspecified properties that otherwise would have been sent by the server.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return List of machine catalogs associated with a delivery group.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/DeliveryGroups/{nameOrId}/MachineCatalogs?"
        if limit:
            url_ += "limit=" + urllib.parse.quote(str(limit))
        if fields:
            url_ += "&fields=" + urllib.parse.quote(str(fields)) 
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getDeliveryGroupsMachineCatalogDetails(nameOrId: str, id: str) -> str:
    """
    Get the details of machine catalog associated with a delivery group.
    @param nameOrId Name or ID of the delivery group. If the delivery group is present in a delivery group folder,
                        specify the name in this format: {delivery group folder path plus delivery group name}.
                        For example, FolderName1|FolderName2|DeliveryGroupName.
    @param id Name or ID of the machine catalog. If the catalog is present in a catalog folder,
                        specify the name in this format: {delivery group folder path plus catalog name}.
                        For example, FolderName1|FolderName2|CatalogName.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return Details of machine catalog.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/DeliveryGroups/{nameOrId}/MachineCatalogs/{id}"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getDeliveryGroupMachines(nameOrId: str, limit: int) -> str:
    """
    Get the machines associated with a delivery group.
    @param nameOrId Name or ID of the delivery group. If the delivery group is present in a delivery group folder,
                        specify the name in this format: {delivery group folder path plus delivery group name}.
                        For example, FolderName1|FolderName2|DeliveryGroupName.
    @param limit (optional) The max number of machines returned by this query.
            If not specified, the server might use a default limit of 250 items.
            If the specified value is larger than 1000, the server might reject the call.
            The default and maximum values depend on server settings.
    @param continuationToken (optional) If a query cannot be completed, the response will have a
            ContinuationToken set.
            To obtain more results from the query, pass the
            continuation token back into the query to get the next
            batch of results.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return List of machines.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/DeliveryGroups/{nameOrId}/Machines?"
        if limit:
            url_ += "limit=" + urllib.parse.quote(str(limit))
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getDeliveryGroupPowerTimeSchemes(nameOrId: str, limit: int) -> str:
    """
    Get the power time schemes associated with a delivery group.
    @param nameOrId Name or ID of the delivery group. If the delivery group is present in a delivery group folder,
                        specify the name in this format: {delivery group folder path plus delivery group name}.
                        For example, FolderName1|FolderName2|DeliveryGroupName.
    @param limit (optional) The max number of power time schemes returned by this query.
            If not specified, the server might use a default limit of 250 items.
            If the specified value is larger than 1000, the server might reject the call.
            The default and maximum values depend on server settings.
    @param continuationToken (optional) If a query cannot be completed, the response will have a
            ContinuationToken set.
            To obtain more results from the query, pass the
            continuation token back into the query to get the next
            batch of results.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return List of power time schemes.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/DeliveryGroups/{nameOrId}/PowerTimeSchemes?"
        if limit:
            url_ += "limit=" + urllib.parse.quote(str(limit))
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getDeliveryGroupPowerTimeScheme(nameOrId: str, schemeNameOrId: str) -> str:
    """
    Get the details about a single power time scheme associated with a delivery
            group.
    @param nameOrId Name or ID of the delivery group. If the delivery group is present in a delivery group folder,
                        specify the name in this format: {delivery group folder path plus delivery group name}.
                        For example, FolderName1|FolderName2|DeliveryGroupName.
    @param schemeNameOrId Name or ID of the power time scheme.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return Details about a power time scheme.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/DeliveryGroups/{nameOrId}/PowerTimeSchemes/{schemeNameOrId}"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getDeiliveryGroupProjectedAutoscaleMachines(nameOrId: str, fromDate: str, numberOfDays: int) -> str:
    """
    Gets the projected number of machines that Autoscale will keep powered on over the specified period
    @param nameOrId Name or ID of the delivery group. If the delivery group is present in a delivery group folder,
                        specify the name in this format: {delivery group folder path plus delivery group name}.
                        For example, FolderName1|FolderName2|DeliveryGroupName.
    @param fromDate (optional) Gets projected Autoscale machines for the period starting at the specified UTC date.
            specify the date in this format:
            For example, yyyy-MM-dd'T'HH:mm:ssZ.
    @param numberOfDays (optional) Gets projected Autoscale machines for the period consisting of the specified number of days.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return The projected number of machines over the specified period.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/DeliveryGroups/{nameOrId}/ProjectedAutoscaleMachines?"
        if fromDate:
            url_ += "fromDate=" + urllib.parse.quote(str(fromDate))
        if numberOfDays:
            url_ += "&numberOfDays=" + urllib.parse.quote(str(numberOfDays)) 
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getDeliveryGroupRebootSchedules(nameOrId: str, limit: int) -> str:
    """
    Get the reboot schedules associated with a delivery group.
    @param nameOrId Name or ID of the delivery group. If the delivery group is present in a delivery group folder,
                        specify the name in this format: {delivery group folder path plus delivery group name}.
                        For example, FolderName1|FolderName2|DeliveryGroupName.
    @param limit (optional) The max number of reboot schedules returned by this query.
            If not specified, the server might use a default limit of 250 items.
            If the specified value is larger than 1000, the server might reject the call.
            The default and maximum values depend on server settings.
    @param continuationToken (optional) If a query cannot be completed, the response will have a
            ContinuationToken set.
            To obtain more results from the query, pass the
            continuation token back into the query to get the next
            batch of results.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return List of reboot schedules.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/DeliveryGroups/{nameOrId}/RebootSchedules?"
        if limit:
            url_ += "limit=" + urllib.parse.quote(str(limit))
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getDeliveryGroupRebootSchedule(nameOrId: str, scheduleNameOrId: str) -> str:
    """
    Get the details about a single reboot schedule associated
            with a delivery group.
    @param nameOrId Name or ID of the delivery group. If the delivery group is present in a delivery group folder,
                        specify the name in this format: {delivery group folder path plus delivery group name}.
                        For example, FolderName1|FolderName2|DeliveryGroupName.
    @param scheduleNameOrId Name or ID of the reboot schedule.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return Details about a reboot schedule.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/DeliveryGroups/{nameOrId}/RebootSchedules/{scheduleNameOrId}"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getDeliveryGroupStartMenuApplications(nameOrId: str, tagRestriction: str) -> str:
    """
    Get the start menu applications from a machine in the delivery group.
    @param nameOrId Name or ID of the delivery group. If the delivery group is present in a delivery group folder,
                        specify the name in this format: {delivery group folder path plus delivery group name}.
                        For example, FolderName1|FolderName2|DeliveryGroupName.
    @param tagRestriction (optional) The tag name for restriction.
    @param async (optional) If `true`, the start menu applications will be queried as a background task.
            This is recommended as this operation may cause a power action, turning on a
            machine in order to gather the data. This may take some time to run, and if it
            exceeds 90 seconds the request may time out.
            The task will have JobType GetStartMenuApplications.
            When the task is complete it will redirect to
            GetJobResults.
            The job's Parameters will contain properties:
    
    _Id_ - ID of the delivery group from which start menu applications are being obtained,
    _Name_ - Name of the delivery group from which start menu applications are being obtained.
    _MachineId_ - ID of the machine selected, from which the start menu applications are being obtained; will be present in Parameters only after a machine is selected.
    _MachineName_ - Name of the machine selected, from which the start menu applications are being obtained; will be present in Parameters only after a machine is selected.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return List of start menu applications.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/DeliveryGroups/{nameOrId}/StartMenuApplications?"
        if tagRestriction:
            url_ += "tagRestriction=" + urllib.parse.quote(str(tagRestriction))
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getDeliveryGroupTags(nameOrId: str, fields: str) -> str:
    """
    Get tags associated with a delivery group.
    @param nameOrId Name or ID of the delivery group. If the delivery group is present in a delivery group folder,
                        specify the name in this format: {delivery group folder path plus delivery group name}.
                        For example, FolderName1|FolderName2|DeliveryGroupName.
    @param fields (optional) Optional parameter, removing unspecified properties that otherwise would have been sent by the server.
    @param async (optional) If `true`, this request will be handled asynchronously.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return List of tags.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/DeliveryGroups/{nameOrId}/Tags?"
        if fields:
            url_ += "fields=" + urllib.parse.quote(str(fields))
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getDeliveryGroupTestReport(nameOrId: str) -> str:
    """
    Get the most recent test report of a delivery group.
    @param nameOrId Name or ID of the delivery group. If the delivery group is present in a delivery group folder,
                        specify the name in this format: {delivery group folder path plus delivery group name}.
                        For example, FolderName1|FolderName2|DeliveryGroupName.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return Last test report.  If no tests have been run, returns a 404
            Not Found.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/DeliveryGroups/{nameOrId}/TestReport"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getDeliveryGroupsUsage(nameOrId: str, limit: int) -> str:
    """
    Get usage data about a delivery group.
    @param nameOrId Name or ID of the delivery group. If the delivery group is present in a delivery group folder,
                        specify the name in this format: {delivery group folder path plus delivery group name}.
                        For example, FolderName1|FolderName2|DeliveryGroupName.
    @param continuationToken (optional) If a query cannot be completed, the response will have a
            ContinuationToken set.
            To obtain more results from the query, pass the
            continuation token back into the query to get the next
            batch of results.
    @param limit (optional) The max number of usage data items returned by this query.
            If not specified, the server might use a default limit of 250 items.
            If the specified value is larger than 1000, the server might reject the call.
            The default and maximum values depend on server settings.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return List of usage data.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/DeliveryGroups/{nameOrId}/Usage?"
        if limit:
            url_ += "limit=" + urllib.parse.quote(str(limit))
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getAutoscalePluginTemplates(type: str) -> str:
    """
    Return all autoscale plugin configuration templates for the specified plugin type.
    @param type The type of the plugin.
                        The supported types are: "Holiday", "Intelligent"
    @param async (optional) If 'true', the templates will be gotten asynchronously.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return List of the autoscale plugin configuration templates.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/DeliveryGroups/AutoscalePlugin/{type}/Templates?"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getAutoscalePluginTemplate(type: str, name: str) -> str:
    """
    @param async (optional)
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/DeliveryGroups/AutoscalePlugin/{type}/Templates/{name}?"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getDeliveryGroupsV2(adminFolder: str, limit: int, fields: str) -> str:
    """
    The V2 version of get all delivery groups.
    @param adminFolder (optional) Optional folder path (URL-encoded) or ID.  If not specified, all delivery groups will
            be returned from all folders.
    @param async (optional)
    @param limit (optional) The max number of delivery groups returned by this query.
            If not specified, the server might use a default limit of 250 items.
            If the specified value is larger than 1000, the server might reject the call.
            The default and maximum values depend on server settings.
    @param continuationToken (optional) If a query cannot be completed, the response will have a
            ContinuationToken set.
            To obtain more results from the query, pass the
            continuation token back into the query to get the next
            batch of results.
    @param fields (optional) Optional. A filter string containing object fields requested to be returned, the requested fields are separated by comma','.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return List of all delivery groups.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/DeliveryGroupsV2?"
        if limit:
            url_ += "limit=" + urllib.parse.quote(str(limit))
        if adminFolder:
            url_ += "&adminFolder=" + urllib.parse.quote(str(adminFolder)) 
        if fields:
            url_ += "&fields=" + urllib.parse.quote(str(fields)) 
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getEnrollments(limit: int) -> str:
    """
    Get the list of all enrollments in the site.
    @param limit (optional) The max number of enrollments returned by this query.
            If not specified, the server might use a default limit of 250 items.
            If the specified value is larger than 1000, the server might reject the call.
            The default and maximum values depend on server settings.
    @param continuationToken (optional) If a query cannot be completed, the response will have a
            ContinuationToken set.
            To obtain more results from the query, pass the
            continuation token back into the query to get the next
            batch of results.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return List of enrollments.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/enrollments?"
        if limit:
            url_ += "limit=" + urllib.parse.quote(str(limit))
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getEnrollment(id: str) -> str:
    """
    Get a single enrollment from the trust.
    @param id ID of the enrollment.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return List of enrollments.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/enrollments/{id}"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getBearerTokenWithWindowsAuthentication() -> str:
    """
    Exchange the FMA token via Windows Authentication.
            Kerberos or NTLM authentication required for current Web Api.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return AuthTokenResponseModel object.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id} + /tokens"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getFilterDefinitions() -> str:
    """
    Get all filter definitions.
    @param customerId The customer ID
    @param siteId The site ID
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return Filter definitions
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/gpo/filterDefinitions"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def readGpoFilters(policyGuid: str) -> str:
    """
    Read filters defined in a policy. A policy in a policy set of type SiteTemplates or CustomTemplates does not
            have filters.
    @param customerId The customer ID
    @param siteId The site ID
    @param policyGuid The GUID of the policy from which filters are read
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return The filters read
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/gpo/filters?"
        if policyGuid:
            url_ += "policyGuid=" + urllib.parse.quote(str(policyGuid))
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def readGpoFilter(filterGuid: str) -> str:
    """
    Read a specific filter.
    @param customerId The customer ID
    @param siteId The site ID
    @param filterGuid The GUID of the filter to be read
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return The filter read
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/gpo/filters/{filterGuid}"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def readGpoPolicies(policySetGuid: str, withSettings: bool, withFilters: bool) -> str:
    """
    Read all policies defined in a policy set. Policy templates don't have filters.
    @param customerId The customer ID
    @param siteId The site ID
    @param policySetGuid The GUID of the policy set from which policies are read
    @param withSettings (optional) If set to true, settings in the policy are read
    @param withFilters (optional) If set to true, filters in the policy are read
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return Collection of policies
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/gpo/policies?"
        if policySetGuid:
            url_ += "policySetGuid=" + urllib.parse.quote(str(policySetGuid))
        if withSettings:
            url_ += "&withSettings=" + urllib.parse.quote(str(withSettings)) 
        if withFilters:
            url_ += "&withFilters=" + urllib.parse.quote(str(withFilters)) 
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def readGpoPolicy(policyGuid: str, withSettings: bool, withFilters: bool) -> str:
    """
    Read a policy. A policy template doesn't have filters.
    @param customerId The customer ID
    @param siteId The site ID
    @param policyGuid GUID of the policy to be read
    @param withSettings (optional) If set to true, read policy settings
    @param withFilters (optional) If set to true, read policy filters
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return The policy read
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/gpo/policies/{policyGuid}?"
        if withSettings:
            url_ += "withSettings=" + urllib.parse.quote(str(withSettings))
        if withFilters:
            url_ += "&withFilters=" + urllib.parse.quote(str(withFilters)) 
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def readGpoPolicySets() -> str:
    """
    Get all GPO policy sets in the site.
    @param customerId The customer ID
    @param siteId The site ID
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return The policy sets in the site
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/gpo/policySets"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def readGpoPolicySet(policySetGuid: str, withPolicies: bool) -> str:
    """
    Read a GPO policy set.
    @param customerId The customer ID
    @param siteId The site ID
    @param policySetGuid GUID of the policy set to read
    @param withPolicies (optional) If set to true, read the policies in the policy set
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return The policy set read
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/gpo/policySets/{policySetGuid}?"
        if withPolicies:
            url_ += "withPolicies=" + urllib.parse.quote(str(withPolicies))
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getSettingDefinitions(isLean: bool, limit: int, isAscending: bool, namePattern: str, isUserSetting: bool) -> str:
    """
    Get setting definitions. If isLean is set to true, only basic session information is returned. EnumType,
            VdaVersions, VersionDetails, and Explanation are not retrieved. If limit is set to -1 or a number larger
            than the number of settings available, all entries are retrieved. If limit is set to a positive integer
            smaller than the number of settings available, the specified number of settings are retrieved.
    @param customerId The customer ID
    @param siteId The site ID
    @param isLean (optional) Get lean parts of setting definitions, the default is set to true
    @param limit (optional) Specify the number of entries to retrieve, the default is all entries
    @param isAscending (optional) Specify sort order, default is true
    @param namePattern (optional) Specify a regular expression to match the internal setting name. The default is match all names.
    @param isUserSetting (optional) Specify the target of applying the settings. If it's set to true, only user settings are retrieved.
            If it's set to false, only computer settings are retrieved. If not specified, both kinds of settings
            are retrieved. The default is to retrieve both kinds of settings.
    @param continuationToken (optional) Continuation token from a previous retrieval
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return Setting definitions
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/gpo/settingDefinitions?"
        if limit:
            url_ += "limit=" + urllib.parse.quote(str(limit))
        if isLean:
            url_ += "&isLean=" + urllib.parse.quote(str(isLean)) 
        if isAscending:
            url_ += "&isAscending=" + urllib.parse.quote(str(isAscending)) 
        if namePattern:
            url_ += "&namePattern=" + urllib.parse.quote(str(namePattern)) 
        if isUserSetting:
            url_ += "&isUserSetting=" + urllib.parse.quote(str(isUserSetting)) 
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getSettingFullDetail(settingName: str) -> str:
    """
    Get full detail of a setting definition.
    @param customerId The customer ID
    @param siteId The site ID
    @param settingName The internal name of the setting
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return All details of the setting definition
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/gpo/settingFullDetail?"
        if settingName:
            url_ += "settingName=" + urllib.parse.quote(str(settingName))
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def readGpoSettings(policyGuid: str) -> str:
    """
    Read settings defined in a policy.
    @param customerId The customer ID
    @param siteId The site ID
    @param policyGuid GUID of the policy from which settings are read
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return The settings read
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/gpo/settings?"
        if policyGuid:
            url_ += "policyGuid=" + urllib.parse.quote(str(policyGuid))
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def readGpoSetting(settingGuid: str) -> str:
    """
    Read a specific setting.
    @param customerId The customer ID
    @param siteId The site ID
    @param settingGuid GUID of the setting to be read
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return The setting read
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/gpo/settings/{settingGuid}"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def runValidation(all: bool) -> str:
    """
    Check the site policies to ensure that they can be successfully converted to the new GPO objects. If an
            error exists in the value of a setting or filter, the error must be fixed before the policy data can be
            converted to new GPO setting, filter, and policy objects. The validation is done only on the site policies.
    @param customerId The customer id of the customer making this rest call
    @param siteId The site id of the customer's site making this rest call
    @param all (optional) If true, all settings and filters in the policies are returned, otherwise only settings and filters with
            errors are returned. Policies are always included in the result, regardless of the value of this parameter.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return Site polices, as well as settings and filters in those policies.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/gpo/validation?"
        if all:
            url_ += "all=" + urllib.parse.quote(str(all))
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def retrieveAllData(locale: str) -> str:
    """
    Get all policies, templates, setting definitions and filter definitions
    @param customerid The customer id of the customer making this rest call
    @param siteid The site id of the customer's site making this rest call
    @param locale Target locale
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return AllResponseContract
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/groupPolicy/allData?"
        if locale:
            url_ += "locale=" + urllib.parse.quote(str(locale))
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getComparison(locale: str, targets: str, withDefaults: bool) -> str:
    """
    Compare policies or templates. Templates are currently not supported.
    @param customerid The customer id of the customer making this rest call
    @param siteid The site id of the customer's site making this rest call
    @param locale Locale for returned strings
    @param targets Comma-separated list of policies, if null, compare all
    @param withDefaults Include defaults in comparison
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return Comparison result
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/groupPolicy/compare?"
        if locale:
            url_ += "locale=" + urllib.parse.quote(str(locale))
        if targets:
            url_ += "&targets=" + urllib.parse.quote(str(targets)) 
        if withDefaults:
            url_ += "&withDefaults=" + urllib.parse.quote(str(withDefaults)) 
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getFilterDefinitions(locale: str) -> str:
    """
    Get all filter definitions.
    @param customerid The customer id of the customer making this rest call
    @param siteid The site id of the customer's site making this rest call
    @param locale (optional)
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return Filter types
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/groupPolicy/filters?"
        if locale:
            url_ += "locale=" + urllib.parse.quote(str(locale))
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def retrievePolicies(locale: str, withSettings: bool, withFilters: bool) -> str:
    """
    Erase the local cache and retrieve all policies from the database. Regardless if the load succeeds or fails,
            the local cache is always cleared.
    @param customerid The customer id of the customer making this rest call
    @param siteid The site id of the customer's site making this rest call
    @param locale The locale for the returned strings
    @param withSettings True if settings are included in the result
    @param withFilters True if filters are included in the result
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return All the policies
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/groupPolicy/policies?"
        if locale:
            url_ += "locale=" + urllib.parse.quote(str(locale))
        if withSettings:
            url_ += "&withSettings=" + urllib.parse.quote(str(withSettings)) 
        if withFilters:
            url_ += "&withFilters=" + urllib.parse.quote(str(withFilters)) 
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def retrievePolicy(policyName: str, locale: str, withSettings: bool, withFilters: bool) -> str:
    """
    Retrieve an existing policy.
    @param customerid The customer id of the customer making this rest call
    @param siteid The site id of the customer's site making this rest call
    @param policyName The policy name
    @param locale Locale for display strings
    @param withSettings True if settings are included in the result
    @param withFilters True if filters are included in the result
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return The policy
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/groupPolicy/policies/{policyName}?"
        if locale:
            url_ += "locale=" + urllib.parse.quote(str(locale))
        if withSettings:
            url_ += "&withSettings=" + urllib.parse.quote(str(withSettings)) 
        if withFilters:
            url_ += "&withFilters=" + urllib.parse.quote(str(withFilters)) 
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def retrieveFilters(policyName: str) -> str:
    """
    Get filters of a policy
    @param customerid The customer id of the customer making this rest call
    @param siteid The site id of the customer's site making this rest call
    @param policyName The policy name
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return Filters
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/groupPolicy/policies/{policyName}/filters"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def retrieveFilter(policyName: str, filterName: str) -> str:
    """
    Retrieve a filter
    @param customerid The customer id of the customer making this rest call
    @param siteid The site id of the customer's site making this rest call
    @param policyName The policy name
    @param filterName The filter name
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return The filter data
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/groupPolicy/policies/{policyName}/filters/{filterName}"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def retrievePolicySettings(locale: str, policyName: str) -> str:
    """
    Get settings of a policy
    @param customerid The customer id of the customer making this rest call
    @param siteid The site id of the customer's site making this rest call
    @param locale The locale for the returned strings
    @param policyName Name of policy for which settings are retrieved
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return Settings used in the policy
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/groupPolicy/policies/{policyName}/settings?"
        if locale:
            url_ += "locale=" + urllib.parse.quote(str(locale))
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def retrievePolicySetting(policyName: str, settingName: str) -> str:
    """
    Retrieve an existing selected policy setting
    @param customerid The customer id of the customer making this rest call
    @param siteid The site id of the customer's site making this rest call
    @param policyName Name of the policy
    @param settingName The setting name
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return The setting data
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/groupPolicy/policies/{policyName}/settings/{settingName}"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def retrievePoliciesTemplates(locale: str) -> str:
    """
    Get all policies and templates
    @param customerid The customer id of the customer making this rest call
    @param siteid The site id of the customer's site making this rest call
    @param locale The locale
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return PolicyTemplateResponseContract
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/groupPolicy/policiesTemplates?"
        if locale:
            url_ += "locale=" + urllib.parse.quote(str(locale))
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getSettingDefinitions(locale: str) -> str:
    """
    Retrieve all setting definitions.
    @param customerid The customer id of the customer making this rest call
    @param siteid The site id of the customer's site making this rest call
    @param locale The locale for the returned strings
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return Global setting definitions
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/groupPolicy/settings?"
        if locale:
            url_ += "locale=" + urllib.parse.quote(str(locale))
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def retrieveTemplates(locale: str, withSettings: bool) -> str:
    """
    Get all templates
    @param customerid The customer id of the customer making this rest call
    @param siteid The site id of the customer's site making this rest call
    @param locale The locale for strings
    @param withSettings Retrieve template settings
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return templates
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/groupPolicy/templates?"
        if locale:
            url_ += "locale=" + urllib.parse.quote(str(locale))
        if withSettings:
            url_ += "&withSettings=" + urllib.parse.quote(str(withSettings)) 
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def retrieveTemplate(templateName: str, locale: str, withSettings: bool) -> str:
    """
    Get one specified template
    @param customerid The customer id of the customer making this rest call
    @param siteid The site id of the customer's site making this rest call
    @param templateName The template name
    @param locale The locale for strings
    @param withSettings Retrieve template settings
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return The template
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/groupPolicy/templates/{templateName}?"
        if locale:
            url_ += "locale=" + urllib.parse.quote(str(locale))
        if withSettings:
            url_ += "&withSettings=" + urllib.parse.quote(str(withSettings)) 
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def retrieveTemplateSettings(templateName: str) -> str:
    """
    Get settings of a template
    @param customerid The customer id of the customer making this rest call
    @param siteid The site id of the customer's site making this rest call
    @param templateName Name of template for which settings are retrieved
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return Settings used in the policy
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/groupPolicy/templates/{templateName}/settings"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def retrieveTemplateSetting(templateName: str, settingName: str) -> str:
    """
    Retrieve an existing selected template setting
    @param customerid The customer id of the customer making this rest call
    @param siteid The site id of the customer's site making this rest call
    @param templateName Name of the template
    @param settingName The setting name
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return The setting data
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/groupPolicy/templates/{templateName}/settings/{settingName}"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getIcons(iconFormat: str, builtIn: bool, limit: int) -> str:
    """
    Get all icons in the site.
    @param iconFormat (optional) Icon format.  Must be: `{mime-type};{width}x{height}x{colordepth}`
    
            where:
    
    _mime-type_ must be `image/png`.  (Other formats may be supported in future.)
    _width_ and _height_ are specified in pixels.
    _colordepth_ (optional) is either `8` or `24`.
    
            example: `"image/png;32x32x24"`
    
            Optional. If not specified, only the raw icon data will be returned. Note that
            this is typically in ICO format, which some clients cannot display properly.
    @param builtIn (optional) If specified as `true`, only built-in icons will be returned.  If specified as
            `false`, only user-created icons will be returned.  If not specified, all
            icons will be returned.
    @param async (optional) If async execute.
    @param limit (optional) The max number of icons returned by this query.
            If not specified, the server might use a default limit of 250 items.
            If the specified value is larger than 1000, the server might reject the call.
            The default and maximum values depend on server settings.
    @param continuationToken (optional) If a query cannot be completed, the response will have a
            ContinuationToken set.
            To obtain more results from the query, pass the
            continuation token back into the query to get the next
            batch of results.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return List of icons.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/Icons?"
        if limit:
            url_ += "limit=" + urllib.parse.quote(str(limit))
        if iconFormat:
            url_ += "&iconFormat=" + urllib.parse.quote(str(iconFormat)) 
        if builtIn:
            url_ += "&builtIn=" + urllib.parse.quote(str(builtIn)) 
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getIcon(id: str, iconFormat: str) -> str:
    """
    Get a single icon from the site.
    @param id ID of the icon.
    @param iconFormat (optional) Icon format.  Must be:
            `{mime-type};{width}x{height}x{colordepth}`
    
            where:
    _mime-type_ must be `image/png`.  (Other formats may be supported in future.)
    _width_ and _height_ are specified in pixels.
    _colordepth_ (optional) is either `8` or `24`.
             example: `"image/png;32x32x24"`
    
            Optional. If not specified, only the raw icon data will be returned. Note that
            this is typically in ICO format, which some clients cannot display properly.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return The icon.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/Icons/{id}?"
        if iconFormat:
            url_ += "iconFormat=" + urllib.parse.quote(str(iconFormat))
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def queryAzureAdSecurityGroups(azureAdTenantId: str, name: str, assigned: bool, maxCount: int, serviceAccountUid: str, x_AccessToken: str) -> str:
    """
    Query AzureAD security group by user's input.
    @param azureAdTenantId The specific azure tenant id.
    @param name (optional) Specific the group display name.
    @param assigned (optional) When name is empty, assigned only support the value of true.
    @param maxCount (optional) The max return count,default is 300.
    @param serviceAccountUid (optional) The service account uid.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_AccessToken (optional) Access token to use when performing the operation. If specified, must be in a format matching that of the standard 'Authorization' request header; UTF8-encoded, then base64-encoded, then the "Bearer" scheme prepended.
            Example: Bearer bGljaGVuZy5saW5AY2l0cml4LmNvbQ==
    @param x_ActionName (optional) Orchestration Action Name
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/Identity/AzureADTenants/{azureAdTenantId}/AzureADSecurityGroups?"
        if name:
            url_ += "name=" + urllib.parse.quote(str(name))
        if assigned:
            url_ += "&assigned=" + urllib.parse.quote(str(assigned)) 
        if maxCount:
            url_ += "&maxCount=" + urllib.parse.quote(str(maxCount)) 
        if serviceAccountUid:
            url_ += "&serviceAccountUid=" + urllib.parse.quote(str(serviceAccountUid)) 
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getAzureADSecurityGroups(azureAdTenantId: str, groupId: str, serviceAccountUid: str, x_AccessToken: str) -> str:
    """
    Get Azure AD security group by group id.
    @param azureAdTenantId AzureAD tenantId
    @param groupId AzureAD security group's objectId
    @param serviceAccountUid (optional) Service account objectId
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_AccessToken (optional) Access token to use when performing the operation. If specified, must be in a format matching that of the standard 'Authorization' request header; UTF8-encoded, then base64-encoded, then the "Bearer" scheme prepended.
            Example: Bearer bGljaGVuZy5saW5AY2l0cml4LmNvbQ==
    @param x_ActionName (optional) Orchestration Action Name
    @return List of Azure AD security groups.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/Identity/AzureADTenants/{azureAdTenantId}/AzureADSecurityGroups/{groupId}?"
        if serviceAccountUid:
            url_ += "serviceAccountUid=" + urllib.parse.quote(str(serviceAccountUid))
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getAzureAdSecurityGroupMember(azureAdTenantId: str, groupId: str, type: str, maxCount: int, serviceAccountUid: str, x_AccessToken: str) -> str:
    """
    Retrieves all the group type of members of a specific group
    @param azureAdTenantId The Azure tenant id.
    @param groupId The security group object id.
    @param type (optional) Only type=group is support now.
    @param maxCount (optional) The max return records number.
    @param serviceAccountUid (optional) The service account uid.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_AccessToken (optional) Access token to use when performing the operation. If specified, must be in a format matching that of the standard 'Authorization' request header; UTF8-encoded, then base64-encoded, then the "Bearer" scheme prepended.
            Example: Bearer bGljaGVuZy5saW5AY2l0cml4LmNvbQ==
    @param x_ActionName (optional) Orchestration Action Name
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/Identity/AzureADTenants/{azureAdTenantId}/AzureADSecurityGroups/{groupId}/members?"
        if type:
            url_ += "type=" + urllib.parse.quote(str(type))
        if maxCount:
            url_ += "&maxCount=" + urllib.parse.quote(str(maxCount)) 
        if serviceAccountUid:
            url_ += "&serviceAccountUid=" + urllib.parse.quote(str(serviceAccountUid)) 
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getContainers(forest: str, domain: str, container: list, startsWith: str, contains: str, matches: str, parentOU: str, recursive: bool, containerType: list, directoryServerHint: str, propertiesToRetrieve: int, limit: int, x_AdminCredential: str) -> str:
    """
    Get containers from identity provider.
    @param forest (optional) Forest to get containers from.  If not specified, all forests are queried, which may take a long time.
    @param domain (optional) Domain to get containers from.  If not specified, all domains in the forest(s) are queried, which may take a long time.
    @param container (optional) Specific container(s) to filter the results to.  If not specified, all matching containers are returned.  If set, `recursive` parameter is ignored and is implied `true`.
    @param startsWith (optional) Search for containers that start with a string.  If not specified, all matching containers are returned.
    @param contains (optional) Search for containers that contain a string.  If not specified, all matching containers are returned.
    @param matches (optional) Search for containers that match a string.  If not specified, all matching containers are returned.
    @param parentOU (optional) The parent OU to search.  If not specified, will search from the root OU.
    @param recursive (optional) Indicates whether the search should be recursive.  Default is `false`.
    @param containerType (optional) Indicates container type(s) that should be retrieved.  If not specified, all container types will be searched.
    @param directoryServerHint (optional) Hint to inform the system of a directory server which is most likely to successfully perform the operation.
    @param propertiesToRetrieve (optional) Properties to retrieve.  This should be specified as an integer representing the OR-ed together values
            of the properties.  If not specified, all properties will be retrieved.
    @param limit (optional) Maximum number of items to return.  If more items are available, a continuation token will
            be returned.  If not specified, all items will be returned.
    @param continuationToken (optional) If specified, a previous query will be continued.  The caller must specify the same query parameters
            and admin credentials as the initial query or else the behavior is undefined.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_AdminCredential (optional) Admin credential to use when performing the operation. If not specified, the operation will be performed using the account under which the identity service is running If specified, must be in a format matching that of the standard 'Authorization' request header; the username and password separated by a colon, UTF8-encoded, then base64-encoded, then the "Basic " scheme prepended.
            Example:Basic QWxhZGRpbjpPcGVuU2VzYW1l
    @param x_ActionName (optional) Orchestration Action Name
    @return List of containers.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/Identity/Containers?"
        if limit:
            url_ += "limit=" + urllib.parse.quote(str(limit))
        if forest:
            url_ += "&forest=" + urllib.parse.quote(str(forest)) 
        if domain:
            url_ += "&domain=" + urllib.parse.quote(str(domain)) 
        if container:
            url_ += "&container=" + urllib.parse.quote(str(container)) 
        if startsWith:
            url_ += "&startsWith=" + urllib.parse.quote(str(startsWith)) 
        if contains:
            url_ += "&contains=" + urllib.parse.quote(str(contains)) 
        if matches:
            url_ += "&matches=" + urllib.parse.quote(str(matches)) 
        if parentOU:
            url_ += "&parentOU=" + urllib.parse.quote(str(parentOU)) 
        if recursive:
            url_ += "&recursive=" + urllib.parse.quote(str(recursive)) 
        if containerType:
            url_ += "&containerType=" + urllib.parse.quote(str(containerType)) 
        if directoryServerHint:
            url_ += "&directoryServerHint=" + urllib.parse.quote(str(directoryServerHint)) 
        if propertiesToRetrieve:
            url_ += "&propertiesToRetrieve=" + urllib.parse.quote(str(propertiesToRetrieve)) 
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getContainer(container: str, forest: str, domain: str, directoryServerHint: str, propertiesToRetrieve: int, x_AdminCredential: str) -> str:
    """
    Get a single container (e.g. OU)
    @param container Container to get.
    @param forest (optional) Forest to get container from.  If not specified, all forests are queried, which may take a long time.
    @param domain (optional) Domain to get container from.  If not specified, all domains in the forest(s) are queried, which may take a long time.
    @param directoryServerHint (optional) Hint to inform the system of a directory server which is most likely to successfully perform the operation.
    @param propertiesToRetrieve (optional) Properties to retrieve.  This should be specified as an integer representing the OR-ed together values
            of the properties.  If not specified, all properties will be retrieved.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_AdminCredential (optional) Admin credential to use when performing the operation. If not specified, the operation will be performed using the account under which the identity service is running If specified, must be in a format matching that of the standard 'Authorization' request header; the username and password separated by a colon, UTF8-encoded, then base64-encoded, then the "Basic " scheme prepended.
            Example:Basic QWxhZGRpbjpPcGVuU2VzYW1l
    @param x_ActionName (optional) Orchestration Action Name
    @return Details about container.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/Identity/Containers/{container}?"
        if forest:
            url_ += "forest=" + urllib.parse.quote(str(forest))
        if domain:
            url_ += "&domain=" + urllib.parse.quote(str(domain)) 
        if directoryServerHint:
            url_ += "&directoryServerHint=" + urllib.parse.quote(str(directoryServerHint)) 
        if propertiesToRetrieve:
            url_ += "&propertiesToRetrieve=" + urllib.parse.quote(str(propertiesToRetrieve)) 
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getDirectories(limit: int) -> str:
    """
    Get list of directories from all identity providers
    @param limit (optional) The max number of items returned by this query.
    @param continuationToken (optional) The continuationToken returned by the previous query.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return List of directories.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/Identity/Directories?"
        if limit:
            url_ += "limit=" + urllib.parse.quote(str(limit))
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getDomains(forest: str, domain: list, directoryServerHint: str, parentDomain: str, recursive: bool, propertiesToRetrieve: int, limit: int, x_AdminCredential: str) -> str:
    """
    Get list of domains from the identity provider
    @param forest (optional) Forest to get domains from.  If not specified, all forests are queried, which may take a long time.
    @param domain (optional) Specific domain(s) to filter the results to.  If not specified, all matching domains are returned.
    @param directoryServerHint (optional) Hint to inform the system of a directory server which is most likely to successfully perform the operation.
    @param parentDomain (optional) Parent domain name to search.  Default is the root domain of the forest.
    @param recursive (optional) Specifies whether the search is recursive.
    @param propertiesToRetrieve (optional) Properties to retrieve.  This should be specified as an integer representing the OR-ed together values of the properties. If not specified,
            all properties other than IdentityDomainProperty.Controllers IdentityDomainProperty.PrimaryController will be retrieved.
    @param limit (optional) Maximum number of items to return.  If more items are available, a continuation token will
            be returned.  If not specified, all items will be returned.
    @param continuationToken (optional) If specified, a previous query will be continued.  The caller must specify the same query parameters
            and admin credentials as the initial query or else the behavior is undefined.
    @param async (optional)
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_AdminCredential (optional) Admin credential to use when performing the operation. If not specified, the operation will be performed using the account under which the identity service is running If specified, must be in a format matching that of the standard 'Authorization' request header; the username and password separated by a colon, UTF8-encoded, then base64-encoded, then the "Basic " scheme prepended.
            Example:Basic QWxhZGRpbjpPcGVuU2VzYW1l
    @param x_ActionName (optional) Orchestration Action Name
    @return List of domains.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/Identity/Domains?"
        if limit:
            url_ += "limit=" + urllib.parse.quote(str(limit))
        if forest:
            url_ += "&forest=" + urllib.parse.quote(str(forest)) 
        if domain:
            url_ += "&domain=" + urllib.parse.quote(str(domain)) 
        if directoryServerHint:
            url_ += "&directoryServerHint=" + urllib.parse.quote(str(directoryServerHint)) 
        if parentDomain:
            url_ += "&parentDomain=" + urllib.parse.quote(str(parentDomain)) 
        if recursive:
            url_ += "&recursive=" + urllib.parse.quote(str(recursive)) 
        if propertiesToRetrieve:
            url_ += "&propertiesToRetrieve=" + urllib.parse.quote(str(propertiesToRetrieve)) 
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getDomain(domain: str, forest: str, directoryServerHint: str, propertiesToRetrieve: int, x_AdminCredential: str) -> str:
    """
    Get a single domain from the identity provider
    @param domain Domain to get details from.
    @param forest (optional) Forest to get domain from.  If not specified, all forests are queried, which may take a long time.
    @param directoryServerHint (optional) Hint to inform the system of a directory server which is most likely to successfully perform the operation.
    @param propertiesToRetrieve (optional) Properties to retrieve.  This should be specified as an integer representing the OR-ed together values of the properties. If not specified,
            all properties other than IdentityDomainProperty.Controllers IdentityDomainProperty.PrimaryController will be retrieved.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_AdminCredential (optional) Admin credential to use when performing the operation. If not specified, the operation will be performed using the account under which the identity service is running If specified, must be in a format matching that of the standard 'Authorization' request header; the username and password separated by a colon, UTF8-encoded, then base64-encoded, then the "Basic " scheme prepended.
            Example:Basic QWxhZGRpbjpPcGVuU2VzYW1l
    @param x_ActionName (optional) Orchestration Action Name
    @return Details about a domain.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/Identity/Domains/{domain}?"
        if forest:
            url_ += "forest=" + urllib.parse.quote(str(forest))
        if directoryServerHint:
            url_ += "&directoryServerHint=" + urllib.parse.quote(str(directoryServerHint)) 
        if propertiesToRetrieve:
            url_ += "&propertiesToRetrieve=" + urllib.parse.quote(str(propertiesToRetrieve)) 
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getDomainAzureADCustomDomain(domain: str) -> str:
    """
    Gets the Azure AD custom domain with the specified domain name.
    @param domain Domain name.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return The Azure AD custom domain with the specified domain name.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/Identity/Domains/{domain}/AzureADCustomDomain"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getForests(forest: list, propertiesToRetrieve: int, limit: int, x_AdminCredential: str) -> str:
    """
    Get the list of forests from the identity provider
    @param forest (optional) Specific forest(s) to filter the results to.  If not specified, all forests are returned.
    @param propertiesToRetrieve (optional) Properties to retrieve.  This should be specified as an integer representing the OR-ed together values
            of the properties.  If not specified, all properties will be retrieved.
    @param limit (optional) Maximum number of items to return.  If more items are available, a continuation token will
            be returned.  If not specified, all items will be returned.
    @param continuationToken (optional) If specified, a previous query will be continued.  The caller must specify the same query parameters
            and admin credentials as the initial query or else the behavior is undefined.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_AdminCredential (optional) Admin credential to use when performing the operation. If not specified, the operation will be performed using the account under which the identity service is running If specified, must be in a format matching that of the standard 'Authorization' request header; the username and password separated by a colon, UTF8-encoded, then base64-encoded, then the "Basic " scheme prepended.
            Example:Basic QWxhZGRpbjpPcGVuU2VzYW1l
    @param x_ActionName (optional) Orchestration Action Name
    @return List of forests.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/Identity/Forests?"
        if limit:
            url_ += "limit=" + urllib.parse.quote(str(limit))
        if forest:
            url_ += "&forest=" + urllib.parse.quote(str(forest)) 
        if propertiesToRetrieve:
            url_ += "&propertiesToRetrieve=" + urllib.parse.quote(str(propertiesToRetrieve)) 
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getForest(forest: str, propertiesToRetrieve: int, x_AdminCredential: str) -> str:
    """
    Get information about a single forest
    @param forest forest
    @param propertiesToRetrieve (optional) Properties to retrieve.  This should be specified as an integer representing the OR-ed together values
            of the properties.  If not specified, all properties will be retrieved.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_AdminCredential (optional) Admin credential to use when performing the operation. If not specified, the operation will be performed using the account under which the identity service is running If specified, must be in a format matching that of the standard 'Authorization' request header; the username and password separated by a colon, UTF8-encoded, then base64-encoded, then the "Basic " scheme prepended.
            Example:Basic QWxhZGRpbjpPcGVuU2VzYW1l
    @param x_ActionName (optional) Orchestration Action Name
    @return Details about a forest.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/Identity/Forests/{forest}?"
        if propertiesToRetrieve:
            url_ += "propertiesToRetrieve=" + urllib.parse.quote(str(propertiesToRetrieve))
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getMachines(forest: str, domain: str, machine: list, startsWith: str, contains: str, matches: str, parentOU: str, recursive: bool, directoryServerHint: str, propertiesToRetrieve: int, limit: int, x_AdminCredential: str) -> str:
    """
    Get machine accounts from identity provider
    @param forest (optional) Forest to get machine accounts from.  If not specified, all forests are queried, which may take a long time.
    @param domain (optional) Domain to get machine accounts from.  If not specified, all domains in the forest(s) are queried, which may take a long time.
    @param machine (optional) Specific machine(s) to filter the results to.  If not specified, all matching machines are returned.  If set, `recursive` parameter is ignored and is implied `true`.
    @param startsWith (optional) Search for machine accounts that start with a string.  This parameter is exclusive with `contains`, and `matches`.
    @param contains (optional) Search for machine accounts that contain a string.  This parameter is exclusive with `startsWith`, and `matches`.
    @param matches (optional) Search for machine accounts that match a string.  This parameter is exclusive with `startsWith`, and `contains`.
    @param parentOU (optional) The parent OU to search.  If not specified, will search from the root OU.
    @param recursive (optional) Indicates whether the search should be recursive.
    @param directoryServerHint (optional) Hint to inform the system of a directory server which is most likely to successfully perform the operation.
    @param propertiesToRetrieve (optional) Properties to retrieve.  This should be specified as an integer representing the OR-ed together values
            of the properties.  If not specified, all properties other than
            IPAddress will be retrieved.
    @param limit (optional) Maximum number of items to return.  If more items are available, a continuation token will
            be returned.  If not specified, all items will be returned.
    @param continuationToken (optional) If specified, a previous query will be continued.  The caller must specify the same query parameters
            and admin credentials as the initial query or else the behavior is undefined.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_AdminCredential (optional) Admin credential to use when performing the operation. If not specified, the operation will be performed using the account under which the identity service is running If specified, must be in a format matching that of the standard 'Authorization' request header; the username and password separated by a colon, UTF8-encoded, then base64-encoded, then the "Basic " scheme prepended.
            Example:Basic QWxhZGRpbjpPcGVuU2VzYW1l
    @param x_ActionName (optional) Orchestration Action Name
    @return List of machines.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/Identity/Machines?"
        if limit:
            url_ += "limit=" + urllib.parse.quote(str(limit))
        if forest:
            url_ += "&forest=" + urllib.parse.quote(str(forest)) 
        if domain:
            url_ += "&domain=" + urllib.parse.quote(str(domain)) 
        if machine:
            url_ += "&machine=" + urllib.parse.quote(str(machine)) 
        if startsWith:
            url_ += "&startsWith=" + urllib.parse.quote(str(startsWith)) 
        if contains:
            url_ += "&contains=" + urllib.parse.quote(str(contains)) 
        if matches:
            url_ += "&matches=" + urllib.parse.quote(str(matches)) 
        if parentOU:
            url_ += "&parentOU=" + urllib.parse.quote(str(parentOU)) 
        if recursive:
            url_ += "&recursive=" + urllib.parse.quote(str(recursive)) 
        if directoryServerHint:
            url_ += "&directoryServerHint=" + urllib.parse.quote(str(directoryServerHint)) 
        if propertiesToRetrieve:
            url_ += "&propertiesToRetrieve=" + urllib.parse.quote(str(propertiesToRetrieve)) 
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getMachine(machine: str, forest: str, domain: str, directoryServerHint: str, propertiesToRetrieve: int, x_AdminCredential: str) -> str:
    """
    Get a single machine account from identity provider
    @param machine Machine to get.
    @param forest (optional) Forest to get machine account from.  If not specified, all forests are queried, which may take a long time.
    @param domain (optional) Domain to get machine account from.  If not specified, all domains in the forest(s) are queried, which may take a long time.
    @param directoryServerHint (optional) Hint to inform the system of a directory server which is most likely to successfully perform the operation.
    @param propertiesToRetrieve (optional) Properties to retrieve.  This should be specified as an integer representing the OR-ed together values
            of the properties.  If not specified, all properties other than
            IPAddress will be retrieved.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_AdminCredential (optional) Admin credential to use when performing the operation. If not specified, the operation will be performed using the account under which the identity service is running If specified, must be in a format matching that of the standard 'Authorization' request header; the username and password separated by a colon, UTF8-encoded, then base64-encoded, then the "Basic " scheme prepended.
            Example:Basic QWxhZGRpbjpPcGVuU2VzYW1l
    @param x_ActionName (optional) Orchestration Action Name
    @return Details about the machine.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/Identity/Machines/{machine}?"
        if forest:
            url_ += "forest=" + urllib.parse.quote(str(forest))
        if domain:
            url_ += "&domain=" + urllib.parse.quote(str(domain)) 
        if directoryServerHint:
            url_ += "&directoryServerHint=" + urllib.parse.quote(str(directoryServerHint)) 
        if propertiesToRetrieve:
            url_ += "&propertiesToRetrieve=" + urllib.parse.quote(str(propertiesToRetrieve)) 
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getPrinters(forest: str, domain: str, server: str, uncpath: str, x_AdminCredential: str) -> str:
    """
    Get network printers from identity provider
    @param forest (optional) Forest to get printers from.  If not specified, all forests are queried, which may take a long time.
    @param domain (optional) Domain to get printers from.  If not specified, all domains in the forest(s) are queried, which may take a long time.
    @param server (optional) Printer server name
    @param uncpath (optional) Printer UNC path
    @param async (optional) If `true`, the get printers will be executed as a background task.
            The task will have JobType GetPrintersIdentity.
            When the task is complete it will redirect to
            GetJobResults.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_AdminCredential (optional) Admin credential to use when performing the operation. If not specified, the operation will be performed using the account under which the identity service is running If specified, must be in a format matching that of the standard 'Authorization' request header; the username and password separated by a colon, UTF8-encoded, then base64-encoded, then the "Basic " scheme prepended.
            Example:Basic QWxhZGRpbjpPcGVuU2VzYW1l
    @param x_ActionName (optional) Orchestration Action Name
    @return List of printers.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/Identity/Printers?"
        if forest:
            url_ += "forest=" + urllib.parse.quote(str(forest))
        if domain:
            url_ += "&domain=" + urllib.parse.quote(str(domain)) 
        if server:
            url_ += "&server=" + urllib.parse.quote(str(server)) 
        if uncpath:
            url_ += "&uncpath=" + urllib.parse.quote(str(uncpath)) 
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getServiceAccount(serviceAccountUid: str) -> str:
    """
    Get a specific service account.
    @param serviceAccountUid The ServiceAccountUid of a specific service account.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return The specific service account.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/Identity/ServiceAccount/{serviceAccountUid}"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getServiceAccountTestReport(serviceAccountUid: str) -> str:
    """
    Get the most recent test report for a service account.
    @param serviceAccountUid ID of the service account.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return Last test report.  If no tests have been run, returns a 404 Not Found.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/Identity/serviceAccount/{serviceAccountUid}/testReport"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getServiceAccounts() -> str:
    """
    Get all service accounts.
    @param async (optional)
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return All existing service accounts.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/Identity/ServiceAccounts?"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getSites(forest: str, domain: str, hostNameOrIP: str, propertiesToRetrieve: int, limit: int, x_AdminCredential: str) -> str:
    """
    Get list of sites from the identity provider
    @param forest (optional) Forest to get sites from.  If not specified, all forests are queried, which may take a long time.
    @param domain (optional) Domain to get sites from.  If not specified, all domains in the forest(s) are queried.
    @param hostNameOrIP (optional) Hostname or IP to get sites from.
    @param site (optional) Specific site(s) to filter the results to.  If not specified, all matching sites are returned.
    @param propertiesToRetrieve (optional) Properties to retrieve.  This should be specified as an integer representing the OR-ed together values
            of the properties.  If not specified, all properties will be retrieved.
    @param limit (optional) Maximum number of items to return.  If more items are available, a continuation token will
            be returned.  If not specified, all items will be returned.
    @param continuationToken (optional) If specified, a previous query will be continued.  The caller must specify the same query parameters
            and admin credentials as the initial query or else the behavior is undefined.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_AdminCredential (optional) Admin credential to use when performing the operation. If not specified, the operation will be performed using the account under which the identity service is running If specified, must be in a format matching that of the standard 'Authorization' request header; the username and password separated by a colon, UTF8-encoded, then base64-encoded, then the "Basic " scheme prepended.
            Example:Basic QWxhZGRpbjpPcGVuU2VzYW1l
    @param x_ActionName (optional) Orchestration Action Name
    @return List of sites.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/Identity/Sites?"
        if limit:
            url_ += "limit=" + urllib.parse.quote(str(limit))
        if forest:
            url_ += "&forest=" + urllib.parse.quote(str(forest)) 
        if domain:
            url_ += "&domain=" + urllib.parse.quote(str(domain)) 
        if hostNameOrIP:
            url_ += "&hostNameOrIP=" + urllib.parse.quote(str(hostNameOrIP)) 
        if propertiesToRetrieve:
            url_ += "&propertiesToRetrieve=" + urllib.parse.quote(str(propertiesToRetrieve)) 
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getSite(forest: str, domain: str, propertiesToRetrieve: int, x_AdminCredential: str) -> str:
    """
    Get information about a single site
    @param site The site to get details for.
    @param forest (optional) Forest to get the site from.  If not specified, all forests are queried, which may take a long time.
    @param domain (optional) Domain to get the site from.  If not specified, all domains in the forest(s) are queried until the site is found.
    @param propertiesToRetrieve (optional) Properties to retrieve.  This should be specified as an integer representing the OR-ed together values
            of the properties.  If not specified, all properties will be retrieved.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_AdminCredential (optional) Admin credential to use when performing the operation. If not specified, the operation will be performed using the account under which the identity service is running If specified, must be in a format matching that of the standard 'Authorization' request header; the username and password separated by a colon, UTF8-encoded, then base64-encoded, then the "Basic " scheme prepended.
            Example:Basic QWxhZGRpbjpPcGVuU2VzYW1l
    @param x_ActionName (optional) Orchestration Action Name
    @return Details about a site.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/Identity/Sites/{site}?"
        if forest:
            url_ += "forest=" + urllib.parse.quote(str(forest))
        if domain:
            url_ += "&domain=" + urllib.parse.quote(str(domain)) 
        if propertiesToRetrieve:
            url_ += "&propertiesToRetrieve=" + urllib.parse.quote(str(propertiesToRetrieve)) 
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getUsers(provider: str, forest: str, domain: str, tenant: str, user: list, startsWith: str, contains: str, matches: str, parentOU: str, recursive: bool, userType: str, directoryServerHint: str, propertiesToRetrieve: int, limit: int, idpInstanceId: str, includeIdentityClaims: bool, x_AdminCredential: str) -> str:
    """
    Get users from identity provider
    @param provider (optional) Provider to get users from.
    @param forest (optional) Forest to get users from.  If not specified, all forests are queried, which may take a long time.
    @param domain (optional) Domain to get users from.  If not specified, all domains in the forest(s) are queried, which may take a long time.
    @param tenant (optional) Tenant to get users from.
    @param user (optional) Specific user(s) to filter the results to. If not specified, all matching users are returned.  If set, `recursive` parameter is ignored and is implied `true`.
    @param startsWith (optional) Search for users that start with a string.  This parameter is exclusive with `contains`, and `matches`.
    @param contains (optional) Search for users that contain a string.  This parameter is exclusive with `startsWith`, and `matches`.
    @param matches (optional) Search for users that match a string.  This parameter is exclusive with `startsWith`, and `contains`.
    @param parentOU (optional) The parent OU to search.  If not specified, will search from the root OU.
    @param recursive (optional) Indicates whether the search should be recursive.
    @param userType (optional) Indicates user type(s) that should be retrieved.  If not specified, all user types will be searched.
    @param directoryServerHint (optional) Hint to inform the system of a directory server which is most likely to successfully perform the operation.
    @param propertiesToRetrieve (optional) Properties to retrieve.  This should be specified as an integer representing the OR-ed together values
            of the properties.  If not specified, all properties will be retrieved.
    @param limit (optional) Maximum number of items to return.  If more items are available, a continuation token will
            be returned.  If not specified, all items will be returned.
    @param continuationToken (optional) If specified, a previous query will be continued.  The caller must specify the same query parameters
            and admin credentials as the initial query or else the behavior is undefined.
    @param async (optional) If `true`, the get users will be executed as a background task.
            The task will have JobType GetUsersIdentity.
            When the task is complete it will redirect to
            GetJobResults.
    @param idpInstanceId (optional) Instance id of the identity provider.
    @param includeIdentityClaims (optional) Inlcude the identity claims in the results.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_AdminCredential (optional) Admin credential to use when performing the operation. If not specified, the operation will be performed using the account under which the identity service is running If specified, must be in a format matching that of the standard 'Authorization' request header; the username and password separated by a colon, UTF8-encoded, then base64-encoded, then the "Basic " scheme prepended.
            Example:Basic QWxhZGRpbjpPcGVuU2VzYW1l
    @param x_ActionName (optional) Orchestration Action Name
    @return List of users.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/Identity/Users?"
        if limit:
            url_ += "limit=" + urllib.parse.quote(str(limit))
        if provider:
            url_ += "&provider=" + urllib.parse.quote(str(provider)) 
        if forest:
            url_ += "&forest=" + urllib.parse.quote(str(forest)) 
        if domain:
            url_ += "&domain=" + urllib.parse.quote(str(domain)) 
        if tenant:
            url_ += "&tenant=" + urllib.parse.quote(str(tenant)) 
        if user:
            url_ += "&user=" + urllib.parse.quote(str(user)) 
        if startsWith:
            url_ += "&startsWith=" + urllib.parse.quote(str(startsWith)) 
        if contains:
            url_ += "&contains=" + urllib.parse.quote(str(contains)) 
        if matches:
            url_ += "&matches=" + urllib.parse.quote(str(matches)) 
        if parentOU:
            url_ += "&parentOU=" + urllib.parse.quote(str(parentOU)) 
        if recursive:
            url_ += "&recursive=" + urllib.parse.quote(str(recursive)) 
        if userType:
            url_ += "&userType=" + urllib.parse.quote(str(userType)) 
        if directoryServerHint:
            url_ += "&directoryServerHint=" + urllib.parse.quote(str(directoryServerHint)) 
        if propertiesToRetrieve:
            url_ += "&propertiesToRetrieve=" + urllib.parse.quote(str(propertiesToRetrieve)) 
        if idpInstanceId:
            url_ += "&idpInstanceId=" + urllib.parse.quote(str(idpInstanceId)) 
        if includeIdentityClaims:
            url_ += "&includeIdentityClaims=" + urllib.parse.quote(str(includeIdentityClaims)) 
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getUser(userOrGroup: str, forest: str, domain: str, directoryServerHint: str, propertiesToRetrieve: int, x_AdminCredential: str) -> str:
    """
    Get a single user or group
    @param userOrGroup Identity of the user or group to get.
    @param forest (optional) Forest to get users from.  If not specified, all forests are queried, which may take a long time.
    @param domain (optional) Domain to get users from.  If not specified, all domains in the forest(s) are queried, which may take a long time.
    @param directoryServerHint (optional) Hint to inform the system of a directory server which is most likely to successfully perform the operation.
    @param propertiesToRetrieve (optional) Properties to retrieve.  This should be specified as an integer representing the OR-ed together values
            of the properties.  If not specified, all properties will be retrieved.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_AdminCredential (optional) Admin credential to use when performing the operation. If not specified, the operation will be performed using the account under which the identity service is running If specified, must be in a format matching that of the standard 'Authorization' request header; the username and password separated by a colon, UTF8-encoded, then base64-encoded, then the "Basic " scheme prepended.
            Example:Basic QWxhZGRpbjpPcGVuU2VzYW1l
    @param x_ActionName (optional) Orchestration Action Name
    @return User or group details.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/Identity/Users/{userOrGroup}?"
        if forest:
            url_ += "forest=" + urllib.parse.quote(str(forest))
        if domain:
            url_ += "&domain=" + urllib.parse.quote(str(domain)) 
        if directoryServerHint:
            url_ += "&directoryServerHint=" + urllib.parse.quote(str(directoryServerHint)) 
        if propertiesToRetrieve:
            url_ += "&propertiesToRetrieve=" + urllib.parse.quote(str(propertiesToRetrieve)) 
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getImageDefinitions(limit: int) -> str:
    """
    Get all image definitions.
    @param limit (optional) The max number of image definitions returned by this query.
            If not specified, the server might use a default limit of 250 items.
            If the specified value is larger than 1000, the server might reject the call.
            The default and maximum values depend on server settings.
    @param continuationToken (optional) If a query cannot be completed, the response will have a
            ContinuationToken set.
            To obtain more results from the query, pass the
            continuation token back into the query to get the next
            batch of results.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return List of image definitions.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/ImageDefinitions?"
        if limit:
            url_ += "limit=" + urllib.parse.quote(str(limit))
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getImageDefinition(nameOrId: str) -> str:
    """
    Get details about a single image definition.
    @param nameOrId Name or ID of the image definition.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return Details of image definition.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/ImageDefinitions/{nameOrId}"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getImageDefinitionImageVersions(nameOrId: str, limit: int) -> str:
    """
    Get all image versions associated with an image definition.
    @param nameOrId Name or Id of the image definition.
    @param limit (optional) The max number of image versions returned by this query.
            If not specified, the server might use a default limit of 250 items.
            If the specified value is larger than 1000, the server might reject the call.
            The default and maximum values depend on server settings.
    @param continuationToken (optional) If a query cannot be completed, the response will have a
            ContinuationToken set.
            To obtain more results from the query, pass the
            continuation token back into the query to get the next
            batch of results.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return List of image versions.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/ImageDefinitions/{nameOrId}/ImageVersions?"
        if limit:
            url_ += "limit=" + urllib.parse.quote(str(limit))
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getImageDefinitionImageVersion(nameOrId: str, versionNumberOrId: str) -> str:
    """
    Get details about a single image version.
    @param nameOrId Name or ID of the image definition.
    @param versionNumberOrId Number or ID of the image version.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return Details of image version.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/ImageDefinitions/{nameOrId}/ImageVersions/{versionNumberOrId}"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getImageVersionProvisioningSchemes(nameOrId: str, versionNumberOrId: str) -> str:
    """
    Get provisioning schemes associated with an image version.
    @param nameOrId Name or ID of image definition.
    @param versionNumberOrId Number or ID of image version.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return List of provisioning schemes associated with an image version.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/ImageDefinitions/{nameOrId}/ImageVersions/{versionNumberOrId}/ProvisioningSchemes"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getImageVersion(id: str) -> str:
    """
    Get details about a single image version.
    @param id ID of the image version.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return Details of image version.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/ImageVersions/{id}"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getImageVersionProvisioningSchemes(id: str) -> str:
    """
    Get provisioning schemes associated with an image version.
    @param id ID of image version.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return List of provisioning schemes associated with an image version.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/ImageVersions/{id}/ProvisioningSchemes"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def isRunningInOrchestrationService() -> str:
    """
    Is running in the Orchestration Service
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return True if running in the real orchestration service; should return false or 400, 401 or 403 error from the mock service.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/IsRunningInOrchestrationService"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getJobs() -> str:
    """
    Get the list of jobs that are currently active, or have recently
            completed, and were initiated by the caller.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return List of jobs.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/Jobs"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getJob(id: str) -> str:
    """
    Get the details of a single job.
    @param id ID of the job.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return Details of the job.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/Jobs/{id}"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getJobResults(id: str) -> str:
    """
    Get the results of a job which has completed execution.
    @param id ID of the job.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return Job results.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/Jobs/{id}/Results"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def checkLicenseCertificate(adminServer: str) -> str:
    """
    Check the certificate of the license server
    @param adminServer (optional)
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/Licensing/CheckLicenseCertificate?"
        if adminServer:
            url_ += "adminServer=" + urllib.parse.quote(str(adminServer))
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getLicenseAdministrators(x_AdminCredential: str) -> str:
    """
    Get the license administrators
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_AdminCredential (optional) Admin credential to use when performing the operation. If not specified, the operation will be performed using the account under which the identity service is running If specified, must be in a format matching that of the standard 'Authorization' request header; the username and password separated by a colon, UTF8-encoded, then base64-encoded, then the "Basic " scheme prepended.
            Example:Basic QWxhZGRpbjpPcGVuU2VzYW1l
    @param x_ActionName (optional) Orchestration Action Name
    @return The list of license administrators
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/Licensing/LicenseAdministrators"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getLicensingAlert() -> str:
    """
    Get alert for license.
    @param async (optional)
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return The alert for license
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/Licensing/LicenseAlert?"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getLicenseCertificate(adminServer: str) -> str:
    """
    Get the certificate of the license server
    @param adminServer (optional)
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return The certificate of the license server
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/Licensing/LicenseCertificate?"
        if adminServer:
            url_ += "adminServer=" + urllib.parse.quote(str(adminServer))
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getLicenseSummary(includeInventory: bool) -> str:
    """
    Get the license overview
    @param includeInventory (optional) If True, license inventories will be returned in the response.
    @param async (optional) If `true`, to get the license overview information will be created as a background task.
                        The task will have JobType GetLicenseSummary.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return License Overview information
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/Licensing/LicenseOverview?"
        if includeInventory:
            url_ += "includeInventory=" + urllib.parse.quote(str(includeInventory))
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getLicensePermission(onConnect: bool, x_AdminCredential: str) -> str:
    """
    Get the permission to the license server
    @param onConnect If true, AuthorizationFailed results in None being returned; otherwise an exception is thrown.
    @param async (optional) If `true`, to get the permission to the license server will be created as a background task.
                        The task will have JobType GetLicensePermission.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_AdminCredential (optional) Admin credential to use when performing the operation. If not specified, the operation will be performed using the account under which the identity service is running If specified, must be in a format matching that of the standard 'Authorization' request header; the username and password separated by a colon, UTF8-encoded, then base64-encoded, then the "Basic " scheme prepended.
            Example:Basic QWxhZGRpbjpPcGVuU2VzYW1l
    @param x_ActionName (optional) Orchestration Action Name
    @return Permission level to the license server
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/Licensing/LicensePermission?"
        if onConnect:
            url_ += "onConnect=" + urllib.parse.quote(str(onConnect))
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getLicenseProductEdition() -> str:
    """
    Get License product edition
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return License product edition
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/Licensing/LicenseProductEdition"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getActions(limit: int) -> str:
    """
    Get all machine catalog actions.
    @param async (optional) If async to request actions.
    @param limit (optional) The max number of actions returned by this query.
            If not specified, the server might use a default limit of 250 items.
            If the specified value is larger than 1000, the server might reject the call.
            The default and maximum values depend on server settings.
    @param continuationToken (optional) If a query cannot be completed, the response will have a
            ContinuationToken set.
            To obtain more results from the query, pass the
            continuation token back into the query to get the next
            batch of results.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return ActionResponseModelCollection
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/machineCatalogActions?"
        if limit:
            url_ += "limit=" + urllib.parse.quote(str(limit))
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getAction(catalogNameOrId: str, actionId: str) -> str:
    """
    Get machine catalog actions by specified catalog name or id and action Id.
    @param catalogNameOrId The machine catalog name or id.
    @param actionId (optional) The action Id, the guid string value.
    @param async (optional) If async calling.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return ActionResponseModel
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/machineCatalogs/{catalogNameOrId}/actions?"
        if actionId:
            url_ += "actionId=" + urllib.parse.quote(str(actionId))
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getActionById(catalogNameOrId: str, actionId: str) -> str:
    """
    Get specified machine catalog specified action.
    @param catalogNameOrId The machine catalog name or id.
    @param actionId The action Id, the guid string value.
    @param async (optional) If async calling.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return ActionResponseModel
            ActionCatalogCreationResponseModel
            ActionMachineCreationResponseModel
            ActionMachineRemovalResponseModel
            ActionUpdateImageResponseModel
            or
            Catalog creation action response
            or
            Machine creation action response
            or
            Machine removal action response
            or
            Update image action response
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/machineCatalogs/{catalogNameOrId}/actions/{actionId}?"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getMachineIdentityPools() -> str:
    """
    Get all existing machine identity pools.
    @param async (optional) If `true`, it will be queried as a background task.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return List of existing machine catalog identity pools.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/MachineIdentityPools?"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getMachineIdentityPool(id: str) -> str:
    """
    Get existing machine identity pool with id.
    @param id Machine identity pool id
    @param async (optional) If `true`, it will be queried as a background task.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return Machine identity pool.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/MachineIdentityPools/{id}?"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getProvSchemeReferences(identityPoolId: str) -> str:
    """
    List all provschemes that reference the given identitypool.
    @param identityPoolId Identity pool id.
    @param async (optional) If `true`, it will be queried as a background task.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return List of provschemes referencing the given identitypool.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/MachineIdentityPools/{identityPoolId}/Provschemes?"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getMachines(sessionSupport: str, configured: bool, limit: int, fields: str, x_TimeZone: str) -> str:
    """
    Get all machines in the site.
    @param sessionSupport (optional) Optionally limit the results to machines that are either single or multi-session capable.
            If not specified, all types of machines are returned.
    @param configured (optional) Optionally limit the results to machines that are either configured or not.
            If not specified, only configured machines are returned.
    @param limit (optional) The max number of machines returned by this query.
            If not specified, the server might use a default limit of 250 items.
            If the specified value is larger than 1000, the server might reject the call.
            The default and maximum values depend on server settings.
    @param continuationToken (optional) If a query cannot be completed, the response will have a
            ContinuationToken set.
            To obtain more results from the query, pass the
            continuation token back into the query to get the next
            batch of results.
    @param async (optional) If `true`, the get machines will be executed as a background task.
            The task will have JobType GetMachines.
            When the task is complete it will redirect to
            GetJobResults.
    @param fields (optional) Optional. A filter string containing object fields requested to be returned, the requested fields are separated by comma','.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_TimeZone (optional) Time zone of the client. If specified, must be a valid Windows Id or Utc Offset from IANA (https://www.iana.org/time-zones) time zones.
            Example: UTC or +00:00
    @param x_ActionName (optional) Orchestration Action Name
    @return List of machines.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/Machines?"
        if limit:
            url_ += "limit=" + urllib.parse.quote(str(limit))
        if sessionSupport:
            url_ += "&sessionSupport=" + urllib.parse.quote(str(sessionSupport)) 
        if configured:
            url_ += "&configured=" + urllib.parse.quote(str(configured)) 
        if fields:
            url_ += "&fields=" + urllib.parse.quote(str(fields)) 
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getMachine(nameOrId: str, fields: str) -> str:
    """
    Get details of a single machine which belongs to this site, or have registered but are not yet configured in this site
    @param nameOrId Name or ID of the machine. If param is Name, currently it should get rid of '\\' and replace it using '|'. For instance, if a MachineName is "DomainA\\NameB", the param will be "DomainA|NameB".
    @param fields (optional) The requested fields.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return Details of the machine.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/Machines/{nameOrId}?"
        if fields:
            url_ += "fields=" + urllib.parse.quote(str(fields))
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getMachinesAdministrators(nameOrId: str) -> str:
    """
    Get administrators who can administer a machine
    @param nameOrId SamName, UPN, or SID of the machine. If param is Name, currently it should get rid of '\\' and replace it using '|'. For instance, if a MachineName is "DomainA\\NameB", the param will be "DomainA|NameB".
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return List of administrators.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/Machines/{nameOrId}/Administrators"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getMachineApplications(nameOrId: str) -> str:
    """
    Get the list of applications on a machine.
    @param nameOrId Name or ID of the machine. If param is Name, currently it should get rid of '\\' and replace it using '|'. For instance, if a MachineName is "DomainA\\NameB", the param will be "DomainA|NameB".
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return List of applications.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/Machines/{nameOrId}/Applications"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getMachineDeliveryGroup(nameOrId: str) -> str:
    """
    Get the delivery group for a machine.
    @param nameOrId Name or ID of the machine. If param is Name, currently it should get rid of '\\' and replace it using '|'. For instance, if a MachineName is "DomainA\\NameB", the param will be "DomainA|NameB".
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return Details of the delivery group.  If the machine is not a member of
            a delivery group, the response will be `204 No Content`.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/Machines/{nameOrId}/DeliveryGroup"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getMachineDesktop(nameOrId: str) -> str:
    """
    Get the desktop associated with the machine, if any.
    @param nameOrId Name or ID of the machine. If param is Name, currently it should get rid of '\\' and replace it using '|'. For instance, if a MachineName is "DomainA\\NameB", the param will be "DomainA|NameB".
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return Details of the desktop.  If the machine is not associated with a
            desktop, the response will be `204 No Content`.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/Machines/{nameOrId}/Desktop"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getMachineMachineCatalog(nameOrId: str) -> str:
    """
    Get the machine catalog for a machine.
    @param nameOrId Name or ID of the machine. If param is Name, currently it should get rid of '\\' and replace it using '|'. For instance, if a MachineName is "DomainA\\NameB", the param will be "DomainA|NameB".
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return Details of the machine catalog.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/Machines/{nameOrId}/MachineCatalog"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getMachinePowerActionSchedules(nameOrId: str) -> str:
    """
    Get the power action schedules associated with a machine.
    @param nameOrId Name or ID of the machine. If param is Name, currently it should get rid of '\\' and replace it using '|'. For instance, if a MachineName is "DomainA\\NameB", the param will be "DomainA|NameB".
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return List of power action schedules.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/Machines/{nameOrId}/PowerActionSchedules"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getMachineSessions(nameOrId: str, fields: str) -> str:
    """
    Get the list of sessions running on a machine.
    @param nameOrId Name or ID of the machine. If param is Name, currently it should get rid of '\\' and replace it using '|'. For instance, if a MachineName is "DomainA\\NameB", the param will be "DomainA|NameB".
    @param fields (optional) The requested session fields.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return List of sessions.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/Machines/{nameOrId}/Sessions?"
        if fields:
            url_ += "fields=" + urllib.parse.quote(str(fields))
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getMachineStartMenuShortcutIcon(nameOrId: str, shortcutPath: str, iconFormat: str) -> str:
    """
    Get a start menu shortcut icon from the machine.
    @param nameOrId Machine to get the shortcut icon from. If param is Name, currently it should get rid of '\\' and replace it using '|'. For instance, if a MachineName is "DomainA\\NameB", the param will be "DomainA|NameB".
    @param shortcutPath (optional) Path to the start menu shortcut.
    @param iconFormat (optional) Icon format.  Must be:
            `{mime-type};{width}x{height}x{colordepth}`
    
            where:
    
    _mime-type_ must be `image/png`.  (Other formats may be supported in future.)
    _width_ and _height_ are specified in pixels.
    _colordepth_ (optional) is either `8` or `24`.
    
            Optional. If not specified, only the raw icon data will be returned.
            Note that this is typically in ICO format, which many clients cannot
            display properly.
    @param async (optional) If `true`, the start menu shortcut icon will be queried as a background task.
            The task will have JobType GetMachineStartMenuShortcutIcon.
            When the task is complete it will redirect to
            GetJobResults.
            The job's Parameters will contain properties:
    
    _Id_ - ID of the machine from which start menu icon are being obtained,
    _Name_ - Name of the machine from which start menu icon are being obtained.
    _ShortcutPath_ - Path to the start menu shortcut.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return Icon data in the requested format.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/Machines/{nameOrId}/StartMenuShortcutIcon?"
        if shortcutPath:
            url_ += "shortcutPath=" + urllib.parse.quote(str(shortcutPath))
        if iconFormat:
            url_ += "&iconFormat=" + urllib.parse.quote(str(iconFormat)) 
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getMachineStartMenuShortcuts(nameOrId: str) -> str:
    """
    Get start menu shortcuts from the machine.
    @param nameOrId Machine to get the shortcuts from. If param is Name, currently it should get rid of '\\' and replace it using '|'. For instance, if a MachineName is "DomainA\\NameB", the param will be "DomainA|NameB".
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return List of shortcuts.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/Machines/{nameOrId}/StartMenuShortcuts"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getMachineTags(nameOrId: str, fields: str) -> str:
    """
    Get tags associated with a machine.
    @param nameOrId Name or ID of the machine. If param is Name, currently it should get rid of '\\' and replace it using '|'. For instance, if a MachineName is "DomainA\\NameB", the param will be "DomainA|NameB".
    @param fields (optional) Optional. A filter string containing object fields requested to be returned,
            the requested fields are separated by comma','. return all if not specified.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return List of tags.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/Machines/{nameOrId}/Tags?"
        if fields:
            url_ += "fields=" + urllib.parse.quote(str(fields))
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getTestMachineReport(nameOrId: str, reportId: str) -> str:
    """
    Get Cloud Health Check Report on a VDA machine.
    @param nameOrId Name or ID of the machine to test. If param is Name, currently it should get rid of '\\' and replace it using '|'. For instance, if a MachineName is "DomainA\\NameB", the param will be "DomainA|NameB".
    @param reportId ID of the Cloud Health Check Report.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return Machine test report.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/Machines/{nameOrId}/TestReports/{reportId}"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getMachineUpgradeVersions(nameOrId: str) -> str:
    """
    Get available upgrade versions for a machine.
    @param nameOrId Name or ID of the machine. If param is Name, currently it should get rid of '\\' and replace it using '|'. For instance, if a MachineName is "DomainA\\NameB", the param will be "DomainA|NameB".
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return List of available upgrade versions for the machine.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/Machines/{nameOrId}/UpgradeVersions"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getVDAComponentsAndFeatures(nameOrId: str, upgradeVersion: str) -> str:
    """
    Get the components and features of VDAs associated with a machine.
    @param nameOrId Name or ID of the machine. If param is Name, currently it should get rid of '\\' and replace it using '|'. For instance, if a MachineName is "DomainA\\NameB", the param will be "DomainA|NameB".
    @param upgradeVersion (optional) The version of the VDA to upgrade to.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return Components and features of VDAs associated with a machine.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/Machines/{nameOrId}/VDAComponentsAndFeatures?"
        if upgradeVersion:
            url_ += "upgradeVersion=" + urllib.parse.quote(str(upgradeVersion))
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getMachinesV2(sessionSupport: str, configured: bool, limit: int, fields: str, x_TimeZone: str) -> str:
    """
    The V2 version of get all machines in the site.
    @param sessionSupport (optional) Optionally limit the results to machines that are either single or multi-session capable.
            If not specified, all types of machines are returned.
    @param configured (optional) Optionally limit the results to machines that are either configured or not.
            If not specified, only configured machines are returned.
    @param limit (optional) The max number of machines returned by this query.
            If not specified, the server might use a default limit of 250 items.
            If the specified value is larger than 1000, the server might reject the call.
            The default and maximum values depend on server settings.
    @param continuationToken (optional) If a query cannot be completed, the response will have a
            ContinuationToken set.
            To obtain more results from the query, pass the
            continuation token back into the query to get the next
            batch of results.
    @param async (optional) If `true`, the get machines will be executed as a background task.
            The task will have JobType GetMachines.
            When the task is complete it will redirect to
            GetJobResults.
    @param fields (optional) Optional. A filter string containing object fields requested to be returned, the requested fields are separated by comma','.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_TimeZone (optional) Time zone of the client. If specified, must be a valid Windows Id or Utc Offset from IANA (https://www.iana.org/time-zones) time zones.
            Example: UTC or +00:00
    @param x_ActionName (optional) Orchestration Action Name
    @return List of machines.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/MachinesV2?"
        if limit:
            url_ += "limit=" + urllib.parse.quote(str(limit))
        if sessionSupport:
            url_ += "&sessionSupport=" + urllib.parse.quote(str(sessionSupport)) 
        if configured:
            url_ += "&configured=" + urllib.parse.quote(str(configured)) 
        if fields:
            url_ += "&fields=" + urllib.parse.quote(str(fields)) 
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getMaintenanceCycle(nameOrId: str) -> str:
    """
    Get a maintenance cycle for a machine catalog.
    @param nameOrId The Id or name of the maintenance cycle to get.
    @param async (optional) If `true`, the maintenance cycle will be get within a background task.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/maintenanceCycles/{nameOrId}?"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getProvisionedVirtualMachineDetails(vMSid: str) -> str:
    """
    Get a Provisioned machine using VMSid.
    @param async (optional)
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return A Provisioned virtual machine.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/provisionedVirtualMachines/{VMSid}?"
        if vMSid:
            url_ += "vMSid=" + urllib.parse.quote(str(vMSid))
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getMaintenanceCycleVMOperationJobs(vmSid: str) -> str:
    """
    Get the maintenance cycle vm operation jobs for a machine.
    @param vmSid Virtual machine SID.
    @param async (optional)
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return A list of maintenance cycle vm operation jobs.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/provisionedVirtualMachines/{vmSid}/operationJobs?"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getProvisioiningSchemeConfigurations(nameOrId: str, version: int) -> str:
    """
    Get provisioning scheme configurations.
    @param nameOrId Provisioning scheme name or id.
    @param version (optional) The version of provisioning scheme configuration.
    @param async (optional) If `true`, the get of provisioning scheme will run as a background task.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/provisioningSchemes/{nameOrId}/configurations?"
        if version:
            url_ += "version=" + urllib.parse.quote(str(version))
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getMaintenanceCycles(nameOrId: str) -> str:
    """
    @param async (optional)
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/provisioningSchemes/{nameOrId}/maintenanceCycles?"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getVMConfigurationResultantSet(nameOrId: str, vmSid: str) -> str:
    """
    Provides the ability get the resultant configuration properties for virtual machine created using Machine Creation Services.
            This merges properties at the provisioning scheme level with those set on a machine with Set-ProvVM specifically.
    @param nameOrId Provisioning scheme name or id.
    @param vmSid Virtual machine SID.
    @param async (optional) If `true`, the get of VM configuration set will run as a background task.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return A list of configurations.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/provisioningSchemes/{nameOrId}/provisionedVirtualMachines/{vmSid}/configurationResultantSet?"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getPvsCollections(serverAddress: str, siteNameOrId: list, resourceLocationNameOrId: str, forest: str, x_AdminCredential: str) -> str:
    """
    Get PVS collections within a site.
    @param serverAddress Name or IP of the PVS server.
    @param siteNameOrId (optional) Name or ID of the PVS site.  Optional.  If not specified, collections from all sites are returned.
    @param resourceLocationNameOrId (optional) Name or ID of the resource location or zone through which to communicate to the PVS server.
            Optional; however, if this is not specified then communication to the PVS server
            may randomly fail based on network firewall rules between resource locations.
            Not used for on-premises deployments.
    @param forest (optional) Active Directory forest of the PVS server.  May be different than the AD forest of the
            machines managed by PVS.
    
            Optional; however, if this is not specified then communication to the PVS server
            may randomly fail if the site is connected to untrusted forests, and communication
            is attempted through a forest that is not within the trust scope of the
            PVS server's AD forest.
    
            Not used for on-premises deployments.
    @param async (optional) If `true`, the get pvs collections will be executed as a background task.
            The task will have JobType GetPvsCollections.
            When the task is complete it will redirect to
            GetJobResults.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_AdminCredential (optional) Admin credential to use when performing the operation. If not specified, the operation will be performed using the account under which the identity service is running If specified, must be in a format matching that of the standard 'Authorization' request header; the username and password separated by a colon, UTF8-encoded, then base64-encoded, then the "Basic " scheme prepended.
            Example:Basic QWxhZGRpbjpPcGVuU2VzYW1l
    @param x_ActionName (optional) Orchestration Action Name
    @return List of PVS collections.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/Pvs/{serverAddress}/Collections?"
        if siteNameOrId:
            url_ += "siteNameOrId=" + urllib.parse.quote(str(siteNameOrId))
        if resourceLocationNameOrId:
            url_ += "&resourceLocationNameOrId=" + urllib.parse.quote(str(resourceLocationNameOrId)) 
        if forest:
            url_ += "&forest=" + urllib.parse.quote(str(forest)) 
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getPvsMachinesForCatalog(serverAddress: str, siteNameOrId: list, collectionNameOrId: list, virtualOnly: bool, resourceLocationNameOrId: str, forest: str, x_AdminCredential: str) -> str:
    """
    Get PVS devices within a collection.
    @param serverAddress Name or IP of the PVS server.
    @param siteNameOrId (optional) Name or ID of the PVS site.  Optional; if not specified, devices from all sites are returned.
    @param collectionNameOrId (optional) Name or ID of the PVS collection.  Optional; if not specified, devices from all collections are returned.
    @param virtualOnly (optional) If `true` then the results will be limited to only machines which
            can be located on hypervisors connected to the site, and each returned device will include the
             and
            through which the machine may be power-managed.
    
            If `false` or not specified then all devices are returned, and
             and
            properties will not be resolved.
    @param resourceLocationNameOrId (optional) Name or ID of the resource location or zone through which to communicate to the PVS server.
            Optional; however, if this is not specified then communication to the PVS server
            may randomly fail based on network firewall rules between resource locations.
            Not used for on-premises deployments.
    @param forest (optional) Active Directory forest of the PVS server.  May be different than the AD forest of the
            machines managed by PVS.
    
            Optional; however, if this is not specified then communication to the PVS server
            may randomly fail if the site is connected to untrusted forests, and communication
            is attempted through a forest that is not within the trust scope of the
            PVS server's AD forest.
    
            Not used for on-premises deployments.
    @param async (optional) If `true`, the get pvs machines will be executed as a background task.
            The task will have JobType GetPvsMachinesForCatalog.
            When the task is complete it will redirect to
            GetJobResults.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_AdminCredential (optional) Admin credential to use when performing the operation. If not specified, the operation will be performed using the account under which the identity service is running If specified, must be in a format matching that of the standard 'Authorization' request header; the username and password separated by a colon, UTF8-encoded, then base64-encoded, then the "Basic " scheme prepended.
            Example:Basic QWxhZGRpbjpPcGVuU2VzYW1l
    @param x_ActionName (optional) Orchestration Action Name
    @return List of PVS devices.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/Pvs/{serverAddress}/MachinesForCatalog?"
        if siteNameOrId:
            url_ += "siteNameOrId=" + urllib.parse.quote(str(siteNameOrId))
        if collectionNameOrId:
            url_ += "&collectionNameOrId=" + urllib.parse.quote(str(collectionNameOrId)) 
        if virtualOnly:
            url_ += "&virtualOnly=" + urllib.parse.quote(str(virtualOnly)) 
        if resourceLocationNameOrId:
            url_ += "&resourceLocationNameOrId=" + urllib.parse.quote(str(resourceLocationNameOrId)) 
        if forest:
            url_ += "&forest=" + urllib.parse.quote(str(forest)) 
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getPvsSites(serverAddress: str, resourceLocationNameOrId: str, forest: str, x_AdminCredential: str) -> str:
    """
    Get PVS sites.
    @param serverAddress Name or IP of the PVS server.
    @param resourceLocationNameOrId (optional) Name or ID of the resource location or zone through which to communicate to the PVS server.
            Optional; however, if this is not specified then communication to the PVS server
            may randomly fail based on network firewall rules between resource locations.
            Not used for on-premises deployments.
    @param forest (optional) Active Directory forest of the PVS server.  May be different than the AD forest of the
            machines managed by PVS.
    
            Optional; however, if this is not specified then communication to the PVS server
            may randomly fail if the site is connected to untrusted forests, and communication
            is attempted through a forest that is not within the trust scope of the
            PVS server's AD forest.
    
            Not used for on-premises deployments.
    @param async (optional) If `true`, the get pvs sites will be executed as a background task.
            The task will have JobType GetPvsSites.
            When the task is complete it will redirect to
            GetJobResults.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_AdminCredential (optional) Admin credential to use when performing the operation. If not specified, the operation will be performed using the account under which the identity service is running If specified, must be in a format matching that of the standard 'Authorization' request header; the username and password separated by a colon, UTF8-encoded, then base64-encoded, then the "Basic " scheme prepended.
            Example:Basic QWxhZGRpbjpPcGVuU2VzYW1l
    @param x_ActionName (optional) Orchestration Action Name
    @return List of PVS sites.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/Pvs/{serverAddress}/Sites?"
        if resourceLocationNameOrId:
            url_ += "resourceLocationNameOrId=" + urllib.parse.quote(str(resourceLocationNameOrId))
        if forest:
            url_ += "&forest=" + urllib.parse.quote(str(forest)) 
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getPvsStreamingSites(farmId: str) -> str:
    """
    Get the list of PVS sites.
    @param farmId (optional) PVS farm id.
    @param async (optional) If `true`, it will be queried as a background task.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return PvsStreamingSiteResponseModelCollection
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/PvsStreaming/Sites?"
        if farmId:
            url_ += "farmId=" + urllib.parse.quote(str(farmId))
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getPvsStreamingStores(farmId: str, pvsSiteId: str) -> str:
    """
    Get the list of PVS stores.
    @param farmId PVS farm id.
    @param pvsSiteId (optional) PVS site id.
    @param async (optional) If `true`, it will be queried as a background task.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return PvsStreamingStoreResponseModelCollection
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/PvsStreaming/Stores/{farmId}?"
        if pvsSiteId:
            url_ += "pvsSiteId=" + urllib.parse.quote(str(pvsSiteId))
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getPvsStreamingVDisks(farmId: str, pvsSiteId: str, storeId: str, diskLocatorId: str) -> str:
    """
    Get the list of PVS vDisks.
    @param farmId (optional) PVS farm id.
    @param pvsSiteId (optional) PVS site id.
    @param storeId (optional) PVS store id.
    @param diskLocatorId (optional) PVS vDisk id.
    @param async (optional) If `true`, it will be queried as a background task.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return PvsStreamingVDiskResponseModelCollection
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/PvsStreaming/vDisks?"
        if farmId:
            url_ += "farmId=" + urllib.parse.quote(str(farmId))
        if pvsSiteId:
            url_ += "&pvsSiteId=" + urllib.parse.quote(str(pvsSiteId)) 
        if storeId:
            url_ += "&storeId=" + urllib.parse.quote(str(storeId)) 
        if diskLocatorId:
            url_ += "&diskLocatorId=" + urllib.parse.quote(str(diskLocatorId)) 
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getRebootSchedules() -> str:
    """
    Get all reboot schedules in the site.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return List of reboot schedules.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/RebootSchedules"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getRecommendations(limit: int) -> str:
    """
    Get all the recommendations.
    @param limit (optional) The max number of recommendations returned by this query.
            If not specified, the server might use a default limit of 250 items.
            If the specified value is larger than 1000, the server might reject the call.
            The default and maximum values depend on server settings.
    @param continuationToken (optional) If a query cannot be completed, the response will have a
            ContinuationToken set.
            To obtain more results from the query, pass the
            continuation token back into the query to get the next
            batch of results.
    @param async (optional) If `true`, recommendations will be fetched asynchronously.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return List of the recommendations.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/recommendations?"
        if limit:
            url_ += "limit=" + urllib.parse.quote(str(limit))
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getSessions(limit: int, fields: str) -> str:
    """
    Get all sessions in the site.
    @param limit (optional) The max number of sessions returned by this query.
            If not specified, the server might use a default limit of 250 items.
            If the specified value is larger than 1000, the server might reject the call.
            The default and maximum values depend on server settings.
    @param continuationToken (optional) If a query cannot be completed, the response will have a
            ContinuationToken set.
            To obtain more results from the query, pass the
            continuation token back into the query to get the next
            batch of results.
    @param async (optional) If `true`, the get sessions will be executed as a background task.
            The task will have JobType GetSessions.
            When the task is complete it will redirect to
            GetJobResults.
    @param fields (optional) Optional. A filter string containing object fields requested to be returned, the requested fields are separated by comma','.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return List of sessions.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/Sessions?"
        if limit:
            url_ += "limit=" + urllib.parse.quote(str(limit))
        if fields:
            url_ += "&fields=" + urllib.parse.quote(str(fields)) 
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getSession(id: str, fields: str) -> str:
    """
    Get details of a single session.
    @param id ID of the session.
    @param fields (optional) The requested fields.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return Details of the session.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/Sessions/{id}?"
        if fields:
            url_ += "fields=" + urllib.parse.quote(str(fields))
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getSessionApplications(id: str) -> str:
    """
    Get the list of applications running within a session.
    @param id ID of the session.
    @param async (optional) If `true`, the get applications will be executed as a background task.
            The task will have JobType GetSessionApplications.
            When the task is complete it will redirect to
            GetJobResults.
            The job's Parameters will contain properties:
    
    _Id_ - ID of the session being queried.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return List of applications.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/Sessions/{id}/Applications?"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getSessionMachine(id: str) -> str:
    """
    Get the details of the machine on which a session is running.
    @param id ID of the session.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return Details of the machine.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/Sessions/{id}/Machine"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getSessionRecordingStatus(id: str) -> str:
    """
    get session recording status of a session.
    @param id ID of the session.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/Sessions/RecordingStatus?"
        if id:
            url_ += "id=" + urllib.parse.quote(str(id))
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getSessionsV2(limit: int, fields: str) -> str:
    """
    The V2 of get all sessions in the site.
    @param limit (optional) The max number of sessions returned by this query.
            If not specified, the server might use a default limit of 250 items.
            If the specified value is larger than 1000, the server might reject the call.
            The default and maximum values depend on server settings.
    @param continuationToken (optional) If a query cannot be completed, the response will have a
            ContinuationToken set.
            To obtain more results from the query, pass the
            continuation token back into the query to get the next
            batch of results.
    @param async (optional) If `true`, the get sessions will be executed as a background task.
            The task will have JobType GetSessions.
            When the task is complete it will redirect to
            GetJobResults.
    @param fields (optional) Optional. A filter string containing object fields requested to be returned, the requested fields are separated by comma','.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return List of sessions.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/SessionsV2?"
        if limit:
            url_ += "limit=" + urllib.parse.quote(str(limit))
        if fields:
            url_ += "&fields=" + urllib.parse.quote(str(fields)) 
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getStoreFrontServers() -> str:
    """
    Get all StoreFront servers.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return List of StoreFront servers.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/StoreFrontServers"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getStoreFrontServer(nameOrId: str) -> str:
    """
    Get the details for a single StoreFront server.
    @param nameOrId The name or ID of the StoreFront server.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return Details of the StoreFront server.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/StoreFrontServers/{nameOrId}"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getStoreFrontAdministrators(nameOrId: str) -> str:
    """
    Get administrators who can administer a StoreFront server.
    @param nameOrId Name or ID of the StoreFront server.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return List of administrators.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/StoreFrontServers/{nameOrId}/Administrators"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getStoreFrontDeliveryGroups(nameOrId: str) -> str:
    """
    GET delivery groups details for a Storefront
    @param nameOrId The id of the Storefront
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return The delivery groups for the Storefront with the given identifier
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/StoreFrontServers/{nameOrId}/DeliveryGroups"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getTags(limit: int, fields: str) -> str:
    """
    Get the list of all tags in the site.
    @param limit (optional) The max number of tags returned by this query.
            If not specified, the server might use a default limit of 250 items.
            If the specified value is larger than 1000, the server might reject the call.
            The default and maximum values depend on server settings.
    @param continuationToken (optional) If a query cannot be completed, the response will have a
            ContinuationToken set.
            To obtain more results from the query, pass the
            continuation token back into the query to get the next
            batch of results.
    @param fields (optional) The required fields of tag.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return List of tags.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/Tags?"
        if limit:
            url_ += "limit=" + urllib.parse.quote(str(limit))
        if fields:
            url_ += "&fields=" + urllib.parse.quote(str(fields)) 
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getTag(nameOrId: str) -> str:
    """
    Get a single tag from the site.
    @param nameOrId Name or ID of the tag.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return List of tags.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/Tags/{nameOrId}"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getTagApplicationGroups(nameOrId: str, limit: int) -> str:
    """
    Get the application groups associated with a tag.
    @param nameOrId Name or ID of the tag.
    @param limit (optional) The max number of application groups returned by this query.
            If not specified, the server might use a default limit of 250 items.
            If the specified value is larger than 1000, the server might reject the call.
            The default and maximum values depend on server settings.
    @param continuationToken (optional) If a query cannot be completed, the response will have a
            ContinuationToken set.
            To obtain more results from the query, pass the
            continuation token back into the query to get the next
            batch of results.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return List of application groups.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/Tags/{nameOrId}/ApplicationGroups?"
        if limit:
            url_ += "limit=" + urllib.parse.quote(str(limit))
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getTagApplications(nameOrId: str, limit: int) -> str:
    """
    Get the applications associated with a tag.
    @param nameOrId Name or ID of the tag.
    @param limit (optional) The max number of applications returned by this query.
            If not specified, the server might use a default limit of 250 items.
            If the specified value is larger than 1000, the server might reject the call.
            The default and maximum values depend on server settings.
    @param continuationToken (optional) If a query cannot be completed, the response will have a
            ContinuationToken set.
            To obtain more results from the query, pass the
            continuation token back into the query to get the next
            batch of results.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return List of applications.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/Tags/{nameOrId}/Applications?"
        if limit:
            url_ += "limit=" + urllib.parse.quote(str(limit))
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getTagDeliveryGroups(nameOrId: str, limit: int) -> str:
    """
    Get the delivery groups associated with a tag.
    @param nameOrId Name or ID of the tag.
    @param limit (optional) The max number of delivery groups returned by this query.
            If not specified, the server might use a default limit of 250 items.
            If the specified value is larger than 1000, the server might reject the call.
            The default and maximum values depend on server settings.
    @param continuationToken (optional) If a query cannot be completed, the response will have a
            ContinuationToken set.
            To obtain more results from the query, pass the
            continuation token back into the query to get the next
            batch of results.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return List of delivery groups.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/Tags/{nameOrId}/DeliveryGroups?"
        if limit:
            url_ += "limit=" + urllib.parse.quote(str(limit))
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getTagMachineCatalogs(nameOrId: str, limit: int) -> str:
    """
    Get the machine catalogs associated with a tag.
    @param nameOrId Name or ID of the tag.
    @param limit (optional) The max number of machine catalogs returned by this query.
            If not specified, the server might use a default limit of 250 items.
            If the specified value is larger than 1000, the server might reject the call.
            The default and maximum values depend on server settings.
    @param continuationToken (optional) If a query cannot be completed, the response will have a
            ContinuationToken set.
            To obtain more results from the query, pass the
            continuation token back into the query to get the next
            batch of results.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return List of machine catalogs.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/Tags/{nameOrId}/MachineCatalogs?"
        if limit:
            url_ += "limit=" + urllib.parse.quote(str(limit))
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getTagMachines(nameOrId: str, limit: int, fields: str) -> str:
    """
    Get the machines associated with a tag.
    @param nameOrId Name or ID of the tag.
    @param limit (optional) The max number of machines returned by this query.
            If not specified, the server might use a default limit of 250 items.
            If the specified value is larger than 1000, the server might reject the call.
            The default and maximum values depend on server settings.
    @param continuationToken (optional) If a query cannot be completed, the response will have a
            ContinuationToken set.
            To obtain more results from the query, pass the
            continuation token back into the query to get the next
            batch of results.
    @param fields (optional) Optional filter, removing unspecified properties that otherwise would
            have been sent by the server
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return List of machines.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/Tags/{nameOrId}/Machines?"
        if limit:
            url_ += "limit=" + urllib.parse.quote(str(limit))
        if fields:
            url_ += "&fields=" + urllib.parse.quote(str(fields)) 
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getTenants(limit: int) -> str:
    """
    Get the list of all tenants in the site.
    @param limit (optional) The max number of tenants returned by this query.
            If not specified, the server might use a default limit of 250 items.
            If the specified value is larger than 1000, the server might reject the call.
            The default and maximum values depend on server settings.
    @param continuationToken (optional) The continuationToken returned by the previous query.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return List of tenants.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/Tenants?"
        if limit:
            url_ += "limit=" + urllib.parse.quote(str(limit))
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getTenant(nameOrId: str) -> str:
    """
    Get a single tenant from the site.
    @param nameOrId Name or ID of the tenant.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return Details of the tenant.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/Tenants/{nameOrId}"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getTenantApplicationGroups(nameOrId: str, includeShared: bool, limit: int) -> str:
    """
    Get application groups associated with a tenant.
    @param nameOrId Name or ID of the tenant.
    @param includeShared (optional) If `true`, shared application groups (those not associated with any
            tenant) are included in the results in addition to the application
            groups that are associated with the specified tenant.
    @param limit (optional) The max number of application groups returned by this query.
            If not specified, the server might use a default limit of 250 items.
            If the specified value is larger than 1000, the server might reject the call.
            The default and maximum values depend on server settings.
    @param continuationToken (optional) The continuationToken returned by the previous query.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return List of application groups.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/Tenants/{nameOrId}/ApplicationGroups?"
        if limit:
            url_ += "limit=" + urllib.parse.quote(str(limit))
        if includeShared:
            url_ += "&includeShared=" + urllib.parse.quote(str(includeShared)) 
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getTenantApplications(nameOrId: str, includeShared: bool, limit: int) -> str:
    """
    Get applications associated with a tenant.
    @param nameOrId Name or ID of the tenant.
    @param includeShared (optional) If `true`, shared applications (those not associated with any
            tenant) are included in the results in addition to the applications
            that are associated with the specified tenant.
    @param limit (optional) The max number of applications returned by this query.
            If not specified, the server might use a default limit of 250 items.
            If the specified value is larger than 1000, the server might reject the call.
            The default and maximum values depend on server settings.
    @param continuationToken (optional) The continuationToken returned by the previous query.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return List of applications.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/Tenants/{nameOrId}/Applications?"
        if limit:
            url_ += "limit=" + urllib.parse.quote(str(limit))
        if includeShared:
            url_ += "&includeShared=" + urllib.parse.quote(str(includeShared)) 
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getTenantDeliveryGroups(nameOrId: str, includeShared: bool, limit: int) -> str:
    """
    Get delivery groups associated with a tenant.
    @param nameOrId Name or ID of the tenant.
    @param includeShared (optional) If `true`, shared delivery groups (those not associated with any
            tenant) are included in the results in addition to the delivery
            groups that are associated with the specified tenant.
    @param limit (optional) The max number of delivery groups returned by this query.
            If not specified, the server might use a default limit of 250 items.
            If the specified value is larger than 1000, the server might reject the call.
            The default and maximum values depend on server settings.
    @param continuationToken (optional) The continuationToken returned by the previous query.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return List of delivery groups.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/Tenants/{nameOrId}/DeliveryGroups?"
        if limit:
            url_ += "limit=" + urllib.parse.quote(str(limit))
        if includeShared:
            url_ += "&includeShared=" + urllib.parse.quote(str(includeShared)) 
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getTenantDesktops(nameOrId: str, includeShared: bool, limit: int) -> str:
    """
    Get desktops associated with a tenant.
    @param nameOrId Name or ID of the tenant.
    @param includeShared (optional) If `true`, shared desktops (those not associated with any tenant)
            are included in the results in addition to the desktops that are
            associated with the specified tenant.
    @param limit (optional) The max number of desktops returned by this query.
            If not specified, the server might use a default limit of 250 items.
            If the specified value is larger than 1000, the server might reject the call.
            The default and maximum values depend on server settings.
    @param continuationToken (optional) The continuationToken returned by the previous query.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return List of desktops.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/Tenants/{nameOrId}/Desktops?"
        if limit:
            url_ += "limit=" + urllib.parse.quote(str(limit))
        if includeShared:
            url_ += "&includeShared=" + urllib.parse.quote(str(includeShared)) 
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getTenantHypervisors(nameOrId: str, includeShared: bool, limit: int) -> str:
    """
    Get hypervisors associated with a tenant.
    @param nameOrId Name or ID of the tenant.
    @param includeShared (optional) If `true`, shared hypervisors (those not associated with any tenant)
            are included in the results in addition to the hypervisors that are
            associated with the specified tenant.
    @param limit (optional) The max number of hypervisors returned by this query.
            If not specified, the server might use a default limit of 250 items.
            If the specified value is larger than 1000, the server might reject the call.
            The default and maximum values depend on server settings.
    @param continuationToken (optional) The continuationToken returned by the previous query.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return List of hypervisors.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/Tenants/{nameOrId}/Hypervisors?"
        if limit:
            url_ += "limit=" + urllib.parse.quote(str(limit))
        if includeShared:
            url_ += "&includeShared=" + urllib.parse.quote(str(includeShared)) 
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getTenantMachineCatalogs(nameOrId: str, includeShared: bool, limit: int) -> str:
    """
    Get machine catalogs associated with a tenant.
    @param nameOrId Name or ID of the tenant.
    @param includeShared (optional) If `true`, shared machine catalogs (those not associated with any
            tenant) are included in the results in addition to the machine
            catalogs that are associated with the specified tenant.
    @param limit (optional) The max number of machine catalogs returned by this query.
            If not specified, the server might use a default limit of 250 items.
            If the specified value is larger than 1000, the server might reject the call.
            The default and maximum values depend on server settings.
    @param continuationToken (optional) The continuationToken returned by the previous query.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return List of machine catalogs.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/Tenants/{nameOrId}/MachineCatalogs?"
        if limit:
            url_ += "limit=" + urllib.parse.quote(str(limit))
        if includeShared:
            url_ += "&includeShared=" + urllib.parse.quote(str(includeShared)) 
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getTimeZones() -> str:
    """
    Get a list of time zones supported by the site.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return List of time zones.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/TimeZones/All"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getUserZonePreferenceList(limit: int) -> str:
    """
    [DEPRECATED] Get zone preference list in this site.
    @param limit (optional) The max number of user zone preferences returned by this query.
            If not specified, the server might use a default limit of 250 items.
            If the specified value is larger than 1000, the server might reject the call.
            The default and maximum values depend on server settings.
    @param continuationToken (optional) If a query cannot be completed, the response will have a
            ContinuationToken set.
            To obtain more results from the query, pass the
            continuation token back into the query to get the next
            batch of results.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return The list users and user groups.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/UserZonePreferences?"
        if limit:
            url_ += "limit=" + urllib.parse.quote(str(limit))
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getUserZonePreference(name: str) -> str:
    """
    [DEPRECATED] Get a zone preference for a user or group account in this site.
    @param name Name of a user or user group.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return The UserZonePreferenceResponseModel.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/UserZonePreferences/{name}"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getZones(limit: int) -> str:
    """
    Get the list of all zones in the site.
    @param limit (optional) The max number of zones returned by this query.
            If not specified, the server might use a default limit of 250 items.
            If the specified value is larger than 1000, the server might reject the call.
            The default and maximum values depend on server settings.
    @param continuationToken (optional) The continuationToken returned by the previous query.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return List of zones.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/Zones?"
        if limit:
            url_ += "limit=" + urllib.parse.quote(str(limit))
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getZone(nameOrId: str) -> str:
    """
    Get a single zone from the site.
    @param nameOrId Name or ID of the zone.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return Details of the zone.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/Zones/{nameOrId}"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getUserZonePreferencesByZone(nameOrId: str, limit: int) -> str:
    """
    [DEPRECATED] Get zone preference list of a specific zone.
    @param nameOrId Name or Id of a zone.
    @param limit (optional) The max number of user zone preferences returned by this query.
            If not specified, the server might use a default limit of 250 items.
            If the specified value is larger than 1000, the server might reject the call.
            The default and maximum values depend on server settings.
    @param continuationToken (optional) If a query cannot be completed, the response will have a
            ContinuationToken set.
            To obtain more results from the query, pass the
            continuation token back into the query to get the next
            batch of results.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return The list users and user groups of the zone.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id}/{customer_id}/{virtual_site_id}/Zones/{nameOrId}/UserZonePreferences?"
        if limit:
            url_ += "limit=" + urllib.parse.quote(str(limit))
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def healthCheck() -> str:
    """
    The health check endpoint.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return true or false
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id} + /HealthCheck"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getMe() -> str:
    """
    Get my details.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return Details about the currently logged-in admin.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id} + /me"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getMyPreferences(namePrefix: str) -> str:
    """
    Get my preferences.
    @param namePrefix (optional) Optional name prefix to filter results.  If not specified, all preferences are returned.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return List of user preferences.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id} + /me/Preferences?"
        if namePrefix:
            url_ += "namePrefix=" + urllib.parse.quote(str(namePrefix))
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getMyPreference(name: str) -> str:
    """
    Get one of my preferences by name.
    @param name Preference name.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return User preferences
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id} + /me/Preferences/{name}"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def pingTP() -> str:
    """
    Test if orchestration web api is ready.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return Bool.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id} + /ping"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getServiceStatus() -> str:
    """
    Get Orchestration service status.
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return StatusModel object.
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id} + /ping/status"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"

async def getStudioSettings() -> str:
    """
    Get settings for Web Studio
    @param authorization (optional) Citrix authorization header: Bearer {token}
    @param citrix_TransactionId (optional) Transaction ID that will be used to track this request. If not provided, a new GUID will be generated and returned.
    @param x_ActionName (optional) Orchestration Action Name
    @return Studio related settings
    """
    try:
        customer_id = get_customer_id()
        auth_token = await get_token(customer_id)

        if not auth_token or len(auth_token) == 0:
            return "Failed to get the bearer token."

        virtual_site_id = await get_site_id(customer_id, auth_token)

        url_ = f"{WEBSTUDIO_API_ENDPOINT % customer_id} + /studio/settings"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }

        result = await client.get(url_, headers=headers)

        if result.status_code == 200:
            items = result.json()
            return json.dumps(items, ensure_ascii=False)
        else:
            return f"Failed to get data. Status code: {result.status_code}, Response: {result.text}"
    except Exception as err:
        logger.error(f"Failed to get data. Error: {err}")
        return f"Failed to get data. Error: {err}"



SENSITIVE_TOOLS = []
