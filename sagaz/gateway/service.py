"""Request routing that never grants privileges from client-provided connector labels."""
import os
from pathlib import Path
from sagaz.gateway.capabilities import Capability, CapabilityCache
from sagaz.gateway.policy import RateLimiter, Denied
from sagaz.gateway.audit import AuditLedger
from sagaz.gateway.cost import CostMeter
from sagaz.gateway.skills import select_skill
from sagaz.gateway.protocols import validate_chat, ProtocolError
from sagaz.gateway.router import connection_details, complete, ProviderUnavailable
from sagaz.gateway.mcp import dispatch
from sagaz.god import system_prompt, resolve


class Gateway:
    def __init__(self, state_root: Path):
        self.state_root = Path(state_root)
        state = Path(state_root).parent / "gateway_state"
        self.audit = AuditLedger(state / "audit.jsonl", key=os.environ.get("SAGAZ_AUDIT_KEY"))
        self.cost = CostMeter(state / "cost.jsonl")
        self.capabilities = CapabilityCache(ttl_seconds=60)
        self.ratelimits = RateLimiter()

    def models(self):
        try:
            _, model, _ = connection_details()
            return {"object": "list", "data": [{"id": model, "object": "model", "owned_by": "configured_provider"}]}
        except ProviderUnavailable:
            return {"object": "list", "data": []}

    def capability(self, scope):
        try:
            _, model, _ = connection_details()
            row = self.capabilities.get_or_load(scope.connector, model, lambda: Capability(
                connector=scope.connector, model=model, tools=False, streaming=False,
                source="configured_unverified"))
            return row.__dict__
        except ProviderUnavailable:
            return {"connector": scope.connector, "model": None, "source": "not_configured", "tools": False, "streaming": False}

    def require(self, scope, operation):
        if scope.connector == "public":
            raise Denied("Authentication required")
        if not self.ratelimits.allow(scope.connector):
            raise Denied("Connector rate quota exhausted")
        self.audit.append("request", {"connector": scope.connector, "operation": operation})

    def chat(self, scope, payload):
        self.require(scope, "chat")
        try:
            _, model, _ = connection_details()
        except ProviderUnavailable as exc:
            raise ProviderUnavailable(str(exc))
        request = validate_chat(payload, model)
        profile = resolve()
        messages = request.get('messages') or []
        if not messages or messages[0].get('role') != 'system':
            request['messages'] = [{'role': 'system', 'content': system_prompt(profile)}] + messages
        budget = os.environ.get("SAGAZ_BUDGET_USD")
        if budget:
            report = self.cost.report(connector=scope.connector, budget_usd=budget)
            if report["unpriced_requests"] or report["at_or_above_80_pct"]:
                raise Denied("Budget threshold reached or unpriced usage prevents enforcement")
            if not (os.environ.get("SAGAZ_INPUT_USD_PER_M") and os.environ.get("SAGAZ_OUTPUT_USD_PER_M")):
                raise Denied("Price configuration required when enforcing SAGAZ_BUDGET_USD")
        result = complete(request)
        usage = result.get("usage")
        if isinstance(usage, dict):
            try:
                self.cost.record(scope.connector, model, usage, os.environ.get("SAGAZ_INPUT_USD_PER_M"),
                                 os.environ.get("SAGAZ_OUTPUT_USD_PER_M"))
            except ValueError:
                self.audit.append("usage_unverified", {"connector": scope.connector})
        else:
            self.audit.append("usage_missing", {"connector": scope.connector})
        self.audit.append("completion", {"connector": scope.connector, "model": model,
                                         "usage_present": isinstance(usage, dict)})
        return result

    def mcp(self, scope, payload):
        self.require(scope, "mcp")
        return dispatch(payload, scope, self.state_root / "discord_memory.sqlite3")

    def select(self, scope, payload):
        self.require(scope, "skills_select")
        text = payload.get("text")
        result = select_skill(text)
        return {"skill": result.name, "score": result.score, "reason": result.reason}
