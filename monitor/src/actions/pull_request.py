"""Create a GitHub PR that updates a constant in ursus_config.py."""

import base64
import logging
import os
import re
from datetime import date

import requests

log = logging.getLogger(__name__)

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
REPO = "all-About-Berlin/aab"
CONFIG_PATH = "frontend/ursus_config.py"
API_BASE = "https://api.github.com"


def github_request(method: str, path: str, **kwargs) -> requests.Response:
    url = f"{API_BASE}{path}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
    }
    response = requests.request(method, url, headers=headers, timeout=30, **kwargs)
    response.raise_for_status()
    return response


def create_pull_request(state_dir, title: str, url: str, summary: str, source_name: str, monitor_config=None, **kwargs):
    """Update a constant in ursus_config.py and open a PR."""
    if not monitor_config:
        raise ValueError("No monitor config provided for PR action")

    constant_name = monitor_config.get("constant")
    if not constant_name:
        raise ValueError(f"No 'constant' defined in monitor {source_name}")

    new_value = summary.strip()

    if not GITHUB_TOKEN:
        raise RuntimeError("GITHUB_TOKEN not set")

    # Get the default branch SHA
    repo_resp = github_request("GET", f"/repos/{REPO}")
    default_branch = repo_resp.json()["default_branch"]

    ref_resp = github_request("GET", f"/repos/{REPO}/git/ref/heads/{default_branch}")
    base_sha = ref_resp.json()["object"]["sha"]

    # Get the current file content
    file_resp = github_request("GET", f"/repos/{REPO}/contents/{CONFIG_PATH}", params={"ref": default_branch})
    file_data = file_resp.json()
    file_content = base64.b64decode(file_data["content"]).decode()
    file_sha = file_data["sha"]

    # Update the constant value
    pattern = rf'(ctx\["{constant_name}"\]\s*=\s*)(.+)'
    if not re.search(pattern, file_content):
        raise ValueError(f"Constant {constant_name} not found in {CONFIG_PATH}")

    updated_content = re.sub(pattern, rf"\g<1>{new_value}", file_content)
    if updated_content == file_content:
        log.info(f"No change needed for {constant_name}")
        return

    # Create branch
    slug = re.sub(r"[^a-z0-9]+", "-", source_name.lower()).strip("-")
    branch_name = f"monitor/update-{slug}-{date.today().isoformat()}"

    github_request(
        "POST",
        f"/repos/{REPO}/git/refs",
        json={
            "ref": f"refs/heads/{branch_name}",
            "sha": base_sha,
        },
    )

    # Update file on new branch
    github_request(
        "PUT",
        f"/repos/{REPO}/contents/{CONFIG_PATH}",
        json={
            "message": f"monitor: Update {constant_name}",
            "content": base64.b64encode(updated_content.encode()).decode(),
            "sha": file_sha,
            "branch": branch_name,
        },
    )

    # Create PR
    pr_resp = github_request(
        "POST",
        f"/repos/{REPO}/pulls",
        json={
            "title": f"Update {constant_name}",
            "body": f"Automated update from monitor `{source_name}`.\n\nSource: {url}\nNew value: `{new_value}`",
            "head": branch_name,
            "base": default_branch,
        },
    )
    log.info(f"Created PR: {pr_resp.json()['html_url']}")
