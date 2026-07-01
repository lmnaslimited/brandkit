"""
Custom exceptions used by the demo installer.
"""


class DemoRepositoryError(Exception):
    """Raised when the demo repository cannot be accessed."""


class ManifestNotFoundError(DemoRepositoryError):
    """Raised when manifest.json cannot be downloaded."""


class DemoFileNotFoundError(DemoRepositoryError):
    """Raised when a JSON resource cannot be downloaded."""