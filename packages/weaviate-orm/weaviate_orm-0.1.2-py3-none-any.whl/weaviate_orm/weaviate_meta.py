from abc import ABCMeta
from typing import Any
import inspect
from inspect import Parameter, Signature

# Replace these imports with your actual module paths
from .weavitae_reference import Reference
from .weaviate_property import Property
from .weaviate_utility import validate_method_params

from weaviate.classes.config import (
    Property as WeaviateProperty,
    ReferenceProperty as WeaviateReferenceProperty,
    Configure

)

from weaviate.collections.collections.sync import _Collections


class Weaviate_Meta(ABCMeta):
    _weaviate_schema: dict[str, Any]  # For type checkers
    _properties: list[Property]
    _references: list[Reference]

    """
    Metaclass that dynamically extracts model attributes to build Weaviate schemas.

    - If an attribute is an instance of `Property`, we treat it as a scalar property.
    - If it's a `Reference`, we treat it as a cross-reference property.
    - If a class variable `__collection_name__` is present, we use that name
      as the Weaviate class name instead of the Python class name.

    We also look for specific config attribute names (like "vectorizer_config")
    to store in the final schema dict.
    """

    def __new__(mcs, name, bases, dct):
        """
        Create the new class, injecting a `_weaviate_schema` dict if `name != "Base_Model"`.
        """

        cls = super().__new__(mcs, name, bases, dct)

        properties = []
        references = []

        # Skip schema building for a base class named "Base_Model".
        if name != "Base_Model":
            # Decide on the Weaviate class/collection name
            collection_name = dct.get("__collection_name__", name)

            # Prepare the schema structure
            weaviate_collection = {
                "name": collection_name,
                "description": dct.get("description", ""),
                "properties": [],
                "references": [],
                "vectorizer_config": Configure.Vectorizer.none(),
                "vector_index_config": None,
                "inverted_index_config": None,
                #"rerank_config": None,
                "generative_config": None
            }

            # Inspect every attribute in the class dict
            for attr_name, attr_value in cls.__dict__.items():
                if isinstance(attr_value, Property):
                    weaviate_collection["properties"].append(
                        attr_value._get_weaviate_property()
                    )
                    properties.append(attr_value)

                elif isinstance(attr_value, Reference):
                    weaviate_collection["references"].append(
                        attr_value._get_weaviate_reference()
                    )
                    references.append(attr_value)

                # 3) If the attr_name matches a top-level config key, store the value
                if attr_name in weaviate_collection and attr_value is not None:
                    weaviate_collection[attr_name] = attr_value

            # Check params 
            validate_method_params(_Collections.create, weaviate_collection)

            # Attach the generated schema to the class
            cls._weaviate_schema = weaviate_collection
            cls._properties = properties
            cls._references = references

            # Create and attach a dynamic __init__ that receives each property/ref as a KW-arg
            cls.__init__ = mcs._make_dynamic_init(properties=properties, references=references)


        
        return cls
    
    @staticmethod
    def _make_dynamic_init(properties:list[Property], references:list[Reference]): #TODO: Rewrite this function!!!
        """
        Build a function with a dynamic signature for __init__.
        Each `Property` or `Reference` becomes a keyword parameter (with default if any).
        """
        # We'll build an inspect.Signature that has parameters for each property/ref.
        parameters = []

        # 0) Add the `self` parameter
        #parameters.append(
        #    Parameter(
        #        name="self",
        #        kind=Parameter.POSITIONAL_ONLY
        #    )
        #)

        # 1) Create parameters for each Property
        for prop in properties:
            # If the property has a default, use that; otherwise Parameter.empty
            default_val = prop.default if (prop.default is not None) else Parameter.empty
            kind = Parameter.POSITIONAL_OR_KEYWORD

            if not prop.name:
                raise ValueError("Property name is not set.")

            parameters.append(
                Parameter(
                    name=prop.name,
                    kind=kind,
                    default=default_val,
                    annotation=prop.cast_type
                )
            )

        # 2) Create parameters for each Reference
        for ref in references:
            # Typically references won't have "default" in the same sense, but if you do:
            default_val = None if not ref.required else Parameter.empty

            if not ref.name:
                raise ValueError("Reference field name is not set.")
            
            parameters.append(
                Parameter(
                    name=ref.name,
                    kind=Parameter.POSITIONAL_OR_KEYWORD,
                    default=default_val,
                    annotation=ref.target_collection_name  # Get type from the target collection name -> str to type
                )
            )

        # Build a signature with the above parameters
        sig = Signature(parameters=parameters)

        # Now define the actual function that uses that signature at runtime.
        def dynamic_init(self, *args, **kwargs):
            # Bind arguments to the signature -> enforces correct usage
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()

            # bound_args.arguments is an OrderedDict of (param_name -> value)
            # first argument is `self`, skip it when setting attributes
            for param_name, arg_val in list(bound_args.arguments.items()):
                if(param_name in self.__dict__):
                    raise ValueError(f"Parameter '{param_name}' already exists in the class.")
                setattr(self, param_name, arg_val)

            #Set uuid
            self.generate_uuid()

        # Attach our custom signature to the function object
        dynamic_init.__signature__ = sig
        # For better debugging, give it a nice name:
        dynamic_init.__name__ = "__init__"

        return dynamic_init
