# enable venv with marimo installed
cd foundation-of-science
bundle exec jekyll build
marimo export html-wasm game_interface.py -o _site/marimo/game_interface.html --mode run -f
cp ../game_backend.py _site/marimo/
python -m http.server --dir _site