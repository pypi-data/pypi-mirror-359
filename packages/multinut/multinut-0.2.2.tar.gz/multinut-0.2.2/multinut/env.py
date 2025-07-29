import os.path as op
from typing import Optional, Callable, Any
from enum import Enum
from dotenv import dotenv_values
import json

NO_DEFAULT = object()  # Used to indicate no default value was provided

class Modes(Enum):
    """
        Enum for different environment modes.
        Note: they are what i commonly use, feel free to use a own enum or directly use strings.
    """
    PRODUCTION = ".production"
    DEVELOPMENT = ".development"
    TESTING = ".testing"
    STAGING = ".staging"
    LOCAL = ""

class Environment:
    """
        Environment class for managing environment variables.
        This class loads environment variables from a file and provides access to them.
        It supports different modes (e.g., production, development) by appending the mode to the file name.
        It uses a singleton pattern to ensure only one instance exists.
        The environment variables can be accessed directly or through a `get` method that allows for casting and default values.

        Usage:
        ```python
        env = Environment(env_file_name='.env', mode=Modes.DEVELOPMENT)
        value = env.get('MY_VARIABLE', default='default_value', cast=str)
        ```
        
        This will load the environment variables from '.env.development' and return the value of 'MY_VARIABLE'.
        If 'MY_VARIABLE' is not found, it will return 'default_value'.
        If the environment file does not exist, it raises a FileNotFoundError.
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, *, env_file_name: Optional[str] = None, env_file_path: Optional[str] = None, mode: Optional[Enum|str] = Modes.LOCAL, suppress_file_not_found: bool = False):        
        self.__initialize(env_file_name, env_file_path, mode, suppress_file_not_found)
        
    def __initialize(self, env_file_name: str, env_file_path: str, mode: Enum|str, suppress_file_not_found: bool):
        if hasattr(self, '__initialized') and self.__initialized:
            return
        
        self.__env_file_path = self.__resolve_file_path(env_file_name, env_file_path, mode)
        
        if not op.exists(self.__env_file_path) and not suppress_file_not_found:
            raise FileNotFoundError(f"Environment file '{self.__env_file_path}' does not exist.")
        
        self.__values = dotenv_values(self.__env_file_path)
        self.__initialized = True

    def __resolve_file_path(self, env_file_name: str, env_file_path: str, mode: Enum|str) -> str:
        """
            Resolves the file path for the environment file.
        """
        if isinstance(mode, Enum):
            mode = mode.value
        else:
            mode = f".{mode}" if mode else ""
            
        if mode != "" and not mode.startswith('.'):
            mode = f".{mode}"
        
        file = (env_file_name or '.env') + mode
        
        if env_file_path:
            return op.join(env_file_path, file)
        
        return file
    
    @property
    def env_file_path(self) -> str:
        """
            Returns the path to the environment file.
            This is the file from which environment variables are loaded.
            If no file was specified, it defaults to '.env'.
            If a mode is specified, it appends the mode to the file name.
            Example: '.env.production', '.env.development', etc.
            If the file was not found, it raises a FileNotFoundError unless suppressed.
            Returns None if no file was specified or found.
        """
        return self.__env_file_path if hasattr(self, '_Environment__env_file_path') else None
    
    @property
    def values(self) -> dict:
        """
            Direct access to environment variables.
            Returns a dictionary of all environment variables loaded.
            Use with caution as it bypasses any casting or default values.
            Prefer using `get` method for safer access.
        """
        return self.__values
    
    def get(self, key: str, default: Optional[Any] = NO_DEFAULT, cast: Optional[Callable] = lambda x: x) -> Any:
        """
            Get the value of an environment variable.
            If the variable is not found, it returns the default value.
            If no default is provided, it raises a KeyError.
            If a cast function is provided, it applies the cast to the value before returning.
        """
        
        if default is NO_DEFAULT:
            return cast(self.__values.get(key))
        
        return cast(self.__values.get(key, default))
    
    def __getattribute__(self, name: str) -> Any:
        if name.startswith("_") or name in super().__dir__():
            return super().__getattribute__(name)
        return self.get(name)

    def __getitem__(self, key: str):
        return self.get(key)
    

def cast_bool(value: str) -> bool:
    return value.strip().lower() in ("1", "true", "yes", "on")

def cast_int(value: str) -> int:
    return int(value.strip())

def cast_float(value: str) -> float:
    return float(value.strip())

def cast_str(value: str) -> str:
    return str(value)

def cast_list(value: str) -> list:
    return [item.strip() for item in value.split(",")]

def cast_tuple(value: str) -> tuple:
    return tuple(item.strip() for item in value.split(","))

def cast_dict(value: str) -> dict:
    return json.loads(value)

def cast_none_or_str(value: str):
    if value.strip().lower() in ("null", "none"):
        return None
    return value
