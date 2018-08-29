
# coding: utf-8

# In[226]:


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


# In[248]:


from inspect import signature
from types import SimpleNamespace
from functools import wraps


class ContextProxy(Proxy):
    def __init__(self, name):
        super().__init__()

        self.name = name
        
    def evaluate(self, ctx):
        return ctx[self.name]
    
    
def contract(func):
    all_pre_conditions = []
    all_post_conditions = []
    sig = signature(func)
        
    @wraps(func)
    def wrapper(*args, **kwargs):
        bound_args = sig.bind(*args, **kwargs)
        bound_args.apply_defaults()
        ctx = {'args': SimpleNamespace(**bound_args.arguments),
               'old': {}}
        
        for condition in all_pre_conditions:
            assert condition.evaluate(ctx), f"Failed to assert pre condition: {condition}"
        
        for condition in all_post_conditions:
            condition.evaluate(ctx)
        
        result = func(*args, **kwargs)
        
        for condition in all_post_conditions:
            assert condition.evaluate(ctx), f"Failed to assert post condition: {condition}"
            
        return result        
    
    def require(*pre_conditions):
        all_pre_conditions.extend(pre_conditions)
        return wrapper
    
    def ensure(*post_conditions):
        all_post_conditions.extend(post_conditions)
        return wrapper
    
    wrapper.require = require
    wrapper.ensure = ensure
    return wrapper

isinstance_ = Proxy(isinstance)
A = args = ContextProxy('args')
S = self = args.self


# ## (1.) Separate contract proxy

# In[249]:


def some_func(x, y, z=3):
    pass

c = contract(some_func)
c.require(
    isinstance_(args.x, (int, float)),
    isinstance_(args.y, (int, float)),
    (args.x**2 + args.y**2) < 25
)
c(2, 4.)


# ## (2.) Contract decorator

# In[250]:


@contract
def some_func(x, y, z=3):
    pass

some_func.require(args.x > 2, 
                  args.y > 4,
                  isinstance_(args.x, int))
some_func(3, y=5)


# ## Post conditions

# In[253]:


class Old(Proxy):
    
    def evaluate(self, ctx):
        memoized_state = ctx['old']
        this_id = id(self)
        if not this_id in memoized_state:
            memoized_state[this_id] = evaluate(self.value, ctx)
        return memoized_state[this_id]
old = Old


# In[272]:


class Stateful:
    counter = 0
    
    @contract
    def increment(self, delta):
        self.counter += delta
    increment.require(args.delta > 0)
    increment.ensure(self.counter==(old(self.counter)+1))

c = Stateful()
c.increment(1)
print("Success 1")
c.increment(-1)
print("Success -1")


# In[271]:


class Account:
    
    def __init__(self, owner):
        self.owner = owner
        self.minimum_balance = 1000
        self.balance = 0
    
    def add(self, sum: int):
        self.balance += sum
    
    @contract
    def withdraw(self, sum: int):
        self.add(-sum)
    withdraw.ensure(self.balance==old(self.balance)-args.sum)    .require(0 <= args.sum <= self.balance - self.minimum_balance)
    
    @contract
    def deposit(self, sum: int):
        self.add(sum)
    deposit.ensure(self.balance==old(self.balance)+args.sum)
    
    def may_widthdraw(self, sum: int) -> bool:
        return self.balance >= self.minimum_balance + sum

acc = Account("Angus")
acc.deposit(1200)
acc.withdraw(200)
print(acc.balance)

