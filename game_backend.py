import numpy as np
import random
import math

# from https://stackoverflow.com/questions/2827393/angles-between-two-n-dimensional-vectors-in-python
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

    def restart(self):
        raise Exception("This level cannot be restarted")
    
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
        return """This level takes 2 dimensions as a movementvector and
        expects the model to take a 3 dimensional position and a 2 dimensional movement_vector
        it should return a 3 dimensional list with the predicted new position
        
        so model should have type model(position: List(int), movement: List(int)) -> List(int)"""
    
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
      

class SimpleTime(Euclidean):
    def __init__(self):
        super().__init__()
        self.dim_move = 2
    
    def description(self):
        return """This level takes 2 dimensions as a movementvector and
        expects the model to take a 3 dimensional position and a 2 dimensional movement_vector
        it should return a 3 dimensional list with the predicted new position
        
        so model should have type model(position: List(int), movement: List(int)) -> List(int)"""
    
    def move(self, movement_vector: np.ndarray):
        self.position += np.append(movement_vector, round(np.sqrt(movement_vector[0]**2+movement_vector[1]**2)))
    
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
        self.position = save_position
        return True




# As you can see: AI generated

class Spherical(Level):
    """
    A level where the player moves on a closed surface.  The implementation
    works with 3‑dimensional spherical coordinates (θ, φ, r) internally, but the
    description does **not** reveal the geometry.
    """
    position = [0.0,0.0]

    # ------------------------------------------------------------------ #
    # Construction – fixed to a 3‑D sphere (dim = 3)
    # ------------------------------------------------------------------ #
    def __init__(self, radius: float = 1.0):
        if radius <= 0:
            raise ValueError("radius must be > 0")
        self.r = float(radius)

        # start at (θ=0, φ=π/2) → point on the equator, x = r
        self.position[0] = 0.0                 # azimuth  ∈ [0, 2π)
        self.position[1] = np.pi / 2.0         # polar    ∈ [0, π]

        self.known_points = {}

    # ------------------------------------------------------------------ #
    # Helpers – conversion between spherical and Cartesian
    # ------------------------------------------------------------------ #
    def _cartesian(self, theta: float, phi: float) -> np.ndarray:
        """Cartesian coordinates of the current radius‑r point."""
        return self.r * np.array([
            np.sin(phi) * np.cos(theta),
            np.sin(phi) * np.sin(theta),
            np.cos(phi)
        ])

    def _normalize_angles(self):
        """Wrap θ to [0,2π) and keep φ inside [0,π] (reflect at the poles)."""
        self.position[0] = self.position[0] % (2 * np.pi)

        # reflect φ when it leaves the [0,π] interval
        while self.position[1] < 0 or self.position[1] > np.pi:
            if self.position[1] < 0:
                self.position[1] = -self.position[1]
                self.position[0] += np.pi          # crossing the south pole flips azimuth
            elif self.position[1] > np.pi:
                self.position[1] = 2 * np.pi - self.position[1]
                self.position[0] += np.pi          # crossing the north pole flips azimuth
        self._normalize_angles() if (self.position[1] < 0 or self.position[1] > np.pi) else None

    # ------------------------------------------------------------------ #
    # Public API required by the framework
    # ------------------------------------------------------------------ #
    def description(self):
        return """This level takes a 3‑dimensional position and a 2‑dimensional movement
vector, updates the position, and lets you save/measure points."""

    def move(self, movement_coords: np.ndarray):
        """
        `movement_coords` is a length‑2 array:  [Δθ, Δφ]  (radians).
        The method adds the deltas to the current angles and normalises them,
        guaranteeing that the player stays on the same surface.
        """
        if movement_coords.shape != (2,):
            raise ValueError("movement vector must have shape (2,) for a 3‑D sphere")

        dtheta, dphi = movement_coords
        self.position[0] += dtheta
        self.position[1]   += dphi
        self._normalize_angles()

    def save_point(self, name: str):
        """Remember the current spherical coordinates under `name`."""
        self.known_points[name] = (self.position[0], self.position[1])

    def measure_angle(self, left_point: str, right_point: str) -> float:
        """
        Returns the angle (in radians) between the two saved points as seen from
        the current position – i.e. the spherical angle at the current vertex of
        the triangle formed by the three points.
        """
        # convert everything to Cartesian vectors that start at the centre
        cur   = self._cartesian(self.position[0], self.position[1])
        left  = self._cartesian(*self.known_points[left_point])
        right = self._cartesian(*self.known_points[right_point])

        # vectors from the current point to the two saved points
        a = left - cur
        b = right - cur

        # angle between the two tangent vectors
        dot = np.dot(a, b)
        norm_a, norm_b = np.linalg.norm(a), np.linalg.norm(b)
        if norm_a == 0 or norm_b == 0:
            raise ValueError("saved point coincides with current position")
        cos_angle = np.clip(dot / (norm_a * norm_b), -1.0, 1.0)
        return np.arccos(cos_angle)

    def measure_length(self, other_point: str) -> float:
        """
        Returns the great‑circle distance between the current position and a
        saved point:  r · Δσ, where Δσ is the central angle between the two radius
        vectors.
        """
        cur  = self._cartesian(self.position[0], self.position[1])
        oth  = self._cartesian(*self.known_points[other_point])
        dot  = np.dot(cur, oth)
        cos_sigma = np.clip(dot / (self.r ** 2), -1.0, 1.0)
        sigma = np.arccos(cos_sigma)
        return self.r * sigma

    def check(self, model):
        """
        Randomly generate 100 positions (θ, φ) and movement vectors (Δθ, Δφ).
        For each trial:
          1. Build the position list   → [θ, φ, r]
          2. Build the movement list   → [Δθ, Δφ]
          3. Compute the expected new spherical coordinates
             using the same logic as `move`.
          4. Call the model and verify:
                * it returns a list of length 3,
                * the radius component equals `self.r` (within tolerance),
                * the returned angles match the expected ones (tolerance 1e‑5).
        """
        for _ in range(100):
            # ----- random position -----
            theta = np.random.uniform(0, 2 * np.pi)
            phi   = np.random.uniform(0, np.pi)
            pos_list = [theta, phi, self.r]

            # ----- random movement (Δθ, Δφ) -----
            dtheta = np.random.uniform(-np.pi, np.pi)          # up to half‑circumference
            dphi   = np.random.uniform(-np.pi / 2, np.pi / 2)   # avoid jumping over both poles at once
            mov_list = [dtheta, dphi]

            # ----- expected new state -----
            # copy current angles so the level isn’t polluted for the next loop
            self.position[0], self.position[1] = theta, phi
            self.move(np.array([dtheta, dphi]))
            expected = [self.position[0], self.position[1], self.r]

            # ----- model output -----
            try:
                out = model(pos_list, mov_list)
            except Exception:
                return False

            # ----- validation -----
            if not isinstance(out, (list, tuple)) or len(out) != 3:
                return False
            out_theta, out_phi, out_r = out
            if not np.isclose(out_r, self.r, atol=1e-5):
                return False
            if not np.isclose(out_theta % (2*np.pi), expected[0] % (2*np.pi), atol=1e-5):
                return False
            if not np.isclose(out_phi, expected[1], atol=1e-5):
                return False
        return True


class NonUniqueODE(Level):
    """
    The world is a one-dimensional curve embedded in a 2d plane.  The curve is a solution of the ODE:
    $ dy/dx = 2 * |y|^(1/2) $
    with the initial condition y(0) = 0.

    Besides the trivial solution y(x) = 0, there is an infinite family of solutions, of the form:
    $
        y(x) =
            -(x - A)^2  , if x < A
            0           , if A <= x <= B
            (x - B)^2   , if x > B
    $
    where A, B are constant with A <= 0 <= B.
    Desmos graph: https://www.desmos.com/calculator/b0hbytghwr

    The goal is to showcase _inter-uiverse non-determinism_ (and not intra-universe). A and B are magic constants that change the "shape" of the world (in a predictable, deterministic way), but they nonetheless can be random.

    The ideal scenario would be: player restarts the world a few times, maybe saves points along the curve and plots them. Then notices the shape always looks similar and (maybe?) takes the derivative.

    Attributes
    ----------
    x : float
        The coordinate along the x-axis of the 2d plane. The `position` is always np.array([x, y(x)])
    A : int
        Lower constant describing the curve
    B : int
        Upper constant describing the curve

    Methods
    -------
    y() -> float
        Computes the y coordinate, for the current `x`
    """

    def __init__(self):
        self.dim = 2
        self.dim_move = 1
        self.x = 0.0 # position
        self.A = -2
        self.B = 1
        self.position = np.array([self.x, self.y()])

    def restart(self):
        self.A = np.random.randint(-10, 0)
        self.B = np.random.randint(0, 10)
        self.x = 0.0
        self.position = np.array([self.x, self.y()])
        self.known_points = {}
    
    def description(self):
        return """In this level, the `model` takes only a 1-dimensional position, representing the y coordinate, and outputs a scalar. Your task is to find the universal law governing this space.

`model` should have type model(y: float) -> float

HINT: restart the world, see what changes, and what doesn't!"""

    def y(self):
        if self.x < self.A: return -(self.x - self.A)**2
        elif self.x > self.B: return (self.x - self.B)**2
        else: return 0
    
    def move(self, movement_vector: np.array):
        assert(len(movement_vector) == 1)
        self.x += movement_vector[0]
        self.position = np.array([self.x, self.y()])
    
    def save_point(self, name: str):
        self.known_points[name] = self.position.copy()

    def measure_angle(self, left_point: str, right_point: str) -> int:
        raise Exception("you do not need to measure angles to complete this level")

    def measure_length(self, other_point) -> int:
        raise Exception("you do not need to measure lengths to complete this level")

    def check(self, model):
        for i in range(100):
            y = np.random.randint(-50, 50, 1)
            sol = 2 * np.sqrt(np.abs(y))
            if not math.isclose(model(y), sol):
                return False
        return True