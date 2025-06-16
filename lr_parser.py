from typing import List, Dict, Set, Tuple
from dataclasses import dataclass
from lexer import Token

@dataclass
class Production:
    """产生式类"""
    left: str  # 左部非终结符
    right: List[str]  # 右部符号列表

@dataclass
class LRItem:
    """LR(0)项类"""
    production: Production
    dot_position: int
    
    def __str__(self):
        right = self.production.right.copy()
        right.insert(self.dot_position, '.')
        return f"{self.production.left} -> {' '.join(right)}"
    
    def __eq__(self, other):
        return (self.production == other.production and 
                self.dot_position == other.dot_position)
    
    def __hash__(self):
        return hash((self.production.left, tuple(self.production.right), 
                    self.dot_position))

class LRParser:
    """LR语法分析器"""
    
    def __init__(self):
        # 文法产生式
        self.productions: List[Production] = []
        # 非终结符集合
        self.non_terminals: Set[str] = set()
        # 终结符集合
        self.terminals: Set[str] = set()
        # First集
        self.first_sets: Dict[str, Set[str]] = {}
        # Follow集
        self.follow_sets: Dict[str, Set[str]] = {}
        # LR(0)项集族
        self.lr0_items: List[Set[LRItem]] = []
        # 动作表
        self.action_table: Dict[Tuple[int, str], Tuple[str, int]] = {}
        # 转移表
        self.goto_table: Dict[Tuple[int, str], int] = {}
        
    def add_production(self, left: str, right: List[str]):
        """添加产生式"""
        self.productions.append(Production(left, right))
        self.non_terminals.add(left)
        for symbol in right:
            if not symbol.isupper() and symbol != 'id':  # 假设终结符都是小写或特殊符号
                self.terminals.add(symbol)
        if 'id' in right:
            self.terminals.add('id')
    
    def compute_first_sets(self):
        """计算First集"""
        # 初始化First集
        for terminal in self.terminals:
            self.first_sets[terminal] = {terminal}
        for non_terminal in self.non_terminals:
            self.first_sets[non_terminal] = set()
            
        while True:
            changed = False
            for production in self.productions:
                left = production.left
                right = production.right
                
                # 如果右部第一个符号是终结符
                if right[0] in self.terminals:
                    if right[0] not in self.first_sets[left]:
                        self.first_sets[left].add(right[0])
                        changed = True
                        
                # 如果右部第一个符号是非终结符
                elif right[0] in self.non_terminals:
                    for symbol in right:
                        if symbol in self.terminals:
                            if symbol not in self.first_sets[left]:
                                self.first_sets[left].add(symbol)
                                changed = True
                            break
                        first_set = self.first_sets[symbol]
                        for first_symbol in first_set:
                            if first_symbol not in self.first_sets[left]:
                                self.first_sets[left].add(first_symbol)
                                changed = True
                        if 'ε' not in first_set:
                            break
                            
            if not changed:
                break
    
    def compute_follow_sets(self):
        """计算Follow集"""
        # 初始化Follow集
        for non_terminal in self.non_terminals:
            self.follow_sets[non_terminal] = set()
        self.follow_sets[self.productions[0].left].add('$')  # 开始符号的Follow集包含$
        
        while True:
            changed = False
            for production in self.productions:
                left = production.left
                right = production.right
                
                for i, symbol in enumerate(right):
                    if symbol in self.non_terminals:
                        # 如果是最后一个符号
                        if i == len(right) - 1:
                            for follow_symbol in self.follow_sets[left]:
                                if follow_symbol not in self.follow_sets[symbol]:
                                    self.follow_sets[symbol].add(follow_symbol)
                                    changed = True
                        else:
                            next_symbol = right[i + 1]
                            if next_symbol in self.terminals:
                                if next_symbol not in self.follow_sets[symbol]:
                                    self.follow_sets[symbol].add(next_symbol)
                                    changed = True
                            else:
                                for first_symbol in self.first_sets[next_symbol]:
                                    if first_symbol != 'ε' and first_symbol not in self.follow_sets[symbol]:
                                        self.follow_sets[symbol].add(first_symbol)
                                        changed = True
                                if 'ε' in self.first_sets[next_symbol]:
                                    for follow_symbol in self.follow_sets[left]:
                                        if follow_symbol not in self.follow_sets[symbol]:
                                            self.follow_sets[symbol].add(follow_symbol)
                                            changed = True
                                            
            if not changed:
                break
    
    def closure(self, items: Set[LRItem]) -> Set[LRItem]:
        """计算LR(0)项集的闭包"""
        result = items.copy()
        while True:
            new_items = set()
            for item in result:
                if item.dot_position < len(item.production.right):
                    symbol_after_dot = item.production.right[item.dot_position]
                    if symbol_after_dot in self.non_terminals:
                        for production in self.productions:
                            if production.left == symbol_after_dot:
                                new_item = LRItem(production, 0)
                                if new_item not in result:
                                    new_items.add(new_item)
            
            if not new_items:
                break
            result.update(new_items)
        
        return result
    
    def goto(self, items: Set[LRItem], symbol: str) -> Set[LRItem]:
        """计算GOTO(I,X)"""
        next_items = set()
        for item in items:
            if (item.dot_position < len(item.production.right) and 
                item.production.right[item.dot_position] == symbol):
                next_items.add(LRItem(item.production, item.dot_position + 1))
        return self.closure(next_items)
    
    def build_lr0_items(self):
        """构建LR(0)项集族"""
        # 添加增广文法的起始产生式
        start_production = Production("S'", [self.productions[0].left])
        initial_item = LRItem(start_production, 0)
        initial_set = self.closure({initial_item})
        
        self.lr0_items = [initial_set]
        processed_sets = set()
        
        while True:
            new_item_sets = []
            for items in self.lr0_items:
                items_tuple = tuple(sorted(str(item) for item in items))
                if items_tuple in processed_sets:
                    continue
                    
                processed_sets.add(items_tuple)
                symbols = set()
                for item in items:
                    if item.dot_position < len(item.production.right):
                        symbols.add(item.production.right[item.dot_position])
                        
                for symbol in symbols:
                    next_items = self.goto(items, symbol)
                    if next_items and next_items not in self.lr0_items:
                        new_item_sets.append(next_items)
                        
            if not new_item_sets:
                break
            self.lr0_items.extend(new_item_sets)
    
    def build_parsing_table(self):
        """构建LR分析表"""
        self.action_table.clear()
        self.goto_table.clear()
        
        # 定义运算符优先级
        precedence = {
            '*': 2,  # 乘法优先级高
            '+': 1,  # 加法优先级低
            '(': 0,  # 括号优先级最低
            ')': 0
        }
        
        for i, items in enumerate(self.lr0_items):
            for item in items:
                if item.dot_position < len(item.production.right):
                    # 移进动作
                    symbol = item.production.right[item.dot_position]
                    next_items = self.goto(items, symbol)
                    if next_items in self.lr0_items:
                        j = self.lr0_items.index(next_items)
                        if symbol in self.terminals:
                            self.action_table[(i, symbol)] = ('shift', j)
                        else:
                            self.goto_table[(i, symbol)] = j
                else:
                    # 归约动作
                    if item.production.left == "S'":
                        self.action_table[(i, '$')] = ('accept', 0)
                    else:
                        # 检查是否需要归约
                        need_reduce = True
                        if item.production.right:
                            last_symbol = item.production.right[-1]
                            if last_symbol in precedence:
                                for terminal in self.terminals | {'$'}:
                                    if terminal in precedence:
                                        if precedence[terminal] > precedence[last_symbol]:
                                            need_reduce = False
                                            break
                        
                        if need_reduce:
                            for terminal in self.terminals | {'$'}:
                                if (i, terminal) not in self.action_table:
                                    self.action_table[(i, terminal)] = ('reduce', 
                                        self.productions.index(item.production))
    
    def get_parsing_table(self) -> Dict[str, Dict[str, str]]:
        """获取格式化的分析表"""
        table = {}
        all_symbols = self.terminals | {'$'} | self.non_terminals
        
        for i in range(len(self.lr0_items)):
            table[str(i)] = {}
            for symbol in all_symbols:
                if (i, symbol) in self.action_table:
                    action, value = self.action_table[(i, symbol)]
                    if action == 'shift':
                        table[str(i)][symbol] = f's{value}'
                    elif action == 'reduce':
                        table[str(i)][symbol] = f'r{value}'
                    elif action == 'accept':
                        table[str(i)][symbol] = 'acc'
                elif (i, symbol) in self.goto_table:
                    table[str(i)][symbol] = str(self.goto_table[(i, symbol)])
        
        return table
    
    def get_first_sets(self) -> Dict[str, List[str]]:
        """获取格式化的First集"""
        return {k: sorted(list(v)) for k, v in self.first_sets.items()}
    
    def get_follow_sets(self) -> Dict[str, List[str]]:
        """获取格式化的Follow集"""
        return {k: sorted(list(v)) for k, v in self.follow_sets.items()}
    
    def parse_with_steps(self, tokens: List[str]) -> Tuple[bool, List[Dict]]:
        """带步骤的语法分析"""
        steps = []
        state_stack = [0]  # 状态栈
        symbol_stack = ['$']  # 符号栈
        input_pos = 0  # 输入串位置
        
        while True:
            current_state = state_stack[-1]
            current_token = tokens[input_pos]
            
            # 记录当前步骤
            step = {
                'stateStack': state_stack.copy(),
                'symbolStack': symbol_stack.copy(),
                'input': tokens[input_pos:],
                'action': ''
            }
            
            if (current_state, current_token) in self.action_table:
                action, value = self.action_table[(current_state, current_token)]
                
                if action == 'shift':
                    state_stack.append(value)
                    symbol_stack.append(current_token)
                    input_pos += 1
                    step['action'] = f'移进 {current_token}'
                    
                elif action == 'reduce':
                    production = self.productions[value]
                    for _ in range(len(production.right)):
                        state_stack.pop()
                        symbol_stack.pop()
                    
                    symbol_stack.append(production.left)
                    current_state = state_stack[-1]
                    state_stack.append(self.goto_table[(current_state, production.left)])
                    step['action'] = f'归约 {production.left} -> {" ".join(production.right)}'
                    
                elif action == 'accept':
                    step['action'] = '接受'
                    steps.append(step)
                    return True, steps
                    
            else:
                step['action'] = '错误'
                steps.append(step)
                return False, steps
            
            steps.append(step)
    
    def parse(self, tokens: List[str]) -> bool:
        """语法分析（向后兼容）"""
        success, _ = self.parse_with_steps(tokens)
        return success 