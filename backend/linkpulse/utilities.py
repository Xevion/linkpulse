from typing import Optional
from fastapi import Request


def pluralize(count: int, word: Optional[str] = None) -> str:
    """
    Pluralize a word based on count. Returns 's' if count is not 1, '' (empty string) otherwise.
    """
    if word:
        return word + 's' if count != 1 else word
    return 's' if count != 1 else ''

def get_ip(request: Request) -> Optional[str]:
    """
    This function attempts to retrieve the client's IP address from the request headers.
    
    It first checks the 'X-Forwarded-For' header, which is commonly used in proxy setups.
    If the header is present, it returns the first IP address in the list.
    If the header is not present, it falls back to the client's direct connection IP address.
    If neither is available, it returns None.
    
    Args:
        request (Request): The request object containing headers and client information.
    
    Returns:
        Optional[str]: The client's IP address if available, otherwise None.
    """
    x_forwarded_for = request.headers.get('X-Forwarded-For')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    
    if request.client:
        return request.client.host
    
    return None

def hide_ip(ip: str, hidden_octets: Optional[int] = None) -> str:
    """
    Hide the last octet(s) of an IP address.

    Args:
        ip (str): The IP address to be masked. Only supports IPv4 (/32) and IPv6 (/64). Prefixes are not supported.
        hidden_octets (Optional[int]): The number of octets to hide. Defaults to 1 for IPv4 and 3 for IPv6.

    Returns:
        str: The IP address with the specified number of octets hidden.

    Examples:
        >>> hide_ip("192.168.1.1")
        '192.168.1.X'
        
        >>> hide_ip("192.168.1.1", 2)
        '192.168.X.X'
        
        >>> hide_ip("2001:0db8:85a3:0000:0000:8a2e:0370:7334")
        '2001:0db8:85a3:0000:0000:XXXX:XXXX:XXXX'
        
        >>> hide_ip("2001:0db8:85a3:0000:0000:8a2e:0370:7334", 4)
        '2001:0db8:85a3:0000:XXXX:XXXX:XXXX:XXXX'
    """
    ipv6 = ':' in ip

    # Make sure that IPv4 (dot) and IPv6 (colon) addresses are not mixed together somehow. Not a comprehensive check.
    if ipv6 == ('.' in ip):
        raise ValueError("Invalid IP address format. Must be either IPv4 or IPv6.")

    total_octets = 8 if ipv6 else 4
    separator = ':' if ipv6 else '.'
    replacement = 'XXXX' if ipv6 else 'X'
    if hidden_octets is None:
        hidden_octets = 3 if ipv6 else 1

    return separator.join(ip.split(separator, total_octets - hidden_octets)[:-1]) + (separator + replacement) * hidden_octets
