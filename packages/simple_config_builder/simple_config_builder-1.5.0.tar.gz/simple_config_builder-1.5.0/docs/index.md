# Welcome to Simple Config Builder

This is a simple tool to help you build a configuration file for your project.

## Installation

```bash
pip install simple_config_builder
```

## Getting Started
When writing your library configuration files are often a necessity. 
Instead of using a dictionary or a class to store your configuration,
you can build config classes using this tool.

```python
from simple_config_builder import Configclass, Field

class MyConfig(Configclass):
    name: str = "John Doe"
    age: int = 30
    is_student: bool = False
    grades: int = Field(gt=0, lt=100)
```

This will create a class with the specified fields and default values and validation rules.

For IO, you can use 
```python
from simple_config_builder.configparser import Configparser
from simple_config_builder import Configclass, Field

@configclass
class MyConfig:
    name: str = "John Doe"
    age: int = 30
    is_student: bool = False
    grades: int = Field(gt=0, lt=100, default=90)

# Load and parse the configuration file
config = Configparser("config.json")

# Save the configuration file
config.save()

# reload the configuration file
config.reload()

# Set a config object
config['my_config'] = MyConfig("John Doe", 30, False, 90)
```

Apart from that autosave and autoreload is supported. 

### Callables
You can also use callables as fields in the config class. 
```python
from simple_config_builder import Field, Configclass
from collections.abc import Callable

@configclass
class MyConfig:
    name: str = "John Doe"
    age: int = 30
    is_student: bool = False
    grades: int = Field(gt=0, lt=100, default=90)
    student_name_calling: Callable
```
The callables are saved in the configuration files as package.module
name and function name. If the module is not in the python path,
a file_path is saved additionally.

```json
{
    "name": "John Doe",
    "age": 30,
    "is_student": false,
    "grades": 90,
    "student_name_calling": 
    {
      "module": "package.module",
      "function": "function_name",
      "file_path": "path/to/file"
    }
}
```


### Typing
Because the Configclass is based on pydantic, you can use all the features of pydantic,
like type hints, validation, and more.
You can use the `Field` from pydantic to define constraints on the fields.

```python
from simple_config_builder import Configclass


class MyConfig(Configclass):
    name: str = "John Doe"
    age: int = 30
    is_student: bool = False
    grades: int = config_field(gt=0, lt=100)

    
c = MyConfig(
    name="John Doe",
    age=30,
    is_student=False,
    grades=90
)    

c.name = "Jane Doe"

def my_function(config: Configclass):
    print(config.name)

my_function(MyConfig())

```

## License
This project is licensed under the MIT License - see the [LICENSE](license.md) file for details.