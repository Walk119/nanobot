"""Test the new raw file endpoint."""
from nanobot.service.bot_chat import get_skills_service

# Get service instance
service = get_skills_service()

print("Testing get_file_content method...")
content = service.get_file_content('github/SKILL.md')

if content:
    print(f"✓ Successfully retrieved file content")
    print(f"  Length: {len(content)} characters")
    print(f"\nFirst 300 characters:\n{content[:300]}")
else:
    print("✗ Failed to retrieve file content")

# Test with non-existent file
print("\n\nTesting with non-existent file...")
content = service.get_file_content('nonexistent/file.txt')
if content is None:
    print("✓ Correctly returns None for non-existent files")
else:
    print("✗ Should return None for non-existent files")
