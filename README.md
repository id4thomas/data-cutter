# data-cutter
Data extraction with LLM structured generation

<img src="./assets/header.png" width=50% height=50%>

## Usage
### SchemaModelMaker

<table>
<tr>
    <th>Pydantic Model</th>
    <th>DataCutter Schema Config</th>
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
            "specification": {"dim": 1, "dtype": "Item"}
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



## References
- Pydantic dynamic model creation ([link](https://docs.pydantic.dev/latest/concepts/models/#dynamic-model-creation))