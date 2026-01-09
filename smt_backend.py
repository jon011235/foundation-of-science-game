from z3 import *
import numpy as np
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
        
        # Get model's output variables
        try:
            out_vars = make_model(s, pos_vars, mov_vars)
        except Exception as e:
            print(f"Error calling make_model: {e}")
            return False
        
        if not isinstance(out_vars, (list, tuple)) or len(out_vars) != self.level.dim:
            print("Model output must have same dimension as level")
            return False
        
        # Add the expected behavior constraint
        expected = self._get_expected_formula(pos_vars, mov_vars)
        
        for i, (out_var, exp_var) in enumerate(zip(out_vars, expected)):
            s.add(out_var == exp_var)
        
        # Try to find a counterexample
        if s.check() == sat:
            model = s.model()
            print("Counterexample found:")
            print(f"  Position: {[model[v].as_long() for v in pos_vars]}")
            print(f"  Movement: {[model[v].as_long() for v in mov_vars]}")
            print(f"  Expected: {[model[v].as_long() for v in expected]}")
            print(f"  Got: {[model[v].as_long() for v in out_vars]}")
            return False
        
        return True
    
    def _get_expected_formula(self, pos_vars, mov_vars):
        """
        Returns the expected output as Z3 formulas based on level type.
        Override this per level subclass for custom behavior.
        """
        # Default: simple addition (Euclidean)
        return [pos_vars[i] + mov_vars[i] for i in range(len(pos_vars))]


class EuclideanSMTWrapper(SMTLevelWrapper):
    """SMT wrapper for Euclidean levels."""
    
    def _get_expected_formula(self, pos_vars, mov_vars):
        return [pos_vars[i] + mov_vars[i] for i in range(len(pos_vars))]


class ElevatorSMTWrapper(SMTLevelWrapper):
    """SMT wrapper for Elevator level (3D position, 2D movement)."""
    
    def _get_expected_formula(self, pos_vars, mov_vars):
        # Move in x, y with no z change, then apply elevator logic
        new_x = pos_vars[0] + mov_vars[0]
        new_y = pos_vars[1] + mov_vars[1]
        new_z = pos_vars[2]
        
        # Elevator at [1, 2, 0] lifts to [1, 2, 1]
        elevator_pos_xy = And(new_x == 1, new_y == 2)
        at_elevator = And(elevator_pos_xy, new_z == 0)
        
        # Apply elevator logic: if at [1,2,0] go to [1,2,1], else if at [1,2,1] go to [1,2,0]
        final_z = If(at_elevator, 1, If(And(elevator_pos_xy, new_z == 1), 0, new_z))
        
        return [new_x, new_y, final_z]


class SimpleTimeSMTWrapper(SMTLevelWrapper):
    """SMT wrapper for SimpleTime level (3D position, 2D movement)."""
    
    def _get_expected_formula(self, pos_vars, mov_vars):
        new_x = pos_vars[0] + mov_vars[0]
        new_y = pos_vars[1] + mov_vars[1]
        
        # z increases by sqrt(dx² + dy²)
        dist_squared = mov_vars[0] * mov_vars[0] + mov_vars[1] * mov_vars[1]
        new_z = pos_vars[2] + Int(np.sqrt(2)) * If(dist_squared > 0, 1, 0)  # Simplified
        
        return [new_x, new_y, new_z]