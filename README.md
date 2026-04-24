# NetBox MCP Server

A read/write [Model Context Protocol](https://modelcontextprotocol.io) server for NetBox, covering all endpoints in the DCIM, IPAM, and Circuits namespaces.

## Requirements

- Python 3.11+
- NetBox instance with API access
- A NetBox API token

## Setup

### 1. Clone the repository

```bash
mkdir /path/to/desired/MCP/directory
cd /path/to/desired/MCP/directory
git clone https://github.com/gregbur000/netbox-rw.git
```

### 2. Create a virtual environment and install dependencies

```bash
python3 -m venv .
source bin/activate
pip install mcp httpx
```

### 2. Configure your token

Copy the example env file:

```bash
cp .env.example .env
```

Edit `.env`:

```
NETBOX_URL=https://your-netbox-instance
NETBOX_TOKEN=your_api_token_here
```

The server reads these at startup from environment variables — you can also set them directly in your MCP client config (see below).

> **SSL:** The server skips SSL verification by default to support self-signed certificates. Remove the `verify=False` argument in `make_client()` if your instance has a valid certificate.

---

## Deploying to Claude Desktop

Edit `~/Library/Application Support/Claude/claude_desktop_config.json` and add the server under `mcpServers`:

```json
{
  "mcpServers": {
    "Netbox MCP": {
      "command": "/path/to/netbox-rw/bin/python3",
      "args": ["/path/to/netbox-rw/server.py"],
      "env": {
        "NETBOX_URL": "https://your-netbox-instance",
        "NETBOX_TOKEN": "your_api_token_here"
      }
    }
  }
}
```

Quit and relaunch Claude Desktop. The server will appear in the tools panel as **Netbox MCP**.

---

## Deploying to Claude Code

Add the server to your global Claude Code settings:

```bash
claude mcp add "Netbox MCP" \
  --scope user \
  -e NETBOX_URL=https://your-netbox-instance \
  -e NETBOX_TOKEN=your_api_token_here \
  -- /path/to/netbox-rw/bin/python3 /path/to/netbox-rw/server.py
```

Or edit `~/.claude.json` directly under the `mcpServers` key using the same structure as the Claude Desktop config above.

---

## Tools

The server exposes 23 tools organized by namespace.

### DCIM — `/api/dcim/`

| Tool | Description |
|---|---|
| `dcim_list` | List resources with optional filters and pagination |
| `dcim_get` | Get a single resource by numeric ID |
| `dcim_create` | Create one or many resources (pass a list for bulk) |
| `dcim_update` | Full replace (PUT) — single or bulk |
| `dcim_patch` | Partial update (PATCH) — single or bulk |
| `dcim_delete` | Delete by ID |
| `dcim_bulk_delete` | Delete a list of IDs in one call |
| `dcim_action` | Sub-resource actions: `trace`, `paths`, `elevation`, `render-config` |
| `dcim_resource_info` | Show required/writable fields for any resource |

**Supported DCIM resources (45):** cable-terminations, cables, connected-device, console-port-templates, console-ports, console-server-port-templates, console-server-ports, device-bay-templates, device-bays, device-roles, device-types, devices, front-port-templates, front-ports, interface-templates, interfaces, inventory-item-roles, inventory-item-templates, inventory-items, locations, mac-addresses, manufacturers, module-bay-templates, module-bays, module-type-profiles, module-types, modules, platforms, power-feeds, power-outlet-templates, power-outlets, power-panels, power-port-templates, power-ports, rack-reservations, rack-roles, rack-types, racks, rear-port-templates, rear-ports, regions, site-groups, sites, virtual-chassis, virtual-device-contexts

### IPAM — `/api/ipam/`

| Tool | Description |
|---|---|
| `ipam_list` | List resources with optional filters |
| `ipam_get` | Get a single resource by ID |
| `ipam_create` | Create one or many resources |
| `ipam_update` | Full replace (PUT) — single or bulk |
| `ipam_patch` | Partial update (PATCH) — single or bulk |
| `ipam_delete` | Delete by ID |
| `ipam_action` | Availability actions: `available-ips`, `available-prefixes`, `available-vlans`, `available-asns` |

**Supported IPAM resources (18):** aggregates, asn-ranges, asns, fhrp-group-assignments, fhrp-groups, ip-addresses, ip-ranges, prefixes, rirs, roles, route-targets, service-templates, services, vlan-groups, vlan-translation-policies, vlan-translation-rules, vlans, vrfs

### Circuits — `/api/circuits/`

| Tool | Description |
|---|---|
| `circuits_list` | List resources with optional filters |
| `circuits_get` | Get a single resource by ID |
| `circuits_create` | Create one or many resources |
| `circuits_update` | Full replace (PUT) — single or bulk |
| `circuits_patch` | Partial update (PATCH) — single or bulk |
| `circuits_delete` | Delete by ID |
| `circuits_action` | Path trace: `paths` on circuit-terminations and virtual-circuit-terminations |

**Supported circuits resources (11):** circuit-group-assignments, circuit-groups, circuit-terminations, circuit-types, circuits, provider-accounts, provider-networks, providers, virtual-circuit-terminations, virtual-circuit-types, virtual-circuits

---

## Usage Examples

### List all active devices at a site
```
dcim_list resource="devices" filters={"site": "nyc-dc1", "status": "active"}
```

### Get field requirements before creating
```
dcim_resource_info resource="devices"
```

### Create a device
```
dcim_create resource="devices" body={
  "name": "spine-01",
  "device_type": 12,
  "role": 3,
  "site": 1,
  "status": "planned"
}
```

### Assign an IP address to an interface
```
ipam_patch resource="ip-addresses" id=142 body={
  "assigned_object_type": "dcim.interface",
  "assigned_object_id": 88,
  "status": "active"
}
```

### Get next available IP from a prefix
```
ipam_action resource="prefixes" id=5 action="available-ips" body={}
```

### Bulk update circuit statuses
```
circuits_patch resource="circuits" id=0 body=[
  {"id": 10, "status": "active"},
  {"id": 11, "status": "active"},
  {"id": 12, "status": "decommissioned"}
]
```

### Trace a cable path from an interface
```
dcim_action resource="interfaces" id=204 action="trace"
```

---

## Getting a NetBox API Token

1. Log in to your NetBox instance
2. Navigate to your profile → **API Tokens**
3. Click **Add a token** and copy the generated key

The token needs read permissions for GET operations and write permissions for POST/PUT/PATCH/DELETE.
