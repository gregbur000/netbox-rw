"""
NetBox MCP Server — DCIM, IPAM, Circuits

Provides read/write access to all /api/dcim/, /api/ipam/, and /api/circuits/ endpoints.
Configure via environment variables:
  NETBOX_URL   - Base URL (default: https://10.99.30.152)
  NETBOX_TOKEN - API token for authentication
"""

import os
import json
import warnings
from typing import Any, Optional
import httpx
from mcp.server.fastmcp import FastMCP

warnings.filterwarnings("ignore", message="Unverified HTTPS request")
try:
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
except ImportError:
    pass

NETBOX_URL = os.environ.get("NETBOX_URL", "https://10.99.30.152").rstrip("/")
NETBOX_TOKEN = os.environ.get("NETBOX_TOKEN", "")

mcp = FastMCP("NetBox DCIM + IPAM + Circuits")

# All valid DCIM resource names
DCIM_RESOURCES = [
    "cable-terminations",
    "cables",
    "connected-device",
    "console-port-templates",
    "console-ports",
    "console-server-port-templates",
    "console-server-ports",
    "device-bay-templates",
    "device-bays",
    "device-roles",
    "device-types",
    "devices",
    "front-port-templates",
    "front-ports",
    "interface-templates",
    "interfaces",
    "inventory-item-roles",
    "inventory-item-templates",
    "inventory-items",
    "locations",
    "mac-addresses",
    "manufacturers",
    "module-bay-templates",
    "module-bays",
    "module-type-profiles",
    "module-types",
    "modules",
    "platforms",
    "power-feeds",
    "power-outlet-templates",
    "power-outlets",
    "power-panels",
    "power-port-templates",
    "power-ports",
    "rack-reservations",
    "rack-roles",
    "rack-types",
    "racks",
    "rear-port-templates",
    "rear-ports",
    "regions",
    "site-groups",
    "sites",
    "virtual-chassis",
    "virtual-device-contexts",
]

# Resources that support special sub-actions
RESOURCE_ACTIONS = {
    "devices": ["render-config"],
    "console-ports": ["trace"],
    "console-server-ports": ["trace"],
    "front-ports": ["paths"],
    "interfaces": ["trace"],
    "power-feeds": ["trace"],
    "power-outlets": ["trace"],
    "power-ports": ["trace"],
    "racks": ["elevation"],
    "rear-ports": ["paths"],
}

# Required fields for create operations (from OpenAPI schema)
REQUIRED_FIELDS = {
    "cables": [],
    "console-port-templates": ["device_type", "name"],
    "console-ports": ["device", "name"],
    "console-server-port-templates": ["device_type", "name"],
    "console-server-ports": ["device", "name"],
    "device-bay-templates": ["device_type", "name"],
    "device-bays": ["device", "name"],
    "device-roles": ["name", "slug"],
    "device-types": ["manufacturer", "model", "slug"],
    "devices": ["device_type", "role", "site"],
    "front-port-templates": ["device_type", "name", "rear_port", "type"],
    "front-ports": ["device", "name", "rear_port", "type"],
    "interface-templates": ["device_type", "name", "type"],
    "interfaces": ["device", "name", "type"],
    "inventory-item-roles": ["name", "slug"],
    "inventory-item-templates": ["device_type", "name"],
    "inventory-items": ["device", "name"],
    "locations": ["name", "site", "slug"],
    "mac-addresses": ["mac_address"],
    "manufacturers": ["name", "slug"],
    "module-bay-templates": ["device_type", "name"],
    "module-bays": ["device", "name"],
    "module-type-profiles": ["name"],
    "module-types": ["manufacturer", "model"],
    "modules": ["device", "module_bay", "module_type"],
    "platforms": ["name", "slug"],
    "power-feeds": ["name", "power_panel"],
    "power-outlet-templates": ["device_type", "name"],
    "power-outlets": ["device", "name"],
    "power-panels": ["name", "site"],
    "power-port-templates": ["device_type", "name"],
    "power-ports": ["device", "name"],
    "rack-reservations": ["rack", "units", "user"],
    "rack-roles": ["name", "slug"],
    "rack-types": ["manufacturer", "model", "slug"],
    "racks": ["name", "site"],
    "rear-port-templates": ["device_type", "name", "type"],
    "rear-ports": ["device", "name", "type"],
    "regions": ["name", "slug"],
    "site-groups": ["name", "slug"],
    "sites": ["name", "slug"],
    "virtual-chassis": ["name"],
    "virtual-device-contexts": ["device", "name"],
}

# Writable fields per resource (from OpenAPI schema)
RESOURCE_FIELDS = {
    "cables": ["type", "a_terminations", "b_terminations", "status", "tenant", "label", "color", "length", "length_unit", "description", "comments", "tags", "custom_fields"],
    "cable-terminations": [],
    "connected-device": [],
    "console-port-templates": ["device_type", "module_type", "name", "label", "type", "description"],
    "console-ports": ["device", "module", "name", "label", "type", "speed", "description", "mark_connected", "tags", "custom_fields"],
    "console-server-port-templates": ["device_type", "module_type", "name", "label", "type", "description"],
    "console-server-ports": ["device", "module", "name", "label", "type", "speed", "description", "mark_connected", "tags", "custom_fields"],
    "device-bay-templates": ["device_type", "name", "label", "description"],
    "device-bays": ["device", "name", "label", "description", "installed_device", "tags", "custom_fields"],
    "device-roles": ["name", "slug", "color", "vm_role", "config_template", "description", "tags", "custom_fields"],
    "device-types": ["manufacturer", "default_platform", "model", "slug", "part_number", "u_height", "exclude_from_utilization", "is_full_depth", "subdevice_role", "airflow", "weight", "weight_unit", "description", "comments", "tags", "custom_fields"],
    "devices": ["name", "device_type", "role", "tenant", "platform", "serial", "asset_tag", "site", "location", "rack", "position", "face", "latitude", "longitude", "status", "airflow", "primary_ip4", "primary_ip6", "oob_ip", "cluster", "virtual_chassis", "vc_position", "vc_priority", "description", "owner", "comments", "config_template", "local_context_data", "tags", "custom_fields"],
    "front-port-templates": ["device_type", "module_type", "name", "label", "type", "color", "rear_port", "rear_port_position", "description"],
    "front-ports": ["device", "module", "name", "label", "type", "color", "rear_port", "rear_port_position", "description", "mark_connected", "tags", "custom_fields"],
    "interface-templates": ["device_type", "module_type", "name", "label", "type", "enabled", "mgmt_only", "bridge", "description", "poe_mode", "poe_type", "rf_role", "rf_channel", "rf_channel_frequency", "rf_channel_width"],
    "interfaces": ["device", "vdcs", "module", "name", "label", "type", "enabled", "parent", "bridge", "lag", "mtu", "duplex", "mac_address", "speed", "wwn", "mgmt_only", "vrf", "tagged_vlans", "untagged_vlan", "mode", "wireless_lans", "description", "mark_connected", "rf_role", "rf_channel", "rf_channel_frequency", "rf_channel_width", "tx_power", "poe_mode", "poe_type", "wireless_link", "tags", "custom_fields"],
    "inventory-item-roles": ["name", "slug", "color", "description", "tags", "custom_fields"],
    "inventory-item-templates": ["device_type", "parent", "name", "label", "role", "manufacturer", "part_id", "description"],
    "inventory-items": ["device", "parent", "name", "label", "role", "manufacturer", "part_id", "serial", "asset_tag", "discovered", "description", "component_type", "component_id", "tags", "custom_fields"],
    "locations": ["site", "parent", "name", "slug", "status", "tenant", "facility", "description", "tags", "custom_fields"],
    "mac-addresses": ["mac_address", "assigned_object_type", "assigned_object_id", "description", "tags", "custom_fields"],
    "manufacturers": ["name", "slug", "description", "tags", "custom_fields"],
    "module-bay-templates": ["device_type", "name", "label", "position", "description"],
    "module-bays": ["device", "name", "label", "position", "description", "tags", "custom_fields"],
    "module-type-profiles": ["name", "weight", "weight_unit", "description", "tags", "custom_fields"],
    "module-types": ["manufacturer", "model", "part_number", "profiles", "airflow", "weight", "weight_unit", "description", "comments", "tags", "custom_fields"],
    "modules": ["device", "module_bay", "module_type", "status", "serial", "asset_tag", "description", "comments", "tags", "custom_fields"],
    "platforms": ["name", "slug", "manufacturer", "config_template", "description", "tags", "custom_fields"],
    "power-feeds": ["power_panel", "rack", "name", "status", "type", "supply", "phase", "voltage", "amperage", "max_utilization", "mark_connected", "cable", "description", "comments", "tenant", "tags", "custom_fields"],
    "power-outlet-templates": ["device_type", "module_type", "name", "label", "type", "power_port", "feed_leg", "description"],
    "power-outlets": ["device", "module", "name", "label", "type", "power_port", "feed_leg", "description", "mark_connected", "tags", "custom_fields"],
    "power-panels": ["site", "location", "name", "description", "tags", "custom_fields"],
    "power-port-templates": ["device_type", "module_type", "name", "label", "type", "maximum_draw", "allocated_draw", "description"],
    "power-ports": ["device", "module", "name", "label", "type", "maximum_draw", "allocated_draw", "description", "mark_connected", "tags", "custom_fields"],
    "rack-reservations": ["rack", "units", "user", "tenant", "description", "tags", "custom_fields"],
    "rack-roles": ["name", "slug", "color", "description", "tags", "custom_fields"],
    "rack-types": ["manufacturer", "model", "slug", "form_factor", "width", "u_height", "starting_unit", "desc_units", "outer_width", "outer_depth", "outer_unit", "weight", "max_weight", "weight_unit", "description", "comments", "tags", "custom_fields"],
    "racks": ["site", "location", "name", "facility_id", "tenant", "status", "role", "rack_type", "serial", "asset_tag", "type", "width", "u_height", "starting_unit", "weight", "max_weight", "weight_unit", "desc_units", "outer_width", "outer_depth", "outer_unit", "mounting_depth", "airflow", "description", "comments", "tags", "custom_fields"],
    "rear-port-templates": ["device_type", "module_type", "name", "label", "type", "color", "positions", "description"],
    "rear-ports": ["device", "module", "name", "label", "type", "color", "positions", "description", "mark_connected", "tags", "custom_fields"],
    "regions": ["parent", "name", "slug", "description", "tags", "custom_fields"],
    "site-groups": ["parent", "name", "slug", "description", "tags", "custom_fields"],
    "sites": ["name", "slug", "status", "region", "group", "tenant", "facility", "time_zone", "description", "physical_address", "shipping_address", "latitude", "longitude", "comments", "asns", "tags", "custom_fields"],
    "virtual-chassis": ["name", "domain", "master", "description", "tags", "custom_fields"],
    "virtual-device-contexts": ["device", "name", "identifier", "tenant", "primary_ip4", "primary_ip6", "status", "description", "comments", "tags", "custom_fields"],
}

# ---------------------------------------------------------------------------
# IPAM
# ---------------------------------------------------------------------------

IPAM_RESOURCES = [
    "aggregates",
    "asn-ranges",
    "asns",
    "fhrp-group-assignments",
    "fhrp-groups",
    "ip-addresses",
    "ip-ranges",
    "prefixes",
    "rirs",
    "roles",
    "route-targets",
    "service-templates",
    "services",
    "vlan-groups",
    "vlan-translation-policies",
    "vlan-translation-rules",
    "vlans",
    "vrfs",
]

# Resources with availability sub-actions
IPAM_ACTIONS = {
    "asn-ranges": ["available-asns"],
    "ip-ranges": ["available-ips"],
    "prefixes": ["available-ips", "available-prefixes"],
    "vlan-groups": ["available-vlans"],
}

IPAM_REQUIRED_FIELDS = {
    "aggregates": ["prefix", "rir"],
    "asn-ranges": ["end", "name", "rir", "slug", "start"],
    "asns": ["asn"],
    "fhrp-group-assignments": ["group", "interface_id", "interface_type", "priority"],
    "fhrp-groups": ["group_id", "protocol"],
    "ip-addresses": ["address"],
    "ip-ranges": ["end_address", "start_address"],
    "prefixes": ["prefix"],
    "rirs": ["name", "slug"],
    "roles": ["name", "slug"],
    "route-targets": ["name"],
    "service-templates": ["name", "ports", "protocol"],
    "services": ["name", "parent_object_id", "parent_object_type", "ports", "protocol"],
    "vlan-groups": ["name", "slug"],
    "vlan-translation-policies": ["name"],
    "vlan-translation-rules": ["local_vid", "policy", "remote_vid"],
    "vlans": ["name", "vid"],
    "vrfs": ["name"],
}

IPAM_RESOURCE_FIELDS = {
    "aggregates": ["prefix", "rir", "tenant", "date_added", "description", "owner", "comments", "tags", "custom_fields"],
    "asn-ranges": ["name", "slug", "rir", "start", "end", "tenant", "description", "owner", "comments", "tags", "custom_fields"],
    "asns": ["asn", "rir", "tenant", "description", "owner", "comments", "tags", "custom_fields", "sites"],
    "fhrp-group-assignments": ["group", "interface_type", "interface_id", "priority"],
    "fhrp-groups": ["name", "protocol", "group_id", "auth_type", "auth_key", "description", "owner", "comments", "tags", "custom_fields"],
    "ip-addresses": ["address", "vrf", "tenant", "status", "role", "assigned_object_type", "assigned_object_id", "nat_inside", "dns_name", "description", "owner", "comments", "tags", "custom_fields"],
    "ip-ranges": ["start_address", "end_address", "vrf", "tenant", "status", "role", "description", "owner", "comments", "tags", "custom_fields", "mark_populated", "mark_utilized"],
    "prefixes": ["prefix", "vrf", "scope_type", "scope_id", "tenant", "vlan", "status", "role", "is_pool", "mark_utilized", "description", "owner", "comments", "tags", "custom_fields"],
    "rirs": ["name", "slug", "is_private", "description", "owner", "comments", "tags", "custom_fields"],
    "roles": ["name", "slug", "weight", "description", "owner", "comments", "tags", "custom_fields"],
    "route-targets": ["name", "tenant", "description", "owner", "comments", "tags", "custom_fields"],
    "service-templates": ["name", "protocol", "ports", "description", "owner", "comments", "tags", "custom_fields"],
    "services": ["parent_object_type", "parent_object_id", "name", "protocol", "ports", "ipaddresses", "description", "owner", "comments", "tags", "custom_fields"],
    "vlan-groups": ["name", "slug", "scope_type", "scope_id", "vid_ranges", "tenant", "description", "owner", "comments", "tags", "custom_fields"],
    "vlan-translation-policies": ["name", "description", "owner", "comments"],
    "vlan-translation-rules": ["policy", "local_vid", "remote_vid", "description"],
    "vlans": ["site", "group", "vid", "name", "tenant", "status", "role", "description", "qinq_role", "qinq_svlan", "owner", "comments", "tags", "custom_fields"],
    "vrfs": ["name", "rd", "tenant", "enforce_unique", "description", "owner", "comments", "import_targets", "export_targets", "tags", "custom_fields"],
}

# ---------------------------------------------------------------------------
# CIRCUITS
# ---------------------------------------------------------------------------

CIRCUITS_RESOURCES = [
    "circuit-group-assignments",
    "circuit-groups",
    "circuit-terminations",
    "circuit-types",
    "circuits",
    "provider-accounts",
    "provider-networks",
    "providers",
    "virtual-circuit-terminations",
    "virtual-circuit-types",
    "virtual-circuits",
]

CIRCUITS_ACTIONS = {
    "circuit-terminations": ["paths"],
    "virtual-circuit-terminations": ["paths"],
}

CIRCUITS_REQUIRED_FIELDS = {
    "circuit-group-assignments": ["group", "member_id", "member_type"],
    "circuit-groups": ["name", "slug"],
    "circuit-terminations": ["circuit", "term_side"],
    "circuit-types": ["name", "slug"],
    "circuits": ["cid", "provider", "type"],
    "provider-accounts": ["account", "provider"],
    "provider-networks": ["name", "provider"],
    "providers": ["name", "slug"],
    "virtual-circuit-terminations": ["interface", "virtual_circuit"],
    "virtual-circuit-types": ["name", "slug"],
    "virtual-circuits": ["cid", "provider_network", "type"],
}

CIRCUITS_RESOURCE_FIELDS = {
    "circuit-group-assignments": ["group", "member_type", "member_id", "priority", "tags"],
    "circuit-groups": ["name", "slug", "description", "tenant", "owner", "comments", "tags", "custom_fields"],
    "circuit-terminations": ["circuit", "term_side", "termination_type", "termination_id", "port_speed", "upstream_speed", "xconnect_id", "pp_info", "description", "mark_connected", "tags", "custom_fields"],
    "circuit-types": ["name", "slug", "color", "description", "owner", "comments", "tags", "custom_fields"],
    "circuits": ["cid", "provider", "provider_account", "type", "status", "tenant", "install_date", "termination_date", "commit_rate", "description", "distance", "distance_unit", "owner", "comments", "tags", "custom_fields", "assignments"],
    "provider-accounts": ["provider", "name", "account", "description", "owner", "comments", "tags", "custom_fields"],
    "provider-networks": ["provider", "name", "service_id", "description", "owner", "comments", "tags", "custom_fields"],
    "providers": ["name", "slug", "accounts", "description", "owner", "comments", "asns", "tags", "custom_fields"],
    "virtual-circuit-terminations": ["virtual_circuit", "role", "interface", "description", "tags", "custom_fields"],
    "virtual-circuit-types": ["name", "slug", "color", "description", "owner", "comments", "tags", "custom_fields"],
    "virtual-circuits": ["cid", "provider_network", "provider_account", "type", "status", "tenant", "description", "owner", "comments", "tags", "custom_fields"],
}


def make_client() -> httpx.Client:
    headers = {"Accept": "application/json"}
    if NETBOX_TOKEN:
        headers["Authorization"] = f"Token {NETBOX_TOKEN}"
    return httpx.Client(
        base_url=NETBOX_URL,
        verify=False,
        headers=headers,
        timeout=30.0,
    )


def _namespace(resource: str) -> str:
    if resource in IPAM_RESOURCES:
        return "ipam"
    if resource in CIRCUITS_RESOURCES:
        return "circuits"
    return "dcim"


def _api_url(resource: str, id: Optional[int] = None, action: Optional[str] = None) -> str:
    ns = _namespace(resource)
    url = f"/api/{ns}/{resource}/"
    if id is not None:
        url += f"{id}/"
    if action:
        url += f"{action}/"
    return url


def _handle_response(resp: httpx.Response) -> str:
    try:
        data = resp.json()
    except Exception:
        data = {"status_code": resp.status_code, "text": resp.text}
    if resp.is_error:
        return json.dumps({"error": True, "status_code": resp.status_code, "detail": data}, indent=2)
    return json.dumps(data, indent=2)


ALL_RESOURCES = set(DCIM_RESOURCES) | set(IPAM_RESOURCES) | set(CIRCUITS_RESOURCES)


def _validate_resource(resource: str) -> Optional[str]:
    if resource not in ALL_RESOURCES:
        return (
            f"Unknown resource '{resource}'. Valid resources — "
            f"DCIM: {', '.join(sorted(DCIM_RESOURCES))}; "
            f"IPAM: {', '.join(sorted(IPAM_RESOURCES))}; "
            f"Circuits: {', '.join(sorted(CIRCUITS_RESOURCES))}"
        )
    return None


# ---------------------------------------------------------------------------
# LIST
# ---------------------------------------------------------------------------

@mcp.tool()
def dcim_list(
    resource: str,
    limit: int = 50,
    offset: int = 0,
    filters: Optional[dict[str, Any]] = None,
) -> str:
    """List DCIM objects with optional filtering.

    Args:
        resource: DCIM resource type. One of: cable-terminations, cables,
            connected-device, console-port-templates, console-ports,
            console-server-port-templates, console-server-ports,
            device-bay-templates, device-bays, device-roles, device-types,
            devices, front-port-templates, front-ports, interface-templates,
            interfaces, inventory-item-roles, inventory-item-templates,
            inventory-items, locations, mac-addresses, manufacturers,
            module-bay-templates, module-bays, module-type-profiles,
            module-types, modules, platforms, power-feeds,
            power-outlet-templates, power-outlets, power-panels,
            power-port-templates, power-ports, rack-reservations, rack-roles,
            rack-types, racks, rear-port-templates, rear-ports, regions,
            site-groups, sites, virtual-chassis, virtual-device-contexts
        limit: Maximum number of results (default 50, max 1000)
        offset: Pagination offset
        filters: Dict of query filter params, e.g. {"site": "nyc", "status": "active",
            "name__ic": "spine", "tag": "prod"}. Common filters include:
            id, name, slug, status, site, site_id, rack, rack_id, device,
            device_id, role, role_id, manufacturer, manufacturer_id,
            tenant, tenant_id, tag, q (search), limit, offset, ordering
    """
    err = _validate_resource(resource)
    if err:
        return json.dumps({"error": err})

    params: dict[str, Any] = {"limit": limit, "offset": offset}
    if filters:
        params.update(filters)

    with make_client() as client:
        resp = client.get(_api_url(resource), params=params)
    return _handle_response(resp)


# ---------------------------------------------------------------------------
# GET BY ID
# ---------------------------------------------------------------------------

@mcp.tool()
def dcim_get(resource: str, id: int) -> str:
    """Get a single DCIM object by its numeric ID.

    Args:
        resource: DCIM resource type (see dcim_list for full list)
        id: Numeric ID of the object
    """
    err = _validate_resource(resource)
    if err:
        return json.dumps({"error": err})

    with make_client() as client:
        resp = client.get(_api_url(resource, id))
    return _handle_response(resp)


# ---------------------------------------------------------------------------
# CREATE
# ---------------------------------------------------------------------------

@mcp.tool()
def dcim_create(resource: str, body: dict[str, Any]) -> str:
    """Create a new DCIM object.

    Supports creating a single object or a list of objects (bulk create).
    Pass a list as body for bulk create: [{"name": "..."}, {"name": "..."}]

    Args:
        resource: DCIM resource type (see dcim_list for full list)
        body: Object data. Required fields vary by resource:
            devices: device_type (id), role (id), site (id)
            racks: name, site (id)
            sites: name, slug
            interfaces: device (id), name, type
            cables: (no strictly required fields)
            console-ports: device (id), name
            console-server-ports: device (id), name
            device-roles: name, slug
            device-types: manufacturer (id), model, slug
            locations: name, slug, site (id)
            manufacturers: name, slug
            modules: device (id), module_bay (id), module_type (id)
            platforms: name, slug
            power-feeds: name, power_panel (id)
            power-panels: name, site (id)
            rack-reservations: rack (id), units (list of ints), user (id)
            rack-roles: name, slug
            regions: name, slug
            site-groups: name, slug
            virtual-chassis: name
            virtual-device-contexts: device (id), name

            Common optional fields: description, comments, tags (list of
            {"name": "..."} objects), custom_fields (dict), tenant (id),
            status (string enum)
    """
    err = _validate_resource(resource)
    if err:
        return json.dumps({"error": err})

    with make_client() as client:
        resp = client.post(
            _api_url(resource),
            json=body,
            headers={"Content-Type": "application/json"},
        )
    return _handle_response(resp)


# ---------------------------------------------------------------------------
# UPDATE (PUT - full replace)
# ---------------------------------------------------------------------------

@mcp.tool()
def dcim_update(resource: str, id: int, body: dict[str, Any]) -> str:
    """Fully update (PUT) a DCIM object. All required fields must be included.

    Supports bulk update by passing a list of objects with 'id' fields.

    Args:
        resource: DCIM resource type (see dcim_list for full list)
        id: Numeric ID of the object to update (ignored for bulk, pass 0)
        body: Complete object data including all required fields.
              For bulk update, pass a list: [{"id": 1, ...}, {"id": 2, ...}]
    """
    err = _validate_resource(resource)
    if err:
        return json.dumps({"error": err})

    with make_client() as client:
        if isinstance(body, list):
            resp = client.put(
                _api_url(resource),
                json=body,
                headers={"Content-Type": "application/json"},
            )
        else:
            resp = client.put(
                _api_url(resource, id),
                json=body,
                headers={"Content-Type": "application/json"},
            )
    return _handle_response(resp)


# ---------------------------------------------------------------------------
# PATCH (partial update)
# ---------------------------------------------------------------------------

@mcp.tool()
def dcim_patch(resource: str, id: int, body: dict[str, Any]) -> str:
    """Partially update (PATCH) a DCIM object. Only include fields to change.

    Supports bulk patch by passing a list of objects with 'id' fields.

    Args:
        resource: DCIM resource type (see dcim_list for full list)
        id: Numeric ID of the object to patch (ignored for bulk, pass 0)
        body: Fields to update. Only include changed fields.
              For bulk patch, pass a list: [{"id": 1, "status": "active"}, ...]

    Examples:
        Decommission a device: body={"status": "decommissioning"}
        Update rack position: body={"position": 10, "face": "front"}
        Add tags: body={"tags": [{"name": "prod"}, {"name": "spine"}]}
        Set custom field: body={"custom_fields": {"field_name": "value"}}
    """
    err = _validate_resource(resource)
    if err:
        return json.dumps({"error": err})

    with make_client() as client:
        if isinstance(body, list):
            resp = client.patch(
                _api_url(resource),
                json=body,
                headers={"Content-Type": "application/json"},
            )
        else:
            resp = client.patch(
                _api_url(resource, id),
                json=body,
                headers={"Content-Type": "application/json"},
            )
    return _handle_response(resp)


# ---------------------------------------------------------------------------
# DELETE
# ---------------------------------------------------------------------------

@mcp.tool()
def dcim_delete(resource: str, id: int) -> str:
    """Delete a DCIM object by ID.

    Supports bulk delete by passing id=0 and a list of IDs via the
    dcim_bulk_delete tool instead.

    Args:
        resource: DCIM resource type (see dcim_list for full list)
        id: Numeric ID of the object to delete
    """
    err = _validate_resource(resource)
    if err:
        return json.dumps({"error": err})

    with make_client() as client:
        resp = client.delete(_api_url(resource, id))
    if resp.status_code == 204:
        return json.dumps({"success": True, "message": f"Deleted {resource} {id}"})
    return _handle_response(resp)


# ---------------------------------------------------------------------------
# BULK DELETE
# ---------------------------------------------------------------------------

@mcp.tool()
def dcim_bulk_delete(resource: str, ids: list[int]) -> str:
    """Bulk delete multiple DCIM objects by their IDs.

    Args:
        resource: DCIM resource type (see dcim_list for full list)
        ids: List of numeric IDs to delete, e.g. [1, 2, 3]
    """
    err = _validate_resource(resource)
    if err:
        return json.dumps({"error": err})

    body = [{"id": i} for i in ids]
    with make_client() as client:
        resp = client.delete(
            _api_url(resource),
            json=body,
            headers={"Content-Type": "application/json"},
        )
    if resp.status_code == 204:
        return json.dumps({"success": True, "message": f"Deleted {len(ids)} {resource} objects"})
    return _handle_response(resp)


# ---------------------------------------------------------------------------
# SPECIAL ACTIONS
# ---------------------------------------------------------------------------

@mcp.tool()
def dcim_action(
    resource: str,
    id: int,
    action: str,
    body: Optional[dict[str, Any]] = None,
    params: Optional[dict[str, Any]] = None,
) -> str:
    """Perform a special action on a DCIM, IPAM, or circuits object.

    Args:
        resource: Resource type. Resources with actions:
            DCIM:
              devices        -> render-config (POST)
              console-ports  -> trace (GET)
              console-server-ports -> trace (GET)
              front-ports    -> paths (GET)
              interfaces     -> trace (GET)
              power-feeds    -> trace (GET)
              power-outlets  -> trace (GET)
              power-ports    -> trace (GET)
              racks          -> elevation (GET, params: face=front|rear, unit=int)
              rear-ports     -> paths (GET)
            IPAM:
              asn-ranges     -> available-asns (GET/POST)
              ip-ranges      -> available-ips (GET/POST)
              prefixes       -> available-ips (GET/POST), available-prefixes (GET/POST)
              vlan-groups    -> available-vlans (GET/POST)
            Circuits:
              circuit-terminations         -> paths (GET)
              virtual-circuit-terminations -> paths (GET)
        id: Numeric ID of the parent object
        action: Action name (e.g. trace, paths, elevation, render-config,
                available-ips, available-prefixes, available-vlans, available-asns)
        body: Request body for POST actions
        params: Query parameters for GET actions
    """
    err = _validate_resource(resource)
    if err:
        return json.dumps({"error": err})

    all_actions = {**RESOURCE_ACTIONS, **IPAM_ACTIONS, **CIRCUITS_ACTIONS}
    valid_actions = all_actions.get(resource, [])
    if action not in valid_actions:
        return json.dumps({
            "error": f"'{action}' is not a valid action for '{resource}'. "
                     f"Valid actions: {valid_actions}"
        })

    url = _api_url(resource, id, action)

    with make_client() as client:
        if body is not None:
            resp = client.post(
                url,
                json=body,
                headers={"Content-Type": "application/json"},
                params=params or {},
            )
        else:
            resp = client.get(url, params=params or {})
    return _handle_response(resp)


# ---------------------------------------------------------------------------
# SCHEMA INTROSPECTION HELPER
# ---------------------------------------------------------------------------

@mcp.tool()
def dcim_resource_info(resource: str) -> str:
    """Get field information for any NetBox resource (DCIM, IPAM, or circuits).

    Returns the required fields and all available writable fields
    for creating/updating the given resource.

    Args:
        resource: Resource type from DCIM, IPAM, or circuits namespaces.
                  Use dcim_list to see all available resource names.
    """
    err = _validate_resource(resource)
    if err:
        return json.dumps({"error": err})

    ns = _namespace(resource)
    all_required = {**REQUIRED_FIELDS, **IPAM_REQUIRED_FIELDS, **CIRCUITS_REQUIRED_FIELDS}
    all_fields = {**RESOURCE_FIELDS, **IPAM_RESOURCE_FIELDS, **CIRCUITS_RESOURCE_FIELDS}
    all_actions = {**RESOURCE_ACTIONS, **IPAM_ACTIONS, **CIRCUITS_ACTIONS}

    info = {
        "resource": resource,
        "namespace": ns,
        "required_for_create": all_required.get(resource, []),
        "writable_fields": all_fields.get(resource, []),
        "supports_actions": all_actions.get(resource, []),
        "collection_url": f"/api/{ns}/{resource}/",
        "object_url": f"/api/{ns}/{resource}/{{id}}/",
    }
    return json.dumps(info, indent=2)


# ---------------------------------------------------------------------------
# IPAM TOOLS
# ---------------------------------------------------------------------------

@mcp.tool()
def ipam_list(
    resource: str,
    limit: int = 50,
    offset: int = 0,
    filters: Optional[dict[str, Any]] = None,
) -> str:
    """List IPAM objects with optional filtering.

    Args:
        resource: IPAM resource type. One of: aggregates, asn-ranges, asns,
            fhrp-group-assignments, fhrp-groups, ip-addresses, ip-ranges,
            prefixes, rirs, roles, route-targets, service-templates, services,
            vlan-groups, vlan-translation-policies, vlan-translation-rules,
            vlans, vrfs
        limit: Maximum number of results (default 50)
        offset: Pagination offset
        filters: Dict of query filter params, e.g.:
            ip-addresses: {"vrf": "default", "status": "active", "dns_name__ic": "web"}
            prefixes:     {"prefix": "10.0.0.0/8", "vrf_id": 1, "status": "active"}
            vlans:        {"vid": 100, "site": "nyc", "status": "active"}
            vrfs:         {"name": "default", "tenant": "acme"}
            Common: id, q (search), tag, tenant, tenant_id, ordering
    """
    if resource not in IPAM_RESOURCES:
        return json.dumps({"error": f"Unknown IPAM resource '{resource}'. Valid: {', '.join(sorted(IPAM_RESOURCES))}"})

    params: dict[str, Any] = {"limit": limit, "offset": offset}
    if filters:
        params.update(filters)

    with make_client() as client:
        resp = client.get(_api_url(resource), params=params)
    return _handle_response(resp)


@mcp.tool()
def ipam_get(resource: str, id: int) -> str:
    """Get a single IPAM object by its numeric ID.

    Args:
        resource: IPAM resource type (see ipam_list for full list)
        id: Numeric ID of the object
    """
    if resource not in IPAM_RESOURCES:
        return json.dumps({"error": f"Unknown IPAM resource '{resource}'. Valid: {', '.join(sorted(IPAM_RESOURCES))}"})

    with make_client() as client:
        resp = client.get(_api_url(resource, id))
    return _handle_response(resp)


@mcp.tool()
def ipam_create(resource: str, body: dict[str, Any]) -> str:
    """Create a new IPAM object. Supports bulk create (pass a list as body).

    Args:
        resource: IPAM resource type (see ipam_list for full list)
        body: Object data. Required fields by resource:
            ip-addresses:   address (e.g. "192.0.2.1/24")
            prefixes:       prefix (e.g. "10.0.0.0/8")
            ip-ranges:      start_address, end_address
            vlans:          name, vid (1-4094)
            vrfs:           name
            aggregates:     prefix, rir (id)
            asns:           asn (integer)
            asn-ranges:     name, slug, rir (id), start, end
            rirs:           name, slug
            roles:          name, slug
            route-targets:  name
            vlan-groups:    name, slug
            services:       name, parent_object_type, parent_object_id, ports, protocol
            service-templates: name, ports, protocol
            fhrp-groups:    group_id, protocol
            fhrp-group-assignments: group (id), interface_type, interface_id, priority

            Common optional: vrf (id), tenant (id), status, description,
            comments, tags, custom_fields
    """
    if resource not in IPAM_RESOURCES:
        return json.dumps({"error": f"Unknown IPAM resource '{resource}'. Valid: {', '.join(sorted(IPAM_RESOURCES))}"})

    with make_client() as client:
        resp = client.post(
            _api_url(resource),
            json=body,
            headers={"Content-Type": "application/json"},
        )
    return _handle_response(resp)


@mcp.tool()
def ipam_update(resource: str, id: int, body: dict[str, Any]) -> str:
    """Fully update (PUT) an IPAM object. All required fields must be included.

    Supports bulk update by passing a list: [{"id": 1, ...}, {"id": 2, ...}]

    Args:
        resource: IPAM resource type (see ipam_list for full list)
        id: Numeric ID (ignored for bulk, pass 0)
        body: Complete object data or list for bulk update
    """
    if resource not in IPAM_RESOURCES:
        return json.dumps({"error": f"Unknown IPAM resource '{resource}'. Valid: {', '.join(sorted(IPAM_RESOURCES))}"})

    with make_client() as client:
        if isinstance(body, list):
            resp = client.put(_api_url(resource), json=body, headers={"Content-Type": "application/json"})
        else:
            resp = client.put(_api_url(resource, id), json=body, headers={"Content-Type": "application/json"})
    return _handle_response(resp)


@mcp.tool()
def ipam_patch(resource: str, id: int, body: dict[str, Any]) -> str:
    """Partially update (PATCH) an IPAM object. Only include fields to change.

    Supports bulk patch by passing a list: [{"id": 1, "status": "active"}, ...]

    Args:
        resource: IPAM resource type (see ipam_list for full list)
        id: Numeric ID (ignored for bulk, pass 0)
        body: Fields to update, or list for bulk patch

    Examples:
        Mark IP active: body={"status": "active"}
        Assign to VRF:  body={"vrf": 3}
        Set DNS name:   body={"dns_name": "web01.example.com"}
        Assign to interface: body={"assigned_object_type": "dcim.interface", "assigned_object_id": 42}
    """
    if resource not in IPAM_RESOURCES:
        return json.dumps({"error": f"Unknown IPAM resource '{resource}'. Valid: {', '.join(sorted(IPAM_RESOURCES))}"})

    with make_client() as client:
        if isinstance(body, list):
            resp = client.patch(_api_url(resource), json=body, headers={"Content-Type": "application/json"})
        else:
            resp = client.patch(_api_url(resource, id), json=body, headers={"Content-Type": "application/json"})
    return _handle_response(resp)


@mcp.tool()
def ipam_delete(resource: str, id: int) -> str:
    """Delete an IPAM object by ID.

    Args:
        resource: IPAM resource type (see ipam_list for full list)
        id: Numeric ID of the object to delete
    """
    if resource not in IPAM_RESOURCES:
        return json.dumps({"error": f"Unknown IPAM resource '{resource}'. Valid: {', '.join(sorted(IPAM_RESOURCES))}"})

    with make_client() as client:
        resp = client.delete(_api_url(resource, id))
    if resp.status_code == 204:
        return json.dumps({"success": True, "message": f"Deleted {resource} {id}"})
    return _handle_response(resp)


@mcp.tool()
def ipam_action(
    resource: str,
    id: int,
    action: str,
    body: Optional[dict[str, Any]] = None,
    params: Optional[dict[str, Any]] = None,
) -> str:
    """Perform an availability action on an IPAM object.

    Args:
        resource: IPAM resource type with actions:
            asn-ranges  -> available-asns  (GET: list free ASNs; POST: allocate)
            ip-ranges   -> available-ips   (GET: list free IPs; POST: allocate)
            prefixes    -> available-ips   (GET/POST: next available IP in prefix)
                        -> available-prefixes (GET/POST: next available child prefix)
            vlan-groups -> available-vlans (GET: list free VIDs; POST: allocate)
        id: Numeric ID of the parent object
        action: One of: available-asns, available-ips, available-prefixes, available-vlans
        body: For POST allocation, e.g. {"prefix_length": 24} for available-prefixes,
              or {"address": "..."} to request specific IP, or {} for next available
        params: Query params for GET (e.g. {"limit": 10})
    """
    if resource not in IPAM_RESOURCES:
        return json.dumps({"error": f"Unknown IPAM resource '{resource}'. Valid: {', '.join(sorted(IPAM_RESOURCES))}"})

    valid_actions = IPAM_ACTIONS.get(resource, [])
    if action not in valid_actions:
        return json.dumps({"error": f"'{action}' is not valid for '{resource}'. Valid: {valid_actions}"})

    url = _api_url(resource, id, action)
    with make_client() as client:
        if body is not None:
            resp = client.post(url, json=body, headers={"Content-Type": "application/json"}, params=params or {})
        else:
            resp = client.get(url, params=params or {})
    return _handle_response(resp)


# ---------------------------------------------------------------------------
# CIRCUITS TOOLS
# ---------------------------------------------------------------------------

@mcp.tool()
def circuits_list(
    resource: str,
    limit: int = 50,
    offset: int = 0,
    filters: Optional[dict[str, Any]] = None,
) -> str:
    """List circuits objects with optional filtering.

    Args:
        resource: Circuits resource type. One of: circuit-group-assignments,
            circuit-groups, circuit-terminations, circuit-types, circuits,
            provider-accounts, provider-networks, providers,
            virtual-circuit-terminations, virtual-circuit-types, virtual-circuits
        limit: Maximum number of results (default 50)
        offset: Pagination offset
        filters: Dict of query filter params, e.g.:
            circuits:  {"provider": "att", "status": "active", "cid__ic": "CKT"}
            providers: {"name": "AT&T", "asn": 7018}
            Common: id, q (search), tag, tenant, tenant_id, ordering
    """
    if resource not in CIRCUITS_RESOURCES:
        return json.dumps({"error": f"Unknown circuits resource '{resource}'. Valid: {', '.join(sorted(CIRCUITS_RESOURCES))}"})

    params: dict[str, Any] = {"limit": limit, "offset": offset}
    if filters:
        params.update(filters)

    with make_client() as client:
        resp = client.get(_api_url(resource), params=params)
    return _handle_response(resp)


@mcp.tool()
def circuits_get(resource: str, id: int) -> str:
    """Get a single circuits object by its numeric ID.

    Args:
        resource: Circuits resource type (see circuits_list for full list)
        id: Numeric ID of the object
    """
    if resource not in CIRCUITS_RESOURCES:
        return json.dumps({"error": f"Unknown circuits resource '{resource}'. Valid: {', '.join(sorted(CIRCUITS_RESOURCES))}"})

    with make_client() as client:
        resp = client.get(_api_url(resource, id))
    return _handle_response(resp)


@mcp.tool()
def circuits_create(resource: str, body: dict[str, Any]) -> str:
    """Create a new circuits object. Supports bulk create (pass a list as body).

    Args:
        resource: Circuits resource type (see circuits_list for full list)
        body: Object data. Required fields by resource:
            circuits:                   cid, provider (id), type (id)
            circuit-terminations:       circuit (id), term_side ("A" or "Z")
            circuit-types:              name, slug
            providers:                  name, slug
            provider-accounts:          account, provider (id)
            provider-networks:          name, provider (id)
            circuit-groups:             name, slug
            circuit-group-assignments:  group (id), member_type, member_id, priority
            virtual-circuits:           cid, provider_network (id), type (id)
            virtual-circuit-types:      name, slug
            virtual-circuit-terminations: virtual_circuit (id), interface (id)

            Common optional: status, tenant (id), description, comments,
            tags, custom_fields
    """
    if resource not in CIRCUITS_RESOURCES:
        return json.dumps({"error": f"Unknown circuits resource '{resource}'. Valid: {', '.join(sorted(CIRCUITS_RESOURCES))}"})

    with make_client() as client:
        resp = client.post(
            _api_url(resource),
            json=body,
            headers={"Content-Type": "application/json"},
        )
    return _handle_response(resp)


@mcp.tool()
def circuits_update(resource: str, id: int, body: dict[str, Any]) -> str:
    """Fully update (PUT) a circuits object. All required fields must be included.

    Supports bulk update by passing a list: [{"id": 1, ...}, {"id": 2, ...}]

    Args:
        resource: Circuits resource type (see circuits_list for full list)
        id: Numeric ID (ignored for bulk, pass 0)
        body: Complete object data or list for bulk update
    """
    if resource not in CIRCUITS_RESOURCES:
        return json.dumps({"error": f"Unknown circuits resource '{resource}'. Valid: {', '.join(sorted(CIRCUITS_RESOURCES))}"})

    with make_client() as client:
        if isinstance(body, list):
            resp = client.put(_api_url(resource), json=body, headers={"Content-Type": "application/json"})
        else:
            resp = client.put(_api_url(resource, id), json=body, headers={"Content-Type": "application/json"})
    return _handle_response(resp)


@mcp.tool()
def circuits_patch(resource: str, id: int, body: dict[str, Any]) -> str:
    """Partially update (PATCH) a circuits object. Only include fields to change.

    Supports bulk patch by passing a list: [{"id": 1, "status": "active"}, ...]

    Args:
        resource: Circuits resource type (see circuits_list for full list)
        id: Numeric ID (ignored for bulk, pass 0)
        body: Fields to update, or list for bulk patch

    Examples:
        Update commit rate: body={"commit_rate": 1000000}
        Change status:      body={"status": "decommissioned"}
        Set install date:   body={"install_date": "2024-01-15"}
    """
    if resource not in CIRCUITS_RESOURCES:
        return json.dumps({"error": f"Unknown circuits resource '{resource}'. Valid: {', '.join(sorted(CIRCUITS_RESOURCES))}"})

    with make_client() as client:
        if isinstance(body, list):
            resp = client.patch(_api_url(resource), json=body, headers={"Content-Type": "application/json"})
        else:
            resp = client.patch(_api_url(resource, id), json=body, headers={"Content-Type": "application/json"})
    return _handle_response(resp)


@mcp.tool()
def circuits_delete(resource: str, id: int) -> str:
    """Delete a circuits object by ID.

    Args:
        resource: Circuits resource type (see circuits_list for full list)
        id: Numeric ID of the object to delete
    """
    if resource not in CIRCUITS_RESOURCES:
        return json.dumps({"error": f"Unknown circuits resource '{resource}'. Valid: {', '.join(sorted(CIRCUITS_RESOURCES))}"})

    with make_client() as client:
        resp = client.delete(_api_url(resource, id))
    if resp.status_code == 204:
        return json.dumps({"success": True, "message": f"Deleted {resource} {id}"})
    return _handle_response(resp)


@mcp.tool()
def circuits_action(
    resource: str,
    id: int,
    action: str,
    params: Optional[dict[str, Any]] = None,
) -> str:
    """Get cable path traces for circuit terminations.

    Args:
        resource: circuit-terminations or virtual-circuit-terminations
        id: Numeric ID of the termination object
        action: paths
        params: Optional query parameters
    """
    if resource not in CIRCUITS_RESOURCES:
        return json.dumps({"error": f"Unknown circuits resource '{resource}'. Valid: {', '.join(sorted(CIRCUITS_RESOURCES))}"})

    valid_actions = CIRCUITS_ACTIONS.get(resource, [])
    if action not in valid_actions:
        return json.dumps({"error": f"'{action}' is not valid for '{resource}'. Valid: {valid_actions}"})

    url = _api_url(resource, id, action)
    with make_client() as client:
        resp = client.get(url, params=params or {})
    return _handle_response(resp)


if __name__ == "__main__":
    mcp.run()
