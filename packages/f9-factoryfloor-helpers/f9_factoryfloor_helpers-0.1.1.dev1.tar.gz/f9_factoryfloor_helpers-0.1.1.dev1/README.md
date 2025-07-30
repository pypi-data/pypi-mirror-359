# FactoryFloor Helpers

A collection of helper tools for FactoryFloor projects.

## Installation

```bash
pip install f9-factoryfloor-helpers
```

## Features

### Context Services

The `context_services` module provides classes for working with Five9 context services:

- `Holiday`: A Pydantic model representing a holiday with a name and date
- `HolidayBuilder`: A builder class for retrieving and formatting holiday information
- `TableBuilder`: A builder class for creating and managing Five9 context service tables

### Environment Utilities

The `environment` module provides utilities for environment-specific configurations:

- `get_base_url`: A function to get the base URL for the Five9 API based on the region

## Usage Examples

### Working with Holidays

```python
from factoryfloor_helpers.context_services import HolidayBuilder

# Create a holiday builder for the UK
holiday_builder = HolidayBuilder("GB")

# Get the next public holidays
holidays = holiday_builder.get_next_public_holidays()

# Print the holidays
for holiday in holidays:
    print(f"{holiday.name}: {holiday_builder.get_date(holiday)}")
```

### Creating Context Service Tables

```python
from factoryfloor_helpers.context_services import TableBuilder
from factoryfloor_helpers.environment import get_base_url
from five9 import RestAdminAPIClient

# Create a Five9 client
f9client = RestAdminAPIClient(
    base_url=get_base_url("US"),
    username="your_username",
    password="your_password",
    domain_id="your_domain_id"
)

# Create a table builder
table_builder = TableBuilder(f9client, dev_mode=True)

# Create a datatable
table = table_builder.create_datatable("MY_TABLE", "My test table")

# Define attributes
attributes = [
    {
        'name': 'ID',
        'type': 'STRING',
        'unique': True,
        'required': True,
    },
    {
        'name': 'NAME',
        'type': 'STRING',
        'unique': False,
        'required': True,
    }
]

# Create attributes
table_builder.create_attributes(table, attributes)

# Create a query
table_builder.create_query(table.id, "MY_QUERY", "My test query", "AND", ["ID"])
```

## License

MIT