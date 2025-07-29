import os

import pytest
from pyspark.sql import SparkSession

os.environ["PYARROW_IGNORE_TIMEZONE"] = "1"


@pytest.fixture(scope="session")
def spark():
    spark = SparkSession.builder.master("local[1]").appName("unit-test").getOrCreate()  # type: ignore
    yield spark
    spark.stop()


def pytest_collection_modifyitems(items):
    for item in items:
        if "spark" in getattr(item, "fixturenames", []):
            item.add_marker(pytest.mark.spark)
