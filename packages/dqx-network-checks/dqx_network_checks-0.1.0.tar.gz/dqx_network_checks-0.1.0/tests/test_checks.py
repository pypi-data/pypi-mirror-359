import pyspark.sql.functions as f
from pyspark.testing.utils import assertDataFrameEqual

from dqx_network_checks.checks import (
    is_ipv4_address_udf,
    is_ipv4_global_address_udf,
    is_ipv4_loopback_address_udf,
    is_ipv4_multicast_address_udf,
    is_ipv4_network_contains_address_udf,
    is_ipv4_private_address_udf,
)


def test_ipv4_checks(spark):
    input_df = spark.createDataFrame(
        [
            ("1", "192.168.1.1"),
            ("2", "10.0.0.1"),
            ("3", "invalid ip"),
            ("4", "127.0.0.1"),
            ("5", "224.0.0.1"),
            ("6", "8.8.8.8"),
            ("7", "1.1.1.1"),
        ],
        "id STRING,ip STRING",
    )
    expected_df = spark.createDataFrame(
        [
            ("1", "192.168.1.1", True, False, False, True, False, False),
            ("2", "10.0.0.1", True, False, False, True, False, True),
            ("3", "invalid ip", False, False, False, False, False, False),
            ("4", "127.0.0.1", True, True, False, True, False, False),
            ("5", "224.0.0.1", True, False, True, False, True, False),
            ("6", "8.8.8.8", True, False, False, False, True, False),
            ("7", "1.1.1.1", True, False, False, False, True, False),
        ],
        "id STRING,ip STRING,is_ipv4_address BOOLEAN,is_ipv4_loopback_address BOOLEAN,is_ipv4_multicast_address BOOLEAN,is_ipv4_private_address BOOLEAN,is_ipv4_global_address BOOLEAN,is_ipv4_network_contains_address BOOLEAN",
    )

    result_df = (
        input_df.withColumn("is_ipv4_address", is_ipv4_address_udf("ip"))
        .withColumn("is_ipv4_loopback_address", is_ipv4_loopback_address_udf("ip"))
        .withColumn("is_ipv4_multicast_address", is_ipv4_multicast_address_udf("ip"))
        .withColumn("is_ipv4_private_address", is_ipv4_private_address_udf("ip"))
        .withColumn("is_ipv4_global_address", is_ipv4_global_address_udf("ip"))
        .withColumn(
            "is_ipv4_network_contains_address",
            is_ipv4_network_contains_address_udf("ip", f.lit("10.0.0.0/8")),
        )
        .orderBy("id")
    )
    assertDataFrameEqual(result_df, expected_df)
