# data-cutter
Data extraction with LLM structured generation

<img src="./assets/header.png" width=75% height=75%>

## Concepts
Each extraction is defined as `Tasks`s. A Task folder should contain the following information files.

| Contents | File Name | Description |
| --- | --- | --- |
| Prompt Template | `prompt_template.yaml` | Contains instructions and input variable names used for this task | 
| Generation Config | `generation_config.json` | Contains combinations of LLM & parameters |
| Output Schema | `output_schema.json` | Contains `SchemaConfig` needed to build response_format's json_schema |
| Input Example | `input_example.json` | (Optional) Example input dictionary for testing |

## Usage
### SchemaModelMaker
Dynamically makes pydantic model types 

```python
from data_cutter.model_maker import PydanticModelMaker
from data_cutter.types.model_specification import ModelSpecification

spec = ModelSpecification.model_validate(specification_dict)
model = PydanticModelMaker().make(spec)
```


<table>
<tr>
    <th>Pydantic Model</th>
    <th>DataCutter ModelSpecification</th>
</tr>
<tr>
<td>

```python
from enum import Enum
from pydantic import BaseModel

class Label(str, Enum):
    a="a"
    b="b"

class Item(BaseModel):
    value: str
    label: Label

class Result(BaseModel):
    items: List[Item]
```

</td>
<td>


```json
{
  "name": "Result",
  "fields": [
    {
      "name": "items",
      "specification": {
        "dim": 1,
        "dtype": "Item"
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
            "dtype": "string"
          }
        },
        {
          "name": "label",
          "specification": {
            "dim": 0,
            "dtype": "string",
            "allowed_values": ["a", "b"]
          }
        }
      ]
    }
  ]
}
```

</td>
</tr>
</table>



## References
- Pydantic dynamic model creation ([link](https://docs.pydantic.dev/latest/concepts/models/#dynamic-model-creation))