# Data-Cutter Demo - Output Schema Builder

Interactive web interface for creating `output_schema.json` files with visual schema design and live JSON generation.

## Features

- **Two-Column Layout**: Current schema state on the left, rendered outputs on the right
- **Modal-Based Forms**: Clean interface for adding main fields and custom types
- **Current Schema State View**: See all added fields and types in real-time with delete functionality
- **Main Fields Editor**: Add fields to the root Result object via modal
- **Custom Data Types**: Create and manage custom data types with fields via modal
- **Advanced Constraints**: Support for string patterns, number ranges, array sizes, and more
- **Live Rendering**: Generate both `output_schema.json` and Pydantic model JSON schema
- **Download Support**: Export schemas as JSON files

## Quick Start

1. **Run the demo:**
   ```bash
   cd src/data-cutter-demo
   ./build.sh
   ```

2. **Open browser:**
   Navigate to `http://localhost:7800`

3. **Build your schema:**
   - Click "+ Add Main Field" to open the modal and add fields to Result object
   - Click "+ Add Custom Type" to create custom types and add their fields
   - View current state in real-time on the left column
   - Click "Generate Schema" to render outputs
   - View results in the right column

## Usage Guide

### Left Column: Current Schema State

The left column is your main workspace showing:
- **Action Buttons**: "+ Add Main Field" and "+ Add Custom Type"
- **Main Fields List**: All fields added to the Result object with details
- **Custom Types List**: All custom types with their fields
- **Generate/Reset Buttons**: Generate schema outputs or reset everything

**Managing Items:**
- Delete individual main fields with the Delete button
- Delete fields within types with the × button
- Delete entire types with the Delete button (also removes dependent main fields)

### Adding Main Fields (Modal)

1. Click "+ Add Main Field" button
2. Fill in the form:
   - Field name (e.g., "items")
   - Dimension: 0 (scalar) or 1 (array)
   - Data type: string, integer, number, boolean, bbox, or custom type
   - Optional checkbox
   - Description (optional)
   - Allowed values (comma-separated, optional)
3. Click "Add Field" - the modal will close and the field appears in the list

### Adding Custom Types (Modal)

1. Click "+ Add Custom Type" button
2. Enter type name (e.g., "Table", "Person", "Item")
3. Add fields to the type:
   - Fill in field name (e.g., "document_no", "page_no")
   - Select dimension (0 for scalar, 1 for array)
   - Choose data type (string, integer, number, boolean, bbox, or another custom type)
   - Set optional checkbox if needed
   - Add description and allowed values if needed
   - Expand constraint sections for advanced options (pattern, min/max, etc.)
   - Click "Add Field to Type"
4. The type is created automatically when you add the first field
5. The form clears field inputs but keeps the type name
6. Continue adding more fields or close the modal
7. The custom type and its fields appear in the Current Schema State

### Right Column: Generated Outputs

After clicking "Generate Schema":
- **Output Schema JSON**: Complete `output_schema.json` (top)
- **Model JSON Schema**: Pydantic model's JSON schema (bottom)
- Copy buttons for quick clipboard access
- Download buttons to save as files

### Advanced Constraints

Expand the constraint sections to add:

**String Constraints:**
- Format: email, date-time, uri, uuid
- Pattern: Regular expression validation

**Number Constraints:**
- Minimum/Maximum values

**Array Constraints:**
- minItems/maxItems counts


## File Structure

```
src/data-cutter-demo/
├── index.html          # Frontend UI (HTML + CSS + JS)
├── server.py           # Flask backend API
├── builder.py          # Schema builder logic (copied from gradio)
├── requirements.txt    # Python dependencies
├── build.sh           # Launch script
└── README.md          # This file
```

## API Endpoints

### POST /api/render
Generate both output_schema.json and model JSON schema.

**Request:**
```json
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
```

**Response:**
```json
{
  "success": true,
  "schema_json": "...",
  "model_schema_json": "...",
  "error": null
}
```

## Technical Details

### Frontend
- Pure HTML + CSS + Vanilla JavaScript
- No build process required
- Responsive design (works on mobile)
- State management in JavaScript

### Backend
- Flask web server
- Integrates with `data_cutter.model_maker.PydanticModelMaker`
- Validates schemas using `data_cutter.types.model_specification`
- Generates Pydantic model JSON schemas dynamically

### Schema Format

The output follows the `data_cutter` schema specification:

```json
{
  "type": "structured",
  "definition": {
    "name": "Result",
    "fields": [
      {
        "name": "field_name",
        "specification": {
          "dim": 0,
          "dtype": "string",
          "optional": false
        }
      }
    ],
    "custom_dtypes": [
      {
        "name": "CustomType",
        "fields": [...]
      }
    ]
  }
}
```

## Requirements

- Python 3.12+
- Flask 3.0+
- Pydantic 2.12.5+
- data_cutter package (parent directory)

## Development

To run in development mode:

```bash
# Activate virtual environment
source venv/bin/activate

# Run server with debug mode
python server.py
```

The server runs on `http://localhost:5000` by default.
