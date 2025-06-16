# LR语法分析器

这是一个基于LR(0)分析方法的编译器前端实现，包含词法分析和语法分析两个主要部分。该项目提供了一个交互式的Web界面，可以直观地展示编译器的分析过程。

## 功能特点

- **词法分析**：将输入的表达式转换为token序列
- **语法分析**：使用LR(0)分析方法进行语法分析
- **可视化展示**：
  - 预测分析表
  - First集和Follow集
  - 详细的分析过程（状态栈、符号栈、输入串）
  - 分析结果

## 项目结构

```
.
├── app.py              # Flask应用主程序
├── lexer.py           # 词法分析器实现
├── lr_parser.py       # LR语法分析器实现
├── templates/         # HTML模板目录
│   └── index.html     # 主页面模板
└── README.md          # 项目说明文档
```

## 安装步骤

1. 确保已安装Python 3.6或更高版本
2. 安装所需的依赖包：
   ```bash
   pip install flask
   ```

## 使用方法

1. 启动应用：
   ```bash
   python app.py
   ```

2. 在浏览器中访问：
   ```
   http://localhost:5000
   ```

3. 在输入框中输入要分析的表达式，例如：
   ```
   2 + 3 * 4
   ```

4. 点击"分析"按钮，查看分析结果

## 支持的语法

当前实现支持以下语法规则：

```
S -> E
E -> E + T
E -> T
T -> T * F
T -> F
F -> ( E )
F -> id
```

其中：
- `id` 表示标识符或数字
- `+` 表示加法运算符
- `*` 表示乘法运算符
- `(` 和 `)` 表示括号

## 分析过程展示

分析结果页面会显示以下信息：

1. **词法分析结果**：显示输入表达式被分解成的token序列
2. **First集和Follow集**：显示每个非终结符的First集和Follow集
3. **预测分析表**：显示LR(0)分析表
4. **分析过程**：显示每一步分析的状态栈、符号栈、输入串和动作
5. **分析结果**：显示最终的分析结果（成功或失败）

## 注意事项

- 输入表达式时，请确保使用正确的语法格式
- 目前仅支持基本的算术表达式
- 分析过程是实时的，每次输入新的表达式都会重新进行分析

## 未来改进

- [ ] 支持更多的运算符和表达式类型
- [ ] 添加错误恢复机制
- [ ] 优化分析表的展示方式
- [ ] 添加更多的语法规则
- [ ] 支持自定义语法规则

## 扩展指南

### 1. 添加新的语法规则

要添加新的语法规则，需要修改 `lr_parser.py` 中的产生式定义。例如，要支持减法运算，可以这样修改：

```python
# 在 app.py 中添加新的产生式
parser.add_production('E', ['E', '-', 'T'])  # 添加减法规则
```

### 2. 添加新的词法单元

要支持新的词法单元，需要修改 `lexer.py` 中的词法规则。例如，要支持减法运算符：

```python
# 在 lexer.py 中添加新的词法规则
def __init__(self, text):
    self.text = text
    self.pos = 0
    self.current_char = self.text[0] if text else None
    self.tokens = {
        '+': 'PLUS',
        '-': 'MINUS',  # 添加减法运算符
        '*': 'MULTIPLY',
        '(': 'LPAREN',
        ')': 'RPAREN'
    }
```

### 3. 扩展语法分析器

要支持更复杂的语法，可以按以下步骤进行：

1. 定义新的非终结符和终结符
2. 添加相应的产生式
3. 更新运算符优先级（如果需要）

例如，添加除法运算：

```python
# 在 app.py 中
parser = LRParser()

# 添加基本产生式
parser.add_production('S', ['E'])
parser.add_production('E', ['E', '+', 'T'])
parser.add_production('E', ['E', '-', 'T'])
parser.add_production('E', ['T'])
parser.add_production('T', ['T', '*', 'F'])
parser.add_production('T', ['T', '/', 'F'])  # 添加除法
parser.add_production('T', ['F'])
parser.add_production('F', ['(', 'E', ')'])
parser.add_production('F', ['id'])

# 更新运算符优先级
precedence = {
    '*': 2,
    '/': 2,  # 添加除法优先级
    '+': 1,
    '-': 1,  # 添加减法优先级
    '(': 0,
    ')': 0
}
```

### 4. 添加新的功能

#### 4.1 支持浮点数

修改词法分析器以支持浮点数：

```python
# 在 lexer.py 中
def number(self):
    result = ''
    while self.current_char is not None and self.current_char.isdigit():
        result += self.current_char
        self.advance()
    
    # 处理小数点
    if self.current_char == '.':
        result += self.current_char
        self.advance()
        while self.current_char is not None and self.current_char.isdigit():
            result += self.current_char
            self.advance()
    
    return Token('FLOAT', float(result))
```

#### 4.2 支持变量赋值

添加赋值语句支持：

```python
# 在 app.py 中
parser.add_production('S', ['ASSIGNMENT'])
parser.add_production('ASSIGNMENT', ['id', '=', 'E'])
```

#### 4.3 支持函数调用

添加函数调用支持：

```python
# 在 app.py 中
parser.add_production('F', ['id', '(', 'ARGS', ')'])
parser.add_production('ARGS', ['E', 'ARGS_TAIL'])
parser.add_production('ARGS_TAIL', [',', 'E', 'ARGS_TAIL'])
parser.add_production('ARGS_TAIL', ['ε'])
```

### 5. 错误处理

添加错误恢复机制：


### 6. 性能优化

1. 使用缓存优化First集和Follow集的计算
2. 优化分析表的构建过程
3. 使用更高效的数据结构

```python
# 在 lr_parser.py 中
from functools import lru_cache

@lru_cache(maxsize=128)
def compute_first(self, symbol: str) -> Set[str]:
    # 计算First集的代码
    pass
```