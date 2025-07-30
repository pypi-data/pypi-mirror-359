"""
Table-related classes for context services.
"""

import string
import random
from typing import List, Dict, Any
from five9 import RestAdminAPIClient
from five9.models.context_services_model import Datatable, Attribute


class TableBuilder:
    """
    Builder class for creating and managing Five9 context service tables.
    
    This class provides methods to create datatables, attributes, and queries
    in Five9 context services.
    
    Attributes:
        f9client: The Five9 REST Admin API client
        dev_mode: Whether to run in development mode (adds random suffix to names)
        dev_id: Random string used as suffix in dev mode
    """
    
    def __init__(self, f9client: RestAdminAPIClient, dev_mode: bool = False):
        """
        Initialize the TableBuilder with a Five9 client.
        
        Args:
            f9client: The Five9 REST Admin API client
            dev_mode: Whether to run in development mode
        """
        self.f9client = f9client
        self.dev_mode = dev_mode
        self.dev_id = self._gen_rnd_string() if dev_mode else ""
    
    def create_datatable(self, name: str, description: str) -> Datatable:
        """
        Create a new datatable in Five9 context services.
        
        Args:
            name: The name of the datatable
            description: The description of the datatable
            
        Returns:
            The created Datatable object
        """
        new_table = Datatable(
            dataTableName=self._dev_check(name),
            dataTableDescription=description
        )
        return self.f9client.context_services.add_datatable(new_table)
    
    def create_attributes(self, datatable: Datatable, attributes: List[Dict[str, Any]]) -> List[Attribute]:
        """
        Create multiple attributes for a datatable.
        
        Args:
            datatable: The datatable to add attributes to
            attributes: List of attribute definitions
            
        Returns:
            List of created Attribute objects
        """
        new_attributes = []
        for attribute in attributes:
            new_attribute = Attribute(
                dataTableId=datatable.id,
                attributeName=attribute['name'],
                dataType=attribute['type'],
                attributeMinimumValue='MIN_VALUE',
                attributeMaximumValue='MAX_VALUE',
                unique=attribute.get('unique', False),
                containsSensitiveData=attribute.get('required', False)
            )
            new_attributes.append(self.f9client.context_services.add_attribute(new_attribute))
        return new_attributes
    
    def create_attribute(self, datatable: Datatable, name: str, data_type: str, 
                        case_sensitive: bool = False, unique: bool = False) -> Attribute:
        """
        Create a single attribute for a datatable.
        
        Args:
            datatable: The datatable to add the attribute to
            name: The name of the attribute
            data_type: The data type of the attribute
            case_sensitive: Whether the attribute is case sensitive
            unique: Whether the attribute values must be unique
            
        Returns:
            The created Attribute object
        """
        new_attribute = Attribute(
            dataTableId=datatable.id,
            attributeName=self._dev_check(name),
            dataType=data_type,
            attributeDefaultValue='DEFAULT_VALUE',
            attributeMinimumValue='MIN_VALUE',
            attributeMaximumValue='MAX_VALUE',
            unique=unique,
            containsSensitiveData=case_sensitive
        )
        return self.f9client.context_services.add_attribute(new_attribute)
    
    def create_query(self, datatable_id: str, query_name: str, 
                    query_description: str, query_type: str, attr_names: List[str]) -> str:
        """
        Create a query for a datatable.
        
        Args:
            datatable_id: The ID of the datatable
            query_name: The name of the query
            query_description: The description of the query
            query_type: The type of query (e.g., 'AND', 'OR')
            attr_names: List of attribute names to include in the query
            
        Returns:
            The ID of the created query
        """
        query_id = self.f9client.context_services.create_query(
            datatable_id, 
            self._dev_check(query_name), 
            query_description
        )
        composite_filter_id = self.f9client.context_services.create_composite_filter(
            datatable_id, 
            query_id, 
            query_type
        )

        for attr in attr_names:
            attribute_id = self.f9client.context_services.get_attribute_by_name(datatable_id, attr)
            self.f9client.context_services.create_property_filter(
                datatable_id, 
                query_id, 
                composite_filter_id, 
                attribute_id, 
                attr, 
                'EQUAL'
            )
        
        return query_id
    
    def _dev_check(self, value: str) -> str:
        """
        Add a random suffix to a value if in dev mode.
        
        Args:
            value: The original value
            
        Returns:
            The value with a suffix if in dev mode, otherwise the original value
        """
        if self.dev_mode:
            return f"{value}_{self.dev_id}"
        return value
    
    def _gen_rnd_string(self, length: int = 8) -> str:
        """
        Generate a random string of uppercase letters.
        
        Args:
            length: The length of the string to generate
            
        Returns:
            A random string
        """
        letters = string.ascii_uppercase
        return ''.join(random.choice(letters) for _ in range(length))