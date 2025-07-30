from .base import Rule
from typing import Any, Dict, List, Optional, Set, Union, Tuple, Type

# =============================================
# BASIC VALIDATION RULES
# =============================================

class AnyOfRule(Rule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        self._last_failed_rules = []  # Reset failed rules
        
        for i, rule_set in enumerate(params):
            if isinstance(rule_set, str):
                rule_set = [rule_set]
            
            from validator import Validator
            
            temp_validator = Validator(
                {field: value},
                {field: rule_set},
                db_config=getattr(self._validator, 'db_config', None)
            )
            
            if temp_validator.validate():
                return True
            else:
                self._last_failed_rules.append({
                    'rules': rule_set,
                    'errors': temp_validator.errors.get(field, [])
                })
                
        return False
        
    def message(self, field: str, params: List[str]) -> str:
        if not self._last_failed_rules:
            return f"The :attribute field is invalid."
        
        error_messages = []
        
        for i, failed in enumerate(self._last_failed_rules, 1):
            rules_str = "|".join(
                r if isinstance(r, str) else getattr(r, 'rule_name', str(r))
                for r in failed['rules']
            )
            
            sub_errors = []
            for j, err_msg in enumerate(failed['errors'], 1):
                sub_errors.append(f"  {j}. {err_msg}")
            
            error_messages.append(
                f"Option {i} (Rules: {rules_str}):\n" + 
                "\n".join(sub_errors)
            )
        
        return (
            f"The :attribute must satisfy at least one of these conditions:\n" +
            "\n".join(error_messages)
        )

class BailRule(Rule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        self.validator._stop_on_first_failure = True
        return True
    
    def message(self, field: str, params: List[str]) -> str:
        return ""

class RequiredRule(Rule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        return not self.is_empty(value)
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :attribute field is required."

class ProhibitedRule(Rule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        return self.is_empty(value)
    
    def message(self, field: str, params: List[str]) -> str:
        return "The :attribute field is must be empty."
    
class NullableRule(Rule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        return True
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :attribute may be null."

class FilledRule(Rule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        return value not in ('', None)
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :attribute field must have a value."

class PresentRule(Rule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        return field in self.validator.data
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :attribute field must be present."
    
class MissingRule(Rule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        return value is None
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :attribute field must be missing."
    
class ProhibitsRule(Rule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if not params or value is None:
            return True
        return all(self.get_field_value(param, param) in (None, 'None') for param in params)
    
    def message(self, field: str, params: List[str]) -> str:
        return f"When :attribute is present, {', '.join(params)} must be absent."

class SometimesRule(Rule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if value is None:
            self.validator._field_to_exclude.append(field)
            
        return True
    
    def message(self, field: str, params: List[str]) -> str:
        return ""
    
class ExcludeRule(Rule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        self.validator._field_to_exclude.append(field)
        
        return True
    
    def message(self, field: str, params: List[str]) -> str:
        return ""