# terraback/terraform_generator/filters.py

import json

def sanitize_for_terraform(value):
    """A general-purpose sanitizer for Terraform resource names."""
    if not isinstance(value, str):
        value = str(value)
    # Replace anything that isn't a letter, number, hyphen, or underscore
    import re
    value = re.sub(r'[^a-zA-Z0-9_-]', '_', value)
    # Ensure it doesn't start with a number
    if value and value[0].isdigit():
        value = '_' + value
    return value

def to_terraform_string(value):
    """Formats a Python string into a Terraform-safe string."""
    if value is None:
        return "null"
    return json.dumps(value)

def to_terraform_list(value):
    """Formats a Python list into a Terraform list."""
    if value is None:
        return "[]"
    return json.dumps(value)

def to_terraform_map(value):
    """Formats a Python dictionary into a Terraform map."""
    if value is None:
        return "{}"
    return json.dumps(value)

def to_terraform_bool(value):
    """Formats a Python boolean into a Terraform boolean."""
    if value is None:
        return "null"
    return str(value).lower()

def to_terraform_int(value):
    """Formats a Python integer into a Terraform number."""
    if value is None:
        return "null"
    return str(int(value))

def to_terraform_float(value):
    """Formats a Python float into a Terraform number."""
    if value is None:
        return "null"
    return str(float(value))

def to_terraform_resource_name(value):
    """Creates a valid Terraform resource name from a string."""
    if not value:
        return "unnamed_resource"
    # Replace common separators and invalid characters with underscores
    name = str(value).replace('.', '_').replace('/', '_').replace('-', '_')
    # Remove any other non-alphanumeric characters
    import re
    name = re.sub(r'[^a-zA-Z0-9_]', '', name)
    # Ensure it starts with a letter or underscore
    if name and name[0].isdigit():
        name = '_' + name
    return name.lower()