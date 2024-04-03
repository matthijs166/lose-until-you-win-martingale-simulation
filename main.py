import random
import itertools
import concurrent.futures
from dataclasses import dataclass

class Wallet:
    def __init__(self, balance):
        self.balance = balance

    def deposit(self, amount):
        self.balance += amount

    def withdraw(self, amount):
        self.balance -= amount

    def get_balance(self):
        return self.balance

    def show_balance(self):
        print(f"wallet balance: {self.balance}")

class Market:
    def __init__(self, win_odds, wallet):
        if win_odds < 0 or win_odds > 100:
            return

        self.wallet = wallet
        self.odds = win_odds

    def trade(self, amount):
        self.wallet.withdraw(amount)
        win = self.coin_flip()
        if win:
            self.wallet.deposit(amount * 2)
            return True
        else:
            return False

    def coin_flip(self):
        return random.randint(0, 100) < self.odds

@dataclass
class SimulationTick:
    trade_count: int
    trade_unit: float
    wallet_balance: float
    is_win: bool

class simulation:
    def __init__(self, market, wallet, start_unit=1, x_factor=1.5, max_trades=10000, parms={}):
        self.market: Market = market
        self.wallet: Wallet = wallet
        self.start_unit = start_unit
        self.x_factor = x_factor
        self.max_trades = max_trades
        self.parms = parms
        self.trade_count = 0
        self.trade_unit = start_unit
        self.status = "running"
        self.name = f"sim-{self.start_unit}-{self.x_factor}-{self.market.odds}"
        self.timeline: SimulationTick = []

    def tick(self):
        is_win = self.market.trade(self.trade_unit)
        if is_win:
            self.trade_unit = self.start_unit
        else:
            self.trade_unit *= self.x_factor
        self.trade_count += 1
        self.record_tick(is_win)
    
    def record_tick(self, is_win):
        new_row = SimulationTick(
            trade_count=self.trade_count,
            trade_unit=self.trade_unit,
            wallet_balance=self.wallet.get_balance(),
            is_win=is_win
        )
        self.timeline.append(new_row)

    def run(self):
        lock = False
        while lock == False:
            if self.trade_count >= self.max_trades:
                lock = True
                self.status = "finished"
            
            if self.wallet.get_balance() <= 0:
                lock = True
                self.status = "stopped"

            self.tick()      

def simulation_builder(
    start_balance=1000,
    win_odds=50,
    start_unit=1,
    grow_factor=1.5,
    max_trades=1000
):
    the_wallet = Wallet(**{
        "balance": start_balance
    })
    the_market = Market(**{
        "win_odds": win_odds,
        "wallet": the_wallet
    })
    the_simulation = simulation(**{
        "market": the_market,
        "wallet": the_wallet,
        "start_unit": start_unit,
        "x_factor": grow_factor,
        "max_trades": max_trades,
        "parms": {
            "start_balance": start_balance,
            "win_odds": win_odds,
            "start_unit": start_unit,
            "grow_factor": grow_factor,
            "max_trades": max_trades
        }
    })
    return the_simulation

def run_parallel_simulations(simulations: list[simulation], max_workers=12):
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        executor.map(lambda x: x.run(), simulations)