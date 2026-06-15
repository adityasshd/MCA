import os
from pathlib import Path
from typing import Any

class PromptManager:
    """
    Manages loading and formatting prompts from the prompts directory.
    """
    
    def __init__(self, prompts_dir: str | Path | None = None) -> None:
        if prompts_dir is None:
            # Default to src/prompts relative to this file's location
            self.prompts_dir = Path(__file__).parent.parent / "prompts"
        else:
            self.prompts_dir = Path(prompts_dir)
            
    def get_prompt(self, prompt_name: str, **kwargs: Any) -> str:
        """
        Load a prompt template from file and optionally format it with kwargs.
        
        Args:
            prompt_name: Name of the prompt file (without extension)
            **kwargs: Variables to format into the prompt
            
        Returns:
            The formatted prompt string.
        """
        file_path = self.prompts_dir / f"{prompt_name}.txt"
        if not file_path.exists():
            raise FileNotFoundError(f"Prompt template '{prompt_name}.txt' not found in {self.prompts_dir}")
            
        template = file_path.read_text(encoding="utf-8")
        
        if kwargs:
            try:
                return template.format(**kwargs)
            except KeyError as e:
                raise ValueError(f"Missing variable {e} for prompt '{prompt_name}'")
        return template
