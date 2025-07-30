import json
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, Any


def synthesize_cdk_template(project_dir: Path) -> Dict[str, Any]:
    """
    Synthesize a CloudFormation template from a CDK project.
    
    This function runs `cdk synth` in the given directory and returns
    the resulting CloudFormation template as a dictionary.
    """
    # Save the current directory to return to it later
    original_dir = os.getcwd()
    
    try:
        # Change to the project directory
        os.chdir(project_dir)
        
        # Create a temporary directory for CDK output
        with tempfile.TemporaryDirectory() as temp_dir:
            # Run cdk synth to generate the CloudFormation template
            subprocess.run(
                ["npx", "--yes", "cdk", "synth", "--app", "./app.py", "--no-staging", "--json", "--output", temp_dir],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            
            # Find the CloudFormation template file
            template_files = list(Path(temp_dir).glob("*.template.json"))
            
            if not template_files:
                raise ValueError("No CloudFormation template was generated")
            
            # Load the template file (use the first one if there are multiple)
            with open(template_files[0], "r") as f:
                template = json.load(f)
                
            return template if isinstance(template, dict) else {}
    
    except subprocess.CalledProcessError as e:
        error_message = e.stderr.decode("utf-8") if e.stderr else str(e)
        raise ValueError(f"Error running CDK synth: {error_message}")
    
    except Exception as e:
        raise ValueError(f"Error synthesizing CloudFormation template: {str(e)}")
    
    finally:
        # Return to the original directory
        os.chdir(original_dir)
