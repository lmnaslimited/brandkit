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
from brandkit.setup.repository import cl_demo_repository
from brandkit.setup.importer import cl_demo_importer


class cl_demo_data_factory:
    """
    Coordinates the demo data installation process.

    Responsibilities:
        - Initialize the installer
        - Download and cache demo resources
        - (Future Phase) Import demo data
        - Mark the installation as complete
    """

    @staticmethod
    def run(i_industry: str, i_show_progress: bool = True):
        """
        Entry point for installing demo data.

        Parameters
        ----------
        i_industry : str
            Industry selected by the user.
        i_show_progress : bool
            Whether to broadcast progress metrics.
        """

        # Dictionary-like reference mapping the local factory engine instance
        ld_factory = cl_demo_data_factory()

        # Initialize the installer
        ld_factory.initialize(
            i_industry=i_industry,
            i_show_progress=i_show_progress,
        )

        # Skip installation if demo data already exists
        if ld_factory.demo_exists():
            update_progress("Demo data is already installed.", 100)
            return

        # Validate existing transaction data
        ld_factory.validate_transaction_data()
        
        # ------------------------------------------------------------------
        # Download and cache all demo resources from the repository
        # ------------------------------------------------------------------
        if ld_factory.l_show_progress:
            update_progress("Downloading demo resources...", 20)

        ld_factory.ld_repository.download_from_manifest()

        frappe.enqueue(
            method="brandkit.setup.importer.import_master_documents",
            queue="long",
            timeout=7200,
            i_industry=ld_factory.l_industry,
            i_show_progress=ld_factory.l_show_progress,
        )

    def initialize(self, i_industry: str, i_show_progress: bool = True):
        """
        Initialize the installer context.

        Parameters
        ----------
        i_industry : str
            Selected industry.
        i_show_progress : bool
            Whether progress alerts are shown.
        """

        self.l_show_progress = i_show_progress
        # Store selected industry for later use
        self.l_industry = i_industry.lower()

        # Create repository client instance mapping
        self.ld_repository = cl_demo_repository(self.l_industry)

        # Download/load manifest dictionary structure
        self.ld_manifest = self.ld_repository.get_manifest()
        self.ld_importer = cl_demo_importer(
            self.ld_repository
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

    def validate_transaction_data(self):
        """
        Prevent installing demo data into a company that already
        contains transactional records.

        Only the transaction doctypes declared in the selected
        industry's manifest are checked.
        """

        # Looping through configuration files using an iterative record dictionary
        for ld_transaction in self.ld_manifest.get("transactions", []):

            # Scalar property representing the targets core record configuration type
            l_doctype = ld_transaction.get("doctype")

            if not l_doctype:
                continue

            if frappe.db.count(l_doctype):

                frappe.throw(
                    (
                        f"Transaction data already exists for <b>{l_doctype}</b>.<br><br>"
                        "Please delete the existing transaction data first.<br><br>"
                        "Go to <b>Company → Click Manage → Delete Transactions</b> "
                        "and remove the transactions before installing "
                        "BrandKit Demo Data."
                    ),
                    title="Existing Transaction Data Found",
                )