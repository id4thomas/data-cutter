from typing import Any, Dict, List, Type, Union
from enum import Enum

from pydantic import BaseModel, create_model

from data_cutter.types.schema import (
    DtypeSpec,
    CustomDTypeSpec,
    FieldSpec,
    SchemaConfig,
)
from .dtypes import Bbox


def create_dynamic_enum(name: str, values: List[Any]) -> Enum:
    return Enum(name, {str(v): v for v in values})


class SchemaModelMaker:
    def __init__(self):
        # cache of already-built custom dtype models
        self._custom_models: Dict[str, Type[BaseModel]] = {}
        # track what's currently being built to prevent recursive custom types
        self._building: set[str] = set()
        # name -> CustomDTypeSpec
        self._custom_dtype_specs: Dict[str, CustomDTypeSpec] = {}

    # ------------------------------------------------------------------ #
    # dtype helpers
    # ------------------------------------------------------------------ #

    def _get_primitive_dtype(self, dtype_name: str) -> Union[type, None]:
        """
        Map schema dtype strings to Python primitive types.
        Returns the Python type if it's a primitive, otherwise None.
        """
        lower = dtype_name.lower()
        if lower in {"string", "str"}:
            return str
        if lower in {"integer", "int"}:
            return int
        if lower in {"number", "float"}:
            return float
        if lower in {"boolean", "bool"}:
            return bool
        return None

    def _get_dtype(self, dtype_name: str) -> type:
        # primitive mapping
        primitive = self._get_primitive_dtype(dtype_name)
        if primitive is not None:
            return primitive

        # bbox
        if dtype_name.lower() == "bbox":
            return Bbox

        # custom model already built
        if dtype_name in self._custom_models:
            return self._custom_models[dtype_name]

        # detect recursion
        if dtype_name in self._building:
            raise ValueError(f"Recursive dtype definition is not allowed: {dtype_name}")

        # custom dtype spec must exist
        if dtype_name not in self._custom_dtype_specs:
            raise ValueError(f"dtype {dtype_name!r} not supported")

        # build custom model from CustomDTypeSpec
        self._building.add(dtype_name)
        custom_spec = self._custom_dtype_specs[dtype_name]  # CustomDTypeSpec
        model = self._build_model(custom_spec)
        self._custom_models[dtype_name] = model
        self._building.remove(dtype_name)
        return model

    # ------------------------------------------------------------------ #
    # core model builder
    # ------------------------------------------------------------------ #

    def _build_model(
        self,
        specification: Union[SchemaConfig, CustomDTypeSpec],
    ) -> Type[BaseModel]:
        """
        Build a Pydantic model from either:
        - a SchemaConfig (top-level schema), or
        - a CustomDTypeSpec (custom dtype).
        """
        model_name = specification.name  # keep model name separate

        model_spec_dict: Dict[str, Any] = {}
        for field in specification.fields:
            field_name: str = field.name
            field_spec: DtypeSpec = field.specification

            # resolve base dtype
            dtype = self._get_dtype(field_spec.dtype)

            # allowed_values -> Enum (applied at dim=0 level)
            if field_spec.allowed_values:
                allowed_values = [dtype(v) for v in field_spec.allowed_values]
                enum = create_dynamic_enum(f"{model_name}_{field_name}_enum", allowed_values)
                dtype = enum

            # expand dims
            dim = field_spec.dim
            if dim == 0:
                pass  # scalar
            elif dim == 1:
                dtype = List[dtype]
            elif dim == 2:
                dtype = List[List[dtype]]
            else:
                raise ValueError("dim > 2 not supported for now")

            # optional -> default None, otherwise required
            default = None if field_spec.optional else ...

            model_spec_dict[field_name] = (dtype, default)

        model = create_model(model_name, __config__={"extra": "forbid"}, **model_spec_dict)
        return model

    # ------------------------------------------------------------------ #
    # public API
    # ------------------------------------------------------------------ #

    def make(self, config: SchemaConfig) -> Type[BaseModel]:
        """
        Build the root model from a SchemaConfig. This will also build
        any custom dtypes on demand.
        """
        # reset caches
        self._custom_models = {}
        self._building = set()
        self._custom_dtype_specs = {}

        # register custom dtype specs
        for custom_dtype in config.custom_dtypes:
            self._custom_dtype_specs[custom_dtype.name] = custom_dtype

        # build root model
        return self._build_model(config)