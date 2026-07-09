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
from frappe import _
import json
from frappe.utils import add_months
import frappe

from brandkit.setup.progress import update_progress
from brandkit.setup.repository import cl_demo_repository

from erpnext.buying.doctype.purchase_order.purchase_order import (
    make_purchase_receipt,
)

from erpnext.stock.doctype.purchase_receipt.purchase_receipt import (
    make_purchase_invoice,
)

from erpnext.selling.doctype.quotation.quotation import (
    make_sales_order,
)

from erpnext.selling.doctype.sales_order.sales_order import (
    make_delivery_note,
)

from erpnext.stock.doctype.delivery_note.delivery_note import (
    make_sales_invoice,
)

from erpnext.accounts.doctype.payment_entry.payment_entry import (
    get_payment_entry,
)

from erpnext.manufacturing.doctype.work_order.work_order import (
    make_stock_entry
)

class cl_demo_importer:
    """
    Generic importer for cached demo JSON files.
    """

    def __init__(self, id_repository):

        self.ld_repository = id_repository
        self.l_cache_root = id_repository.l_cache_root
        self.ld_manifest = id_repository.get_manifest()

    # -------------------------------------------------------------------------

    def import_file(
        self,
        i_folder: str,
        i_filename: str,
        i_submit: bool = False,
        i_create_from: str | None = None,
        i_purpose: str | None = None,
    ):
        """
        Import all records from a cached JSON file.
        """

        # Scalar variable path construction mapping the target local file context
        l_file_path = self.l_cache_root / i_folder / i_filename

        if not l_file_path.exists():
            frappe.throw(_("Demo file not found:\n{0}").format(l_file_path))

        with open(l_file_path, encoding="utf-8") as file:
            # Array block loading parsed dictionary components from source file
            la_records = json.load(file)

        # Dictionary instance reference tracking an entry row during process loops
        for ld_record in la_records:
            self.import_doc(
                id_record=ld_record,
                i_submit=i_submit,
                i_create_from=i_create_from,
                i_purpose=i_purpose,
            )

        frappe.db.commit()

    # -------------------------------------------------------------------------

    def import_doc(
        self,
        id_record: dict,
        i_submit: bool = False,
        i_create_from: str | None = None,
        i_purpose: str | None = None,
    ):
        """
        Import a single document.
        """
        
        if self.document_exists(id_record):
            return

        # Dictionary document reference fetching the mapped data object model
        ld_doc = self.make_document(
                    id_record=id_record,
                    i_create_from=i_create_from,
                    i_purpose=i_purpose,
                )

        ld_doc.insert(
            ignore_permissions=True,
        )
        if i_submit and ld_doc.docstatus == 0:
            ld_doc.submit()

    # -------------------------------------------------------------------------
    def make_document(
        self,
        id_record: dict,
        i_create_from: str | None = None,
        i_purpose: str | None = None,
    ):
        """
        Create a document.

        If i_create_from is specified, the document is created using
        ERPNext's mapping methods.

        Otherwise the JSON is imported directly.
        """

        if not i_create_from:
            return frappe.get_doc(id_record)

        if i_create_from == "Purchase Order":
            return self.make_purchase_receipt(id_record)

        if i_create_from == "Purchase Receipt":
            return self.make_purchase_invoice(id_record)

        if i_create_from == "Quotation":
            return self.make_sales_order(id_record)

        if i_create_from == "Sales Order":
            return self.make_delivery_note(id_record)

        if i_create_from == "Delivery Note":
            return self.make_sales_invoice(id_record)

        if i_create_from == "Work Order":
            return self.make_stock_entry(id_record)
        
        if i_create_from == "Sales Invoice":
            return self.make_payment_entry(id_record)

        if i_create_from == "Purchase Invoice":
            return self.make_payment_entry(id_record)

        frappe.throw(
            _("Unsupported create_from: {0}").format(i_create_from)
        )

    def update_document(
        self,
        id_doc,
        id_record,
    ):
        """
        Update a mapped document using values from the JSON record.
        """

        # Dictionary collection capturing field names that must be skipped
        ld_skip_fields = {
            "doctype",
            "items",
            "docstatus",
            "status",
            "idx",
            "owner",
            "creation",
            "modified",
            "modified_by",
        }

        # Looping through JSON attributes with scalar and dictionary properties
        for l_fieldname, l_value in id_record.items():

            if l_fieldname in ld_skip_fields:
                continue

            setattr(
                id_doc,
                l_fieldname,
                l_value,
            )

        return id_doc
    #-----------------------------------------------------------------------

    def update_child_rows(
        self,
        id_doc,
        id_record,
    ):
        """
        Update child table values from JSON while preserving
        ERPNext-generated row links.
        """

        if "items" not in id_record:
            return

        # Array container extracting the items row tracking block from input data
        la_json_items = id_record["items"]
        ld_doc_items = id_doc.get("items") if isinstance(id_doc, dict) else id_doc.items

        # Index loop using scalar and dictionary elements to process sequential entries
        for l_index, ld_json_row in enumerate(la_json_items):

            if l_index >= len(ld_doc_items):
                frappe.throw(
                    _("JSON contains more item rows than the mapped document.")
                )

            # Dictionary-like reference mapping to the corresponding core row model object
            ld_doc_row = ld_doc_items[l_index]

            # Nested iteration capturing sub-table properties across target rows
            for l_fieldname, l_value in ld_json_row.items():

                if l_fieldname in (
                    "doctype",
                    "name",
                ):
                    continue

                if isinstance(ld_doc_row, dict):
                    ld_doc_row[l_fieldname] = l_value
                else:
                    setattr(ld_doc_row, l_fieldname, l_value)
    #--------------------------------------------------------------------------

    def make_purchase_receipt(
        self,
        id_record,
    ):
        """
        Create a Purchase Receipt from a Purchase Order.
        """

        # Local scalar tracking the reference string ID of the purchase order
        l_purchase_order = (
            id_record.get("purchase_order")
            or id_record.get("against_purchase_order")
        )

        if not l_purchase_order:
            frappe.throw(
                _("Purchase Order is required in the Purchase Receipt JSON.")
            )

        # Dictionary mapping the newly instantiated document model object
        ld_doc = make_purchase_receipt(
            l_purchase_order
        )

        self.update_document(
            ld_doc,
            id_record,
        )

        self.update_child_rows(
            ld_doc,
            id_record,
        )

        return ld_doc
    
    #----------------------------------------------------------
    def make_purchase_invoice(
        self,
        id_record,
    ):
        """
        Create a Purchase Invoice from a Purchase Receipt.
        """

        # Local scalar tracking the reference string ID of the purchase receipt
        l_purchase_receipt = (
            id_record.get("purchase_receipt")
            or id_record.get("against_purchase_receipt")
        )

        if not l_purchase_receipt:
            frappe.throw(
                _("Purchase Receipt is required in the Purchase Invoice JSON.")
            )

        # Dictionary mapping the newly instantiated document model object
        ld_doc = make_purchase_invoice(
            l_purchase_receipt
        )

        self.update_document(
            ld_doc,
            id_record,
        )

        self.update_child_rows(
            ld_doc,
            id_record,
        )

        return ld_doc
    #--------------------------------------------------------------

    def make_sales_order(
        self,
        id_record,
    ):
        """
        Create a Sales Order from a Quotation.
        """

        # Local scalar tracking the reference string ID of the quotation source document
        l_quotation = (
            id_record.get("quotation")
            or id_record.get("against_quotation")
        )

        if not l_quotation:
            frappe.throw(
                _("Quotation is required in the Sales Order JSON.")
            )

        # Dictionary mapping the newly instantiated document model object
        ld_doc = make_sales_order(
            l_quotation
        )
        ld_doc.delivery_date = add_months(
            ld_doc.transaction_date,
            1
        )

        self.update_document(
            ld_doc,
            id_record,
        )

        self.update_child_rows(
            ld_doc,
            id_record,
        )

        return ld_doc
    #----------------------------------------------------

    def make_delivery_note(
        self,
        id_record,
    ):
        """
        Create a Delivery Note from a Sales Order.
        """

        # Local scalar tracking the reference string ID of the sales order source document
        l_sales_order = (
            id_record.get("sales_order")
            or id_record.get("against_sales_order")
        )

        if not l_sales_order:
            frappe.throw(
                _("Sales Order is required in the Delivery Note JSON.")
            )

        # Dictionary mapping the newly instantiated document model object
        ld_doc = make_delivery_note(
            l_sales_order
        )

        self.update_document(
            ld_doc,
            id_record,
        )

        self.update_child_rows(
            ld_doc,
            id_record,
        )

        return ld_doc
    #---------------------------------------------------------

    def make_sales_invoice(
        self,
        id_record,
    ):
        """
        Create a Sales Invoice from a Delivery Note.
        """

        # Local scalar tracking the reference string ID of the delivery note source document
        l_delivery_note = (
            id_record.get("delivery_note")
            or id_record.get("against_delivery_note")
        )

        if not l_delivery_note:
            frappe.throw(
                _("Delivery Note is required in the Sales Invoice JSON.")
            )

        # Dictionary mapping the newly instantiated document model object
        ld_doc = make_sales_invoice(
            l_delivery_note
        )

        self.update_document(
            ld_doc,
            id_record,
        )

        self.update_child_rows(
            ld_doc,
            id_record,
        )

        return ld_doc
    #------------------------------------------------------

    def make_payment_entry(
        self,
        id_record,
    ):
        """
        Create a Payment Entry from a Sales Invoice or Purchase Invoice.
        """

        if id_record.get("sales_invoice"):
            # Local scalar tracking the targeted reference doctype string identifier
            l_reference_doctype = "Sales Invoice"
            # Local scalar capturing the specific document transaction key value
            l_reference_name = id_record["sales_invoice"]

        elif id_record.get("purchase_invoice"):
            # Local scalar tracking the targeted reference doctype string identifier
            l_reference_doctype = "Purchase Invoice"
            # Local scalar capturing the specific document transaction key value
            l_reference_name = id_record["purchase_invoice"]

        else:
            frappe.throw(
                _("Either a Sales Invoice or Purchase Invoice must be specified.")
            )

        # Dictionary mapping the newly instantiated document model object
        ld_doc = get_payment_entry(
            l_reference_doctype,
            l_reference_name,
        )

        self.update_document(
            ld_doc,
            id_record,
        )

        return ld_doc
    #--------------------------------------------------

    def make_stock_entry(
        self,
        id_record,
    ):
        """
        Create a Stock Entry from a Work Order using ERPNext's native
        Work Order mapper.

        Supported purposes:
            - Material Transfer for Manufacture
            - Manufacture
            - Material Consumption for Manufacture
        """

        # Local scalar tracking the reference string ID of the work order source document
        l_work_order = id_record.get("work_order")

        if not l_work_order:
            frappe.throw(
                _("Work Order is required for Stock Entry.")
            )

        # Local scalar capturing the explicit configuration purpose string mapping type
        l_purpose = id_record.get("stock_entry_type")

        if l_purpose not in (
            "Material Transfer for Manufacture",
            "Manufacture",
            "Material Consumption for Manufacture",
        ):
            frappe.throw(
                _("Unsupported Stock Entry type: {0}").format(l_purpose)
            )

        # Dictionary mapping the newly instantiated stock entry document model object
        ld_doc = frappe.get_doc(
            make_stock_entry(
                work_order_id=l_work_order,
                purpose=l_purpose,
                qty=id_record.get("fg_completed_qty"),
            )
        )

        self.update_document(
            ld_doc,
            id_record,
        )

        self.update_child_rows(
            ld_doc,
            id_record,
        )

        return ld_doc

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

        if l_doctype == "Stock Entry":
            return False

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
                    _("Importing {0}...").format(ld_file_info["doctype"]),
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
                _("Installation failed.<br>{0}").format(
                    frappe.utils.escape_html(str(e))
                ),
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
                    _("Importing {0}...").format(ld_file_info["doctype"]),
                    60 + int(l_index / max(l_total, 1) * 35),
                )

            ld_importer.import_file(
                i_folder="transactions",
                i_filename=ld_file_info["file"],
                i_submit=ld_file_info.get("submit", False),
                i_create_from=ld_file_info.get("create_from"),
                i_purpose=ld_file_info.get("purpose"),
            )

        finish_installation(i_industry, i_show_progress)
    except Exception as e:
        frappe.log_error(
            frappe.get_traceback(),
            "BrandKit Demo Import"
        )

        if i_show_progress:
            update_progress(
                _("Installation failed.<br>{0}").format(
                    frappe.utils.escape_html(str(e))
                ),
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
            _("Demo setup completed."),
            100,
        )