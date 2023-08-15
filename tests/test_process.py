import os

import pandas as pd
import pytest
import yaml
from pandas.testing import assert_frame_equal

from app import process


def load_test_data():
    path_config = os.path.join(os.path.dirname(__file__), "test_process.yml")
    with open(path_config) as file:
        test_data = yaml.safe_load(file)
    return test_data


@pytest.mark.parametrize("data", load_test_data())
def test_processing(data):
    # define input parameters
    l0 = data["l0"]
    l1 = data["l1"]
    hsreuse = data["hsreuse"]
    year = data["year"]
    q0 = data["q0"]
    q1 = data["q1"]
    tpdist_beton_reuse = data["tpdist_beton_reuse"]
    tpdist_metal_reuse = data["tpdist_metal_reuse"]
    steelprofile_type = data["steelprofile_type"]

    df_result = process.processing(
        l0, l1, hsreuse, year, q0, q1, tpdist_beton_reuse, tpdist_metal_reuse, steelprofile_type
    )[2]

    expected_df = pd.DataFrame({"values": data["expected"]}, index=["Impact new", "Impact reuse"]).rename_axis("labels")

    assert_frame_equal(df_result, expected_df)
