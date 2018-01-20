import re
import pdb
from collections import defaultdict

def run(source):
    _globals = {}
    _locals = {}
    stack = [{0: _locals}]
    tokensier = Tokenizer()
    tokens = tokensier.tokenise(source)
    pdb.set_trace()
    _globals.update(tokens)
    
    current_tokens = _globals['main_tokens']
    line_nb_to_ind = {line_nb: i for i, line_nb in enumerate(current_tokens.keys())}
    i = 0
    while i < len(current_tokens):
        tokens = current_tokens[i]
        i += 1

class Tokenizer:
    def __init__(self):
        self.var_reg = r'[_a-zA-Z][_a-zA-Z0-9]*'
        self.method_reg = self.var_reg
        self.boolean_reg = r'true|false'
        self.integer_reg = r'\d+'
        self.string_reg = r'\".*\"'
        self.float_reg = r'\d+\.\d+'
        self.basic_types_reg = rf'({self.boolean_reg}|{self.integer_reg}|{self.string_reg}|{self.float_reg})'
        self.params_reg = rf'({self.var_reg},)*({self.var_reg})'
        self.method_def_reg = rf'def {self.method_reg}\({self.params_reg}\)'
        self.assign_reg = rf'^{self.var_reg}=({self.var_reg}|{self.basic_types_reg})$'
        self.result_op_reg = rf'^{self.var_reg}={self.method_reg}\({self.params_reg}\)$'
        self.no_result_op_reg =  rf'^{self.method_reg}\({self.params_reg}\)$'
        self.main_start_reg = r'^main_start:$'
        self.basic_result_ops = ['add', 'substr', 'mult', 'div']
        self.basic_no_result_ops = ['return', 'print']
        self.state = None
    
    def tokenise(self, source):
        lines = [(i, line) for i, line in enumerate(source.split("\n")) if line]
        all_tokens = {'main_tokens': defaultdict(list), 'method_tokens': defaultdict(dict)}

        tokeniser = Tokenizer()
        is_method_def = False
        is_main = False 
        for line_number, line in lines:
            tokens = tokeniser.get_tokens(line)
            error = self.error_handling(tokens)
            if error:
                return error

            if self._main_start(tokens):
                self.state = 'in_main'

            elif self._method_def_start(tokens):
                self.state = 'in_method'
                method_name = tokens[1].value
                method_params = [token.value for token in tokens[2:]]
                all_tokens['method_tokens'][method_name]['signature'] = method_params
            elif self._in_main():
                all_tokens['main_tokens'][line_number] = tokens
            elif self._in_method():
                if 'tokens' not in all_tokens['method_tokens'][method_name]:
                    all_tokens['method_tokens'][method_name]['tokens'] = {}
                all_tokens['method_tokens'][method_name]['tokens'][line_number] = tokens
            
        return all_tokens

    def error_handling(self, tokens):
        if tokens is None:    
            return f'line number: {line_number} | Could not tokenise line \"{line}\"'


    def _method_def_start(self, tokens):
        return tokens[0]._type == 'METHOD_DEF'

    def _main_start(self, tokens):
        return tokens[0]._type == 'MAIN_START'

    def _in_method(self):
        return self.state == 'in_method'

    def _in_main(self):
        return self.state == 'in_main'


    def get_tokens(self, line):
        line = line.strip()
        if re.match(self.assign_reg, line):
            var_name, value = line.split('=')
            return [Token('VAR', var_name), Token('ASSIGN', '='), Token(*self._get_value_type(value))]
        elif re.match(self.result_op_reg, line):
            var_name, op_and_params = line.split('=')
            op_name, params = self._get_op_name_and_params(op_and_params)
            op_type = 'OP' if op_name in self.basic_result_ops else 'METHOD'
            params = params.split(',')
            return (
                [Token('VAR', var_name), Token('ASSIGN', '='), Token(op_type, op_name)] + 
                [Token(*self._get_value_type(param)) for param in params]
            )
        elif re.match(self.no_result_op_reg, line):
            op_and_params = line
            op_name, params = self._get_op_name_and_params(op_and_params)
            op_type = 'OP' if op_name in self.basic_no_result_ops else 'METHOD'
            params = params.split(',')
            return [Token(op_type, op_name)] + [Token(*self._get_value_type(param)) for param in params]
            
        elif re.match(self.method_def_reg, line):
            mtd_kw, method = line.split(' ')
            method_name, params = self._get_op_name_and_params(method[:-1])
            return (
                [Token('METHOD_DEF', mtd_kw), Token('METHOD', method_name)] + 
                [Token(*self._get_value_type(param)) for param in params]
            )
        elif re.match(self.main_start_reg, line):
            return [Token('MAIN_START', line)]
        return None

    def _get_value_type(self, value):
        if re.match(f'{self.boolean_reg}$', value):
            return 'BOOL', bool(value)
        elif re.match(f'{self.integer_reg}$', value):
            return 'INT', int(value)
        elif re.match(f'{self.string_reg}$', value) and value.count('\"') == 2:
            return 'STR', str(value)
        elif re.match(f'{self.float_reg}$', value):
            return 'FLT', float(value)
        elif re.match(f'{self.var_reg}$', value):
            return 'VAR', value
        return 'NO_MATCH'

    def _get_op_name_and_params(self, op_with_params):
        op_with_params = op_with_params.replace('(', ' ')
        op_with_params = op_with_params.replace(')', '')
        op_name, params = op_with_params.split(' ')
        return op_name, params

class Token:
    def __init__(self, token_type, value):
        self._type = token_type
        self.value = value
    
    def __repr__(self):
        return f'Type: {self._type}, Value: {self.value}'

def add(*args, _locals):
    if len(args) != 2:
        return 

    if not all(arg._type in ['FLT', 'INT', 'VAR'] for arg in args):
        return 
        
    return sum(arg.value for arg in args)

def subtr(*args, _locals):
    if len(args) != 2:
        return 
    if not all(arg._type in ['FLT', 'INT'] for arg in args):
        return 
    
    arg1, arg2 = args
    return arg1 - arg2

def mult():
    pass 

def div():
    pass

def print():
    pass

class Method:
    def __init__(self, name):
        self.super()
        self.name = name
    
    def execute(self, params, _globals, _locals):
        pass

class Value:
    def __init__(self, value):
        self.value = value
        self._type = None

class Variable(Value):
    def __init__(self, name, value):
        self.super(value)
        self.name = name

if __name__ == '__main__':
    with open('test.smb', 'r') as file:
        source = file.read()
        run(source)