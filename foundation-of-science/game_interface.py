import marimo

__generated_with = "0.19.0"
app = marimo.App()


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell
def _():
    import pandas
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

# TODO: only allow existing levels (generate this?)

@app.cell
def _(mo):
    from pyodide.http import open_url
    from importlib.util import spec_from_loader, module_from_spec

    def _load_module_from_url(name: str, url: str):
        code = open_url(url).read()
        module_spec = spec_from_loader(name, loader=None)
        module = module_from_spec(module_spec)
        exec(code, module.__dict__)
        return module

    gb = _load_module_from_url("gb", "/marimo/game_backend.py")

    url_params = mo.query_params()

    # TODO I know this is incredibly insecure. I should add validation later when I have a list of levels
    exec(f"currentLevel = gb.{url_params["level"]}") 

    return (currentLevel,)


@app.cell
def _(mo):
    # TODO get this from the level itself
    mo.md(r"""
    # Elevator
    _Ever heard of a wormhole?_
    """)
    return


@app.cell
def _(currentLevel, mo):
    # Initialize your level and store it in state
    get_lvl, set_lvl = mo.state(currentLevel())
    return get_lvl, set_lvl


@app.cell
def _(get_lvl):
    lvl = get_lvl()
    return (lvl,)


@app.cell
def _(lvl, mo):
    mo.md(f"""
    ## Description

    {lvl.description()}
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
def _(get_lvl, mo, np, save_name, set_lvl):
    def move_btn_click(value):
        if x_move.value is not None and y_move.value is not None:
            curr_lvl = get_lvl()
            curr_lvl.move(np.array([x_move.value, y_move.value]))
            set_lvl(curr_lvl)

    def save_btn_click(value):
        if save_name.value:
            curr_lvl = get_lvl()
            curr_lvl.save_point(save_name.value)
            set_lvl(curr_lvl)

    # TODO add other interaction options + maybe sliders?
    x_move = mo.ui.number(label="Move X:")
    y_move = mo.ui.number(label="Move Y:")
    move_btn = mo.ui.button(label="Move", on_click=move_btn_click)
    save_btn = mo.ui.button(label="Save", on_click=save_btn_click)
    return move_btn, save_btn, x_move, y_move


@app.cell
def _(lvl, mo):
    position = mo.md(f"""Current position: `{lvl.position}`""")
    save_name = mo.ui.text(label="Name:")
    return position, save_name


@app.cell(hide_code=True)
def _(mo, move_btn, position, save_btn, save_name, x_move, y_move):
    mo.hstack([
        mo.vstack([x_move, y_move, move_btn], align="start"),
        mo.vstack([position, save_name, save_btn], align="start"),
    ])
    return


@app.cell(hide_code=True)
def _(lvl, np):
    import plotly.graph_objects as go

    # TODO for 2D level other plot possibility
    def create_3d_plot(lvl):
        points_dict = lvl.known_points

        fig = go.Figure()

        # 1. Add the points
        if points_dict:
            # Extracting coordinates for all points
            pts_list = list(points_dict.values())
            pts = np.array(pts_list)
            names = list(points_dict.keys())

            fig.add_trace(go.Scatter3d(
                x=pts[:, 0], y=pts[:, 1], z=pts[:, 2],
                mode='markers+text',
                text=names,
                marker=dict(size=4, color='blue'),
                textposition="top center"
            ))

            fig.add_trace(go.Scatter3d(
                x=[lvl.position[0]], y=[lvl.position[1]], z=[lvl.position[2]],
                mode='markers',
                marker=dict(size=5, color='red'),
            ))

        # 2. Fix the Axes and Orientation
        fig.update_layout(
            scene=dict(
                # Force axis limits
                xaxis=dict(range=[-10, 10], autorange=False),
                yaxis=dict(range=[-10, 10], autorange=False),
                zaxis=dict(range=[0, 1], autorange=False),
                # Set fixed orientation (camera)
                aspectmode='manual',
                aspectratio=dict(x=1, y=1, z=0.2), # z is 1/5th the visual height of x/y

                camera=dict(eye=dict(x=1.5, y=1, z=.5))
            ),
            # CRITICAL: This keeps the camera from resetting on update
            uirevision='constant_value', 
            margin=dict(l=0, r=0, b=0, t=0),
            showlegend=False
        )

        return fig

    create_3d_plot(lvl)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Model
    """)
    return


@app.cell
def _(mo):
    # TODO: Be clearer what the form of the function has to be (including list size)
    user_code = mo.ui.code_editor(
        value="def model(position, movement):\n  return []",
        label="Write your model here:",
        language="python"
    )

    user_code
    return (user_code,)


@app.cell
def _(lvl, mo, user_code):
    def run_user_validation(code_string, check):
        namespace = {}
        # TODO Validate more of how the function has to be (list length etc) before passing to validation
        try:
            # 1. Execute the code string in the namespace
            exec(code_string, namespace)

            # 2. Extract the 'model' function
            if "model" not in namespace or not callable(namespace["model"]):
                return mo.md("⚠️ **Error:** You must define a function named `model`.")

            user_model = namespace["model"]

            success = check(user_model)

            if success:
                return mo.md(f"✅ **Success**!: Your model correctly predicts the level's behavior.\n\n {lvl.solution_description()}")
            else:
                return mo.md("❌ **Validation Failed**: The model did not return the expected values for random trials.")

        except Exception as e:
            return mo.md(f"🛑 **Syntax or Runtime Error**: `{type(e).__name__}: {str(e)}`")

    validation_result = run_user_validation(user_code.value, lvl.check)
    validation_result
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
