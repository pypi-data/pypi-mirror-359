# multinut

The multitool nobody asked for. Includes stuff and so

---

## `multinut.env`

A simple but flexible environment loader.
Supports `.env` file parsing with optional mode suffixes (e.g. `.env.production`, `.env.testing`, etc.), lazy loading, and dynamic access.

Useful when:

* You want a single class that can load environment configs based on mode (`development`, `production`, etc.)
* You need access via `env["KEY"]`, `env.get("KEY")`, or even `env.KEY`
* You want optional type casting and sane default handling
* You *don’t* want `os.environ` to be touched

### Use cases

* Loading `.env` files in mode-aware Python projects
* Separating secrets and configs by deployment context
* Dynamically reading values like `env.DB_URL`, `env.get("DEBUG", default=False, cast=bool)`
* Avoiding external dependencies beyond `python-dotenv`
