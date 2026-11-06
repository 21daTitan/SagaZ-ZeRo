"""Minimal MCP tools/resources/prompts over authenticated JSON-RPC."""
from sagaz.attribution import credits
from sagaz.tools.bus import Bus
from sagaz.gateway.protocols import rpc_result, rpc_error, validate_rpc
from sagaz.gateway.policy import Denied
from sagaz.cti import CTIError

TOOLS = [
    {"name": "sagaz_status", "description": "Get SagaZ status and attribution",
     "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False}},
    {"name": "sagaz_skills", "description": "List installed skill manifests",
     "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False}},
    {"name": "sagaz_cti_summary", "description": "Summarize the local, read-only CTI catalog",
     "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False}},
    {"name": "sagaz_cti_search", "description": "Search the local CTI catalog by ID, topic, or keyword",
     "inputSchema": {"type": "object", "properties": {
         "q": {"type": "string", "minLength": 1, "maxLength": 200},
         "limit": {"type": "integer", "minimum": 1, "maximum": 50}},
         "required": ["q"], "additionalProperties": False}},
]
RESOURCES = [{"uri": "sagaz://provenance", "name": "Provenance", "mimeType": "application/json"}]
PROMPTS = [{"name": "sagaz_brief", "description": "Prepare a contextual brief for offline use",
            "arguments": [{"name": "brief", "description": "User brief", "required": True}]}]


def dispatch(payload, scope, audit=None):
    req = validate_rpc(payload)
    method = req["method"]
    params = req.get("params") or {}
    if not isinstance(params, dict):
        return rpc_error(req, -32602, "Invalid params")
    if method == "initialize":
        return rpc_result(req, {"protocolVersion": "2025-03-26", "capabilities": {
            "tools": {}, "resources": {}, "prompts": {}}, "serverInfo": {"name": "sagaz-zero", "version": credits()["version"]}})
    if method == "notifications/initialized":
        return None
    if method == "ping":
        return rpc_result(req, {})
    if method == "tools/list":
        return rpc_result(req, {"tools": TOOLS})
    if method == "resources/list":
        return rpc_result(req, {"resources": RESOURCES})
    if method == "resources/read":
        if params.get("uri") != "sagaz://provenance":
            return rpc_error(req, -32602, "Unknown resource")
        import json
        return rpc_result(req, {"contents": [{"uri": "sagaz://provenance", "mimeType": "application/json",
                                               "text": json.dumps(credits(), ensure_ascii=False)}]})
    if method == "prompts/list":
        return rpc_result(req, {"prompts": PROMPTS})
    if method == "prompts/get":
        if params.get("name") != "sagaz_brief" or not isinstance((params.get("arguments") or {}).get("brief"), str):
            return rpc_error(req, -32602, "Invalid prompt arguments")
        return rpc_result(req, {"description": "Offline preparation template", "messages": [{
            "role": "user", "content": {"type": "text", "text": "Organize o briefing: " + params["arguments"]["brief"][:6000]}}]})
    if method == "tools/call":
        name = params.get("name")
        try:
            scope.check_tool(name)
        except Denied:
            return rpc_error(req, -32003, "Tool not permitted")
        try:
            data = Bus(audit=audit).call(scope, name, params.get("arguments") or {})
        except (Denied, ValueError):
            return rpc_error(req, -32602, "Tool arguments or permissions invalid")
        except CTIError:
            return rpc_error(req, -32603, "CTI catalog unavailable")
        import json
        return rpc_result(req, {"content": [{"type": "text", "text": json.dumps(data, ensure_ascii=False)}]})
    return rpc_error(req, -32601, "Method not found")
