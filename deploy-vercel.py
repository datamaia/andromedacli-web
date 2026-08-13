#!/usr/bin/env python3
"""Deploy this static site to Vercel production via the REST API.

Not Git-connected, so this uploads files to /v2/files by sha1 then POSTs
/v13/deployments with target=production (as documented in README.md).

Reads VERCEL_PAT (required) and optional VERCEL_TEAM_ID / VERCEL_PROJECT from a
.env file. The token is never printed. Run from the site directory:

    ENV_FILE=/path/to/andromeda/.env python3 deploy-vercel.py
    # or, if .env is here:  python3 deploy-vercel.py
    # override project:      VERCEL_PROJECT=andromedacli-web python3 deploy-vercel.py
"""
import hashlib
import json
import os
import sys
import urllib.error
import urllib.request

API = "https://api.vercel.com"
ENV_FILE = os.environ.get("ENV_FILE", ".env")


def from_env(key):
    v = os.environ.get(key)
    if v:
        return v.strip()
    try:
        with open(ENV_FILE, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith(key + "="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    except FileNotFoundError:
        pass
    return None


TOKEN = from_env("VERCEL_PAT")
TEAM = from_env("VERCEL_TEAM_ID")  # optional
PROJECT = from_env("VERCEL_PROJECT")  # optional override
if not TOKEN:
    sys.exit(f"VERCEL_PAT not found (env or {ENV_FILE})")

QS = f"?teamId={TEAM}" if TEAM else ""


def api(method, path, data=None, raw=None, extra_headers=None):
    url = API + path
    headers = {"Authorization": f"Bearer {TOKEN}"}
    if extra_headers:
        headers.update(extra_headers)
    body = raw
    if data is not None:
        body = json.dumps(data).encode()
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        detail = e.read().decode()
        sys.exit(f"{method} {path} -> {e.code}\n{detail}")


# 1. Resolve the project (by explicit name, else by matching the andromedacli.com alias / name).
def resolve_project():
    if PROJECT:
        return PROJECT
    projects = api("GET", f"/v9/projects{QS}").get("projects", [])
    for p in projects:
        alias = " ".join(t.get("alias", [""])[0] if t.get("alias") else ""
                          for t in [p.get("targets", {}).get("production", {})])
        if "andromedacli.com" in (alias or "") or "andromeda" in p.get("name", ""):
            return p["name"]
    names = ", ".join(p.get("name", "?") for p in projects) or "(none)"
    sys.exit(f"Could not auto-detect the project. Set VERCEL_PROJECT to one of: {names}")


project = resolve_project()

# 2. Collect files (everything except .git/, this script, and *.tmp).
files = []
for root, dirs, names in os.walk("."):
    dirs[:] = [d for d in dirs if d != ".git"]
    for n in names:
        path = os.path.join(root, n)
        rel = os.path.relpath(path, ".").replace(os.sep, "/")
        if rel in ("deploy-vercel.py",) or rel.endswith(".tmp"):
            continue
        files.append(rel)
files.sort()

# 3. Upload each file to /v2/files (keyed by sha1) and build the manifest.
manifest = []
print(f"Deploying {len(files)} files to project '{project}'...")
for rel in files:
    with open(rel, "rb") as f:
        blob = f.read()
    sha = hashlib.sha1(blob).hexdigest()
    api("POST", f"/v2/files{QS}", raw=blob,
        extra_headers={"x-vercel-digest": sha, "Content-Length": str(len(blob))})
    manifest.append({"file": rel, "sha": sha, "size": len(blob)})
    print(f"  + {rel} ({len(blob)} B)")

# 4. Create the production deployment.
dep = api("POST", f"/v13/deployments{QS}{'&' if QS else '?'}forceNew=1", data={
    "name": project,
    "files": manifest,
    "target": "production",
    "projectSettings": {"framework": None},
})
url = dep.get("url") or dep.get("alias", ["?"])[0]
print(f"\n✅ Production deployment created: https://{url}")
print(f"   id={dep.get('id')} state={dep.get('readyState', dep.get('status', '?'))}")
print("   (Vercel finishes the build/alias asynchronously; check the dashboard or the URL above.)")
