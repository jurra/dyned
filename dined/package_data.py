'''
Generate a data-package.json for the dined data.
For now each resource is a table that should be a study
Each study has individuals as rows and measurements as fields

TODO: Packaging must be genericized to allow the transformation of different
tables coming from differnet sources and not necessarily standardize like dined data,
perhaps this package can also facilitate in this....perhaps is out of scope...

'''
from distutils.command import build
import json
import os
from os import name
from xmlrpc.client import Boolean

import pandas as pd
from frictionless import Package, Resource, validate
from dined import load_studies_metadata


# We use this class to generate fields for each resource in
# the data package
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

def get_fields_from_metadata(metadata_path: str) -> list:
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

            # if there is no description, use the name
            if field_info['description_en'] == '' or field_info['description_en'] == None:
                field.add_property('description', field_info['name_en'])
            else:
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
        # Read file and store in dataframe
        df = pd.read_csv(file_path)

        # Get fields from file
        # Pick the fields that match the column in the file
        fields = [ field for column in df.columns for field in dataset_fields if column == field['name']]        
        return fields
    
def write_fields(fields: list, fields_path: str):
    '''Writes fields to a json file in the specified fields_path.'''
    with open(fields_path, 'w') as f:
        # write fields to file
        json.dump(fields, f, indent=4)

def check_study_name(study_file_name: str, study_name: str) -> Boolean:
    '''Checks if the file name matches the study name.
    Given that the file name was generated from the study name in the metadata by lowercasing and adding _ to spaces,
    '''
    # Remove .csv extension from as well as _ from file name
    file_name = study_file_name.split('.')[0].lower()
    file_name = study_file_name.replace('_', ' ')
    study_name = study_name.lower()
    return file_name == study_name

def get_study_metadata(study_file_name: str, studies_metadata: list) -> dict:
    '''Checks if the study name exists in the metadata. 
    Throws an error if the study is duplicate
    
    >>> get_study_metadata('caesar_(it)', [{'name': 'Caesar (IT)'}])
    '''
    
    studies = load_studies_metadata(studies_metadata)

    # filter studies by file name
    study = [study for study in studies if check_study_name(study_file_name, study['name'])]
    # if study name is duplicate throw an error
    if len(study) > 1:
        raise ValueError('Study name is not unique')
    elif len(study) == 0:
        raise ValueError('Study name not found in metadata')
    else:
        return study[0]

# FRICTIONLESS METADATA GENERATION AND VALIDATION
def build_resource_descriptor(file_path: str, 
                             studies_metadata: str, 
                             measures_metadata: str) -> Resource:
    '''Builds a resource descriptor for a file.'''
    # Get file name without extension
    file_name = os.path.basename(os.path.normpath(file_path))
    file_name = file_name.split('.')[0]
    
    study_metadata = get_study_metadata(file_name, studies_metadata)
    
    # metadata fields means all the fields in all the studies
    metadata_fields = get_fields_from_metadata(measures_metadata)

    # resource_fields are the fields that are in the file
    resource_fields = get_fields_from_file(file_path, metadata_fields) 
    
    resource = Resource(
        path=f"./{file_path}",
        name=study_metadata['name'],
        description=study_metadata['description'],
        profile='tabular-data-resource',
        encoding='utf-8',
        schema={
            'fields': resource_fields
        }
    )
    return resource

def build_dined_data_package(measures_metadata: str,
                             studies_metadata: str,  
                             data_dir='./data') -> Package:
    '''Builds a data package for the dined data.'''
    # Get fields from metadata
    pkg = Package(
        name='dined-tables',
        title='Dined tabular Data',
        description='A data package consisting of tables describing 1D dimensional anthropometric data.',
    ) 

    pkg.resources = [] # we do this after creating the package to keep a more convenient output format
    
    files = os.listdir(data_dir)

    for file in files:
        # ignore files that are not csv
        if file.endswith('.csv'):
            # Create a resource for each file
            resource = build_resource_descriptor(f'{data_dir}/{file}', 
                                                studies_metadata , measures_metadata)
            print(resource)
            pkg.resources.append(resource)
    return pkg

def write_data_package(data_package: Package, package_medata_path: str, package_name) -> None:
    '''writes the data pakcage'''
    # Write table descriptor to file
    with open(f"{package_medata_path}/{package_name}", 'w') as f:
        json.dump(data_package, f, indent=4)

def validate_package(package_metadata) -> None:
    '''
    Checks for errors in the package using the frictionless 
    matadata spec for data-package
    '''    
    # Load package descriptor as a frictionless package
    pkg = Package(package_metadata)
    
    # Validate each file in the data directory with map function in pkg.rsources
    pkg.resources = list(map(lambda resource: validate(resource), pkg.resources))

    for resource in pkg.resources:
        # Validate each resource
        report = validate(f"./data/{resource.name}")
        # if report is invalid, write the log to a file
        if not report.valid:
            with open('validation_log.txt', 'w') as f:
                f.write(str(report.flatten(["rowPosition", "fieldPosition", "code"])))
            raise Exception('Invalid package')
        else:
            print(f'resource {resource.name} is valid')

    report = validate(package_metadata)
    if not report.valid:
        with open('validation_log.txt', 'w') as f:
            f.write(str(report.flatten(["rowPosition", "fieldPosition", "code"])))
        raise Exception('Invalid package')
    else:
        print('package is valid')
    
validate_resource = lambda resource: validate(resource)

def validate_resources(package_metadata='data-package/json') -> list:
    # Map and reduce function to validate each resource
    # return list(map(lambda resource: validate(resource), package_metadata))
    # load package descriptor as a frictionless package
    pkg = Package(package_metadata)
    # print(pkg)
    # print_resource = lambda resource: print(f'resource {resource.name}')
    return list(map(validate_resource, pkg.resources))

# Run main function
if __name__ == '__main__':
    # This the target directory where we want to put our package
    PACKAGE_DIR = './data'
    PACKAGE_METADATA = 'data-package.yaml'
    INFO = './metadata/measures.json'
    # package = build_dined_data_package()
    # package.to_json('./data/data-package.json')
    # package.to_yaml('./data/data-package.yaml')
    # validate_package(PACKAGE_METADATA)
    validate_resources(f"{PACKAGE_DIR}/{PACKAGE_METADATA}")
    
    # write_data_package(package, "./metadata", "data-package.json")
    print('Done.')








    
    