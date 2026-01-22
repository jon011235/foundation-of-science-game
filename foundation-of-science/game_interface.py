"""
A webinterface for simple levels that are 2 or 3 dimensional in movement and position
"""

import marimo

__generated_with = "0.19.2"
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
async def _(micropip):
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
    return (custom_code,)


@app.cell
def _(custom_code, mo):
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
    try:
        gb = _load_module_from_url("gb", "/foundation-of-science-game"+base_url)
    except:
        gb = _load_module_from_url("gb", base_url)

    url_params = mo.query_params()

    if url_params.get("custom") == "true":
        ns = {}
        exec(base64.b64decode(custom_code.value), ns)
        currentLevel = ns["Level"]
    else:
        exec(f"currentLevel = gb.{url_params['level']}") 
    # import game_backend as gb
    # currentLevel = gb.EverythingRandom
    return (currentLevel,)


@app.cell
def _(currentLevel, mo):
    # Initialize your level and store it in state
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
        set_history,
        set_lvl,
        set_repl_code,
        set_repl_output,
    )


@app.cell
def _(get_lvl):
    lvl = get_lvl()
    return (lvl,)


@app.cell
def _(lvl, mo):
    try:
        quote = lvl.quote()
    except:
        quote = ""
    mo.md(quote)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Simulation

    Move around the world, or save your current position. The blue dots represent saved positions, and the red one is your current position.
    """)
    return


@app.cell
def _(currentLevel, get_history, get_lvl, mo, save_name, set_history, set_lvl):
    # Define move_inputs first so it is available for clojure
    curr_lvl = get_lvl()
    move_inputs = [
        mo.ui.number(label=f"Move {axis}:")
        for axis in "XYZ"[:curr_lvl.dim_move]
    ]

    def move_btn_click(value):
        curr_lvl = get_lvl()
        move_vec = []
        for inp in move_inputs:
            if inp.value is None:
                return
            move_vec.append(inp.value)
        if len(move_vec) == curr_lvl.dim_move:
            curr_lvl.move(tuple(move_vec))
            set_lvl(curr_lvl)

    def save_btn_click(value):
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
        set_lvl(currentLevel())

    def reset_plot_click(value):
        set_history([])

    move_btn = mo.ui.button(label="Move", on_click=move_btn_click)
    save_btn = mo.ui.button(label="Save", on_click=save_btn_click)
    reset_lvl_btn = mo.ui.button(label="Reset Level", on_click=reset_lvl_click)
    reset_plot_btn = mo.ui.button(label="Reset old points", on_click=reset_plot_click)
    return move_btn, move_inputs, reset_lvl_btn, reset_plot_btn, save_btn


@app.cell
def _(mo):
    save_name = mo.ui.text(label="Name:")
    return (save_name,)


@app.cell
def _(get_lvl, mo):
    lvl0 = get_lvl()
    pos_str = ", ".join([str(x) for x in lvl0.position])
    position = mo.md(f"""Current position: `[{pos_str}]`""")
    return (position,)


@app.cell(hide_code=True)
def _(
    mo,
    move_btn,
    move_inputs,
    position,
    reset_lvl_btn,
    reset_plot_btn,
    save_btn,
    save_name,
):
    stack = mo.vstack([*move_inputs, move_btn], align="start")
    mo.hstack([
        stack,
        mo.vstack([position, save_name, save_btn], align="start"),
        mo.vstack([reset_lvl_btn, reset_plot_btn], align="start")
    ])
    return


@app.cell(hide_code=True)
def _(get_history, get_lvl, np):
    import plotly.graph_objects as go
    lvl3 = get_lvl()
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
    create_plot(lvl3, history)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Interactive Shell
    """)
    return


@app.cell
def _(get_lvl, get_repl_code, mo, set_lvl, set_repl_code, set_repl_output):
    repl_code = mo.ui.code_editor(
        value=get_repl_code(),
        label="Code",
        language="python",
        on_change=set_repl_code
    )

    def run_repl(value):
        import io
        import contextlib
        import numpy as np
        # ... existing code ...

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
def _(get_repl_output, mo, repl_code, run_btn):
    mo.vstack([
        repl_code,
        run_btn,
        mo.md(f"```\n{get_repl_output()}\n```")
    ])
    return


@app.cell
def _(mo):
    mo.md(r"""
    <details><summary>Quick reference</summary>
    To see whether you model is successfull write it into the editor below and check the result at the bottom of the page

     <ul class="acc-list">
          <li>Move: <code>lvl.move(movement_vector)</code> (tuple of size given in typesignature in the Description below)</li>
          <li>Save current position: <code>lvl.save_point("name")</code><</li>
          <li>Measure angle: <code>lvl.measure_angle("left","right")</code> (both are saved point names)</li>
          <li>Measure length: <code>lvl.measure_length("name")</code> (where "name" is a saved point)</li>
          <li>Inspect state: <code>lvl.position</code>
          <ul>
              <li><code>lvl.dim</code></li>
              <li><code>lvl.dim_move</code></li>
              <li><code>lvl.known_points</code></li>
          </ul>
          </li>
        </ul>
    </details>
    """)
    return


@app.cell
def _(get_lvl, mo):
    mo.md(f"""
    ## Description

    {get_lvl().description()}

    ## Model
    """)
    return


@app.cell
def _(mo):
    user_code = mo.ui.code_editor(
        value="def model(position, movement):\n  return ()",
        label="Write your model here:",
        language="python"
    )

    user_code
    return (user_code,)


@app.cell
def _(get_lvl, mo, user_code):
    lvl1 = get_lvl()
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
                return mo.md(f"✅ **Success**!: Your model correctly predicts the level's behavior.\n\n {lvl1.solution_description()}")
            else:
                return mo.md("❌ **Validation Failed**: The model did not return the expected values for random trials.")

        except Exception as e:
            return mo.md(f"🛑 **Syntax or Runtime Error**: `{type(e).__name__}: {str(e)}`")

    validation_result = run_user_validation(user_code.value, lvl1.check)
    validation_result
    return


if __name__ == "__main__":
    app.run()
