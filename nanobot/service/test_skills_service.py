"""Tests for the skills service."""
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from service.models import FileNode, SkillsTree, SkillInfo
from service.repository import SkillsRepository
from service.service import SkillsService


def test_models():
    """Test data models."""
    print("Testing models...")
    
    # Test FileNode
    file_node = FileNode(
        name="test.py",
        type="file",
        path="test/test.py",
        content="print('hello')",
        size=14,
        extension=".py"
    )
    
    assert file_node.name == "test.py"
    assert file_node.type == "file"
    
    dict_repr = file_node.to_dict()
    assert dict_repr['name'] == "test.py"
    assert dict_repr['content'] == "print('hello')"
    print("  ✓ FileNode works correctly")
    
    # Test SkillsTree
    tree = SkillsTree(
        root_path="/skills",
        children=[file_node],
        total_files=1,
        total_directories=0
    )
    
    dict_repr = tree.to_dict()
    assert dict_repr['root_path'] == "/skills"
    assert len(dict_repr['children']) == 1
    print("  ✓ SkillsTree works correctly")
    
    # Test SkillInfo
    info = SkillInfo(
        name="test_skill",
        description="A test skill",
        directory="test_skill",
        has_scripts=True,
        script_count=2
    )
    
    assert info.name == "test_skill"
    assert info.has_scripts is True
    print("  ✓ SkillInfo works correctly")


def test_repository():
    """Test repository layer."""
    print("\nTesting repository...")
    
    # Use the actual skills directory
    current_dir = Path(__file__).parent
    nanobot_dir = current_dir.parent
    skills_root = nanobot_dir / "skills"
    
    if not skills_root.exists():
        print(f"  ⚠ Skills directory not found: {skills_root}")
        return
    
    repo = SkillsRepository(str(skills_root))
    
    # Test list_skills
    skills = repo.list_skills()
    assert isinstance(skills, list)
    assert len(skills) > 0, "Should find at least one skill"
    print(f"  ✓ Found {len(skills)} skills: {', '.join(skills[:3])}...")
    
    # Test get_skills_tree
    tree = repo.get_skills_tree(include_content=False, max_depth=1)
    assert isinstance(tree, SkillsTree)
    assert tree.total_directories > 0
    print(f"  ✓ Directory tree built: {tree.total_files} files, {tree.total_directories} dirs")
    
    # Test get_file_content
    if skills:
        first_skill = skills[0]
        skill_md_path = f"{first_skill}/SKILL.md"
        content = repo.get_file_content(skill_md_path)
        assert content is not None
        assert isinstance(content, str)
        assert len(content) > 0
        print(f"  ✓ File content retrieved for {skill_md_path}")


def test_service():
    """Test service layer."""
    print("\nTesting service...")
    
    current_dir = Path(__file__).parent
    nanobot_dir = current_dir.parent
    skills_root = nanobot_dir / "skills"
    
    if not skills_root.exists():
        print(f"  ⚠ Skills directory not found: {skills_root}")
        return
    
    service = SkillsService(str(skills_root))
    
    # Test list_skills
    skills = service.list_skills()
    assert isinstance(skills, list)
    assert len(skills) > 0
    print(f"  ✓ Service listed {len(skills)} skills")
    
    # Check structure of returned data
    first_skill = skills[0]
    assert 'name' in first_skill
    assert 'description' in first_skill
    assert 'directory' in first_skill
    print(f"  ✓ Skill data structure correct")
    
    # Test get_skill_info
    skill_name = skills[0]['name']
    info = service.get_skill_info(skill_name)
    assert info is not None
    assert isinstance(info, SkillInfo)
    assert info.name == skill_name
    print(f"  ✓ Skill info retrieved for {skill_name}")
    
    # Test get_skill_details
    details = service.get_skill_details(skill_name)
    assert details is not None
    assert 'structure' in details
    assert 'skill_content' in details
    print(f"  ✓ Skill details retrieved with structure and content")
    
    # Test search_skills
    results = service.search_skills(skill_name[:3])  # Search first 3 chars
    assert isinstance(results, list)
    print(f"  ✓ Search returned {len(results)} results")


def test_api_router():
    """Test API router creation."""
    print("\nTesting API router...")
    
    try:
        from service.api import SkillsAPI
        
        api = SkillsAPI()
        router = api.get_router()
        
        assert router is not None
        print("  ✓ API router created successfully")
        
        # Check routes are registered
        routes = [route.path for route in router.routes]
        assert any('/api/skills' in r for r in routes)
        print(f"  ✓ {len(routes)} routes registered")
        
    except ImportError as e:
        print(f"  ⚠ FastAPI not installed, skipping API tests: {e}")


def main():
    """Run all tests."""
    print("=" * 60)
    print("NanoBot Skills Service - Test Suite")
    print("=" * 60)
    
    try:
        test_models()
        test_repository()
        test_service()
        test_api_router()
        
        print("\n" + "=" * 60)
        print("✅ All tests passed!")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
