"""
Repository client responsible for downloading
and caching demo data from GitHub.

This class DOES NOT import ERPNext documents.

Its only responsibility is downloading files.
"""

from pathlib import Path
import json

import frappe
import requests

from brandkit.setup.constants import (
    L_cache_folder,
    L_raw_base_url,
)

from brandkit.setup.exceptions import (
    cl_demo_file_not_found_error,
    cl_manifest_not_found_error,
)

"""
Downloads and caches demo resources.
"""
class cl_demo_repository:

    def __init__(self, i_industry: str):

        self.l_industry = i_industry.lower()

        self.l_base_url = f"{L_raw_base_url}/{self.l_industry}"

        self.l_cache_root = Path(
            frappe.get_site_path(
                "private",
                "files",
                L_cache_folder,
                self.l_industry,
            )
        )

    """
    Return the industry's manifest.

    Downloads it if not already cached.
    """
    def get_manifest(self) -> dict:

        l_path = self.download("manifest.json")

        with open(l_path, encoding="utf-8") as file:
            return json.load(file)

    """
    Download a file if it doesn't already exist.
    """
    def download(self, i_relative_path: str) -> Path:

        # Local scalar instance representing targeted download track
        l_local_file = self.l_cache_root / i_relative_path

        if l_local_file.exists():
            return l_local_file

        # remote target URL address
        l_url = f"{self.l_base_url}/{i_relative_path}"

        # Dictionary-like request response object tracking remote status
        ld_response = requests.get(l_url, timeout=60)

        if ld_response.status_code == 404:

            if i_relative_path == "manifest.json":
                raise cl_manifest_not_found_error(l_url)

            raise cl_demo_file_not_found_error(l_url)

        ld_response.raise_for_status()

        l_local_file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        l_local_file.write_bytes(ld_response.content)

        return l_local_file

    """
    Download every JSON file declared in manifest.
    """
    def download_from_manifest(self):
        # Dictionary container capturing manifest structures
        ld_manifest = self.get_manifest()

        # Dictionary looping through metadata elements in masters key
        for ld_file_info in ld_manifest.get("masters", []):

            self.download(
                f"masters/{ld_file_info['file']}"
            )

        # Dictionary looping through transactions elements
        for ld_file_info in ld_manifest.get("transactions", []):

            self.download(
                f"transactions/{ld_file_info['file']}"
            )

    def cached_manifest_path(self) -> Path:

        return self.l_cache_root / "manifest.json"

    def clear_cache(self):

        if self.l_cache_root.exists():

            import shutil

            shutil.rmtree(self.l_cache_root)

    """
    Return all industries available in the demo repository.
    """
    @staticmethod
    def get_available_industries():
        # Local scalar tracking the remote global industry list endpoint
        l_url = f"{L_raw_base_url}/industries.json"
        # Dictionary-like response tracking server status output data
        ld_response = requests.get(l_url, timeout=30)
        ld_response.raise_for_status()

        return ld_response.json()