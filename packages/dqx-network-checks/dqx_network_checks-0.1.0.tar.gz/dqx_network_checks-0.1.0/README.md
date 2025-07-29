# DQX Network Checks

A comprehensive extension to the [Databricks Data Quality Framework (DQX)](https://github.com/databrickslabs/dqx) that provides specialized data quality checks for network-related data, including IPv4 addresses, CIDR networks, and network validation operations. It provides row-level validation rules that can be applied to DataFrame columns containing IP addresses, network ranges, and other network-related information.

## Quick Start

### Basic Usage

Use the network checks inside `DQRule` classes and apply them to your dataframes 

```python
from databricks.labs.dqx.engine import DQEngine
from databricks.labs.dqx.rule import DQRowRule
from databricks.sdk import WorkspaceClient
from dqx_network_checks import is_ipv4_address, is_ipv4_private_address

# Create sample data
input_df = spark.createDataFrame([
    ("192.168.1.1",),
    ("10.0.0.1",),
    ("invalid ip",),
    ("8.8.8.8",),
], "ip STRING")

# Define data quality checks
checks = [
    DQRowRule(criticality="error", check_func=is_ipv4_address, column="ip"),
    DQRowRule(criticality="warning", check_func=is_ipv4_private_address, column="ip"),
]

# Apply checks using DQX engine
dq_engine = DQEngine(WorkspaceClient())
valid_df, quarantine_df = dq_engine.apply_checks_and_split(input_df, checks)
```

Or use the YAML syntax to define and apply your (network)rules

```python
from databricks.labs.dqx.engine import DQEngine
from databricks.sdk import WorkspaceClient
from dqx_network_checks import get_network_checks

# Create sample data
input_df = spark.createDataFrame([
    ("192.168.1.1",),
    ("10.0.0.1",),
    ("invalid ip",),
    ("8.8.8.8",),
], "ip STRING")

# Define data quality checks
custom_checks = get_network_checks()
checks = yaml.safe_load("""
- criticality: error
  check:
    function: is_ipv4_address
    arguments:
      column: ip
""")

# Apply checks using DQX engine
dq_engine = DQEngine(WorkspaceClient())
valid_df, quarantine_df = dq_engine.apply_checks_by_metadata_and_split(
    input_df, checks, custom_checks
)
```

## Available Checks

### Address Type Validation

| Check Function | Description | Example Valid Values |
|---------------|-------------|---------------------|
| `is_ipv4_address` | Validates IPv4 address format | `"192.168.1.1"`, `"10.0.0.1"` |
| `is_ipv4_loopback_address` | Loopback addresses (127.0.0.0/8) | `"127.0.0.1"`, `"127.255.255.255"` |
| `is_ipv4_multicast_address` | Multicast addresses (224.0.0.0/4) | `"224.0.0.1"`, `"239.255.255.255"` |
| `is_ipv4_private_address` | Private network addresses | `"192.168.1.1"`, `"10.0.0.1"`, `"172.16.0.1"` |
| `is_ipv4_global_address` | Public/global addresses | `"8.8.8.8"`, `"1.1.1.1"` |

### Network Operations

| Check Function | Description | Example Valid Values |
|---------------|-------------|---------------------|
| `is_ipv4_network` | Validates CIDR network notation | `"192.168.1.0/24"`, `"10.0.0.0/8"` |
| `is_ipv4_network_contains_address` | Checks if IP is in network range | `("192.168.1.1", "192.168.1.0/24")` |

## Performance Considerations

- All checks use PySpark UDFs for distributed processing
- Network validation is performed using Python's built-in `ipaddress` module
- Checks are optimized for large-scale data processing in Databricks

## Acknowledgments

- Built on the [Databricks Data Quality Framework (DQX)](https://github.com/databrickslabs/dqx)
