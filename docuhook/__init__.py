"""Official DocuHook Python client."""

from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Mapping, MutableMapping, Optional


class DocuHookError(Exception):
    def __init__(self, message: str, status: int = 0, body: Any = None) -> None:
        super().__init__(message)
        self.status = status
        self.body = body


class Client:
    """Minimal DocuHook API client (stdlib only)."""

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://docuhook.com",
        timeout: float = 30.0,
    ) -> None:
        api_key = (api_key or "").strip()
        if not api_key:
            raise ValueError("DocuHook api_key is required")
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def render(
        self,
        data: Mapping[str, Any],
        html: str,
        *,
        mode: str = "sync",
        filename: str = "document.pdf",
    ) -> dict[str, Any]:
        return self._request(
            "POST",
            "/api/v1/render",
            {
                "mode": "async" if mode == "async" else "sync",
                "data": dict(data),
                "html": html,
                "filename": filename,
            },
        )

    def hook_render(
        self,
        data: Mapping[str, Any],
        html: str,
        *,
        mode: str = "async",
        filename: str = "document.pdf",
    ) -> dict[str, Any]:
        return self._request(
            "POST",
            "/api/v1/hooks/render",
            {
                "mode": "sync" if mode == "sync" else "async",
                "data": dict(data),
                "html": html,
                "filename": filename,
            },
        )

    def job_status(self, job_id: str) -> dict[str, Any]:
        return self._request("GET", f"/api/v1/jobs/{urllib.parse.quote(job_id, safe='')}")

    def job_result(self, job_id: str) -> dict[str, Any]:
        return self._request("GET", f"/api/v1/jobs/{urllib.parse.quote(job_id, safe='')}/result")

    def _request(
        self,
        method: str,
        path: str,
        payload: Optional[MutableMapping[str, Any]] = None,
    ) -> dict[str, Any]:
        body = None if payload is None else json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            f"{self.base_url}{path}",
            data=body,
            method=method,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "X-DocuHook-Key": self.api_key,
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as res:
                raw = res.read().decode("utf-8")
                status = getattr(res, "status", 200)
        except urllib.error.HTTPError as exc:
            raw = exc.read().decode("utf-8", errors="replace")
            status = exc.code
            try:
                data = json.loads(raw) if raw else {}
            except json.JSONDecodeError:
                data = {"error": raw}
            message = data.get("error") if isinstance(data, dict) else str(data)
            raise DocuHookError(str(message or f"HTTP {status}"), status, data) from exc

        try:
            data = json.loads(raw) if raw else {}
        except json.JSONDecodeError as exc:
            raise DocuHookError("Invalid JSON response", status, raw) from exc

        if not isinstance(data, dict):
            raise DocuHookError("Unexpected response shape", status, data)

        out: dict[str, Any] = {"ok": True, "raw": data, "status_code": status}
        for key in ("html", "filename", "job_id", "status", "status_url", "result_url"):
            if key in data:
                out[key] = data[key]
        return out


__all__ = ["Client", "DocuHookError"]
