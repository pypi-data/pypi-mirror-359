# listofdicts

**Enterprise-grade strongly-typed list of dictionaries for Python**

---

## Summary

`listofdicts` is a powerful custom Python data structure designed for modern data processing, data pipelines, ETL systems, API layers, and JSON-based applications where structured lists of dictionaries are commonly used.

---

## Key Features

- ✅ Only allows dictionaries inside.
- ✅ Optional schema validation (enforce required keys and value types).
- ✅ Optional immutability (lock data after loading).
- ✅ Full JSON serialization/deserialization.
- ✅ Supports deep copying and safe mutations.
- ✅ Strict runtime type safety.
- ✅ Merge and update support.
- ✅ Fully tested and production-grade.

---

## Installation

```bash
pip install listofdicts
```

## Usage

```python
from listofdicts import listofdicts

# Define schema for safety
schema = {
    'id': int,
    'name': str,
    'active': bool
}

lod = listofdicts([
    {'id': 1, 'name': 'Alice', 'active': True},
    {'id': 2, 'name': 'Bob', 'active': False}
], schema=schema)

# Append valid
lod.append({'id': 3, 'name': 'Carol', 'active': True})

# Partial update
lod.update_item(0, {'active': False})

# Merge with another listofdicts
lod2 = listofdicts([
    {'id': 4, 'name': 'Eve', 'active': True}
], schema=schema)

merged = lod.merge(lod2)

# Serialize to JSON
json_str = merged.to_json(indent=2)

# Deserialize from JSON
restored = listofdicts.from_json(json_str, schema=schema)

print(restored)
```

## Why Use listofdicts?
- Prevent accidental bad data.
- Fail fast with strict schema enforcement.
- Easy to serialize and deserialize.
- Safer than plain list[dict].
- Perfect for: ETL, API validation, data cleaning pipelines.

## API Summary

Method	Description
append()	Append a validated dictionary
extend()	Extend with another listofdicts
merge()	Merge two instances
update_item()	Partially update an entry
copy()	Deep copy
as_mutable()	Return mutable copy
as_immutable()	Return immutable copy
to_json()	Serialize to JSON
from_json()	Deserialize from JSON
immutable	Property to check mutability
schema	Property to access schema


## Directory Structure
```
listofdicts/
    ├── src/
    │   ├── __init__.py
    │   └── listofdicts.py
    ├── tests/
    │   └── test_listofdicts.py
    ├── README.md
    ├── pyproject.toml
    ├── setup.cfg
    └── LICENSE
```