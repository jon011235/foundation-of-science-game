"""
A webinterface for simple levels that are 2 or 3 dimensional in movement and position
"""

import marimo

__generated_with = "0.19.0"
app = marimo.App()


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell
def _():
    import numpy as np
    return (np,)


@app.cell
def _():
    import micropip
    return (micropip,)


@app.cell
async def _(micropip, mo):
    with mo.status.spinner(title="Installing Plotly (this may take a while)..."):
        await micropip.install("plotly")
    import plotly.express as px
    return


@app.cell
def _(mo):
    url_param = mo.query_params()
    if url_param.get("custom") == "true":
        custom_code = mo.ui.code_editor(
            value="",
            label="Paste the base64 encoded level here",
            language="python"
        )
    else:
        custom_code = None

    custom_code
    return


@app.cell
def _(mo):
    # FOR LOCAL EDITING,
    # -------> COMMENT FROM HERE
    from pyodide.http import open_url
    from importlib.util import spec_from_loader, module_from_spec
    import base64

    def _load_module_from_url(name: str, url: str):
        code = open_url(url).read()
        module_spec = spec_from_loader(name, loader=None)
        module = module_from_spec(module_spec)
        exec(code, module.__dict__)
        return module

    # Hack to make it work both locally and on github pages
    base_url = "/marimo/game_backend.py"
    with mo.status.spinner(title="Loading game backend..."):
        try:
            gb = _load_module_from_url("gb", "/foundation-of-science-game"+base_url)
        except:
            gb = _load_module_from_url("gb", base_url)
    # <------- UNTIL HERE

    # AND UNCOMMNET THE FOLLOWING LINE
    # import game_backend as gb

    currentLevel = gb.Euclidean
    return (currentLevel,)


@app.cell
def _():
    from enum import IntEnum

    class TutState(IntEnum):
        START = 1
        MOVED = 2
        SAVED_PNT = 3
        SAVED_PNT_AND_MVD = 4
        RESETTED = 5
        RUN_CODE = 6
        SOLVED = 7
    return (TutState,)


@app.cell
def _(TutState, currentLevel, mo):
    # Initialize your level and store it in state
    get_tut_state, set_tut_state = mo.state(TutState.START)

    get_lvl, set_lvl = mo.state(currentLevel())
    get_history, set_history = mo.state([])
    get_repl_output, set_repl_output = mo.state("")
    get_repl_code, set_repl_code = mo.state(
        "# lvl.move((1,0,0))\nprint(lvl.position)"
    )
    return (
        get_history,
        get_lvl,
        get_repl_code,
        get_repl_output,
        get_tut_state,
        set_history,
        set_lvl,
        set_repl_code,
        set_repl_output,
        set_tut_state,
    )


@app.cell
def _(get_lvl, get_tut_state):
    lvl = get_lvl()
    tut_state = get_tut_state()
    return lvl, tut_state


@app.cell
def _(mo):
    mo.md(f"""
    # Euclidean (Tutorial)

    _There is no royal road to geometry._ -- Euclid

    This first level will be a walk through the base mechanics of the game.

    ### A ~~short~~ philosophical introduction

    (if you just want to play, you may skip to _The mechanics of the game_)

    Over the past century, humanity has lived through a scientific revolution. It is awe-inspiring to look back and see how much we have achieved in a short 100 years. At the beginning of the 20th century, we had little idea of what the age of Earth is, no idea what plate tectonics are, and could not fathom that chickens are direct descendents of Mesozoic Era dinasours. We have landed on the Moon, developed vaccines and laid cables across ocean floors that allow for near-instantaneous communication. Most importantly, we now know <a href="https://www.reddit.com/r/todayilearned/comments/1gxcdtc/til_before_2022_it_was_unknown_how_eels_reproduced/" target="_blank">how eels reproduce</a>.


    We are brought up in a society where the capital-S instituion of Science is ingrained in everyday life. Besides the technology that surrounds us, how often do we not hear "you know, I heard scientists have discovered X". Because of Science's prevelance however, we rarely stop and ask: who are the scientists that discovered X? How did they discover X?

    As we dig deeper into science and its foundations, we quickly run into fundamental philosophical questions. What can be _known_ about the surrounding world? How can information about the world be aquired, and to what degree can it be trusted?

    In philosophy, such questions are brought together under the field of <a href="https://en.wikipedia.org/wiki/Epistemology" target="_blank"><i>epistemology</i></a>. Debates over epistemological beliefs have been going on for centuries.

    These debates have naturally spilled over into the _philosophy of science_. Take a second and ask yourself: what is science? What is its purpose? What are its methods? The more one considers these questions, the murkier the answers become. If you are able to give a concrete answer to any of the questions, try to think of a field of science where the

    This game will try to give you a feeling for how science works, at its most fundamental level. Note that the game will _not_ provide answers to the aforementioned questions. In fact, the purpose of the game is to immerse you in the uncertainty at the foundations of science. To get you to think about science in a new way, and to ask many questions: often enough, a well-posed question is worth more than the answer.

    But what does this mean in practice?
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## The mechanics of the game

    Generally, a level consists of a _world_. This a 2D (or 3D) space, where you can move around, save points, and make measurements. To help you visualise all of this, a live plot of your position (the red dot) and saved points (blue dots) is shown below.
    """)
    return


@app.cell(hide_code=True)
def _(get_history, lvl, np):
    import plotly.graph_objects as go
    history = get_history()

    def create_plot(lvl, history):
        points_dict = lvl.known_points
        pts_list = list(points_dict.values()) if points_dict else []
        names = list(points_dict.keys()) if points_dict else []
        pos = lvl.position

        fig = go.Figure()

        # Plot history
        for hist_pts_dict in history:
            h_pts_list = list(hist_pts_dict.values())
            if not h_pts_list: continue
            h_pts = np.array(h_pts_list)

            if lvl.dim == 3:
                fig.add_trace(go.Scatter3d(
                    x=h_pts[:, 0], y=h_pts[:, 1], z=h_pts[:, 2],
                    mode='markers',
                    marker=dict(size=3, color='gray', opacity=0.5),
                    hoverinfo='skip'
                ))
            elif lvl.dim == 2:
                fig.add_trace(go.Scatter(
                    x=h_pts[:, 0], y=h_pts[:, 1],
                    mode='markers',
                    marker=dict(size=6, color='gray', opacity=0.5),
                    hoverinfo='skip'
                ))

        if lvl.dim == 3:
            if pts_list:
                pts = np.array(pts_list)
                fig.add_trace(go.Scatter3d(
                    x=pts[:, 0], y=pts[:, 1], z=pts[:, 2],
                    mode='markers+text',
                    text=names,
                    marker=dict(size=4, color='blue'),
                    textposition="top center"
                ))
            fig.add_trace(go.Scatter3d(
                x=[pos[0]], y=[pos[1]], z=[pos[2]],
                mode='markers',
                marker=dict(size=5, color='red'),
            ))
            fig.update_layout(
                scene=dict(
                    xaxis=dict(range=[-10, 10], autorange=True),
                    yaxis=dict(range=[-10, 10], autorange=True),
                    zaxis=dict(range=[-10, 10], autorange=True),
                    aspectmode='manual',
                    aspectratio=dict(x=1, y=1, z=1),
                    camera=dict(eye=dict(x=1.5, y=1, z=.5))
                ),
                uirevision='constant_value',
                margin=dict(l=0, r=0, b=0, t=0),
                showlegend=False
            )
        elif lvl.dim == 2:
            if pts_list:
                pts = np.array(pts_list)
                fig.add_trace(go.Scatter(
                    x=pts[:, 0], y=pts[:, 1],
                    mode='markers+text',
                    text=names,
                    marker=dict(size=8, color='blue'),
                    textposition="top center"
                ))
            fig.add_trace(go.Scatter(
                x=[pos[0]], y=[pos[1]],
                mode='markers',
                marker=dict(size=10, color='red'),
            ))
            fig.update_layout(
                xaxis=dict(range=[-10, 10], autorange=True),
                yaxis=dict(range=[-10, 10], autorange=True),
                uirevision='constant_value',
                margin=dict(l=0, r=0, b=0, t=0),
                showlegend=False,
                yaxis_scaleanchor="x"
            )
        else:
            fig = go.Figure()
        return fig
    create_plot(lvl, history)
    return


@app.cell
def _(
    TutState,
    currentLevel,
    get_history,
    get_lvl,
    get_tut_state,
    mo,
    save_name,
    set_history,
    set_lvl,
    set_tut_state,
):
    # Define move_inputs first so it is available for clojure
    curr_lvl = get_lvl()
    move_inputs = [
        mo.ui.number(label=f"Move {axis}:", value=0.0, full_width=True)
        for axis in "XYZ"[:curr_lvl.dim_move]
    ]

    def move_btn_click(value):
        curr_lvl = get_lvl()
        curr_state = get_tut_state()
        move_vec = []
        for inp in move_inputs:
            if inp.value is None:
                return
            move_vec.append(inp.value)
        if len(move_vec) == curr_lvl.dim_move:
            curr_lvl.move(tuple(move_vec))
            set_lvl(curr_lvl)

        # only change state if actual movement is done
        l0 = sum([abs(d) for d in move_vec])
        if l0 != 0:
            if curr_state == TutState.START: set_tut_state(TutState(curr_state + 1))
            elif curr_state == TutState.SAVED_PNT: set_tut_state(TutState(curr_state + 1))

    def save_btn_click(value):
        curr_state = get_tut_state()
        set_tut_state(TutState(max(curr_state, TutState.SAVED_PNT)))

        if save_name.value:
            curr_lvl = get_lvl()
            curr_lvl.save_point(save_name.value)
            set_lvl(curr_lvl)

    def reset_lvl_click(value):
        import copy
        curr_lvl = get_lvl()
        hist = list(get_history())
        pts_copy = copy.deepcopy(curr_lvl.known_points)
        hist.append(pts_copy)
        set_history(hist)

        pts = dict()
        for past_pts in hist:
            pts = pts | past_pts
        curr_lvl = currentLevel()
        curr_lvl.known_points = pts
        set_lvl(curr_lvl)

    def reset_plot_click(value):
        curr_state = get_tut_state()
        set_tut_state(TutState(max(curr_state, TutState.RESETTED)))

        curr_lvl = get_lvl()
        curr_lvl.known_points = dict()
        set_lvl(curr_lvl)
        set_history([])

    move_btn = mo.ui.button(label="Move", on_click=move_btn_click)
    save_btn = mo.ui.button(label="Save", on_click=save_btn_click)
    reset_lvl_btn = mo.ui.button(label="Reset Level", on_click=reset_lvl_click)
    reset_plot_btn = mo.ui.button(label="Reset Points", on_click=reset_plot_click)
    return move_btn, move_inputs, reset_lvl_btn, reset_plot_btn, save_btn


@app.cell
def _(mo):
    save_name = mo.ui.text(label="Name:")
    return (save_name,)


@app.cell
def _(lvl, mo):
    pos_str = ", ".join([str(x) for x in lvl.position])
    position = mo.md(f"""Current position: `[{pos_str}]`""")
    return (position,)


@app.cell
def _(lvl, mo):
    dist_to_pnt = mo.ui.dropdown(options=lvl.known_points.keys())

    def dist_str_to_dropdown_pnt(name):
        try:
            return f"~{lvl.measure_length(name):.2f}"
        except:
            return "NaN"
    return dist_str_to_dropdown_pnt, dist_to_pnt


@app.cell
def _(dist_str_to_dropdown_pnt, dist_to_pnt, mo):
    dist_to_pnt_md = mo.md(f"Distance to {dist_to_pnt} is {dist_str_to_dropdown_pnt(dist_to_pnt.value)}")
    return (dist_to_pnt_md,)


@app.cell
def _(
    TutState,
    dist_to_pnt_md,
    mo,
    move_btn,
    move_inputs,
    position,
    reset_lvl_btn,
    reset_plot_btn,
    save_btn,
    save_name,
    tut_state,
):
    mv_stack = mo.vstack([*move_inputs, move_btn], align="start", justify="space-between")
    save_stack = mo.vstack([save_name, save_btn], align="start")
    reset_stack = mo.vstack([save_name, save_btn, dist_to_pnt_md, reset_lvl_btn, reset_plot_btn], align="start")

    output = None
    if tut_state == TutState.START:
        output = mo.vstack(
            [
                position,
                mo.hstack([mv_stack])
            ],
            align="center"
        )
    elif tut_state >= TutState.MOVED and tut_state <= TutState.SAVED_PNT:
        output = mo.vstack(
            [
                position,
                mo.hstack([
                    mv_stack,
                    save_stack
                ], gap=3)
            ],
            align="center"
        )
    elif tut_state >= TutState.SAVED_PNT_AND_MVD:
        # output = mo.hstack([
        #     stack,
        #     mo.vstack([position, save_name, save_btn], align="start"),
        #     mo.vstack([reset_lvl_btn, reset_plot_btn], align="start")
        # ])
        output = mo.vstack(
            [
                position,
                mo.hstack([
                    mv_stack,
                    reset_stack,
                ], gap=3)
            ],
            align="center"
        )


    output
    return


@app.cell
def _(TutState, mo, tut_state):
    text = None
    if tut_state == TutState.START:
        text = mo.md("Let's start with **moving around**! Above, input some (non-zero) values for the <code>X, Y, Z</code> coordinates, and click on <code>Move</code>!")
    elif tut_state == TutState.MOVED:
        text = mo.md("""Nice! Notice how the plot updates instantaneously.

        Now **save a point**: give it a name, and click on <code>Save</code>.""")
    elif tut_state == TutState.SAVED_PNT:
        text = mo.md("A label with your given name should have appeared ontop of your position. **Move slightly**, and you will see a blue dot where you used to be.")
    elif tut_state == TutState.SAVED_PNT_AND_MVD:
        text = mo.md("""Now that you have a point saved, you can **make measurements**! By selecting the point in the dropdown, you can see the distance between your current position and the saved point.

        You can also **reset** your work: resetting the level keeps your points, but resets the world state (this will come in handy in future levels). **Click on** <code>Reset Points</code> to remove your saved points!""")
    elif tut_state >= TutState.RESETTED:
        text = mo.md("""The tutorial continues below!""")

    mo.callout(
        text,
        kind="success"
    )
    return


@app.cell
def _(
    TutState,
    get_lvl,
    get_repl_code,
    get_tut_state,
    mo,
    set_lvl,
    set_repl_code,
    set_repl_output,
    set_tut_state,
):
    repl_code = mo.ui.code_editor(
        value=get_repl_code(),
        label="Code",
        language="python",
        on_change=set_repl_code
    )

    def run_repl(value):
        curr_state = get_tut_state()
        set_tut_state(TutState(max(curr_state, TutState.RUN_CODE)))

        import io
        import contextlib
        import numpy as np

        lvl = get_lvl()

        # Capture stdout
        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            try:
                ns = {"lvl": lvl, "np": np}
                exec(repl_code.value, ns)
                if "lvl" in ns:
                     set_lvl(ns["lvl"])
            except Exception as e:
                print(e)

        set_repl_output(f.getvalue())

    run_btn = mo.ui.button(label="Run", on_click=run_repl)
    return repl_code, run_btn


@app.cell
def _(TutState, get_repl_output, mo, repl_code, run_btn, tut_state):
    if tut_state >= TutState.RESETTED:
        mo.output.replace(
            mo.vstack([
                mo.md("## Interactive Shell"),
                repl_code,
                run_btn,
                mo.md(f"```\n{get_repl_output()}\n```")
            ]))
    return


@app.cell
def _(TutState, mo, tut_state):
    if tut_state >= TutState.RESETTED:
        mo.output.replace(
            mo.md(r"""
            <details><summary>Quick reference</summary>
             <ul class="acc-list">
                  <li>Move: <code>lvl.move(movement_vector)</code> (tuple of size given in typesignature in the Description below)</li>
                  <li>Save current position: <code>lvl.save_point("name")</code></li>
                  <li>Measure angle: <code>lvl.measure_angle("left","right")</code> (both are saved point names)</li>
                  <li>Measure length: <code>lvl.measure_length("name")</code> (where "name" is a saved point)</li>
                  <li>Inspect state:
                  <ul>
                      <li><code>lvl.position</code></li>
                      <li><code>lvl.dim</code></li>
                      <li><code>lvl.dim_move</code></li>
                      <li><code>lvl.known_points</code></li>
                  </ul>
                  </li>
                </ul>
            </details>
            """))
    return


@app.cell
def _(TutState, mo, tut_state):
    cell_text = None

    if tut_state == TutState.RESETTED:
        cell_text = mo.md("""
        Playing around with the visual interface is usually enough. Sometimes though, it helps to "program" some experiments. Above, you have a shell where you can write down Python code which interacts with the level.

        Write some code (maybe consult the _Quick reference_ above) and **click on** <code>Run</code>.""")
    elif tut_state == TutState.RUN_CODE:
        cell_text = mo.md("""Nice!

        Now, let's get to the fun part! Once you moved around the world and have a feeling for how it works, it's time to try to describe it! To do so, you will have to write a _model_ (which takes the form of a Python function called `model`).

        Below, you have:
        - a model description, which defines the inputs/outputs of the `model` function
        - a code editor, where you need to define the function
        - the output cell, which gives you live feedback

        Now, try to solve this level!""")
    elif tut_state > TutState.RUN_CODE:
        cell_text = mo.md("""The tutorial continues below!""")

    if tut_state >= TutState.RESETTED:
        mo.output.replace(mo.callout(
            cell_text,
            kind="success"
        ))
    return


@app.cell
def _(TutState, lvl, mo, tut_state):
    if tut_state >= TutState.RUN_CODE:
        mo.output.replace(mo.md(f"""## Description

        {lvl.description()}
        """))
    return


@app.cell
def _(mo):
    user_code = mo.ui.code_editor(
        value="def model(position, movement):\n  return ()",
        label="Write your model here:",
        language="python"
    )
    return (user_code,)


@app.cell
def _(TutState, mo, tut_state, user_code):
    if tut_state >= TutState.RUN_CODE:
        mo.output.replace(mo.md(f"## Model\n{user_code}"))
    return


@app.cell
def _(TutState, get_tut_state, lvl, mo, set_tut_state, user_code):
    def run_user_validation(code_string, check):
        namespace = {}
        # TODO Validate more of how the function has to be (tuple length etc) before passing to validation
        try:
            # 1. Execute the code string in the namespace
            exec(code_string, namespace)

            # 2. Extract the 'model' function
            if "model" not in namespace or not callable(namespace["model"]):
                return mo.md("⚠️ **Error:** You must define a function named `model`.")
            user_model = namespace["model"]

            # TODO check types better (List return causes Validation failed)

            success = check(user_model)

            if success:
                curr_state = get_tut_state()
                if curr_state < TutState.SOLVED: set_tut_state(TutState.SOLVED)
                user_code = code_string
                return mo.md(f"✅ **Success**!: Your model correctly predicts the level's behavior.\n\n {lvl.solution_description()}")
            else:
                return mo.md("❌ **Validation Failed**: The model did not return the expected values for random trials.")

        except Exception as e:
            return mo.md(f"🛑 **Syntax or Runtime Error**: `{type(e).__name__}: {str(e)}`")

    validation_result = run_user_validation(user_code.value, lvl.check)
    return (validation_result,)


@app.cell
def _(TutState, mo, tut_state, validation_result):
    if tut_state >= TutState.RUN_CODE:
        mo.output.replace(validation_result)
    return


@app.cell
def _(TutState, mo, tut_state):
    if tut_state >= TutState.SOLVED:
        mo.output.replace(mo.callout(
            mo.md("""Congratulations, you've solved the level!

            After solving any level, you will get a short description, explaining the rationale of the world, as well as the "intended" solution.

            This is also where the game starts to differ significantly from the real world: when we come up with a real model, there is no way to be _certain_ it is correct. <a href="https://plato.stanford.edu/entries/hume/#CausInfeCritPhas" target="_blank">Regardless of how much we test the model</a>, it may be that at some point in the future, an experiment will prove it incorrect!

            In any case, it's time to <a href="../../">move on to the next level!</a>"""),
            kind="success"
        ))
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
