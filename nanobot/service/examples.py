"""Example usage of the NanoBot Skills Service.

This file demonstrates various ways to use the skills service.
"""


def example_1_standalone_server():
    """Example 1: Run as a standalone FastAPI server."""
    from nanobot.service.bot_chat import create_standalone_app
    
    app = create_standalone_app()
    
    # The app can be run with uvicorn:
    # uvicorn examples.example_1_standalone_server:create_standalone_app --reload
    # Or: python -m nanobot.service.bot_chat
    
    return app


def example_2_integrate_existing():
    """Example 2: Integrate into an existing FastAPI application."""
    from fastapi import FastAPI
    from nanobot.service import SkillsAPI
    
    # Your existing app
    app = FastAPI(
        title="My App",
        description="My existing application"
    )
    
    # Add skills endpoints under /api/skills
    skills_api = SkillsAPI()
    app.include_router(skills_api.get_router())
    
    # Now you have both your routes and /api/skills/* routes
    return app


def example_3_programmatic_usage():
    """Example 3: Use the service programmatically without HTTP."""
    from nanobot.service.bot_chat import get_skills_service
    
    # Get the service instance
    service = get_skills_service()
    
    # List all skills
    skills = service.list_skills()
    print(f"Found {len(skills)} skills:")
    for skill in skills:
        print(f"  - {skill['name']}: {skill['description']}")
    
    # Get detailed information about a specific skill
    details = service.get_skill_details('github')
    if details:
        print(f"\nGitHub Skill Details:")
        print(f"  Description: {details['description']}")
        print(f"  Has scripts: {details['has_scripts']}")
        print(f"  Script count: {details['script_count']}")
    
    # Get the complete directory tree
    tree = service.get_skills_tree(include_content=False, max_depth=2)
    print(f"\nDirectory Structure:")
    print(f"  Root: {tree['root_path']}")
    print(f"  Total files: {tree['total_files']}")
    print(f"  Total directories: {tree['total_directories']}")
    
    # Search for skills
    results = service.search_skills('github')
    print(f"\nSearch results for 'github': {len(results)} matches")
    
    return service


def example_4_custom_skills_directory():
    """Example 4: Use a custom skills directory."""
    from nanobot.service import SkillsService, SkillsAPI
    
    # Specify a custom path
    custom_path = '/path/to/custom/skills'
    
    # Create service with custom path
    service = SkillsService(custom_path)
    
    # Create API with custom path
    api = SkillsAPI(custom_path)
    
    return service, api


def example_5_repository_layer():
    """Example 5: Use the repository layer directly for low-level operations."""
    from nanobot.service import SkillsRepository
    
    repo = SkillsRepository('/path/to/skills')
    
    # Get raw file tree
    tree = repo.get_skills_tree(include_content=True)
    
    # Get specific file content
    content = repo.get_file_content('github/SKILL.md')
    
    # List skill directories
    skills = repo.list_skills()
    
    return repo


def example_6_fetch_api():
    """Example 6: Call the API from a client application."""
    import requests
    
    BASE_URL = "http://localhost:8000/api/skills"
    
    # List all skills
    response = requests.get(f"{BASE_URL}")
    skills = response.json()
    print("Skills:", skills)
    
    # Get skill details
    response = requests.get(f"{BASE_URL}/github")
    details = response.json()
    print("GitHub details:", details)
    
    # Get specific file (JSON format)
    response = requests.get(f"{BASE_URL}/github/file/SKILL.md")
    file_data = response.json()
    print("SKILL.md content (JSON):", file_data['content'])
    
    # Get raw file content (plain text)
    response = requests.get(
        f"{BASE_URL}/file/raw",
        params={"file_path": "github/SKILL.md"}
    )
    raw_content = response.text
    print("SKILL.md content (raw):", raw_content[:100] + "...")
    
    # Search
    response = requests.get(f"{BASE_URL}/search", params={"q": "github"})
    results = response.json()
    print("Search results:", results)


def example_7_async_usage():
    """Example 7: Use in an async application."""
    import asyncio
    import httpx
    
    async def fetch_skills():
        async with httpx.AsyncClient() as client:
            BASE_URL = "http://localhost:8000/api/skills"
            
            # Fetch multiple skills in parallel
            tasks = [
                client.get(f"{BASE_URL}"),
                client.get(f"{BASE_URL}/github"),
                client.get(f"{BASE_URL}/weather"),
            ]
            
            responses = await asyncio.gather(*tasks)
            
            all_skills = responses[0].json()
            github_details = responses[1].json()
            weather_details = responses[2].json()
            
            return all_skills, github_details, weather_details
    
    # Run: asyncio.run(fetch_skills())
    return fetch_skills


if __name__ == "__main__":
    print("NanoBot Skills Service Examples")
    print("=" * 50)
    
    print("\nExample 3: Programmatic Usage")
    print("-" * 50)
    try:
        example_3_programmatic_usage()
    except Exception as e:
        print(f"Error: {e}")
        print("Note: This example requires the skills directory to exist")
    
    print("\n" + "=" * 50)
    print("For more examples, see the README.md file")
