# Copyright (c) 2026, BrandKit
# License: MIT

"""
Realtime helpers used during demo installation.

This module is intentionally kept separate so that
DemoDataFactory focuses only on the installation logic.
"""

import frappe


def update_progress(message: str, progress: int):
    """
    Publish realtime progress to the current user.

    Parameters
    ----------
    message:
        Message displayed on the client.

    progress:
        Progress percentage.
    """

    frappe.publish_realtime(
        event="brandkit_demo_progress",
        user=frappe.session.user,
        message={
            "message": message,
            "progress": progress,
        },
    )