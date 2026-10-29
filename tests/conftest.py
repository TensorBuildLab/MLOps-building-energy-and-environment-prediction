import pandas as pd
import pytest

from bemlops.datasets import OFFICE_POINTS, messy_office

TS_FORMAT = "%m/%d/%Y %I:%M:%S %p"


@pytest.fixture(scope="session")
def messy():
    export, truth = messy_office(days=60, seed=0)
    return export, truth


@pytest.fixture(scope="session")
def messy_indexed(messy):
    export, truth = messy
    df = export.copy()
    df.index = pd.to_datetime(df.pop("Timestamp"), format=TS_FORMAT)
    return df, truth


@pytest.fixture()
def points():
    return dict(OFFICE_POINTS)
