"""
viemind_notion_orm.utils

Helper functions for easier extraction of property values from Notion page objects
and other utility operations.
"""
from typing import Dict, Any, List, Optional, Union
from .exceptions import PropertyNotFoundError, InvalidPropertyTypeError


# --- Property Value Extractor Functions ---

def get_property_data(page_obj: Dict[str, Any], property_name: str) -> Optional[Dict[str, Any]]:
    """
    Safely retrieves the raw data block for a given property name from a page object.
    """
    properties = page_obj.get("properties")
    if not properties:
        raise PropertyNotFoundError(property_name, page_obj.get("id", "Unknown Page ID"))

    prop_data = properties.get(property_name)
    if prop_data is None:
        raise PropertyNotFoundError(property_name, page_obj.get("id", "Unknown Page ID"))
    return prop_data


def get_title(page_obj: Dict[str, Any], property_name: str) -> Optional[str]:
    """Extracts the plain text from a 'title' property."""
    prop_data = get_property_data(page_obj, property_name)
    if prop_data["type"] != "title":
        raise InvalidPropertyTypeError(property_name, "title", prop_data["type"], page_obj.get("id"))

    title_items = prop_data.get("title", [])
    if title_items and isinstance(title_items, list) and len(title_items) > 0:
        return title_items[0].get("plain_text")
    return None


def get_rich_text(page_obj: Dict[str, Any], property_name: str) -> str:
    """Extracts and concatenates plain text from a 'rich_text' property."""
    prop_data = get_property_data(page_obj, property_name)
    if prop_data["type"] != "rich_text":
        raise InvalidPropertyTypeError(property_name, "rich_text", prop_data["type"], page_obj.get("id"))

    text_parts = [item.get("plain_text", "") for item in prop_data.get("rich_text", [])]
    return "".join(text_parts)


def get_number(page_obj: Dict[str, Any], property_name: str) -> Optional[Union[int, float]]:
    """Extracts the value from a 'number' property."""
    prop_data = get_property_data(page_obj, property_name)
    if prop_data["type"] != "number":
        raise InvalidPropertyTypeError(property_name, "number", prop_data["type"], page_obj.get("id"))
    return prop_data.get("number")


def get_select_name(page_obj: Dict[str, Any], property_name: str) -> Optional[str]:
    """Extracts the name of the selected option from a 'select' property."""
    prop_data = get_property_data(page_obj, property_name)
    if prop_data["type"] != "select":
        raise InvalidPropertyTypeError(property_name, "select", prop_data["type"], page_obj.get("id"))

    select_option = prop_data.get("select")
    return select_option.get("name") if select_option else None


def get_multi_select_names(page_obj: Dict[str, Any], property_name: str) -> List[str]:
    """Extracts a list of names of selected options from a 'multi_select' property."""
    prop_data = get_property_data(page_obj, property_name)
    if prop_data["type"] != "multi_select":
        raise InvalidPropertyTypeError(property_name, "multi_select", prop_data["type"], page_obj.get("id"))

    return [option.get("name") for option in prop_data.get("multi_select", []) if option.get("name")]


def get_status_name(page_obj: Dict[str, Any], property_name: str) -> Optional[str]:
    """Extracts the name of the current status from a 'status' property."""
    prop_data = get_property_data(page_obj, property_name)
    if prop_data["type"] != "status":
        raise InvalidPropertyTypeError(property_name, "status", prop_data["type"], page_obj.get("id"))

    status_option = prop_data.get("status")
    return status_option.get("name") if status_option else None


def get_date_value(page_obj: Dict[str, Any], property_name: str) -> Optional[Dict[str, Optional[str]]]:
    """
    Extracts the date object (with 'start', 'end', 'time_zone') from a 'date' property.
    Returns: {"start": "YYYY-MM-DD", "end": "YYYY-MM-DD" or None, "time_zone": "tz" or None}
    """
    prop_data = get_property_data(page_obj, property_name)
    if prop_data["type"] != "date":
        raise InvalidPropertyTypeError(property_name, "date", prop_data["type"], page_obj.get("id"))
    return prop_data.get("date")  # This is a dict like {"start": "...", "end": "...", "time_zone": "..."}


def get_checkbox_value(page_obj: Dict[str, Any], property_name: str) -> Optional[bool]:
    """Extracts the boolean value from a 'checkbox' property."""
    prop_data = get_property_data(page_obj, property_name)
    if prop_data["type"] != "checkbox":
        raise InvalidPropertyTypeError(property_name, "checkbox", prop_data["type"], page_obj.get("id"))
    return prop_data.get("checkbox")


def get_url(page_obj: Dict[str, Any], property_name: str) -> Optional[str]:
    """Extracts the URL string from a 'url' property."""
    prop_data = get_property_data(page_obj, property_name)
    if prop_data["type"] != "url":
        raise InvalidPropertyTypeError(property_name, "url", prop_data["type"], page_obj.get("id"))
    return prop_data.get("url")


def get_email(page_obj: Dict[str, Any], property_name: str) -> Optional[str]:
    """Extracts the email string from an 'email' property."""
    prop_data = get_property_data(page_obj, property_name)
    if prop_data["type"] != "email":
        raise InvalidPropertyTypeError(property_name, "email", prop_data["type"], page_obj.get("id"))
    return prop_data.get("email")


def get_phone_number(page_obj: Dict[str, Any], property_name: str) -> Optional[str]:
    """Extracts the phone number string from a 'phone_number' property."""
    prop_data = get_property_data(page_obj, property_name)
    if prop_data["type"] != "phone_number":  # Corrected API type
        raise InvalidPropertyTypeError(property_name, "phone_number", prop_data["type"], page_obj.get("id"))
    return prop_data.get("phone_number")


def get_files(page_obj: Dict[str, Any], property_name: str) -> List[Dict[str, Any]]:
    """Extracts a list of file objects from a 'files' property."""
    prop_data = get_property_data(page_obj, property_name)
    if prop_data["type"] != "files":
        raise InvalidPropertyTypeError(property_name, "files", prop_data["type"], page_obj.get("id"))
    return prop_data.get("files", [])


def get_created_time(page_obj: Dict[str, Any], property_name: str = "Created time") -> Optional[str]:
    """Extracts the 'created_time' string. Note: Property name might vary."""
    prop_data = get_property_data(page_obj, property_name)  # Common name, could be different
    if prop_data["type"] != "created_time":
        raise InvalidPropertyTypeError(property_name, "created_time", prop_data["type"], page_obj.get("id"))
    return prop_data.get("created_time")


def get_last_edited_time(page_obj: Dict[str, Any], property_name: str = "Last edited time") -> Optional[str]:
    """Extracts the 'last_edited_time' string. Note: Property name might vary."""
    prop_data = get_property_data(page_obj, property_name)  # Common name, could be different
    if prop_data["type"] != "last_edited_time":
        raise InvalidPropertyTypeError(property_name, "last_edited_time", prop_data["type"], page_obj.get("id"))
    return prop_data.get("last_edited_time")


def get_people_ids(page_obj: Dict[str, Any], property_name: str) -> List[str]:
    """Extracts a list of user IDs from a 'people' property."""
    prop_data = get_property_data(page_obj, property_name)
    if prop_data["type"] != "people":
        raise InvalidPropertyTypeError(property_name, "people", prop_data["type"], page_obj.get("id"))
    return [person.get("id") for person in prop_data.get("people", []) if person.get("id")]


def get_relation_ids(page_obj: Dict[str, Any], property_name: str) -> List[str]:
    """Extracts a list of related page IDs from a 'relation' property."""
    prop_data = get_property_data(page_obj, property_name)
    if prop_data["type"] != "relation":
        raise InvalidPropertyTypeError(property_name, "relation", prop_data["type"], page_obj.get("id"))
    return [relation.get("id") for relation in prop_data.get("relation", []) if relation.get("id")]

# --- Property Payload Builder Functions (for creating/updating pages) ---
# These are more complex and would typically involve specific formats.
# For now, we'll let users construct the raw dict, but these are good future additions.

# Example structure (not fully implemented here, just illustrative)
# def build_title_payload(content: str) -> Dict[str, Any]:
#     return {"title": [{"type": "text", "text": {"content": content}}]}

# def build_rich_text_payload(content: str) -> Dict[str, Any]:
#     return {"rich_text": [{"type": "text", "text": {"content": content}}]}

# def build_number_payload(value: Union[int, float]) -> Dict[str, Any]:
#     return {"number": value}

# ... and so on for other property types.