"""DQX network checks plugin.

This module provides a comprehensive set of data quality checks for IPv4 address
and network validation using PySpark DataFrames. It includes checks for various
IPv4 address types (loopback, multicast, private, global) and network operations.

The module integrates with the Databricks Data Quality Framework (DQX) to provide
row-level validation rules that can be applied to DataFrame columns. For more information
on how to use the DQX framework, see the [DQX documentation](https://github.com/databrickslabs/dqx).

Example:
    ```python
    import yaml

    from databricks.labs.dqx.engine import DQEngine
    from databricks.sdk import WorkspaceClient
    from databricks.labs.dqx.rule import DQRowRule
    from dqx_network_checks import is_ipv4_address

    input_df = spark.createDataFrame(
        [
            ("1", "192.168.1.1"),
            ("2", "10.0.0.1"),
            ("3", "invalid ip"),
        ],
        "id STRING,ip STRING",
    )
    checks = [
        DQRowRule(criticality="error", check_func=is_ipv4_address, column="ip"),
    ]
    dq_engine = DQEngine(WorkspaceClient(), spark=spark)
    valid_df, quarantine_df = dq_engine.apply_checks_and_split(input_df, checks)
"""

__version__ = "0.1.0"

from typing import Callable

from dqx_network_checks.checks import (
    is_ipv4_address,
    is_ipv4_global_address,
    is_ipv4_loopback_address,
    is_ipv4_multicast_address,
    is_ipv4_network,
    is_ipv4_network_contains_address,
    is_ipv4_private_address,
)


def get_network_checks() -> dict[str, Callable]:
    return {
        "is_ipv4_address": is_ipv4_address,
        "is_ipv4_loopback_address": is_ipv4_loopback_address,
        "is_ipv4_multicast_address": is_ipv4_multicast_address,
        "is_ipv4_private_address": is_ipv4_private_address,
        "is_ipv4_global_address": is_ipv4_global_address,
        "is_ipv4_network": is_ipv4_network,
        "is_ipv4_network_contains_address": is_ipv4_network_contains_address,
    }


__all__ = [
    "get_network_checks",
    "is_ipv4_address",
    "is_ipv4_loopback_address",
    "is_ipv4_multicast_address",
    "is_ipv4_private_address",
    "is_ipv4_global_address",
    "is_ipv4_network",
    "is_ipv4_network_contains_address",
]
