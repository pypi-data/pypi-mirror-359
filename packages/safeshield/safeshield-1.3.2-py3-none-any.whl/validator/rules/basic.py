from .base import ValidationRule
from typing import Any, Dict, List, Optional, Set, Union, Tuple, Type

# =============================================
# BASIC VALIDATION RULES
# =============================================

class AnyOfRule(ValidationRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if not params:
            return False
        return any(self.get_field_value(param, param) == value for param in params)
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :attribute must be one of: {', '.join(params)}"

class BailRule(ValidationRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        self.validator._stop_on_first_failure = True
        return True
    
    def message(self, field: str, params: List[str]) -> str:
        return ""

class RequiredRule(ValidationRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        return not self.is_empty(value)
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :attribute field is required."

class ProhibitedRule(ValidationRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        return self.is_empty(value)
    
    def message(self, field: str, params: List[str]) -> str:
        return "The :attribute field is must be empty."
    
class NullableRule(ValidationRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        return True
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :attribute may be null."

class FilledRule(ValidationRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        return value not in ('', None)
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :attribute field must have a value."

class PresentRule(ValidationRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        return field in self.validator.data
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :attribute field must be present."
    
class MissingRule(ValidationRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        return value is None
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :attribute field must be missing."
    
class ProhibitsRule(ValidationRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if not params or value is None:
            return True
        return all(self.get_field_value(param, param) in (None, 'None') for param in params)
    
    def message(self, field: str, params: List[str]) -> str:
        return f"When :attribute is present, {', '.join(params)} must be absent."
    
class AcceptedRule(ValidationRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        value = self.get_field_value(value, value)
        
        if isinstance(value, str):
            return value.lower() in ['yes', 'on', '1', 1, True, 'true', 'True']
        if isinstance(value, int):
            return value == 1
        if isinstance(value, bool):
            return value
        return False
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :attribute must be accepted."

class DeclinedRule(ValidationRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        value = self.get_field_value(value, value)
        
        if isinstance(value, str):
            return value.lower() in ['no', 'off', '0', 0, False, 'false', 'False']
        if isinstance(value, int):
            return value == 0
        if isinstance(value, bool):
            return not value
        return False
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :attribute must be declined."

class SometimesRule(ValidationRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        return True
    
    def message(self, field: str, params: List[str]) -> str:
        return ""
    
class ExcludeRule(ValidationRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        self.validator._is_exclude = True
        
        return True
    
    def message(self, field: str, params: List[str]) -> str:
        return ""

class UniqueRule(ValidationRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if not params or not hasattr(self.validator, 'db_manager') or not self.validator.db_manager:
            return False
            
        table = params[0]
        column = field if len(params) == 1 else params[1]
        
        try:
            ignore_id = None
            if len(params) > 2 and params[2].startswith('ignore:'):
                ignore_field = params[2].split(':')[1]
                ignore_id = self.get_field_value(ignore_field) 
            return self.validator.db_manager.is_unique(table, column, value, ignore_id)
        except Exception as e:
            print(f"Database error in UniqueRule: {e}")
            return False
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :attribute has already been taken."

class ExistsRule(ValidationRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if not params or not hasattr(self.validator, 'db_manager') or not self.validator.db_manager:
            return False
            
        table = params[0]
        column = field if len(params) == 1 else params[1]
        
        try:
            return self.validator.db_manager.exists(table, column, value)
        except Exception as e:
            print(f"Database error in ExistsRule: {e}")
            return False
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The selected :attribute is invalid."

class ConfirmedRule(ValidationRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        confirmation_field = f"{field}_confirmation"
        
        return value == self.get_field_value(confirmation_field, '') 
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :attribute confirmation does not match."

class SameRule(ValidationRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if not params:
            return False
        return value == self.get_field_value(params[0]) 
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :attribute and {params[0]} must match."

class DifferentRule(ValidationRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if not params:
            return False
        return value != self.get_field_value(params[0]) 
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :attribute and {params[0]} must be different."
    
class RegexRule(ValidationRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if not params or not isinstance(value, str):
            return False
        try:
            return bool(re.fullmatch(params[0], value))
        except re.error:
            return False
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :attribute format is invalid."

class NotRegexRule(ValidationRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if not params or not isinstance(value, str):
            return True
        print(not bool(re.search(params[0], value)))
        try:
            return not bool(re.search(params[0], value))
        except re.error:
            return True
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :attribute format is invalid."

class InRule(ValidationRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        allowed_values = self._parse_option_values(field, params)
        return (str(value) in allowed_values or value in allowed_values)

    def message(self, field: str, params: List[str]) -> str:
        allowed_values = self._parse_option_values(field, params)
        return f"The selected :attribute must be in : {', '.join(map(str, allowed_values))}"

class NotInRule(ValidationRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        not_allowed_values = self._parse_option_values(field, params)
        return str(value) not in not_allowed_values
    
    def message(self, field: str, params: List[str]) -> str:
        not_allowed_values = self._parse_option_values(field, params)
        return f"The selected :attribute must be not in : {', '.join(map(str, not_allowed_values))}"
    
class EnumRule(ValidationRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        allowed_values = self._parse_option_values(field, params)
        return (str(value) in allowed_values or value in allowed_values)

    def message(self, field: str, params: List[str]) -> str:
        allowed_values = self._parse_option_values(field, params)
        return f"The :attribute must be one of: {', '.join(map(str, allowed_values))}"