import frappe


def after_install():
    apply_branding()


def apply_branding():
    logo = "/assets/brandkit/images/lensicon.png"
    favicon = "/assets/brandkit/images/lensfavicon.ico"

    update_website_settings(logo, favicon)
    update_navbar_settings(logo)

    frappe.clear_cache()

def update_website_settings(logo, favicon):
    web_settings = frappe.get_single("Website Settings")

    web_settings.app_logo = logo
    web_settings.favicon = favicon
    web_settings.app_name = "LENS"
    web_settings.disable_signup = 0
    web_settings.banner_image = logo
    web_settings.splash_image = logo
    web_settings.favicon = favicon
    web_settings.footer_powered = "LENS Powered By Frappe"

    web_settings.save(ignore_permissions=True)

def update_navbar_settings(logo):
    if frappe.db.exists("DocType", "Navbar Settings"):
        navbar = frappe.get_single("Navbar Settings")

        navbar.app_logo = logo

        navbar.save(ignore_permissions=True)