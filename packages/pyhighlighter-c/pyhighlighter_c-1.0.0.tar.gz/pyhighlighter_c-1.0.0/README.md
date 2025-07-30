# Highlighter

Advanced syntax highlighting library with built-in compiler (dockr) for multiple languages.

## Features

- Syntax highlighting for 15+ languages
- Integrated compiler/runner (dockr)
- Customizable color schemes
- HTML and terminal output formats
- Easy to extend with new languages

## Installation

```bash
pip install highlighter
```

## Usage

### Syntax Highlighting

```python
from highlighter import Highlighter

hl = Highlighter()
code = """
def hello(name):
    print(f"Hello, {name}!")
"""

# Get HTML output
html_output = hl.highlight(code, "python")
print(html_output)

# Get terminal output
term_output = hl.highlight(code, "python", output_format="terminal")
print(term_output)

# Get CSS for the highlighting
print(hl.get_css())
```

### Dockr Compiler

```python
from highlighter import DockrCompiler

compiler = DockrCompiler()
code = """
#include <stdio.h>

int main() {
    printf("Hello from C!\\n");
    return 0;
}
"""

output, error, return_code = compiler.compile_and_run(code, "c")
print(f"Output: {output}")
print(f"Error: {error}")
print(f"Return code: {return_code}")
```

### Command Line Usage

```bash
# Run a Python file
dockr script.py

# Run a C file with input
dockr program.c -i input.txt
```

## Supported Languages

- Python, JavaScript, Ruby, PHP, Lua
- C, C++, Java, Rust, Zig
- HTML, CSS, SCSS
- And more!

## License

MIT