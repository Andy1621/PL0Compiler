#!/usr/bin/python 
# -*- coding: UTF-8 -*-

from lexer2 import LexerEngine, Token
from enum import Enum
from exceptions import *
from copy import deepcopy


# 合法后继集合
declaration_head = [
    'const', 'var', 'procedure'     # 值
]
factor_head = [
    'IDENTIFIER', 'NUMBER',     # 类型
    '('     # 值
]
statement_head = [
    'IDENTIFIER',   # 类型
    'if', 'while', 'call', 'read', 'write', 'begin', 'repeat'   # 值
]


# 最大嵌套层数
LEVEL_MAX = 3
# PL/0整数最大值
INT_MAX = 2147483647


# P-code枚举类
class OPCode(Enum):
    LIT = 1
    OPR = 2
    LOD = 3
    STO = 4
    CAL = 5
    INT = 6
    JMP = 7
    JPC = 8
    RED = 9
    WRT = 10


# 指令类
class PCode:
    def __init__(self, f, l, a):
        self.f = f
        self.l = l
        self.a = a

    def __str__(self):
        return '({}\t{}\t{})'.format(self.f.name, self.l, self.a)


# 符号类
class Symbol:
    def __init__(self, name=None, kind=None, val=None, level=None, adr=None):
        self.name = name
        self.kind = kind
        self.val = val
        self.level = level
        self.adr = adr

    def __str__(self):
        return '({}\t{}\t{}\t{}\t{})'.format(self.name, self.kind, self.val, self.level, self.adr)


# 指令表
class PCodeEngine:
    def __init__(self):
        self.code = []

    def __getitem__(self, item):
        return self.code[item]

    def __setitem__(self, key, value):
        self.code[key] = value

    def __len__(self):
        return len(self.code)

    def get(self):
        return self.code

    def gen(self, f, l, a):
        self.code.append(PCode(f, l, a))

    def clear(self):
        self.code.clear()


# 符号表
class SymbolTable:
    def __init__(self):
        self.table = []

    def __getitem__(self, item):
        return self.table[item]

    def __setitem__(self, key, value):
        self.table[key] = value

    def __len__(self):
        return len(self.table)

    def get(self, name, kind=None, pos=(1, 1)):
        for symbol in self.table[::-1]:
            if symbol.name == name:
                if kind and symbol.kind != kind:
                    e = ParserError(pos=pos, error_num=29)
                    return e.message
                else:
                    return symbol
        e = ParserError(pos=pos, error_num=11)
        return e.message

    def enter(self, symbol, pos=(1, 1)):
        for t_symbol in self.table[::-1]:
            if symbol.level != t_symbol.level:
                break
            if symbol.name == t_symbol.name:
                e = ParserError(pos=pos, error_num=31)
                return e.message
        if symbol.kind == 'const' and '.' in symbol.val:
            e = ParserError(pos=pos, error_num=34)
            return e.message
        self.table.append(deepcopy(symbol))     # 深拷贝，常量和变量声明中循环登录，浅拷贝拷贝地址导致所有都会改变
        return None

    def print(self):
        for t_symbol in self.table[::-1]:
            print(t_symbol)
        print('------------------------')

    def clear(self):
        self.table.clear()


# 错误控制器
class ErrorManager:
    def __init__(self):
        self.error = []
        self.errorMsg = {
            1: "常数说明中应是'='而不是':='",
            2: "常数说明中'='后应为数字",
            3: "常数说明中标识符后应为'='",
            4: "const,var,procedure后应为标识符",
            5: "漏掉逗号或分号",
            6: "过程说明后的符号不正确",
            7: "应为语句开始符号",
            8: "程序体内语句部分后的符号不正确",
            9: "程序结尾应为句号",
            10: "语句之间漏了分号",
            11: "标识符未说明",
            12: "不可向常量或过程赋值",
            13: "赋值语句中应为赋值运算符':='",
            14: "call后应为标识符",
            15: "call后标识符属性应为过程，不可调用常量或变量",
            16: "条件语句中缺失then",
            17: "应为分号或end",
            18: "当到型循环语句中缺失do",
            19: "语句后的符号不正确",
            20: "应为关系运算符",
            21: "表达式内不可有过程标识符",
            22: "缺失右括号",
            23: "因子后不可为此符号",
            24: "表达式不能以此符号开始",
            25: "循环语句中缺失until",
            26: "读语句括号内不是标识符",
            27: "写语句括号内不是表达式",
            28: "读语句括号内的标识符属性应为变量",
            29: "标识符类型不正确",
            30: "这个数太大，超过INT32_MAX",
            31: "标识符重名",
            32: "嵌套层数过多",
            33: "句号后程序未结束",
            34: "应为整数而不是浮点数",
            40: "应为左括号",
            50: "无法识别的符号"
        }

    def __len__(self):
        return len(self.error)

    def add(self, pos, error_num):
        self.error.append('Error({0}, {1}): {2}'.format(pos[0], pos[1], self.errorMsg[error_num]))

    def direct_add(self, e):
        self.error.append(e)

    def print(self):
        for i, e in enumerate(self.error):
            print('{0:4} {1}'.format(i+1, e))

    def clear(self):
        self.error.clear()


# P-code生成器
class Parser:
    def __init__(self):
        self.lexer = LexerEngine()
        self.token = None
        self.curToken = None
        self.curLevel = -1
        self.table = SymbolTable()
        self.p_code = PCodeEngine()
        self.error = ErrorManager()

    # 加载PL/0源代码
    def load_program(self, program):
        self.token = None
        self.curToken = None
        self.curLevel = -1
        self.table.clear()
        self.p_code.clear()
        self.error.clear()
        self.lexer.load_file_by_content(program)
        self.token = self.lexer.get_token()

    # 词法分析读取一个单词
    def _get_symbol(self):
        self.curToken = next(self.token)
        while self.curToken.type == 'OTHER':
            self.error.add(pos=self._error_pos(), error_num=50)
            self.curToken = next(self.token)

    # 判断得到单词是否符合文法
    def _expect(self, token, pos=None, error_num=0):
        if pos is None:
            pos = self._error_pos()
        if token.type is None:
            ok = token.value == self.curToken.value
        elif token.value is None:
            ok = token.type == self.curToken.type
        else:
            ok = token == self.curToken
        if not ok:
            if error_num == 1:
                if self.curToken.value != ':=':
                    error_num = 3
            self.error.add(pos=pos, error_num=error_num)

    # 检查后继符号合法性，symbol_set1为当前语法合法后继符号集合
    # symbol_set2为停止符号集合，error_num为错误编号
    def _test(self, symbol_set1, symbol_set2, error_num):
        if self.curToken.type not in symbol_set1 and self.curToken.value not in symbol_set1:
            print('err_pos: ', self._error_pos())
            self.error.add(pos=self._error_pos(), error_num=error_num)
            t_set = symbol_set1 + symbol_set2
            while self.curToken.type not in t_set and self.curToken.value not in t_set:
                self._get_symbol()

    # 获取出错的准确位置
    def _error_pos(self):
        pos = deepcopy(self.lexer.pos)
        pos[1] = pos[1] - len(self.curToken.value)
        return pos

    # 返回字典格式的结果，用于前端显示
    def get_result(self):
        self._program()
        p_code = self.p_code.get()
        code_list = list()
        code_list.append({
            'n': 'Number',
            'f': 'Operation',
            'l': 'Layer',
            'a': 'Address',
        })
        for i, code in enumerate(p_code):
            code_list.append({
                'n': i,
                'f': code.f.name,
                'l': code.l,
                'a': code.a,
            })
        msg = list()
        if len(self.error) > 0:
            msg.append({
                'state': 'fail',
                'abbr': '代码中存在' + str(len(self.error)) +'个错误'
            })
            msg.append({
                'msg': '编译发生错误，请检查！！！'
            })
            for e in self.error.error:
                msg.append({
                    'msg': e
                })
        else:
            msg.append({
                'state': 'success'
            })
            msg.append({
                'msg': '编译成功，可执行解释'
            })
            msg.append({
                'msg': '程序中若有输入，请先输入数据'
            })
        return p_code, code_list, msg

    # 调用_program()子程序开始语法分析，打印生成的P-code
    def analyse(self):
        self._program()
        for i, code in enumerate(self.p_code.get()):
            print('{:4}\t'.format(i), end='')
            print(code)
        if len(self.error) > 0:
            print('编译发生错误！！！')
            self.error.print()
            check = 'fail'
        else:
            print('编译成功！')
            check = 'success'
        return check, self.p_code.get()

    # 程序
    def _program(self):
        try:
            self._get_symbol()
            self.table.enter(Symbol(), pos=self._error_pos())
            t_set = declaration_head + statement_head
            t_set.append('.')
            self._block(3, t_set)
            self._expect(Token(None, '.'), error_num=9)
            try:
                self._get_symbol()
                self.error.add(pos=self._error_pos(), error_num=33)
            except StopIteration:
                pass
        except StopIteration:
            self.error.add(pos=self._error_pos(), error_num=9)

    # 分程序
    def _block(self, dx, symbol_set):
        def _const():
            def _const_deal():
                if self.curToken.type == 'IDENTIFIER':
                    symbol.name = self.curToken.value
                    self._get_symbol()
                    if self.curToken.value == '=' or self.curToken.value == ':=':
                        if self.curToken.value == ':=':
                            self.error.add(pos=self._error_pos(), error_num=1)
                        self._get_symbol()
                        if self.curToken.type == 'NUMBER':
                            symbol.val = self.curToken.value
                            res = self.table.enter(symbol, pos=self._error_pos())
                            if res is not None:
                                self.error.direct_add(res)
                            self._get_symbol()
                        else:
                            self.error.add(pos=self._error_pos(), error_num=2)
                    else:
                        self.error.add(pos=self._error_pos(), error_num=3)
                else:
                    self.error.add(pos=self._error_pos(), error_num=4)

            symbol = Symbol(kind='const')
            _const_deal()
            while self.curToken.value == ',':
                self._get_symbol()
                _const_deal()
            if self.curToken.value == ';':
                self._get_symbol()
            else:
                self.error.add(pos=self._error_pos(), error_num=5)

        def _var():
            def _var_deal():
                nonlocal dx
                if self.curToken.type == 'IDENTIFIER':
                    symbol.name = self.curToken.value
                    symbol.adr = dx
                    dx += 1
                    res = self.table.enter(symbol, pos=self._error_pos())
                    if res is not None:
                        self.error.direct_add(res)
                    self._get_symbol()
                else:
                    self.error.add(pos=self._error_pos(), error_num=4)

            symbol = Symbol(kind='var', level=self.curLevel)
            _var_deal()
            while self.curToken.value == ',':
                self._get_symbol()
                _var_deal()
            if self.curToken.value == ';':
                self._get_symbol()
            else:
                self.error.add(pos=self._error_pos(), error_num=5)

        def _proc():
            symbol = Symbol(kind='proc', level=self.curLevel)
            while self.curToken.value == 'procedure':
                self._get_symbol()
                if self.curToken.type == 'IDENTIFIER':
                    symbol.name = self.curToken.value
                    res = self.table.enter(symbol, pos=self._error_pos())
                    if res is not None:
                        self.error.direct_add(res)
                    self._get_symbol()
                else:
                    self.error.add(pos=self._error_pos(), error_num=4)
                if self.curToken.value == ';':
                    self._get_symbol()
                else:
                    self.error.add(pos=self._error_pos(), error_num=5)
                t_set = deepcopy(symbol_set)
                t_set.append(';')
                self._block(3, t_set)
                if self.curToken.value == ';':
                    self._get_symbol()
                    t_set2 = deepcopy(statement_head)
                    t_set2.append('IDENTIFIER')
                    t_set2.append('procedure')
                    self._test(t_set2, symbol_set, 6)
                else:
                    self.error.add(pos=self._error_pos(), error_num=5)

        self.curLevel += 1
        tx0 = len(self.table) - 1
        code1 = len(self.p_code)
        self.p_code.gen(OPCode.JMP, 0, 0)   # 产生跳转指令，跳转位置未知暂时填0

        if self.curLevel > LEVEL_MAX:
            self.error.add(pos=self._error_pos(), error_num=32)

        while True:
            if self.curToken.value == 'const':
                self._get_symbol()
                _const()
            if self.curToken.value == 'var':
                self._get_symbol()
                _var()
            if self.curToken.value == 'procedure':
                _proc()
            t_set3 = deepcopy(statement_head)
            self._test(t_set3, symbol_set, 7)
            if self.curToken.value not in declaration_head:
                break

        self.p_code[code1].a = len(self.p_code)     # 符号表回填
        self.table[tx0].adr = len(self.p_code)      # 指令表回填
        self.p_code.gen(OPCode.INT, 0, dx)  # 添加生成指令，为被调用的过程开辟dx单元的数据区
        t_set4 = deepcopy(symbol_set)
        t_set4.append(';')
        t_set4.append('end')
        self._statement(t_set4)
        self.p_code.gen(OPCode.OPR, 0, 0)   # 添加释放指令，过程出口需要释放数据段
        self.curLevel -= 1
        self.table[tx0+1:] = []
        self._test(symbol_set, [], 8)

    #  语句
    def _statement(self, symbol_set):
        if self.curToken.type == 'IDENTIFIER':
            symbol = self.table.get(name=self.curToken.value, pos=self._error_pos())
            if not isinstance(symbol, Symbol):
                self.error.direct_add(symbol)
            elif symbol.kind != 'var':
                self.error.add(pos=self._error_pos(), error_num=12)
            self._get_symbol()
            self._expect(Token(None, ':='), error_num=13)
            self._get_symbol()
            self._expression(symbol_set)
            if isinstance(symbol, Symbol):
                self.p_code.gen(OPCode.STO, self.curLevel-symbol.level, symbol.adr)

        elif self.curToken.value == 'if':
            self._get_symbol()
            t_set = deepcopy(symbol_set)
            t_set.append('then')
            self._condition(t_set)
            self._expect(Token(None, 'then'), error_num=16)
            self._get_symbol()
            code1 = len(self.p_code)
            self.p_code.gen(OPCode.JPC, 0, 0)
            t_set2 = deepcopy(symbol_set)
            t_set2.append('else')
            self._statement(t_set2)
            if self.curToken.value == 'else':
                self._get_symbol()
                code2 = len(self.p_code)
                self.p_code.gen(OPCode.JMP, 0, 0)
                self.p_code[code1].a = len(self.p_code)
                self._statement(symbol_set)
                self.p_code[code2].a = len(self.p_code)
            else:
                self.p_code[code1].a = len(self.p_code)

        elif self.curToken.value == 'while':
            adr1 = len(self.p_code)
            self._get_symbol()
            t_set = deepcopy(symbol_set)
            t_set.append('do')
            self._condition(t_set)
            self._expect(Token(None, 'do'), error_num=18)
            code1 = len(self.p_code)
            self.p_code.gen(OPCode.JPC, 0, 0)
            self._get_symbol()
            self._statement(symbol_set)
            self.p_code.gen(OPCode.JMP, 0, adr1)
            adr2 = len(self.p_code)
            self.p_code[code1].a = adr2

        elif self.curToken.value == 'call':
            self._get_symbol()
            self._expect(Token('IDENTIFIER', None), error_num=14)
            symbol = self.table.get(name=self.curToken.value, kind='proc', pos=self._error_pos())
            if not isinstance(symbol, Symbol):
                self.error.direct_add(symbol)
            else:
                if symbol.kind != 'proc':
                    self.error.add(pos=self._error_pos(), error_num=15)
                self.p_code.gen(OPCode.CAL, self.curLevel-symbol.level, symbol.adr)
            self._get_symbol()

        elif self.curToken.value == 'begin':
            self._get_symbol()
            t_set = deepcopy(symbol_set)
            t_set.append(';')
            t_set.append('end')
            self._statement(t_set)
            s_head = deepcopy(statement_head)
            s_head.append(';')
            # 判断是否语句开始从而判断两个语句间是否缺少分号
            while self.curToken.type == s_head[0] or self.curToken.value in s_head[1:]:
                if self.curToken.value == ';':
                    self._get_symbol()
                else:
                    self.error.add(pos=self._error_pos(), error_num=10)
                self._statement(t_set)
            self._expect(Token(None, 'end'), error_num=17)
            self._get_symbol()

        elif self.curToken.value == 'repeat':
            adr1 = len(self.p_code)
            self._get_symbol()
            t_set = deepcopy(symbol_set)
            t_set.append(';')
            t_set.append('until')
            self._statement(t_set)
            s_head = deepcopy(statement_head)
            s_head.append(';')
            # 判断是否语句开始从而判断两个语句间是否缺少分号
            while self.curToken.type == s_head[0] or self.curToken.value in s_head[1:]:
                if self.curToken.value == ';':
                    self._get_symbol()
                else:
                    self.error.add(pos=self._error_pos(), error_num=10)
                self._statement(t_set)
            if self.curToken.value == 'until':
                self._get_symbol()
                self._condition(symbol_set)
                self.p_code.gen(OPCode.JPC, 0, adr1)
            else:
                self.error.add(pos=self._error_pos(), error_num=25)

        elif self.curToken.value == 'read':
            self._get_symbol()
            self._expect(Token(None, '('), error_num=40)
            self._get_symbol()
            while True:
                self._expect(Token('IDENTIFIER', None), error_num=26)
                symbol = self.table.get(name=self.curToken.value, kind='var', pos=self._error_pos())
                if not isinstance(symbol, Symbol):
                    self.error.direct_add(symbol)
                else:
                    if symbol.kind != 'var':
                        self.error.add(pos=self._error_pos(), error_num=28)
                    else:
                        self.p_code.gen(OPCode.RED, self.curLevel - symbol.level, symbol.adr)
                self._get_symbol()
                if self.curToken.value != ',':
                    break
                else:
                    self._get_symbol()
            self._expect(Token(None, ')'), error_num=22)
            self._get_symbol()

        elif self.curToken.value == 'write':
            self._get_symbol()
            if self.curToken.value == '(':
                self._get_symbol()
                while True:
                    t_set = deepcopy(symbol_set)
                    t_set.append(')')
                    t_set.append(',')
                    self._expression(t_set)
                    self.p_code.gen(OPCode.WRT, 0, 0)
                    if self.curToken.value != ',':
                        break
                    else:
                        self._get_symbol()
                self._expect(Token(None, ')'), error_num=22)
                self._get_symbol()
            else:
                self.error.add(pos=self._error_pos(), error_num=40)
        self._test(symbol_set, [], 19)

    # 条件
    def _condition(self, symbol_set):
        if self.curToken.value == 'odd':
            self._get_symbol()
            self._expression(symbol_set)
            self.p_code.gen(OPCode.OPR, 0, 6)
        else:
            t_set = deepcopy(symbol_set)
            t_set.extend(['=', '<>', '<', '>', '<=', '>='])
            self._expression(t_set)
            if self.curToken.type != 'RELATION_OPERATOR':
                self.error.add(pos=self._error_pos(), error_num=20)
            else:
                op = self.curToken.value
                self._get_symbol()
                self._expression(symbol_set)
                if op == '=':
                    self.p_code.gen(OPCode.OPR, 0, 8)
                elif op == '<>':
                    self.p_code.gen(OPCode.OPR, 0, 9)
                elif op == '<':
                    self.p_code.gen(OPCode.OPR, 0, 10)
                elif op == '>=':
                    self.p_code.gen(OPCode.OPR, 0, 11)
                elif op == '>':
                    self.p_code.gen(OPCode.OPR, 0, 12)
                elif op == '<=':
                    self.p_code.gen(OPCode.OPR, 0, 13)

    # 表达式
    def _expression(self, symbol_set):
        t_set = deepcopy(symbol_set)
        t_set.append('+')
        t_set.append('-')
        if self.curToken.type == 'PLUS_OPERATOR':
            op = self.curToken.value
            self._get_symbol()
            self._term(t_set)
            if op == '-':
                self.p_code.gen(OPCode.OPR, 0, 1)
        else:
            self._term(t_set)
        while self.curToken.type == 'PLUS_OPERATOR':
            op = self.curToken.value
            self._get_symbol()
            self._term(t_set)
            if op == '+':
                self.p_code.gen(OPCode.OPR, 0, 2)
            elif op == '-':
                self.p_code.gen(OPCode.OPR, 0, 3)
            else:
                ParserError(pos=self._error_pos(), error_num=23)

    # 项
    def _term(self, symbol_set):
        t_set = deepcopy(symbol_set)
        t_set.append('*')
        t_set.append('/')
        self._factor(t_set)
        while self.curToken.type == 'MULTIPLY_OPERATOR':
            op = self.curToken.value
            self._get_symbol()
            self._factor(t_set)
            if op == '*':
                self.p_code.gen(OPCode.OPR, 0, 4)
            elif op == '/':
                self.p_code.gen(OPCode.OPR, 0, 5)
            else:
                ParserError(pos=self._error_pos(), error_num=23)

    # 因子
    def _factor(self, symbol_set):
        self._test(factor_head, symbol_set, 24)
        while self.curToken.type in factor_head or self.curToken.value in factor_head:
            if self.curToken.type == 'IDENTIFIER':
                symbol = self.table.get(name=self.curToken.value, pos=self._error_pos())
                if not isinstance(symbol, Symbol):
                    self.error.direct_add(symbol)
                else:
                    if symbol.kind == 'const':
                        if int(symbol.val) > INT_MAX:
                            self.error.add(pos=self._error_pos(), error_num=30)
                        self.p_code.gen(OPCode.LIT, 0, symbol.val)
                    elif symbol.kind == 'var':
                        self.p_code.gen(OPCode.LOD, self.curLevel-symbol.level, symbol.adr)
                    elif symbol.kind == 'proc':
                        self.error.add(pos=self._error_pos(), error_num=21)
                self._get_symbol()
            elif self.curToken.type == 'NUMBER':
                if '.' in self.curToken.value:
                    self.error.add(pos=self._error_pos(), error_num=34)
                elif int(self.curToken.value) > INT_MAX:
                    self.error.add(pos=self._error_pos(), error_num=30)
                else:
                    self.p_code.gen(OPCode.LIT, 0, int(self.curToken.value))
                self._get_symbol()
            elif self.curToken.value == '(':
                self._get_symbol()
                t_set = deepcopy(symbol_set)
                t_set.append(')')
                self._expression(t_set)
                if self.curToken.value == ')':
                    self._get_symbol()
                else:
                    self.error.add(pos=self._error_pos(), error_num=22)
            self._test(symbol_set, ['('], 23)


def main():
    parser = Parser()
    with open('../doc/test.txt') as f:
        parser.load_program(f.read())
        parser.analyse()


if __name__ == '__main__':
    main()




