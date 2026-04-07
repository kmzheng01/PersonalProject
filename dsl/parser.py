"""DSL parser for AudioStream feature definitions."""

import re
from typing import List, Dict, Any, Optional, Union
from enum import Enum

from utils.logger import get_logger

logger = get_logger(__name__)


class TokenType(Enum):
    """DSL token types."""
    KEYWORD = "KEYWORD"
    IDENTIFIER = "IDENTIFIER"
    STRING = "STRING"
    NUMBER = "NUMBER"
    LPAREN = "LPAREN"
    RPAREN = "RPAREN"
    LBRACE = "LBRACE"
    RBRACE = "RBRACE"
    COMMA = "COMMA"
    EQUALS = "EQUALS"
    DOT = "DOT"
    COLON = "COLON"
    ARROW = "ARROW"
    EOF = "EOF"


class Token:
    """Represents a DSL token."""

    def __init__(self, type_: TokenType, value: Any, line: int = 1, column: int = 1):
        self.type = type_
        self.value = value
        self.line = line
        self.column = column

    def __repr__(self) -> str:
        return f"Token({self.type.value}, {self.value!r})"


class DSLLexer:
    """Tokenizer for DSL."""

    KEYWORDS = {
        'define', 'feature', 'function', 'on', 'if', 'else', 'while', 'for',
        'return', 'true', 'false', 'null', 'import', 'as',
    }

    def __init__(self, code: str):
        self.code = code
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens: List[Token] = []

    def error(self, message: str) -> None:
        """Report lexer error."""
        raise SyntaxError(f"Lexer error at line {self.line}, column {self.column}: {message}")

    def peek(self, offset: int = 0) -> Optional[str]:
        """Peek at character."""
        pos = self.pos + offset
        return self.code[pos] if pos < len(self.code) else None

    def advance(self) -> Optional[str]:
        """Get next character."""
        if self.pos >= len(self.code):
            return None
        
        ch = self.code[self.pos]
        self.pos += 1
        
        if ch == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        
        return ch

    def skip_whitespace(self) -> None:
        """Skip whitespace and comments."""
        while self.peek() and self.peek() in ' \t\n\r':
            self.advance()
        
        # Skip comments
        if self.peek() == '#':
            while self.peek() and self.peek() != '\n':
                self.advance()
            if self.peek() == '\n':
                self.advance()
            self.skip_whitespace()

    def read_string(self, quote: str) -> str:
        """Read string literal."""
        result = ""
        self.advance()  # Skip opening quote
        
        while self.peek() and self.peek() != quote:
            if self.peek() == '\\':
                self.advance()
                next_ch = self.advance()
                if next_ch == 'n':
                    result += '\n'
                elif next_ch == 't':
                    result += '\t'
                elif next_ch == 'r':
                    result += '\r'
                elif next_ch == '\\':
                    result += '\\'
                elif next_ch == quote:
                    result += quote
                else:
                    result += next_ch or ''
            else:
                result += self.advance() or ""
        
        if self.peek() != quote:
            self.error(f"Unterminated string")
        
        self.advance()  # Skip closing quote
        return result

    def read_number(self) -> Union[int, float]:
        """Read number literal."""
        result = ""
        while self.peek() and (self.peek().isdigit() or self.peek() == '.'):
            result += self.advance()
        
        return float(result) if '.' in result else int(result)

    def read_identifier(self) -> str:
        """Read identifier or keyword."""
        result = ""
        while self.peek() and (self.peek().isalnum() or self.peek() in '_-'):
            result += self.advance()
        return result

    def tokenize(self) -> List[Token]:
        """Tokenize DSL code."""
        while self.pos < len(self.code):
            self.skip_whitespace()
            
            if self.pos >= len(self.code):
                break
            
            ch = self.peek()
            
            # String literals
            if ch in ('"', "'"):
                value = self.read_string(ch)
                self.tokens.append(Token(TokenType.STRING, value, self.line, self.column))
            
            # Numbers
            elif ch.isdigit():
                value = self.read_number()
                self.tokens.append(Token(TokenType.NUMBER, value, self.line, self.column))
            
            # Identifiers and keywords
            elif ch.isalpha() or ch == '_':
                value = self.read_identifier()
                if value in self.KEYWORDS:
                    self.tokens.append(Token(TokenType.KEYWORD, value, self.line, self.column))
                else:
                    self.tokens.append(Token(TokenType.IDENTIFIER, value, self.line, self.column))
            
            # Operators and delimiters
            elif ch == '(':
                self.advance()
                self.tokens.append(Token(TokenType.LPAREN, '(', self.line, self.column))
            elif ch == ')':
                self.advance()
                self.tokens.append(Token(TokenType.RPAREN, ')', self.line, self.column))
            elif ch == '{':
                self.advance()
                self.tokens.append(Token(TokenType.LBRACE, '{', self.line, self.column))
            elif ch == '}':
                self.advance()
                self.tokens.append(Token(TokenType.RBRACE, '}', self.line, self.column))
            elif ch == ',':
                self.advance()
                self.tokens.append(Token(TokenType.COMMA, ',', self.line, self.column))
            elif ch == '=':
                self.advance()
                if self.peek() == '>':
                    self.advance()
                    self.tokens.append(Token(TokenType.ARROW, '=>', self.line, self.column))
                else:
                    self.tokens.append(Token(TokenType.EQUALS, '=', self.line, self.column))
            elif ch == '.':
                self.advance()
                self.tokens.append(Token(TokenType.DOT, '.', self.line, self.column))
            elif ch == ':':
                self.advance()
                self.tokens.append(Token(TokenType.COLON, ':', self.line, self.column))
            else:
                self.advance()
        
        self.tokens.append(Token(TokenType.EOF, None, self.line, self.column))
        return self.tokens


class DSLParser:
    """Parser for DSL code."""

    def __init__(self, code: str):
        lexer = DSLLexer(code)
        self.tokens = lexer.tokenize()
        self.pos = 0

    def error(self, message: str) -> None:
        """Report parser error."""
        token = self.current_token()
        raise SyntaxError(f"Parser error at line {token.line}: {message}")

    def current_token(self) -> Token:
        """Get current token."""
        return self.tokens[min(self.pos, len(self.tokens) - 1)]

    def peek_token(self, offset: int = 1) -> Token:
        """Peek at token."""
        return self.tokens[min(self.pos + offset, len(self.tokens) - 1)]

    def advance(self) -> Token:
        """Move to next token."""
        token = self.current_token()
        if self.current_token().type != TokenType.EOF:
            self.pos += 1
        return token

    def expect(self, type_: TokenType) -> Token:
        """Expect specific token type."""
        token = self.current_token()
        if token.type != type_:
            self.error(f"Expected {type_.value}, got {token.type.value}")
        return self.advance()

    def match(self, *types: TokenType) -> bool:
        """Check if current token matches any type."""
        return self.current_token().type in types

    def parse(self) -> List[Dict[str, Any]]:
        """Parse DSL code."""
        statements = []
        
        while self.current_token().type != TokenType.EOF:
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
        
        return statements

    def parse_statement(self) -> Optional[Dict[str, Any]]:
        """Parse a single statement."""
        if self.match(TokenType.KEYWORD):
            keyword = self.current_token().value
            
            if keyword == 'define':
                return self.parse_define()
            elif keyword == 'function':
                return self.parse_function()
            elif keyword == 'import':
                return self.parse_import()
        
        return None

    def parse_define(self) -> Dict[str, Any]:
        """Parse define statement."""
        self.expect(TokenType.KEYWORD)  # 'define'
        
        if self.current_token().value != 'feature':
            self.error("Expected 'feature' after 'define'")
        
        self.advance()  # 'feature'
        
        name_token = self.expect(TokenType.STRING)
        feature_name = name_token.value
        
        self.expect(TokenType.LBRACE)
        
        body = self.parse_block()
        
        self.expect(TokenType.RBRACE)
        
        return {
            'type': 'define_feature',
            'name': feature_name,
            'body': body,
        }

    def parse_function(self) -> Dict[str, Any]:
        """Parse function definition."""
        self.expect(TokenType.KEYWORD)  # 'function'
        
        name_token = self.expect(TokenType.IDENTIFIER)
        function_name = name_token.value
        
        self.expect(TokenType.LPAREN)
        params = self.parse_parameters()
        self.expect(TokenType.RPAREN)
        
        self.expect(TokenType.LBRACE)
        body = self.parse_block()
        self.expect(TokenType.RBRACE)
        
        return {
            'type': 'function',
            'name': function_name,
            'params': params,
            'body': body,
        }

    def parse_parameters(self) -> List[str]:
        """Parse function parameters."""
        params = []
        
        while self.current_token().type == TokenType.IDENTIFIER:
            params.append(self.advance().value)
            if self.match(TokenType.COMMA):
                self.advance()
        
        return params

    def parse_block(self) -> List[Dict[str, Any]]:
        """Parse code block."""
        statements = []
        
        while self.current_token().type != TokenType.RBRACE and \
              self.current_token().type != TokenType.EOF:
            if self.match(TokenType.KEYWORD) and self.current_token().value == 'on':
                statements.append(self.parse_event_handler())
            else:
                self.advance()
        
        return statements

    def parse_event_handler(self) -> Dict[str, Any]:
        """Parse event handler."""
        self.expect(TokenType.KEYWORD)  # 'on'
        
        event_name = self.expect(TokenType.IDENTIFIER).value
        
        self.expect(TokenType.LBRACE)
        body = self.parse_block()
        self.expect(TokenType.RBRACE)
        
        return {
            'type': 'event_handler',
            'event': event_name,
            'body': body,
        }

    def parse_import(self) -> Dict[str, Any]:
        """Parse import statement."""
        self.expect(TokenType.KEYWORD)  # 'import'
        
        module = self.expect(TokenType.STRING).value
        
        alias = None
        if self.match(TokenType.KEYWORD) and self.current_token().value == 'as':
            self.advance()
            alias = self.expect(TokenType.IDENTIFIER).value
        
        return {
            'type': 'import',
            'module': module,
            'alias': alias,
        }
