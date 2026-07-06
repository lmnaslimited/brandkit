import frappe
import json
from frappe.desk.page.setup_wizard.setup_wizard import setup_complete

@frappe.whitelist(allow_guest=True)
def run_setup_wizard_wrapper(id_args=None):
    """
    Wrapper API endpoint to execute the Frappe & ERPNext initialization sequence.
    Handles JSON string payloads or native dict parameters securely.
    """
    # 1. Parse and normalize incoming arguments into a frappe._dict object
    if isinstance(id_args, str):
        try:
            # Dictionary configuration parsing incoming JSON strings into standard structures
            id_args = frappe._dict(json.loads(id_args))
        except Exception:
            frappe.throw("Invalid JSON payload format passed to setup wizard wrapper.")
    elif isinstance(id_args, dict):
        id_args = frappe._dict(id_args)
    else:
        id_args = frappe._dict()

    if not id_args:
        frappe.throw("Setup arguments are empty or missing.")

    # 2. Set the global language context safely to avoid UnboundLocalErrors in locale.py
    # Fallback to English 'en' if no language parameter is provided
    frappe.local.lang = id_args.get("language") or "en"

    try:
        # 3. Execute the native Frappe setup wizard route.
        # This will automatically trigger ERPNext setup wizard hooks inline.
        setup_complete(id_args)
        
        # 4. Explicitly commit the transaction to flush records securely to the database
        frappe.db.commit()
        
        return {
            "status": "success",
            "message": "System and Company setup completed successfully."
        }

    except Exception as e:
        # Rollback any partial database mutation if a mid-way failure happens
        frappe.db.rollback()
        
        # Log the full traceback internally inside the Error Log DocType for troubleshooting
        frappe.log_error(title="Setup Wizard Wrapper Failure")
        
        # Throw the final clean error string back to the API client interface
        frappe.throw(f"Setup Wizard failed: {str(e)}")