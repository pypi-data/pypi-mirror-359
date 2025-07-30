"""
URL utilities for different environments and regions.
"""


def get_base_url(region: str) -> str:
    """
    Get the base URL for the Five9 API based on the region.

    This function returns the appropriate Five9 API URL for the specified region.
    If the region is not recognized, it defaults to the US region.

    Args:
        region: The region code (e.g., "US", "UK", "EU")

    Returns:
        The base URL for the specified region
    """
    region_urls = {
        "UK": "https://api.prod.uk.five9.net",
        "EU": "https://api.prod.eu.five9.net",
        "US": "https://api.prod.us.five9.net",
        "IN": "https://api.prod.in.five9.net",
        "CA": "https://api.prod.ca.five9.net",
        "ALPHA": "https://api.alpha.us.five9.net"
    }

    # Default to US if region not found
    return region_urls.get(region.upper(), "https://api.prod.us.five9.net")