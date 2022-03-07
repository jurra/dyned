import pandas as pd
from dined.dined import *
import pytest

@pytest.fixture
def pop_1():
    '''
    Loads a sample population 1
    '''
    # TODO: Optimize this fixture smaller data frame
    path = "./tests/fixtures/population_mock.csv"
    return pd.read_csv(path)

@pytest.fixture
def pop_2():
    '''
    Loads a sample population 2
    '''
    # TODO: Optimize this fixture smaller data frame
    path = "./tests/fixtures/population_mock_2.csv"
    return pd.read_csv(path)

@pytest.fixture
def door_handle_specs():
    '''
    Loads a sample door handle specs
    '''
    return pd.DataFrame({"Dimensions": ["Stature (mm)", "Elbow Ht Stand Rt (mm)" ],
                         "Target percentile": ["5%", "99%"],
                         "Clearance":[0, 0]})


def test_load_pop_1(pop_1):
    '''
    Tests if the sample population is loaded correctly
    '''
    assert type(pop_1) == pd.core.frame.DataFrame, "The population must be a dataframe" 

def test_get_design_param(pop_1):
    param = get_design_param(pop_1["Stature (mm)"], "5%", 10 )
    assert param == pytest.approx(1589.0)

def test_get_design_params(pop_1, door_handle_specs):
    '''
    Test this with a door handle
    WHEN a population dataframe with the "Stature (mm)" column,
    
    AND another dataframe with the "Elbow Ht Stand Rt (mm)" column
    
    AND a dataframe of specs with the "Dimensions" column, the "Target percentile" column 
    and the "Clearance" column

    THEN return a dataframe with the updated design specifications
    '''
    assert 
     

    # Except if populations dataframes have same column names




