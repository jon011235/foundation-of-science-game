// We'll dynamically import z3-solver in runDemo and load the z3-built.js
// artifact (the emscripten-generated script) into the page so that the
// browser entrypoint can find the `initZ3` global it expects.
import { loadPyodide } from 'pyodide';
// import the built JS as a URL so Vite copies it into `dist/` and we can
// load it at runtime. The `?url` suffix tells Vite to treat it as an asset.
import z3BuiltUrl from 'z3-solver/build/z3-built.js?url';
// Also import the wasm so Vite copies it to the build output (it will be
// located next to z3-built.js so the loader's locateFile() can find it).
//import z3WasmUrl from 'z3-solver/build/z3-built.wasm?url';

const OUT = document.getElementById('output');
const runBtn = document.getElementById('run');

function log(...m) {
  OUT.textContent += '\n' + m.map(String).join(' ');
}

async function runDemo() {
  OUT.textContent = 'Initializing Pyodide and Z3...';

  // Initialize Pyodide (Python runtime compiled to WASM)
  // NOTE: keep this version in sync with the pyodide package installed in `package.json`.
  // A version mismatch will throw an error like:
  // "Pyodide version does not match: '0.23.4' <==> '0.23.2'"
  // Update the URL below to the version you have installed (e.g. v0.23.4).
  let pyodide;
  try {
    pyodide = await loadPyodide({
      indexURL: 'https://cdn.jsdelivr.net/pyodide/v0.23.4/full/',
      stdout: (s) => { OUT.textContent += '\n' + s },
      stderr: (s) => { OUT.textContent += '\n[stderr] ' + s }
    });
  } catch (e) {
    OUT.textContent += '\nError initializing Pyodide: ' + e;
    console.error(e);
    throw e;
  }

  // Initialize Z3 (WASM) via the npm package. The package loads Z3's WASM and returns a helper API.
  // API surface varies between versions; the wrapper below is intentionally small and defensive to be
  // easy to modify if needed.
  let Z3;
  let Context;
  try {
    // dynamically import z3-solver, preferring the browser entrypoint if available.
    // Some builds expect a `global` variable to exist (Node-style). In browsers
    // `global` is not defined, so define it to point to globalThis for the
    // library's initialization code.
    if (typeof global === 'undefined') {
      try { globalThis.global = globalThis; } catch (e) { /* ignore */ }
    }

      // Ensure the Module.locateFile points to the copied wasm URL. The Emscripten
      // loader will call locateFile('z3-built.wasm') (or similar) to fetch the
      // wasm. Vite renames assets to hashed filenames; we imported `z3WasmUrl`
      // above so we can return the correct hashed URL here.
      globalThis.Module = globalThis.Module || {};
      globalThis.Module.locateFile = (path) => {
        // If Emscripten asks for a wasm file, return the hashed wasm URL we
        // imported so the request succeeds.
        if (path.endsWith('.wasm')) return z3WasmUrl;
        return path;
      };

      // If the emscripten-generated z3-built.js hasn't loaded yet, inject it as a
      // script. We imported z3BuiltUrl above with `?url` so the file will be
      // copied to `dist/` at build time and this URL will point to it.
      if (typeof global.initZ3 === 'undefined') {
        OUT.textContent += '\nLoading z3-built.js...';
        await new Promise((resolve, reject) => {
          const s = document.createElement('script');
          s.src = z3BuiltUrl;
          s.onload = () => resolve();
          s.onerror = (e) => reject(new Error('Failed to load z3-built.js: ' + e));
          document.head.appendChild(s);
        });
        OUT.textContent += '\nLoaded z3-built.js';
      }

      // Import the package (will select browser build via package.json "browser" field).
      const pkg = await import('z3-solver');
      const initZ3 = pkg.init || pkg.default || pkg;

      // z3-solver exports an `init` function that returns the runtime bindings
      const res = await initZ3();
    Z3 = res.Z3;
    Context = res.Context;
    OUT.textContent += '\nZ3 initialized.';
    console.log('Z3 initialized', { Z3, Context });
  } catch (e) {
    let hint = '';
    const msg = String(e && e.message ? e.message : e);
    if (/SharedArrayBuffer|COOP|COEP|Cross-Origin/i.test(msg)) {
      hint = '\nHint: Z3 uses WebAssembly threads and requires SharedArrayBuffer and COOP/COEP headers. See README for troubleshooting.';
    }
    OUT.textContent += '\nError initializing Z3: ' + e + hint;
    console.error('Z3 init failed', e);
    throw e;
  }

  // A tiny wrapper that exposes a couple of useful operations to Python using the
  // library's high-level Context API.
  const jsz3 = {
    _inited: false,
    _ctxApi: null, // object returned by `new Context('name')`
    _solver: null,
    _vars: {},

    init() {
      if (this._inited) return;
      // Create a new high-level context API container
      this._ctxApi = new Context('main');
      const { Solver } = this._ctxApi;
      this._solver = new Solver();
      this._inited = true;
    },

    declare_int(name) {
      this.init();
      const { Int } = this._ctxApi;
      const v = Int.const(name);
      this._vars[name] = v;
      return name;
    },

    // Add an equality between sum(vars...) and a constant value
    add_eq_sum(varNames, value) {
      this.init();
      const parts = varNames.map(n => this._vars[n]);
      if (parts.includes(undefined)) throw new Error('Unknown variable in add_eq_sum');
      let sumExpr = parts.reduce((a, b) => a.add(b));
      this._solver.add(sumExpr.eq(value));
    },

    add_gt(varName, value) {
      this.init();
      const v = this._vars[varName];
      if (!v) throw new Error('Unknown var in add_gt');
      this._solver.add(v.gt(value));
    },

    async check() {
      this.init();
      const r = await this._solver.check();
      return String(r).toLowerCase().startsWith('sat');
    },

    async model() {
      this.init();
      const m = this._solver.model();
      const out = {};
      for (const [name, v] of Object.entries(this._vars)) {
        try {
          const val = m.eval ? m.eval(v, true) : null;
          out[name] = val ? (val.toString ? val.toString() : val) : null;
        } catch (e) {
          out[name] = null;
        }
      }
      return out;
    }
  };

  // Register the bridge so Python code can 'import jsz3'
  pyodide.registerJsModule('jsz3', jsz3);

  // A small Python snippet that uses the JS module
  const python = `
import jsz3
import asyncio

async def main():
    jsz3.init()
    jsz3.declare_int('x')
    jsz3.declare_int('y')
    jsz3.add_eq_sum(['x', 'y'], 10)
    jsz3.add_gt('x', 3)
    sat = await jsz3.check()
    print('satisfiable=', sat)
    model = await jsz3.model()
    print('model=', model)

asyncio.run(main())
`;

  log('Running Python snippet...');
  try {
    // run and capture stdout via Python's print which goes to browser console by default
    await pyodide.runPythonAsync(python, { globals: pyodide.globals });
    log('Python finished. See console for detailed output.');
  } catch (err) {
    log('Error running Python:', err);
    console.error(err);
  }
}

runBtn.addEventListener('click', () => {
  runBtn.disabled = true;
  runDemo().finally(() => (runBtn.disabled = false));
});
