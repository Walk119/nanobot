"""Service layer for skills management."""
import re
from pathlib import Path
from typing import Optional
from .repository import SkillsRepository
from .models import SkillInfo, SkillsTree, FileNode


class SkillsService:
    """Business logic for skills operations."""
    
    def __init__(self, skills_root: str):
        """Initialize the skills service.
        
        Args:
            skills_root: Absolute path to the skills directory
        """
        self.repository = SkillsRepository(skills_root)
        self.skills_root = Path(skills_root)
    
    def get_skills_tree(self, include_content: bool = False, max_depth: int = -1) -> dict:
        """Get the complete skills directory structure.
        
        Args:
            include_content: Whether to include file contents (default: False)
            max_depth: Maximum depth to traverse (-1 for unlimited, default: -1)
            
        Returns:
            Dictionary representation of the skills tree
        """
        tree = self.repository.get_skills_tree(include_content, max_depth)
        return tree.to_dict()
    
    def get_skill_info(self, skill_name: str) -> Optional[SkillInfo]:
        """Get detailed information about a specific skill.
        
        Args:
            skill_name: Name of the skill (directory name)
            
        Returns:
            SkillInfo object or None if not found
        """
        skill_dir = self.skills_root / skill_name
        
        if not skill_dir.exists() or not skill_dir.is_dir():
            return None
        
        # Check for SKILL.md
        skill_md = skill_dir / 'SKILL.md'
        if not skill_md.exists():
            return None
        
        # Parse SKILL.md for metadata
        description = self._extract_description(skill_md)
        
        # Check for scripts directory
        scripts_dir = skill_dir / 'scripts'
        has_scripts = scripts_dir.exists() and scripts_dir.is_dir()
        script_count = 0
        
        if has_scripts:
            try:
                script_count = len([f for f in scripts_dir.iterdir() if f.is_file()])
            except (OSError, IOError):
                script_count = 0
        
        # Get timestamps
        try:
            stat = skill_md.stat()
            created_at = None  # Windows doesn't reliably track creation time
            updated_at = None
        except (OSError, IOError):
            created_at = None
            updated_at = None
        
        return SkillInfo(
            name=skill_name,
            description=description,
            directory=skill_name,
            has_scripts=has_scripts,
            script_count=script_count,
            created_at=created_at,
            updated_at=updated_at,
        )
    
    def _extract_description(self, skill_md_path: Path) -> str:
        """Extract description from SKILL.md frontmatter or first paragraph.
        
        Args:
            skill_md_path: Path to SKILL.md file
            
        Returns:
            Extracted description string
        """
        try:
            content = skill_md_path.read_text(encoding='utf-8')
            
            # Try to extract from YAML frontmatter
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    yaml_content = parts[1]
                    # Look for description field
                    for line in yaml_content.split('\n'):
                        if line.startswith('description:'):
                            return line.split(':', 1)[1].strip().strip('"\'')
            
            # Fallback: extract first non-empty line after heading
            lines = content.split('\n')
            for line in lines:
                line = line.strip()
                if line and not line.startswith('#') and not line.startswith('---'):
                    # Clean up markdown formatting
                    description = re.sub(r'\*\*([^*]+)\*\*', r'\1', line)  # Remove bold
                    description = re.sub(r'\*([^*]+)\*', r'\1', description)  # Remove italic
                    return description
            
            return ""
            
        except (OSError, IOError):
            return ""
    
    def list_skills(self) -> list[dict]:
        """List all available skills with basic info.
        
        Returns:
            List of dictionaries containing skill information
        """
        skill_names = self.repository.list_skills()
        skills = []
        
        for name in skill_names:
            info = self.get_skill_info(name)
            if info:
                skills.append({
                    'name': info.name,
                    'description': info.description,
                    'directory': info.directory,
                    'has_scripts': info.has_scripts,
                    'script_count': info.script_count,
                })
        
        return skills
    
    def get_skill_details(self, skill_name: str) -> Optional[dict]:
        """Get detailed information about a skill including its structure.
        
        Args:
            skill_name: Name of the skill
            
        Returns:
            Dictionary with skill details or None if not found
        """
        info = self.get_skill_info(skill_name)
        if not info:
            return None
        
        # Get the skill's directory structure
        skill_dir = self.skills_root / skill_name
        repo = SkillsRepository(str(skill_dir))
        
        try:
            tree = repo.get_skills_tree(include_content=False, max_depth=2)
            structure = tree.to_dict()
        except FileNotFoundError:
            structure = None
        
        # Read SKILL.md content
        skill_md = skill_dir / 'SKILL.md'
        skill_content = None
        try:
            skill_content = skill_md.read_text(encoding='utf-8')
        except (OSError, IOError):
            pass
        
        return {
            'name': info.name,
            'description': info.description,
            'directory': info.directory,
            'has_scripts': info.has_scripts,
            'script_count': info.script_count,
            'structure': structure,
            'skill_content': skill_content,
        }
    
    def get_file(self, file_path: str) -> Optional[FileNode]:
        """Get a specific file's content.
        
        Args:
            file_path: Relative path from skills root (e.g., 'github/SKILL.md')
            
        Returns:
            FileNode with content or None if not found
        """
        content = self.repository.get_file_content(file_path)
        if content is None:
            return None
        
        full_path = self.skills_root / file_path
        return FileNode(
            name=full_path.name,
            type='file',
            path=file_path,
            content=content,
            size=len(content.encode('utf-8')),
            extension=full_path.suffix,
        )
    
    def get_file_content(self, file_path: str) -> Optional[str]:
        """Get raw file content without metadata.
        
        Args:
            file_path: Relative path from skills root (e.g., 'github/SKILL.md')
            
        Returns:
            File content as string or None if not found
        """
        return self.repository.get_file_content(file_path)
    
    def search_skills(self, query: str) -> list[dict]:
        """Search skills by name or description.
        
        Args:
            query: Search query string
            
        Returns:
            List of matching skills
        """
        query_lower = query.lower()
        results = []
        
        for skill_name in self.repository.list_skills():
            info = self.get_skill_info(skill_name)
            if info:
                # Search in name and description
                if (query_lower in info.name.lower() or 
                    query_lower in info.description.lower()):
                    results.append({
                        'name': info.name,
                        'description': info.description,
                        'directory': info.directory,
                        'has_scripts': info.has_scripts,
                        'script_count': info.script_count,
                    })
        
        return results
    
    def create_file(self, file_path: str, content: str = "") -> bool:
        """Create a file at the specified path.
        
        Args:
            file_path: Relative path from skills root
            content: Content to write to the file
            
        Returns:
            True if file was created successfully, False otherwise
        """
        return self.repository.create_file(file_path, content)
    
    def create_directory(self, directory_path: str) -> bool:
        """Create a directory at the specified path.
        
        Args:
            directory_path: Relative path from skills root
            
        Returns:
            True if directory was created successfully, False otherwise
        """
        return self.repository.create_directory(directory_path)
    
    def move_file(self, source_path: str, destination_path: str) -> bool:
        """Move a file from source to destination.
        
        Args:
            source_path: Relative path from skills root to the source file
            destination_path: Relative path from skills root to the destination
            
        Returns:
            True if file was moved successfully, False otherwise
        """
        return self.repository.move_file(source_path, destination_path)
    
    def move_directory(self, source_path: str, destination_path: str) -> bool:
        """Move a directory from source to destination.
        
        Args:
            source_path: Relative path from skills root to the source directory
            destination_path: Relative path from skills root to the destination
            
        Returns:
            True if directory was moved successfully, False otherwise
        """
        return self.repository.move_directory(source_path, destination_path)