# Some thoughts and Ideas for the future
## Marimo features

[ ] editor to submit either code or equations. When clicking check button sends this to our python code
[ ] interactive plot together with a REPL to move in the level
    [ ] ability to reset level. Graph stays but now plots in different color
    [ ] ability to reset plot
    [ ] bonus feature: pagination to switch between different graphs and REPLs that are in different states
    [ ] bonus feature: little editor to execute automated routine with the level
[ ] formatted Introduction to the Level including specification of what to submit
[ ] Introduction what requesites are needed to play this game and where to find docu i.e. for numpy
[ ] After solving level information on what exactly was going on and link to external sourceWrite me a proof of concept, that is easy to understand and extend which does the following:

What I want to do is to run python in WASM and use z3. Just write a simple demo

One way to do this is to use the z3-solver npm package and piodide and let the python interact with the js bindings. If you have a more direct/more elegant approach please use that

Take care to have an easy to use development setup as well as a ready to use CI pipeline compatible with github pages
[ ] Last: Level overview, unlocking of levels (cookies?) and fluff








# Old (from before the meeting with Andrei)
## Audience?
- Should be playable on its own and possibly self explanatory
- Base levels should basically be open to anyone with some programming experience -> indication for rising requirements (i.e. geometry series)
- Nontheless should be usable for the wintercamp or similar stuff

## Interface
I think the interface should have 4 independent sections:

### The graph and interaction
It would be interesting if this component could be openend multiple times and there would be some pagination and/or the possible to break it into a new window to switch between different states of the same level to experiment

It should have the ability to reset the graph and the level independently. First of all there is a big graph and below the possibility to enter moves, like with our current terminal interface. In contrary to the current system the plot should be non blocking

### Writing the model
This should be a simple text editor maybe with syntax highlighting etc
Furthermore it should give helpful feedback when the function does not fullfill our formal requirements or does not compile

Maybe we could integrate the vs code editor like okaml does

### menu
Something to enable jumps between levels etc, the possibility to get hints...


## Infrastructure
I think this python terminal environment does not scale well. Both from the interface (see above) as well as the securitys it gives (typing system etc)

### Rust + WEBASM + js
Would allow us to write everything in a typesafe language that also makes the coordinate stuff nicer, the js bindings would still allow the integration of js levels AFAIK (but I don't know in detail) allowing for instance students to contribute something. The interface could then be in js

### Godot
Godot is a game engine which could improve the interaction if we actually develop this as a game, we could still do a lot of programming and let the people enter text but we would be quite bound to how the engine wants us to handle things. It would also still be possible to put this on the web

## Narration/Explanation?
TODO better way to handle this than just walls of text

## Level
Here we should commit on a list of things that level can and can't do so that we then can actually build the interface

### supported Level actions
- observe
- move (in different dimensions). What about the unit? floats bring there own problems
- description of the level (should have clearer and more consistent structure, with formatting (maybe render markdown?))
- hints: If you are stuck you should be able (maybe with some difficulty) to get the case where your model is failing
- checking (minimum standards for this)
    After checking and passing our automated tests, the user should get a simple checklist so they can make sure they did not actually cheat the level (maybe with an easy option to give feedback?)

### level workings
Should they use floats internally? Can we unify levels more?



