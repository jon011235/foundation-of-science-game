"""
Basically all of this was kindly provided by Github Copilot
"""

import sys
import os
import importlib.util
import readline
import numpy as np
import matplotlib.pyplot as plt

# local import
import game_backend as gb
import smt_backend as smtb

def load_model_from_path(path):
    path = os.path.expanduser(path)
    if not os.path.isfile(path):
        print("model file not found:", path)
        return None
    spec = importlib.util.spec_from_file_location("user_model", path)
    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
    except Exception as e:
        print("error importing model:", e)
        return None
    if not hasattr(mod, "model"):
        print("module does not define 'model(position, movement)' function")
        return None
    if not callable(mod.model):
        print("'model' is not callable")
        return None
    return mod.model

class CLI:
    success = False # Flag used to stop the interface if a level was mastered

    def __init__(self, level):
        self.level = level
        self.history = [self.level.position.copy()] # list of numpy positions

    def start(self):
        print("Simple terminal interface for foundation-of-science-game")
        print("type 'help' for commands")
        print()
        print("This levels description:")
        print(self.level.description())
        while True:
            try:
                line = input("> ").strip()
            except (EOFError, KeyboardInterrupt):
                print()
                break
            if not line:
                continue
            parts = line.split()
            cmd = parts[0].lower()
            args = parts[1:]
            if cmd in ("quit", "exit"):
                break
            handler = getattr(self, "cmd_" + cmd, None)
            if handler:
                try:
                    handler(args)
                    if self.success == True:
                        break
                except Exception as e:
                    print("error:", e)
            else:
                print("unknown command:", cmd)

    def cmd_help(self, args):
        print("""commands:
  move x,y,...         - move by the given integer vector
  save NAME            - save current position under NAME
  angle LEFT RIGHT     - measure angle between saved points LEFT and RIGHT from current position (radians)
  length NAME          - vector from current position to saved point NAME
  show                 - show current position
  plot                 - plot visited positions (2D or 3D depending on dimension)
  check PATH           - load model from PATH (Python file with function model(position, movement))
                         and run level.check(model)
  help                 - show this message
  exit | quit          - quit""")
        print(self.level.description())

    def cmd_move(self, args):
        if not args:
            print("usage: move x,y,...")
            return
        vec_str = " ".join(args)
        # accept comma or space separated
        if "," in vec_str:
            parts = [p.strip() for p in vec_str.split(",") if p.strip()]
        else:
            parts = vec_str.split()
        if len(parts) != self.level.dim_move:
            print(f"expected {self.level.dim_move} values, got {len(parts)}")
            return
        try:
            vec = np.array([float(p) for p in parts])
        except ValueError:
            print("invalid numbers")
            return
        self.level.move(vec)
        self.history.append(self.level.position.copy())
        print("moved to", self.level.position)

    def cmd_save(self, args):
        if not args:
            print("usage: save NAME")
            return
        name = args[0]
        self.level.save_point(name)
        print(f"saved current position as '{name}'")

    def cmd_angle(self, args):
        if len(args) != 2:
            print("usage: angle LEFT RIGHT")
            return
        left, right = args
        try:
            a = self.level.measure_angle(left, right)
        except Exception as e:
            print("error measuring angle:", e)
            return
        print("angle (radians):", a)

    def cmd_length(self, args):
        if len(args) != 1:
            print("usage: length NAME")
            return
        name = args[0]
        try:
            vec = self.level.measure_length(name)
        except Exception as e:
            print("error measuring length:", e)
            return
        print("vector to", name, "=", vec)

    def cmd_show(self, args):
        print("position:", self.level.position)
        if hasattr(self.level, "known_points"):
            print("saved points:", list(self.level.known_points.keys()))

    def cmd_plot(self, args):
        dim = self.level.dim
        hist = np.array(self.history)
        if hist.shape[0] < 1:
            print("no history to plot")
            return
        if dim == 2:
            plt.figure()
            plt.plot(hist[:, 0], hist[:, 1], marker="o", linestyle="-")
            plt.scatter(hist[0, 0], hist[0, 1], c="green", label="start")
            plt.scatter(hist[-1, 0], hist[-1, 1], c="red", label="current")
            for name, pos in self.level.known_points.items():
                p = np.array(pos)
                plt.scatter(p[0], p[1], marker="x")
                plt.text(p[0], p[1], " "+name)
            plt.xlabel("x"); plt.ylabel("y"); plt.axis("equal"); plt.legend()
            plt.title("Movement history (2D)")
            plt.show()
        elif dim == 3:
            from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
            fig = plt.figure()
            ax = fig.add_subplot(111, projection="3d")
            ax.plot(hist[:, 0], hist[:, 1], hist[:, 2], marker="o")
            ax.scatter([hist[0,0]], [hist[0,1]], [hist[0,2]], c="green", label="start")
            ax.scatter([hist[-1,0]], [hist[-1,1]], [hist[-1,2]], c="red", label="current")
            for name, pos in self.level.known_points.items():
                p = np.array(pos)
                ax.scatter([p[0]], [p[1]], [p[2]], marker="x")
                ax.text(p[0], p[1], p[2], " "+name)
            ax.set_xlabel("x"); ax.set_ylabel("y"); ax.set_zlabel("z")
            plt.title("Movement history (3D)")
            plt.show()
        else:
            # high-dim: show pairwise first two dims as fallback
            plt.figure()
            plt.plot(hist[:, 0], hist[:, 1], marker="o", linestyle="-")
            plt.title(f"Movement history (first two dims of dim={dim})")
            plt.show()

    def cmd_check(self, args):
        if not args:
            print("usage: check PATH_TO_MODEL_PY")
            return
        path = args[0]
        model_func = load_model_from_path(path)
        if model_func is None:
            return
        try:
            ok = self.level.check(model_func)
        except Exception as e:
            print("error running check:", e)
            return
        print("model check result:", ok)
        self.success = ok

    def cmd_checksmt(self, args):
        if not isinstance(self.level, smtb.SMTLevelWrapper):
            print("error running SMT check: this level does not support SMT checking")
        if not args:
            print("usage: checksmt PATH_TO_MODEL_PY")
            return
        path = args[0]
        model_func = load_model_from_path(path)
        if model_func is None:
            return
        try:
            cntex = self.level.find_counterexample(model_func)
        except Exception as e:
            print("error running check:", e)
            return
        if cntex is None:
            print("model check result: True")
            self.success = True
        else:
            print("model check result: False")
            # TODO: pretty print `cntex` for extra hint
            # print(cntex)
            self.success = False



if __name__ == "__main__":
    cli = CLI(gb.Euclidean())
    cli.start()