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


@app.cell
def _(np):
    def unit_vector(vector):
        """ Returns the unit vector of the vector.  """
        return vector / np.linalg.norm(vector)

    def angle_between(v1, v2):
        """ Returns the angle in radians between vectors 'v1' and 'v2'::

                >>> angle_between((1, 0, 0), (0, 1, 0))
                1.5707963267948966
                >>> angle_between((1, 0, 0), (1, 0, 0))
                0.0
                >>> angle_between((1, 0, 0), (-1, 0, 0))
                3.141592653589793
        """
        v1_u = unit_vector(v1)
        v2_u = unit_vector(v2)
        return np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0))

    def nparr_to_list(arr):
        return [int(i) for i in arr]
    # ==============================================================

    class Level():
        known_points = {}

        def __init__(self):
            raise NotImplemented
    
        def description(self): # prints a description of the level,
            # in particular how many dimensions and how the context of the model looks like
            raise NotImplemented

        def move(self, movement_vector):
            raise NotImplemented

        def save_point(self, name):
            raise NotImplemented
    
        def measure_angle(self, left_point, right_point): # measuring the angle between two points and the current position
            raise NotImplemented
    
        def check(self, model): # odel is a function that given the context (i.e. the position and where to move) and predicts how a state (i.e. the position) changes
            raise NotImplemented

    class Euclidean(Level):
        def __init__(self, dim: int = 3):
            self.dim = dim
            self.dim_move = dim
            self.position = np.zeros(dim)
    
        def description(self):
            return """This level takes dim (usually 3) values as a movementvector and
            expects the model to take a dim sized list position and a dim sized list movement_vector
            it should return a dim sized list with the predicted new position
        
            so model should have type model(position: List(int), movement: List(int)) -> List(int) where every list is dim long"""
    
        def move(self, movement_vector: np.ndarray):
            self.position += movement_vector
    
        def save_point(self, name: str):
            self.known_points[name] = self.position.copy()

        def measure_angle(self, left_point: str, right_point: str) -> int: # measuring the angle (in rad) between two points and the current position
            a = self.known_points[left_point] - self.position
            b = self.known_points[right_point] - self.position
            return angle_between(a, b)

        def measure_length(self, other_point) -> int:
            return self.known_points[other_point]-self.position

        def check(self, model):
            for i in range(100):
                pos = np.random.randint(-1000, 1000, self.dim)
                move = np.random.randint(-1000, 1000, self.dim)
                if nparr_to_list(pos+move) != model(nparr_to_list(pos), nparr_to_list(move)):
                    return False
            return True


    class Elevator(Euclidean):
        def __init__(self):
            super().__init__()
            self.dim_move = 2
            self.known_points["check me out"] = np.array([1,2,0])
    
        def description(self):
            return """In this level, positions are represented by 3-dimensional lists, while the movement vector by a 2-dimensional list. Given the current position and a movement vector, you need to predict the next position.
        
            `model` should have type `model(position: List(int), movement: List(int)) -> List(int)`"""

        def solution_description(self):
            return """The world seems to consist of a simple 2-dimensional plane, until you travel to `[1, 2, 0]`. Here, you get "teleported" to the parallel plane `z = 1`.

    A possible solution is:
    ```py
    def model(position, movement):
        for i in range(2):
            position[i] += movement[i]
        if position[0] == 1 and position[1] == 2:
            position[2] = 1 - position[2]
        return position
    ```

    You could think of `[1, 2, 0]` as a [wormhole](https://en.wikipedia.org/wiki/Wormhole), a hypothetical structure that connects seemingly desperate points in space. Fascinating about wormholes is that the mathematical framework of general relativity _allows for their existence_. Does this imply that they exist? Or that they could?

    It has been pointed out that maths is [unreasonably effective](https://en.wikipedia.org/wiki/The_Unreasonable_Effectiveness_of_Mathematics_in_the_Natural_Sciences) at modelling the natural word. And indeed, when we try to model simple physics experiments, we often reach mathematical descriptions that apply to a large class of phenomena. Is there underlying truth to these models? Should we expect that mathematical possibilities in our models will translate to (yet-unobserved) physical phenomena?

    Or should we always be careful not to mistake the map for the mountain? That is, (mathematical) models are useful as "maps" in as much as they predict how the world functions (i.e. show us the way through the mountains). But we should put little trust in maps of uncharted territories. Even if an elegant mathematical theory predicts some theoretical outcomes, should we only trust in it once we observe it empirically?"""
    
        def move(self, movement_vector: np.ndarray):
            self.position += np.append(movement_vector, 0)
            if np.all(self.position == self.known_points["check me out"]):
                self.position += np.array([0,0,1])
            elif list(self.position) == list(self.known_points["check me out"]+np.array([0,0,1])):
                self.position -= np.array([0,0,1])
    
        def check(self, model):
            save_position = self.position

            for i in range(100):
                pos = np.random.randint(-1000, 1000, 3)
                self.position = pos.copy()
                move = np.random.randint(-1000, 1000, 2)
                self.move(move)
                if nparr_to_list(self.position) != model(nparr_to_list(pos), nparr_to_list(move)):
                    self.position = save_position
                    return False
        
            for i in range(30):
                pos = np.random.randint(-10, 10, 3)
                self.position = pos.copy()
                move = np.random.randint(-10, 10, 2)
                self.move(move)
                if nparr_to_list(self.position) != model(nparr_to_list(pos), nparr_to_list(move)):
                    self.position = save_position
                    return False
        
            pos = [30, 20, 1]
            self.position = pos.copy()
            move = [-29, -28]
            self.move(move)
            if nparr_to_list(self.position) != model(nparr_to_list(pos), nparr_to_list(move)):
                self.position = save_position
                return False
        
            pos = [30, 20, 0]
            self.position = pos.copy()
            move = [-29, -28]
            self.move(move)
            if nparr_to_list(self.position) != model(nparr_to_list(pos), nparr_to_list(move)):
                self.position = save_position
                return False
        
            # TODO can not test position at "check me out" and move 0 as this is not testable for user
            # TODO wrong, they can stand still on that spot, but maybe hard to guess

            self.position = save_position
            return True
    return (Elevator,)


@app.cell
def _(mo):
    mo.md(r"""
    # Elevator
    _Ever heard of a wormhole?_
    """)
    return


@app.cell
def _(Elevator, mo):
    # Initialize your level and store it in state
    get_lvl, set_lvl = mo.state(Elevator())
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
