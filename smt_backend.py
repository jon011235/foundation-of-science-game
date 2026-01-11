from z3 import *
from game_backend import Level, Euclidean, Elevator, SimpleTime, Spherical

class SMTLevelWrapper:
    """
    Wraps a Level and provides SMT-based validation using Z3.
    The validator uses symbolic execution to verify that a model
    satisfies the level's constraints for all possible inputs.
    """
    
    def __init__(self, level: Level):
        self.level = level
    
    def __getattr__(self, name):
        """Delegate all other method calls to the wrapped level."""
        return getattr(self.level, name)
    
    def find_counterexample(self, make_model, use_ints = False):
        """
        Validates a model using SMT solver Z3.
        
        Args:
            make_model: A function that takes (pos_vars, mov_vars) and returns
                       formulas for the new position after movement.
                       pos_vars and mov_vars are lists of Z3 Int variables.
        
        Returns:
            None if the user & expected models are the same. Otherwise, a dict with a counterexample:
            ```py
            {
                'pos': {0: 1, 1: 0, 2: 1},  # indicating the initial position (1, 0, 1)
                'mov': {0: 0, 1: 2},
                'exp': {0: 1, 1: 2, 2: 0},
                'out': {0: 1, 1: 2, 2: 9},
            }
            ```
        """
        s = Solver()
        
        # Create SMT variables based on level dimensions
        var_type = Real if not use_ints else Int
        pos_vars = [var_type(f'pos_{i}') for i in range(self.level.dim)]
        mov_vars = [var_type(f'mov_{i}') for i in range(self.level.dim_move)]
        expected_vars = [var_type(f'exp_{i}') for i in range(self.level.dim)]

        # Add the expected behavior constraint
        self._get_expected_formula(s, pos_vars, mov_vars, expected_vars)
        
        # Get user model's formulas for output variables
        try:
            out_formulas = make_model(pos_vars, mov_vars)
            if len(out_formulas) != self.level.dim:
                print(f"Incorrect output for model: should be list of formulas, with length {self.level.dim}")
                return None
        except Exception as e:
            print(f"Error calling make_model: {e}")
            return False

        # Add dummy variables for user model's output formulas 
        out_vars = [var_type(f'out_{i}') for i in range(self.level.dim)]
        for (var, formula) in zip(out_vars, out_formulas):
            s.add(var == formula)
        
        # Constrain model to find values where at least one expected/output pair is different
        diff_out = [out_var != exp_var for (out_var, exp_var) in zip(out_vars, expected_vars)]
        s.add(Or(diff_out))


        # Try to find a counterexample
        if s.check() == sat:
            model = s.model()
            counter = {}

            # help function (get {id} from string of type "pos_{id}")
            def var_to_id(var, prefix_len = 4): return int((var.__str__())[prefix_len:])

            for (name, vars) in [("pos", pos_vars), ("mov", mov_vars), ("exp", expected_vars), ("out", out_vars)]:
                counter[name] = dict([(var_to_id(v), model[v]) for v in vars])

            return counter
        
        return None
    
    def _get_expected_formula(self, s: Solver, pos_vars, mov_vars, expected_vars):
        """
        Adds level-specific constraints to solver:
            - constraints relating initial coordinates & movement vector to expected output coordinates
            - constraints on the initial coordinates & movement vector (e.g. initial position can only take certain values in certain dimensions)

        Args:
            s: z3 solver
            pos_vars: z3 variables for initial coordinates (list of length level.dim)
            mov_vars: z3 variables for movement vector (list of length level.dim_move)
            expected_vars: z3 variables for expected output coordinates (list of length level.dim)
        """
        raise NotImplemented


class EuclideanSMTWrapper(SMTLevelWrapper):
    """SMT wrapper for Euclidean levels."""

    def __init__(self, dim = 3):
        super(EuclideanSMTWrapper, self).__init__(Euclidean(dim))
    
    def _get_expected_formula(self, s: Solver, pos_vars, mov_vars, expected_vars):
        for (pos, mov, out) in zip(pos_vars, mov_vars, expected_vars):
            s.add(out == pos + mov)


class ElevatorSMTWrapper(SMTLevelWrapper):
    """SMT wrapper for Elevator level (3D position, 2D movement)."""

    def __init__(self):
        super(ElevatorSMTWrapper, self).__init__(Elevator())
    
    def _get_expected_formula(self, s, pos_vars, mov_vars, expected_vars):
        s.add(Or(pos_vars[2] == 0, pos_vars[2] == 1))

        new_x = pos_vars[0] + mov_vars[0]
        new_y = pos_vars[1] + mov_vars[1]

        at_elevator_pos = And(new_x == 1, new_y == 2)
        new_z = If(at_elevator_pos, 1 - pos_vars[2], pos_vars[2])

        s.add([exp == out for (exp, out) in zip(expected_vars, [new_x, new_y, new_z])])