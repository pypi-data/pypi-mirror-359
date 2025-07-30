"""
viemind_notion_orm.filters

This module provides class-based filter conditions for Notion API queries.
It allows combining filters using bitwise operators (& for AND, | for OR).
"""

from abc import ABC, abstractmethod
from typing import Any, List, Union, Dict # Added Dict for type hinting

class FilterComponent(ABC):
    """
    Abstract base class for all filter components (conditions and groups).
    Enables combining filters using & and | operators.
    """
    def __and__(self, other: 'FilterComponent') -> 'AndFilter':
        """Combines this filter with another using AND logic."""
        return AndFilter(self, other)

    def __or__(self, other: 'FilterComponent') -> 'OrFilter':
        """Combines this filter with another using OR logic."""
        return OrFilter(self, other)

    @abstractmethod
    def to_notion_filter(self) -> Dict[str, Any]:
        """
        Translates this filter component into the Notion API filter JSON structure.
        """
        raise NotImplementedError


class AndFilter(FilterComponent):
    """Represents a logical AND combination of multiple filter components."""
    def __init__(self, *conditions: FilterComponent):
        self.conditions: List[FilterComponent] = []
        for cond in conditions:
            # Flatten nested AndFilters for a cleaner structure
            if isinstance(cond, AndFilter):
                self.conditions.extend(cond.conditions)
            else:
                self.conditions.append(cond)

    def to_notion_filter(self) -> Dict[str, Any]:
        """Converts to Notion's 'and' filter structure."""
        if not self.conditions:
            # According to Notion API, 'and' and 'or' must not be empty.
            # This case should ideally be prevented by how filters are constructed.
            raise ValueError("AND filter cannot be empty.")
        return {"and": [c.to_notion_filter() for c in self.conditions]}


class OrFilter(FilterComponent):
    """Represents a logical OR combination of multiple filter components."""
    def __init__(self, *conditions: FilterComponent):
        self.conditions: List[FilterComponent] = []
        for cond in conditions:
            # Flatten nested OrFilters
            if isinstance(cond, OrFilter):
                self.conditions.extend(cond.conditions)
            else:
                self.conditions.append(cond)

    def to_notion_filter(self) -> Dict[str, Any]:
        """Converts to Notion's 'or' filter structure."""
        if not self.conditions:
            raise ValueError("OR filter cannot be empty.")
        return {"or": [c.to_notion_filter() for c in self.conditions]}


class PropertyFilter(FilterComponent):
    """
    Base class for filters that apply to a specific property.
    """
    def __init__(self, property_name: str, property_api_type: str):
        """
        Initializes a property filter.

        Args:
            property_name: The name of the Notion property to filter on.
            property_api_type: The API type key for this property (e.g., 'rich_text', 'number').
        """
        super().__init__()
        self.property_name = property_name
        self.property_api_type = property_api_type
        self._condition_payload: Dict[str, Any] = {} # Stores the specific condition for this property type

    def to_notion_filter(self) -> Dict[str, Any]:
        """
        Generates the Notion filter dictionary for this single property condition.
        Example: {"property": "Name", "rich_text": {"contains": "Task"}}
        """
        if not self._condition_payload:
            raise ValueError(
                f"Filter condition not set for property '{self.property_name}'. "
                "Ensure you call a comparison method (e.g., .equals(), .contains())."
            )
        return {
            "property": self.property_name,
            self.property_api_type: self._condition_payload
        }


# --- Specific Property Filter Classes ---

class Title(PropertyFilter):
    """Filter for 'title' properties."""
    def __init__(self, property_name: str):
        super().__init__(property_name, "title")

    def equals(self, value: str) -> 'Title':
        self._condition_payload = {"equals": value}
        return self
    def does_not_equal(self, value: str) -> 'Title':
        self._condition_payload = {"does_not_equal": value}
        return self
    def contains(self, value: str) -> 'Title':
        self._condition_payload = {"contains": value}
        return self
    def does_not_contain(self, value: str) -> 'Title':
        self._condition_payload = {"does_not_contain": value}
        return self
    def starts_with(self, value: str) -> 'Title':
        self._condition_payload = {"starts_with": value}
        return self
    def ends_with(self, value: str) -> 'Title':
        self._condition_payload = {"ends_with": value}
        return self
    def is_empty(self) -> 'Title':
        self._condition_payload = {"is_empty": True}
        return self
    def is_not_empty(self) -> 'Title':
        self._condition_payload = {"is_not_empty": True}
        return self

class RichText(PropertyFilter):
    """Filter for 'rich_text' properties (Notion's 'Text' property type)."""
    def __init__(self, property_name: str):
        super().__init__(property_name, "rich_text")

    def equals(self, value: str) -> 'RichText':
        self._condition_payload = {"equals": value}
        return self
    def does_not_equal(self, value: str) -> 'RichText':
        self._condition_payload = {"does_not_equal": value}
        return self
    def contains(self, value: str) -> 'RichText':
        self._condition_payload = {"contains": value}
        return self
    def does_not_contain(self, value: str) -> 'RichText':
        self._condition_payload = {"does_not_contain": value}
        return self
    def starts_with(self, value: str) -> 'RichText':
        self._condition_payload = {"starts_with": value}
        return self
    def ends_with(self, value: str) -> 'RichText':
        self._condition_payload = {"ends_with": value}
        return self
    def is_empty(self) -> 'RichText':
        self._condition_payload = {"is_empty": True}
        return self
    def is_not_empty(self) -> 'RichText':
        self._condition_payload = {"is_not_empty": True}
        return self

Text = RichText # Alias as per prompt's naming suggestion

class Number(PropertyFilter):
    """Filter for 'number' properties."""
    def __init__(self, property_name: str):
        super().__init__(property_name, "number")

    def equals(self, value: Union[int, float]) -> 'Number':
        self._condition_payload = {"equals": value}
        return self
    def does_not_equal(self, value: Union[int, float]) -> 'Number':
        self._condition_payload = {"does_not_equal": value}
        return self
    def greater_than(self, value: Union[int, float]) -> 'Number':
        self._condition_payload = {"greater_than": value}
        return self
    def less_than(self, value: Union[int, float]) -> 'Number':
        self._condition_payload = {"less_than": value}
        return self
    def greater_than_or_equal_to(self, value: Union[int, float]) -> 'Number':
        self._condition_payload = {"greater_than_or_equal_to": value}
        return self
    def less_than_or_equal_to(self, value: Union[int, float]) -> 'Number':
        self._condition_payload = {"less_than_or_equal_to": value}
        return self
    def is_empty(self) -> 'Number':
        self._condition_payload = {"is_empty": True}
        return self
    def is_not_empty(self) -> 'Number':
        self._condition_payload = {"is_not_empty": True}
        return self

class Select(PropertyFilter):
    """Filter for 'select' properties."""
    def __init__(self, property_name: str):
        super().__init__(property_name, "select")

    def equals(self, value: str) -> 'Select':
        self._condition_payload = {"equals": value}
        return self
    def does_not_equal(self, value: str) -> 'Select':
        self._condition_payload = {"does_not_equal": value}
        return self
    def is_empty(self) -> 'Select':
        self._condition_payload = {"is_empty": True}
        return self
    def is_not_empty(self) -> 'Select':
        self._condition_payload = {"is_not_empty": True}
        return self

class MultiSelect(PropertyFilter):
    """Filter for 'multi_select' properties."""
    def __init__(self, property_name: str):
        super().__init__(property_name, "multi_select")

    def contains(self, value: str) -> 'MultiSelect':
        self._condition_payload = {"contains": value}
        return self
    def does_not_contain(self, value: str) -> 'MultiSelect':
        self._condition_payload = {"does_not_contain": value}
        return self
    def is_empty(self) -> 'MultiSelect':
        self._condition_payload = {"is_empty": True}
        return self
    def is_not_empty(self) -> 'MultiSelect':
        self._condition_payload = {"is_not_empty": True}
        return self

class Status(PropertyFilter):
    """Filter for 'status' properties."""
    def __init__(self, property_name: str):
        super().__init__(property_name, "status")

    def equals(self, value: str) -> 'Status':
        self._condition_payload = {"equals": value}
        return self
    def does_not_equal(self, value: str) -> 'Status':
        self._condition_payload = {"does_not_equal": value}
        return self
    def is_empty(self) -> 'Status':
        self._condition_payload = {"is_empty": True}
        return self
    def is_not_empty(self) -> 'Status':
        self._condition_payload = {"is_not_empty": True}
        return self

class Date(PropertyFilter):
    """
    Filter for 'date' properties.
    Dates should be in ISO 8601 format (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SSZ).
    """
    def __init__(self, property_name: str):
        super().__init__(property_name, "date")

    def equals(self, date_str: str) -> 'Date':
        self._condition_payload = {"equals": date_str}
        return self
    def before(self, date_str: str) -> 'Date':
        self._condition_payload = {"before": date_str}
        return self
    def after(self, date_str: str) -> 'Date':
        self._condition_payload = {"after": date_str}
        return self
    def on_or_before(self, date_str: str) -> 'Date':
        self._condition_payload = {"on_or_before": date_str}
        return self
    def on_or_after(self, date_str: str) -> 'Date': # Added for completeness
        self._condition_payload = {"on_or_after": date_str}
        return self
    def is_empty(self) -> 'Date':
        self._condition_payload = {"is_empty": True}
        return self
    def is_not_empty(self) -> 'Date':
        self._condition_payload = {"is_not_empty": True}
        return self
    def past_week(self) -> 'Date':
        self._condition_payload = {"past_week": {}}
        return self
    def past_month(self) -> 'Date':
        self._condition_payload = {"past_month": {}}
        return self
    def past_year(self) -> 'Date':
        self._condition_payload = {"past_year": {}}
        return self
    def this_week(self) -> 'Date':
        self._condition_payload = {"this_week": {}}
        return self
    def next_week(self) -> 'Date':
        self._condition_payload = {"next_week": {}}
        return self
    def next_month(self) -> 'Date':
        self._condition_payload = {"next_month": {}}
        return self
    def next_year(self) -> 'Date':
        self._condition_payload = {"next_year": {}}
        return self

class Checkbox(PropertyFilter):
    """Filter for 'checkbox' properties."""
    def __init__(self, property_name: str):
        super().__init__(property_name, "checkbox")

    def equals(self, value: bool) -> 'Checkbox':
        self._condition_payload = {"equals": value}
        return self
    def does_not_equal(self, value: bool) -> 'Checkbox':
        self._condition_payload = {"does_not_equal": value}
        return self


class URL(PropertyFilter):
    """Filter for 'url' properties."""
    def __init__(self, property_name: str):
        super().__init__(property_name, "url")
    def equals(self, value: str) -> 'URL': self._condition_payload = {"equals": value}; return self
    def does_not_equal(self, value: str) -> 'URL': self._condition_payload = {"does_not_equal": value}; return self
    def contains(self, value: str) -> 'URL': self._condition_payload = {"contains": value}; return self
    def does_not_contain(self, value: str) -> 'URL': self._condition_payload = {"does_not_contain": value}; return self
    def starts_with(self, value: str) -> 'URL': self._condition_payload = {"starts_with": value}; return self
    def ends_with(self, value: str) -> 'URL': self._condition_payload = {"ends_with": value}; return self
    def is_empty(self) -> 'URL': self._condition_payload = {"is_empty": True}; return self
    def is_not_empty(self) -> 'URL': self._condition_payload = {"is_not_empty": True}; return self

class Email(PropertyFilter):
    """Filter for 'email' properties."""
    def __init__(self, property_name: str):
        super().__init__(property_name, "email")
    # Methods similar to URL/Text
    def equals(self, value: str) -> 'Email': self._condition_payload = {"equals": value}; return self
    def does_not_equal(self, value: str) -> 'Email': self._condition_payload = {"does_not_equal": value}; return self
    def contains(self, value: str) -> 'Email': self._condition_payload = {"contains": value}; return self
    def does_not_contain(self, value: str) -> 'Email': self._condition_payload = {"does_not_contain": value}; return self
    def starts_with(self, value: str) -> 'Email': self._condition_payload = {"starts_with": value}; return self
    def ends_with(self, value: str) -> 'Email': self._condition_payload = {"ends_with": value}; return self
    def is_empty(self) -> 'Email': self._condition_payload = {"is_empty": True}; return self
    def is_not_empty(self) -> 'Email': self._condition_payload = {"is_not_empty": True}; return self

class PhoneNumber(PropertyFilter):
    """Filter for 'phone_number' properties."""
    def __init__(self, property_name: str):
        super().__init__(property_name, "phone_number")
    # Methods similar to URL/Text
    def equals(self, value: str) -> 'PhoneNumber': self._condition_payload = {"equals": value}; return self
    def does_not_equal(self, value: str) -> 'PhoneNumber': self._condition_payload = {"does_not_equal": value}; return self
    def contains(self, value: str) -> 'PhoneNumber': self._condition_payload = {"contains": value}; return self
    def does_not_contain(self, value: str) -> 'PhoneNumber': self._condition_payload = {"does_not_contain": value}; return self
    def starts_with(self, value: str) -> 'PhoneNumber': self._condition_payload = {"starts_with": value}; return self
    def ends_with(self, value: str) -> 'PhoneNumber': self._condition_payload = {"ends_with": value}; return self
    def is_empty(self) -> 'PhoneNumber': self._condition_payload = {"is_empty": True}; return self
    def is_not_empty(self) -> 'PhoneNumber': self._condition_payload = {"is_not_empty": True}; return self

class Files(PropertyFilter):
    """Filter for 'files' properties."""
    def __init__(self, property_name: str):
        super().__init__(property_name, "files")
    def is_empty(self) -> 'Files': self._condition_payload = {"is_empty": True}; return self
    def is_not_empty(self) -> 'Files': self._condition_payload = {"is_not_empty": True}; return self

class Relation(PropertyFilter):
    """Filter for 'relation' properties. Value is a page_id."""
    def __init__(self, property_name: str):
        super().__init__(property_name, "relation")
    def contains(self, page_id: str) -> 'Relation': self._condition_payload = {"contains": page_id}; return self
    def does_not_contain(self, page_id: str) -> 'Relation': self._condition_payload = {"does_not_contain": page_id}; return self
    def is_empty(self) -> 'Relation': self._condition_payload = {"is_empty": True}; return self
    def is_not_empty(self) -> 'Relation': self._condition_payload = {"is_not_empty": True}; return self

class People(PropertyFilter):
    """Filter for 'people' properties. Value is a user_id."""
    def __init__(self, property_name: str):
        super().__init__(property_name, "people")
    def contains(self, user_id: str) -> 'People': self._condition_payload = {"contains": user_id}; return self
    def does_not_contain(self, user_id: str) -> 'People': self._condition_payload = {"does_not_contain": user_id}; return self
    def is_empty(self) -> 'People': self._condition_payload = {"is_empty": True}; return self
    def is_not_empty(self) -> 'People': self._condition_payload = {"is_not_empty": True}; return self

class CreatedTime(PropertyFilter):
    """Filter for 'created_time' properties."""
    def __init__(self, property_name: str = "Created time"): # Default name, can be overridden
        super().__init__(property_name, "created_time")
    # Methods similar to Date
    def equals(self, date_str: str) -> 'CreatedTime': self._condition_payload = {"equals": date_str}; return self
    def before(self, date_str: str) -> 'CreatedTime': self._condition_payload = {"before": date_str}; return self
    def after(self, date_str: str) -> 'CreatedTime': self._condition_payload = {"after": date_str}; return self
    def on_or_before(self, date_str: str) -> 'CreatedTime': self._condition_payload = {"on_or_before": date_str}; return self
    def on_or_after(self, date_str: str) -> 'CreatedTime': self._condition_payload = {"on_or_after": date_str}; return self
    def is_empty(self) -> 'CreatedTime': self._condition_payload = {"is_empty": True}; return self # Should not be empty
    def is_not_empty(self) -> 'CreatedTime': self._condition_payload = {"is_not_empty": True}; return self
    def past_week(self) -> 'CreatedTime': self._condition_payload = {"past_week": {}}; return self
    # ... other relative date filters as in Date class

class LastEditedTime(PropertyFilter):
    """Filter for 'last_edited_time' properties."""
    def __init__(self, property_name: str = "Last edited time"): # Default name
        super().__init__(property_name, "last_edited_time")
    # Methods similar to Date/CreatedTime
    def equals(self, date_str: str) -> 'LastEditedTime': self._condition_payload = {"equals": date_str}; return self
    def before(self, date_str: str) -> 'LastEditedTime': self._condition_payload = {"before": date_str}; return self
    def after(self, date_str: str) -> 'LastEditedTime': self._condition_payload = {"after": date_str}; return self
    def on_or_before(self, date_str: str) -> 'LastEditedTime': self._condition_payload = {"on_or_before": date_str}; return self
    def on_or_after(self, date_str: str) -> 'LastEditedTime': self._condition_payload = {"on_or_after": date_str}; return self
    def is_empty(self) -> 'LastEditedTime': self._condition_payload = {"is_empty": True}; return self # Should not be empty
    def is_not_empty(self) -> 'LastEditedTime': self._condition_payload = {"is_not_empty": True}; return self
    def past_week(self) -> 'LastEditedTime': self._condition_payload = {"past_week": {}}; return self
    # ... other relative date filters

# Formula and Rollup filters require specifying the result type
# Example: FormulaText, FormulaNumber, FormulaDate, FormulaCheckbox
class Formula(PropertyFilter):
    """
    Base filter for 'formula' properties.
    You must use a type-specific subclass like FormulaText, FormulaNumber, etc.
    """
    def __init__(self, property_name: str, formula_result_type_key: str):
        super().__init__(property_name, "formula")
        self.formula_result_type_key = formula_result_type_key # e.g., "string", "number", "date", "checkbox"

    def to_notion_filter(self) -> Dict[str, Any]:
        if not self._condition_payload:
            raise ValueError(f"Filter condition not set for formula property '{self.property_name}'.")
        return {
            "property": self.property_name,
            "formula": {
                self.formula_result_type_key: self._condition_payload
            }
        }

class FormulaText(Formula):
    def __init__(self, property_name: str):
        super().__init__(property_name, "string") # Notion API uses "string" for text formula results
    # Methods like RichText/URL
    def equals(self, value: str) -> 'FormulaText': self._condition_payload = {"equals": value}; return self
    def does_not_equal(self, value: str) -> 'FormulaText': self._condition_payload = {"does_not_equal": value}; return self
    def contains(self, value: str) -> 'FormulaText': self._condition_payload = {"contains": value}; return self
    def does_not_contain(self, value: str) -> 'FormulaText': self._condition_payload = {"does_not_contain": value}; return self
    def starts_with(self, value: str) -> 'FormulaText': self._condition_payload = {"starts_with": value}; return self
    def ends_with(self, value: str) -> 'FormulaText': self._condition_payload = {"ends_with": value}; return self
    def is_empty(self) -> 'FormulaText': self._condition_payload = {"is_empty": True}; return self
    def is_not_empty(self) -> 'FormulaText': self._condition_payload = {"is_not_empty": True}; return self

class FormulaNumber(Formula):
    def __init__(self, property_name: str):
        super().__init__(property_name, "number")
    # Methods like Number
    def equals(self, value: Union[int, float]) -> 'FormulaNumber': self._condition_payload = {"equals": value}; return self
    # ... other number comparison methods

class FormulaDate(Formula):
    def __init__(self, property_name: str):
        super().__init__(property_name, "date")
    # Methods like Date
    def equals(self, date_str: str) -> 'FormulaDate': self._condition_payload = {"equals": date_str}; return self
    # ... other date comparison methods

class FormulaCheckbox(Formula):
    def __init__(self, property_name: str):
        super().__init__(property_name, "checkbox")
    # Methods like Checkbox
    def equals(self, value: bool) -> 'FormulaCheckbox': self._condition_payload = {"equals": value}; return self
    def does_not_equal(self, value: bool) -> 'FormulaCheckbox': self._condition_payload = {"does_not_equal": value}; return self

# Rollup filters are similar to Formula filters in that their condition depends on the rollup's function output
# The Notion API structure for rollup filters is:
# "rollup": { "any" | "every" | "none": { <property_type_filter_for_rolled_up_property> } }
# OR "rollup": { "number" | "date": { <comparison_for_number_or_date> } }
# This is more complex and might require a different approach or more detailed sub-classing.
# For now, we'll skip comprehensive Rollup filter classes but acknowledge their complexity