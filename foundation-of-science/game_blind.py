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
    return


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
    with mo.status.spinner(title="Loading game backend..."):
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
    # currentLevel = gb.GoingInBlind
    return (currentLevel,)


@app.cell
def _(currentLevel, mo):
    # Initialize your level and store it in state
    get_lvl, set_lvl = mo.state(currentLevel())
    get_history, set_history = mo.state([])
    get_repl_output, set_repl_output = mo.state("")
    get_repl_code, set_repl_code = mo.state(
        "# lvl.move((1,0,0))\nprint(lvl.position())"
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
    <a href="https://jon011235.github.io/foundation-of-science-game/">← Go back (all work will be discarded)</a>
    """)
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
    # Define move_inputs first so it is available for closure
    curr_lvl = get_lvl()
    move_inputs = [
        mo.ui.number(label=f"Move {axis}:", value=0.0, full_width=True)
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

        pts = dict()
        for past_pts in hist:
            pts = pts | past_pts
        curr_lvl = currentLevel()
        curr_lvl.known_points = curr_lvl.known_points | pts
        set_lvl(curr_lvl)

    def reset_plot_click(value):
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
    return


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
    dist_to_pnt_md,
    mo,
    move_btn,
    move_inputs,
    reset_lvl_btn,
    reset_plot_btn,
    save_btn,
    save_name,
):
    mv_stack = mo.vstack([*move_inputs, move_btn], align="start", justify="space-between")
    save_stack = mo.vstack([save_name, save_btn], align="start")
    reset_stack = mo.vstack([save_name, save_btn, dist_to_pnt_md, reset_lvl_btn, reset_plot_btn], align="start")


    mo.hstack([
        mv_stack,
        reset_stack,
    ], gap=3)
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

    class LevelWrapper():
        def position(self): return None

        def dim(self): return get_lvl().dim

        def dim_move(self): return get_lvl().dim_move

        # def known_points(self): return {k: tuple(map(float,tuple(v))) for k, v in get_lvl().known_points.items()}

        def known_points(self): return set(get_lvl().known_points.keys())

        def move(self, v): get_lvl().move(v)

        def save_point(self, n): get_lvl().save_point(n)

        def measure_length(self, n): return get_lvl().measure_length(n)

        def measure_angle(self, a, b): return get_lvl().measure_angle(a, b)

    def run_repl(value):
        import io
        import contextlib
        import numpy as np
        # ... existing code ...

        lvl = LevelWrapper()

        # Capture stdout
        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            try:
                ns = {"lvl": lvl, "np": np}
                exec(repl_code.value, ns)
                set_lvl(get_lvl())
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
     <ul class="acc-list">
          <li>Move: <code>lvl.move(movement_vector)</code> (tuple of size given in typesignature in the Description below)</li>
          <li>Save current position: <code>lvl.save_point("name")</code></li>
          <li>Measure angle: <code>lvl.measure_angle("left","right")</code> (both are saved point names)</li>
          <li>Measure length: <code>lvl.measure_length("name")</code> (where "name" is a saved point)</li>
          <li>Inspect state:
          <ul>
              <li><code>lvl.position()</code></li>
              <li><code>lvl.dim()</code></li>
              <li><code>lvl.dim_move()</code></li>
              <li><code>lvl.known_points()</code></li>
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
def _(lvl, mo, user_code):
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
                user_code = code_string
                return mo.md(f"✅ **Success**: Your model correctly predicts the level's behavior.\n\n {lvl.solution_description()}")
            else:
                return mo.md("❌ **Validation Failed**: The model did not return the expected values for random trials.")

        except Exception as e:
            return mo.md(f"🛑 **Syntax or Runtime Error**: `{type(e).__name__}: {str(e)}`")

    validation_result = run_user_validation(user_code.value, lvl.check)
    validation_result
    return


if __name__ == "__main__":
    app.run()
