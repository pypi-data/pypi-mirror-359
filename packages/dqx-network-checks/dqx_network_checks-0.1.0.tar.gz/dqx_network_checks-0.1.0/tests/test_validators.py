import pytest

from dqx_network_checks.validators import (
    validate_global_ipv4_address,
    validate_ipv4_address,
    validate_ipv4_network,
    validate_loopback_ipv4_address,
    validate_multicast_ipv4_address,
    validate_network_contains_ipv4_address,
    validate_private_ipv4_address,
)


@pytest.mark.parametrize(
    "address,is_valid",
    [
        ("192.168.1.1", True),
        ("10.0.0.1", True),
        ("172.16.0.1", True),
        ("127.0.0.1", True),
        ("0.0.0.0", True),
        ("255.255.255.255", True),
        ("8.8.8.8", True),
        ("1.1.1.1", True),
        ("256.1.2.3", False),  # Invalid octet > 255
        ("1.2.3.256", False),  # Invalid octet > 255
        ("192.168.1", False),  # Missing octet
        ("192.168.1.1.1", False),  # Too many octets
        ("192.168.001.1", False),  # Leading zeros
        ("192.168.1.", False),  # Trailing dot
        (".192.168.1.1", False),  # Leading dot
        ("192.168.1.1.", False),  # Trailing dot
        ("192.168..1", False),  # Empty octet
        ("192.168.1.1.1", False),  # Too many octets
        ("192.168.1.1/24", False),  # CIDR notation
        ("2001:db8::1", False),  # IPv6 address
        ("localhost", False),  # Hostname
        ("example.com", False),  # Domain name
        ("", False),  # Empty string
        ("not an ip", False),  # Invalid string
        ("192.168.1.1.1", False),  # Too many octets
    ],
)
def test_validate_ipv4_address(address, is_valid):
    assert validate_ipv4_address(address) is is_valid


@pytest.mark.parametrize(
    "address,is_valid",
    [
        ("224.0.0.1", True),
        ("8.8.8.8", False),
        ("invalid ip", False),  # not an IP address
    ],
)
def test_validate_multicast_ipv4_address(address, is_valid):
    assert validate_multicast_ipv4_address(address) is is_valid


@pytest.mark.parametrize(
    "address,is_valid",
    [
        ("10.0.0.1", True),
        ("172.16.0.1", True),
        ("127.0.0.1", True),
        ("192.168.1.1", True),
        ("8.8.8.8", False),
        ("invalid ip", False),  # not an IP address
    ],
)
def test_validate_private_ipv4_address(address, is_valid):
    assert validate_private_ipv4_address(address) is is_valid


@pytest.mark.parametrize(
    "address,is_valid",
    [
        ("8.8.8.8", True),
        ("1.1.1.1", True),
        ("127.0.0.1", False),
        ("192.168.1.1", False),
        ("invalid ip", False),  # not an IP address
    ],
)
def test_validate_global_ipv4_address(address, is_valid):
    assert validate_global_ipv4_address(address) is is_valid


@pytest.mark.parametrize(
    "address,is_valid",
    [
        ("127.0.0.1", True),
        ("8.8.8.8", False),
        ("invalid ip", False),  # not an IP address
    ],
)
def test_validate_loopback_ipv4_address(address, is_valid):
    assert validate_loopback_ipv4_address(address) is is_valid


@pytest.mark.parametrize(
    "network,is_valid",
    [
        ("10.0.0.0/8", True),
        ("10.0.0.0", True),  # prefix is assumed to be /32
        ("192.168.1.0/33", False),  # Invalid prefix
        ("10.0.0.0/-1", False),  # Invalid prefix
        ("not a network", False),  # Invalid string
        ("", False),  # Empty string
        ("2001:db8::/32", False),  # IPv6 network
    ],
)
def test_validate_ipv4_network(network, is_valid):
    assert validate_ipv4_network(network) is is_valid


@pytest.mark.parametrize(
    "network,address,is_valid",
    [
        ("10.0.0.0/8", "10.0.0.1", True),
        ("10.0.0.0/8", "8.8.8.8", False),
        ("invalid network", "10.0.0.1", False),  # not an IP network
        ("10.0.0.0/8", "invalid ip", False),  # not an IP address
    ],
)
def test_validate_network_contains_ipv4_address(network, address, is_valid):
    assert validate_network_contains_ipv4_address(network, address) is is_valid
