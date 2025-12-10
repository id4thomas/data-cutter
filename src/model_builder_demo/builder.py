"""
SchemaBuilder class for creating output_schema.json structures
Can be used standalone without Gradio
"""

import json
from typing import List


class SchemaBuilder:
    """Builder for creating output schema JSON structures"""

    def __init__(self):
        self.reset_schema()

    def reset_schema(self):
        """Reset to default schema structure"""
        self.schema = {
            "type": "structured",
            "definition": {
                "name": "Result",
                "fields": [],
                "custom_dtypes": []
            }
        }

    def add_field(self, field_name: str, dim: int, dtype: str,
                  optional: bool = False, description: str = "",
                  allowed_values: str = "") -> str:
        """Add a field to the main Result object"""
        if not field_name:
            return "Error: Field name is required"

        field = {
            "name": field_name,
            "specification": {
                "dim": dim,
                "dtype": dtype,
                "optional": optional
            }
        }

        if description:
            field["specification"]["description"] = description

        if allowed_values:
            values = [v.strip() for v in allowed_values.split(",")]
            field["specification"]["allowed_values"] = values

        self.schema["definition"]["fields"].append(field)
        return f"Added field: {field_name}"

    def add_custom_dtype(self, dtype_name: str) -> str:
        """Add a new custom dtype"""
        if not dtype_name:
            return "Error: Custom dtype name is required"

        # Check if already exists
        for dt in self.schema["definition"]["custom_dtypes"]:
            if dt["name"] == dtype_name:
                return f"Error: Custom dtype '{dtype_name}' already exists"

        custom_dtype = {
            "name": dtype_name,
            "fields": []
        }
        self.schema["definition"]["custom_dtypes"].append(custom_dtype)
        return f"Added custom dtype: {dtype_name}"

    def add_custom_dtype_field(self, dtype_name: str, field_name: str,
                               dim: int, dtype: str,
                               optional: bool = False,
                               description: str = "",
                               pattern: str = "",
                               format_type: str = "",
                               allowed_values: str = "",
                               minimum: str = "",
                               maximum: str = "",
                               min_items: str = "",
                               max_items: str = "") -> str:
        """Add a field to a custom dtype"""
        if not dtype_name or not field_name:
            return "Error: Both dtype name and field name are required"

        # Find the custom dtype
        custom_dtype = None
        for dt in self.schema["definition"]["custom_dtypes"]:
            if dt["name"] == dtype_name:
                custom_dtype = dt
                break

        if not custom_dtype:
            return f"Error: Custom dtype '{dtype_name}' not found"

        field = {
            "name": field_name,
            "specification": {
                "dim": dim,
                "dtype": dtype,
                "optional": optional
            }
        }

        # Add optional fields
        if description:
            field["specification"]["description"] = description

        if pattern:
            field["specification"]["pattern"] = pattern

        if format_type:
            field["specification"]["format"] = format_type

        if allowed_values:
            values = [v.strip() for v in allowed_values.split(",")]
            field["specification"]["allowed_values"] = values

        if minimum:
            try:
                field["specification"]["minimum"] = float(minimum) if '.' in minimum else int(minimum)
            except ValueError:
                pass

        if maximum:
            try:
                field["specification"]["maximum"] = float(maximum) if '.' in maximum else int(maximum)
            except ValueError:
                pass

        if min_items:
            try:
                field["specification"]["minItems"] = int(min_items)
            except ValueError:
                pass

        if max_items:
            try:
                field["specification"]["maxItems"] = int(max_items)
            except ValueError:
                pass

        custom_dtype["fields"].append(field)
        return f"Added field '{field_name}' to custom dtype '{dtype_name}'"

    def get_json(self) -> str:
        """Get the current schema as formatted JSON"""
        return json.dumps(self.schema, indent=4)

    def get_custom_dtype_names(self) -> List[str]:
        """Get list of custom dtype names"""
        return [dt["name"] for dt in self.schema["definition"]["custom_dtypes"]]

    def load_example(self, example_type: str) -> str:
        """Load a predefined example schema"""
        if example_type == "Table Extraction":
            self.schema = {
                "type": "structured",
                "definition": {
                    "name": "Result",
                    "fields": [
                        {
                            "name": "items",
                            "specification": {
                                "dim": 1,
                                "dtype": "Table",
                                "optional": False
                            }
                        }
                    ],
                    "custom_dtypes": [
                        {
                            "name": "Table",
                            "fields": [
                                {
                                    "name": "document_no",
                                    "specification": {
                                        "dim": 0,
                                        "dtype": "integer",
                                        "optional": False
                                    }
                                },
                                {
                                    "name": "page_no",
                                    "specification": {
                                        "dim": 0,
                                        "dtype": "integer",
                                        "optional": False
                                    }
                                },
                                {
                                    "name": "parsed_text",
                                    "specification": {
                                        "dim": 0,
                                        "dtype": "string",
                                        "optional": False
                                    }
                                },
                                {
                                    "name": "bbox",
                                    "specification": {
                                        "dim": 0,
                                        "dtype": "bbox",
                                        "optional": False
                                    }
                                }
                            ]
                        }
                    ]
                }
            }
            return "Loaded Table Extraction example"

        elif example_type == "Simple List":
            self.schema = {
                "type": "structured",
                "definition": {
                    "name": "Result",
                    "fields": [
                        {
                            "name": "items",
                            "specification": {
                                "dim": 1,
                                "dtype": "Item",
                                "optional": False
                            }
                        }
                    ],
                    "custom_dtypes": [
                        {
                            "name": "Item",
                            "fields": [
                                {
                                    "name": "value",
                                    "specification": {
                                        "dim": 0,
                                        "dtype": "string",
                                        "optional": False
                                    }
                                },
                                {
                                    "name": "label",
                                    "specification": {
                                        "dim": 0,
                                        "dtype": "string",
                                        "optional": False,
                                        "allowed_values": ["a", "b"]
                                    }
                                }
                            ]
                        }
                    ]
                }
            }
            return "Loaded Simple List example"

        else:  # Empty
            self.reset_schema()
            return "Reset to empty schema"
