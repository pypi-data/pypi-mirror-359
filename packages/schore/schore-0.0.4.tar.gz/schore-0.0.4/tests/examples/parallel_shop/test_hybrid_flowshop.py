import io

import pytest

from src.schore.parameters_examples.parallel_shop.identical_flow import (
    HybridFlowshopParameters,
)


@pytest.fixture
def pra_data_stream():
    """Fixture to provide a sample PRA data stream."""
    data = """\
6
3
2 3 2
2 3 4
6 4 8
9 1 5
4 6 3
1 5 10
4 8 12
"""
    return io.StringIO(data)


@pytest.fixture
def params(pra_data_stream) -> HybridFlowshopParameters:
    """Fixture to parse the PRA data into a HybridFlowshopParameters."""
    return HybridFlowshopParameters.from_pra_data("from_pra_data", pra_data_stream)


def test_params_structure(params: HybridFlowshopParameters):
    """Test the overall structure of the parsed params."""
    assert params.job_count == 6
    assert params.stage_count == 3
    assert params.machine_count_per_stage == [2, 3, 2]
    assert params.job_id_list == ["j0", "j1", "j2", "j3", "j4", "j5"]
    assert params.stage_id_list == ["i0", "i1", "i2"]
    assert params.stage_2_machines_map == {
        "i0": ["i0_0", "i0_1"],
        "i1": ["i1_0", "i1_1", "i1_2"],
        "i2": ["i2_0", "i2_1"],
    }


def test_create_instance_of_job_subset(params: HybridFlowshopParameters):
    """Test the creation of a new instance based on a subset of jobs."""
    job_subset = ["j0", "j2", "j4"]
    subset_params = params.create_instance_of_job_subset(job_subset)

    assert subset_params.job_count == len(job_subset)
    assert subset_params.stage_count == params.stage_count
    assert subset_params.machine_count_per_stage == params.machine_count_per_stage
    assert subset_params.job_id_list == job_subset

    expected_processing_times = [
        params.p_manager.df.iloc[0].tolist(),
        params.p_manager.df.iloc[2].tolist(),
        params.p_manager.df.iloc[4].tolist(),
    ]
    actual_processing_times = subset_params.p_manager.df.values.tolist()
    assert actual_processing_times == expected_processing_times

    assert subset_params.stage_2_machines_map == params.stage_2_machines_map


def test_invalid_job_count():
    """
    Test that from_pra_data raises EOFError for mismatched job count.
    If the number of jobs in the data is less than the specified job count,
    it should raise a EOFError indicating the mismatch.
    If the number of jobs in the data is more than the specified job count,
    it will truncate the data to match the specified job count.
    """
    bad_data = """\
5
3
2 3 2
2 3 4
6 4 8
9 1 5
"""
    with pytest.raises(
        EOFError,
        match="Unexpected end of file while reading 4-th row"
        " among 5 rows of list of type int.",
    ):
        HybridFlowshopParameters.from_pra_data("from_pra_data", io.StringIO(bad_data))


def test_invalid_stage_count():
    """Test that from_pra_data raises ValueError for mismatched stage count."""
    bad_data = """\
6
4
2 3 2
2 3 4
6 4 8
9 1 5
4 6 3
1 5 10
4 8 12
"""
    with pytest.raises(
        ValueError,
        match="Stage count mismatch; stage_count=4; by machine_count_per_stage=3",
    ):
        HybridFlowshopParameters.from_pra_data("from_pra_data", io.StringIO(bad_data))


def test_empty_input():
    """Test that from_pra_data raises EOFError for empty input."""
    data = ""
    with pytest.raises(EOFError, match="Unexpected end of file while reading data."):
        HybridFlowshopParameters.from_pra_data("from_pra_data", io.StringIO(data))


def test_null_processing_time():
    """Test that from_pra_data raises ValueError for null processing time."""
    bad_data = """\
6
3
2 3 2
2 3 4
6 4 8
9 1
4 6 3
1 5 10
4 8 12
"""
    with pytest.raises(
        ValueError, match="Null value exists in the processing time data"
    ):
        HybridFlowshopParameters.from_pra_data("from_pra_data", io.StringIO(bad_data))
