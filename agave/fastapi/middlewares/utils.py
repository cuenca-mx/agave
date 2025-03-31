from fastapi import Request


def get_source_ip(request: Request) -> str:
    ip_address = (
        request.headers.get('X-Forwarded-For', '').split(',')[0].strip()
    )

    if not ip_address:
        ip_address = request.client.host if request.client else 'NA'

    return ip_address
