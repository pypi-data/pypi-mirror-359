"""
viemind_notion_orm.client

This module contains the main NotionClient class for interacting with the Notion API.
"""
import notion_client
from typing import List, Dict, Any, Optional, Union
from .filters import FilterComponent
from .exceptions import DatabaseExistsError, SchemaValidationError, NotionORMError
from .schema_types import NotionPropertyType, PropertyDefinition, SelectOption, StatusOption

class NotionClient:
    """
    Main entry point for the Notion ORM library.
    Provides methods to create, query, and join Notion databases.
    """
    def __init__(self, auth: str):
        """
        Initializes the NotionClient.

        Args:
            auth (str): The Notion integration token.
        """
        self.client = notion_client.Client(auth=auth)
        self._db_schema_cache: Dict[str, Dict[str, Any]] = {} # Cache for database schemas

    def _get_db_schema(self, database_id: str, use_cache: bool = True) -> Dict[str, Any]:
        """
        Retrieves and caches the schema of a database.
        The schema contains property definitions including their IDs.
        """
        if use_cache and database_id in self._db_schema_cache:
            return self._db_schema_cache[database_id]

        try:
            schema = self.client.databases.retrieve(database_id=database_id)
            if use_cache:
                self._db_schema_cache[database_id] = schema
            return schema
        except notion_client.APIResponseError as e:
            print(f"Notion API Error retrieving schema for DB {database_id}: {e}")
            raise

    def _get_all_related_page_ids_for_property(self, page_id: str, property_id: str) -> List[str]:
        """
        Retrieves all related page IDs for a specific paginated relation property on a page.
        """
        related_ids: List[str] = []
        start_cursor: Optional[str] = None
        while True:
            try:
                prop_item = self.client.pages.properties.retrieve(
                    page_id=page_id,
                    property_id=property_id,
                    start_cursor=start_cursor,
                    page_size=100 # Max page size
                )
            except notion_client.APIResponseError as e:
                print(f"Notion API Error retrieving property {property_id} for page {page_id}: {e}")
                # Depending on the error, we might want to return what we have or raise
                return related_ids # Or raise e

            if prop_item.get("object") == "list": # Paginated property
                for item in prop_item.get("results", []):
                    if item.get("type") == "relation" and item.get("relation"):
                        related_ids.append(item["relation"]["id"])
            elif prop_item.get("type") == "relation": # Non-paginated (or first page of) relation property
                 for rel_obj in prop_item.get("relation", []):
                     if rel_obj.get("id"):
                        related_ids.append(rel_obj["id"])

            if not prop_item.get("has_more"):
                break
            start_cursor = prop_item.get("next_cursor")
        return list(set(related_ids))

    def query(self,
              database_id: str,
              filters: Optional[FilterComponent] = None,
              sorts: Optional[List[Dict[str, str]]] = None,
              page_size: int = 100) -> List[Dict[str, Any]]: # Added page_size
        """
        Queries a Notion database with optional filters and sorts.
        Handles pagination automatically to return all matching results.
        ... (rest of docstring same)
        """
        all_results: List[Dict[str, Any]] = []
        start_cursor: Optional[str] = None

        notion_filter_payload: Optional[Dict[str, Any]] = None
        if filters:
            notion_filter_payload = filters.to_notion_filter()

        while True:
            try:
                # Build query parameters, excluding None values
                query_params = {
                    "database_id": database_id,
                    "start_cursor": start_cursor,
                    "page_size": min(page_size, 100)
                }
                
                if notion_filter_payload is not None:
                    query_params["filter"] = notion_filter_payload
                    
                if sorts:
                    query_params["sorts"] = sorts
                
                response = self.client.databases.query(**query_params)
            except notion_client.APIResponseError as e:
                print(f"Notion API Error during query: {e}")
                print(f"Request details - DB ID: {database_id}, Filter: {notion_filter_payload}, Sorts: {sorts}")
                raise e

            all_results.extend(response.get("results", []))

            if not response.get("has_more"):
                break
            start_cursor = response.get("next_cursor")

        return all_results

    def join(self,
             left_database_id: str,
             right_database_id: str,
             on_relation: str,
             left_filters: Optional[FilterComponent] = None, # Allow filtering left table
             right_filters: Optional[FilterComponent] = None # Allow filtering right table
            ) -> List[Dict[str, Any]]:
        """
        Performs a LEFT JOIN operation between two Notion databases based on a relation property.
        Fetches data from the left database (optionally filtered) and enriches it with related items
        from the right database (optionally filtered). Handles paginated relations robustly.

        Args:
            left_database_id (str): The ID of the primary (left) database.
            right_database_id (str): The ID of the database to join with (right).
            on_relation (str): The name of the 'Relation' property in the left_database
                               that links to the right_database.
            left_filters (FilterComponent, optional): Filters to apply to the left database query.
            right_filters (FilterComponent, optional): Filters to apply to the right database query.


        Returns:
            List[Dict[str, Any]]: A list of page objects from the left_database,
                                  each augmented with a new key (e.g., '_joined_relation_name')
                                  containing a list of related page objects from the right_database.
        """
        # 1. Fetch schema for the left database to get property IDs
        left_db_schema = self._get_db_schema(left_database_id)
        relation_property_id: Optional[str] = None
        for prop_name, prop_details in left_db_schema.get("properties", {}).items():
            if prop_name == on_relation:
                if prop_details.get("type") == "relation":
                    relation_property_id = prop_details.get("id")
                    break
                else:
                    raise ValueError(f"Property '{on_relation}' in database '{left_database_id}' is not a relation type.")

        if not relation_property_id:
            raise ValueError(f"Relation property '{on_relation}' not found in database '{left_database_id}'.")

        # 2. Fetch pages from the left database (potentially filtered)
        left_pages = self.query(database_id=left_database_id, filters=left_filters)

        # 3. Fetch all pages from the right database (potentially filtered) and create a lookup map
        right_pages_list = self.query(database_id=right_database_id, filters=right_filters)
        right_pages_map = {page['id']: page for page in right_pages_list}

        joined_results: List[Dict[str, Any]] = []

        # 4. Process each page from the left database
        for left_page in left_pages:
            current_joined_page = left_page.copy()
            related_right_items: List[Dict[str, Any]] = []

            # Get relation data from the left page object
            relation_property_data = current_joined_page['properties'].get(on_relation)

            if relation_property_data and relation_property_data['type'] == 'relation':
                relation_ids_on_page = [rel['id'] for rel in relation_property_data.get('relation', [])]

                # If the relation property indicates `has_more`, fetch all relations for this property
                if relation_property_data.get('has_more', False):
                    print(f"Info: Relation property '{on_relation}' for page ID '{left_page['id']}' "
                          f"has more items. Fetching all via property_id '{relation_property_id}'.")
                    try:
                        all_relation_ids_for_prop = self._get_all_related_page_ids_for_property(
                            left_page['id'],
                            relation_property_id
                        )
                        # The IDs from has_more might not be on the page object itself,
                        # so we use the result of the dedicated property fetch.
                        relation_ids_to_join = all_relation_ids_for_prop
                    except Exception as e:
                        print(f"Warning: Failed to fetch all relations for page {left_page['id']}, property {on_relation}. Using partial data. Error: {e}")
                        relation_ids_to_join = relation_ids_on_page # Fallback to page data
                else:
                    relation_ids_to_join = relation_ids_on_page

                for r_id in relation_ids_to_join:
                    if r_id in right_pages_map:
                        related_right_items.append(right_pages_map[r_id])

            join_key = f"_joined_{on_relation.replace(' ', '_').lower()}"
            current_joined_page[join_key] = related_right_items
            joined_results.append(current_joined_page)

        return joined_results

    def _validate_db_schema(self, schema: Dict[str, Dict[str, Any]]):
        """Basic validation for database schema structure."""
        if not isinstance(schema, dict):
            raise SchemaValidationError("Schema must be a dictionary.")
        for prop_name, prop_definition in schema.items():
            if not isinstance(prop_name, str) or not prop_name:
                raise SchemaValidationError(f"Property name '{prop_name}' must be a non-empty string.")
            if not isinstance(prop_definition, dict):
                raise SchemaValidationError(
                    f"Definition for property '{prop_name}' must be a dictionary."
                )
            # Check for at least one type key (e.g., "title": {}, "rich_text": {}, etc.)
            type_keys = ["title", "rich_text", "number", "select", "multi_select",
                           "status", "date", "checkbox", "url", "email", "phone_number",
                           "files", "relation", "formula", "rollup", "people",
                           "created_by", "created_time", "last_edited_by", "last_edited_time"]
            if not any(key in prop_definition for key in type_keys):
                 raise SchemaValidationError(
                    f"Property definition for '{prop_name}' is missing a valid type key (e.g., 'title': {{}}). "
                    f"Got: {prop_definition.keys()}"
                )
            # More detailed validation per type could be added here or using a library like Pydantic.

    def create_database(self,
                        parent_page_id: str,
                        db_title: str,
                        schema: Dict[str, Union[PropertyDefinition, NotionPropertyType, str]],
                        if_exists: str = 'error' # 'error', 'skip', 'return_existing'
                       ) -> Optional[Dict[str, Any]]:
        """
        Creates a new Notion database using a simplified schema definition.

        Args:
            parent_page_id (str): ID of the parent page.
            db_title (str): Title for the new database.
            schema (Dict): Simplified schema dictionary. Keys are property names,
                           values are NotionPropertyType, string type, or PropertyDefinition instances.
            if_exists (str): Action if DB with same title exists under parent:
                             'error' (default), 'skip', 'return_existing'.
        Returns:
            Optional[Dict[str, Any]]: The created database object, or None if skipped.
        """
        try:
            # Translate the simplified schema to Notion's format
            notion_api_schema = self._translate_simplified_schema(schema)
        except SchemaValidationError as e: # Catch validation errors from translator
            raise e
        except ValueError as e: # Catch other ValueErrors from PropertyDefinition
            raise SchemaValidationError(str(e))


        if if_exists == 'error' or if_exists == 'return_existing':
            try:
                # Notion API doesn't allow filtering databases by parent directly in a search.
                # We list children of the parent page.
                children_response = self.client.blocks.children.list(block_id=parent_page_id)
                for child in children_response.get("results", []):
                    if child.get("type") == "child_database":
                        # To get the title, we'd need to retrieve the database object itself,
                        # or assume the 'child_database' block has a title (it does not directly).
                        # This makes "if_exists" by title check a bit more involved.
                        # A simpler check: if *any* child_database exists, and then rely on Notion's
                        # own behavior if names collide (Notion allows duplicate DB names).
                        # For a true title check, we need to retrieve each child_database.
                        # Let's retrieve and check title if it's a child_database block.
                        db_block_id = child.get("id")
                        try:
                            # This retrieves the database object using the block ID which is also the DB ID
                            # for child_database blocks.
                            existing_db_candidate = self.client.databases.retrieve(database_id=db_block_id)
                            existing_db_title_parts = existing_db_candidate.get("title", [])
                            if existing_db_title_parts and isinstance(existing_db_title_parts, list):
                                existing_db_title = "".join(t.get("plain_text","") for t in existing_db_title_parts)
                                if existing_db_title == db_title:
                                    if if_exists == 'error':
                                        print(f"Database '{db_title}' already exists (ID: {existing_db_candidate['id']}). Skipping creation.")
                                        return None
                                    elif if_exists == 'return_existing':
                                        print(f"Database '{db_title}' already exists (ID: {existing_db_candidate['id']}). Returning existing.")
                                        return existing_db_candidate
                                    # 'error' case handled below implicitly if not for this explicit check
                        except notion_client.APIResponseError as e_retrieve:
                            print(f"Warning: Could not retrieve child database {db_block_id} for title check: {e_retrieve}")
                            pass # Continue checking other children
            except notion_client.APIResponseError as e_children:
                print(f"Warning: Could not list children of parent {parent_page_id} for exists check: {e_children}")
                # Proceed to create, or handle error based on policy

        parent_payload = {"type": "page_id", "page_id": parent_page_id}
        title_payload = [{"type": "text", "text": {"content": db_title}}]

        try:
            created_db = self.client.databases.create(
                parent=parent_payload,
                title=title_payload,
                properties=notion_api_schema # Use translated schema
            )
            return created_db
        except notion_client.APIResponseError as e:
            if if_exists == 'error' and ("conflict" in str(e).lower() or "already exists" in str(e).lower()):
                raise DatabaseExistsError(db_title, parent_page_id, "Unknown (API error suggests existence)") from e
            print(f"Notion API Error during database creation: {e}")
            print(f"Attempted Notion API Schema: {notion_api_schema}")  # Helpful for debugging
            raise NotionORMError(f"Database creation failed for '{db_title}': {e}") from e

    # --- Page CRUD Operations ---
    def create_page_in_database(self,
                                database_id: str,
                                properties: Dict[str, Any],
                                children: Optional[List[Dict[str,Any]]] = None, # For page content
                                icon: Optional[Dict[str,Any]] = None, # e.g., {"emoji": "📄"}
                                cover: Optional[Dict[str,Any]] = None, # e.g., {"external": {"url": "..."}}
                               ) -> Dict[str, Any]:
        """
        Creates a new page within a specified database.

        Args:
            database_id (str): The ID of the database to add the page to.
            properties (Dict[str, Any]): Dictionary of property values for the new page.
                                         The structure must match Notion API requirements.
                                         Example: {"Name": {"title": [{"text": {"content": "New Task"}}]},
                                                   "Status": {"status": {"name": "To Do"}}}
            children (List[Dict[str, Any]], optional): List of block objects for page content.
            icon (Dict[str, Any], optional): Page icon object.
            cover (Dict[str, Any], optional): Page cover object.


        Returns:
            Dict[str, Any]: The Notion page object of the newly created page.
        """
        payload = {
            "parent": {"database_id": database_id},
            "properties": properties
        }
        if children:
            payload["children"] = children
        if icon:
            payload["icon"] = icon
        if cover:
            payload["cover"] = cover

        try:
            return self.client.pages.create(**payload)
        except notion_client.APIResponseError as e:
            print(f"Notion API Error creating page in DB {database_id}: {e}")
            print(f"Payload: {payload}")
            raise

    def update_page_properties(self, page_id: str, properties: Dict[str, Any]) -> Dict[str, Any]:
        """
        Updates specific properties of an existing page.

        Args:
            page_id (str): The ID of the page to update.
            properties (Dict[str, Any]): Dictionary of property values to update.
                                         Structure must match Notion API requirements.

        Returns:
            Dict[str, Any]: The updated Notion page object.
        """
        try:
            return self.client.pages.update(page_id=page_id, properties=properties)
        except notion_client.APIResponseError as e:
            print(f"Notion API Error updating page {page_id}: {e}")
            print(f"Properties payload: {properties}")
            raise

    def archive_page(self, page_id: str) -> Dict[str, Any]:
        """
        Archives a page (effectively 'deleting' it from most views).

        Args:
            page_id (str): The ID of the page to archive.

        Returns:
            Dict[str, Any]: The archived Notion page object.
        """
        try:
            return self.client.pages.update(page_id=page_id, archived=True)
        except notion_client.APIResponseError as e:
            print(f"Notion API Error archiving page {page_id}: {e}")
            raise

    def unarchive_page(self, page_id: str) -> Dict[str, Any]:
        """
        Restores (un-archives) a previously archived page.

        Args:
            page_id (str): The ID of the page to unarchive.

        Returns:
            Dict[str, Any]: The restored Notion page object.
        """
        try:
            return self.client.pages.update(page_id=page_id, archived=False)
        except notion_client.APIResponseError as e:
            print(f"Notion API Error unarchiving page {page_id}: {e}")
            raise

    def delete_block(self, block_id: str) -> Dict[str, Any]:
        """
        Deletes a block (page, database, or any other block type).
        Warning: This is a permanent deletion if the block is a top-level page
                 not in a parent's trash, or if it's a child block.
                 For pages in databases, archiving is generally preferred.

        Args:
            block_id (str): The ID of the block to delete.

        Returns:
            Dict[str, Any]: The API response, typically the deleted block object.
        """
        try:
            return self.client.blocks.delete(block_id=block_id)
        except notion_client.APIResponseError as e:
            print(f"Notion API Error deleting block {block_id}: {e}")
            raise

    def _translate_simplified_schema(self, simplified_schema: Dict[
        str, Union[PropertyDefinition, NotionPropertyType, str]]) -> Dict[str, Dict[str, Any]]:
        """
        Translates a simplified schema definition into Notion's API property schema format.

        Args:
            simplified_schema: A dictionary where keys are property names and values are
                               either a NotionPropertyType enum, a string representation of the type,
                               or a PropertyDefinition instance for more complex types.
                               Example:
                               {
                                   "Project Name": NotionPropertyType.TITLE,
                                   "Description": "text",
                                   "Budget": PropertyDefinition(NotionPropertyType.NUMBER, number_format="dollar"),
                                   "Priority": PropertyDefinition(
                                       NotionPropertyType.SELECT,
                                       options=[SelectOption("High", "red"), "Medium", SelectOption("Low")]
                                   ),
                                   "Related Tasks": PropertyDefinition(
                                       NotionPropertyType.RELATION,
                                       relation_database_id="tasks_db_id_here"
                                   )
                               }

        Returns:
            A dictionary in the format required by Notion's databases.create API.
        """
        notion_schema = {}
        has_title = False

        for name, definition_input  in simplified_schema.items():
            prop_def: PropertyDefinition
            if isinstance(definition_input , PropertyDefinition):
                prop_def = definition_input
            elif isinstance(definition_input , (NotionPropertyType, str)):
                prop_def = PropertyDefinition(type=definition_input )  # Basic type
            else:
                raise SchemaValidationError(
                    f"Invalid schema definition for property '{name}'. "
                    "Value must be a NotionPropertyType, string type, or PropertyDefinition instance."
                )

            prop_type_enum = prop_def.type
            notion_prop_config: Dict[str, Any] = {}

            if prop_type_enum == NotionPropertyType.TITLE:
                notion_prop_config = {"title": {}}
                has_title = True
            elif prop_type_enum == NotionPropertyType.TEXT or prop_type_enum == NotionPropertyType.JSON_TEXT:
                notion_prop_config = {"rich_text": {}}
            elif prop_type_enum in [NotionPropertyType.NUMBER, NotionPropertyType.INTEGER, NotionPropertyType.FLOAT]:
                num_config = {}
                if prop_def.number_format:
                    num_config["format"] = prop_def.number_format
                notion_prop_config = {"number": num_config if num_config else {}}
            elif prop_type_enum == NotionPropertyType.BOOLEAN:
                notion_prop_config = {"checkbox": {}}
            elif prop_type_enum == NotionPropertyType.DATE or prop_type_enum == NotionPropertyType.DATETIME:
                notion_prop_config = {"date": {}}
            elif prop_type_enum == NotionPropertyType.URL:
                notion_prop_config = {"url": {}}
            elif prop_type_enum == NotionPropertyType.EMAIL:
                notion_prop_config = {"email": {}}
            elif prop_type_enum == NotionPropertyType.PHONE:
                notion_prop_config = {"phone_number": {}}
            elif prop_type_enum == NotionPropertyType.PEOPLE:
                notion_prop_config = {"people": {}}
            elif prop_type_enum == NotionPropertyType.FILES:
                notion_prop_config = {"files": {}}
            elif prop_type_enum in [NotionPropertyType.SELECT, NotionPropertyType.MULTI_SELECT,
                                    NotionPropertyType.STATUS]:
                options_payload = []
                if prop_def.options:
                    for opt in prop_def.options:
                        if isinstance(opt, (SelectOption, StatusOption)):
                            options_payload.append(opt.to_notion_option())
                        elif isinstance(opt, str):  # Simple string option name
                            options_payload.append(SelectOption(opt).to_notion_option())
                        else:
                            raise SchemaValidationError(f"Invalid option type for '{name}': {opt}")

                type_key = prop_type_enum.value  # "select", "multi_select", "status"
                notion_prop_config = {type_key: {"options": options_payload}}

                # For Status, Notion can also have 'groups', but defining them via API at creation
                # is more complex as it requires option IDs which are not known beforehand.
                # Users can arrange options into groups via UI later.
            elif prop_type_enum == NotionPropertyType.RELATION:
                # prop_def.relation_database_id will now be correct
                if not prop_def.relation_database_id:
                    raise SchemaValidationError(f"Relation property '{name}' is missing 'relation_database_id'.")

                relation_config: Dict[str, Any] = {"database_id": prop_def.relation_database_id}
                # prop_def.two_way_relation_property_name will now be correct
                if prop_def.two_way_relation_property_name:
                    relation_config["type"] = "dual_property"
                    relation_config["dual_property"] = {
                        "synced_property_name": prop_def.two_way_relation_property_name
                    }
                else:
                    relation_config["type"] = "single_property"
                    relation_config["single_property"] = {}
                notion_prop_config = {"relation": relation_config}
            elif prop_type_enum == NotionPropertyType.UNIQUE_ID:
                unique_id_config = {}
                if prop_def.unique_id_prefix:
                    unique_id_config["prefix"] = prop_def.unique_id_prefix
                notion_prop_config = {"unique_id": unique_id_config}
            else:
                raise SchemaValidationError(f"Unsupported simplified property type: {prop_type_enum} for '{name}'")

            notion_schema[name] = notion_prop_config

        if not has_title and not any(v.get("title") for v in notion_schema.values()):
            raise SchemaValidationError(
                "The database schema must include at least one 'title' property. "
                "Define a property with type NotionPropertyType.TITLE."
            )

        return notion_schema