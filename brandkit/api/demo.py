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

import frappe

from brandkit.setup.demo import DemoDataFactory
from brandkit.setup.repository import DemoRepository


# -------------------------------------------------------------------------
# Banner State
# -------------------------------------------------------------------------


@frappe.whitelist()
def get_demo_banner_state():
    """
    Returns whether the demo banner should be displayed.
    """

    settings = frappe.get_single("BrandKit Settings")

    return {
        "show_banner": (
            "System Manager" in frappe.get_roles()
            and not settings.demo_installed
        ),
        "installed": settings.demo_installed,
        "industry": settings.demo_industry,
        "industries": DemoRepository.get_available_industries(),
    }


# -------------------------------------------------------------------------
# Setup Demo Data
# -------------------------------------------------------------------------


@frappe.whitelist()
def setup_demo_data(industry: str):
    """
    Start the demo installation.

    Parameters
    ----------
    industry:
        Industry selected by the user.
    """

    if not industry:
        frappe.throw("Please select an industry.")

    DemoDataFactory.run(industry)