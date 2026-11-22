"""
Schema validation module
"""

from typing import Dict, List, Tuple

try:
    import jsonschema
    JSONSCHEMA_AVAILABLE = True
except ImportError:
    JSONSCHEMA_AVAILABLE = False

try:
    from pydantic import BaseModel, ValidationError
    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False


class SchemaValidator:
    """Validates datapoints against schemas."""
    
    def __init__(self):
        self.schemas: Dict[str, Dict] = {}
        self.pydantic_models: Dict[str, type] = {}
    
    def add_json_schema(self, name: str, schema: Dict):
        self.schemas[name] = schema
    
    def add_pydantic_model(self, name: str, model: type):
        self.pydantic_models[name] = model
    
    def validate_json_schema(self, datapoint: Dict, schema_name: str) -> Tuple[bool, List[str]]:
        if not JSONSCHEMA_AVAILABLE:
            return False, ["jsonschema not installed"]
        
        if schema_name not in self.schemas:
            return False, [f"Schema '{schema_name}' not found"]
        
        try:
            jsonschema.validate(datapoint, self.schemas[schema_name])
            return True, []
        except jsonschema.ValidationError as e:
            return False, [str(e.message)]
    
    def validate_pydantic(self, datapoint: Dict, model_name: str) -> Tuple[bool, List[str]]:
        if not PYDANTIC_AVAILABLE:
            return False, ["pydantic not installed"]
        
        if model_name not in self.pydantic_models:
            return False, [f"Model '{model_name}' not found"]
        
        try:
            model = self.pydantic_models[model_name]
            model(**datapoint)
            return True, []
        except ValidationError as e:
            return False, [str(err) for err in e.errors()]
