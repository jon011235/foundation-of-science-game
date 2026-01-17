import numpy as np
import random

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
        return f"""This level takes {self.dim_move} values as a movementvector and
        expects the model to take a {self.dim} sized tuple `position` and a {self.dim_move} sized tuple `movement_vector`.
        It should return a {self.dim} sized tuple with the predicted new position.
        
        So `model` should have type `model(position: Tuple[int, ...], movement: Tuple[int, ...]) -> Tuple[int, ...]`
        where the tuples have size {self.dim}, {self.dim_move} and {self.dim} respectively."""
    
    def solution_description(self):
        return """This is just a normal [Euclidean](https://en.wikipedia.org/wiki/Euclidean_geometry) geometry that we are used to, from our normal lifes.
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


class NObservation(Euclidean):
    # roughly every second has something to observe
    observations = [(random.randint(0,100), random.randint(0,100)) for i in range(5000)]

    def __init__(self):
        super().__init__(2, 2)

    def observe(self):
        return self.position in self.observations


    def description(self):
        return """This level takes 2 dimensions as a movement and positionvector.

        This level allows to observe stuff, we already looked around in the world for a bit and will give you those things using the objects lists (a list with the position of the objects in 2d space)
        As a new thing please also return, whether there is something to be observed at the place where you are after the movement

        So model should have type model(position: Tuple[int, int], movement: Tuple[int, int], objects: List(Tuple[int, int])) -> (Tuple[int, int], Bool)"""
    
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
            p = (random.randint(0, 150) for i in range(2))
            result = model(p, (0,0), self.observations)
            if p in self.observations != result[1] or self.observations != result[2]:
                # print(p in self.observations, p, model(p, (0,0), self.observations)[:3])
                return False
        return True


class Observation(NObservation):
    observations = []

    def __init__(self):
        super().__init__()
        
    
    def description(self):
        return """This level takes 2 dimensions as a movement and positionvector.

        This level allows to observe stuff, we already looked around in the world for a bit and will give you those things using the objects list (a list with the position of the objects in 2d space).
        As a new thing please also return, whether there is something to be observed at the place where you are after the movement. Also return the observations you made

        Differently to the previous level your model should take in a magic number between 0 and 3

        so model should have type model(position: List(int), movement: List(int), objects: List(List(int)), magic: int) -> (List(int), Bool, List(List(int)))"""
    
    # TODO they need to reverse basically exact this function... Do you have a better idea @andcov?
    def observe(self, magic=None):
        if magic is None:
            magic = random.randint(0,3)
        if magic == 0:
            self.observations.append(self.position)
            return True
        else: return False
    
    def check(self, model):
        def model_curried(a, b, c):
            return  model(a,b, c, 1)
        if not super().check(model_curried): # super = Nobservation
            return False
        

        # Test no observations there before
        save_observations = list(self.observations)
        save_position = self.position.copy()

        # Now test observation generation and persistence
        for _ in range(500):
            # pick a position that is not currently observed
            p = (random.randint(0, 150), random.randint(0, 150))
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


