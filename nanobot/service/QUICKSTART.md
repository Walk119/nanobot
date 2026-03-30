# Quick Start Guide - NanoBot Skills Service

## Overview

The Skills Service exposes the `nanobot/skills` directory structure and file contents via RESTful API endpoints.

## Architecture

```
nanobot/service/
├── bot_chat.py          # Entry point (use this!)
├── api.py               # API layer (FastAPI routes)
├── service.py           # Business logic
├── repository.py        # File system operations
├── models.py            # Data models
├── examples.py          # Usage examples
└── README.md            # Full documentation
```

## Installation

```bash
pip install fastapi uvicorn
```

## Quick Start

### Option 1: Run Standalone Server (Recommended for Testing)

```bash
# From project root
python -m nanobot.service.bot_chat
```

This starts a server at `http://localhost:8000`

Test it:
```bash
curl http://localhost:8000/api/skills
```

### Option 2: Integrate into Existing FastAPI App

```python
from fastapi import FastAPI
from nanobot.service import SkillsAPI

app = FastAPI()

skills_api = SkillsAPI()
app.include_router(skills_api.get_router())
```

### Option 3: Use Programmatically (No HTTP)

```python
from nanobot.service.bot_chat import get_skills_service

service = get_skills_service()

# List all skills
skills = service.list_skills()

# Get skill details
details = service.get_skill_details('github')
print(details['description'])
```

## API Endpoints

Once running, access these endpoints:

| Endpoint | Description |
|----------|-------------|
| `GET /api/skills` | List all skills |
| `GET /api/skills/tree` | Get complete directory tree |
| `GET /api/skills/{skill_name}` | Get skill details |
| `GET /api/skills/{skill_name}/info` | Get basic skill info |
| `GET /api/skills/{skill_name}/file/{path}` | Get specific file (JSON) |
| `GET /api/skills/file/raw?file_path={path}` | Get raw file content (plain text) |
| `GET /api/skills/search?q={query}` | Search skills |

## Examples

### List All Skills
```bash
curl http://localhost:8000/api/skills
```

Response:
```json
{
  "skills": [
    {
      "name": "github",
      "description": "Interact with GitHub using the gh CLI",
      "has_scripts": false,
      "script_count": 0
    }
  ]
}
```

### Get Directory Tree
```bash
curl http://localhost:8000/api/skills/tree
```

### Get Specific Skill
```bash
curl http://localhost:8000/api/skills/github
```

### Get File Content
```bash
curl http://localhost:8000/api/skills/github/file/SKILL.md
```

### Search Skills
```bash
curl "http://localhost:8000/api/skills/search?q=github"
```

## Interactive Documentation

When running the server, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Common Use Cases

### 1. Browse Available Skills
```python
import requests

response = requests.get("http://localhost:8000/api/skills")
skills = response.json()["skills"]

for skill in skills:
    print(f"{skill['name']}: {skill['description']}")
```

### 2. Read Skill Documentation
```python
response = requests.get("http://localhost:8000/api/skills/github")
skill = response.json()

print(skill['skill_content'])  # Full SKILL.md content
```

### 3. Get File Structure
```python
response = requests.get("http://localhost:8000/api/skills/tree")
tree = response.json()

def print_tree(node, indent=0):
    print("  " * indent + f"- {node['name']} ({node['type']})")
    if node['type'] == 'directory':
        for child in node['children']:
            print_tree(child, indent + 1)

for child in tree['children']:
    print_tree(child)
```

### 4. Search for Skills
```python
response = requests.get(
    "http://localhost:8000/api/skills/search",
    params={"q": "github"}
)
results = response.json()["results"]

for result in results:
    print(f"Found: {result['name']}")
```

## Configuration

### Custom Skills Directory

By default, uses `nanobot/skills`. To customize:

```python
from nanobot.service import SkillsService

# Custom path
service = SkillsService("/custom/path/to/skills")
```

Or via API:
```python
from nanobot.service import SkillsAPI

api = SkillsAPI(skills_root="/custom/path/to/skills")
```

## Troubleshooting

### Port Already in Use
```bash
# Use different port
uvicorn nanobot.service.bot_chat:create_standalone_app --port 8001
```

### Module Not Found
Make sure you're in the project root:
```bash
cd /path/to/nanobot
python -m nanobot.service.bot_chat
```

### Permission Denied
Check read permissions on skills directory:
```bash
# Linux/Mac
chmod -R a+r nanobot/skills

# Windows (PowerShell)
icacls nanobot\skills /grant Everyone:R
```

## Next Steps

- See `README.md` for full documentation
- Check `examples.py` for more code examples
- Visit `/docs` when server is running for interactive API docs

## Support

For issues or questions, refer to:
- Full documentation: `service/README.md`
- Examples: `service/examples.py`
- Source code: Layered architecture with clear separation
