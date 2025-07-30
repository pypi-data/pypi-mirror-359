# Notion ORM - Python Library

A Python library for Notion that provides a high-level, SQL-like interface for creating, querying, and joining databases. This library acts as an abstraction layer over the official `notion-client` Python SDK, offering a more intuitive and developer-friendly experience with a class-based filtering system.

## Features

- **Class-Based Filtering**: Construct complex filters using Python classes and logical operators (`&` for AND, `|` for OR) instead of raw JSON.
- **Automatic Pagination**: The `query` method handles pagination seamlessly, returning all results.
- **Database Joining**: A `join` method to mimic SQL LEFT JOIN functionality between two databases based on a relation property.
- **Database Creation**: Simple `create_database` method.
- **Built on `notion-client`**: Leverages the official Notion Python SDK.

## Installation

1.  **Prerequisites**: Ensure you have Python 3.7+ and pip installed.
2.  **Install `notion-client`**:
    ```bash
    pip install notion-client
    ```
3.  **Add `viemind_notion_orm` to your project**:
    Place the `viemind_notion_orm` directory (containing `__init__.py`, `client.py`, and `filters.py`) into your Python project's root directory or ensure it's in your `PYTHONPATH`.

## Authentication

To use this library, you need a Notion integration token.

1.  Go to [My Integrations](https://www.notion.so/my-integrations) on Notion.
2.  Click "New integration" and give it a name.
3.  Choose the associated workspace. Select appropriate capabilities (e.g., "Read content", "Update content", "Insert content").
4.  Copy the "Internal Integration Token".
5.  Share the specific databases or pages you want to access with your integration. Click the `•••` menu on a database/page, select "Add connections", and find your integration.

Initialize the `NotionClient` with your token:

```python
# In your main script or README example:
from viemind_notion_orm import NotionClient, NotionPropertyType, PropertyDefinition, SelectOption

# client = NotionClient(auth=NOTION_TOKEN) # Assume client is initialized
# PARENT_PAGE_ID_FOR_DBS = "YOUR_PARENT_PAGE_ID"
# SOME_OTHER_DB_ID = "ID_OF_ANOTHER_DATABASE_FOR_RELATION" # e.g., a Users DB

# New, simplified schema definition:
simplified_projects_schema = {
    "Project ID": NotionPropertyType.TITLE, # Every DB needs one title property
    "Project Name": NotionPropertyType.TEXT,
    "Description": "text", # Can use string alias
    "Budget": PropertyDefinition(NotionPropertyType.NUMBER, number_format="euro"),
    "Is Urgent": NotionPropertyType.BOOLEAN, # a.k.a. checkbox
    "Start Date": NotionPropertyType.DATE,
    "Priority": PropertyDefinition(
        type=NotionPropertyType.SELECT,
        options=[
            SelectOption("Critical", "red"), 
            "High", # String shorthand for SelectOption("High")
            SelectOption("Medium", "yellow"),
            SelectOption("Low", "green")
        ]
    ),
    "Tags": PropertyDefinition(
        type=NotionPropertyType.MULTI_SELECT,
        options=["Internal", "Client Facing", SelectOption("Q4 Target", "purple")]
    ),
    "Project Lead": PropertyDefinition(type=NotionPropertyType.PEOPLE),
    "Attachment": PropertyDefinition(type=NotionPropertyType.FILES),
    # One-way relation to another database:
    "Related Department": PropertyDefinition(
        type=NotionPropertyType.RELATION,
        relation_database_id=SOME_OTHER_DB_ID 
    ),
    # Two-way relation (Notion will try to create/link 'Related Projects' in SOME_OTHER_DB_ID):
    "Assigned Users": PropertyDefinition(
        type=NotionPropertyType.RELATION,
        relation_database_id=SOME_OTHER_DB_ID, # e.g., Users DB
        two_way_relation_property_name="Projects For User" # Name of property to create/link in Users DB
    ),
    "Project Homepage": NotionPropertyType.URL,
    "Contact Email": NotionPropertyType.EMAIL,
    "Status Detail (JSON)": NotionPropertyType.JSON_TEXT # For storing complex data as string
}

try:
    print("Creating database with simplified schema...")
    my_new_db = client.create_database(
        parent_page_id=PARENT_PAGE_ID_FOR_DBS,
        db_title="Advanced Projects DB",
        schema=simplified_projects_schema,
        if_exists='return_existing' 
    )
    if my_new_db:
        print(f"DB '{my_new_db['title'][0]['plain_text']}' created/retrieved with ID: {my_new_db['id']}")
        # You can inspect my_new_db['properties'] to see the translated Notion schema
        # import json
        # print("Translated Notion Schema:", json.dumps(my_new_db['properties'], indent=2))

except Exception as e:
    print(f"Error: {e}")