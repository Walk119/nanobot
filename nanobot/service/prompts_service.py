"""Service layer for prompts management."""
from pathlib import Path
from typing import List, Optional, Dict
import os


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
    
    def list_prompts(self) -> List[Dict[str, str]]:
        """List all available prompts (markdown files).
        
        Returns:
            List of dictionaries containing prompt name and content.
        """
        prompts = []
        for file in self.prompts_root.glob("*.md"):
            if file.is_file():
                try:
                    content = file.read_text(encoding='utf-8')
                    prompts.append({
                        "name": file.stem,
                        "content": content
                    })
                except Exception:
                    continue
        return sorted(prompts, key=lambda x: x['name'])
    
    def get_prompt(self, name: str) -> Optional[str]:
        """Get the content of a specific prompt.
        
        Args:
            name: Name of the prompt (without .md extension)
            
        Returns:
            Prompt content or None if not found
        """
        file_path = self.prompts_root / f"{name}.md"
        if file_path.exists() and file_path.is_file():
            try:
                return file_path.read_text(encoding='utf-8')
            except Exception:
                return None
        return None
    
    def save_prompt(self, name: str, content: str) -> bool:
        """Create or update a prompt.
        
        Args:
            name: Name of the prompt
            content: Content of the prompt
            
        Returns:
            True if successful
        """
        try:
            # Ensure name is safe (no path traversal)
            safe_name = Path(name).stem
            file_path = self.prompts_root / f"{safe_name}.md"
            file_path.write_text(content, encoding='utf-8')
            return True
        except Exception:
            return False
            
    def delete_prompt(self, name: str) -> bool:
        """Delete a prompt.
        
        Args:
            name: Name of the prompt
            
        Returns:
            True if deleted, False if not found or error
        """
        try:
            file_path = self.prompts_root / f"{name}.md"
            if file_path.exists() and file_path.is_file():
                file_path.unlink()
                return True
            return False
        except Exception:
            return False
