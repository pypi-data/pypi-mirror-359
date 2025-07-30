"""
Notion ORM - A Python library for Notion with a SQL-like interface.
"""
from .client import NotionClient
from .filters import (
    PropertyFilter, FilterComponent, AndFilter, OrFilter, # Base/Logic classes
    Title, RichText, Text, Number, Select, MultiSelect, Status, Date, Checkbox, # Original Filters
    URL, Email, PhoneNumber, Files, Relation, People, # New Filters
    CreatedTime, LastEditedTime, # New Time-based Filters
    Formula, FormulaText, FormulaNumber, FormulaDate, FormulaCheckbox # New Formula Filters
)
from .utils import ( # Expose utility functions
    get_title, get_rich_text, get_number, get_select_name, get_multi_select_names,
    get_status_name, get_date_value, get_checkbox_value, get_url, get_email,
    get_phone_number, get_files, get_created_time, get_last_edited_time,
    get_people_ids, get_relation_ids, get_property_data
)
from .exceptions import ( # Expose custom exceptions
    NotionORMError, DatabaseExistsError, PropertyNotFoundError,
    InvalidPropertyTypeError, SchemaValidationError
)
from .schema_types import ( # Add these
    NotionPropertyType,
    PropertyDefinition,
    SelectOption,
    StatusOption
)

# Import OOP-style models (may have some linter warnings but functional)
try:
    from .models import (
        NotionModel, Field, TitleField, TextField, NumberField, BooleanField,
        DateField, EmailField, URLField, PhoneField, PeopleField, FilesField,
        UniqueIDField, SelectField, MultiSelectField, StatusField, RelationField,
        QueryManager
    )
    _MODELS_AVAILABLE = True
except Exception:
    _MODELS_AVAILABLE = False

__version__ = "0.2.0"

__all__ = [
    "NotionClient",
    # Filters
    "PropertyFilter", "FilterComponent", "AndFilter", "OrFilter",
    "Title", "RichText", "Text", "Number", "Select", "MultiSelect", "Status", "Date", "Checkbox",
    "URL", "Email", "PhoneNumber", "Files", "Relation", "People",
    "CreatedTime", "LastEditedTime",
    "Formula", "FormulaText", "FormulaNumber", "FormulaDate", "FormulaCheckbox",
    # Utils
    "get_title", "get_rich_text", "get_number", "get_select_name", "get_multi_select_names",
    "get_status_name", "get_date_value", "get_checkbox_value", "get_url", "get_email",
    "get_phone_number", "get_files", "get_created_time", "get_last_edited_time",
    "get_people_ids", "get_relation_ids", "get_property_data",
    # Exceptions
    "NotionORMError", "DatabaseExistsError", "PropertyNotFoundError",
    "InvalidPropertyTypeError", "SchemaValidationError",
    # Schema types
    "NotionPropertyType", "PropertyDefinition", "SelectOption", "StatusOption"
]

# Add models to exports if available
if _MODELS_AVAILABLE:
    __all__.extend([
        "NotionModel", "Field", "TitleField", "TextField", "NumberField", "BooleanField",
        "DateField", "EmailField", "URLField", "PhoneField", "PeopleField", "FilesField",
        "UniqueIDField", "SelectField", "MultiSelectField", "StatusField", "RelationField",
        "QueryManager"
    ])