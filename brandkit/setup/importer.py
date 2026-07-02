"""
Generic importer for BrandKit demo data.

Responsibilities
----------------
- Read cached JSON files
- Insert documents into ERPNext
- Skip existing records
- Handle child tables automatically

This module does not download any files.
Downloaded resources are read from the local cache created
by DemoRepository.
"""

from __future__ import annotations

import json

import frappe

from brandkit.setup.progress import update_progress
from brandkit.setup.repository import DemoRepository


class DemoImporter:
    """
    Generic importer for cached demo JSON files.
    """

    def __init__(self, repository):

        self.repository = repository
        self.cache_root = repository.cache_root
        self.manifest = repository.get_manifest()

    # -------------------------------------------------------------------------

    def import_section(self, folder: str, files: list[dict]):
        """
        Import every file in a manifest section.
        """

        total = len(files)

        for index, file_info in enumerate(files, start=1):

            update_progress(
                f"Importing {file_info['doctype']}...",
                30 + int(index / max(total, 1) * 50),
            )

            self.import_file(
                folder,
                file_info["file"],
            )

    # -------------------------------------------------------------------------

    def import_file(self, folder: str, filename: str, submit=False):
        """
        Import all records from a cached JSON file.
        """

        file_path = self.cache_root / folder / filename

        if not file_path.exists():
            frappe.throw(f"Demo file not found:\n{file_path}")

        with open(file_path, encoding="utf-8") as file:
            records = json.load(file)

        for record in records:
            self.import_doc(record, submit)

        frappe.db.commit()

    # -------------------------------------------------------------------------

    def import_doc(self, record: dict, submit=False):
        """
        Import a single document.
        """

        if self.document_exists(record):
            return

        doc = frappe.get_doc(record)

        doc.insert(
            ignore_permissions=True,
        )
        if submit and doc.docstatus == 0:
            doc.submit()

    # -------------------------------------------------------------------------

    def document_exists(self, record: dict) -> bool:
        """
        Generic duplicate detection.
        """

        doctype = record["doctype"]

        if "name" in record:
            return bool(frappe.db.exists(doctype, record["name"]))

        meta = frappe.get_meta(doctype)

        if meta.title_field and record.get(meta.title_field):
            return bool(
                frappe.db.exists(
                    doctype,
                    {meta.title_field: record[meta.title_field]},
                )
            )

        if meta.autoname and meta.autoname.startswith("field:"):

            field = meta.autoname.split(":", 1)[1]

            if record.get(field):
                return bool(
                    frappe.db.exists(
                        doctype,
                        {field: record[field]},
                    )
                )

        return False


# =============================================================================
# Background Jobs
# =============================================================================


@frappe.whitelist()
def import_master_documents(industry: str):
    """
    Background job that imports all master documents.
    """

    repository = DemoRepository(industry)

    importer = DemoImporter(repository)

    manifest = repository.get_manifest()

    masters = manifest.get("masters", [])

    total = len(masters)

    for index, file_info in enumerate(masters, start=1):

        update_progress(
            f"Importing {file_info['doctype']}...",
            30 + int(index / max(total, 1) * 30),
        )

        importer.import_file(
            "masters",
            file_info["file"],
        )

    frappe.enqueue(
        method="brandkit.setup.importer.import_transaction_documents",
        queue="long",
        timeout=7200,
        industry=industry,
    )


@frappe.whitelist()
def import_transaction_documents(industry: str):
    """
    Background job that imports all transaction documents.
    """

    repository = DemoRepository(industry)

    importer = DemoImporter(repository)

    manifest = repository.get_manifest()

    transactions = manifest.get("transactions", [])

    total = len(transactions)

    for index, file_info in enumerate(transactions, start=1):

        update_progress(
            f"Importing {file_info['doctype']}...",
            60 + int(index / max(total, 1) * 35),
        )

        importer.import_file(
            folder="transactions",
            filename=file_info["file"],
            submit=file_info.get("submit", False),
        )

    finish_installation(industry)


# =============================================================================
# Installation Finalization
# =============================================================================


def finish_installation(industry: str):
    """
    Mark the demo installation as completed.
    """

    settings = frappe.get_single("BrandKit Settings")

    settings.demo_installed = 1
    settings.demo_industry = industry

    settings.save(ignore_permissions=True)

    frappe.db.commit()

    update_progress(
        "Demo setup completed.",
        100,
    )