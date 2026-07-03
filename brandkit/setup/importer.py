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
by cl_demo_repository.
"""

from __future__ import annotations

import json

import frappe

from brandkit.setup.progress import update_progress
from brandkit.setup.repository import cl_demo_repository


class cl_demo_importer:
    """
    Generic importer for cached demo JSON files.
    """

    def __init__(self, id_repository):

        self.ld_repository = id_repository
        self.l_cache_root = id_repository.l_cache_root
        self.ld_manifest = id_repository.get_manifest()

    # -------------------------------------------------------------------------

    def import_file(self, i_folder: str, i_filename: str, i_submit=False):
        """
        Import all records from a cached JSON file.
        """

        # Scalar variable path construction mapping the target local file context
        l_file_path = self.l_cache_root / i_folder / i_filename

        if not l_file_path.exists():
            frappe.throw(f"Demo file not found:\n{l_file_path}")

        with open(l_file_path, encoding="utf-8") as file:
            # Array block loading parsed dictionary components from source file
            la_records = json.load(file)

        # Dictionary instance reference tracking an entry row during process loops
        for ld_record in la_records:
            self.import_doc(ld_record, i_submit)

        frappe.db.commit()

    # -------------------------------------------------------------------------

    def import_doc(self, id_record: dict, i_submit=False):
        """
        Import a single document.
        """

        if self.document_exists(id_record):
            return

        # Dictionary document reference fetching the mapped data object model
        ld_doc = frappe.get_doc(id_record)

        ld_doc.insert(
            ignore_permissions=True,
        )
        if i_submit and ld_doc.docstatus == 0:
            ld_doc.submit()

    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # Composite uniqueness rules
    # -------------------------------------------------------------------------

    Ld_composite_unique_fields = {
        "Warehouse": (
            "warehouse_name",
            "company",
        ),
        "Item Price": (
            "item_code",
            "price_list",
        ),
    }

    def document_exists(self, id_record: dict) -> bool:
        """
        Determine whether a document already exists.

        Duplicate detection is performed in the following order:

            1. Composite unique fields (custom rules)
            2. Explicit document name
            3. Title field
            4. Autoname field
        """

        # Scalar tracker representing targeted field metadata layout context
        l_doctype = id_record["doctype"]

        # ------------------------------------------------------------------
        # Composite uniqueness rules
        # ------------------------------------------------------------------

        if l_doctype in self.Ld_composite_unique_fields:

            # Dictionary query configuration holding dynamic key parameters
            ld_filters = {}

            for l_field in self.Ld_composite_unique_fields[l_doctype]:
                # Scalar value parsing metadata values inside configuration
                l_value = id_record.get(l_field)

                if l_value is None:
                    return False

                ld_filters[l_field] = l_value

            return bool(
                frappe.db.exists(
                    l_doctype,
                    ld_filters,
                )
            )

        # ------------------------------------------------------------------
        # Explicit document name
        # ------------------------------------------------------------------

        if id_record.get("name"):
            return bool(
                frappe.db.exists(
                    l_doctype,
                    id_record["name"],
                )
            )

        # ------------------------------------------------------------------
        # Title field
        # ------------------------------------------------------------------

        # Dictionary tracking target metadata blueprint schema structures
        ld_meta = frappe.get_meta(l_doctype)

        if ld_meta.title_field:

            # Scalar structural variable checking schema validation title rules
            l_value = id_record.get(ld_meta.title_field)

            if l_value:
                return bool(
                    frappe.db.exists(
                        l_doctype,
                        {
                            ld_meta.title_field: l_value,
                        },
                    )
                )

        # ------------------------------------------------------------------
        # Autoname: field:<fieldname>
        # ------------------------------------------------------------------

        if (
            ld_meta.autoname
            and ld_meta.autoname.startswith("field:")
        ):

            # Scalar identifier holding explicit naming string properties
            l_fieldname = ld_meta.autoname.split(":", 1)[1]

            # Scalar parameter variable recording custom naming content fields
            l_value = id_record.get(l_fieldname)

            if l_value:
                return bool(
                    frappe.db.exists(
                        l_doctype,
                        {
                            l_fieldname: l_value,
                        },
                    )
                )

        return False


# =============================================================================
# Background Jobs
# =============================================================================


@frappe.whitelist()
def import_master_documents(i_industry: str, i_show_progress: bool = True):
    try:
        # Dictionary-like class instance referencing the repository module engine
        ld_repository = cl_demo_repository(i_industry)
        
        # Dictionary-like class instance targeting the file import execution module
        ld_importer = cl_demo_importer(ld_repository)
        
        # Dictionary asset capturing complete dataset deployment schemas
        ld_manifest = ld_repository.get_manifest()

        # Array stack aggregating master definition target datasets
        la_masters = ld_manifest.get("masters", [])
        
        # Scalar number capturing total dataset processing lengths
        l_total = len(la_masters)

        # Dictionary iterator accessing nested execution element fields
        for l_index, ld_file_info in enumerate(la_masters, start=1):
            if i_show_progress:
                update_progress(
                    f"Importing {ld_file_info['doctype']}...",
                    30 + int(l_index / max(l_total, 1) * 30),
                )

            ld_importer.import_file(
                i_folder="masters",
                i_filename=ld_file_info["file"],
                i_submit=ld_file_info.get("submit", False),
            )

        frappe.enqueue(
            method="brandkit.setup.importer.import_transaction_documents",
            queue="long",
            timeout=7200,
            i_industry=i_industry,
            i_show_progress=i_show_progress,
        )

    except Exception as e:
        frappe.log_error(
            frappe.get_traceback(),
            "BrandKit Demo Import"
        )

        if i_show_progress:
            update_progress(
                f"Installation failed.<br>{frappe.utils.escape_html(str(e))}",
                -1,
            )

        raise


@frappe.whitelist()
def import_transaction_documents(i_industry: str, i_show_progress: bool = True):
    """
    Background job that imports all transaction documents.
    """
    try:
        # Dictionary-like class instance tracking workspace repository references
        ld_repository = cl_demo_repository(i_industry)

        # Dictionary-like class instance targeting data entry framework engine
        ld_importer = cl_demo_importer(ld_repository)

        # Dictionary metadata context loading deployment instruction files
        ld_manifest = ld_repository.get_manifest()

        # Array configuration lists keeping transaction tracking metrics
        la_transactions = ld_manifest.get("transactions", [])

        # Scalar counting maximum record quantities to loop over
        l_total = len(la_transactions)

        # Dictionary iteration elements processing system table inputs
        for l_index, ld_file_info in enumerate(la_transactions, start=1):

            if i_show_progress:
                update_progress(
                    f"Importing {ld_file_info['doctype']}...",
                    60 + int(l_index / max(l_total, 1) * 35),
                )

            ld_importer.import_file(
                i_folder="transactions",
                i_filename=ld_file_info["file"],
                i_submit=ld_file_info.get("submit", False),
            )

        finish_installation(i_industry, i_show_progress)
    except Exception as e:
        frappe.log_error(
            frappe.get_traceback(),
            "BrandKit Demo Import"
        )

        if i_show_progress:
            update_progress(
                f"Installation failed.<br>{frappe.utils.escape_html(str(e))}",
                -1,
            )

        raise


# =============================================================================
# Installation Finalization
# =============================================================================


def finish_installation(i_industry: str, i_show_progress: bool = True):
    """
    Mark the demo installation as completed.
    """

    # Dictionary application wrapper capturing configuration states
    ld_settings = frappe.get_single("BrandKit Settings")

    ld_settings.demo_installed = 1
    ld_settings.demo_industry = i_industry

    ld_settings.save(ignore_permissions=True)

    frappe.db.commit()

    if i_show_progress:
        update_progress(
            "Demo setup completed.",
            100,
        )