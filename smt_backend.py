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
    
    def validate_with_smt(self, make_model):
        """
        Validates a model using SMT solver Z3.
        
        Args:
            make_model: A function that takes (s, pos_vars, mov_vars) and returns
                       output variables representing the new position after movement.
                       s is the Z3 solver, pos_vars and mov_vars are lists of Z3 Int variables.
        
        Returns:
            True if the model is valid for all inputs, False otherwise (with counterexample).
        """
        s = Solver()
        
        # Create SMT variables based on level dimensions
        pos_vars = [Int(f'pos_{i}') for i in range(self.level.dim)]
        mov_vars = [Int(f'mov_{i}') for i in range(self.level.dim_move)]
        out_vars = [Int(f'out_{i}') for i in range(self.level.dim)]
        expected_vars = [Int(f'expected_{i}') for i in range(self.level.dim)]
        
        # Get model's output variables
        try:
            make_model(s, pos_vars, mov_vars, out_vars)
        except Exception as e:
            print(f"Error calling make_model: {e}")
            return False

        # Add the expected behavior constraint
        self._get_expected_formula(s, pos_vars, mov_vars, expected_vars)
        
        diff_out = [out_var != exp_var for (out_var, exp_var) in zip(out_vars, expected_vars)]
        s.add(Or(diff_out))

        # s.add(pos_vars[0] == 0)
        # s.add(pos_vars[1] == 0)
        # s.add(pos_vars[2] == 0)
        # s.add(mov_vars[0] == 1)
        # s.add(mov_vars[1] == 2)
        # print(s)
        # print(s.check())
        # print(s.model())
        # print(s.consequences([pos_vars[0] == 1, pos_vars[1] == 2, pos_vars[2] == 0], [expected_vars[0]]))
        
        # Try to find a counterexample
        if s.check() == sat:
            model = s.model()
            print("Counterexample found:")
            print(f"  Position: {[model[v] for v in pos_vars]}")
            print(f"  Movement: {[model[v] for v in mov_vars]}")
            print(f"  Expected: {[model[v] for v in expected_vars]}")
            print(f"  Got: {[model[v] for v in out_vars]}")
            return False
        
        return True
    
    def _get_expected_formula(self, s: Solver, pos_vars, mov_vars, expected_vars):
        """
        Returns the expected output as Z3 formulas based on level type.
        Override this per level subclass for custom behavior.
        """
        raise NotImplemented


class EuclideanSMTWrapper(SMTLevelWrapper):
    """SMT wrapper for Euclidean levels."""
    
    def _get_expected_formula(self, s: Solver, pos_vars, mov_vars, expected_vars):
        for (pos, mov, out) in zip(pos_vars, mov_vars, expected_vars):
            s.add(out == pos + mov)


class ElevatorSMTWrapper(SMTLevelWrapper):
    """SMT wrapper for Elevator level (3D position, 2D movement)."""
    
    def _get_expected_formula(self, s, pos_vars, mov_vars, expected_vars):
        s.add(Or([ pos_vars[2] == 1, pos_vars[2] == 0]))

        # Move in x, y with no z change, then apply elevator logic
        new_x = pos_vars[0] + mov_vars[0]
        new_y = pos_vars[1] + mov_vars[1]
        old_z = pos_vars[2]

        s.add(expected_vars[0] == new_x)
        s.add(expected_vars[1] == new_y)
        
        # Elevator at [1, 2, 0] lifts to [1, 2, 1]
        at_elevator = And(new_x == 1, new_y == 2)
        at_elevator_lower = And(at_elevator, old_z == 0)
        
        # Apply elevator logic: if at [1,2,0] go to [1,2,1], else if at [1,2,1] go to [1,2,0]
        final_z = If(at_elevator_lower, 1, If(at_elevator, 0, old_z))

        s.add(expected_vars[2] == final_z)
        


def make_model_euclidean(s, pos_vars, mov_vars, out_vars):
    for (pos, mov, out) in zip(pos_vars, mov_vars, out_vars):
        s.add(out == pos + mov)

# TODO: the user should not get access to s
def make_model_elevator(s, pos_vars, mov_vars, out_vars):
    new_x = pos_vars[0] + mov_vars[0]
    new_y = pos_vars[1] + mov_vars[1]

    at_elevator_pos = And(new_x == 1, new_y == 2)
    new_z = If(at_elevator_pos, 1 - pos_vars[2], pos_vars[2])

    s.add(out_vars[0] == new_x)
    s.add(out_vars[1] == new_y)
    s.add(out_vars[2] == new_z)

# lvl = EuclideanSMTWrapper(Euclidean(3))
# print(lvl.validate_with_smt(make_model_euclidean))


lvl = ElevatorSMTWrapper(Elevator())
print(lvl.validate_with_smt(make_model_elevator))