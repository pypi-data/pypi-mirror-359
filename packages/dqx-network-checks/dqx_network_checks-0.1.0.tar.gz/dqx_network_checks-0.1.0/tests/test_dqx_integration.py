import yaml
from unittest import mock

from databricks.labs.dqx.engine import DQEngine
from databricks.labs.dqx.rule import DQRowRule
from databricks.sdk import WorkspaceClient

from dqx_network_checks import get_network_checks, is_ipv4_address


def test_dqx_integration_classes(spark):
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
    mock_workspace_client = mock.create_autospec(WorkspaceClient)
    dq_engine = DQEngine(mock_workspace_client, spark=spark)

    valid_df, quarantine_df = dq_engine.apply_checks_and_split(input_df, checks)  # type: ignore

    assert valid_df.count() == 2
    assert quarantine_df.count() == 1


def test_dqx_integration_yaml(spark):
    input_df = spark.createDataFrame(
        [
            ("1", "192.168.1.1"),
            ("2", "10.0.0.1"),
            ("3", "invalid ip"),
        ],
        "id STRING,ip STRING",
    )
    checks = yaml.safe_load(
        """
    - criticality: error
      check:
        function: is_ipv4_address
        arguments:
          column: ip
    """
    )
    mock_workspace_client = mock.create_autospec(WorkspaceClient)
    dq_engine = DQEngine(mock_workspace_client, spark=spark)
    custom_checks = get_network_checks()

    valid_df, quarantine_df = dq_engine.apply_checks_by_metadata_and_split(
        input_df, checks, custom_checks
    )

    assert valid_df.count() == 2
    assert quarantine_df.count() == 1
