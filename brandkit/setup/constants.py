"""
Constants used by the BrandKit demo installer.

Keeping these values in one location makes it easy
to switch repositories or branches later.
"""

# -----------------------------------------------------------------------------
# GitHub Repository
# -----------------------------------------------------------------------------

# Fixed scalar constant defining the GitHub repository owner name
L_demo_repository_owner = "lmnaslimited"

# Fixed scalar constant defining the target GitHub repository identifier
L_demo_repository_name = "brandkit-demo-data"

# Fixed scalar constant pointing to the development or production branch resource path
L_demo_repository_branch = "main"

# -----------------------------------------------------------------------------
# Raw GitHub URL
# -----------------------------------------------------------------------------

# Fixed scalar base path string dynamically constructed for remote requests
L_raw_base_url = (
    "https://raw.githubusercontent.com/"
    f"{L_demo_repository_owner}/"
    f"{L_demo_repository_name}/"
    f"{L_demo_repository_branch}"
)

# -----------------------------------------------------------------------------
# Cache Directory
# -----------------------------------------------------------------------------

# Fixed scalar string defining the local caching directory destination name
L_cache_folder = "demo-data"