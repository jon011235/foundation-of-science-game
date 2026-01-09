# TODO the idea is this should bind together multiple levels to a coherent picture (while not relling on an interface, so it can be either terminal or web)
# It should provide explanations and background

# The main technical question for me right now whether it would be possible to open a python REPL with the context of the given level so that it can be explored automatically
from terminal_interface import CLI
from game_backend import Euclidean, Elevator, SimpleTime, Spherical, NonUniqueODE

# TODO for wintercamp: In German + in Grad nicht in rad
print("Welcome to this game, the idea is to give some intuition about how scientific progress, in the sense of creating models of the world around us works")
print("For this, we present a toy world to you: you can walk (in a given amount of dimensions) mark points by name and measure distance and angle (in radians) between such points")
print("Measuring distance and angles (in radians) between known points encapsulates all possible ways you have to collect new information")
print("NOTE: It is very easy to 'hack' this game, you just need to have a look into one of the level files and you will find plain python code. This of course works, but takes away all the fun")
print("To master a level, you need to understand the dynamics of the world the level sets you in. And by understanding we of course mean: build a model")
print("At the beginning of each level (or using help) you will be given a function signature that you have to implement, which should when executed simulate the world in the level. If the simulation is correct i.e. you correctly understood the system you can proceed")
print()
print("BACKGROUND: This is also where this game deviates from actual science: There you have no way to verify the model against the ground truth, so one can never be sure whether the model is actually correct. But more on this shortly")

# Euclidean Level
cli = CLI(Euclidean())
cli.start()

print("Well done! Please give us feedback on this projects github game and write some fun levels for others to play")
# Elevator Level
cli = CLI(Elevator())
cli.start()

# time level
print("What concept in 'normal' physics is represented here?")
cli = CLI(SimpleTime())
cli.start()

# Sphere
print("The ancient Greeks had a lot of nice geometry, but let's try something newer")
cli = CLI(Spherical)
cli.start()

# Non determinism Level
cli = CLI(NonUniqueODE())
cli.start()
