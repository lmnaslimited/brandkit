# Copyright (c) 2026, BrandKit
# License: MIT

"""
Public APIs used by the BrandKit demo setup frontend.

This module exposes the APIs required by the Desk banner.

Responsibilities
----------------
- Return banner state
- Start demo installation
"""

from __future__ import annotations
from frappe import _
import frappe

from brandkit.setup.demo import cl_demo_data_factory
from brandkit.setup.repository import cl_demo_repository


# -------------------------------------------------------------------------
# Banner State
# -------------------------------------------------------------------------


@frappe.whitelist()
def get_demo_banner_state():
    """
    Returns whether the demo banner should be displayed.
    """

    # Fetching application configurations as a dictionary object
    ld_settings = frappe.get_single("BrandKit Settings")

    return {
        "show_banner": (
            "System Manager" in frappe.get_roles()
            and not ld_settings.demo_installed
        ),
        "installed": ld_settings.demo_installed,
        "industry": ld_settings.demo_industry,
        "industries": cl_demo_repository.get_available_industries(),
    }

# Setup Demo Data
@frappe.whitelist()
def setup_demo_data(i_industry: str, i_show_progress: bool = True):
    """
    Start the demo installation.

    Parameters
    ----------
    i_industry:
        Industry selected by the user.

    i_show_progress:
        Whether realtime progress events should
        be published to the client.
    """

    if not i_industry:
        frappe.throw(_("Please select an industry."))

    # Initialize local variable from parameter for modification
    l_show_progress = i_show_progress

    # frappe.call() sends everything as strings.
    if isinstance(l_show_progress, str):
        l_show_progress = l_show_progress.lower() in (
            "1",
            "true",
            "yes",
        )

    cl_demo_data_factory.run(
        i_industry=i_industry,
        i_show_progress=l_show_progress,
    )