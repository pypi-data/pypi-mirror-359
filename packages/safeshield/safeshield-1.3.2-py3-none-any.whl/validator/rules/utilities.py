from .base import ValidationRule
from typing import Any, Dict, List, Optional, Set, Union, Tuple, Type
from .basic import AcceptedRule, DeclinedRule, ExcludeRule, RequiredRule, PresentRule, MissingRule, ProhibitedRule

class RequiredWithRule(RequiredRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if not params:
            return False
            
        if any(f in self.validator.data for f in params):
            return super().validate(field, value, params)
        return True

class RequiredWithAllRule(RequiredRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if not params:
            return False
            
        if all(f in self.validator.data for f in params):
            return not self.is_empty(value)
        return True
    
class RequiredWithoutRule(RequiredRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if not params:
            return False
            
        if any(f not in self.validator.data for f in params):
            return super().validate(field, value, params)
        return True
    
class RequiredWithoutAllRule(RequiredRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if not params:
            return False
            
        if all(f not in self.validator.data for f in params):
            return super().validate(field, value, params)
        return True
    
class PresentWithRule(PresentRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if not params:
            return False
        if any(self.get_field_value(param, None) is not None for param in params):
            return super().validate(field, value, params)
        
        return True
    
class PresentWithAllRule(PresentRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if not params:
            return False
        
        if all(self.get_field_value(param, None) is not None for param in params):
            return super().validate(field, value, params)
        
class MissingWithRule(MissingRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if not params:
            return False
        
        if any(self.get_field_value(param, None) is not None for param in params):
            return super().validate(field, value, params)
        
        return True
    
class MissingWithAllRule(MissingRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if not params:
            return False
        
        if all(self.get_field_value(param, None) is not None for param in params):
            return super().validate(field, value, params)
        
        return True

class ExcludeWithRule(ExcludeRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if any(not self.is_empty(self.get_field_value(param, None)) for param in params):
            return super().validate(field, value, params)
            
        return True
    
class ExcludeWithoutRule(ExcludeRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if any(self.is_empty(self.get_field_value(param, None)) for param in params):
            return super().validate(field, value, params)
            
        return True
    
class ProhibitedIfAcceptedRule(ProhibitedRule, AcceptedRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if not params:
            return False
        
        if AcceptedRule.validate(self, field, params[0], params):
            return super().validate(field, value, params)
        return True

class ProhibitedIfDeclinedRule(ProhibitedRule, DeclinedRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if not params:
            return False
        
        if DeclinedRule.validate(self, field, params[0], params):
            return super().validate(field, value, params)
        
        return True
    
class RequiredIfAcceptedRule(RequiredRule, AcceptedRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if not params:
            return False
        
        if AcceptedRule.validate(self, field, params[0], params):
            return super().validate(field, value, params)
        
        return True
    
class RequiredIfDeclinedRule(RequiredRule, DeclinedRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if not params:
            return False
        
        if DeclinedRule.validate(self, field, params[0], params):
            return super().validate(field, value, params)
        
        return True
    
class RequiredArrayKeysRule(ValidationRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if not isinstance(value, dict) or not params:
            return False
        return all(key in value for key in params)
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :attribute must contain all required keys: {', '.join(params)}"
