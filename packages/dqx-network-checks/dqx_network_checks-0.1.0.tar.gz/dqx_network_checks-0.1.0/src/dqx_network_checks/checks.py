"""Data quality checks for IPv4 network validation.

This module provides a comprehensive set of data quality checks for IPv4 address
and network validation using PySpark DataFrames. It includes checks for various
IPv4 address types (loopback, multicast, private, global) and network operations.

The module integrates with the Databricks Data Quality Framework (DQX) to provide
row-level validation rules that can be applied to DataFrame columns.

Example:
    ```python
    from dqx_network_checks import is_ipv4_address, is_ipv4_private_address

    # Apply checks to a DataFrame
    df = spark.read.csv("network_data.csv")
    result = df.filter(is_ipv4_address("ip_column"))
    private_ips = df.filter(is_ipv4_private_address("ip_column"))
    ```

All validation functions return PySpark Column objects that can be used in
DataFrame operations for filtering, aggregating, or creating derived columns.
"""

import ipaddress

import pyspark.sql.functions as f
import pyspark.sql.types as t
from databricks.labs.dqx.check_funcs import make_condition
from databricks.labs.dqx.rule import register_rule
from pyspark.sql import Column

from dqx_network_checks.validators import (
    validate_global_ipv4_address,
    validate_ipv4_address,
    validate_ipv4_network,
    validate_loopback_ipv4_address,
    validate_multicast_ipv4_address,
    validate_network_contains_ipv4_address,
    validate_private_ipv4_address,
)


@register_rule("row")
def is_ipv4_address(column: str | Column) -> Column:
    """Validates that a column contains valid IPv4 address.

    This function creates a data quality check that validates whether each value
    in the specified column is a valid IPv4 address format (e.g., "192.168.1.1").

    Args:
        column: The (name of the) column to validate.

    Returns:
        A `Column` with a boolean value representing the validation condition.

    Note:
        This check validates the format only. It does not verify if the address
        is reachable or currently in use.
    """
    col = _as_column(column)
    error_message = f"Column `{col.name}` is not a valid IPv4 address"
    return make_condition(~is_ipv4_address_udf(col), error_message, "is_ipv4_address")


@register_rule("row")
def is_ipv4_loopback_address(column: str | Column) -> Column:
    """Validates that a column contains IPv4 loopback address.

    This function creates a data quality check that validates whether each value
    in the specified column is a valid IPv4 loopback address (127.0.0.0/8 range).

    Args:
        column: The (name of the) column to validate.

    Returns:
        A `Column` with a boolean value representing the validation condition.

    Note:
        Loopback addresses are in the range 127.0.0.0/8 and are used for
        internal communication within a host. See the [IANA documentation](https://www.iana.org/assignments/iana-ipv4-special-registry/iana-ipv4-special-registry.xhtml)
        for more information.
    """
    col = _as_column(column)
    error_message = f"Column `{col.name}` is not a valid IPv4 loopback address"
    return make_condition(
        ~is_ipv4_loopback_address_udf(col),
        error_message,
        "is_ipv4_loopback_address",
    )


@register_rule("row")
def is_ipv4_multicast_address(column: str | Column) -> Column:
    """Validates that a column contains IPv4 multicast address.

    This function creates a data quality check that validates whether each value
    in the specified column is a valid IPv4 multicast address (224.0.0.0/4 range).

    Args:
        column: The (name of the) column to validate.

    Returns:
        A `Column` with a boolean value representing the validation condition.

    Note:
        Multicast addresses are in the range 224.0.0.0/4 and are used for
        one-to-many communication. See the [IANA documentation](https://www.iana.org/assignments/iana-ipv4-special-registry/iana-ipv4-special-registry.xhtml)
        for more information.
    """
    col = _as_column(column)
    error_message = f"Column `{col.name}` is not a valid IPv4 multicast address"
    return make_condition(
        ~is_ipv4_multicast_address_udf(col),
        error_message,
        "is_ipv4_multicast_address",
    )


@register_rule("row")
def is_ipv4_private_address(column: str | Column) -> Column:
    """Validates that a column contains a IPv4 private address.

    This function creates a data quality check that validates whether each value
    in the specified column is a valid IPv4 private address. Private address
    ranges include:
    - 10.0.0.0/8
    - 172.16.0.0/12
    - 192.168.0.0/16

    Args:
        column: The (name of the) column to validate.

    Returns:
        A `Column` with a boolean value representing the validation condition.

    Note:
        Private addresses are reserved for use within private networks and are
        not routable on the public internet. See the [IANA documentation](https://www.iana.org/assignments/iana-ipv4-special-registry/iana-ipv4-special-registry.xhtml)
        for more information.
    """
    col = _as_column(column)
    error_message = f"Column `{col.name}` is not a valid IPv4 private address"
    return make_condition(
        ~is_ipv4_private_address_udf(col),
        error_message,
        "is_ipv4_private_address",
    )


@register_rule("row")
def is_ipv4_global_address(column: str | Column) -> Column:
    """Validates that a column contains a IPv4 global (public) address.

    This function creates a data quality check that validates whether each value
    in the specified column is a valid IPv4 global address. Global addresses
    are public IP addresses that are routable on the internet.

    Args:
        column: The (name of the) column to validate.

    Returns:
        A `Column` with a boolean value representing the validation condition.

    Note:
        Global addresses exclude private, loopback, multicast, and other
        reserved address ranges. See the [IANA documentation](https://www.iana.org/assignments/iana-ipv4-special-registry/iana-ipv4-special-registry.xhtml)
        for more information.
    """
    col = _as_column(column)
    error_message = f"Column `{col.name}` is not a valid IPv4 global address"
    return make_condition(
        ~is_ipv4_global_address_udf(col),
        error_message,
        "is_ipv4_global_address",
    )


@register_rule("row")
def is_ipv4_network(column: str | Column) -> Column:
    """Validates that a column contains a valid IPv4 network.

    This function creates a data quality check that validates whether each value
    in the specified column is a valid IPv4 network address in CIDR notation
    (e.g., "192.168.1.0/24").

    Args:
        column: The (name of the) column to validate.

    Returns:
        A `Column` with a boolean value representing the validation condition.

    Note:
        Network addresses must be in CIDR notation with a valid subnet mask
        (e.g., /8, /16, /24, /32).
    """
    col = _as_column(column)
    error_message = f"Column `{column}` is not a valid IPv4 network"
    return make_condition(
        ~is_ipv4_network_udf(col),
        error_message,
        "is_ipv4_network",
    )


@register_rule("row")
def is_ipv4_network_contains_address(
    column: str | Column, network: str | ipaddress.IPv4Network
) -> Column:
    """Validates that the IPv4 addresses in a column is contained within a specified network.

    This function creates a data quality check that validates whether each value
    in the specified column is an IPv4 address that falls within the given
    network.

    Args:
        column: The (name of the) column to validate.
        network: The IPv4 network in CIDR notation (e.g., "192.168.1.0/24")
            that should contain the addresses in the specified column.

    Returns:
        A `Column` with a boolean value representing the validation condition.

    Note:
        The network parameter must be a valid IPv4 network in CIDR notation. If the column
        contains invalid IPv4 addresses, the check will return `False`.
    """
    col = _as_column(column)
    if isinstance(network, str):
        network_parsed = str(ipaddress.IPv4Network(network))
    else:
        network_parsed = str(network)

    error_message = f"Network `{network_parsed}` does not contain address `{col}`"
    return make_condition(
        ~is_ipv4_network_contains_address_udf(col, f.lit(network_parsed)),
        error_message,
        "is_ipv4_network_contains_address",
    )


@f.udf(t.BooleanType())
def is_ipv4_address_udf(address: str) -> bool:
    """User-defined function to validate IPv4 address format.

    Args:
        address: A string representing an IPv4 address to validate.

    Returns:
        True if the address is a valid IPv4 address, False otherwise.

    Note:
        This is an internal UDF used by the main validation functions.
        It should not be called directly in most cases.
    """
    return validate_ipv4_address(address)


@f.udf(t.BooleanType())
def is_ipv4_loopback_address_udf(address: str) -> bool:
    """User-defined function to validate IPv4 loopback address.

    Args:
        address: A string representing an IPv4 address to validate.

    Returns:
        True if the address is a valid IPv4 loopback address, False otherwise.

    Note:
        This is an internal UDF used by the main validation functions.
        It should not be called directly in most cases.
    """
    return validate_loopback_ipv4_address(address)


@f.udf(t.BooleanType())
def is_ipv4_multicast_address_udf(address: str) -> bool:
    """User-defined function to validate IPv4 multicast address.

    Args:
        address: A string representing an IPv4 address to validate.

    Returns:
        True if the address is a valid IPv4 multicast address, False otherwise.

    Note:
        This is an internal UDF used by the main validation functions.
        It should not be called directly in most cases.
    """
    return validate_multicast_ipv4_address(address)


@f.udf(t.BooleanType())
def is_ipv4_private_address_udf(address: str) -> bool:
    """User-defined function to validate IPv4 private address.

    Args:
        address: A string representing an IPv4 address to validate.

    Returns:
        True if the address is a valid IPv4 private address, False otherwise.

    Note:
        This is an internal UDF used by the main validation functions.
        It should not be called directly in most cases.
    """
    return validate_private_ipv4_address(address)


@f.udf(t.BooleanType())
def is_ipv4_global_address_udf(address: str) -> bool:
    """User-defined function to validate IPv4 global address.

    Args:
        address: A string representing an IPv4 address to validate.

    Returns:
        True if the address is a valid IPv4 global address, False otherwise.

    Note:
        This is an internal UDF used by the main validation functions.
        It should not be called directly in most cases.
    """
    return validate_global_ipv4_address(address)


@f.udf(t.BooleanType())
def is_ipv4_network_udf(network: str) -> bool:
    """User-defined function to validate IPv4 network format.

    Args:
        network: A string representing an IPv4 network in CIDR notation to validate.

    Returns:
        True if the network is a valid IPv4 network, False otherwise.

    Note:
        This is an internal UDF used by the main validation functions.
        It should not be called directly in most cases.
    """
    return validate_ipv4_network(network)


@f.udf(t.BooleanType())
def is_ipv4_network_contains_address_udf(address: str, network: str) -> bool:
    """User-defined function to check if an address is contained within a network.

    Args:
        network: A string representing an IPv4 network in CIDR notation.
        address: A string representing an IPv4 address to check.

    Returns:
        True if the address is contained within the network, False otherwise.

    Note:
        This is an internal UDF used by the main validation functions.
        It should not be called directly in most cases.
    """
    return validate_network_contains_ipv4_address(network, address)


def _as_column(column: str | Column) -> Column:
    if isinstance(column, str):
        return f.col(column)
    else:
        return column
