---
# Feel free to add content and custom Front Matter to this file.
# To modify the layout, see https://jekyllrb.com/docs/themes/#overriding-theme-defaults

layout: home
title: Foundation of Science
---

<style>
.level-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 20px;
    margin-bottom: 2rem;
}
.level-card {
    display: block;
    background: #f8f9fa;
    border: 1px solid #dee2e6;
    border-radius: 8px;
    padding: 1.5rem;
    text-decoration: none !important;
    color: inherit;
    transition: transform 0.2s, box-shadow 0.2s;
}
.level-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    background: white;
}
.level-name {
    display: block;
    font-weight: bold;
    font-size: 1.1em;
    margin-bottom: 0.5rem;
    color: #2c3e50;
}
.level-meta {
    display: block;
    font-size: 0.85em;
    color: #6c757d;
}
.warning-box {
    background: #fff3cd;
    border: 1px solid #ffeeba;
    padding: 1rem;
    border-radius: 4px;
    margin-top: 2rem;
    font-size: 0.9em;
}
</style>

<div style="text-align: center; margin-bottom: 3rem;">
    <p style="font-size: 1.25rem; color: #555;">
        Explore unknown universes. Reverse-engineer physical laws. Write code.
    </p>
</div>

<div class="warning-box">
    <strong>⚠️ Security Note:</strong> Links to the game levels run code in your browser. Be careful when you get an external link to this page or load a custom level
</div>

### 🛠️ Prerequisites

To play, you are the scientist. You will need:

- **Python**: Basic syntax and logic.
- **NumPy**: Only needed later, but helpful from the beginning (i.e. `np.isclose`).

### 🔁 Loading time

The first time you open a level, loading time is usually significant; for subsequent levels, it should be much quicker.

---

### 🟢 Tutorial & Basics

_Start here. Simple Introduction challenges._

<div class="level-grid">
    <a href="marimo/game_tutorial.html" class="level-card">
        <span class="level-name">Euclidean (Tutorial)</span>
        <span class="level-meta">The familiar flat world.</span>
    </a>
    <a href="marimo/game_interface.html?level=Elevator" class="level-card">
        <span class="level-name">Elevator</span>
        <span class="level-meta">Going up or down?</span>
    </a>
    <a href="marimo/game_interface.html?level=SimpleTime" class="level-card">
        <span class="level-name">Simple Time</span>
        <span class="level-meta">Limited Freedom</span>
    </a>
</div>

### 🔵 Geometry Levels

_Requires knowledge of trigonometry (sin, cos) and exponentials._

<div class="level-grid">
    <a href="marimo/game_interface.html?level=Spherical" class="level-card">
        <span class="level-name">Spherical</span>
        <span class="level-meta">Curved space.</span>
    </a>
</div>

### 🟣 Puzzle Levels

_Logic puzzles disguised as physics._

<div class="level-grid">
    <a href="marimo/game_interface.html?level=EverythingRandom" class="level-card">
        <span class="level-name">Everything Random</span>
        <span class="level-meta">Does chaos have a pattern?</span>
    </a>
</div>

<!--<div class="level-grid">
    <a href="marimo/game_interface.html?level=NonUniqueODE" class="level-card">
        <span class="level-name">Parabel</span>
        <span class="level-meta">Just another x²?</span>
    </a>
</div>-->

### 🟠 Community & Custom

_Play levels created by others._

<div class="level-grid">
    <a href="marimo/game_interface.html?custom=true" class="level-card" style="border-left: 4px solid #ffc107;">
        <span class="level-name">Load Custom Level</span>
        <span class="level-meta">Paste base64 level code.</span>
    </a>
</div>
