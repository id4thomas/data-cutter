"""
Flask server for Output Schema Builder Demo
Provides API endpoints to generate output_schema.json and Pydantic model JSON schema
"""

import json
import sys
from pathlib import Path
from flask import Flask, request, jsonify, send_from_directory

# Add parent directory to path to import data_cutter
sys.path.insert(0, str(Path(__file__).parent.parent))

from data_cutter.types.model_specification import ModelSpecification
from data_cutter.model_maker.maker import PydanticModelMaker
from builder import SchemaBuilder


app = Flask(__name__, static_folder='.')


@app.route('/')
def index():
    """Serve the main HTML page"""
    return send_from_directory('.', 'index.html')


@app.route('/api/render', methods=['POST'])
def render_schema():
    """
    Generate both output_schema.json and Pydantic model JSON schema

    Expected input:
    {
        "schema": {
            "type": "structured",
            "definition": {
                "name": "Result",
                "fields": [...],
                "custom_dtypes": [...]
            }
        }
    }

    Returns:
    {
        "success": true,
        "schema_json": "...",
        "model_schema_json": "...",
        "error": null
    }
    """
    try:
        data = request.get_json()

        if not data or 'schema' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing schema in request body'
            }), 400

        schema = data['schema']

        # Validate that it's structured type
        if schema.get('type') != 'structured':
            return jsonify({
                'success': False,
                'error': 'Only structured schemas are supported'
            }), 400

        definition = schema.get('definition')
        if not definition:
            return jsonify({
                'success': False,
                'error': 'Missing definition in schema'
            }), 400

        # Generate output_schema.json (formatted)
        schema_json = json.dumps(schema, indent=4)

        # Generate Pydantic model JSON schema
        try:
            # Validate and create ModelSpecification
            model_spec = ModelSpecification(**definition)

            # Generate Pydantic model
            maker = PydanticModelMaker()
            pydantic_model = maker.make(model_spec)

            # Get JSON schema
            model_schema = pydantic_model.model_json_schema()
            model_schema_json = json.dumps(model_schema, indent=4)

            return jsonify({
                'success': True,
                'schema_json': schema_json,
                'model_schema_json': model_schema_json,
                'error': None
            })

        except ValueError as e:
            return jsonify({
                'success': False,
                'error': f'Model validation error: {str(e)}'
            }), 400
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Error generating model schema: {str(e)}'
            }), 500

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500


# @app.route('/api/examples/<example_name>', methods=['GET'])
# def get_example(example_name):
#     """
#     Get predefined example schemas

#     Available examples: table_extraction, simple_list
#     """
#     builder = SchemaBuilder()

#     if example_name == 'table_extraction':
#         builder.load_example('Table Extraction')
#     elif example_name == 'simple_list':
#         builder.load_example('Simple List')
#     else:
#         return jsonify({
#             'success': False,
#             'error': f'Unknown example: {example_name}'
#         }), 404

#     schema = builder.schema
#     return jsonify({
#         'success': True,
#         'schema': schema
#     })


if __name__ == '__main__':
    port=7800
    print("=" * 60)
    print("  Output Schema Builder Demo")
    print("=" * 60)
    print(f"\n  Server running at: http://localhost:{port}")
    print("\n  Press Ctrl+C to stop the server\n")
    print("=" * 60)

    app.run(debug=True, host='0.0.0.0', port=port)
