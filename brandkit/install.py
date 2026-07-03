from pathlib import Path
import frappe
from frappe.utils.file_manager import save_file


def upload_file(i_filename):
    """
    Locates a file within the app's public/images directory, reads its content,
    and uploads it to Frappe's file manager system as a public file.
    
    Returns:
        str: The public URL of the uploaded file, or None if the file doesn't exist.
    """
    # Fetch the absolute path of the 'brandkit' application
    l_app_path = frappe.get_app_path("brandkit")
    
    # Construct the full file system path to the target image
    l_file_path = Path(l_app_path) / "public" / "images" / i_filename

    # Check if the file physically exists on the disk before proceeding
    if not l_file_path.exists():
        # Log a warning to the Frappe logger if the file is missing and exit early
        frappe.logger().warning(f"{i_filename} not found")
        return None

    # Upload and register the file within Frappe's database using the file manager
    # `is_private=0` ensures the file is accessible publicly via a URL
    l_file_doc = save_file(
        i_filename,                   # fname: Name of the file
        l_file_path.read_bytes(),     # content: Raw binary data of the file
        None,                         # dt: Attached DocType (None for standalone)
        None,                         # dn: Attached DocName (None for standalone)
        is_private=0,
    )

    # Return the newly generated public web URL of the file
    return l_file_doc.file_url


def after_install():
    """
    Frappe hook function that executes automatically after the application is installed.
    It triggers the configuration setup for both Website and Navbar settings.
    """
    # Execute the setup for system website branding and configurations
    set_website_settings()
    
    # Execute the setup for top navigation bar branding
    set_navbar_settings()


def set_website_settings():
    """
    Uploads the necessary branding assets and updates Frappe's 
    'Website Settings' Single DocType with the new identity config.
    """
    # Upload the 'lensicon.png' for various UI components and store their public URLs
    l_favicon = upload_file("lensicon.png")
    l_banner = upload_file("lensicon.png")
    l_splash = upload_file("lensicon.png")
    l_app_logo = upload_file("lensicon.png")

    # Fetch the Single DocType instance for 'Website Settings' to modify global portal UI
    ld_settings = frappe.get_single("Website Settings")

    # Assign new value configurations to the Website Settings document fields
    ld_settings.app_name = "LENS"
    ld_settings.disable_signup = 0
    ld_settings.footer_powered = "LENS Powered by Frappe"
    ld_settings.app_logo = l_app_logo
    ld_settings.banner_image = l_banner
    ld_settings.splash_image = l_splash
    ld_settings.favicon = l_favicon

    # Save the document modifications to memory, bypassing system permission checks
    ld_settings.save(ignore_permissions=True)

    # Commit the transaction to the database so changes persist permanently
    frappe.db.commit()


def set_navbar_settings():
    """
    Uploads the navbar logo asset and updates Frappe's 
    'Navbar Settings' Single DocType configuration.
    """
    # Upload the 'lensicon.png' to use specifically as the Navigation Bar logo
    l_app_logo = upload_file("lensicon.png")

    # Fetch the Single DocType instance for 'Navbar Settings' to modify global header UI
    ld_navbar = frappe.get_single("Navbar Settings")

    # Assign the uploaded logo URL to the navbar application logo field
    ld_navbar.app_logo = l_app_logo

    # Save the document modifications to memory, bypassing system permission checks
    ld_navbar.save(ignore_permissions=True)

    # Commit the transaction to the database so changes persist permanently
    frappe.db.commit()