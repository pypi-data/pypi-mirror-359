from .base import Rule
from typing import Any, Dict, List, Optional, Set, Union, Tuple, Type

class ArrayRule(Rule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        self._missing_keys = params
        
        if params:
            params = self._parse_option_values(self.rule_name, params)
            if not isinstance(value, dict):
                return False

            missing = [param for param in params if param not in value]
            self._missing_keys = missing
            return len(missing) == 0

        return isinstance(value, (list, tuple, set))

    def message(self, field: str, params: List[str]) -> str:
        if params:
            return f"The :attribute must contain the keys: {', '.join(self._missing_keys)}."
        return f"The :attribute must be an array."
    
class DistinctRule(Rule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if not isinstance(value, (list, tuple, set)):
            return False
            
        ignore_case = 'ignore_case' in params
        
        seen = set()
        for item in value:
            compare_val = item
            
            if ignore_case and isinstance(item, str):
                compare_val = item.lower()
            
            if compare_val in seen:
                return False
            seen.add(compare_val)
            
        return True
    
    def message(self, field: str, params: List[str]) -> str:
        base_msg = f"The :attribute must contain unique values"
        
        if 'ignore_case' in params:
            return f"{base_msg} (case insensitive)"
        else:
            return f"{base_msg} (strict comparison)"
    
class InArrayRule(Rule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if not params:
            return False
            
        return str(value) in params
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :attribute must be one of: {', '.join(params)}"
    
class InArrayKeysRule(Rule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if not params or not isinstance(value, dict):
            return False
            
        return any(key in value for key in params)
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :attribute must contain at least one of these keys: {', '.join(params)}"