class Token:
    def __init__(self, token_type, value):
        self._type = token_type
        self.value = value
    
    def __repr__(self):
        return f'(Type: {self._type}, Value: {self.value})'


class Method:
    def __init__(self, name):
        self.name = name
    
    def execute(self, params, _globals, _locals):
        pass

class Value:
    def __init__(self, value, _type):
        self.value = value
        self._type = _type
    
    def __repr__(self):
        return f'(Type: {self._type}, Value: {self.value})'

class Variable(Value):
    def __init__(self, name, value, _type):
        super().__init__(value, _type)
        self.name = name
