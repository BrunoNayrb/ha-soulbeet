#!/usr/bin/python3

import json
import os
import secrets
import sys
import urllib.request

OPTIONS = "/data/options.json"
SECRET_KEY_FILE = "/data/secret_key"
SERVER = "/app/server/server"


def log(message):
    print(f"[soulbeet] {message}", flush=True)


def load_options():
    try:
        with open(OPTIONS) as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def persist_secret_key():
    try:
        with open(SECRET_KEY_FILE) as f:
            key = f.read().strip()
        if key:
            return key
    except FileNotFoundError:
        pass

    key = secrets.token_hex(32)
    with open(SECRET_KEY_FILE, "w") as f:
        f.write(key)

    log("Generated persistent SECRET_KEY")
    return key


def log_slskd_hint():
    token = os.environ.get("SUPERVISOR_TOKEN")
    if not token:
        return

    try:
        req = urllib.request.Request(
            "http://supervisor/addons/self/info",
            headers={"Authorization": f"Bearer {token}"},
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            slug = json.load(response).get("data", {}).get("slug", "")

        if slug:
            prefix = slug.rsplit("_", 1)[0]
            host = f"{prefix}_slskd".replace("_", "-")
            log(f"Suggested slskd URL: http://{host}:5030")
    except Exception as exc:
        log(f"Could not determine slskd address: {exc}")


def main():
    opts = load_options()

    navidrome_url = (opts.get("navidrome_url") or "").strip()
    if navidrome_url:
        os.environ["NAVIDROME_URL"] = navidrome_url
    else:
        os.environ.pop("NAVIDROME_URL", None)

    download_dir = (
        opts.get("download_dir") or "/media/slskd/downloads"
    ).strip()
    os.environ["DOWNLOAD_PATH"] = download_dir
    os.environ["SECRET_KEY"] = persist_secret_key()

    os.makedirs("/data/beets-plugins", exist_ok=True)

    if opts.get("album_mode"):
        os.environ["BEETS_ALBUM_MODE"] = "true"

    tz = (opts.get("tz") or "").strip()
    if tz:
        os.environ["TZ"] = tz

    beets_config = "/config/beets_config.yaml"
    if os.path.isfile(beets_config):
        os.environ["BEETS_CONFIG"] = beets_config
        log(f"Using custom Beets config: {beets_config}")

    log(f"Downloads: {download_dir}")
    log_slskd_hint()

    os.execv(SERVER, [SERVER])


if __name__ == "__main__":
    main()
