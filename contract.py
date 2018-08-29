from inspect import signature
from types import SimpleNamespace
from functools import wraps
from proxy import Proxy
    
    
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


class ContextProxy(Proxy):
    def __init__(self, name):
        super().__init__()

        self.name = name
        
    def evaluate(self, ctx):
        return ctx[self.name]


class Old(Proxy):
    
    def evaluate(self, ctx):
        memoized_state = ctx['old']
        this_id = id(self)
        if not this_id in memoized_state:
            memoized_state[this_id] = evaluate(self.value, ctx)
        return memoized_state[this_id]
        
old = Old
isinstance_ = Proxy(isinstance)
A = args = ContextProxy('args')
S = self = args.self
