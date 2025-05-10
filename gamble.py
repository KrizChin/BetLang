from textx import metamodel_from_file
import random

# Game Call Variants
class RouletteCall:
    def __init__(self, color=None, **kwargs):
        self.color = color

class CoinFlipCall:
    def __init__(self, side=None, **kwargs):
        self.side = side

class SlotsCall:
    def __init__(self, **kwargs):
        pass

# Main Commands
class InitialCommand:
    def __init__(self, parent=None, amount=None, **kwargs):
        self.amount = amount

class BetCommand:
    def __init__(self, parent=None, amount=None, gameCall=None, **kwargs):
        self.amount = amount
        self.gameCall = gameCall

class ForLoop:
    def __init__(self, start, end, commands=None, **kwargs):
        self.start = int(start)
        self.end = int(end)
        self.commands = commands or []

    def interpret(self, context):
        for i in range(self.start, self.end + 1):
            print(f"🔁 Loop iteration {i}")
            for cmd in self.commands:
                context.execute(cmd)

# If Statement
class IfStatement:
    def __init__(self, **kwargs):        
        self.condition = kwargs.get('condition')
        self.true_commands = kwargs.get('ifCommands', [])
        self.elif_blocks = kwargs.get('elifBlocks', [])
        self.else_block = kwargs.get('elseBlock')

    def interpret(self, context):
        if self.condition.evaluate(context):
            for cmd in self.true_commands:
                context.execute(cmd)
        else:
            for elif_block in self.elif_blocks:
                if elif_block.condition.evaluate(context):
                    for cmd in elif_block.elifCommands:
                        context.execute(cmd)
                    return  # Only execute first matching branch

            if self.else_block:
                for cmd in self.else_block.elseCommands:
                    context.execute(cmd)



class ElifBlock:
    def __init__(self, condition=None, commands=None, **kwargs):
        self.condition = condition
        self.commands = commands or []

class ElseBlock:
    def __init__(self, commands=None, **kwargs):
        self.commands = commands or []

class Condition:
    def __init__(self, left=None, op=None, right=None, **kwargs):
        self.left = left
        self.op = op
        self.right = right

    def evaluate(self, context):
        # Simple evaluation based on bankroll
        left_value = getattr(context, self.left, None)

        if left_value is None:
            print(f"⚠️  Unknown condition variable: {self.left}")
            return False
        try:
            right_value = int(self.right)
        except ValueError:
            print(f"⚠️  Invalid number: {self.right}")
            return False

        if self.op == '>':
            return left_value > right_value
        elif self.op == '<':
            return left_value < right_value
        elif self.op == '==':
            return left_value == right_value
        elif self.op == '!=':
            return left_value != right_value
        elif self.op == '>=':
            return left_value >= right_value
        elif self.op == '<=':
            return left_value <= right_value
        else:
            print(f"⚠️  Unsupported operator: {self.op}")
            return False
        
class SimulateCommand:
    def __init__(self, runs=None, commands=None, **kwargs):
        self.runs = int(runs)
        self.commands = commands or []

    def interpret(self, context):
        print(f"\n⏱️ Simulating {self.runs} times...\n")
        profit_count = 0
        loss_count = 0
        bankrupt_count = 0

        for i in range(self.runs):
            print(f"\n🔁 Simulation {i+1}/{self.runs}")
            sim_context = context.clone()  # Create a copy of the context
            for cmd in self.commands:
                sim_context.execute(cmd)

            final_bankroll = sim_context.bankroll
            print(f"Final bankroll for simulation {i+1}: {final_bankroll}")

            if final_bankroll >= context.initial_bankroll:
                profit_count += 1
            elif final_bankroll < context.initial_bankroll and final_bankroll > 0:
                loss_count += 1
            elif final_bankroll == 0:
                bankrupt_count += 1

        print(f"\n📊 Simulation Summary:")
        print(f"Profitable runs: {profit_count}/{self.runs}")
        print(f"Loss runs: {loss_count}/{self.runs}")
        print(f"Bankrupt runs: {bankrupt_count}/{self.runs}")

class Program:
    def __init__(self, commands=None, **kwargs):
        self.commands = commands
        self.initial_bankroll = 0
        self.bankroll = 0

    def interpret(self):
        print("🤑 Welcome to BetLang Casino!")
        for command in self.commands:
            self.execute(command)

    def execute(self, command):
        if isinstance(command, InitialCommand):
            self.initial_bankroll = command.amount
            self.bankroll = command.amount
            print(f"💰 Starting bankroll: {self.bankroll}")
        
        elif isinstance(command, SimulateCommand):
            command.interpret(self) 

        elif isinstance(command, BetCommand):
            amount = command.amount
            if amount > self.bankroll:
                print(f"❌ Not enough funds to bet {amount}. Current bankroll: {self.bankroll}")
                return

            # Roulette
            if isinstance(command.gameCall, RouletteCall):
                color = command.gameCall.color.strip('"').lower()
                print(f"🪙  Bet {amount} on roulette {color}")
                result = random.choice(['black'] * 18 + ['red'] * 18 + ['green'])
                emoji_map = {'black': '⚫', 'red': '🔴', 'green': '🟢'}
                emoji = emoji_map[result]
                print(f"Roulette spins... Result: {emoji} {result}")
                
                if result == color:
                    self.bankroll += amount
                    print(f"📈 You win {amount}! New bankroll: {self.bankroll}")
                else:
                    self.bankroll -= amount
                    print(f"📉 You lose {amount}. New bankroll: {self.bankroll}")
            
            # Coinflip
            elif isinstance(command.gameCall, CoinFlipCall):
                side = command.gameCall.side.strip('"').lower()
                print(f"🪙  Bet {amount} on coinflip {side}")
                result = random.choice(['heads', 'tails'])
                emoji_map = {'heads': '🙂', 'tails': '🙃'}
                emoji = emoji_map[result]
                print(f"Coin flips... Result: {emoji} {result}")

                if result == side:
                    self.bankroll += amount
                    print(f"📈 You win {amount}! New bankroll: {self.bankroll}")
                else:
                    self.bankroll -= amount
                    print(f"📉 You lose {amount}. New bankroll: {self.bankroll}")
            
            # Slots
            elif isinstance(command.gameCall, SlotsCall):
                print(f"🪙  Bet {amount} on slots")
                symbols = ['🍒', '🍋', '🔔', '💎', '7️⃣', '🍀']
                reels = [random.choice(symbols) for _ in range(3)]
                print(f"🎰 Spin result: {' | '.join(reels)}")

                if reels[0] == reels[1] == reels[2]:
                    # Jackpot: 3 matching
                    win_amount = amount * 10
                    self.bankroll += win_amount
                    print(f"🎉 JACKPOT! You win {win_amount}! New bankroll: {self.bankroll}")

                elif reels[0] == reels[1] or reels[1] == reels[2] or reels[0] == reels[2]:
                    # Partial match: 2 matching
                    win_amount = int(amount * 2)
                    self.bankroll += win_amount
                    print(f"🥈 Two of a kind! You win {win_amount}. New bankroll: {self.bankroll}")

                else:
                    # No match
                    self.bankroll -= amount
                    print(f"📉 No match. You lose {amount}. New bankroll: {self.bankroll}")


            # Error
            else:
                print("⚠️  Unknown game.")

        elif isinstance(command,ForLoop):
            command.interpret(self)

        elif isinstance(command, IfStatement):
            command.interpret(self)

        else:
            print("⚠️  Unknown command type. Skipping.")
    def clone(self):
        new_context = Program(self.commands)
        new_context.initial_bankroll = self.initial_bankroll
        new_context.bankroll = self.initial_bankroll
        return new_context

# Main Execution
def main():
    mm = metamodel_from_file('betlang.tx', classes=[Program, InitialCommand, BetCommand, 
                                                    RouletteCall, CoinFlipCall, SlotsCall, 
                                                    ForLoop, IfStatement, ElifBlock, ElseBlock, Condition, SimulateCommand])
    model = mm.model_from_file('program50.gmb') # change which program to run
    model.interpret()

if __name__ == "__main__":
    main()

#implememnt more games, if-statement, for-loop,and simulate profit 
#submit project module 1 and say that professor said I can still submit assignment