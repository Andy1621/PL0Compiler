#! env python3
# -*- coding: UTF-8 -*-

from flask import Flask, render_template, request
from tools import lexer, opg, parser, interpreter
import json

app = Flask(__name__)

lexer_engine = lexer.LexerEngine()
opg_engine = opg.OPGEngine()
parser_engine = parser.Parser()
interpreter_engine = interpreter.Interpreter()


@app.route('/lexer')
def lexer():
    return render_template('lexer.html')


@app.route('/opg')
def opg():
    return render_template('opg.html')


@app.route('/')
@app.route('/compiler')
def compiler():
    global p_code
    p_code = []
    return render_template('compiler.html')


@app.route('/help')
def help():
    return render_template('help.html')


@app.route('/homework1')
def homework1():
    return render_template('homework1.html')


@app.route('/homework2')
def homework2():
    return render_template('homework2.html')


@app.route('/api/v1/lexer', methods=['POST'])
def api_lexer():
    lexer_engine.load_file_by_content(request.form['code'])
    res = lexer_engine.complete_token()
    return json.dumps(res)


@app.route('/api/v1/opg', methods=['POST'])
def api_opg():
    grammar = request.form['grammar'].replace('\r', '').split('\n')
    sentence = ''.join(request.form['sentence'].split())
    opg_engine.get_rules(grammar)
    res = dict()
    res['priority_table'] = opg_engine.complete_priority_table()
    res['analyse'] = opg_engine.complete_analyse(sentence)

    return json.dumps(res)


@app.route('/api/v1/compiler', methods=['POST'])
def api_compiler():
    parser_engine.load_program(request.form['code'])
    code, code_list, msg = parser_engine.get_result()
    res = dict()
    res['code'] = code_list
    res['msg'] = msg
    return json.dumps(res)


@app.route('/api/v1/interpreter', methods=['POST'])
def api_interpreter():
    parser_engine.load_program(request.form['code'])
    code, code_list, msg = parser_engine.get_result()
    interpreter_engine.input = request.form['in'].strip().split()
    output = interpreter_engine.get_output(code)
    res = dict()
    res['code'] = code_list
    res['msg'] = msg
    res['output'] = output
    return json.dumps(res)


if __name__ == '__main__':
    app.run(debug=True)
