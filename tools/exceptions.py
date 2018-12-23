#!/usr/bin/python 
# -*- coding: UTF-8 -*-


class CompilerError(Exception):
    def __init__(self, message='Error', pos=(1, 1)):
        self.message = 'Error({0}, {1}): {2}'.format(pos[0], pos[1], message)


class LexerError(CompilerError):
    def __init__(self, message='Lexer error', pos=(1, 1)):
        self.message = 'Error({0}, {1}): {2}'.format(pos[0], pos[1], message)


class NotOPGError(CompilerError):
    def __init__(self, message='Not OPG'):
        self.message = '{0}'.format(message)


class OPGRunError(CompilerError):
    def __init__(self, message='OPG runtime error', pos=1):
        self.message = '{0} in character {1}'.format(message, pos)


class ParserError(CompilerError):
    def __init__(self, message='Parser error', pos=(1, 1), error_num=0):
        self.error = {
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
        if error_num != 0:
            message = self.error[error_num]
            self.message = 'Error({0}, {1}): {2}'.format(pos[0], pos[1], message)


class InterpreterError(CompilerError):
    def __init__(self, message='Interpreter error', pos=1):
        self.message = 'Error({0}): {1}'.format(pos, message)


