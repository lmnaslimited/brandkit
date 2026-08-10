# Copyright (c) 2026, BrandKit
# License: MIT

"""
Realtime helpers used during demo installation.

This module is intentionally kept separate so that
DemoDataFactory focuses only on the installation logic.

Progress is delivered two ways:

1. frappe.publish_realtime() -- instant push over the websocket,
   when the client's socket connection happens to be ready.

2. frappe.cache() -- a durable snapshot of the latest progress,
   read by a polling endpoint (see brandkit.api.demo.get_demo_progress).

The websocket push is fast but best-effort: on a slow network, a
proxy that doesn't forward websocket upgrades correctly, or simply a
fast install, the client's socket may not finish connecting before
the job is already done, and events published in the meantime are
silently lost. The cache snapshot exists so the frontend has a
reliable fallback that doesn't depend on socket timing at all.
"""

import frappe

CACHE_KEY_PREFIX = "brandkit_demo_progress"

# Keep the cached snapshot around for 10 minutes -- long enough to
# cover a slow install plus some buffer, short enough not to leak
# stale state across unrelated installs.
CACHE_EXPIRY_SECONDS = 600


def _cache_key(i_user: str) -> str:
    return f"{CACHE_KEY_PREFIX}:{i_user}"


def update_progress(i_message: str, i_progress: int, i_user: str = None):
    """
    Publish realtime progress to the current user, and store a
    durable snapshot in cache for polling clients.

    Parameters
    ----------
    i_message:
        Message displayed on the client.

    i_progress:
        Progress percentage.

    i_user:
        User to target. Defaults to frappe.session.user, which is
        correctly set both in the foreground request and inside
        background jobs enqueued from it.
    """

    l_user = i_user or frappe.session.user

    # Dictionary configuration storing realtime message payload states
    ld_message_payload = {
        "message": i_message,
        "progress": i_progress,
    }

    # Durable snapshot -- source of truth for the polling fallback.
    frappe.cache().set_value(
        _cache_key(l_user),
        ld_message_payload,
        expires_in_sec=CACHE_EXPIRY_SECONDS,
    )

    # Best-effort instant push over the websocket.
    frappe.publish_realtime(
        event="brandkit_demo_progress",
        user=l_user,
        message=ld_message_payload,
    )


def get_cached_progress(i_user: str = None) -> dict:
    """
    Return the latest known progress snapshot for a user.

    Used by the polling endpoint. Returns a "nothing started yet"
    payload if no snapshot exists (e.g. before installation begins,
    or after it has already been cleared).
    """

    l_user = i_user or frappe.session.user

    ld_snapshot = frappe.cache().get_value(_cache_key(l_user))

    return ld_snapshot or {"message": "", "progress": 0}


def clear_progress(i_user: str = None):
    """
    Remove the cached snapshot. Called once installation finishes
    (success or failure) so stale progress doesn't linger for the
    next install attempt.
    """

    l_user = i_user or frappe.session.user

    frappe.cache().delete_value(_cache_key(l_user))