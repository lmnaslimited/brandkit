from pathlib import Path

import frappe
from frappe.utils.file_manager import save_file


def upload_file(filename):
    app_path = frappe.get_app_path("brandkit")
    file_path = Path(app_path) / "public" / "images" / filename

    if not file_path.exists():
        frappe.logger().warning(f"{filename} not found")
        return None

    file_doc = save_file(
        filename,                   # fname
        file_path.read_bytes(),     # content
        None,                       # dt
        None,                       # dn
        is_private=0,
    )

    return file_doc.file_url


def after_install():
    set_website_settings()
    set_navbar_settings()


def set_website_settings():
    favicon = upload_file("lensfavicon.ico")
    banner = upload_file("lensicon.png")
    splash = upload_file("lensicon.png")

    settings = frappe.get_single("Website Settings")

    settings.app_name = "LENS"
    settings.disable_signup = 0
    settings.footer_powered = "LENS Powered by Frappe"
    settings.banner_image = banner
    settings.splash_image = splash
    settings.favicon = favicon

    settings.save(ignore_permissions=True)

    frappe.db.commit()


def set_navbar_settings():
    app_logo = upload_file("lensicon.png")

    navbar = frappe.get_single("Navbar Settings")

    navbar.app_logo = app_logo

    navbar.save(ignore_permissions=True)

    frappe.db.commit()