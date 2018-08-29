import operator


class MagicMethod:
    def __init__(self, operation=None):
        self.operation = operation
    def __get__(self, instance, owner):
        return BoundMagicMethod(self.operation, instance)
    def __set_name__(self, owner, name):
        if self.operation is None:
            self.operation = getattr(operator, name)

            
class BoundMagicMethod:
    def __init__(self, operation, instance):
        self.operation = operation
        self.instance = instance
    def __call__(self, *args):    
        return OperationProxy(self.operation, self.instance, *args)
    
    
def caller(self, *args):
    return self(*args)
    
    
class Proxy:
    def __init__(self, value=None):
        self.value = value
    
    def __repr__(self):
        return f"{self.value}?" if self.value is not None else "?"
    
    def evaluate(self, ctx=None):
        return self.value
    
    __call__ = MagicMethod(caller)
    __lt__ = MagicMethod()
    __le__= MagicMethod()
    __eq__= MagicMethod()
    __ne__= MagicMethod()
    __ge__= MagicMethod()
    __gt__= MagicMethod()
    __add__ = MagicMethod()
    __and__ = MagicMethod()
    __sub__ = MagicMethod()
    __floordiv__ = MagicMethod()
    __invert__ = MagicMethod()
    __mul__ = MagicMethod()
    __matmul__ = MagicMethod()
    __lshift__ = MagicMethod()
    __matmul__ = MagicMethod()
    __neg__ = MagicMethod()
    __or__ = MagicMethod()
    __pos__ = MagicMethod()
    __pow__ = MagicMethod()
    __sub__ = MagicMethod()
    __rshift__ = MagicMethod()
    __truediv__ = MagicMethod()
    __xor__ = MagicMethod()
    __getitem__ = MagicMethod()
    __delitem__ = MagicMethod()
    __setitem__ = MagicMethod()
    __getattr__ = MagicMethod(getattr)
    
    
def evaluate(arg, ctx):
    try:
        evaluate = arg.evaluate
    except AttributeError:
        return arg
    return evaluate(ctx)
        
        
class OperationProxy(Proxy):
    def __init__(self, operation, *args):
        self.operation = operation
        self.args = args
        
    def evaluate(self, ctx):
        return self.operation(*(evaluate(a, ctx) for a in self.args))
    
    def __repr__(self):
        return f"{self.operation}{self.args}"


