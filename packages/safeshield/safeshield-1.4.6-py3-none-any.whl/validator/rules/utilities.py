from .base import Rule
from typing import Any, Dict, List, Optional, Set, Union, Tuple, Type
from .basic import *
from .boolean import AcceptedRule, DeclinedRule

class RequiredIfRule(RequiredRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if len(params) == 1 and callable(params[0]):
            condition_met = params[0](self.validator.data)
        elif len(params) == 1 and isinstance(params[0], bool):
            condition_met = params[0]
        else:  
            conditions = list(zip(params[::2], params[1::2]))
            
            condition_met = any(
                str(self.get_field_value(field, '')) == str(expected_value)
                for field, expected_value in conditions
                if field and expected_value is not None
            )
                
        if condition_met:
            return super().validate(field, value, params)
        
        return True
    
class RequiredUnlessRule(RequiredRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if len(params) < 2:
            return False
            
        other_field, other_value = params[0], params[1]
        actual_value = self.get_field_value(other_field, '') 
        
        if actual_value == other_value:
            return True
            
        return super().validate(field, value, params)
    
class RequiredAllIfRule(RequiredRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if len(params) < 2:
            return False
            
        conditions = [(f.strip(), v.strip()) for f, v in zip(params[::2], params[1::2])]
        
        all_conditions_met = all(
            self.get_field_value(f) == v 
            for f, v in conditions
        )
        
        if not all_conditions_met:
            return True
            
        return super().validate(field, value, params)
    
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
    
class RequiredArrayKeysRule(Rule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if not isinstance(value, dict) or not params:
            return False
        return all(key in value for key in params)
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :attribute must contain all required keys: {', '.join(params)}"
    
class ProhibitedIfRule(ProhibitedRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if len(params) == 1 and callable(params[0]):
            condition_met = params[0](self.validator.data)
        elif len(params) == 1 and isinstance(params[0], bool):
            condition_met = params[0]
        else:    
            other_field, other_value = params[0], params[1]
            actual_value = self.get_field_value(other_field, '')
        
            condition_met = actual_value == other_value
        
        if condition_met:
            return super().validate(field, value, params)
        return True            
    
class ProhibitedUnlessRule(ProhibitedRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if len(params) < 2:
            return False
            
        other_field, other_value = params[0], params[1]
        actual_value = self.get_field_value(other_field, '') 
        
        if actual_value == other_value:
            return True
            
        return super().validate(field, value, params)
    
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
    
class PresentIfRule(PresentRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        condition_met = False
        
        if len(params) == 1 and callable(params[0]):
            condition_met = params[0](self.validator.data)
        elif len(params) == 1 and isinstance(params[0], bool):
            condition_met = params[0]
        else:
            conditions = list(zip(params[::2], params[1::2]))
            for other_field, expected_value in conditions:
                if self.get_field_value(other_field, None) == expected_value:
                    condition_met = True
                    break
            
        if condition_met:
            return super().validate(field, value, params)
        
        return True
    
class PresentUnlessRule(PresentRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if len(params) < 2:
            return False
        other_field, other_value = params[0], params[1]
        
        if self.get_field_value(other_field, None) != other_value:
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

class MissingIfRule(MissingRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        condition_met = False
        
        if len(params) == 1 and callable(params[0]):
            condition_met = params[0](self.validator.data)
        elif len(params) == 1 and isinstance(params[0], bool):
            condition_met = params[0]
        else:
            conditions = list(zip(params[::2], params[1::2]))
            for other_field, expected_value in conditions:
                if self.get_field_value(other_field, None) == expected_value:
                    condition_met = True
                    break
            
        if condition_met:
            return super().validate(field, value, params)
        
        return True
    
class MissingUnlessRule(MissingRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if len(params) < 2:
            return False
        other_field, other_value = params[0], params[1]
        if self.get_field_value(other_field, None) != other_value:
            return super().validate(field, value, params)

        return True
            
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
    
class IncludeIfRule(ExcludeRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if len(params) == 1 and callable(params[0]):
            condition_met = params[0](self.validator.data)
        elif len(params) == 1 and isinstance(params[0], bool):
            condition_met = params[0]
        else:
            conditions = list(zip(params[::2], params[1::2]))
            condition_met = all(
                str(self.get_field_value(f)) == str(v) 
                for f, v in conditions
            )
        
        if not condition_met:
            return super().validate(field, value, params)
        return True
    
class ExcludeIfRule(ExcludeRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if len(params) == 1 and callable(params[0]):
            condition_met = params[0](self.validator.data)
        elif len(params) == 1 and isinstance(params[0], bool):
            condition_met = params[0]
        else:
            conditions = list(zip(params[::2], params[1::2]))
            condition_met = all(
                str(self.get_field_value(f)) == str(v) 
                for f, v in conditions
            )
        
        if condition_met:
            return super().validate(field, value, params)
        return True

class ExcludeUnlessRule(ExcludeRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        conditions = [(f.strip(), v.strip()) for f, v in zip(params[::2], params[1::2])]
        
        all_conditions_met = all(
            self.get_field_value(f) == v 
            for f, v in conditions
        )
        
        if not all_conditions_met:
            return super().validate(field, value, params)
            
        return True
            
    def message(self, field: str, params: List[str]) -> str:
        return f"The :attribute field is excluded unless {params[0]} is {params[1]}."

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
