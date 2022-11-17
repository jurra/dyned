import json
import os
from dataclasses import dataclass
from operator import itemgetter

# import fastjsonschema
import pandas as pd
from jsonschema import validate
import pytest
from genson import SchemaBuilder


# create a measure class
@dataclass
class Measure():
    # this measure class is based on the measure json schema
    # initialize the class
    name: str
    description: str
    measure: object

    # return data as a dictionary
    def to_dict(self):
        return {
            "name": self.name,
            "description": self.description,
            "measure": self.measure
        }

# normalize data with pandas
def normalize_measurement(measurement):
    '''Normalize measurements for one measure type from seralized json
    to a pandas dataframe
    >>> normalize_measurement(measurement)
    output example:
    head.value   head.unit    head.labels
         10        cm         [head, hands, sitting]
    '''
    # We build a dictionary that can use pandas json normalize to get a normalized
    # dataframe
    name, measure = itemgetter('name', 'measure')(measurement)
    measurement = {}
    measurement[name] = measure
    return pd.json_normalize(measurement)

measure_schema = {
    "type": "object",
    "properties": {
        "value": {
            "type": "number"
        },
        "unit": {
            "type": "string"
        },
        "labels": {
            "type": "array",
            "items": {
                "type": "string"
            }
        }
    }
}

head_schema = {
    "name": "Head",
    "description": "the head description",
    # type object
    "type": "object" ,
    "properties": {
        "name": {
            "type": "string",
            "pattern": "Head"
        },
        "field_name": {
            "type": "string",
            "pattern": "head"
        },
        "description": {
            "type": "string",
            "pattern": "the head description"
        },
        "measure": {
            "$ref": "#/definitions/measure"
        }
    },
    # definitions
    "definitions": {
        "measure": measure_schema
    }
}

# Example of serialized antropometric data respecting the head_schema_standard
HEAD = { "name": "head",
    "description": "the head description",
    "measure": {
        "value": 10,
        "unit": "cm",
        "labels": ["head", "hands", "sitting"]
        }
    }

def validate_schema(schema, data):
    '''Validate a schema against data'''
    return validate(data, schema)

def gen_schema(**kwargs):
    '''
    Generate a schema from a dictionary or a loaded schema
    '''
    builder = SchemaBuilder()
    # if schema is in kwargs, use it to build the schema
    if 'schema' in kwargs:
        builder.add_schema(kwargs['schema'])
    if 'schema_obj' in kwargs:
        builder.add_object(kwargs['schema_obj'])
    builder.to_schema()
    return builder

def write_schema(builder, filename) -> None:
    '''Write a schema to a file'''
    # dont rewrite the file
    if os.path.exists(filename):
        print(f'File {filename} already exists, skipping')
    else:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(builder.to_json(indent=2))

def load_jsonschema(filename):
    '''Load a jsonschema from a file'''
    with open(filename,'r', encoding='utf-8') as f:
        schema = json.loads(f.read())
    return schema

@pytest.fixture
def valid_measure_data():
    '''measure_data fixture'''
    return HEAD

@pytest.fixture
def invalid_measure_data():
    '''measure_data fixture'''
    return { "name": "Arm",
    "description": "the head description",
    "measure": {
        "value": "A string",
        "unit": "cm",
        "labels": ["head", "hands", "sitting"]
        }
    }

# Validate measure
def test_measure_standard(valid_measure_data, invalid_measure_data):
    '''Test the measure standard'''
    # exception when data is not valid
    with pytest.raises(Exception):
        validate_schema(instance=invalid_measure_data, schema=measure_schema)
    
    assert validate(instance=valid_measure_data, schema=measure_schema) is None

def test_study_standard():
    pass

def test_individual_standard():
    pass