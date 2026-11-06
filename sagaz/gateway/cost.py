"""Usage and cost metering; no invented USD estimate when pricing is unknown."""
from decimal import Decimal, InvalidOperation
import json
from pathlib import Path
import threading
from datetime import datetime, timezone


class CostMeter:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.lock = threading.RLock()

    def record(self, connector: str, model: str, usage: dict, input_price: str | None = None, output_price: str | None = None):
        if not isinstance(usage, dict):
            raise ValueError("Usage must be an object")
        prompt = usage.get("prompt_tokens")
        completion = usage.get("completion_tokens")
        count_ok = all(type(x) is int and 0 <= x <= 10000000 for x in (prompt, completion))
        if not count_ok:
            raise ValueError("Actual provider token usage required")
        usd = None
        if input_price is not None and output_price is not None:
            try:
                inp = Decimal(input_price)
                out = Decimal(output_price)
                if not (inp.is_finite() and out.is_finite()) or min(inp, out) < 0:
                    raise ValueError("Invalid price")
                usd = str((inp * prompt + out * completion) / Decimal(1000000))
            except InvalidOperation as exc:
                raise ValueError("Invalid price") from exc
        item = {"at": datetime.now(timezone.utc).isoformat(), "connector": connector, "model": model,
                "prompt_tokens": prompt, "completion_tokens": completion, "usd": usd}
        with self.lock:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self.path.open("a", encoding="utf-8") as stream:
                stream.write(json.dumps(item, sort_keys=True) + "\n")
        return item

    def report(self, connector=None, budget_usd=None):
        with self.lock:
            items = []
            if self.path.is_file():
                items = [json.loads(line) for line in self.path.read_text(encoding="utf-8").splitlines() if line.strip()]
        if connector:
            items = [item for item in items if item["connector"] == connector]
        total = sum((Decimal(item["usd"]) for item in items if item["usd"] is not None), Decimal("0"))
        unpriced = sum(item["usd"] is None for item in items)
        budget = Decimal(str(budget_usd)) if budget_usd is not None else None
        return {"connector": connector or "all", "count": len(items), "total_known_usd": str(total),
                "unpriced_requests": unpriced, "budget_usd": str(budget) if budget is not None else None,
                "at_or_above_80_pct": (total >= budget * Decimal("0.8") if budget and not unpriced else None),
                "series": items[-100:]}
