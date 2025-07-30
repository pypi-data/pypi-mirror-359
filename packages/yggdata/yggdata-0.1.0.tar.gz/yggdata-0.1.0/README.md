# YggData

YggData is a Python package that provides a hierarchical tree-like data structure called `Yggdrasil` and a set of input validation utilities.

## Installation

```bash
pip install yggdata
```

## Features

### Yggdrasil Tree

`Yggdrasil` is a hierarchical tree-like data structure that extends Python's `dict` with specialized behavior:

- **Automatic Node Creation**: Accessing non-existent keys automatically creates nested nodes
- **Customizable Leaf Behavior**: Configure how duplicate leaf nodes are handled:
  - `overwrite`: Replace existing value (default)
  - `append`: Append to existing value if possible
  - `add`: Add to existing value if both are numeric
  - `subtract`: Subtract new value from existing value if both are numeric
  - `multiply`: Multiply with existing value if both are numeric
  - `divide`: Divide existing value by new value if both are numeric
  - Custom function: Provide your own function to handle value merging
- **Tree Visualization**: Built-in method to print the tree structure
- **Intuitive API**: Uses familiar dictionary syntax with enhanced tree functionality
- **Data Integration**: Methods to create trees from DataFrames and SQL queries

### Input Validation Utilities

YggData also provides a set of input validation utilities for getting user input with validation and retry logic:

- `string_put`: Get string input
- `int_put`: Get integer input with validation
- `float_put`: Get float input with validation
- `choice_put`: Get input from a predefined set of choices
- `bool_put`: Get boolean input (y/n)
- `file_put`: Get a valid file path
- `date_put`: Get a date in YYYY-MM-DD format
- `mail_put`: Get a valid email address

## Usage Examples

### Basic Usage

```python
from yggdata.yggdrasil import Yggdrasil

# Create a new tree
tree = Yggdrasil()

# Add values using dictionary syntax
tree['animals']['mammals']['cats'] = 'Meow'
tree['animals']['mammals']['dogs'] = 'Woof'
tree['animals']['birds']['parrot'] = 'Squawk'

# Access data
print(tree['animals']['mammals']['cats'])  # Output: Meow

# Print the tree structure
tree.print_tree()
```

Output:
```
├── animals
    ├── mammals
    │   ├── cats
    │   │   └── Meow
    │   └── dogs
    │       └── Woof
    └── birds
        └── parrot
            └── Squawk
```

### Using Different Leaf Behaviors

```python
# Create a tree that adds numeric values
from yggdata.yggdrasil import Yggdrasil

add_tree = Yggdrasil(leaf_behavior='add')

# Add values
add_tree['scores']['math'] = 90
add_tree['scores']['math'] = 5  # Will add to existing value

print(add_tree['scores']['math'])  # Output: 95


# Create a tree with custom behavior
def custom_merge(existing, new):
    if isinstance(existing, list):
        return existing + [new]
    else:
        return [existing, new]


list_tree = Yggdrasil(leaf_behavior=custom_merge)
list_tree['data'] = 'first'
list_tree['data'] = 'second'
list_tree['data'] = 'third'

print(list_tree['data'])  # Output: ['first', 'second', 'third']
```

### Adding Branches with add_fiber

```python
from yggdata.yggdrasil import Yggdrasil

tree = Yggdrasil()
tree.add_fiber(['config', 'database', 'username', 'admin'])
tree.add_fiber(['config', 'database', 'password', 'secure123'])
tree.add_fiber(['config', 'server', 'port', 8080])

tree.print_tree()
```

Output:
```
└── config
    ├── database
    │   ├── username
    │   │   └── admin
    │   └── password
    │       └── secure123
    └── server
        └── port
            └── 8080
```

### Using with pandas Series

```python
import pandas as pd
from yggdata.yggdrasil import Yggdrasil

# Create a pandas Series
series = pd.Series(['users', 'john', 'email', 'john@example.com'])

# Add the Series as a fiber
tree = Yggdrasil()
tree.add_fiber(series)

tree.print_tree()
```

Output:
```
└── users
    └── john
        └── email
            └── john@example.com
```

### Creating Trees from pandas DataFrames

```python
import pandas as pd
from yggdata.yggdrasil import Yggdrasil

# Create a sample DataFrame
data = {
    'department': ['IT', 'IT', 'HR', 'HR'],
    'employee': ['Alice', 'Bob', 'Carol', 'Dave'],
    'position': ['Developer', 'Manager', 'Recruiter', 'Director'],
    'salary': [85000, 110000, 75000, 120000]
}
df = pd.DataFrame(data)

# Create a tree from the DataFrame
tree = Yggdrasil.from_dataframe(df)

tree.print_tree()
```

Output:
```
├── IT
│   ├── Alice
│   │   ├── Developer
│   │   │   └── 85000
│   └── Bob
│       ├── Manager
│       │   └── 110000
└── HR
    ├── Carol
    │   ├── Recruiter
    │   │   └── 75000
    └── Dave
        ├── Director
        │   └── 120000
```

### Creating Trees from SQL Queries

```python
import sqlite3
from yggdata.yggdrasil import Yggdrasil

# Create a sample SQLite database
conn = sqlite3.connect(':memory:')
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE products (
    category TEXT,
    subcategory TEXT,
    product TEXT,
    price REAL
)
''')
cursor.executemany('INSERT INTO products VALUES (?, ?, ?, ?)', [
    ('Electronics', 'Computers', 'Laptop', 999.99),
    ('Electronics', 'Phones', 'Smartphone', 699.99),
    ('Clothing', 'Shirts', 'T-Shirt', 19.99),
    ('Clothing', 'Pants', 'Jeans', 49.99)
])
conn.commit()

# Create a tree from a SQL query
query = "SELECT * FROM products"
tree = Yggdrasil.from_sql(query, conn)

tree.print_tree()
```

Output:
```
├── Electronics
│   ├── Computers
│   │   ├── Laptop
│   │   │   └── 999.99
│   └── Phones
│       ├── Smartphone
│       │   └── 699.99
└── Clothing
    ├── Shirts
    │   ├── T-Shirt
    │   │   └── 19.99
    └── Pants
        ├── Jeans
        │   └── 49.99
```

### Using Input Validation Utilities

```python
from yggdata.inputs import int_put, choice_put, bool_put

# Get an integer with validation
age = int_put("Enter your age: ", conditions=[lambda x: x > 0])

# Get a choice from a list
color = choice_put("Choose a color ", ["red", "green", "blue"])

# Get a boolean (y/n)
confirm = bool_put("Are you sure? ")
```

## Testing

The project includes a comprehensive test suite using pytest. To run the tests:

1. Install the required testing dependencies:
   ```bash
   pip install pytest pandas
   ```

2. Run the tests:
   ```bash
   python -m pytest -v tests
   ```

The test suite covers:
- Basic functionality (initialization, dictionary operations)
- All leaf behaviors (overwrite, append, add, subtract, multiply, divide, custom)
- The add_fiber method with both lists and pandas Series
- Creating trees from DataFrames and SQL queries
- Tree visualization with print_tree
- Input validation utilities

## Development Commands

The project includes a command script (`command.sh`) that provides various utilities for development. You can use these commands as follows:

```bash
./command.sh [command]
```

Available commands:

### python
Installs Python 3.12 and the Python venv package:

```bash
./command.sh python
```

### package
Installs required system packages (currently none required):

```bash
./command.sh package
```

### venv
Sets up a virtual environment, activates it, and installs dependencies from requirements.txt:

```bash
./command.sh venv
```

### build
Builds distribution packages:

```bash
./command.sh build
```

### push
Uploads packages to PyPI:

```bash
./command.sh push
```

### test
Runs the test suite:

```bash
./command.sh test
```

You can combine multiple commands:

```bash
./command.sh venv build test
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Author

Cedric Sascha Wagner <cedric.sascha.wagner@outlook.de>
