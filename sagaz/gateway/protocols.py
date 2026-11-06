"""Strict, non-streaming OpenAI and MCP JSON-RPC request validation."""
import json


class ProtocolError(ValueError):
    pass


def validate_chat(payload: dict, model: str):
    if not isinstance(payload, dict):
        raise ProtocolError("Chat request must be an object")
    if payload.get("stream", False):
        raise ProtocolError("Streaming is not implemented; set stream=false")
    messages = payload.get("messages")
    if not isinstance(messages, list) or not 1 <= len(messages) <= 80:
        raise ProtocolError("messages must contain 1 to 80 entries")
    for msg in messages:
        if not isinstance(msg, dict) or msg.get("role") not in {"system", "developer", "user", "assistant", "tool"}:
            raise ProtocolError("Invalid message role")
        content = msg.get("content")
        if not (isinstance(content, str) or (isinstance(content, list) and len(content) <= 20)):
            raise ProtocolError("Invalid message content")
    requested = payload.get("model", model)
    if requested != model:
        raise ProtocolError("Only the explicitly configured DSANT_MODEL may be used")
    allowed = {"model", "messages", "temperature", "max_tokens", "top_p", "stream", "response_format", "tools", "tool_choice"}
    result = {k: v for k, v in payload.items() if k in allowed}
    result["model"] = model
    result["stream"] = False
    return result


def validate_rpc(payload):
    if not isinstance(payload, dict) or payload.get("jsonrpc") != "2.0":
        raise ProtocolError("JSON-RPC 2.0 object required")
    if not isinstance(payload.get("method"), str):
        raise ProtocolError("Method required")
    if "id" in payload and not (payload["id"] is None or type(payload["id"]) in (int, str)):
        raise ProtocolError("Invalid RPC id")
    return payload


def rpc_result(request, result):
    return {"jsonrpc": "2.0", "id": request.get("id"), "result": result}


def rpc_error(request, code: int, message: str):
    return {"jsonrpc": "2.0", "id": request.get("id") if isinstance(request, dict) else None,
            "error": {"code": code, "message": message}}
