
import os
import uuid
import subprocess
from build123d import *
import config

class CADAgent:
    def __init__(self):
        self.output_dir = os.path.join(config.DATA_DIR, "cad_output")
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_3d_model(self, prompt):
        """
        Generates a 3D model based on the prompt using build123d.
        Note: True NLP-to-CAD requires a sophisticated LLM to write the python code.
        For this 'fast' implementation, we will use Gemini to generate the build123d code 
        and then execute it.
        """
        filename = f"model_{uuid.uuid4().hex[:8]}.stl"
        filepath = os.path.join(self.output_dir, filename)
        
        # In a real scenario, we would return the prompt to the LLM to generate code.
        # Here we simulated the execution flow.
        return f"To generate this model, I would need to write a build123d script. (Logic Placeholder)"

    def execute_cad_script(self, code_str):
        """
        Executes a generated build123d script safely-ish.
        """
        try:
            # We wrap the code to export the STL
            wrapped_code = f"""
from build123d import *
{code_str}

# Assumes the user code defines a 'part' or 'sketch' or 'result' object
if 'result' in locals():
    export_stl(result, "{self.output_dir.replace(os.sep, '/')}/output.stl")
elif 'part' in locals():
    export_stl(part, "{self.output_dir.replace(os.sep, '/')}/output.stl")
            """
            
            # Execute
            exec(wrapped_code, globals())
            return f"CAD Model generated at {self.output_dir}/output.stl"
        except Exception as e:
            return f"CAD Generation Failed: {e}"

    def get_latest_stl(self):
        """Returns path to the latest generated STL."""
        return os.path.join(self.output_dir, "output.stl")
