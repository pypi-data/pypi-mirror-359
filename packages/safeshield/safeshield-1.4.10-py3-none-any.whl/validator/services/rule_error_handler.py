from typing import Dict, List, Any, Optional, Union
import re

class RuleErrorHandler:
    """Enhanced validation error handler with complete Laravel-style placeholder support,
    including field-value pair parameters (field1,value1,field2,value2)"""
    
    def __init__(self, messages: Dict[str, str], custom_attributes: Dict[str, str]):
        self.messages = messages or {}
        self.custom_attributes = custom_attributes or {}
        self.errors: Dict[str, List[str]] = {}
        self._current_rule: Optional[str] = None
        self._current_params: Optional[List[str]] = None
        self._current_value: Optional[Any] = None

    def add_error(self, field: str, rule_name: str, rule_params: List[str], default_message: str, value: Any) -> None:
        """Add a formatted error message with complete placeholder support"""
        self._current_rule = rule_name
        self._current_params = rule_params
        self._current_value = value
        
        message = self._format_message(field, rule_name, default_message, value)
        self.errors.setdefault(field, []).append(message)

    def _format_message(self, field: str, rule_name: str, default_message: str, value: Any) -> str:
        """Format error message with all supported placeholders"""
        attribute = self._get_attribute_name(field)
        value_str = self._stringify_value(value)
        
        # Get the most specific message available
        message = self._get_message(field, rule_name, attribute, default_message)
        
        # Prepare all possible replacements
        replacements = self._prepare_replacements(attribute, value_str)
        
        # Apply replacements safely
        return self._apply_replacements(message, replacements)

    def _get_attribute_name(self, field: str) -> str:
        """Get the display name for a field with nested field support"""
        # Check for exact match first
        if field in self.custom_attributes:
            return self.custom_attributes[field]
        
        # Handle nested fields (e.g., 'user.profile.name')
        parts = field.split('.')
        for i in range(len(parts), 0, -1):
            wildcard_key = '.'.join(parts[:i]) + '.*'
            if wildcard_key in self.custom_attributes:
                return self.custom_attributes[wildcard_key]
        
        # Fallback to last part or field itself
        return self.custom_attributes.get(parts[-1], field.replace('_', ' ').title())

    def _stringify_value(self, value: Any) -> str:
        """Convert any value to a string representation"""
        if value is None:
            return ''
        if isinstance(value, (list, dict, set)):
            return ', '.join(str(v) for v in value) if value else ''
        return str(value)

    def _get_message(self, field: str, rule_name: str, attribute: str, default: str) -> str:
        """Get the most specific error message available"""
        return (
            self.messages.get(f"{field}.{rule_name}") or  # Field-specific rule message
            self.messages.get(field) or                    # Field-specific default
            self.messages.get(rule_name) or                # Rule-specific default
            default                                       # Fallback
        )

    def _prepare_replacements(self, attribute: str, value_str: str) -> Dict[str, str]:
        """Prepare all placeholder replacements including field-value pairs"""
        replacements = {
            ':attribute': attribute,
            ':input': value_str,
            ':value': value_str,
            ':values': self._get_values_param(),
            ':min': self._get_min_param(),
            ':max': self._get_max_param(),
            ':size': self._get_size_param(),
            ':other': self._get_other_param_display(),
            ':date': self._get_date_param(),
            ':format': self._get_format_param(),
            ':param': self._get_first_param(),
        }
        
        # Add numbered placeholders for field-value pairs (e.g., :other1, :value1, :other2, :value2)
        if self._is_field_value_rule() and self._current_params:
            field_value_pairs = self._get_field_value_pairs()
            if field_value_pairs:
                first_field, first_value = field_value_pairs[0]
                replacements[':other'] = self._get_attribute_name(first_field)
                replacements[':value'] = first_value
                
                for i, (field, val) in enumerate(field_value_pairs[1:], start=2):
                    replacements[f':other{i}'] = self._get_attribute_name(field)
                    replacements[f':value{i}'] = val
        
        return replacements

    def _is_field_value_rule(self) -> bool:
        """Check if the current rule uses field-value pairs"""
        return self._current_rule and self._current_rule.lower() in {
            'required_if', 'required_unless', 
            'exclude_if', 'exclude_unless',
            'missing_if', 'missing_unless',
            'present_if', 'present_unless'
        }

    def _get_field_value_pairs(self) -> List[tuple]:
        """Extract field-value pairs from parameters"""
        if not self._current_params:
            return []
        
        pairs = []
        params = list(self._current_params).copy()
        
        # Process parameters in pairs (field, value)
        while len(params) >= 2:
            field = params.pop(0)
            value = params.pop(0)
            pairs.append((field, value))
        
        return pairs

    def _apply_replacements(self, message: str, replacements: Dict[str, str]) -> str:
        """Safely apply all replacements to the message"""
        for placeholder, replacement in replacements.items():
            if replacement is not None:
                # Use regex to avoid partial replacements
                safe_replacement = re.escape(str(replacement))
                safe_replacement = safe_replacement.replace('\\', r'')
                message = re.sub(
                    re.escape(placeholder) + r'(?![a-zA-Z0-9_])', 
                    safe_replacement, 
                    message
                )
        return message

    def _get_other_param_display(self) -> Optional[str]:
        """Get display names for other fields with proper formatting"""
        other_fields = self._get_raw_other_fields()
        if not other_fields:
            return None
            
        display_names = [self._get_attribute_name(f) for f in other_fields]
        
        if len(display_names) == 1:
            return display_names[0]
        if len(display_names) == 2:
            return f"{display_names[0]} and {display_names[1]}"
        return f"{', '.join(display_names[:-1])}, and {display_names[-1]}"

    def _get_raw_other_fields(self) -> List[str]:
        """Extract field references from rule parameters"""
        if not self._current_rule or not self._current_params:
            return []
            
        rule = self._current_rule.lower()
        
        # Rules with field-value pairs (field1,value1,field2,value2,...)
        if rule in {
            'required_if', 'required_unless', 'exclude_if', 'exclude_unless',
            'accepted_if', 'accepted_all_if', 'declined_if', 'declined_all_if',
            'accepted_unless', 'declined_unless',
            'missing_if', 'missing_unless', 'present_if', 'present_unless'
        }:
            return self._current_params[::2]  # Take every even index
            
        # Rules with multi field references
        if rule in {
            'required_with', 'required_with_all', 'required_without', 'required_without_all',
            'prohibits', 'exclude_with', 'exclude_without',
            'missing_with', 'missing_with_all', 
            'present_with', 'present_with_all'
        }:
            return self._current_params
            
        # Single field rules
        if rule in {
            'required_if_accepted', 'required_if_declined',
            'prohibited_if_accepted', 'prohibited_if_declined'
        }:
            return [self._current_params[0]] if self._current_params else []
            
        return []

    def _get_min_param(self) -> Optional[str]:
        """Get min parameter from rule"""
        if not self._current_params:
            return None
            
        if self._current_rule and self._current_rule.startswith(('min', 'between', 'digits_between')):
            return self._current_params[0]
        return None

    def _get_max_param(self) -> Optional[str]:
        """Get max parameter from rule"""
        if not self._current_params or len(self._current_params) < 2:
            return None
            
        if self._current_rule and self._current_rule.startswith(('max', 'between', 'digits_between')):
            return self._current_params[1] if self._current_rule.startswith('between') else self._current_params[0]
        return None

    def _get_size_param(self) -> Optional[str]:
        """Get size parameter from rule"""
        if self._current_rule and self._current_rule.startswith('size') and self._current_params:
            return self._current_params[0]
        return None

    def _get_values_param(self) -> Optional[str]:
        """Get values list for in/not_in rules"""
        if (self._current_rule and 
            self._current_rule.startswith(('in', 'not_in')) and 
            self._current_params):
            return ', '.join(self._current_params)
        return None

    def _get_date_param(self) -> Optional[str]:
        """Get date parameter for date rules"""
        if (self._current_rule and 
            self._current_rule.startswith(('after', 'before', 'after_or_equal', 'before_or_equal')) and 
            self._current_params):
            return self._current_params[0]
        return None

    def _get_format_param(self) -> Optional[str]:
        """Get format parameter"""
        if (self._current_rule and 
            self._current_rule.startswith('date_format') and 
            self._current_params):
            return self._current_params[0]
        return None

    def _get_first_param(self) -> Optional[str]:
        """Get first parameter from rule"""
        return self._current_params[0] if self._current_params else None

    @property
    def has_errors(self) -> bool:
        """Check if any errors exist"""
        return bool(self.errors)