# Copyright (c) 2026, BrandKit
# License: MIT

"""
Demo data installation framework.

Phase 1 responsibilities

- initialise installer
- check installation state
- mark installation complete

No importing happens here yet.
"""

import frappe

from brandkit.setup.progress import update_progress
from brandkit.setup.repository import DemoRepository


import frappe

from brandkit.setup.progress import update_progress
from brandkit.setup.repository import DemoRepository
from brandkit.setup.importer import DemoImporter


class DemoDataFactory:
    """
    Coordinates the demo data installation process.

    Responsibilities:
        - Initialize the installer
        - Download and cache demo resources
        - (Future Phase) Import demo data
        - Mark the installation as complete
    """

    @staticmethod
    def run(industry: str, show_progress: bool = True):
        """
        Entry point for installing demo data.

        Parameters
        ----------
        industry : str
            Industry selected by the user.
        """

        factory = DemoDataFactory()

        # Initialize the installer
        factory.initialize(
            industry=industry,
            show_progress=show_progress,
        )

        # Skip installation if demo data already exists
        if factory.demo_exists():
            update_progress("Demo data is already installed.", 100)
            return

        # ------------------------------------------------------------------
        # Phase 2
        # Download and cache all demo resources from the repository
        # ------------------------------------------------------------------
        if factory.show_progress:
            update_progress("Downloading demo resources...", 20)

        factory.repository.download_from_manifest()

        frappe.enqueue(
            method="brandkit.setup.importer.import_master_documents",
            queue="long",
            timeout=7200,
            industry=factory.industry,
            show_progress=factory.show_progress,
        )

    def initialize(self, industry: str, show_progress: bool = True):
        """
        Initialize the installer context.

        Parameters
        ----------
        industry : str
            Selected industry.
        """

        self.show_progress = show_progress
        # Store selected industry for later use
        self.industry = industry.lower()

        # Create repository client
        self.repository = DemoRepository(self.industry)

        # Download/load manifest
        self.manifest = self.repository.get_manifest()
        self.importer = DemoImporter(
            self.repository
        )

    def demo_exists(self) -> bool:
        """
        Check whether demo data has already been installed.
        """

        return bool(
            frappe.db.get_single_value(
                "BrandKit Settings",
                "demo_installed",
            )
        )