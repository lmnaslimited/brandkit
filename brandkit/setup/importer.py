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

    # -------------------------------------------------------------------------
    # Composite uniqueness rules
    # -------------------------------------------------------------------------

    COMPOSITE_UNIQUE_FIELDS = {
        "Warehouse": (
            "warehouse_name",
            "company",
        ),
        "Item Price": (
            "item_code",
            "price_list",
        ),
    }
    def document_exists(self, record: dict) -> bool:
        """
        Determine whether a document already exists.

        Duplicate detection is performed in the following order:

            1. Composite unique fields (custom rules)
            2. Explicit document name
            3. Title field
            4. Autoname field
        """

        doctype = record["doctype"]

        # ------------------------------------------------------------------
        # Composite uniqueness rules
        # ------------------------------------------------------------------

        if doctype in self.COMPOSITE_UNIQUE_FIELDS:

            filters = {}

            for field in self.COMPOSITE_UNIQUE_FIELDS[doctype]:
                value = record.get(field)

                if value is None:
                    return False

                filters[field] = value

            return bool(
                frappe.db.exists(
                    doctype,
                    filters,
                )
            )

        # ------------------------------------------------------------------
        # Explicit document name
        # ------------------------------------------------------------------

        if record.get("name"):
            return bool(
                frappe.db.exists(
                    doctype,
                    record["name"],
                )
            )

        # ------------------------------------------------------------------
        # Title field
        # ------------------------------------------------------------------

        meta = frappe.get_meta(doctype)

        if meta.title_field:

            value = record.get(meta.title_field)

            if value:
                return bool(
                    frappe.db.exists(
                        doctype,
                        {
                            meta.title_field: value,
                        },
                    )
                )

        # ------------------------------------------------------------------
        # Autoname: field:<fieldname>
        # ------------------------------------------------------------------

        if (
            meta.autoname
            and meta.autoname.startswith("field:")
        ):

            fieldname = meta.autoname.split(":", 1)[1]

            value = record.get(fieldname)

            if value:
                return bool(
                    frappe.db.exists(
                        doctype,
                        {
                            fieldname: value,
                        },
                    )
                )

        return False


# =============================================================================
# Background Jobs
# =============================================================================


@frappe.whitelist()
def import_master_documents(industry: str, show_progress: bool = True):
    try:
        repository = DemoRepository(industry)
        importer = DemoImporter(repository)
        manifest = repository.get_manifest()

        masters = manifest.get("masters", [])
        total = len(masters)

        for index, file_info in enumerate(masters, start=1):
            if show_progress:
                update_progress(
                    f"Importing {file_info['doctype']}...",
                    30 + int(index / max(total, 1) * 30),
                )

            importer.import_file(
                folder="masters",
                filename=file_info["file"],
                submit=file_info.get("submit", False),
            )

        frappe.enqueue(
            method="brandkit.setup.importer.import_transaction_documents",
            queue="long",
            timeout=7200,
            industry=industry,
            show_progress=show_progress,
        )

    except Exception as e:
        frappe.log_error(
            frappe.get_traceback(),
            "BrandKit Demo Import"
        )

        if show_progress:
            update_progress(
                f"Installation failed.<br>{frappe.utils.escape_html(str(e))}",
                -1,
            )

        raise

@frappe.whitelist()
def import_transaction_documents(industry: str, show_progress: bool = True):
    """
    Background job that imports all transaction documents.
    """
    try:

        repository = DemoRepository(industry)

        importer = DemoImporter(repository)

        manifest = repository.get_manifest()

        transactions = manifest.get("transactions", [])

        total = len(transactions)

        for index, file_info in enumerate(transactions, start=1):

            if show_progress:
                update_progress(
                    f"Importing {file_info['doctype']}...",
                    60 + int(index / max(total, 1) * 35),
                )

            importer.import_file(
                folder="transactions",
                filename=file_info["file"],
                submit=file_info.get("submit", False),
            )

        finish_installation(industry, show_progress)
    except Exception as e:
        frappe.log_error(
            frappe.get_traceback(),
            "BrandKit Demo Import"
        )

        if show_progress:
            update_progress(
                f"Installation failed.<br>{frappe.utils.escape_html(str(e))}",
                -1,
            )

        raise


# =============================================================================
# Installation Finalization
# =============================================================================


def finish_installation(industry: str, show_progress: bool = True):
    """
    Mark the demo installation as completed.
    """

    settings = frappe.get_single("BrandKit Settings")

    settings.demo_installed = 1
    settings.demo_industry = industry

    settings.save(ignore_permissions=True)

    frappe.db.commit()

    if show_progress:
        update_progress(
            "Demo setup completed.",
            100,
        )