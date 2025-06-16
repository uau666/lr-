from flask import Flask, render_template, request, jsonify
from lexer import Lexer
from lr_parser import LRParser

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    expression = data.get('expression', '')
    
    try:
        # 词法分析
        lexer = Lexer(expression)
        tokens = []
        while True:
            token = lexer.get_next_token()
            if token.type == 'EOF':
                break
            tokens.append({
                'type': token.type,
                'value': token.value
            })
        
        # 语法分析
        parser = LRParser()
        # 添加产生式
        parser.add_production('S', ['E'])
        parser.add_production('E', ['E', '+', 'T'])
        parser.add_production('E', ['T'])
        parser.add_production('T', ['T', '*', 'F'])
        parser.add_production('T', ['F'])
        parser.add_production('F', ['(', 'E', ')'])
        parser.add_production('F', ['id'])
        # 计算First集和Follow集
        parser.compute_first_sets()
        parser.compute_follow_sets()
        # 构建LR(0)项集族和分析表
        parser.build_lr0_items()
        parser.build_parsing_table()

        # Token类型到终结符的映射
        token_to_terminal = {
            'IDENTIFIER': 'id',
            'INTEGER': 'id',
            'FLOAT': 'id',
            'PLUS': '+',
            'MULTIPLY': '*',
            'LPAREN': '(',
            'RPAREN': ')',
            'EOF': '$'
        }
        mapped_tokens = [token_to_terminal.get(token['type'], token['value']) for token in tokens] + ['$']
        
        # 获取分析表和First/Follow集
        parsing_table = parser.get_parsing_table()
        first_sets = parser.get_first_sets()
        follow_sets = parser.get_follow_sets()
        
        # 执行语法分析并获取分析过程
        result, analysis_steps = parser.parse_with_steps(mapped_tokens)
        
        return jsonify({
            'success': True,
            'tokens': tokens,
            'ast': '分析' + ('成功' if result else '失败'),
            'parsing_table': parsing_table,
            'first_sets': first_sets,
            'follow_sets': follow_sets,
            'analysis_steps': analysis_steps
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) 