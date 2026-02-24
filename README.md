# foundation-of-science-game
A little programming game that helps to familiarize with the scientific method and its boundarys


# Level ideas:
- funky geometrys
    [x] Sphere
    [ ] hyperbolic
    [ ] 4d stuff
- simple model for complex world (ockham)
    [x] more dimensions
[x] random numbers appear to build coherrent picture
- obsever dependence (needs things that can be observed)
[x] inter universe independence
[ ] level with search space programatically

not clear how to implement yet:
- measurement errors?

# How to get started
Just visit the github page of [this project](jon011235.github.io/foundation-of-science-game) and start a level.
If you have problems with your browser or want to interact with the level more flexibly just clone this and directly interact with the levels class (or use out `terminal_interface.py`). No cheating though (-:!


# How to help
First and foremost: Help us find a good name!

If you have cool level ideas, we would love a pull request!

But more importantly we would be really interested in improving the explanation and theoretical footings. If you are knowledgeable in didactics and/or epistemology, we would love to hear your suggestions for improvement.

# Possible Roadmap
[x] Tutorial
[ ] put marimo in app mode (with grid for better overview and more effective hiding of the code)
[ ] more languages
[ ] better level difficulty (and preknowledge) management to make it actually accesible for people that might find this interesting
[ ] bonus feature: pagination to switch between different graphs and REPLs that are in different states
[ ] Bonus: Set cookies that enable the next levels?

## More TODOs:
- favicon
- plotting def. must be worked on, it looks as if there is no change when you move (unless you pay close attention to the axes); I think it would be best to have something like coords fixed to -10; 10, but if you leave that box, make the coords -20; 20, after -30; 30 (and back to -10; 10 if you move  back into the -10; 10 box); an LLM should be able to fix this
- Make tutorial and level controls consistent.
- there are some small changes to the code which could me made (there are a lot of "lvl1" and "lvl2" which are not needed)