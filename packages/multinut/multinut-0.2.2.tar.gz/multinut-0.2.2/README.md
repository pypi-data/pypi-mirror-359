# `multinut`

The multitool nobody asked for. Includes stuff and so.

---

## `multinut.env`

A simple but flexible environment loader.

Supports `.env` file parsing with optional mode suffixes (e.g. `.env.production`, `.env.testing`, etc.), lazy loading, and dynamic access.

### Features

* Mode-based config support (`.env.production`, `.env.testing`, etc.)
* Access via:

  * `env["KEY"]`
  * `env.get("KEY", ...)`
  * `env.KEY`
* Optional type casting (`str`, `bool`, `list`, `dict`, etc.)
* Sane default handling
* Does **not** mutate `os.environ`

---

### Use cases

* Loading `.env` files in mode-aware Python projects
* Separating secrets and configs by deployment context
* Dynamically reading values like `env.DB_URL`, `env.get("DEBUG", default=False, cast=cast_bool)`
* Avoiding `os.environ` pollution

---

### Basic Example

```python
from multinut.env import Environment, Modes

env = Environment(env_file_name=".env", mode=Modes.DEVELOPMENT)

print(env.get("DEBUG", default=False))
print(env["API_KEY"])
print(env.DB_URL)
```

Given a `.env.development` file:

```env
DEBUG=true
API_KEY=secret
DB_URL=https://example.com
```

---

### Smart Casts Example

```python
from multinut.env import (
    Environment, cast_bool, cast_int, cast_float,
    cast_list, cast_tuple, cast_dict, cast_none_or_str
)

env = Environment()

print("INT:", env.get("PORT", cast=cast_int))                      # -> int
print("FLOAT:", env.get("PI", cast=cast_float))                    # -> float
print("BOOL:", env.get("ENABLED", cast=cast_bool))                 # -> bool
print("LIST:", env.get("NUMBERS", cast=cast_list))                 # -> list[str]
print("TUPLE:", env.get("WORDS", cast=cast_tuple))                 # -> tuple[str]
print("DICT:", env.get("CONFIG", cast=cast_dict))                  # -> dict
print("NONE_OR_STR:", env.get("OPTIONAL", cast=cast_none_or_str))  # -> None or str
```

Example `.env`:

```env
PORT=8080
PI=3.1415
ENABLED=yes
NUMBERS=1,2,3
WORDS=hello,world,test
CONFIG={"timeout": 30, "debug": true}
OPTIONAL=null
```

### Included Cast Helpers

All built-in cast functions handle common edge cases:

| Cast Function      | Description                                 |
| ------------------ | ------------------------------------------- |
| `cast_str`         | Ensures string                              |
| `cast_int`         | Converts to integer                         |
| `cast_float`       | Converts to float                           |
| `cast_bool`        | Accepts `1`, `true`, `yes`, `on`, etc.      |
| `cast_list`        | Comma-split list                            |
| `cast_tuple`       | Comma-split, converted to tuple             |
| `cast_dict`        | Parses JSON string into dictionary          |
| `cast_none_or_str` | Returns `None` if value is `null` or `None` |

---
