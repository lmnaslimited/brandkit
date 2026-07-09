import frappe
from urllib.parse import urlparse

@frappe.whitelist(allow_guest=True)
def get_google_auth_link(i_redirect_to_nextjs: str = None):
    """
    Exposes Frappe's internal OAuth authorization URL generation for website users.

    Frappe's `get_oauth2_authorize_url` builds the required OAuth `code` and
    `state` flow but is not whitelisted. This endpoint provides guest access to
    that functionality while validating the requested redirect URL against the
    configured trusted origins to prevent open redirect attacks.
    """
    
    # Use a safe default destination to prevent untrusted redirect targets.
    l_safe_redirect_url = "/desk"

    if i_redirect_to_nextjs:
        ld_parsed_url = urlparse(i_redirect_to_nextjs)

        # Restrict redirect destinations to configured frontend origins to prevent open redirect attacks.
        la_configured_cors = frappe.conf.get("allow_cors") or []

        # Normalize configured origins so they can be compared consistently with the requested redirect URL.
        if isinstance(la_configured_cors, str):
            la_allowed_domains = [urlparse(la_configured_cors).netloc] if "http" in la_configured_cors else [la_configured_cors]
        else:
            la_allowed_domains = [urlparse(url).netloc if "http" in url else url for url in la_configured_cors]

        # Accept the redirect only when it belongs to a trusted origin.
        if ld_parsed_url.netloc in la_allowed_domains:
            l_safe_redirect_url = i_redirect_to_nextjs

    # Generate the OAuth initiation URL with our safe destination path
    from frappe.utils.oauth import get_oauth2_authorize_url
    auth_url = get_oauth2_authorize_url("google", redirect_to=l_safe_redirect_url)

    return {"auth_url": auth_url}