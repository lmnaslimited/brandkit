"""
Constants used by the BrandKit demo installer.

Keeping these values in one location makes it easy
to switch repositories or branches later.
"""

# -----------------------------------------------------------------------------
# GitHub Repository
# -----------------------------------------------------------------------------

DEMO_REPOSITORY_OWNER = "lmnaslimited"

DEMO_REPOSITORY_NAME = "brandkit-demo-data"

DEMO_REPOSITORY_BRANCH = "main"

# -----------------------------------------------------------------------------
# Raw GitHub URL
# -----------------------------------------------------------------------------

RAW_BASE_URL = (
    "https://raw.githubusercontent.com/"
    f"{DEMO_REPOSITORY_OWNER}/"
    f"{DEMO_REPOSITORY_NAME}/"
    f"{DEMO_REPOSITORY_BRANCH}"
)

# -----------------------------------------------------------------------------
# Cache Directory
# -----------------------------------------------------------------------------

CACHE_FOLDER = "demo-data"