from .base import ValidationRule
from typing import Any, Dict, List, Optional, Set, Union, Tuple, Type
from enum import Enum
from .basic import RequiredRule, ProhibitedRule, PresentRule, MissingRule, ExcludeRule
import re
import inspect
from collections.abc import Iterable

# =============================================
# CONDITIONAL VALIDATION RULES
# =============================================

class RequiredIfRule(RequiredRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if len(params) < 2 or len(params) % 2 != 0:
            return True
            
        conditions = list(zip(params[::2], params[1::2]))
        
        condition_met = False
        for other_field, expected_value in conditions:
            if not other_field or expected_value is None:
                continue
                
            actual_value = self.get_field_value(other_field, '')
            
            if actual_value == expected_value:
                condition_met = True
                break
            
        if not condition_met:
            return True
        
        return super().validate(field, value, params)
    
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
    
class ProhibitedIfRule(ProhibitedRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if len(params) < 2:
            return False
            
        other_field, other_value = params[0], params[1]
        actual_value = self.get_field_value(other_field, '')
        
        if actual_value != other_value:
            return True
            
        return super().validate(field, value, params)
    
class ProhibitedUnlessRule(ProhibitedRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if len(params) < 2:
            return False
            
        other_field, other_value = params[0], params[1]
        actual_value = self.get_field_value(other_field, '') 
        
        if actual_value == other_value:
            return True
            
        return super().validate(field, value, params)
    
class PresentIfRule(PresentRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if len(params) < 2:
            return False
        other_field, other_value = params[0], params[1]
        
        if self.get_field_value(other_field, None) == other_value:
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
        
class MissingIfRule(MissingRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if len(params) < 2:
            return False
        other_field, other_value = params[0], params[1]
        
        if self.get_field_value(other_field, None) == other_value:
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
    
class ExcludeIfRule(ExcludeRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        conditions = [(f.strip(), v.strip()) for f, v in zip(params[::2], params[1::2])]
        
        all_conditions_met = all(
            self.get_field_value(f) == v 
            for f, v in conditions
        )
        
        if all_conditions_met:
            return super().validate(field, value, params)
        return True
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :attribute field is excluded when {params[0]} is {params[1]}."

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