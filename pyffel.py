from contract import args, self, contract, old


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
@contract
def some_func(x, y, z=3):
    pass

some_func.require(args.x > 2, 
                  args.y > 4,
                  isinstance_(args.x, int))
some_func(3, y=5)


# ## Post conditions
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
