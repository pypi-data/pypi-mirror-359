import re
from pygments import lex
from pygments.lexers import (
    get_lexer_by_name,
    ZigLexer, RustLexer, JavascriptLexer, LuaLexer, PythonLexer,
    HtmlLexer, CssLexer, ScssLexer, JavaLexer, CLexer, CppLexer,
    PhpLexer, SwiftLexer, RubyLexer, CSharpLexer
)
from pygments.formatters import HtmlFormatter
from pygments.styles import get_style_by_name
from pygments.style import Style
from pygments.token import Token

class CustomStyle(Style):
    styles = {
        Token.Keyword: '#569CD6',
        Token.Keyword.Constant: '#4FC1FF',
        Token.Keyword.Declaration: '#569CD6',
        Token.Keyword.Namespace: '#569CD6',
        Token.Keyword.Pseudo: '#569CD6',
        Token.Keyword.Reserved: '#569CD6',
        Token.Keyword.Type: '#4EC9B0',
        Token.Name: '#D4D4D4',
        Token.Name.Attribute: '#9CDCFE',
        Token.Name.Builtin: '#4EC9B0',
        Token.Name.Builtin.Pseudo: '#D4D4D4',
        Token.Name.Class: '#4EC9B0',
        Token.Name.Constant: '#4FC1FF',
        Token.Name.Decorator: '#DCDCAA',
        Token.Name.Entity: '#4EC9B0',
        Token.Name.Exception: '#4EC9B0',
        Token.Name.Function: '#DCDCAA',
        Token.Name.Label: '#C8C8C8',
        Token.Name.Namespace: '#4EC9B0',
        Token.Name.Other: '#D4D4D4',
        Token.Name.Tag: '#569CD6',
        Token.Name.Variable: '#9CDCFE',
        Token.String: '#CE9178',
        Token.String.Doc: '#CE9178',
        Token.String.Escape: '#D7BA7D',
        Token.String.Interpol: '#CE9178',
        Token.String.Other: '#CE9178',
        Token.String.Regex: '#D16969',
        Token.String.Symbol: '#CE9178',
        Token.Number: '#B5CEA8',
        Token.Operator: '#D4D4D4',
        Token.Operator.Word: '#569CD6',
        Token.Comment: '#6A9955',
        Token.Comment.Multiline: '#6A9955',
        Token.Comment.Preproc: '#569CD6',
        Token.Comment.Single: '#6A9955',
        Token.Comment.Special: '#6A9955',
        Token.Punctuation: '#D4D4D4',
    }

class Highlighter:
    LEXER_MAP = {
        'zig': ZigLexer,
        'rust': RustLexer,
        'javascript': JavascriptLexer,
        'js': JavascriptLexer,
        'lua': LuaLexer,
        'python': PythonLexer,
        'py': PythonLexer,
        'html': HtmlLexer,
        'css': CssLexer,
        'scss': ScssLexer,
        'java': JavaLexer,
        'c': CLexer,
        'cs': CSharpLexer,
        'c++': CppLexer,
        'cpp': CppLexer,
        'php': PhpLexer,
        'swift': SwiftLexer,
        'ruby': RubyLexer,
    }
    
    def __init__(self, style='custom'):
        self.style = CustomStyle if style == 'custom' else get_style_by_name(style)
    
    def highlight(self, code, language, inline=False):
        """Highlight code with specified language syntax."""
        if language.lower() not in self.LEXER_MAP:
            raise ValueError(f"Unsupported language: {language}")
        
        lexer = self.LEXER_MAP[language.lower()]()
        formatter = HtmlFormatter(style=self.style, nowrap=inline)
        
        from pygments import highlight
        return highlight(code, lexer, formatter)
    
    def list_languages(self):
        """List all supported languages."""
        return list(self.LEXER_MAP.keys())
    
    def get_css(self, class_name='.highlight'):
        """Get CSS for the highlighted code."""
        formatter = HtmlFormatter(style=self.style)
        return formatter.get_style_defs(class_name)