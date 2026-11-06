"""Concurrent hash-linked JSONL event ledger, redaction and HMAC checkpoints."""
import hashlib
import hmac
import json
import os
from pathlib import Path
import re
import threading
import time
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

NULL_HASH = "0" * 64
SENSITIVE = re.compile(r"(token|password|secret|authorization|api[_-]?key|cookie|wallet|private[_-]?key)", re.I)
BEARER = re.compile(r"(?i)\b(bearer\s+)[A-Za-z0-9._~+\/-]{8,}")


def redact(value):
    """Never persist header/query values that may carry credentials."""
    if isinstance(value, dict):
        return {str(key): ("[REDACTED]" if SENSITIVE.search(str(key)) else redact(val)) for key, val in value.items()}
    if isinstance(value, list):
        return [redact(item) for item in value]
    if isinstance(value, str):
        value = BEARER.sub(r"\1[REDACTED]", value)
        if "?" in value and "://" in value:
            parts = urlsplit(value)
            params = [(k, "[REDACTED]" if SENSITIVE.search(k) else v) for k, v in parse_qsl(parts.query, keep_blank_values=True)]
            value = urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(params), ""))
        return value
    return value


def digest_payload(payload):
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


class AuditLedger:
    def __init__(self, path: str | Path, key: str | None = None):
        self.path = Path(path)
        self.key = key or ""
        self.lock = threading.RLock()

    def _records(self):
        if not self.path.exists():
            return []
        return [json.loads(line) for line in self.path.read_text(encoding="utf-8").splitlines() if line.strip()]

    def append(self, category: str, details: dict):
        if not isinstance(category, str) or not category.isidentifier() or not isinstance(details, dict):
            raise ValueError("Invalid audit event")
        with self.lock:
            entries = self._records()
            valid = self._verify(entries)
            if not valid["valid"]:
                raise ValueError("Audit chain integrity failure; write blocked")
            prev = entries[-1]["hash"] if entries else NULL_HASH
            record = {"seq": len(entries) + 1, "timestamp": time.time(), "category": category,
                      "details": redact(details), "prev": prev}
            record["hash"] = digest_payload(record)
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self.path.open("a", encoding="utf-8", newline="\n") as stream:
                stream.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
                stream.flush()
                os.fsync(stream.fileno())
            return record["hash"]

    @staticmethod
    def _verify(entries):
        prev = NULL_HASH
        for seq, record in enumerate(entries, start=1):
            if not isinstance(record, dict) or record.get("seq") != seq or record.get("prev") != prev:
                return {"valid": False, "records": seq - 1, "error": "broken_sequence_or_previous_hash"}
            check = {k: v for k, v in record.items() if k != "hash"}
            if record.get("hash") != digest_payload(check):
                return {"valid": False, "records": seq - 1, "error": "mismatched_hash"}
            prev = record["hash"]
        return {"valid": True, "records": len(entries), "last_hash": prev}

    def verify(self):
        with self.lock:
            try:
                return self._verify(self._records())
            except (ValueError, OSError, UnicodeDecodeError):
                return {"valid": False, "records": 0, "error": "unreadable_ledger"}

    def checkpoint(self):
        if not self.key:
            raise ValueError("SAGAZ_AUDIT_KEY must be configured to sign a checkpoint")
        with self.lock:
            result = self.verify()
            if not result["valid"]:
                raise ValueError("Ledger integrity failure")
            item = {"last_hash": result["last_hash"], "records": result["records"]}
            payload = json.dumps(item, sort_keys=True, separators=(",", ":")).encode()
            item["signature"] = hmac.new(self.key.encode(), payload, hashlib.sha256).hexdigest()
            return item

    def verify_checkpoint(self, checkpoint: dict):
        if not self.key:
            return False
        try:
            item = {"last_hash": checkpoint["last_hash"], "records": checkpoint["records"]}
            signature = checkpoint["signature"]
            payload = json.dumps(item, sort_keys=True, separators=(",", ":")).encode()
            actual = hmac.new(self.key.encode(), payload, hashlib.sha256).hexdigest()
            return hmac.compare_digest(actual, signature) and self.verify()["last_hash"] == item["last_hash"]
        except (KeyError, TypeError):
            return False
