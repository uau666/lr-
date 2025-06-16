from lexer import Lexer
from lr_parser import LRParser

def main():
    # 创建一个简单的文法
    parser = LRParser()
    
    # 添加产生式
    # S -> E
    # E -> E + T | T
    # T -> T * F | F
    # F -> ( E ) | id
    
    # 修改后的产生式，处理运算符优先级
    parser.add_production('S', ['E'])  # 起始产生式
    parser.add_production('E', ['E', '+', 'T'])  # 加法
    parser.add_production('E', ['T'])  # E可以直接推导出T
    parser.add_production('T', ['T', '*', 'F'])  # 乘法（优先级高于加法）
    parser.add_production('T', ['F'])  # T可以直接推导出F
    parser.add_production('F', ['(', 'E', ')'])  # 括号（最高优先级）
    parser.add_production('F', ['id'])  # 标识符
    
    # 计算First集和Follow集
    parser.compute_first_sets()
    parser.compute_follow_sets()
    
    # 构建LR(0)项集族和分析表
    parser.build_lr0_items()
    parser.build_parsing_table()
    
    # 打印First集和Follow集
    print("First集:")
    for symbol, first_set in sorted(parser.first_sets.items()):
        print(f"{symbol}: {first_set}")
    
    print("\nFollow集:")
    for symbol, follow_set in sorted(parser.follow_sets.items()):
        print(f"{symbol}: {follow_set}")
    
    print("\nLR(0)项集族:")
    for i, items in enumerate(parser.lr0_items):
        print(f"\n状态 {i}:")
        for item in sorted(items, key=str):
            print(f"  {item}")
    
    # 测试用例
    test_cases = [
        "x + y * z",
        "(a + b) * c",
        "a * (b + c) * d",
        "a + b + c * d"
    ]
    
    # Token类型到终结符的映射
    token_to_terminal = {
        'IDENTIFIER': 'id',
        'PLUS': '+',
        'MULTIPLY': '*',
        'LPAREN': '(',
        'RPAREN': ')',
        'EOF': '$'
    }
    
    for test_input in test_cases:
        print(f"\n{'='*50}")
        print(f"分析输入: {test_input}")
        
        # 词法分析
        lexer = Lexer(test_input)
        tokens = lexer.tokenize()
        
        print("\n词法分析结果:")
        for token in tokens:
            print(f"  {token}")
            
        # 将token类型转换为终结符
        mapped_tokens = [token_to_terminal[token.type] for token in tokens] + ['$']
        
        # 语法分析
        print(f"\n开始语法分析...")
        result = parser.parse(mapped_tokens)
        print(f"\n语法分析结果: {'成功' if result else '失败'}")

if __name__ == "__main__":
    main() 