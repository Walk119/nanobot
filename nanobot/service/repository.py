"""Repository layer for skills file system operations."""
import datetime
import os
from pathlib import Path
from typing import Optional
from .models import FileNode, SkillsTree
from nanobot.utils.logger import logger


class SkillsRepository:
    """Handles file system operations for skills directory."""
    
    def __init__(self, skills_root: str):
        """Initialize with the skills root directory path.
        
        Args:
            skills_root: Absolute path to the skills directory
        """
        self.skills_root = Path(skills_root)
        
    def get_skills_tree(self, include_content: bool = False, max_depth: int = -1) -> SkillsTree:
        """Build a tree structure of the skills directory.
        
        Args:
            include_content: Whether to include file contents (only for text files)
            max_depth: Maximum depth to traverse (-1 for unlimited)
            
        Returns:
            SkillsTree object representing the directory structure
        """
        if not self.skills_root.exists():
            raise FileNotFoundError(f"Skills directory not found: {self.skills_root}")
        logger.info("Building skills tree from: {}", self.skills_root)
        children = []
        total_files = 0
        total_directories = 0

        for item in self.skills_root.iterdir():
            logger.info("Processing: {}", item)
            node = self._build_file_node(item, include_content, max_depth, current_depth=0)
            if node:
                children.append(node)
                if node.type == 'file':
                    total_files += 1
                else:
                    total_directories += 1
                    # Count nested items
                    nested_files, nested_dirs = self._count_nested(node)
                    total_files += nested_files
                    total_directories += nested_dirs
        
        return SkillsTree(
            root_path=str(self.skills_root),
            children=children,
            total_files=total_files,
            total_directories=total_directories,
        )
    
    def _count_nested(self, node: FileNode) -> tuple[int, int]:
        """Count nested files and directories."""
        files = 0
        dirs = 0
        for child in node.children:
            if child.type == 'file':
                files += 1
            else:
                dirs += 1
                nested_files, nested_dirs = self._count_nested(child)
                files += nested_files
                dirs += nested_dirs
        return files, dirs
    
    def _build_file_node(
        self, 
        path: Path, 
        include_content: bool, 
        max_depth: int,
        current_depth: int
    ) -> Optional[FileNode]:
        """Build a FileNode from a path.
        
        Args:
            path: Path to the file or directory
            include_content: Whether to include file content
            max_depth: Maximum depth to traverse
            current_depth: Current recursion depth
            
        Returns:
            FileNode or None if should be excluded
        """
        # Skip hidden files and directories
        if path.name.startswith('.'):
            return None
        
        # Skip __pycache__ and common non-essential directories
        if path.name in {'__pycache__', 'node_modules', '.git', '.idea'}:
            return None
        
        relative_path = path.relative_to(self.skills_root)
        
        if path.is_file():
            return self._create_file_node(path, str(relative_path), include_content)
        elif path.is_dir():
            return self._create_directory_node(
                path, 
                str(relative_path), 
                include_content, 
                max_depth,
                current_depth
            )
        
        return None
    
    def _create_file_node(self, path: Path, relative_path: str, include_content: bool) -> FileNode:
        """Create a FileNode for a file."""
        try:
            logger.info(f"generate file {path} {relative_path}")
            stat = path.stat()
            size = stat.st_size
            
            # Only read content for text files and if requested
            content = None
            if include_content and self._is_text_file(path):
                try:
                    content = path.read_text(encoding='utf-8')
                except (UnicodeDecodeError, PermissionError):
                    content = None
            # Get timestamps
            created_at = datetime.datetime.fromtimestamp(stat.st_ctime)
            updated_at = datetime.datetime.fromtimestamp(stat.st_mtime)
            return FileNode(
                name=path.name,
                type='file',
                path=relative_path,
                content=content,
                size=size,
                extension=path.suffix,
                created_at=created_at,
                updated_at=updated_at
            )
        except (OSError, IOError):
            # Return basic node even if we can't read all details
            return FileNode(
                name=path.name,
                type='file',
                path=relative_path,
                size=0,
                extension=path.suffix,
            )
    
    def _create_directory_node(
        self, 
        path: Path, 
        relative_path: str,
        include_content: bool,
        max_depth: int,
        current_depth: int
    ) -> FileNode:
        """Create a FileNode for a directory."""
        logger.info(f"generate directory {path} {relative_path}")
        # Check depth limit
        if max_depth != -1 and current_depth >= max_depth:
            return FileNode(
                name=path.name,
                type='directory',
                path=relative_path,
            )
        
        children = []
        try:
            for item in path.iterdir():
                child_node = self._build_file_node(
                    item, 
                    include_content, 
                    max_depth,
                    current_depth + 1
                )
                if child_node:
                    children.append(child_node)
        except PermissionError:
            pass
        
        return FileNode(
            name=path.name,
            type='directory',
            path=relative_path,
            children=children,
        )
    
    def _is_text_file(self, path: Path) -> bool:
        """Check if a file is likely a text file based on extension."""
        text_extensions = {
            '.txt', '.md', '.rst', '.py', '.js', '.ts', '.jsx', '.tsx',
            '.json', '.yaml', '.yml', '.xml', '.html', '.css', '.scss',
            '.sh', '.bash', '.zsh', '.fish', '.env', '.ini', '.cfg',
            '.toml', '.sql', '.graphql', '.vue', '.svelte'
        }
        return path.suffix.lower() in text_extensions
    
    def get_file_content(self, file_path: str) -> Optional[str]:
        """Get the content of a specific file.
        
        Args:
            file_path: Relative path from skills root
            
        Returns:
            File content as string or None if not found/readable
        """
        try:
            full_path = self.skills_root / file_path
            if not full_path.exists() or full_path.is_dir():
                return None
            
            return full_path.read_text(encoding='utf-8')
        except (OSError, IOError, UnicodeDecodeError):
            return None
    
    def list_skills(self) -> list[str]:
        """List all skill directories (directories containing SKILL.md).
        
        Returns:
            List of skill names (directory names)
        """
        skills = []
        try:
            for item in self.skills_root.iterdir():
                if item.is_dir() and not item.name.startswith('.'):
                    skill_md = item / 'SKILL.md'
                    if skill_md.exists():
                        skills.append(item.name)
        except (OSError, IOError):
            pass
        
        return sorted(skills)
    
    def create_file(self, file_path: str, content: str = "") -> bool:
        """Create a file at the specified path.
        
        Args:
            file_path: Relative path from skills root
            content: Content to write to the file
            
        Returns:
            True if file was created successfully, False otherwise
        """
        try:
            full_path = self.skills_root / file_path
            # Create parent directories if they don't exist
            full_path.parent.mkdir(parents=True, exist_ok=True)
            # Write content to file
            full_path.write_text(content, encoding='utf-8')
            logger.info(f"Created file: {full_path}")
            return True
        except (OSError, IOError) as e:
            logger.error(f"Failed to create file {file_path}: {e}")
            return False
    
    def create_directory(self, directory_path: str) -> bool:
        """Create a directory at the specified path.
        
        Args:
            directory_path: Relative path from skills root
            
        Returns:
            True if directory was created successfully, False otherwise
        """
        try:
            full_path = self.skills_root / directory_path
            # Create directory and parent directories if they don't exist
            full_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created directory: {full_path}")
            return True
        except (OSError, IOError) as e:
            logger.error(f"Failed to create directory {directory_path}: {e}")
            return False

    def move_node(self, source_path: str, destination_path: str) -> str:
        """Move or rename a file or directory.

        Args:
            source_path: Current relative path
            destination_path: Target relative path

        Returns:
            The new relative path
        """
        src = self.skills_root / source_path
        dst = self.skills_root / destination_path

        if not src.exists():
            raise FileNotFoundError(f"Source path not found: {source_path}")

        # Ensure parent of destination exists
        dst.parent.mkdir(parents=True, exist_ok=True)

        src.rename(dst)
        return str(dst.relative_to(self.skills_root))