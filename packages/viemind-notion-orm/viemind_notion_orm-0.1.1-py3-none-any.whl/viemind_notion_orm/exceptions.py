"""
viemind_notion_orm.exceptions

Custom exceptions for the Notion ORM library.
"""

class NotionORMError(Exception):
    """Base exception for Notion ORM library."""
    pass

class DatabaseExistsError(NotionORMError):
    """Raised when trying to create a database that already exists."""
    def __init__(self, title: str, parent_id: str, existing_db_id: str):
        self.title = title
        self.parent_id = parent_id
        self.existing_db_id = existing_db_id
        super().__init__(
            f"Database with title '{title}' already exists under parent '{parent_id}'. "
            f"Existing DB ID: {existing_db_id}"
        )

class PropertyNotFoundError(NotionORMError):
    """Raised when a property is not found in a Notion page object."""
    def __init__(self, property_name: str, page_id: str):
        self.property_name = property_name
        self.page_id = page_id
        super().__init__(f"Property '{property_name}' not found on page '{page_id}'.")

class InvalidPropertyTypeError(NotionORMError):
    """Raised when a property is not of the expected type for an operation."""
    def __init__(self, property_name: str, expected_type: str, actual_type: str, page_id: str):
        self.property_name = property_name
        self.expected_type = expected_type
        self.actual_type = actual_type
        self.page_id = page_id
        super().__init__(
            f"Property '{property_name}' on page '{page_id}' is of type '{actual_type}', "
            f"but expected '{expected_type}'."
        )

class SchemaValidationError(NotionORMError):
    """Raised when a database schema is invalid."""
    pass