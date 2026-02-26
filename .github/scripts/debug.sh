# enable venv with marimo installed
cd foundation-of-science
bundle exec jekyll build
marimo export html-wasm game_interface.py -o _site/marimo/game_interface.html --mode run -f
marimo export html-wasm game_interface_obs.py -o _site/marimo/game_interface_obs.html --mode run -f
marimo export html-wasm game_tutorial.py -o _site/marimo/game_tutorial.html --mode run -f
cp ../game_backend.py _site/marimo/
python -m http.server --dir _site