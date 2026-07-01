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
    CACHE_FOLDER,
    RAW_BASE_URL,
)

from brandkit.setup.exceptions import (
    DemoFileNotFoundError,
    ManifestNotFoundError,
)


class DemoRepository:
    """
    Downloads and caches demo resources.
    """

    def __init__(self, industry: str):

        self.industry = industry.lower()

        self.base_url = f"{RAW_BASE_URL}/{self.industry}"

        self.cache_root = Path(
            frappe.get_site_path(
                "private",
                "files",
                CACHE_FOLDER,
                self.industry,
            )
        )

    # -------------------------------------------------------------------------

    def get_manifest(self) -> dict:
        """
        Return the industry's manifest.

        Downloads it if not already cached.
        """

        path = self.download("manifest.json")

        with open(path, encoding="utf-8") as file:
            return json.load(file)

    # -------------------------------------------------------------------------

    def download(self, relative_path: str) -> Path:
        """
        Download a file if it doesn't already exist.
        """

        local_file = self.cache_root / relative_path

        if local_file.exists():
            return local_file

        url = f"{self.base_url}/{relative_path}"

        response = requests.get(url, timeout=60)

        if response.status_code == 404:

            if relative_path == "manifest.json":
                raise ManifestNotFoundError(url)

            raise DemoFileNotFoundError(url)

        response.raise_for_status()

        local_file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        local_file.write_bytes(response.content)

        return local_file

    # -------------------------------------------------------------------------

    def download_from_manifest(self):
        """
        Download every JSON file declared in manifest.
        """

        manifest = self.get_manifest()

        for file_info in manifest.get("masters", []):

            self.download(
                f"masters/{file_info['file']}"
            )

        for file_info in manifest.get("transactions", []):

            self.download(
                f"transactions/{file_info['file']}"
            )

    # -------------------------------------------------------------------------

    def cached_manifest_path(self) -> Path:

        return self.cache_root / "manifest.json"

    # -------------------------------------------------------------------------

    def clear_cache(self):

        if self.cache_root.exists():

            import shutil

            shutil.rmtree(self.cache_root)

    @staticmethod
    def get_available_industries():
        """
        Return all industries available in the demo repository.
        """

        url = f"{RAW_BASE_URL}/industries.json"

        response = requests.get(url, timeout=30)
        response.raise_for_status()

        return response.json()