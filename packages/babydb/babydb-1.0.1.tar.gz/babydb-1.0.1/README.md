Got it! Here's your **SimpleDB README content** rewritten in **GitHub-Flavored Markdown (GFM)**, properly formatted for PyPI and GitHub:

````markdown
# SimpleDB

A lightweight key-value database with compression, supporting CLI and web interfaces.

---

## Installation

```bash
pip install simpledb
````

---

## Usage

### CLI

```bash
simpledb-cli
```

### Web

```bash
simpledb-web
```

Access the web interface at [http://localhost:5000](http://localhost:5000).

---

## Features

* Compressed storage (`database.json.gz`, `.gz` files)
* CRUD operations, file uploads/downloads, full-text search
* Transaction support (`begin`, `commit`, `rollback`)
* Admin/user roles

  * `admin`: `admin123`
  * `user`: `user123`

---

## Example

```bash
simpledb-cli
> login admin admin123
> create student001 "{\"Name\": \"Alice\", \"Age\": 15, \"Grade\": 10, \"Class\": \"A\", \"Subjects\": [\"Math\", \"Science\"]}"
> upload student001 photo.jpg
> find fulltext "Math Science" sortby Age
```

```

---

### How to use this:

- Save it as `README.md` in your project root.
- Include it in your `setup.py` or `pyproject.toml` as your long description.
- Validate with `twine check dist/*` before uploading to PyPI.

---

If you want, I can help you generate the full `README.md` file ready to copy-paste!
```
