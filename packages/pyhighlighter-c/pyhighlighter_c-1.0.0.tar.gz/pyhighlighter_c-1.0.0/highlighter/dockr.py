import subprocess
import os
import tempfile
from typing import Optional, Dict, Tuple

class DockrCompiler:
    SUPPORTED_LANGUAGES = {
        'python': {'command': 'python', 'extension': 'py'},
        'javascript': {'command': 'node', 'extension': 'js'},
        'rust': {'command': 'rustc', 'extension': 'rs'},
        'c': {'command': 'gcc', 'extension': 'c'},
        'cpp': {'command': 'g++', 'extension': 'cpp'},
        'java': {'command': 'javac', 'extension': 'java'},
        'go': {'command': 'go run', 'extension': 'go'},
        'ruby': {'command': 'ruby', 'extension': 'rb'},
        'php': {'command': 'php', 'extension': 'php'},
        'lua': {'command': 'lua', 'extension': 'lua'},
        'zig': {'command': 'zig run', 'extension': 'zig'}
    }
    
    def __init__(self):
        self.environment_vars = os.environ.copy()
    
    def compile_and_run(self, code: str, language: str) -> Tuple[str, str, int]:
        """
        Compile and run code in the specified language.
        Returns (output, error, return_code)
        """
        if language not in self.SUPPORTED_LANGUAGES:
            return "", f"Unsupported language: {language}", -1
        
        lang_info = self.SUPPORTED_LANGUAGES[language]
        with tempfile.NamedTemporaryFile(suffix=f'.{lang_info["extension"]}', delete=False) as temp:
            temp.write(code.encode('utf-8'))
            temp_path = temp.name
        
        try:
            if language in ['python', 'javascript', 'ruby', 'php', 'lua']:
                # Interpreted languages
                result = subprocess.run(
                    f'{lang_info["command"]} {temp_path}',
                    shell=True,
                    capture_output=True,
                    text=True,
                    env=self.environment_vars
                )
            else:
                # Compiled languages
                compile_result = subprocess.run(
                    f'{lang_info["command"]} {temp_path} -o {temp_path}.out',
                    shell=True,
                    capture_output=True,
                    text=True,
                    env=self.environment_vars
                )
                
                if compile_result.returncode != 0:
                    return "", compile_result.stderr, compile_result.returncode
                
                result = subprocess.run(
                    f'{temp_path}.out',
                    shell=True,
                    capture_output=True,
                    text=True,
                    env=self.environment_vars
                )
            
            return result.stdout, result.stderr, result.returncode
        finally:
            try:
                os.unlink(temp_path)
                if os.path.exists(f'{temp_path}.out'):
                    os.unlink(f'{temp_path}.out')
            except:
                pass
    
    def set_environment_var(self, key: str, value: str):
        """Set environment variable for the compilation process."""
        self.environment_vars[key] = value
    
    def get_supported_languages(self) -> list:
        """Get list of supported languages."""
        return list(self.SUPPORTED_LANGUAGES.keys())
    
    def get_language_info(self, language: str) -> Optional[Dict]:
        """Get information about a specific language."""
        return self.SUPPORTED_LANGUAGES.get(language)