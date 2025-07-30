"""
viemind_notion_orm.models

This module provides an OOP-style interface for defining and working with Notion databases
as Python classes, similar to Django ORM or SQLAlchemy.
"""

from typing import Dict, Any, List, Optional, Union, Type, get_type_hints
from enum import Enum
from datetime import datetime, date
from .client import NotionClient
from .schema_types import NotionPropertyType, PropertyDefinition, SelectOption, StatusOption
from .exceptions import NotionORMError, SchemaValidationError
import inspect


class Field:
    """Base field class for model attributes"""
    
    def __init__(self, notion_type: NotionPropertyType, **kwargs):
        self.notion_type = notion_type
        self.kwargs = kwargs
        self.property_name = None  # Will be set by metaclass
    
    def to_property_definition(self) -> Union[NotionPropertyType, PropertyDefinition]:
        if self.kwargs:
            return PropertyDefinition(type=self.notion_type, **self.kwargs)
        return self.notion_type


class TitleField(Field):
    """Title field - required for every model"""
    def __init__(self):
        super().__init__(NotionPropertyType.TITLE)


class TextField(Field):
    """Text field for rich text"""
    def __init__(self):
        super().__init__(NotionPropertyType.TEXT)


class NumberField(Field):
    """Number field"""
    def __init__(self, number_format: Optional[str] = None):
        super().__init__(NotionPropertyType.NUMBER, number_format=number_format)


class BooleanField(Field):
    """Boolean field (checkbox)"""
    def __init__(self):
        super().__init__(NotionPropertyType.BOOLEAN)


class DateField(Field):
    """Date field"""
    def __init__(self):
        super().__init__(NotionPropertyType.DATE)


class EmailField(Field):
    """Email field"""
    def __init__(self):
        super().__init__(NotionPropertyType.EMAIL)


class URLField(Field):
    """URL field"""
    def __init__(self):
        super().__init__(NotionPropertyType.URL)


class PhoneField(Field):
    """Phone field"""
    def __init__(self):
        super().__init__(NotionPropertyType.PHONE)


class PeopleField(Field):
    """People field"""
    def __init__(self):
        super().__init__(NotionPropertyType.PEOPLE)


class FilesField(Field):
    """Files field"""
    def __init__(self):
        super().__init__(NotionPropertyType.FILES)


class UniqueIDField(Field):
    """Unique ID field with optional prefix"""
    def __init__(self, prefix: Optional[str] = None):
        kwargs = {}
        if prefix:
            kwargs['unique_id_prefix'] = prefix
        super().__init__(NotionPropertyType.UNIQUE_ID, **kwargs)


class SelectField(Field):
    """Select field with options"""
    def __init__(self, choices: Union[List[str], List[SelectOption], Type[Enum]]):
        options = self._process_choices(choices)
        super().__init__(NotionPropertyType.SELECT, options=options)
    
    def _process_choices(self, choices):
        if inspect.isclass(choices) and issubclass(choices, Enum):
            # Handle Enum class
            return [SelectOption(choice.value) for choice in choices]
        elif isinstance(choices, list):
            # Handle list of strings or SelectOptions
            options = []
            for choice in choices:
                if isinstance(choice, str):
                    options.append(SelectOption(choice))
                elif isinstance(choice, SelectOption):
                    options.append(choice)
                else:
                    raise ValueError(f"Invalid choice type: {type(choice)}")
            return options
        else:
            raise ValueError("Choices must be a list or Enum class")


class MultiSelectField(Field):
    """Multi-select field with options"""
    def __init__(self, choices: Union[List[str], List[SelectOption], Type[Enum]]):
        # Use same logic as SelectField
        if inspect.isclass(choices) and issubclass(choices, Enum):
            options = [SelectOption(choice.value) for choice in choices]
        elif isinstance(choices, list):
            options = []
            for choice in choices:
                if isinstance(choice, str):
                    options.append(SelectOption(choice))
                elif isinstance(choice, SelectOption):
                    options.append(choice)
                else:
                    raise ValueError(f"Invalid choice type: {type(choice)}")
        else:
            raise ValueError("Choices must be a list or Enum class")
        super().__init__(NotionPropertyType.MULTI_SELECT, options=options)


class StatusField(Field):
    """Status field with options"""
    def __init__(self, choices: Union[List[str], List[StatusOption], Type[Enum]]):
        if inspect.isclass(choices) and issubclass(choices, Enum):
            options = [StatusOption(choice.value) for choice in choices]
        elif isinstance(choices, list):
            options = []
            for choice in choices:
                if isinstance(choice, str):
                    options.append(StatusOption(choice))
                elif isinstance(choice, StatusOption):
                    options.append(choice)
                else:
                    raise ValueError(f"Invalid choice type: {type(choice)}")
        else:
            raise ValueError("Choices must be a list or Enum class")
        
        super().__init__(NotionPropertyType.STATUS, options=options)


class RelationField(Field):
    """Relation field to another model"""
    def __init__(self, to: Union[str, Type['NotionModel']], two_way_property: Optional[str] = None):
        self.to = to
        self.two_way_property = two_way_property
        # Note: relation_database_id will be resolved later
        kwargs = {}
        if two_way_property:
            kwargs['two_way_relation_property_name'] = two_way_property
        super().__init__(NotionPropertyType.RELATION, **kwargs)


class ModelMetaclass(type):
    """Metaclass for NotionModel that processes field definitions"""
    
    def __new__(cls, name, bases, attrs):
        # Extract fields from class attributes
        fields = {}
        for key, value in list(attrs.items()):
            if isinstance(value, Field):
                value.property_name = key
                fields[key] = value
                # Remove field from class attributes to avoid conflicts
                attrs.pop(key)
        
        # Store fields in class
        attrs['_fields'] = fields
        attrs['_table_name'] = attrs.get('_table_name', name)
        
        # Validate that there's exactly one title field (only if fields exist)
        if fields:  # Only validate if there are fields defined
            title_fields = [name for name, field in fields.items() if isinstance(field, TitleField)]
            if len(title_fields) == 0:
                raise SchemaValidationError(f"Model {name} must have exactly one TitleField")
            elif len(title_fields) > 1:
                raise SchemaValidationError(f"Model {name} can only have one TitleField, found: {title_fields}")
        
        return super().__new__(cls, name, bases, attrs)


class NotionModel(metaclass=ModelMetaclass):
    """Base class for Notion ORM models"""
    
    def __init__(self, **kwargs):
        self._data = {}
        self._page_id = None
        self._client = None
        
        # Set field values from kwargs
        for field_name, field in self._fields.items():
            if field_name in kwargs:
                setattr(self, field_name, kwargs[field_name])
            else:
                setattr(self, field_name, None)
    
    def __setattr__(self, name, value):
        if name.startswith('_'):
            super().__setattr__(name, value)
        elif hasattr(self, '_fields') and name in self._fields:
            if not hasattr(self, '_data'):
                super().__setattr__('_data', {})
            self._data[name] = value
        else:
            super().__setattr__(name, value)
    
    def __getattribute__(self, name):
        if name.startswith('_') or name == '_fields':
            return super().__getattribute__(name)
        
        fields = super().__getattribute__('_fields')
        if name not in fields:
            return super().__getattribute__(name)
        
        data = super().__getattribute__('_data')
        return data.get(name)
    
    @classmethod
    def get_schema(cls) -> Dict[str, Union[NotionPropertyType, PropertyDefinition]]:
        """Convert model fields to Notion schema"""
        schema = {}
        for field_name, field in cls._fields.items():
            schema[field_name] = field.to_property_definition()
        return schema
    
    @classmethod
    def create_table(cls, client: NotionClient, parent_page_id: str, 
                    table_name: Optional[str] = None, if_exists: str = 'error'):
        """Create the Notion database for this model"""
        table_name = table_name or cls._table_name
        schema = cls.get_schema()
        
        # Resolve relation database IDs
        if hasattr(cls, '_fields'):
            for field_name, field in cls._fields.items():
                if isinstance(field, RelationField):
                    if isinstance(field.to, str):
                        # TODO: Implement model registry to resolve string references
                        raise NotImplementedError("String-based model references not yet implemented")
                    elif hasattr(field.to, '_database_id'):
                        # Update schema with resolved database ID
                        schema[field_name] = PropertyDefinition(
                            type=NotionPropertyType.RELATION,
                            relation_database_id=field.to._database_id,
                            **field.kwargs
                        )
        
        db = client.create_database(
            parent_page_id=parent_page_id,
            db_title=table_name,
            schema=schema,
            if_exists=if_exists
        )
        
        cls._database_id = db['id']
        cls._client = client
        return db
    
    def save(self):
        """Save this instance to Notion"""
        if not hasattr(self.__class__, '_client') or not hasattr(self.__class__, '_database_id'):
            raise NotionORMError("Model must be created/synced with database first")
        
        # Convert model data to Notion format
        properties = self._to_notion_properties()
        
        if self._page_id:
            # Update existing page
            page = self.__class__._client.update_page_properties(self._page_id, properties)
        else:
            # Create new page
            page = self.__class__._client.create_page_in_database(
                database_id=self.__class__._database_id,
                properties=properties
            )
            self._page_id = page['id']
        
        return page
    
    def _to_notion_properties(self) -> Dict[str, Any]:
        """Convert model data to Notion properties format"""
        properties = {}
        
        if not hasattr(self, '_fields') or not hasattr(self, '_data'):
            return properties
            
        for field_name, field in self._fields.items():
            value = self._data.get(field_name)
            if value is None:
                continue
            
            if isinstance(field, TitleField):
                properties[field_name] = {"title": [{"text": {"content": str(value)}}]}
            elif isinstance(field, TextField):
                properties[field_name] = {"rich_text": [{"text": {"content": str(value)}}]}
            elif isinstance(field, NumberField):
                properties[field_name] = {"number": float(value)}
            elif isinstance(field, BooleanField):
                properties[field_name] = {"checkbox": bool(value)}
            elif isinstance(field, DateField):
                if isinstance(value, (date, datetime)):
                    date_str = value.isoformat()
                else:
                    date_str = str(value)
                properties[field_name] = {"date": {"start": date_str}}
            elif isinstance(field, EmailField):
                properties[field_name] = {"email": str(value)}
            elif isinstance(field, URLField):
                properties[field_name] = {"url": str(value)}
            elif isinstance(field, PhoneField):
                properties[field_name] = {"phone_number": str(value)}
            elif isinstance(field, (SelectField, StatusField)):
                properties[field_name] = {"select": {"name": str(value)}}
            elif isinstance(field, MultiSelectField):
                if isinstance(value, (list, tuple)):
                    properties[field_name] = {"multi_select": [{"name": str(v)} for v in value]}
                else:
                    properties[field_name] = {"multi_select": [{"name": str(value)}]}
            elif isinstance(field, RelationField):
                if isinstance(value, (list, tuple)):
                    properties[field_name] = {"relation": [{"id": str(v)} for v in value]}
                else:
                    properties[field_name] = {"relation": [{"id": str(value)}]}
        
        return properties
    
    @classmethod
    def objects(cls):
        """Return a query manager for this model"""
        return QueryManager(cls)
    
    def __repr__(self):
        title_field = None
        for field_name, field in self._fields.items():
            if isinstance(field, TitleField):
                title_field = field_name
                break
        
        title_value = getattr(self, title_field) if title_field else "Untitled"
        return f"<{self.__class__.__name__}: {title_value}>"


class QueryManager:
    """Query manager for NotionModel with advanced filtering and sorting"""
    
    def __init__(self, model_class):
        self.model_class = model_class
        self._filters = None
        self._sorts = []
        self._limit = None
    
    def all(self) -> List[NotionModel]:
        """Get all records"""
        if not hasattr(self.model_class, '_client') or not hasattr(self.model_class, '_database_id'):
            raise NotionORMError("Model must be created/synced with database first")
        
        # Check if we have pre-filtered results (from simple kwargs filtering)
        if hasattr(self, '_prefiltered_results'):
            return self._prefiltered_results
        
        # Build query parameters for direct client.query call
        query_params = {"database_id": self.model_class._database_id}
        
        if self._sorts:
            query_params["sorts"] = self._sorts
            
        if self._limit:
            query_params["page_size"] = self._limit
        
        # For client.query, we need to pass filters as FilterComponent, but we store the dict
        # So we'll use the client's query method differently
        if self._filters:
            # Call client.query with filters as dict using **query_params approach
            pages = self._query_with_dict_filters(**query_params)
        else:
            pages = self.model_class._client.query(**query_params)
        
        return [self._page_to_model(page) for page in pages]
    
    def _query_with_dict_filters(self, **query_params):
        """Helper method to handle dict filters with client query"""
        # Since client.query expects FilterComponent but we have dict, 
        # we need to bypass the conversion and call the underlying Notion API directly
        all_results = []
        start_cursor = None
        
        while True:
            try:
                # Build the actual query params for Notion API
                api_query_params = {
                    "database_id": query_params["database_id"],
                    "start_cursor": start_cursor,
                    "page_size": query_params.get("page_size", 100)
                }
                
                if self._filters:
                    api_query_params["filter"] = self._filters
                    
                if query_params.get("sorts"):
                    api_query_params["sorts"] = query_params["sorts"]
                
                response = self.model_class._client.client.databases.query(**api_query_params)
            except Exception as e:
                print(f"Notion API Error during query: {e}")
                raise e

            all_results.extend(response.get("results", []))

            if not response.get("has_more"):
                break
            start_cursor = response.get("next_cursor")

        return all_results
    
    def filter(self, filter_obj=None, **kwargs):
        """
        Filter records using either filter objects or simple kwargs
        
        Args:
            filter_obj: FilterComponent instance (e.g., Select("status").equals("Active"))
            **kwargs: Simple field=value filters for basic queries
        
        Returns:
            New QueryManager instance with filters applied
        """
        new_query = QueryManager(self.model_class)
        new_query._sorts = self._sorts.copy()
        new_query._limit = self._limit
        
        if filter_obj:
            # Use advanced filter system
            from .filters import FilterComponent
            if isinstance(filter_obj, FilterComponent):
                new_query._filters = filter_obj.to_notion_filter()
            else:
                raise ValueError("filter_obj must be a FilterComponent instance")
        elif kwargs:
            # Use simple field=value filtering (legacy support)
            # For now, just get all and filter in Python (inefficient but simple)
            # TODO: Convert kwargs to proper Notion filters
            all_records = self.all()
            filtered = []
            
            for record in all_records:
                match = True
                for field_name, value in kwargs.items():
                    if getattr(record, field_name) != value:
                        match = False
                        break
                if match:
                    filtered.append(record)
            
            # Return a mock QueryManager with pre-filtered results
            mock_query = QueryManager(self.model_class)
            mock_query._prefiltered_results = filtered
            return mock_query
        
        return new_query
    
    def order_by(self, *field_names):
        """
        Add sorting to the query (ORDER BY equivalent)
        
        Args:
            *field_names: Field names to sort by. Use '-field_name' for descending order.
        
        Returns:
            New QueryManager instance with sorting applied
        
        Example:
            Student.objects.order_by('name')  # Ascending
            Student.objects.order_by('-created_at', 'name')  # Descending created_at, then ascending name
        """
        new_query = QueryManager(self.model_class)
        new_query._filters = self._filters
        new_query._limit = self._limit
        new_query._sorts = self._sorts.copy()
        
        for field_name in field_names:
            if field_name.startswith('-'):
                # Descending order
                actual_field = field_name[1:]
                direction = "descending"
            else:
                # Ascending order
                actual_field = field_name
                direction = "ascending"
            
            new_query._sorts.append({
                "property": actual_field,
                "direction": direction
            })
        
        return new_query
    
    def limit(self, count: int):
        """
        Limit the number of results (similar to SQL LIMIT)
        
        Args:
            count: Maximum number of records to return
        
        Returns:
            New QueryManager instance with limit applied
        """
        new_query = QueryManager(self.model_class)
        new_query._filters = self._filters
        new_query._sorts = self._sorts.copy()
        new_query._limit = count
        
        return new_query
    
    def first(self) -> Optional[NotionModel]:
        """Get the first record matching the query"""
        results = self.limit(1).all()
        return results[0] if results else None
    
    def count(self) -> int:
        """Count the number of records matching the query"""
        # Notion API doesn't support count directly, so we get all and count
        return len(self.all())
    
    def exists(self) -> bool:
        """Check if any records match the query"""
        return self.first() is not None
    
    def create(self, **kwargs) -> NotionModel:
        """Create and save a new record"""
        instance = self.model_class(**kwargs)
        instance.save()
        return instance
    
    def get_or_create(self, defaults=None, **kwargs) -> tuple[NotionModel, bool]:
        """
        Get an existing record or create a new one
        
        Returns:
            (instance, created) tuple where created is True if a new record was created
        """
        try:
            instance = self.filter(**kwargs).first()
            if instance:
                return instance, False
        except:
            pass
        
        # Create new instance
        create_kwargs = kwargs.copy()
        if defaults:
            create_kwargs.update(defaults)
        
        instance = self.create(**create_kwargs)
        return instance, True
    
    def update(self, **kwargs) -> int:
        """
        Update all records matching the query
        
        Returns:
            Number of records updated
        """
        records = self.all()
        count = 0
        
        for record in records:
            for field_name, value in kwargs.items():
                setattr(record, field_name, value)
            record.save()
            count += 1
        
        return count
    
    def delete(self) -> int:
        """
        Delete all records matching the query (archives pages in Notion)
        
        Returns:
            Number of records deleted
        """
        records = self.all()
        count = 0
        
        for record in records:
            if record._page_id and hasattr(self.model_class, '_client'):
                # Archive the page (Notion doesn't support true deletion)
                self.model_class._client.update_page_properties(
                    record._page_id, 
                    {"archived": True}
                )
                count += 1
        
        return count
    
    def _page_to_model(self, page: Dict[str, Any]) -> NotionModel:
        """Convert Notion page to model instance"""
        
        kwargs = {}
        
        for field_name, field in self.model_class._fields.items():
            prop_data = page['properties'].get(field_name, {})
            
            if isinstance(field, TitleField):
                title_data = prop_data.get('title', [])
                kwargs[field_name] = title_data[0]['plain_text'] if title_data else None
            elif isinstance(field, TextField):
                text_data = prop_data.get('rich_text', [])
                kwargs[field_name] = text_data[0]['plain_text'] if text_data else None
            elif isinstance(field, NumberField):
                kwargs[field_name] = prop_data.get('number')
            elif isinstance(field, BooleanField):
                kwargs[field_name] = prop_data.get('checkbox')
            elif isinstance(field, DateField):
                date_data = prop_data.get('date')
                kwargs[field_name] = date_data.get('start') if date_data else None
            elif isinstance(field, EmailField):
                kwargs[field_name] = prop_data.get('email')
            elif isinstance(field, URLField):
                kwargs[field_name] = prop_data.get('url')
            elif isinstance(field, PhoneField):
                kwargs[field_name] = prop_data.get('phone_number')
            elif isinstance(field, (SelectField, StatusField)):
                select_data = prop_data.get('select')
                kwargs[field_name] = select_data.get('name') if select_data else None
            elif isinstance(field, MultiSelectField):
                multi_select_data = prop_data.get('multi_select', [])
                kwargs[field_name] = [item['name'] for item in multi_select_data]
            elif isinstance(field, RelationField):
                relation_data = prop_data.get('relation', [])
                kwargs[field_name] = [item['id'] for item in relation_data]
        
        instance = self.model_class(**kwargs)
        instance._page_id = page['id']
        instance._client = self.model_class._client
        return instance
    
    def join(self, right_model_class, on_relation: str, left_filters=None, right_filters=None):
        """
        Perform a LEFT JOIN with another model (similar to SQL JOIN)
        
        Args:
            right_model_class: The model class to join with
            on_relation: The relation property name in the left model
            left_filters: Additional filters for the left (current) model
            right_filters: Additional filters for the right model
        
        Returns:
            List of left model instances with joined data accessible via ._joined_<relation>
        
        Example:
            # Task.objects.join(Project, on_relation="project").all()
            tasks_with_projects = Task.objects.filter(
                Select("status").equals("Active")
            ).join(Project, "project").all()
        """
        if not hasattr(self.model_class, '_client') or not hasattr(self.model_class, '_database_id'):
            raise NotionORMError("Model must be created/synced with database first")
        
        if not hasattr(right_model_class, '_database_id'):
            raise NotionORMError("Right model must be created/synced with database first")
        
        # Combine current filters with additional left filters
        combined_left_filters = self._filters
        if left_filters:
            from .filters import FilterComponent, AndFilter
            if isinstance(left_filters, FilterComponent):
                if combined_left_filters:
                    # Convert dict back to FilterComponent if needed
                    # This is a simplified approach - in production you'd want better filter composition
                    pass
                else:
                    combined_left_filters = left_filters.to_notion_filter()
        
        # Use the client's join functionality
        joined_results = self.model_class._client.join(
            left_database_id=self.model_class._database_id,
            right_database_id=right_model_class._database_id,
            on_relation=on_relation,
            left_filters=None,  # Would need to convert back from dict - complex
            right_filters=right_filters
        )
        
        # Convert to model instances
        result_instances = []
        for joined_page in joined_results:
            instance = self._page_to_model(joined_page)
            
            # Add joined data as a special attribute
            join_key = f"_joined_{on_relation.replace(' ', '_').lower()}"
            joined_data = joined_page.get(join_key, [])
            
            # Convert joined pages to right model instances
            joined_instances = []
            for joined_item in joined_data:
                joined_instance = right_model_class._page_to_model_static(joined_item)
                joined_instances.append(joined_instance)
            
            setattr(instance, join_key, joined_instances)
            result_instances.append(instance)
        
        return result_instances
    
    def group_by(self, *field_names):
        """
        GROUP BY equivalent - groups records by specified fields
        
        Args:
            *field_names: Field names to group by
        
        Returns:
            Dictionary with grouped results
        
        Example:
            # GROUP BY status
            grouped = Student.objects.group_by('status')
            # Result: {'Active': [student1, student2], 'Inactive': [student3]}
        """
        all_records = self.all()
        grouped_results = {}
        
        for record in all_records:
            # Create a grouping key from the specified fields
            group_key_parts = []
            for field_name in field_names:
                value = getattr(record, field_name, None)
                group_key_parts.append(str(value) if value is not None else 'None')
            
            group_key = '|'.join(group_key_parts) if len(field_names) > 1 else group_key_parts[0]
            
            if group_key not in grouped_results:
                grouped_results[group_key] = []
            grouped_results[group_key].append(record)
        
        return grouped_results
    
    def aggregate(self, **aggregations):
        """
        Perform aggregations on the queryset (similar to SQL aggregate functions)
        
        Args:
            **aggregations: Dict of {result_name: (field_name, function)}
        
        Returns:
            Dictionary with aggregation results
        
        Example:
            # COUNT, AVG, SUM, MIN, MAX equivalents
            stats = Student.objects.aggregate(
                total_count=('id', 'count'),
                avg_grade=('grade', 'avg'),
                max_grade=('grade', 'max')
            )
        """
        all_records = self.all()
        results = {}
        
        for result_name, (field_name, func) in aggregations.items():
            values = []
            
            # Collect values for the field
            for record in all_records:
                value = getattr(record, field_name, None)
                if value is not None:
                    # Try to convert to number for mathematical operations
                    try:
                        if isinstance(value, (int, float)):
                            values.append(value)
                        elif isinstance(value, str) and value.replace('.', '').isdigit():
                            values.append(float(value))
                    except:
                        values.append(value)
            
            # Apply aggregation function
            if func == 'count':
                results[result_name] = len(all_records)
            elif func == 'sum' and values:
                results[result_name] = sum(v for v in values if isinstance(v, (int, float)))
            elif func == 'avg' and values:
                numeric_values = [v for v in values if isinstance(v, (int, float))]
                results[result_name] = sum(numeric_values) / len(numeric_values) if numeric_values else 0
            elif func == 'min' and values:
                results[result_name] = min(values)
            elif func == 'max' and values:
                results[result_name] = max(values)
            else:
                results[result_name] = None
        
        return results 