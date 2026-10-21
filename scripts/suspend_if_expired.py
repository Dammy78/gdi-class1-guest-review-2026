#!/usr/bin/env python3
"""Suspend the guest-review Render static site after the NZDT expiry timestamp."""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime
from zoneinfo import ZoneInfo

NZ = ZoneInfo("Pacific/Auckland")


def main() -> int:
    service_id = os.environ.get("RENDER_GUEST_SERVICE_ID", "").strip()
    api_key = os.environ.get("RENDER_API_KEY", "").strip()
    expiry_raw = os.environ.get("GUEST_REVIEW_EXPIRY_NZDT", "").strip()
    if not service_id or not api_key or not expiry_raw:
        print("MISSING_CONFIG", file=sys.stderr)
        return 2
    expiry = datetime.strptime(expiry_raw, "%Y-%m-%d %H:%M:%S %z")
    now = datetime.now(NZ)
    if now < expiry:
        print(f"NOT_YET expired={expiry.isoformat()} now={now.isoformat()}")
        return 0
    req = urllib.request.Request(
        f"https://api.render.com/v1/services/{service_id}/suspend",
        data=b"{}",
        method="POST",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            body = resp.read().decode()
    except urllib.error.HTTPError as e:
        print(f"SUSPEND_HTTP_{e.code}", file=sys.stderr)
        print(e.read().decode(), file=sys.stderr)
        return 1
    print("SUSPENDED", body[:200])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
