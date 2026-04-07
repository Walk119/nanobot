"""Models for skills service."""
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime


@dataclass
class SkillInfo:
    """Information about a skill."""
    name: str
    description: str
    directory: str
    has_scripts: bool = False
    script_count: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class FileNode:
    """Represents a file or directory in the skills tree."""
    name: str
    type: str  # 'file' or 'directory'
    path: str
    content: Optional[str] = None
    children: list['FileNode'] = field(default_factory=list)
    size: int = 0
    extension: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        result = {
            'name': self.name,
            'type': self.type,
            'path': self.path,
        }
        
        if self.type == 'file':
            result.update({
                'content': self.content,
                'size': self.size,
                'extension': self.extension,
                'created_at': self.created_at,
                'updated_at': self.updated_at,
            })
        else:
            result['children'] = [child.to_dict() for child in self.children]
            
        return result


@dataclass
class SkillsTree:
    """Represents the complete skills directory structure."""
    root_path: str
    children: list[FileNode] = field(default_factory=list)
    total_files: int = 0
    total_directories: int = 0
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            'root_path': self.root_path,
            'children': [child.to_dict() for child in self.children],
            'total_files': self.total_files,
            'total_directories': self.total_directories,
        }
