import inspect
from typing import Any, Dict, Type, Tuple, Callable, Optional
from uuid import UUID

from weaviate import WeaviateClient

from .weavitae_reference import Reference_Type, Reference

def validate_method_params(method: Callable, params: Dict[str, Any]) -> Optional[Type]:
    """
    Validate that `params` contain all required arguments with correct types for `method`.
    Returns the expected return type if specified in the function signature.

    Args:
        method (callable): The method to validate.
        params (Dict[str, Any]): The parameters to validate. Keys are parameter names.

    Returns:
        Type: The expected return type of the method. None if not specified.
    """
    
    # Get function signature
    sig = inspect.signature(method)

    # Extract required parameters and their expected types
    required_params = {
        k: v.annotation
        for k, v in sig.parameters.items()
        if v.default == inspect.Parameter.empty and not (k == 'self' or k == 'cls')  # Only required params
    }

    # Check for missing required parameters
    missing_params = [param for param in required_params if param not in params]
    if missing_params:
        raise ValueError(f"Missing required parameters: {missing_params}")

    # Validate types if type hints exist
    for param, expected_type in required_params.items():
        if expected_type is not inspect.Parameter.empty and not isinstance(params[param], expected_type):
            raise TypeError(f"Parameter '{param}' should be {expected_type}, got {type(params[param])}")

    # Extract return type if specified
    return_type = sig.return_annotation
    return return_type if return_type is not inspect.Signature.empty else None

def compare_instance(instance_a: Any, instance_b: Any) -> bool:

    #Try get an uuid
    uuid_a = None
    uuid_b = None

    if hasattr(instance_a, 'get_uuid'):
        uuid_a = instance_a.get_uuid()
    elif isinstance(instance_a, UUID):
        uuid_a = instance_a
    if hasattr(instance_b, 'get_uuid'):
        uuid_b = instance_b.get_uuid()
    elif isinstance(instance_b, UUID):
        uuid_b = instance_b

    #Check equality
    if uuid_a and uuid_b:
        return uuid_a == uuid_b
    else:
        return instance_a == instance_b

class _Handle_Referenzes():

    @staticmethod
    def _get_relevant_referenzes(client:WeaviateClient, reference_collection=None) -> Dict[str, list[str]]:
        """Get all references in the Weaviate schema that point to a specific collection.
        
        Args:
            client (WeaviateClient): The Weaviate client to use.
            target_collection (str): The name of the target collection to search for. If None, all references are returned.

        Returns:
            Dict[str, List[str]]: A dictionary of collection names and their references.
        """
    
        shema = client.collections.list_all()
        refs = {}
        rel_refs = []

        for col_name, col in shema.items():

            if reference_collection:
                rel_refs = [ref.name for ref in col.references if reference_collection in ref.target_collections]
            else:
                rel_refs = [ref.name for ref in col.references]

            if rel_refs and rel_refs != []:
                refs[col_name] = rel_refs

        return refs

    @staticmethod
    def _generate_graphql_query_for_referenzes(referenzes:Dict[str, list[str]], reference_collection:str, to_uuid:UUID) -> dict[str, str]:
        """Generate a GraphQL query string to retrieve all referenzes.
        
        Args:
            referenzes (Dict[str, List[str]]): A dictionary of collection names and their references.

        Returns:
            str: The generated GraphQL query string.
        """
    
        graphql_queries = {}
        refs = referenzes


        nl = ',\n'

        for col, col_refs in refs.items():
            operands = []
            outputs = []

            #Generate an operand per ref
            for ref in col_refs:
                q = f"""
                {{
                    path: ["{ref}", "{reference_collection}", "id"],
                    operator: Equal,
                    valueText: "{to_uuid}"
                }}"""

                o = f"""
                    {ref}{{
                        ... on Author {{
                            _additional {{
                            id
                            }}
                        }}
                        }}
                        """

                operands.append(q)
                outputs.append(o)

            #Generate Query per Collection
            output = '\n'.join(outputs)
            col_q = f"""
            {{
                Get {{
                    {col}(
                        where : {{
                            operator: Or
                            operands : [ {nl.join(operands)}
                            ]
                        }}
                    ){{
                        _additional {{
                            id
                        }}
                        {output}
                        
                    }}

                }}      
            }}"""

            graphql_queries[col] = col_q

        return graphql_queries
    
    @staticmethod
    def get_referenzes(client:WeaviateClient, reference_collection:str, to_uuid:UUID) -> dict:

        referenzes = {}

        #Get all relevant referenzes
        refs = _Handle_Referenzes._get_relevant_referenzes(client, reference_collection)

        #Generate GraphQL Queries
        queries = _Handle_Referenzes._generate_graphql_query_for_referenzes(refs, reference_collection, to_uuid)

        #Execute Queries
        for col, query in queries.items():
            resp = client.graphql_raw_query(query)

            #Check if the collection is in the response #GEÄNDERT 08.04 THE
            if col not in resp.get.keys() or resp.get[col] == [] or resp.get[col] is None:
                continue

            referenzes[col] = {}

            for obj in resp.get[col]:
                referenzes[col][obj["_additional"]["id"]] = {}
                for key, prop in obj.items():
                    if key != "_additional" and prop:
                        
                        elements = [element["_additional"]["id"] for element in prop if element["_additional"]["id"] == to_uuid]
                        if elements and elements != []:
                            referenzes[col][obj["_additional"]["id"]][key] = elements

        return referenzes

    @staticmethod
    def _compare_single_reference(ref_a, ref_b):
        """Compare two references (SINGLE).
        Args:
            ref_a (Any): The first reference.
            ref_b (Any): The second reference.
        
        Returns:
            bool: True if they are equal, False otherwise.
        """

        if ref_a is None and ref_b is None:
            return True
        elif ref_a is None or ref_b is None:
            return False
        
        if not isinstance(ref_a, UUID) and not isinstance(ref_b, UUID):
            return ref_a.get_uuid() == ref_b.get_uuid()
        elif isinstance(ref_a, UUID) and not isinstance(ref_b, UUID):
            return ref_a == ref_b.get_uuid()
        elif isinstance(ref_b, UUID) and not isinstance(ref_a, UUID):
            return ref_b == ref_a.get_uuid()
        elif not isinstance(ref_a, UUID) and not isinstance(ref_b, UUID):
            return ref_a.get_uuid() == ref_b.get_uuid()
        else:
            return ref_a == ref_b

    @staticmethod
    def compare_references(ref_a, ref_b):
        """Compare two references (SINGLE or LIST).

        Args:
            ref_a (Any): The first reference.
            ref_b (Any): The second reference.
        Returns:
            bool: True if they are equal, False otherwise.
        """

        #Check for list
        if isinstance(ref_a, list) and isinstance(ref_b, list):
            if len(ref_a) != len(ref_b):
                return False

            for a, b in zip(ref_a, ref_b):
                if not _Handle_Referenzes._compare_single_reference(a, b):
                    return False
            return True
        elif isinstance(ref_a, list) and not isinstance(ref_b, list):
            return False
        elif not isinstance(ref_a, list) and isinstance(ref_b, list):
            return False
        else:
            #Check if both are UUIDs
            return _Handle_Referenzes._compare_single_reference(ref_a, ref_b)