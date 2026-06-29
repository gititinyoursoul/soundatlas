import json
import gzip
import urllib.error
import urllib.parse
import urllib.request
from typing import Any


class MediaProviderError(RuntimeError):
    pass


def request_json(
    url: str,
    params: dict[str, str] | None = None,
    method: str = "GET",
    body: bytes | None = None,
    headers: dict[str, str] | None = None,
) -> dict[str, Any]:
    if params:
        url = f"{url}?{urllib.parse.urlencode(params)}"
    request = urllib.request.Request(
        url,
        data=body,
        headers=headers or {},
        method=method,
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            raw_body = response.read()
            if response.headers.get("Content-Encoding", "").lower() == "gzip":
                raw_body = gzip.decompress(raw_body)
            return json.loads(raw_body.decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise MediaProviderError(f"HTTP {exc.code}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise MediaProviderError(str(exc.reason)) from exc
