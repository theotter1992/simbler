import re
import pdb
from collections import defaultdict

from operators import *
from smb_types import *

basic_result_op_map = {
    'add': add, 
    'substr': substr, 
    'mult': mult,
    'div': div,
    'and': and_op,
    'or': or_op,
    'not': not_op,
    'eql': eql_op
}

basic_no_result_op_map = {
    'print': print_op,
}

control_flow_ops_map = {
    'return': return_op,
    'if': if_op
}

basic_op_map = {**basic_result_op_map, **basic_no_result_op_map}

def run(source):
    _globals = {}
    tokensier = Tokenizer()
    tokens = tokensier.tokenise(source)
    _globals.update(tokens)
    execute_context(_globals['main_tokens'], _globals, {})
    

def execute_context(context_token, _globals, _locals):
    line_nb_to_ind = {line_nb: i for i, line_nb in enumerate(context_token.keys())}
    line_numbers = sorted(context_token.keys())
    i = 0
    while i < len(context_token):
        tokens = context_token[line_numbers[i]]
        if is_simple_assignment(tokens):
            var = Variable(tokens[0].value, tokens[2].value, tokens[2]._type)
            _locals[var.name] = var
        elif is_result_operator(tokens):
            op_name = tokens[2].value
            
            param_tokens = tokens[3:]
            params = [_locals[token.value] for token in param_tokens]
            value = basic_op_map[op_name](*params, _locals=_locals) 
            var_name = tokens[0].value
            var = Variable(var_name, value.value, value._type)
            _locals[var.name] = var
        elif is_result_method(tokens):
            op_name = tokens[2].value
            param_tokens = tokens[3:]
            params = [_locals[token.value] for token in param_tokens]
            method_sign = _globals['method_tokens'][op_name]['signature']
            method_tokens = _globals['method_tokens'][op_name]['tokens']
           
            value = execute_context(
                method_tokens, _globals, {method_var: param for param, method_var in zip(params, method_sign)}
            )
            var_name = tokens[0].value
            var = Variable(var_name, value.value, value._type)
            _locals[var.name] = var
        elif is_no_result_operator(tokens):
            op_name = tokens[0].value
            param_tokens = tokens[1:]
            params = [_locals[token.value] for token in param_tokens]
            basic_op_map[op_name](*params, _locals=_locals)
        elif is_control_flow_op(tokens):
            op_name = tokens[0].value
            param_tokens = tokens[1:]
            params = [_locals[token.value] for token in param_tokens]
            next_line = control_flow_ops_map[op_name](
                *params, line_number=line_numbers[i],_locals=_locals
            )
            if op_name == 'return':
                return params[0]
            else:
                i = line_nb_to_ind[next_line]
                continue
        i += 1

def is_simple_assignment(tokens):
    if len(tokens) != 3:
        return False
    return (tokens[0]._type == 'VAR' and tokens[1]._type == 'ASSIGN' and
        (tokens[2]._type != 'OP' and tokens[2]._type != 'METHOD'))

def is_result_operator(tokens):
    if len(tokens) < 3:
        return False
    return (tokens[0]._type == 'VAR' and tokens[1]._type == 'ASSIGN' and tokens[2]._type == 'OP')

def is_no_result_operator(tokens):
    return tokens[0]._type == 'OP'

def is_result_method(tokens):
    if len(tokens) < 3:
        return False
    return (tokens[0]._type == 'VAR' and tokens[1]._type == 'ASSIGN' and tokens[2]._type == 'METHOD')

def is_no_result_method(tokens):
    return tokens[0]._type == 'METHOD'

def is_control_flow_op(tokens):
    return tokens[0]._type == 'CTFL'

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
        self.basic_result_ops = list(basic_result_op_map.keys())
        self.basic_no_result_ops = list(basic_no_result_op_map.keys())
        self.control_flow_ops = list(control_flow_ops_map.keys())
        self.state = None
    
    def tokenise(self, source):
        # i starts with 0, but line numbers start at 1
        lines = [(i+1, line) for i, line in enumerate(source.split("\n")) if line]
        all_tokens = {'main_tokens': defaultdict(list), 'method_tokens': defaultdict(dict)}

        tokeniser = Tokenizer()
        is_method_def = False
        is_main = False 
        for line_number, line in lines:
            tokens = tokeniser.get_tokens(line)
            error = self.error_handling(tokens, line_number, line)
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

    def error_handling(self, tokens, line_number, line):
        if tokens is None:  
            raise Exception(f'line number: {line_number} | Could not tokenise line \"{line}\"')  

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
            if op_name in self.basic_no_result_ops:
                op_type = 'OP'
            elif op_name in self.control_flow_ops:
                op_type = 'CTFL'
            else:
                op_type = 'METHOD'
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
        return 'NO_MATCH', None

    def _get_op_name_and_params(self, op_with_params):
        op_with_params = op_with_params.replace('(', ' ')
        op_with_params = op_with_params.replace(')', '')
        op_name, params = op_with_params.split(' ')
        return op_name, params


if __name__ == '__main__':
    with open('test.smb', 'r') as file:
        source = file.read()
        run(source)