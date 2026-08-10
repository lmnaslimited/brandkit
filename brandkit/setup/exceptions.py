"""
Custom exceptions used by the demo installer.
"""


class cl_demo_repository_error(Exception):
    """Raised when the demo repository cannot be accessed."""


class cl_manifest_not_found_error(cl_demo_repository_error):
    """Raised when manifest.json cannot be downloaded."""


class cl_demo_file_not_found_error(cl_demo_repository_error):
    """Raised when a JSON resource cannot be downloaded."""