from typing import List, Optional, Dict
from dataclasses import dataclass

@dataclass
class Token:
    """词法单元类"""
    type: str
    value: str
    line: int
    column: int

class Lexer:
    """词法分析器"""
    
    def __init__(self, source_code: str):
        self.source_code = source_code
        self.position = 0
        self.line = 1
        self.column = 1
        self.current_char = self.source_code[0] if source_code else None
        
        # 定义关键字
        self.keywords = {
            'if': 'IF',
            'else': 'ELSE',
            'while': 'WHILE',
            'int': 'INT',
            'float': 'FLOAT',
            'return': 'RETURN'
        }
        
    def error(self):
        raise Exception(f'非法字符 {self.current_char} 在位置 {self.line}:{self.column}')
    
    def advance(self):
        """移动到下一个字符"""
        self.position += 1
        if self.position >= len(self.source_code):
            self.current_char = None
        else:
            self.current_char = self.source_code[self.position]
            if self.current_char == '\n':
                self.line += 1
                self.column = 1
            else:
                self.column += 1
    
    def skip_whitespace(self):
        """跳过空白字符"""
        while self.current_char and self.current_char.isspace():
            self.advance()
    
    def get_number(self) -> Token:
        """解析数字"""
        result = ''
        token_type = 'INTEGER'
        
        while self.current_char and (self.current_char.isdigit() or self.current_char == '.'):
            if self.current_char == '.':
                if '.' in result:
                    self.error()
                token_type = 'FLOAT'
            result += self.current_char
            self.advance()
            
        return Token(
            type=token_type,
            value=result,
            line=self.line,
            column=self.column - len(result)
        )
    
    def get_identifier(self) -> Token:
        """解析标识符或关键字"""
        result = ''
        start_column = self.column
        
        while self.current_char and (self.current_char.isalnum() or self.current_char == '_'):
            result += self.current_char
            self.advance()
            
        # 检查是否是关键字
        token_type = self.keywords.get(result, 'IDENTIFIER')
        return Token(
            type=token_type,
            value=result,
            line=self.line,
            column=start_column
        )
    
    def get_next_token(self) -> Optional[Token]:
        """获取下一个词法单元"""
        while self.current_char:
            
            # 跳过空白字符
            if self.current_char.isspace():
                self.skip_whitespace()
                continue
            
            # 数字
            if self.current_char.isdigit():
                return self.get_number()
            
            # 标识符或关键字
            if self.current_char.isalpha() or self.current_char == '_':
                return self.get_identifier()
            
            # 运算符和分隔符
            if self.current_char == '+':
                token = Token('PLUS', '+', self.line, self.column)
                self.advance()
                return token
                
            if self.current_char == '-':
                token = Token('MINUS', '-', self.line, self.column)
                self.advance()
                return token
                
            if self.current_char == '*':
                token = Token('MULTIPLY', '*', self.line, self.column)
                self.advance()
                return token
                
            if self.current_char == '/':
                token = Token('DIVIDE', '/', self.line, self.column)
                self.advance()
                return token
                
            if self.current_char == '(':
                token = Token('LPAREN', '(', self.line, self.column)
                self.advance()
                return token
                
            if self.current_char == ')':
                token = Token('RPAREN', ')', self.line, self.column)
                self.advance()
                return token
                
            if self.current_char == '{':
                token = Token('LBRACE', '{', self.line, self.column)
                self.advance()
                return token
                
            if self.current_char == '}':
                token = Token('RBRACE', '}', self.line, self.column)
                self.advance()
                return token
                
            if self.current_char == '=':
                current_column = self.column
                self.advance()
                if self.current_char == '=':
                    token = Token('EQUALS', '==', self.line, current_column)
                    self.advance()
                else:
                    token = Token('ASSIGN', '=', self.line, current_column)
                return token
                
            if self.current_char == ';':
                token = Token('SEMICOLON', ';', self.line, self.column)
                self.advance()
                return token
            
            self.error()
            
        return Token('EOF', '', self.line, self.column)
    
    def tokenize(self) -> List[Token]:
        """将源代码转换为词法单元列表"""
        tokens = []
        while True:
            token = self.get_next_token()
            tokens.append(token)
            if token.type == 'EOF':
                break
        return tokens 