#!/usr/bin/python 
# -*- coding: UTF-8 -*-

from exceptions import *
from tools.parser import Parser, OPCode
import traceback


class Interpreter:
    def __init__(self):
        self.input = []
        self.output = []

    def interpret(self, p_codes):
        try:
            self._interpret(p_codes)
        except InterpreterError as e:
            print(e.message)

    def _interpret(self, p_codes):
        def base(l):
            t = base_pointer
            for i in range(l):
                t = stack[t]
            return t

        self.output = []
        program_counter = 0
        base_pointer = 0
        stack = [0, 0, 0]

        try:
            while True:
                code = p_codes[program_counter]
                program_counter += 1
                if code.f == OPCode.LIT:
                    stack.append(int(code.a))
                elif code.f == OPCode.OPR:
                    if code.a == 0:
                        current_base_pointer = base_pointer
                        program_counter = stack[base_pointer+2]
                        base_pointer = stack[base_pointer+1]
                        stack[current_base_pointer:] = []
                    elif code.a == 1:
                        stack.append(-stack.pop())
                    elif code.a == 2:
                        stack.append(stack.pop() + stack.pop())
                    elif code.a == 3:
                        stack.append(-stack.pop() + stack.pop())
                    elif code.a == 4:
                        stack.append(stack.pop() * stack.pop())
                    elif code.a == 5:
                        y = stack.pop()
                        x = stack.pop()
                        stack.append(x // y)
                    elif code.a == 6:
                        stack.append(stack.pop() % 2)
                    elif code.a == 8:
                        stack.append(int(stack.pop() == stack.pop()))
                    elif code.a == 9:
                        stack.append(int(stack.pop() != stack.pop()))
                    elif code.a == 10:
                        stack.append(int(stack.pop() > stack.pop()))
                    elif code.a == 11:
                        stack.append(int(stack.pop() <= stack.pop()))
                    elif code.a == 12:
                        stack.append(int(stack.pop() < stack.pop()))
                    elif code.a == 13:
                        stack.append(int(stack.pop() >= stack.pop()))
                    else:
                        raise InterpreterError(pos=program_counter-1)
                elif code.f == OPCode.LOD:
                    stack.append(int(stack[base(code.l) + code.a]))
                elif code.f == OPCode.STO:
                    stack[base(code.l) + code.a] = stack.pop()
                elif code.f == OPCode.CAL:
                    stack.append(base(code.l))
                    stack.append(base_pointer)
                    stack.append(program_counter)
                    base_pointer = len(stack) - 3
                    program_counter = code.a
                elif code.f == OPCode.INT:
                    stack.extend([0] * int(code.a))
                elif code.f == OPCode.JMP:
                    program_counter = code.a
                elif code.f == OPCode.JPC:
                    if stack.pop() == 0:
                        program_counter = code.a
                elif code.f == OPCode.RED:
                    if len(self.input) > 0:
                        stack[base(code.l) + code.a] = int(self.input[0])
                        self.input = self.input[1:]
                    elif __name__ == '__main__':
                        print("请输入： ", end='')
                        stack[base(code.l) + code.a] = int(input())
                    else:
                        raise InterpreterError(message="输入不合法", pos=program_counter-1)
                elif code.f == OPCode.WRT:
                    print("输出： ", stack[len(stack) - 1])
                    self.output.append(stack[len(stack) - 1])
                if program_counter == 0:
                    break
        except InterpreterError as e:
            raise e
        except Exception as e:
            raise InterpreterError(traceback.format_exc(), program_counter-1)

    # 字典格式输出
    def get_output(self, p_code):
        res = list()
        try:
            res.append({
                'state': 'success'
            })
            self._interpret(p_code)
            for o in self.output:
                res.append({
                    'output': o
                })
        except InterpreterError as e:
            res.clear()
            res.append({
                'state': 'fail',
                'msg': e.message
            })
        finally:
            return res


def main():
    parser = Parser()
    with open('../doc/corrected.txt') as f:
        parser.load_program(f.read())
        check, p_codes = parser.analyse()
        if p_codes:
            interpreter = Interpreter()
            interpreter.interpret(p_codes)


if __name__ == '__main__':
    main()