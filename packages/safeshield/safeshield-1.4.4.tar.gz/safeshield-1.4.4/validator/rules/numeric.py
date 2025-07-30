from .base import Rule
from typing import Any, Dict, List, Optional, Set, Union, Tuple, Type
import decimal

class NumericRule(Rule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if isinstance(value, (int, float)):
            return True
        if not isinstance(value, str):
            return False
        return value.replace('.', '', 1).isdigit()
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :attribute must be a number."
    
class IntegerRule(Rule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if isinstance(value, int):
            return True
        if not isinstance(value, str):
            return False
        return value.isdigit()
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :attribute must be an integer."

class DigitsRule(Rule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if not params or not isinstance(value, str):
            return False
            
        try:
            digits = int(params[0])
        except ValueError:
            return False
            
        return value.isdigit() and len(value) == digits
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :attribute must be {params[0]} digits."

class DigitsBetweenRule(Rule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if len(params) < 2 or not isinstance(value, str):
            return False
            
        try:
            min_digits = int(params[0])
            max_digits = int(params[1])
        except ValueError:
            return False
            
        return value.isdigit() and min_digits <= len(value) <= max_digits
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :attribute must be between {params[0]} and {params[1]} digits."
    
class DecimalRule(Rule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        try:
            decimal.Decimal(str(value))
            return True
        except (decimal.InvalidOperation, TypeError, ValueError):
            return False
    
    def message(self, field: str, params: List[str]) -> str:
        return "The :attribute must be a decimal number."

class GreaterThanRule(Rule):
    _name = 'gt'
    
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if len(params) < 1:
            return False
        
        try:
            threshold = decimal.Decimal(params[0])
            numeric_value = decimal.Decimal(str(value))
            return numeric_value > threshold
        except (decimal.InvalidOperation, TypeError, ValueError):
            return False
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :attribute must be greater than {params[0]}."

class GreaterThanOrEqualRule(Rule):
    _name = 'gte'
    
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if len(params) < 1:
            return False
        
        try:
            threshold = decimal.Decimal(params[0])
            numeric_value = decimal.Decimal(str(value))
            return numeric_value >= threshold
        except (decimal.InvalidOperation, TypeError, ValueError):
            return False
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :attribute must be greater than or equal to {params[0]}."

class LessThanRule(Rule):
    _name = 'lt'
    
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if len(params) < 1:
            return False
        
        try:
            threshold = decimal.Decimal(params[0])
            numeric_value = decimal.Decimal(str(value))
            return numeric_value < threshold
        except (decimal.InvalidOperation, TypeError, ValueError):
            return False
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :attribute must be less than {params[0]}."

class LessThanOrEqualRule(Rule):
    _name = 'lte'
    
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if len(params) < 1:
            return False
        
        try:
            threshold = decimal.Decimal(params[0])
            numeric_value = decimal.Decimal(str(value))
            return numeric_value <= threshold
        except (decimal.InvalidOperation, TypeError, ValueError):
            return False
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :attribute must be less than or equal to {params[0]}."

class MaxDigitsRule(Rule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if len(params) < 1:
            return False
        
        try:
            max_digits = int(params[0])
            numeric_value = decimal.Decimal(str(value))
            str_value = str(numeric_value).replace("-", "")
            if '.' in str_value:
                str_value = str_value.replace(".", "")
            return len(str_value) <= max_digits
        except (decimal.InvalidOperation, TypeError, ValueError):
            return False
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :attribute must not exceed {params[0]} digits."

class MinDigitsRule(Rule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if len(params) < 1:
            return False
        
        try:
            min_digits = int(params[0])
            numeric_value = decimal.Decimal(str(value))
            str_value = str(numeric_value).replace("-", "")
            if '.' in str_value:
                str_value = str_value.replace(".", "")
            return len(str_value) >= min_digits
        except (decimal.InvalidOperation, TypeError, ValueError):
            return False
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :attribute must have at least {params[0]} digits."

class MultipleOfRule(Rule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if not params:
            return False
            
        try:
            divisor = float(params[0])
            if divisor == 0:
                return False
            num = float(value)
            return num % divisor == 0
        except (ValueError, TypeError):
            return False
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :attribute must be a multiple of {params[0]}."