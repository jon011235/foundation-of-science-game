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

def nparr_to_tuple(arr):
    return tuple(int(i) for i in arr)
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

    def solution_description(self):
        # should include the relevant things to notice and model in this level
        raise NotImplemented

    def move(self, movement_vector):
        raise NotImplemented

    def save_point(self, name):
        raise NotImplemented
    
    def measure_angle(self, left_point, right_point): # measuring the angle between two points and the current position
        raise NotImplemented
    
    def check(self, model): # odel is a function that given the context (i.e. the position and where to move) and predicts how a state (i.e. the position) changes
        raise NotImplemented
    
    def quote(self):
        raise NotImplemented

class Euclidean(Level):
    def __init__(self, dim: int = 3, dim_move: int = 3):
        self.dim = dim
        self.dim_move = dim
        self.position = np.zeros(dim)
        self.known_points = {}
    
    def description(self):
        return f"""This level expects the model to take a {self.dim}-sized tuple `position` and a {self.dim_move}-sized tuple `movement_vector`.
        It should return a {self.dim}-sized tuple with the predicted new position.
        
        That is, `model` should have type `model(position: Tuple[int, ...], movement: Tuple[int, ...]) -> Tuple[int, ...]`
        where the tuples have size {self.dim}, {self.dim_move} and {self.dim} respectively."""
    
    def solution_description(self):
        return """This is just a normal [Euclidean](https://en.wikipedia.org/wiki/Euclidean_geometry) geometry that we are used to, from our normal lives.
A possible solution is:
```python
def model(position, movement):
    return tuple(p+m for (p,m) in zip(position, movement))
```
"""
    
    def quote(self):
        return r"""
    # Euclidean
    _There is no royal road to geometry._ 
    -- Euclid
    """

    def move(self, movement_vector: np.ndarray):
        self.position += movement_vector
    
    def save_point(self, name: str):
        self.known_points[name] = self.position.copy()

    def measure_angle(self, left_point: str, right_point: str) -> float: # measuring the angle (in rad) between two points and the current position
        a = self.known_points[left_point] - self.position
        b = self.known_points[right_point] - self.position
        return angle_between(a, b)

    def measure_length(self, other_point):
        return np.linalg.norm(self.known_points[other_point]-self.position)

    def check(self, model):
        for i in range(100):
            pos = np.random.randint(-1000, 1000, self.dim)
            move = np.random.randint(-1000, 1000, self.dim)
            if nparr_to_tuple(pos+move) != model(nparr_to_tuple(pos), nparr_to_tuple(move)):
                return False
        return True


class Elevator(Euclidean):
    def __init__(self):
        super().__init__()
        self.dim_move = 2
        self.known_points["check me out"] = np.array([1,2,0])

    def description(self):
        return """In this level, positions are represented by 3-dimensional tuples, while the movement vector by a 2-dimensional tuple. Given the current position and a movement vector, you need to predict the next position.
        
        `model` should have type `model(position: Tuple[int, int, int], movement: Tuple[int, int]) -> Tuple[int, int, int]`"""

    def solution_description(self):
        return """The world seems to consist of a simple 2-dimensional plane, until you travel to `(1, 2, 0)`. Here, you get "teleported" to the parallel plane `z = 1`.

A possible solution is:
```py
def model(position, movement):
    # Convert tuple to list to modify
    pos = list(position)
    for i in range(2):
        pos[i] += movement[i]
    if pos[0] == 1 and pos[1] == 2:
        pos[2] = 1 - pos[2]
    return tuple(pos)
```

You could think of `(1, 2, 0)` as a [wormhole](https://en.wikipedia.org/wiki/Wormhole), a hypothetical structure that connects seemingly desperate points in space. Fascinating about wormholes is that the mathematical framework of general relativity _allows for their existence_. Does this imply that they exist? Or that they could?

It has been pointed out that maths is [unreasonably effective](https://en.wikipedia.org/wiki/The_Unreasonable_Effectiveness_of_Mathematics_in_the_Natural_Sciences) at modelling the natural word. And indeed, when we try to model simple physics experiments, we often reach mathematical descriptions that apply to a large class of phenomena. Is there underlying truth to these models? Should we expect that mathematical possibilities in our models will translate to (yet-unobserved) physical phenomena?

Or should we always be careful not to mistake the map for the mountain? That is, (mathematical) models are useful as "maps" in as much as they predict how the world functions (i.e. show us the way through the mountains). But we should put little trust in maps of uncharted territories. Even if an elegant mathematical theory predicts some theoretical outcomes, should we only trust in it once we observe it empirically?"""
    
    def quote(self):
        return r"""
        # Elevator
        _Ever heard of a wormhole?_
        """

    def move(self, movement_vector: np.ndarray):
        self.position += np.append(movement_vector, 0)
        if np.all(self.position == self.known_points["check me out"]):
            self.position += np.array([0,0,1])
        elif list(self.position) == list(self.known_points["check me out"]+np.array([0,0,1])):
            self.position -= np.array([0,0,1])

    def check(self, model):
        save_position = self.position
        try:

            for i in range(100):
                pos = np.random.randint(-1000, 1000, 3)
                pos[2] = np.random.randint(0,2)
                self.position = pos.copy()
                move = np.random.randint(-1000, 1000, 2)
                self.move(move)
                if nparr_to_tuple(self.position) != model(nparr_to_tuple(pos), nparr_to_tuple(move)):
                    self.position = save_position
                    return False
        
            for i in range(100):
                pos = np.random.randint(-10, 10, 3)
                pos[2] = np.random.randint(0,2)
                self.position = pos.copy()
                move = np.random.randint(-10, 10, 2)
                self.move(move)
                if nparr_to_tuple(self.position) != model(nparr_to_tuple(pos), nparr_to_tuple(move)):
                    self.position = save_position
                    return False
        
            pos = [30, 20, 1]
            self.position = pos.copy()
            move = [-29, -18]
            self.move(move)
            if nparr_to_tuple(self.position) != model(nparr_to_tuple(pos), nparr_to_tuple(move)):
                self.position = save_position
                return False
        
            pos = [30, 20, 0]
            self.position = pos.copy()
            move = [-29, -18]
            self.move(move)
            if nparr_to_tuple(self.position) != model(nparr_to_tuple(pos), nparr_to_tuple(move)):
                self.position = save_position
                return False
        
            # TODO can not test position at "check me out" and move 0 as this is not testable for user
            # TODO wrong, they can stand still on that spot, but maybe hard to guess

            self.position = save_position
            return True
        finally:
            self.position = save_position
      

class SimpleTime(Euclidean):
    def __init__(self):
        super().__init__()
        self.dim_move = 2
    
    def description(self):
        return """This level takes 2 dimensions as a movementvector (tuple) and
        expects the model to take a 3 dimensional `position` tuple and a 2 dimensional `movement_vector` tuple.
        It should return a 3 dimensional tuple with the predicted new position
        
        So `model` should have type `model(position: Tuple[int, int, int], movement: Tuple[int, int]) -> Tuple[int, int, int]`"""
    
    def solution_description(self):
        return """
A possible solution is:
```python
import math
def model(p, m):
    pos = (p[0]+m[0], p[1]+m[1], p[2]+round(math.sqrt(m[0]**2 + m[1]**2)))
    return pos
```

Notice how the third dimension always increases as you move? This mirrors how [Time](https://en.wikipedia.org/wiki/Spacetime) behaves in our universe. In physics, space and time are fused into a four-dimensional continuum called spacetime. We can move freely in space, but we are seemingly forced to move forward in time.

Or is it related to entropy? The [Second Law of Thermodynamics](https://en.wikipedia.org/wiki/Second_law_of_thermodynamics) states that the total entropy of an isolated system can never decrease over time. This gives time an arrow, a direction.
"""

    def quote(self):
        return r"""
    # SimpleTime
    _The distinction between the past, present and future is only a stubbornly persistent illusion._
    -- Albert Einstein
    """

    def move(self, movement_vector: np.ndarray):
        self.position += np.append(movement_vector, round(np.sqrt(movement_vector[0]**2+movement_vector[1]**2)))
    
    def check(self, model):
        save_position = self.position
        try:

            for i in range(100):
                pos = np.random.randint(-1000, 1000, 3)
                self.position = pos.copy()
                move = np.random.randint(-1000, 1000, 2)
                self.move(move)
                if nparr_to_tuple(self.position) != model(nparr_to_tuple(pos), nparr_to_tuple(move)):
                    self.position = save_position
                    return False
            
            for i in range(30):
                pos = np.random.randint(-10, 10, 3)
                self.position = pos.copy()
                move = np.random.randint(-10, 10, 2)
                self.move(move)
                if nparr_to_tuple(self.position) != model(nparr_to_tuple(pos), nparr_to_tuple(move)):
                    self.position = save_position
                    return False
            self.position = save_position
            return True
        finally:
            self.position = save_position

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
        self.dim = 2
        self.dim_move =2

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
        return """This level takes 3 dimensions as a movementvector (tuple) and
        expects the model to take a 2 dimensional `position` tuple and a 2 dimensional `movement_vector` tuple.
        It should return a 3 dimensional tuple with the predicted new position
        
        So `model` should have type `model(position: Tuple[float, float, float], movement: Tuple[float, float]) -> Tuple[float, float, float]`"""

    def solution_description(self):
        return """This level represents movement on a [Sphere](https://en.wikipedia.org/wiki/Sphere), using spherical coordinates (azimuth, polar angle, radius).

A possible solution is:
```python
import math

def model(position, movement):
    # position is (theta, phi, r)
    # movement is (d_theta, d_phi)
    
    theta = position[0] + movement[0]
    phi = position[1] + movement[1]
    r = position[2]

    # Normalize theta to [0, 2pi)
    theta = theta % (2 * math.pi)

    # Handle pole crossings for phi
    while phi < 0 or phi > math.pi:
        if phi < 0:
            phi = -phi
            theta += math.pi
        elif phi > math.pi:
            phi = 2 * math.pi - phi
            theta += math.pi
            
        # Re-normalize theta in case it flipped
        theta = theta % (2 * math.pi)

    return (theta, phi, r)
```

Historically, realizing the Earth was spherical required looking at the stars or observing ships disappear hull-first over the horizon. In this model, you might have noticed that moving "East" (changing $\\theta$) eventually brings you back to where you started, or that moving "North" (changing $\\phi$) behaves strangely near the poles.

This geometry is non-Euclidean. On a sphere, the sum of angles in a triangle is greater than 180 degrees!
"""

    def quote(self):
        return r"""
    # Spherical
    _The shortest path between two points is not always a straight line._ 
    """

    def move(self, movement_coords: np.ndarray):
        movement_coords = np.array(movement_coords)
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
          1. Build the position tuple   → (θ, φ, r)
          2. Build the movement tuple   → (Δθ, Δφ)
          3. Compute the expected new spherical coordinates
             using the same logic as `move`.
          4. Call the model and verify:
                * it returns a tuple of length 3,
                * the radius component equals `self.r` (within tolerance),
                * the returned angles match the expected ones (tolerance 1e‑5).
        """
        save_position = self.position
        try:
            for _ in range(100):
                # ----- random position -----
                theta = np.random.uniform(0, 2 * np.pi)
                phi   = np.random.uniform(0, np.pi)
                pos_tuple = (theta, phi, self.r)

                # ----- random movement (Δθ, Δφ) -----
                dtheta = np.random.uniform(-np.pi, np.pi)          # up to half‑circumference
                dphi   = np.random.uniform(-np.pi / 2, np.pi / 2)   # avoid jumping over both poles at once
                mov_tuple = (dtheta, dphi)

                # ----- expected new state -----
                # copy current angles so the level isn’t polluted for the next loop
                self.position[0], self.position[1] = theta, phi
                self.move(np.array([dtheta, dphi]))
                expected = (self.position[0], self.position[1], self.r)

                # ----- model output -----
                try:
                    out = model(pos_tuple, mov_tuple)
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
        finally:
            self.position = save_position



# AI generated, human checked
class UnitCircle(Level):
    """
    A level where the player stays on the unit circle in the plane.
    The position is a 2D point on the circle, but movement is a single scalar.
    A movement of 1 means moving by one radian along the circle.
    """
    def __init__(self):
        self.theta = 0.0
        self.dim = 2
        self.dim_move = 1
        self.position = np.array([1.0, 0.0])
        self.known_points = {}

    def _update_position(self):
        self.position[:] = np.array([np.cos(self.theta), np.sin(self.theta)])

    def _normalize_theta(self):
        self.theta = self.theta % (2 * np.pi)

    def restart(self):
        self.theta = 0.0
        self._update_position()

    def description(self):
        return """In this level, the `model` takes a 2-dimensional position, and a 1-dimensional movement vector. It should output the new, 2-dimensional position.

`model` should have type `model(position: Tuple[float, float], movement: Tuple[float]) -> Tuple[float, float]`"""

    def solution_description(self):
        return """This level represents motion along a unit circle in the plane.

A possible solution is:
```python
def model(position, movement):
    import math

    theta = math.atan2(position[1], position[0])
    theta = (theta + movement[0]) % (2 * math.pi)
    return (math.cos(theta), math.sin(theta))
```
"""

    def quote(self):
        return r"""
    # Unit Circle
    _Going round and round!_
    """

    def move(self, movement_coords: np.ndarray):
        movement_coords = np.array(movement_coords)
        if movement_coords.shape != (1,):
            raise ValueError("movement vector must have shape (1,) for UnitCircle")
        self.theta += float(movement_coords[0])
        self._normalize_theta()
        self._update_position()

    def save_point(self, name: str):
        self.known_points[name] = self.position.copy()

    def measure_angle(self, left_point: str, right_point: str) -> float:
        a = self.known_points[left_point] - self.position
        b = self.known_points[right_point] - self.position
        return angle_between(a, b)

    def measure_length(self, other_point: str) -> float:
        cur = self.position
        oth = self.known_points[other_point]
        dot = np.dot(cur, oth)
        sigma = np.arccos(np.clip(dot, -1.0, 1.0))
        return sigma

    def check(self, model):
        for _ in range(100):
            theta = np.random.uniform(0, 2 * np.pi)
            pos = np.array([np.cos(theta), np.sin(theta)])
            dtheta = np.random.uniform(-2 * np.pi, 2 * np.pi)
            expected_theta = (theta + dtheta) % (2 * np.pi)
            expected = np.array([np.cos(expected_theta), np.sin(expected_theta)])

            try:
                out = model(tuple(pos), (dtheta,))
            except Exception:
                return False
            if not isinstance(out, (list, tuple)) or len(out) != 2:
                return False
            out_pos = np.array(out, dtype=float)
            if not np.allclose(out_pos, expected, atol=1e-5):
                return False
        return True


# AI generated, human checked
class UnitSphere(Level):
    """
    A level where the player stays on the unit sphere in 3D.
    The position is a 3D point on the sphere, and movement is a 2D vector of radians.
    The first value changes the azimuth and the second the polar angle.
    """
    def __init__(self):
        self.theta = 0.0
        self.phi = np.pi / 2.0
        self.dim = 3
        self.dim_move = 2
        self.position = self._cartesian(self.theta, self.phi)
        self.known_points = {}

    def _cartesian(self, theta: float, phi: float) -> np.ndarray:
        return np.array([
            np.sin(phi) * np.cos(theta),
            np.sin(phi) * np.sin(theta),
            np.cos(phi)
        ])

    def _normalize_angles(self, theta: float, phi: float):
        theta = theta % (2 * np.pi)
        while phi < 0 or phi > np.pi:
            if phi < 0:
                phi = -phi
                theta += np.pi
            elif phi > np.pi:
                phi = 2 * np.pi - phi
                theta += np.pi
        return theta % (2 * np.pi), phi

    def _update_position(self):
        self.position[:] = self._cartesian(self.theta, self.phi)

    def restart(self):
        self.theta = 0.0
        self.phi = np.pi / 2.0
        self._update_position()

    def description(self):
        return """In this level, the `model` takes a 3-dimensional position, and a 2-dimensional movement vector. It should output the new, 3-dimensional position.

`model` should have type `model(position: Tuple[float, float, float], movement: Tuple[float, float]) -> Tuple[float, float, float]`"""

    def solution_description(self):
        return """This level represents motion on a unit sphere in 3D.

A possible solution is:
```python
def model(position, movement):
    import math

    theta = math.atan2(position[1], position[0])
    phi = math.acos(position[2])
    theta = (theta + movement[0]) % (2 * math.pi)
    phi = phi + movement[1]
    while phi < 0 or phi > math.pi:
        if phi < 0:
            phi = -phi
            theta += math.pi
        elif phi > math.pi:
            phi = 2 * math.pi - phi
            theta += math.pi
    theta = theta % (2 * math.pi)
    return (math.sin(phi) * math.cos(theta), math.sin(phi) * math.sin(theta), math.cos(phi))
```
"""

    def quote(self):
        return r"""
    # Unit Sphere
    _Ok, I'm getting dizzy..._
    """

    def move(self, movement_coords: np.ndarray):
        movement_coords = np.array(movement_coords)
        if movement_coords.shape != (2,):
            raise ValueError("movement vector must have shape (2,) for UnitSphere")
        self.theta, self.phi = self._normalize_angles(
            self.theta + float(movement_coords[0]),
            self.phi + float(movement_coords[1])
        )
        self._update_position()

    def save_point(self, name: str):
        self.known_points[name] = self.position.copy()

    def measure_angle(self, left_point: str, right_point: str) -> float:
        a = self.known_points[left_point] - self.position
        b = self.known_points[right_point] - self.position
        return angle_between(a, b)

    def measure_length(self, other_point: str) -> float:
        cur = self.position
        oth = self.known_points[other_point]
        dot = np.dot(cur, oth)
        sigma = np.arccos(np.clip(dot, -1.0, 1.0))
        return sigma

    def check(self, model):
        for _ in range(100):
            theta = np.random.uniform(0, 2 * np.pi)
            phi = np.random.uniform(0, np.pi)
            pos = tuple(self._cartesian(theta, phi))
            dtheta = np.random.uniform(-np.pi, np.pi)
            dphi = np.random.uniform(-np.pi / 2, np.pi / 2)
            expected_theta, expected_phi = self._normalize_angles(
                theta + dtheta,
                phi + dphi
            )
            expected = np.array(self._cartesian(expected_theta, expected_phi))

            try:
                out = model(pos, (dtheta, dphi))
            except Exception:
                return False
            if not isinstance(out, (list, tuple)) or len(out) != 3:
                return False
            out_pos = np.array(out, dtype=float)
            if not np.allclose(out_pos, expected, atol=1e-5):
                return False
        return True


import random

class EverythingRandom(Euclidean):
    def __init__(self):
        super().__init__(2, 2)
        self.rng = np.random.default_rng(26764197)
    """ the seed was derived by this heavenly brute force, which did not run to its success (highest tested seed: 471539671 outputs 1 for 31 times)
    maximum = 0
    seed = 0
    i = 0

    while maximum != 100:
        r = np.random.default_rng(seed)
        i = 0
        while r.integers(0,2) ==1:
            i+=1
        if i>maximum:
            maximum = i
            max_seed = seed
        seed+=1
    """
    
    def description(self):
        return """This level takes 2 dimensions as a movement and positionvector.
        
        Your model should also use our magic number, that we will pass to you.
        So `model` should have type `model(position: Tuple[int, int], movement: Tuple[int, int], magic_number: int) -> Tuple[int, int]`"""
    
    def solution_description(self):
        return """
Did I trick you here? Everything feels so well behaved and then all out of a sudden nothing makes sense anymore.
While the model does get a `magic_number` the level at first does not fell like it needs such a random/magic number

A possible solution involves realizing the `magic_number` acts as a multiplier or switch for the movement:
```python
import numpy as np
def unit_vector(vector):
    base = np.sqrt(sum(i**2 for i in vector))
    if base == 0:
        return tuple(0 for i in vector)
    else:
        return tuple(i/base for i in vector)

def model(position, movement, magic_number):
    # When 0, position doesn't change.
    # When 1, position moves by the unit vector of movement.
    
    pos_arr = np.array(position)
    mov_arr = np.array(movement)
    
    if magic_number == 0:
        return tuple(pos_arr)
    else:
        uv = unit_vector(mov_arr)
        new_pos = pos_arr + magic_number * uv
        return tuple(int(x) for x in new_pos)
```

If we repeat experiments where we either can not control all influences or the experiment has some inherent randomness we always have to assume to risk of just recording `lucky` outcomes, that fit our hypothesis instead of the actual dynamic. One way to estimate the probability of this is to use a [hypothesis test](https://en.wikipedia.org/wiki/Statistical_hypothesis_test) where we estimate the probability of our hypothesis being wrong given some datapoints.
"""

    def quote(self):
        return r"""
    # EverythingRandom
    _God does not play dice with the universe._
    -- Albert Einstein
    """

    def move(self, movement_vector: np.ndarray, magic=None):
        if magic is None:
            magic = self.rng.integers(0,2)
        self.position += np.round(magic*unit_vector(movement_vector), 3)
    
    def check(self, model):
        save_position = self.position
        try:
            for i in range(100):
                pos = np.float64(np.random.randint(-1000, 1000, 2))
                magic = np.random.randint(0,2)
                move = np.random.randint(-1000, 1000, 2)
                self.position = pos.copy()
                self.move(move, magic)
                if not np.isclose(self.position, np.round(np.array(model(nparr_to_tuple(pos), nparr_to_tuple(move), magic)), 3)).all():
                    self.position = save_position
                    return False
            
            self.position = save_position
            return True
        finally:
            self.position = save_position



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

`model` should have type `model(y: float) -> float`

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
      

class NObservation(Euclidean):
    # roughly every second has something to observe
    observations = [(random.randint(0,100), random.randint(0,100)) for i in range(5000)]

    def __init__(self):
        super().__init__(2, 2)

    def observe(self):
        return tuple(self.position) in self.observations


    def description(self):
        return """This level uses 2D position and 2D movement.
Your model also receives `objects`, a list of known observable positions.

Return:
1) the new position after movement,
2) whether that new position is in `objects`,
3) the `objects` list.

Type:
model(position: Tuple[int, int], movement: Tuple[int, int], objects: List[Tuple[int, int]]) -> Tuple[Tuple[int, int], bool, List[Tuple[int, int]]]"""

    def solution_description(self):
        return """A correct model keeps ordinary 2D movement and checks membership in `objects`.

A possible solution is:
```python
def model(position, movement, objects):
    new_pos = tuple((position[0] + movement[0], position[1] + movement[1]))
    observed = new_pos in objects
    return (new_pos, observed, objects)
```
"""


    def quote(self):
        return r"""
    # NObservation
    _You see, but you do not observe._
    -- Sherlock Holmes
    """

    def check(self, model):
        def model_curried(a, b):
            a,b,c = model(a,b, self.observations)
            return a
        if not super().check(model_curried):
            return False
        
        
        for i in range(100):
            p = tuple((random.randint(0, 150) for i in range(2)))
            result = model(p, (0,0), self.observations)
            if (p in self.observations) != result[1] or self.observations != result[2]:
                print(p, result[:2], p in self.observations, self.observations!= result[2])
                # print(p in self.observations, p, model(p, (0,0), self.observations)[:3])
                return False
        return True
      
      
class Observation(NObservation):
    observations = []

    def __init__(self):
        super().__init__()
        
    
    def description(self):
        return """This level extends NObservation with a `magic` value in {0,1,2,3}.

If `magic == 0`, the current position is added to observations.
Otherwise, observations stay unchanged.

Return:
1) the new position after movement,
2) whether the new position is observed,
3) the observations list.

Type:
model(position: Tuple[int, int], movement: Tuple[int, int], objects: List[Tuple[int, int]], magic: int) -> Tuple[Tuple[int, int], bool, List[Tuple[int, int]]]"""

    # TODO they need to reverse basically exact this function... Do you have a better idea @andcov?
    def observe(self, magic=None):
        if magic is None:
            magic = random.randint(0,3)
        if magic == 0:
            self.observations.append(self.position)
            return True
        else: return False
    
    def solution_description(self):
        return """This level adds "quantum" stuff (if you want to use such a big and ill-used word) to the world. The observations change based on your movement, in particular they can only come into existence upon observations (when you move there) (simulated by `magic == 0`).

This once again shows us, that we always have to consider that we are part of the system we want to observe.

A possible solution is:
```python
def model(position, movement, objects, magic):
    new_pos = (position[0] + movement[0], position[1] + movement[1])

    # copy to avoid mutating caller-owned data
    new_objects = list(objects)
    if magic == 0 and new_pos not in new_objects:
        new_objects.append(new_pos)

    observed = new_pos in new_objects
    return (new_pos, observed, new_objects)
```
"""

    def quote(self):
        return r"""
    # Observation
    _Chance favors the prepared mind._
    -- Louis Pasteur
    """

    def check(self, model):
        def model_curried(a, b, c):
            return  model(a,b, c, 1)
        if not super().check(model_curried): # super = Nobservation
            return False
        
        # Test no observations there before
        save_observations = list(self.observations)
        save_position = self.position.copy()
        try:

            # Now test observation generation and persistence
            for _ in range(500):
                # pick a position that is not currently observed
                p = tuple((random.randint(0, 150), random.randint(0, 150)))
                if p in self.observations:
                    continue

                # if magic != 0, model must not claim an observation at a previously empty spot
                magic = random.randint(1, 3)
                out = model(p, (0, 0), self.observations, magic)
                if out[1] or set(self.observations) != set(out[2]):
                    self.observations = save_observations
                    self.position = save_position
                    return False

                # with magic == 0 the model should report an observation
                out = model(p, (0, 0), self.observations, 0)
                if not out[1] or not p in out[2]:
                    self.observations = save_observations
                    self.position = save_position
                    return False

                # subsequent queries (any magic) must report the observation exists (persistence)
                for magic2 in (0, 1, 2, 3):
                    res = model(p, (0, 0), out[2], magic2)
                    if not res[1] or set(res[2]) != set(out[2]):
                        self.observations = save_observations
                        self.position = save_position
                        return False


            # restore and succeed
            self.observations = save_observations
            self.position = save_position
            return True
        finally:
            self.position = save_position
            self.observations = save_observations


