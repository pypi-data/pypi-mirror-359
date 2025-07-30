from pathlib import Path
from typing import Dict, List, Optional

import yaml
from pydantic import BaseModel, Field
from rich.markdown import Markdown


class Challenge(BaseModel):
    """Represents a CDK challenge."""
    
    name: str
    description: str
    difficulty: str = Field(default="beginner")
    instructions: str
    expected_cf_template: Dict
    starter_code_files: Dict[str, str]
    next_challenge: Optional[str] = None
    
    def extract_to(self, output_dir: Path) -> None:
        """Extract the starter code files to the output directory."""
        output_dir.mkdir(exist_ok=True, parents=True)
        
        # Create the starter code files
        for path_str, content in self.starter_code_files.items():
            file_path = output_dir / path_str
            file_path.parent.mkdir(exist_ok=True, parents=True)
            file_path.write_text(content)
            if path_str == "app.py":
                # Make the file executable
                file_path.chmod(0o755)
            
        # Create a .cdk-tutor.yml file with challenge metadata
        metadata = {
            "challenge": self.name,
            "difficulty": self.difficulty,
            "next_challenge": self.next_challenge,
        }
        
        with open(output_dir / ".cdk-tutor.yml", "w") as f:
            yaml.dump(metadata, f)
            
        # Create README.md with instructions
        with open(output_dir / "README.md", "w") as f:
            f.write(f"# {self.name}\n\n")
            f.write(f"{self.instructions}\n")
    
    def get_instructions(self) -> Markdown:
        """Get rich formatted instructions."""
        return Markdown(self.instructions)


def get_available_challenges() -> List[Challenge]:
    """Get a list of all available challenges."""
    # In a real implementation, this would load challenges from files
    # For now, we'll return some sample challenges
    from cdk_tutor.challenges.sample_challenges import SAMPLE_CHALLENGES
    return SAMPLE_CHALLENGES
