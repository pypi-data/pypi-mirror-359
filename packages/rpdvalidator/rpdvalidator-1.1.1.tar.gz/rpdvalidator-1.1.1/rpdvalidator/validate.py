import json
import os
from referencing import Registry
from jsonschema import Draft7Validator
from referencing.jsonschema import DRAFT7
from rpdvalidator.jsonpath_utils import *


def schema_validate(rpd: dict, schema_version: str = "0.1.7", full_errors: bool = False) -> dict:
    """
    Validates an RPD against the specified version of the schema.
    Parameters
    ----------
    rpd : dict
        The RPD to validate
    schema_version : str
        The version of the schema to validate against
    full_errors : bool
        Whether to print full error messages

    Returns
    -------
    dict
        A dictionary containing the validation result. The "passed" key is a boolean indicating whether the validation
        passed. If the validation failed, the "errors" key contains a list of error messages

    """

    schema_file_paths = get_schema_file_paths(schema_version)

    # Load the schema files
    with open(schema_file_paths["SCHEMA_PATH"]) as json_file:
        schema = json.load(json_file)
    with open(schema_file_paths["SCHEMA_901_ENUM_PATH"]) as json_file:
        schema_enum = json.load(json_file)
    with open(schema_file_paths["SCHEMA_T24_ENUM_PATH"]) as json_file:
        schema_t24_enum = json.load(json_file)
    with open(schema_file_paths["SCHEMA_RESNET_ENUM_PATH"]) as json_file:
        schema_resnet_enum = json.load(json_file)
    with open(schema_file_paths["SCHEMA_OUTPUT_PATH"]) as json_file:
        schema_output = json.load(json_file)

    # Create a resource registry for resolving schema references
    registry = Registry().with_resources(
        [
            ("ASHRAE229.schema.json", DRAFT7.create_resource(schema)),
            ("Enumerations2019ASHRAE901.schema.json", DRAFT7.create_resource(schema_enum)),
            ("Enumerations2019T24.schema.json", DRAFT7.create_resource(schema_t24_enum)),
            ("EnumerationsRESNET.schema.json", DRAFT7.create_resource(schema_resnet_enum)),
            ("Output2019ASHRAE901.schema.json", DRAFT7.create_resource(schema_output)),
        ]
    )
    try:
        # Validate the RPD against the schema
        validator = Draft7Validator(schema, registry=registry)
        Draft7Validator.check_schema(schema)
        errors = list(validator.iter_errors(rpd))

        if errors:
            error_details = []
            for error in errors:
                # Convert absolute paths to JSONPath format
                error_path = convert_absolute_path_list_to_jsonpath(list(error.absolute_path))
                parent_id_path = format_jsonpath_with_id(list(error.absolute_path))
                parent_id = find_all(parent_id_path, rpd) if parent_id_path else ""

                # Construct the error message
                parent_id = parent_id[0] if parent_id else parent_id
                if not full_errors:
                    truncated_message = (error.message[:20] + '..........' + error.message[-130:]) if len(error.message) > 160 else error.message
                    error_message = (
                        f"{truncated_message}. Path: {error_path}." +
                        (f" Parent ID: {parent_id}" if parent_id else "")
                    )
                else:
                    error_message = (
                        f"{error.message}. Path: {error_path}." +
                        (f" Parent ID: {parent_id}" if parent_id else "")
                    )
                error_details.append(error_message)

            return {"passed": False, "errors": error_details}

        return {"passed": True, "errors": None}  # No errors found

    except Exception as error:
        return {"passed": False, "errors": [f"Unexpected error: {str(error)}"]}


def get_schema_file_paths(schema_version: str) -> dict:
    """
    Get the paths to the schema files for the given schema version
    Parameters
    ----------
    schema_version : str
        The version of the schema

    Returns
    -------
    dict
        A dictionary containing the paths to the schema files

    """
    file_dir = os.path.dirname(__file__)
    schema_paths = {
        "SCHEMA_PATH": os.path.join(file_dir, f"schema_versions/{schema_version}/ASHRAE229.schema.json"),
        "SCHEMA_901_ENUM_PATH": os.path.join(file_dir, f"schema_versions/{schema_version}/Enumerations2019ASHRAE901.schema.json"),
        "SCHEMA_T24_ENUM_PATH": os.path.join(file_dir, f"schema_versions/{schema_version}/Enumerations2019T24.schema.json"),
        "SCHEMA_RESNET_ENUM_PATH": os.path.join(file_dir, f"schema_versions/{schema_version}/EnumerationsRESNET.schema.json"),
        "SCHEMA_OUTPUT_PATH": os.path.join(file_dir, f"schema_versions/{schema_version}/Output2019ASHRAE901.schema.json")
    }

    return schema_paths
