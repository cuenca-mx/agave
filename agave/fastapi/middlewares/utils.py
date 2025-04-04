from fastapi import Request


def get_source_ip(request: Request) -> str:
    # Try to get the original client IP from the 'X-Forwarded-For' header.
    # The first IP in the list is typically the originating client's real IP.
    ip_address = (
        request.headers.get('X-Forwarded-For', '').split(',')[0].strip()
    )

    # If the header is missing or empty fallback to the immediate client's IP,
    # which may be the address of a proxy or load balancer.
    if not ip_address:
        ip_address = request.client.host if request.client else 'NA'

    return ip_address
