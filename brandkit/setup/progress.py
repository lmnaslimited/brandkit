# Copyright (c) 2026, BrandKit
# License: MIT

"""
Realtime helpers used during demo installation.

This module is intentionally kept separate so that
DemoDataFactory focuses only on the installation logic.
"""

import frappe


def update_progress(i_message: str, i_progress: int):
    """
    Publish realtime progress to the current user.

    Parameters
    ----------
    i_message:
        Message displayed on the client.

    i_progress:
        Progress percentage.
    """

    # Dictionary configuration storing realtime message payload states
    ld_message_payload = {
        "message": i_message,
        "progress": i_progress,
    }

    frappe.publish_realtime(
        event="brandkit_demo_progress",
        user=frappe.session.user,
        message=ld_message_payload,
    )