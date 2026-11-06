"""Explicit provider client: no implicit API calls, fixed validated endpoint."""
import json
import os
from urllib.parse import urlsplit
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


class ProviderUnavailable(RuntimeError):
    pass


def connection_details():
    base = os.environ.get("DSANT_BASE_URL", "").strip().rstrip("/")
    model = os.environ.get("DSANT_MODEL", "").strip()
    key = os.environ.get("DSANT_API_KEY", "")
    if not base or not model:
        raise ProviderUnavailable("DSANT_BASE_URL and DSANT_MODEL are required")
    parsed = urlsplit(base)
    local = parsed.hostname in ("127.0.0.1", "localhost", "::1")
    if (parsed.scheme not in ("http", "https") or (parsed.scheme == "http" and not local)
            or parsed.username or parsed.password or parsed.query or parsed.fragment):
        raise ProviderUnavailable("Only HTTPS or local loopback HTTP provider URLs are permitted")
    if not local and not key:
        raise ProviderUnavailable("Remote provider requires DSANT_API_KEY")
    if not parsed.path.endswith("/v1"):
        raise ProviderUnavailable("DSANT_BASE_URL must end in /v1")
    return base, model, key


def complete(payload: dict, timeout=45):
    base, model, key = connection_details()
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    if key:
        headers["Authorization"] = "Bearer " + key
    request = Request(base + "/chat/completions", json.dumps(payload, ensure_ascii=False).encode("utf-8"), headers, method="POST")
    try:
        with urlopen(request, timeout=timeout) as reply:
            raw = reply.read(4_000_001)
            if len(raw) > 4_000_000:
                raise ProviderUnavailable("Provider response too large")
        result = json.loads(raw)
        if not isinstance(result, dict) or not isinstance(result.get("choices"), list):
            raise ValueError("Missing choices")
        return result
    except (HTTPError, URLError, ValueError, TimeoutError, OSError) as exc:
        # Do not include provider exception strings: some proxies return credentials in error URLs.
        raise ProviderUnavailable("Provider failed: " + type(exc).__name__) from None
