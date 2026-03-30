# NanoBot Skills Service

A RESTful API service for browsing and retrieving skills directory structure and file contents.

## Architecture

The service follows a clean layered architecture:

```
bot_chat.py (Entry Point)
    ↓
api.py (API Layer - FastAPI routes)
    ↓
service.py (Service Layer - Business Logic)
    ↓
repository.py (Repository Layer - File System Operations)
    ↓
models.py (Data Models)
```

### Layers

1. **Entry Point** (`bot_chat.py`)
   - Main entry point for the service
   - Provides convenience functions and factory methods
   - Creates standalone FastAPI application

2. **API Layer** (`api.py`)
   - FastAPI router with HTTP endpoints
   - Request/response handling
   - Input validation and error handling

3. **Service Layer** (`service.py`)
   - Business logic implementation
   - Data processing and transformation
   - Coordinates repository operations

4. **Repository Layer** (`repository.py`)
   - Direct file system operations
   - Directory traversal
   - File reading utilities

5. **Models** (`models.py`)
   - Data structures (dataclasses)
   - Type definitions
   - Serialization methods

## Installation

The service requires FastAPI and uvicorn:

```bash
pip install fastapi uvicorn
```

## Usage

### Option 1: Standalone Server

Run as a standalone service:

```bash
python -m nanobot.service.bot_chat
```

Or programmatically:

```python
from nanobot.service.bot_chat import create_standalone_app

app = create_standalone_app()

# Run with uvicorn
# uvicorn nanobot.service.bot_chat:create_standalone_app --reload
```

### Option 2: Include in Existing FastAPI App

```python
from fastapi import FastAPI
from nanobot.service import SkillsAPI

app = FastAPI()

# Include skills router
skills_api = SkillsAPI()
app.include_router(skills_api.get_router())
```

### Option 3: Use Service Directly (No HTTP)

```python
from nanobot.service.bot_chat import get_skills_service

service = get_skills_service()

# List all skills
skills = service.list_skills()

# Get skill details
details = service.get_skill_details('github')

# Get directory tree
tree = service.get_skills_tree(include_content=True)
```

## API Endpoints

### List All Skills
```http
GET /api/skills
```

Returns a list of all available skills with basic information.

**Response:**
```json
{
  "skills": [
    {
      "name": "github",
      "description": "Interact with GitHub using the gh CLI",
      "directory": "github",
      "has_scripts": false,
      "script_count": 0
    }
  ]
}
```

### Get Complete Directory Tree
```http
GET /api/skills/tree?include_content=false&max_depth=-1
```

**Parameters:**
- `include_content` (boolean): Include file contents (default: false)
- `max_depth` (integer): Maximum depth to traverse, -1 for unlimited (default: -1)

**Response:**
```json
{
  "root_path": "/path/to/skills",
  "children": [
    {
      "name": "github",
      "type": "directory",
      "path": "github",
      "children": [...]
    }
  ],
  "total_files": 15,
  "total_directories": 9
}
```

### Get Skill Details
```http
GET /api/skills/{skill_name}
```

**Example:**
```http
GET /api/skills/github
```

**Response:**
```json
{
  "name": "github",
  "description": "Interact with GitHub using the gh CLI",
  "directory": "github",
  "has_scripts": false,
  "script_count": 0,
  "structure": {...},
  "skill_content": "# GitHub Skill\n..."
}
```

### Get Skill Basic Info
```http
GET /api/skills/{skill_name}/info
```

Returns basic information about a skill without full content.

### Get Specific File
```http
GET /api/skills/{skill_name}/file/{file_path}
```

**Example:**
```http
GET /api/skills/github/SKILL.md
```

**Response:**
```json
{
  "name": "SKILL.md",
  "path": "github/SKILL.md",
  "content": "# GitHub Skill\n...",
  "size": 1234,
  "extension": ".md"
}
```

### Get Raw File Content
```http
GET /api/skills/file/raw?file_path={path}
```

**Example:**
```http
GET /api/skills/file/raw?file_path=github/SKILL.md
```

**Response:** Returns plain text content (not JSON)

```
# GitHub Skill

Interact with GitHub using the gh CLI...
```

### Search Skills
```http
GET /api/skills/search?q={query}
```

**Example:**
```http
GET /api/skills/search?q=github
```

**Response:**
```json
{
  "results": [...],
  "count": 1
}
```

## Programmatic API

### Service Methods

```python
from nanobot.service import SkillsService

service = SkillsService('/path/to/skills')

# List skills
skills = service.list_skills()

# Get skill info
info = service.get_skill_info('github')

# Get skill details (includes structure and content)
details = service.get_skill_details('github')

# Get complete tree
tree = service.get_skills_tree(
    include_content=False,
    max_depth=-1
)

# Get specific file
file_node = service.get_file('github/SKILL.md')

# Search skills
results = service.search_skills('github')
```

### Repository Methods

```python
from nanobot.service import SkillsRepository

repo = SkillsRepository('/path/to/skills')

# Build tree structure
tree = repo.get_skills_tree(include_content=True)

# Get file content
content = repo.get_file_content('github/SKILL.md')

# List skill directories
skills = repo.list_skills()
```

## Configuration

### Custom Skills Root Directory

By default, the service uses `nanobot/skills`. To use a different directory:

```python
# Via API
api = SkillsAPI(skills_root='/custom/path/to/skills')

# Via Service
service = SkillsService('/custom/path/to/skills')

# Via bot_chat functions
service = get_skills_service(skills_root='/custom/path/to/skills')
api = get_skills_api(skills_root='/custom/path/to/skills')
```

## Features

- ✅ **Directory Browsing**: Navigate the skills directory structure
- ✅ **File Content Retrieval**: Read file contents with proper encoding handling
- ✅ **Search**: Search skills by name and description
- ✅ **Metadata Extraction**: Automatically extract skill descriptions
- ✅ **Structured Response**: Well-organized JSON responses
- ✅ **Error Handling**: Proper HTTP status codes and error messages
- ✅ **Type Safety**: Full TypeScript support via dataclasses
- ✅ **Performance**: Lazy initialization and efficient file traversal
- ✅ **Security**: Filters hidden files and non-essential directories

## Security Considerations

The service automatically:
- Skips hidden files and directories (starting with `.`)
- Excludes `__pycache__`, `node_modules`, `.git`, `.idea`
- Only reads text files with safe extensions
- Handles encoding errors gracefully
- Prevents directory traversal attacks

## Testing

Test the service directly:

```bash
# Start the server
python -m nanobot.service.bot_chat

# Test endpoints with curl
curl http://localhost:8000/api/skills
curl http://localhost:8000/api/skills/tree
curl http://localhost:8000/api/skills/github
curl http://localhost:8000/api/skills/search?q=github
```

## Example Responses

### List Skills
```json
{
  "skills": [
    {
      "name": "clawhub",
      "description": "Search and install skills from ClawHub registry",
      "directory": "clawhub",
      "has_scripts": false,
      "script_count": 0
    },
    {
      "name": "github",
      "description": "Interact with GitHub using the gh CLI",
      "directory": "github",
      "has_scripts": false,
      "script_count": 0
    }
  ]
}
```

### Search Results
```json
{
  "results": [
    {
      "name": "github",
      "description": "Interact with GitHub using the gh CLI",
      "directory": "github",
      "has_scripts": false,
      "script_count": 0
    }
  ],
  "count": 1
}
```

## Troubleshooting

### Module Not Found Errors

Ensure you're running from the project root:
```bash
cd /path/to/nanobot
python -m nanobot.service.bot_chat
```

### Permission Errors

Make sure the service has read permissions for the skills directory.

### Encoding Issues

The service handles UTF-8 encoding. If you encounter encoding errors, check that files are properly encoded.

## License

Part of the NanoBot project.
