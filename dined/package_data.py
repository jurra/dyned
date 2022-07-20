'''
Generate a data-package.json for the dined data.
For now each resource is a table that should be a study
Each study has individuals as rows and measurements as fields
'''
from distutils.command import build
import json
import os
from os import name
from frictionless import Package, Resource
import pandas as pd
# Load env where we store metadata files, etc.

# Field data class
class Field:
    '''
    A class to store field data.
    A field is the dictionary that must include the name property
    '''
    # Here we put only the required properties
    def __init__(self, name):
        self.name = name
        self.field = { "name": name }
    
    # add name to field dictionary
    def add_name(self, name):
        self.field['name'] = name

    def add_property(self, key, value):
        self.field[key] = value
    
    # get field dictionary
    def get_field(self):
        return self.field
    
    def get_field_serialized(self):
        return json.dumps(self.field)

    # get subfield
    def get_property(self, key):
        return self.field[key]

class DataPackage():
    '''A class to to create a data-package.json.'''
    def __init__(self, name):
        self.name = name
        self.package = { "name": name }
        
    def add_property(self, key, value):
        self.package[key] = value
    
    def get_property(self, key):
        return self.package[key]

def get_fields_from_metadata(metadata_path) -> list:
    '''Gets fields from the dined metadata used to describe dined data
    '''    
    # load metadata
    metadata = json.load(open(metadata_path))
    
    # Get fields value pairs
    fields = []

    # The first field for each resource (study)
    individual = Field('id')
    individual.add_property('type', 'integer')
    fields.append(individual.field)

    for group in metadata:
        for field_info in group['labels']:
            field = Field(field_info['name_en'])
            field.add_property('id', field_info['id'])
            field.add_property('description', field_info['description_en'])
            field.add_property('type', "number")
            field.add_property('rdfType', 'https://schema.org/QuantitativeValue')
            field.add_property('unit', field_info['dimension'])
            # append only the Field.field dictionary not the entire object
            fields.append(field.field)
            
    return fields 

def load_fields(fields_path: str) -> list:
    '''Loads fields from a json file.'''
    with open(fields_path) as f:
        fields = json.load(f)
    return fields

def get_fields_from_file(file_path: str, dataset_fields: list) -> list:
    '''Procedure to get fields from a csv file to be later added to a Resource object.
    We read the columns and if the column name is in the list of fields generated,
    we return a list of fields
    '''
    # ignore file if it is not a csv
    if file_path.endswith('.csv'):
        # Get fields from file
        fields = []
        # Open the file with pandas
        df = pd.read_csv(file_path)

        # Pick the fields that match the column in the file
        for column in df.columns:
            for field in dataset_fields:
                if column == field['name']:
                    fields.append(field)
        return fields
    
def write_fields(fields, fields_path):
    with open(fields_path, 'w') as f:
        # write fields to file
        json.dump(fields, f, indent=4)

def build_dined_data_package(metadata_file='./metadata/measures.json', data_dir='./data'):
    '''Builds a data package for the dined data.'''
    # Get fields from metadata
    pkg = Package(
        name='dined-tables',
        title='Dined tabular Data',
        description='A data package consisting of tables describing 1D dimensional anthropometric data.',
        resources=[]
        ) 
    
    files = os.listdir(data_dir)

    for file in files:
        # Create a resource for each file
        resource = Resource(
            name=file,
            title=file,
            description='A table of data from the ' + file + ' file.'
        )
        file_fields = (get_fields_from_file(os.path.join(data_dir, file), get_fields_from_metadata(metadata_file)))
        resource.schema.fields = file_fields
        pkg.resources.append(resource)
    return pkg


def write_data_package(data_package: DataPackage, package_medata_path: str, package_name) -> None:
    '''writes the data pakcage'''
    # Write table descriptor to file
    with open(f"{package_medata_path}/{package_name}", 'w') as f:
        json.dump(data_package, f, indent=4)

def validate_table(package, table_path: str) -> None:
    '''TODO: Validates a table using frictionless.
    Once we have created the data we want to make sure that all data files are valid, 
    this is the ultimate test for this module.
    '''    
    package.validate()
    pass

# Create a data package using frictionless
def main()-> None:
    return build_dined_data_package()

# Run main function
if __name__ == '__main__':
    # TODO: pass arguments to main function from the command line
    # main("metadata","measures.json")
    # fields = get_fields_from_metadata("metadata/measures.json")
    # write_fields(fields, "./metadata/fields.json")
    pkg = main()
    write_data_package(pkg, "./metadata", "data-package.json")

    print('Done.')
    # exit(0)








    
    