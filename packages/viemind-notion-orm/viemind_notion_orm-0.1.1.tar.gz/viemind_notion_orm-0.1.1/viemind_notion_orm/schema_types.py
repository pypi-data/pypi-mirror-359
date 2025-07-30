from typing import List, Optional, Union, Type, Dict, Any
from enum import Enum


class NotionPropertyType(Enum):
    TEXT = "text"  # Maps to Notion's 'rich_text'
    TITLE = "title"  # Maps to Notion's 'title' (usually one per DB)
    NUMBER = "number"
    INTEGER = "integer"  # Alias for NUMBER, no specific integer format in Notion
    FLOAT = "float"  # Alias for NUMBER
    BOOLEAN = "boolean"  # Maps to Notion's 'checkbox'
    DATE = "date"
    DATETIME = "datetime"  # Alias for DATE, Notion dates can include time
    SELECT = "select"  # Requires options
    MULTI_SELECT = "multi_select"  # Requires options
    STATUS = "status"  # Requires options and potentially group definitions
    URL = "url"
    EMAIL = "email"
    PHONE = "phone"
    PEOPLE = "people"
    FILES = "files"
    # For relations, we need to specify the target database ID
    RELATION = "relation"
    # Potentially for more complex JSON-like data, we could map it to a Text property
    # and the user would handle JSON serialization/deserialization.
    JSON_TEXT = "json_text"  # Maps to Notion's 'rich_text' for storing JSON strings
    UNIQUE_ID = "unique_id"
    # Future: Could add Formula, Rollup if we define a way to pass their complex configs


# Helper for defining property options
class SelectOption:
    def __init__(self, name: str, color: Optional[str] = None):
        self.name = name
        self.color = color  # Notion color string like "red", "blue", etc.

    def to_notion_option(self) -> Dict[str, Any]:
        option_dict = {"name": self.name}
        if self.color:
            option_dict["color"] = self.color
        return option_dict


class StatusOption(SelectOption):  # Status options are like select options
    pass


class StatusGroup:
    def __init__(self, name: str, color: str, option_ids: List[str]):
        # Option IDs are tricky here as they are assigned by Notion on creation.
        # For initial schema, we might only define options, and groups are managed later
        # or we accept option names and map them.
        # For simplicity now, let's focus on options for status, groups are UI.
        pass


class PropertyDefinition:
    """
    Represents a simplified definition for a Notion database property.
    """

    def __init__(self,
                 type: Union[NotionPropertyType, str],
                 options: Optional[List[Union[SelectOption, StatusOption, str]]] = None,
                 relation_database_id: Optional[str] = None,
                 number_format: Optional[str] = None,  # "number", "dollar", "percent", etc.
                 # for two-way relations
                 two_way_relation_property_name: Optional[str] = None,
                 unique_id_prefix: Optional[str] = None
                 ):
        self.type = type
        if isinstance(type, str):
            try:
                self.type = NotionPropertyType(type.lower())
            except ValueError:
                raise ValueError(
                    f"Invalid property type string: {type}. Supported types: {[e.value for e in NotionPropertyType]}")
        else:
            self.type = type

        self.options = options
        self.relation_database_id = relation_database_id
        self.number_format = number_format
        self.two_way_relation_property_name = two_way_relation_property_name
        self.unique_id_prefix = unique_id_prefix
        # Validations
        if self.type in [NotionPropertyType.SELECT, NotionPropertyType.MULTI_SELECT,
                         NotionPropertyType.STATUS] and not self.options:
            raise ValueError(f"Property type '{self.type.value}' requires 'options'.")
        if self.type == NotionPropertyType.RELATION and not self.relation_database_id:
            raise ValueError("Property type 'relation' requires 'relation_database_id'.")
        if self.type not in [NotionPropertyType.NUMBER, NotionPropertyType.INTEGER,
                             NotionPropertyType.FLOAT] and self.number_format:
            raise ValueError(f"Number format '{self.number_format}' is only applicable to number types.")
        if self.type == NotionPropertyType.UNIQUE_ID and self.unique_id_prefix is not None and not isinstance(
                self.unique_id_prefix, str):
            raise ValueError("unique_id_prefix must be a string if provided.")