from .base import Rule
from typing import Any, Dict, List, Optional, Set, Union, Tuple, Type

class BooleanRule(Rule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if isinstance(value, bool):
            return True
        if isinstance(value, str):
            return value.lower() in ['true', 'false', '1', '0', 'yes', 'no', 'on', 'off']
        if isinstance(value, int):
            return value in [0, 1]
        return False
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :attribute field must be true or false."
    
class AcceptedRule(Rule):
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

class DeclinedRule(Rule):
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
    
class AcceptedIfRule(AcceptedRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        condition_met = False

        if len(params) == 1 and callable(params[0]):
            condition_met = params[0](self.validator.data)
        elif len(params) == 1 and isinstance(params[0], bool):
            condition_met = params[0]
        else:  
            conditions = list(zip(params[::2], params[1::2]))
            
            for other_field, expected_value in conditions:
                if not other_field or expected_value is None:
                    continue
                    
                actual_value = self.get_field_value(other_field, '')
                
                if actual_value == expected_value:
                    condition_met = True
                    break
            
        if condition_met:
            return super().validate(field, value, params)
        
        return True
    
class AcceptedUnlessRule(AcceptedRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if len(params) < 2:
            return False
            
        other_field, other_value = params[0], params[1]
        actual_value = self.get_field_value(other_field, '') 
        
        if actual_value == other_value:
            return True
            
        return super().validate(field, value, params)
    
class AcceptedAllIfRule(AcceptedRule):
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
    
class DeclinedIfRule(DeclinedRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        condition_met = False
                
        if len(params) == 1 and callable(params[0]):
            condition_met = params[0](self.validator.data)
        elif len(params) == 1 and isinstance(params[0], bool):
            condition_met = params[0]
        else:  
            conditions = list(zip(params[::2], params[1::2]))
            
            for other_field, expected_value in conditions:
                if not other_field or expected_value is None:
                    continue
                    
                actual_value = self.get_field_value(other_field, '')
                
                if actual_value == expected_value:
                    condition_met = True
                    break
                
            if condition_met:
                return super().validate(field, value, params)
            
        return True
    
class DeclinedUnlessRule(DeclinedRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if len(params) < 2:
            return False
            
        other_field, other_value = params[0], params[1]
        actual_value = self.get_field_value(other_field, '') 
        
        if actual_value == other_value:
            return True
            
        return super().validate(field, value, params)
    
class DeclinedAllIfRule(DeclinedRule):
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