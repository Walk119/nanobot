"""Service layer for prompts management."""
from pathlib import Path
from typing import List, Optional, Dict
import os
import re


class PromptsService:
    """Business logic for prompts operations."""
    
    def __init__(self, prompts_root: Optional[str] = None):
        """Initialize the prompts service.
        
        Args:
            prompts_root: Absolute path to the prompts directory
        """
        if prompts_root is None:
            # Default to nanobot/service/prompts relative to this file
            current_dir = os.path.dirname(os.path.abspath(__file__))
            prompts_root = os.path.join(current_dir, 'prompts')
            
        self.prompts_root = Path(prompts_root)
        self.prompts_root.mkdir(parents=True, exist_ok=True)
    
    def _extract_name(self, content: str, default_name: str) -> str:
        """Extract the first markdown heading as name, or fallback to default."""
        for line in content.splitlines():
            line = line.strip()
            if line.startswith('#'):
                # Handle both '# Title' and '### Title'
                return line.lstrip('#').strip()
        return default_name

    def list_prompts(self) -> List[Dict[str, str]]:
        """List all available prompts (markdown files).
        
        Returns:
            List of dictionaries containing prompt name, path and content.
        """
        prompts = []
        for file in self.prompts_root.glob("*.md"):
            if file.is_file():
                try:
                    content = file.read_text(encoding='utf-8')
                    prompts.append({
                        "name": self._extract_name(content, file.stem),
                        "path": file.name,
                        "content": content
                    })
                except Exception:
                    continue
        return sorted(prompts, key=lambda x: x['name'])
    
    def get_prompt(self, filename: str) -> Optional[Dict[str, str]]:
        """Get a specific prompt info.
        
        Args:
            filename: The filename (e.g., 'midwife.md')
            
        Returns:
            Prompt info or None if not found
        """
        file_path = self.prompts_root / filename
        if file_path.exists() and file_path.is_file():
            try:
                content = file_path.read_text(encoding='utf-8')
                return {
                    "name": self._extract_name(content, file_path.stem),
                    "path": file_path.name,
                    "content": content
                }
            except Exception:
                return None
        return None
    
    def save_prompt(self, filename: str, content: str) -> bool:
        """Create or update a prompt.
        
        Args:
            filename: The filename (e.g., 'midwife.md')
            content: Content of the prompt
            
        Returns:
            True if successful
        """
        try:
            # Basic validation to ensure it's just a filename
            if os.path.sep in filename or (os.path.altsep and os.path.altsep in filename):
                filename = os.path.basename(filename)
                
            if not filename.endswith('.md'):
                filename += '.md'
                
            file_path = self.prompts_root / filename
            file_path.write_text(content, encoding='utf-8')
            return True
        except Exception:
            return False
            
    def delete_prompt(self, filename: str) -> bool:
        """Delete a prompt.
        
        Args:
            filename: The filename (e.g., 'midwife.md')
            
        Returns:
            True if deleted, False if not found or error
        """
        try:
            file_path = self.prompts_root / filename
            if file_path.exists() and file_path.is_file():
                file_path.unlink()
                return True
            return False
        except Exception:
            return False
