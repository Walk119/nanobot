# New Raw File Endpoint Documentation

## Overview

A new endpoint has been added to retrieve the raw content of files without JSON wrapping.

## Endpoint Details

### GET /api/skills/file/raw

Returns the plain text content of a file directly (not wrapped in JSON).

**Parameters:**
- `file_path` (query parameter, required): Relative path from skills root

**Example Requests:**

```bash
# Using curl
curl "http://localhost:8000/api/skills/file/raw?file_path=github/SKILL.md"

# Using Python requests
import requests
response = requests.get(
    "http://localhost:8000/api/skills/file/raw",
    params={"file_path": "github/SKILL.md"}
)
content = response.text

# Using the service directly
from nanobot.service.bot_chat import get_file_content
content = get_file_content('github/SKILL.md')
```

**Response:**
- Content-Type: `text/plain; charset=utf-8`
- Body: Raw file content as plain text

**Example Response:**
```
---
name: github
description: "Interact with GitHub using the `gh` CLI..."
---

# GitHub Skill

Interact with GitHub using the gh CLI. Use `gh issue`, `gh pr`...
```

## Comparison with Other File Endpoints

### 1. Get File (JSON format)
```http
GET /api/skills/github/file/SKILL.md
```

**Response (JSON):**
```json
{
  "name": "SKILL.md",
  "path": "github/SKILL.md",
  "content": "# GitHub Skill\n...",
  "size": 1371,
  "extension": ".md"
}
```

**Use case:** When you need metadata along with content

### 2. Get Raw File (Plain text)
```http
GET /api/skills/file/raw?file_path=github/SKILL.md
```

**Response (Plain text):**
```
# GitHub Skill
...
```

**Use case:** When you only need the raw content without metadata

## Implementation Details

### API Layer (`api.py`)

```python
@self.router.get('/file/raw')
async def get_raw_file(file_path: str = Query(...)):
    """Get raw file content by file path."""
    content = self.service.get_file_content(file_path)
    
    if content is None:
        raise HTTPException(status_code=404, detail="File not found")
    
    from fastapi.responses import PlainTextResponse
    return PlainTextResponse(content, media_type="text/plain")
```

### Service Layer (`service.py`)

```python
def get_file_content(self, file_path: str) -> Optional[str]:
    """Get raw file content without metadata."""
    return self.repository.get_file_content(file_path)
```

### Repository Layer (`repository.py`)

Uses existing `get_file_content` method which handles:
- File existence checking
- UTF-8 encoding
- Error handling
- Security filtering

## Error Handling

### File Not Found
```http
HTTP/1.1 404 Not Found
Content-Type: application/json

{
  "detail": "File 'nonexistent/SKILL.md' not found or cannot be read"
}
```

### Missing Parameter
```http
HTTP/1.1 422 Unprocessable Entity
Content-Type: application/json

{
  "detail": [
    {
      "type": "missing",
      "loc": ["query", "file_path"],
      "msg": "Field required"
    }
  ]
}
```

## Usage Examples

### Example 1: Display Markdown Content

```python
import requests

def display_skill(skill_name: str):
    """Fetch and display a skill's SKILL.md content."""
    response = requests.get(
        "http://localhost:8000/api/skills/file/raw",
        params={"file_path": f"{skill_name}/SKILL.md"}
    )
    
    if response.status_code == 200:
        print(response.text)
    else:
        print(f"Error: {response.status_code}")

display_skill('github')
```

### Example 2: Download File

```python
import requests

def download_file(file_path: str, output_path: str):
    """Download a file from the skills service."""
    response = requests.get(
        "http://localhost:8000/api/skills/file/raw",
        params={"file_path": file_path}
    )
    
    if response.status_code == 200:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(response.text)
        print(f"Saved to {output_path}")
    else:
        print(f"Error: {response.status_code}")

download_file('weather/SKILL.md', 'weather_skill.md')
```

### Example 3: Batch Fetch Files

```python
import requests
from concurrent.futures import ThreadPoolExecutor

def fetch_all_skill_docs():
    """Fetch all skill documentation in parallel."""
    skills = ['github', 'weather', 'tmux', 'memory']
    
    def fetch_skill(name):
        response = requests.get(
            "http://localhost:8000/api/skills/file/raw",
            params={"file_path": f"{name}/SKILL.md"}
        )
        return name, response.text if response.status_code == 200 else None
    
    with ThreadPoolExecutor() as executor:
        results = list(executor.map(fetch_skill, skills))
    
    for name, content in results:
        if content:
            print(f"{name}: {len(content)} chars")
        else:
            print(f"{name}: Failed to fetch")

fetch_all_skill_docs()
```

### Example 4: Programmatic Usage

```python
from nanobot.service.bot_chat import get_file_content

# Direct function call (no HTTP)
content = get_file_content('github/SKILL.md')

if content:
    # Process the content
    lines = content.split('\n')
    print(f"Total lines: {len(lines)}")
    print(f"First line: {lines[0]}")
```

## Testing

### Manual Test

```bash
# Start the server
python -m nanobot.service.bot_chat

# In another terminal, test the endpoint
curl "http://localhost:8000/api/skills/file/raw?file_path=github/SKILL.md"
```

### Automated Test

```python
# test_raw_file.py
from nanobot.service.bot_chat import get_file_content

def test_get_file_content():
    # Test existing file
    content = get_file_content('github/SKILL.md')
    assert content is not None
    assert len(content) > 0
    assert 'GitHub' in content
    
    # Test non-existent file
    content = get_file_content('nonexistent.txt')
    assert content is None
    
    print("✓ All tests passed")

test_get_file_content()
```

## Security Considerations

The endpoint includes built-in security measures:

1. **Path Traversal Prevention**: Automatically filters out attempts to access files outside skills directory
2. **Hidden File Filtering**: Cannot access files starting with `.`
3. **Directory Exclusion**: Cannot access `__pycache__`, `node_modules`, `.git`, etc.
4. **Encoding Safety**: Handles UTF-8 encoding errors gracefully
5. **Permission Handling**: Returns 404 for files without read permissions

## Performance

- **Direct file access**: No JSON serialization overhead
- **Streaming ready**: Can be extended to support streaming for large files
- **Caching friendly**: Response can be cached by CDNs or proxies
- **Small footprint**: Minimal memory usage for text responses

## Best Practices

1. **Use JSON endpoint when**: You need file metadata (size, extension, etc.)
2. **Use raw endpoint when**: You only need the content
3. **Always validate**: Check response status code before processing
4. **Handle errors**: Implement proper error handling for 404 and 422 responses
5. **Cache responses**: Static files can be cached to improve performance

## Related Endpoints

- `GET /api/skills/{skill_name}/file/{path}` - Get file with metadata (JSON)
- `GET /api/skills/tree` - Get complete directory structure
- `GET /api/skills/{skill_name}` - Get skill details including structure

## Changelog

### Version 1.0.0
- Added `/api/skills/file/raw` endpoint
- Added `get_file_content()` method to service layer
- Added convenience function in bot_chat.py
- Updated documentation
