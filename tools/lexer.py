#! env python3
# -*- coding: UTF-8 -*-

import re
from exceptions import *
from collections import namedtuple

lexicon = [
    r'(?P<BLANK>\s)',
    r'(?P<KEYWORD>const|var|procedure|if|then|else|while|do|call|begin|end|repeat|until|read|write|odd)',
    r'(?P<IDENTIFIER>[A-Za-z][A-Za-z0-9]*)',
    r'(?P<NUMBER>\d+(\.\d+)?)',
    r'(?P<DELIMITER>\(|\)|\.|,|;)',
    r'(?P<PLUS_OPERATOR>\+|-)',
    r'(?P<MULTIPLY_OPERATOR>\*|/)',
    r'(?P<ASSIGN_OPERATOR>:=)',
    r'(?P<RELATION_OPERATOR>=|<>|<=|<|>=|>)',
    r'(?P<COMMENT>/\*[\s\S]*\*/)'
]
Token = namedtuple('Token', 'type, value')


# 整个词法分析程序封装成一个LexerEngine类，正则表达式使用(?P...)进行不同类型的分组，
# 读取采用文件输入，file变量为文件内容。
class LexerEngine:
    def __init__(self):
        self.file = ''
        self.lexicon = [re.compile(x) for x in lexicon]
        self.pos = [1, 1]

    # 根据文件路径输入
    def load_file_by_path(self, file_path):
        with open(file_path) as f:
            self.file = f.read()

    # 根据文件内容输入
    def load_file_by_content(self, content):
        self.file = content

    # 进制浮点数转换为二进制浮点数
    def dec2bin(self, dec_num):
        if '.' in dec_num:
            num = dec_num.split('.')
            res = str(bin(int(num[0]))).split('0b')[1]
            num[1] = '0.' + num[1]
            temp = float(num[1])
            bins = []
            while temp:
                temp *= 2
                if temp >= 1.0:
                    bins.append('1')
                else:
                    bins.append('0')
                temp -= int(temp)
            res = res + '.' + ''.join(bins)
        else:
            res = str(bin(int(dec_num))).split('0b')[1]
        return res

    # 词法分析关键函数，它将文件内容按行处理，设置cur作内容指针，表明当前读取了几个字符，
    # pos表明当前读取的行列数。每次进行正则表达式匹配，从当前字符位置往后匹配，
    # 使用re.match，这会匹配第一个符合条件的字符串，当一轮匹配中出现多个符合条件的字符串时，
    # 选择最长的字符串，这种情况只出现在标识符字符串内容开头为关键字或者双字符运算符的时候。
    # 若一轮匹配中没有出现符合条件的字符串，说明文件中出现了不规范的单词，程序报错。
    # 当识别到换行符时，要设置pos指向下一行的第一个字符，即行数加1，列数设置为1。
    def get_token(self):
        self.pos = [1, 1]
        cur = 0
        length = len(self.file)
        while cur < length:
            token_length = 0
            for pattern in self.lexicon:
                match = re.match(pattern, self.file[cur:])
                if match and (token_length == 0 or match.end() > token_length):
                    token = Token(match.lastgroup, match.group())
                    token_length = len(token.value)
            if token_length == 0:
                raise LexerError(pos=tuple(self.pos))
            self.pos[1] += token_length
            cur += token_length
            if token.type == 'BLANK':
                if token.value == '\n':
                    self.pos[0] += 1
                    self.pos[1] = 1
                continue
            elif token.type == 'COMMENT':
                temp = token.value.split('\n')
                if len(temp) != 1:
                    self.pos[0] = self.pos[0] + len(temp) - 1
                    self.pos[1] = len(temp[-1]) + 1
                continue
            else:
                yield token

    # 返回字典格式的token，用于前端js处理显示。
    def complete_token(self):
        res = list()
        try:
            for index, token in enumerate(self.get_token()):
                if token.type == 'NUMBER':
                    res.append({
                        'state': 'normal',
                        'type': token.type,
                        'value': self.dec2bin(token.value)
                    })
                else:
                    res.append({
                        'state': 'normal',
                        'type': token.type,
                        'value': token.value
                    })
        except LexerError as e:
            res.append({
                'state': 'error',
                'message': e.message
            })
        finally:
            return res

    # token输出程序，当识别出单词类型为NUMBER时要转换为二进制数。
    def print_token(self):
        try:
            for index, token in enumerate(self.get_token()):
                if token.type == 'NUMBER':
                    print("{0:<15}{1}".format(token.type, self.dec2bin(token.value)))
                else:
                    print("{0:<15}{1}".format(token.type, token.value))
        except LexerError as e:
            print(e.message)


def main():
    lexer = LexerEngine()
    file_path = "../doc/right.pl0"
    lexer.load_file_by_path(file_path)
    lexer.print_token()


if __name__ == '__main__':
    main()
