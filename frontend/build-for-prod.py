#!/usr/bin/env python
# 1. Build the static site in a staging directory
# 2. Rsync the finished static site to the final dir
# 3. Purge the cloudflare cache

from pathlib import Path
from subprocess import run, STDOUT
from urllib import request
import json
import logging
import os
import sys

logger = logging.getLogger(__name__)


def purge_cloudflare_cache(cloudflare_zone: str, cloudflare_api_key: str):
    logger.info("Purging Cloudflare cache")
    assert cloudflare_zone and cloudflare_api_key
    headers = {
        "Authorization": f"Bearer {cloudflare_api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    data = json.dumps({"purge_everything": True}).encode("utf8")
    req = request.Request(
        f"https://api.cloudflare.com/client/v4/zones/{cloudflare_zone}/purge_cache",
        data=data,
        headers=headers,
    )
    return request.urlopen(req)


def build_site(site_path: Path, tmp_output_path: Path, output_path: Path):
    """
    Build the website in a temporary location. If the build is successful, copy the files to the final location.
    """
    logger.info(f"Copying {output_path} to {tmp_output_path}")
    run(
        ["rsync", "-a", "--delete", str(output_path) + "/", tmp_output_path],
        check=True,
        stdout=sys.stdout,
        stderr=STDOUT,
    )

    run(
        ["ursus", "-c", site_path / "ursus_config.py"],
        check=True,
        stdout=sys.stdout,
        stderr=STDOUT,
    )

    logger.info(f"Copying {tmp_output_path} to {output_path}")
    run(
        ["rsync", "-a", "--delete", "--stats", str(tmp_output_path) + "/", output_path],
        check=True,
        stdout=sys.stdout,
        stderr=STDOUT,
    )


if __name__ == "__main__":
    logging.basicConfig(
        datefmt="%Y-%m-%d %H:%M:%S",
        format="%(asctime)s %(levelname)s [%(name)s:%(lineno)d] %(message)s",
        level=logging.INFO,
    )

    cloudflare_zone = os.environ["CLOUDFLARE_ZONE"]
    cloudflare_api_key = os.environ["CLOUDFLARE_API_KEY"]
    services_cloudflare_zone = os.environ["SERVICES_CLOUDFLARE_ZONE"]
    services_cloudflare_api_key = os.environ["SERVICES_CLOUDFLARE_API_KEY"]

    ursus_path = Path("/usr/lib/ursus")
    site_path = Path("/var/project/frontend")
    tmp_output_path = Path("/var/output")
    final_output_path = Path("/var/live-output")

    try:
        build_site(site_path, tmp_output_path, final_output_path)
        purge_cloudflare_cache(cloudflare_zone, cloudflare_api_key)
        purge_cloudflare_cache(services_cloudflare_zone, services_cloudflare_api_key)
    except:  # noqa
        logger.exception("Failed to build site")
