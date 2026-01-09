# NOT WORKING

# Pyodide + Z3 Proof of Concept

This small proof-of-concept demonstrates running Python in the browser (Pyodide/WASM) and interacting with Z3 (WASM) from Python via a small JavaScript bridge.

Key ideas:
- Z3 runs as WebAssembly via the `z3-solver` npm package (bundled at build time).
- Pyodide runs Python in the browser and can call back to JS using `registerJsModule`.

Quick start (development):

1. Install deps

   npm ci

2. Run dev server

   npm run dev

3. Open http://localhost:5173 and click "Run demo".

Build for production

  npm run build

The `dist` folder can be deployed to GitHub Pages. A GitHub Actions workflow is provided to build and publish to the `gh-pages` branch automatically on pushes to `main`.

To publish the site via GitHub Pages:

1. Push this repo to GitHub (main branch).
2. Actions will build and publish to the `gh-pages` branch automatically (the workflow uses the built-in `GITHUB_TOKEN`).
3. In your repository settings -> Pages, set the source to "Deploy from a branch" and choose the `gh-pages` branch (or use the default Pages configuration if GitHub set it up automatically).

Notes

- The JS↔Python bridge (`jsz3`) is intentionally minimal and defensive because the `z3-solver` package exposes a few different APIs depending on the release. If an API mismatch occurs, inspect `src/main.js` and adapt the small wrapper methods (`declare_int`, `add_eq_sum`, `add_gt`, `check`, `model`).
- If you see an error like `Pyodide version does not match: '0.23.4' <==> '0.23.2'`, update the `indexURL` in `src/main.js` to match the installed pyodide version (or pin the version in `package.json`). The demo now uses `v0.23.4`.

Browser-specific notes (SharedArrayBuffer / COOP/COEP)

- Z3's WASM build uses threads and therefore requires SharedArrayBuffer support in the browser. That in turn requires serving pages with the Cross-Origin-Opener-Policy and Cross-Origin-Embedder-Policy headers (COOP/COEP). If you see errors mentioning `SharedArrayBuffer`, `COOP` or `COEP`, you'll need to serve the site with those headers. See the z3-solver README for details and the `coi-serviceworker` trick for GitHub Pages if you cannot set headers at the host level.
- For local development you can add the headers in a small static server (Express/serve + custom headers) or test in an environment that supports SharedArrayBuffer without COOP/COEP. The demo prints a helpful hint to the page if such an error occurs.
 - For local development you can add the headers in a small static server (Express/serve + custom headers) or test in an environment that supports SharedArrayBuffer without COOP/COEP. The demo prints a helpful hint to the page if such an error occurs. A convenience script is provided:

      npm run build && npm run serve-headers

   This serves `dist/` with the required headers so you can test Z3's threaded WASM locally.

Module/entrypoint

- The demo injects the Emscripten-generated `z3-built.js` into the page (copied into `dist/` at build time) and then imports `z3-solver`. This ensures the browser build can find the `initZ3` global that it expects and the `z3-built.wasm` is available next to the script.
- This is a proof-of-concept; extend by exposing more Z3 functionality into the `jsz3` module for richer Python-side modeling.
