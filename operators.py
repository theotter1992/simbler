from smb_types import *


def add(*_args, _locals):
    if len(_args) != 2:
        raise Exception(f'Expected number of _args 2, given: {len(_args)}')   

    if not all(arg._type in ['FLT', 'INT', 'VAR'] for arg in _args):
        raise Exception(
            f'Expected types are float, integers but got: {(arg._type for arg in _args)}'
        )   
        
    return Value(sum(arg.value for arg in _args), 'FLT')

def substr(*_args, _locals):
    if len(_args) != 2:
        raise Exception(f'Expected number of _args 2, given: {len(_args)}') 
    if not all(arg._type in ['FLT', 'INT'] for arg in _args):
        raise Exception(
            f'Expected types are float and integers but got: {(arg._type for arg in _args)}'
        ) 
    
    arg1, arg2 = _args
    return Value(arg1.value - arg2.value, 'FLT')

def mult(*_args, _locals):
    if len(_args) != 2:
        raise Exception(f'Expected number of _args 2, given: {len(_args)}') 
    if not all(arg._type in ['FLT', 'INT'] for arg in _args):
        raise Exception(
            f'Expected types are float and integers but got: {(arg._type for arg in _args)}'
        )   
    
    arg1, arg2 = _args
    return Value(arg1.value * arg2.value, 'FLT')


def div(*_args, _locals):
    if len(_args) != 2:
        raise Exception(f'Expected number of _args 2, given: {len(_args)}') 
    if not all(arg._type in ['FLT', 'INT'] for arg in _args):
        raise Exception(
            f'Expected types are float and integers but got: {(arg._type for arg in _args)}'
        )   
    
    arg1, arg2 = _args
    return Value(arg1.value / arg2.value, 'FLT')

def print_op(*_args, _locals):
    if len(_args) != 1:
        raise Exception(f'Expected number of _args 1, given: {len(_args)}') 
    print(_args[0].value)

def return_op(*_args, line_number, _locals):
    pass

def if_op(*_args, line_number, _locals):
    if len(_args) != 2:
        raise Exception(f'Expected number of _args 2, given: {len(_args)}')
    if _args[0]._type != 'BOOL' or _args[1]._type != 'INT':
        raise Exception(f'Expected types are boolean and integer but got: {(_args[0]._type, _args[1]._type)}')
    if _args[1].value <= line_number:
        raise Exception(f'Next line number ({_args[1].value}) has to be higher than current ({line_number})')
    
    if _args[0].value:
        return line_number + 1
    return _args[1].value

def goto_op(*_args, _locals):
    pass

def and_op(*_args, _locals):
    pass

def or_op(*_args, _locals):
    pass

def not_op(*_args, _locals):
    pass

def eql_op(*_args, _locals):
    if len(_args) != 2:
        raise Exception(f'Expected number of _args 2, given: {len(_args)}')
    
    return Value(_args[0].value == _args[1].value, 'BOOL')