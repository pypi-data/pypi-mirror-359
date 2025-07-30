from .base import Rule
from typing import Any, Dict, List, Optional, Set, Union, Tuple, Type
from datetime import datetime
import zoneinfo
from dateutil.parser import parse

class DateRule(Rule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if not isinstance(value, str):
            return False
            
        try:
            parse(value)
            return True
        except ValueError:
            return False
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :attribute is not a valid date."

class DateEqualsRule(Rule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if not params or not isinstance(value, str):
            return False
        
        try:
            date1 = parse(value)
            
            params = list(params)
            params[0] = self.get_field_value(params[0], params[0])
            
            date2 = parse(params[0])
            return date1 == date2
        except ValueError as e:
            return False
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :attribute must be equal to {params[0]}."
    
class AfterRule(Rule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if not params or len(params) < 1:
            return False
            
        try:
            # Parse input date
            if isinstance(value, str):
                date_value = parse(value)
            elif isinstance(value, datetime):
                date_value = value
            else:
                return False
                
            
            params = list(params)# Parse comparison date
            params[0] = self.get_field_value(params[0], params[0])
            compare_date = parse(params[0])
            
            return date_value > compare_date
            
        except (ValueError, TypeError):
            return False
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :attribute must be after {params[0]}"
    
class AfterOrEqualRule(Rule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if not params or len(params) < 1:
            return False
        try:
            if isinstance(value, str):
                date_value = parse(value)
            elif isinstance(value, datetime):
                date_value = value
            else:
                return False
            
            params = list(params)
            params[0] = self.get_field_value(params[0], params[0])
            compare_date = parse(params[0])
            
            return date_value >= compare_date
            
        except (ValueError, TypeError) as e:
            return False
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :attribute must be after or equal to {params[0]}"
    
class BeforeRule(Rule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if not params or len(params) < 1:
            return False
        
        value = self.get_field_value(value, value)
    
        try:
            if isinstance(value, str):
                date_value = parse(value)
            elif isinstance(value, datetime):
                date_value = value
            else:
                return False
            
            params = list(params)
            params[0] = self.get_field_value(params[0], params[0])    
            compare_date = parse(params[0])
            
            return date_value < compare_date
            
        except (ValueError, TypeError):
            return False
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :attribute must be before {params[0]}"
    
class BeforeOrEqualRule(Rule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if not params or len(params) < 1:
            return False
        
        value = self.get_field_value(value, value) 
        
        try:
            if isinstance(value, str):
                date_value = parse(value)
            elif isinstance(value, datetime):
                date_value = value
            else:
                return False
            
            params = list(params)
            params[0] = self.get_field_value(params[0], params[0])
            compare_date = parse(params[0])
            
            return date_value <= compare_date
            
        except (ValueError, TypeError):
            return False
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :attribute must be before or equal to {params[0]}"
    
class DateFormatRule(Rule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if not params or len(params) < 1 or not isinstance(value, str):
            return False
        
        try:
            datetime.strptime(value, params[0])
            return True
        except ValueError:
            return False
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :attribute must match the format {params[0]}"
    
class TimezoneRule(Rule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if not isinstance(value, str):
            return False
        try:
            zoneinfo.ZoneInfo(value)
            return True
        except zoneinfo.ZoneInfoNotFoundError:
            return False
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :attribute must be a valid timezone."