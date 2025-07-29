import ipaddress


def validate_ipv4_address(address: str) -> bool:
    try:
        ipaddress.IPv4Address(address)
        return True
    except ipaddress.AddressValueError:
        return False


def validate_multicast_ipv4_address(address: str) -> bool:
    try:
        parsed_ip = ipaddress.IPv4Address(address)
        return parsed_ip.is_multicast
    except ValueError:
        return False


def validate_private_ipv4_address(address: str) -> bool:
    try:
        parsed_ip = ipaddress.IPv4Address(address)
        return parsed_ip.is_private
    except ValueError:
        return False


def validate_global_ipv4_address(address: str) -> bool:
    try:
        parsed_ip = ipaddress.IPv4Address(address)
        return parsed_ip.is_global
    except ValueError:
        return False


def validate_loopback_ipv4_address(address: str) -> bool:
    try:
        parsed_ip = ipaddress.IPv4Address(address)
        return parsed_ip.is_loopback
    except ValueError:
        return False


def validate_ipv4_network(network: str) -> bool:
    try:
        ipaddress.IPv4Network(network)
        return True
    except (ipaddress.NetmaskValueError, ipaddress.AddressValueError):
        return False


def validate_network_contains_ipv4_address(network: str, address: str) -> bool:
    try:
        parsed_network = ipaddress.IPv4Network(network)
        parsed_ip = ipaddress.IPv4Address(address)
        return parsed_ip in parsed_network
    except ValueError:
        return False
