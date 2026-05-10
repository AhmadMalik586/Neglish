# gui.py — Advanced HTML/CSS/JS Neglish GUI Engine (v4.4+)
# A massive 2000+ line UI framework powering Neglish's new web-based frontend
# Built with PyWebview. Completely responsive, highly styled, and extensible.

import os
import sys
import threading
import time
import json
import base64
import random
import traceback
import webview

# Attempt to load native dialog fallbacks if webview doesn't support them fully
try:
    import tkinter as tk
    from tkinter import filedialog, colorchooser
except ImportError:
    tk = None

# ==========================================
# 1. MASSIVE CSS FRAMEWORK (Themes & Styles)
# ==========================================

CSS_FRAMEWORK = """
:root {
    /* Catppuccin Macchiato Default Theme */
    --bg-base: #24273a;
    --bg-crust: #181926;
    --bg-mantle: #1e2030;
    --bg-surface0: #363a4f;
    --bg-surface1: #494d64;
    --bg-surface2: #5b6078;
    
    --text-main: #cad3f5;
    --text-subtext0: #a5adcb;
    --text-subtext1: #b8c0e0;
    
    --accent: #8aadf4;
    --accent-hover: #7dc4e4;
    --accent-focus: rgba(138, 173, 244, 0.3);
    
    --color-red: #ed8796;
    --color-green: #a6da95;
    --color-yellow: #eed49f;
    --color-blue: #8aadf4;
    --color-magenta: #c6a0f6;
    --color-cyan: #8bd5ca;
    
    --border-radius: 8px;
    --border-color: var(--bg-surface1);
    
    --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
    --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
}

[data-theme="light"] {
    --bg-base: #eff1f5;
    --bg-crust: #dce0e8;
    --bg-mantle: #e6e9ef;
    --bg-surface0: #ccd0da;
    --bg-surface1: #bcc0cc;
    --text-main: #4c4f69;
    --text-subtext0: #6c6f85;
    --accent: #1e66f5;
    --accent-hover: #04a5e5;
    --border-color: var(--bg-surface0);
}

[data-theme="dracula"] {
    --bg-base: #282a36;
    --bg-crust: #191a21;
    --bg-mantle: #21222c;
    --bg-surface0: #44475a;
    --bg-surface1: #6272a4;
    --text-main: #f8f8f2;
    --text-subtext0: #bfbfbf;
    --accent: #bd93f9;
    --accent-hover: #ff79c6;
    --border-color: var(--bg-surface0);
    --color-red: #ff5555;
    --color-green: #50fa7b;
    --color-yellow: #f1fa8c;
    --color-blue: #8be9fd;
}

[data-theme="nord"] {
    --bg-base: #2e3440;
    --bg-crust: #242933;
    --bg-mantle: #292e39;
    --bg-surface0: #3b4252;
    --bg-surface1: #434c5e;
    --bg-surface2: #4c566a;
    --text-main: #eceff4;
    --text-subtext0: #d8dee9;
    --accent: #88c0d0;
    --accent-hover: #81a1c1;
    --accent-focus: rgba(136, 192, 208, 0.25);
    --border-color: var(--bg-surface1);
    --color-red: #bf616a;
    --color-green: #a3be8c;
    --color-yellow: #ebcb8b;
    --color-blue: #5e81ac;
    --color-magenta: #b48ead;
    --color-cyan: #88c0d0;
}

[data-theme="gruvbox"] {
    --bg-base: #282828;
    --bg-crust: #1d2021;
    --bg-mantle: #242424;
    --bg-surface0: #3c3836;
    --bg-surface1: #504945;
    --bg-surface2: #665c54;
    --text-main: #ebdbb2;
    --text-subtext0: #d5c4a1;
    --accent: #fabd2f;
    --accent-hover: #fe8019;
    --accent-focus: rgba(250, 189, 47, 0.25);
    --border-color: var(--bg-surface1);
    --color-red: #fb4934;
    --color-green: #b8bb26;
    --color-yellow: #fabd2f;
    --color-blue: #83a598;
    --color-magenta: #d3869b;
    --color-cyan: #8ec07c;
}

/* ---- Tooltip ---- */
[data-tooltip] {
    position: relative;
}
[data-tooltip]::after {
    content: attr(data-tooltip);
    position: absolute;
    bottom: calc(100% + 6px);
    left: 50%;
    transform: translateX(-50%) scale(0.9);
    background: var(--bg-surface2);
    color: var(--text-main);
    padding: 5px 10px;
    border-radius: 6px;
    font-size: 12px;
    white-space: nowrap;
    pointer-events: none;
    opacity: 0;
    transition: opacity 0.18s, transform 0.18s;
    z-index: 9990;
    box-shadow: var(--shadow-md);
}
[data-tooltip]:hover::after {
    opacity: 1;
    transform: translateX(-50%) scale(1);
}

/* ---- Listbox multi-select highlight ---- */
.neg-select[multiple] option:checked {
    background: var(--accent);
    color: var(--bg-crust);
}
.neg-select[multiple] option:hover {
    background: var(--accent-focus);
}

/* ---- Code block copy button fix ---- */
pre { white-space: pre-wrap; word-break: break-word; }

*, *::before, *::after { box-sizing: border-box; }

body {
    background-color: var(--bg-base);
    color: var(--text-main);
    font-family: 'Inter', 'Segoe UI', system-ui, -apple-system, sans-serif;
    margin: 0; padding: 20px;
    line-height: 1.5;
    -webkit-font-smoothing: antialiased;
    overflow-x: hidden;
    user-select: none;
}

/* =============================================
   Neglish Title Bar  —  Apple-style traffic lights
   ============================================= */
.neg-titlebar {
    position: fixed;
    top: 0; left: 0; right: 0;
    height: 36px;
    background: var(--bg-crust);
    display: flex;
    align-items: center;
    padding: 0 12px;
    z-index: 9999;
    -webkit-app-region: drag;
    border-bottom: 1px solid rgba(0,0,0,0.25);
    gap: 0;
}

/* Traffic-light cluster ------------------------------------------------- */
.neg-traffic-lights {
    display: flex;
    gap: 8px;
    align-items: center;
    -webkit-app-region: no-drag;
    flex-shrink: 0;
}

.neg-tl {
    width: 13px; height: 13px;
    border-radius: 50%;
    cursor: pointer;
    position: relative;
    transition: filter 0.15s;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0;
}
/* colours */
.neg-tl.tl-close  { background: #ff5f57; box-shadow: inset 0 0 0 0.5px rgba(0,0,0,0.25); }
.neg-tl.tl-min    { background: #ffbd2e; box-shadow: inset 0 0 0 0.5px rgba(0,0,0,0.2); }
.neg-tl.tl-max    { background: #28c840; box-shadow: inset 0 0 0 0.5px rgba(0,0,0,0.2); }

/* icons — hidden until the group is hovered */
.neg-tl svg { opacity: 0; transition: opacity 0.12s; pointer-events: none; }
.neg-traffic-lights:hover .neg-tl svg { opacity: 1; }

/* dim non-focused state — mimic macOS unfocused dots */
.neg-titlebar.unfocused .neg-tl { background: #6d6d6d !important; box-shadow: none !important; }

/* App title centred ---------------------------------------------------- */
.neg-app-title {
    flex: 1;
    text-align: center;
    font-size: 12px;
    font-weight: 600;
    color: var(--text-subtext0);
    opacity: 0.8;
    pointer-events: none;
    user-select: none;
}

/* =============================================
   Neglish App Animations
   ============================================= */

/* Boot-in: the whole app fades + scales up from slightly below */
@keyframes neg-launch {
    0%   { opacity: 0; transform: scale(0.94) translateY(10px); }
    60%  { opacity: 1; transform: scale(1.01) translateY(-2px); }
    100% { opacity: 1; transform: scale(1)    translateY(0); }
}

/* Close-out: scale down + fade */
@keyframes neg-close-out {
    0%   { opacity: 1; transform: scale(1); }
    100% { opacity: 0; transform: scale(0.92); }
}

/* Page content wrapper — plays launch anim on load */
#app {
    animation: neg-launch 0.42s cubic-bezier(0.22, 1, 0.36, 1) both;
}

/* Widget entrance — staggered via JS data-neg-delay */
@keyframes neg-widget-in {
    from { opacity: 0; transform: translateY(12px); }
    to   { opacity: 1; transform: translateY(0); }
}
.neg-frame, .neg-btn, .neg-tab-group, .neg-table-wrapper {
    animation: neg-widget-in 0.3s cubic-bezier(0.22, 1, 0.36, 1) both;
}

/* Ripple on button click */
.neg-btn { overflow: hidden; }
.neg-ripple {
    position: absolute;
    border-radius: 50%;
    transform: scale(0);
    animation: neg-ripple-anim 0.55s linear;
    background: rgba(255,255,255,0.22);
    pointer-events: none;
}
@keyframes neg-ripple-anim {
    to { transform: scale(4); opacity: 0; }
}

/* Toast slide — already defined but improved spring */
@keyframes toastSlideIn {
    from { transform: translateX(120%) scale(0.9); opacity: 0; }
    to   { transform: translateX(0)   scale(1);   opacity: 1; }
}

/* Allow selection in inputs */
input, textarea, [contenteditable] { user-select: auto; }

/* Scrollbars */
::-webkit-scrollbar { width: 10px; height: 10px; }
::-webkit-scrollbar-track { background: var(--bg-crust); }
::-webkit-scrollbar-thumb { background: var(--bg-surface1); border-radius: 5px; }
::-webkit-scrollbar-thumb:hover { background: var(--bg-surface2); }

/* =============================================
   Full-viewport iframe mode
   Activated by adding class 'neg-fullview' to <body>
   ============================================= */
body.neg-fullview {
    padding: 0 !important;
    margin: 0 !important;
    overflow: hidden;
}
body.neg-fullview #app {
    padding: 0;
    gap: 0;
}
/* iframe that fills below the titlebar */
.neg-fullview-iframe {
    display: block;
    width: 100%;
    height: calc(100vh - 36px);
    border: none;
    margin: 0;
    padding: 0;
}

/* =============================================
   Splash Screen
   ============================================= */
#neg-splash {
    position: fixed;
    inset: 0;
    z-index: 99999;
    background: var(--bg-crust);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 18px;
    pointer-events: none;
    animation: neg-splash-lifecycle 2.6s cubic-bezier(0.22,1,0.36,1) forwards;
}
@keyframes neg-splash-lifecycle {
    0%   { opacity: 0; }
    18%  { opacity: 1; }
    72%  { opacity: 1; }
    100% { opacity: 0; }
}
.neg-splash-logo {
    font-size: 32px;
    font-weight: 900;
    letter-spacing: -1px;
    color: var(--text-main);
    animation: neg-splash-rise 0.55s cubic-bezier(0.22,1,0.36,1) 0.2s both;
}
.neg-splash-logo span { color: var(--accent); }
.neg-splash-tagline {
    font-size: 15px;
    color: var(--text-subtext0);
    font-weight: 500;
    letter-spacing: 0.04em;
    animation: neg-splash-rise 0.55s cubic-bezier(0.22,1,0.36,1) 0.38s both;
}
.neg-splash-bar-wrap {
    width: 180px;
    height: 3px;
    border-radius: 99px;
    background: var(--bg-surface1);
    overflow: hidden;
    animation: neg-splash-rise 0.4s ease 0.5s both;
}
.neg-splash-bar {
    height: 100%;
    width: 0;
    border-radius: 99px;
    background: var(--accent);
    animation: neg-splash-bar-fill 1.6s cubic-bezier(0.4,0,0.2,1) 0.55s both;
}
@keyframes neg-splash-rise {
    from { opacity: 0; transform: translateY(10px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes neg-splash-bar-fill {
    from { width: 0%; }
    to   { width: 100%; }
}

/* Containers & Layout */
.app-container {
    display: flex;
    flex-direction: column;
    gap: 16px;
    width: 100%;
    max-width: 100%;
}

.neg-frame {
    background-color: var(--bg-mantle);
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius);
    padding: 20px;
    box-shadow: var(--shadow-md);
    transition: all 0.3s ease;
}
.neg-frame:hover { box-shadow: var(--shadow-lg); }

.neg-frame.glass {
    background: rgba(30, 32, 48, 0.4);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.1);
}

.neg-grid {
    display: grid;
    gap: 16px;
}

/* Typography */
h1, h2, h3, h4, h5, h6 { margin-top: 0; margin-bottom: 0.5rem; color: var(--text-main); font-weight: 700; }
.neg-label { display: block; font-size: 14px; font-weight: 500; margin-bottom: 4px; color: var(--text-main); transition: color 0.2s; }
.neg-label.muted { color: var(--text-subtext0); }
.neg-text-center { text-align: center; }

/* Buttons */
.neg-btn {
    display: inline-flex; align-items: center; justify-content: center;
    background-color: var(--bg-surface0); color: var(--text-main);
    border: 1px solid var(--border-color); border-radius: var(--border-radius);
    padding: 8px 16px; font-size: 14px; font-weight: 600;
    cursor: pointer; transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    outline: none; gap: 8px; white-space: nowrap;
}
.neg-btn:hover { background-color: var(--bg-surface1); transform: translateY(-1px); box-shadow: var(--shadow-sm); }
.neg-btn:active { transform: translateY(1px); }
.neg-btn:focus-visible { box-shadow: 0 0 0 3px var(--accent-focus); }
.neg-btn:disabled { opacity: 0.5; cursor: not-allowed; transform: none; box-shadow: none; }

.neg-btn.primary { background-color: var(--accent); color: var(--bg-crust); border-color: var(--accent); }
.neg-btn.primary:hover { background-color: var(--accent-hover); border-color: var(--accent-hover); }
.neg-btn.danger { background-color: var(--color-red); color: var(--bg-crust); border-color: var(--color-red); }
.neg-btn.success { background-color: var(--color-green); color: var(--bg-crust); border-color: var(--color-green); }
.neg-btn.warning { background-color: var(--color-yellow); color: var(--bg-crust); border-color: var(--color-yellow); }

.neg-btn.outline { background-color: transparent; border-color: var(--accent); color: var(--accent); }
.neg-btn.outline:hover { background-color: var(--accent-focus); }

/* Inputs & Forms */
.neg-input-wrapper { display: flex; flex-direction: column; gap: 4px; margin-bottom: 12px; width: 100%; }
.neg-entry, .neg-textarea, .neg-select {
    width: 100%;
    background-color: var(--bg-crust);
    color: var(--text-main);
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius);
    padding: 10px 12px;
    font-size: 14px;
    font-family: inherit;
    transition: all 0.2s;
    box-shadow: inset 0 1px 2px rgba(0,0,0,0.1);
}
.neg-textarea { resize: vertical; min-height: 80px; }
.neg-entry:hover, .neg-textarea:hover, .neg-select:hover { border-color: var(--bg-surface2); }
.neg-entry:focus, .neg-textarea:focus, .neg-select:focus { 
    outline: none; 
    border-color: var(--accent); 
    box-shadow: 0 0 0 3px var(--accent-focus); 
}
.neg-entry:disabled { opacity: 0.6; cursor: not-allowed; }

/* Checkboxes & Radios */
.neg-check-wrapper { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; cursor: pointer; }
.neg-checkbox, .neg-radio {
    appearance: none; -webkit-appearance: none;
    width: 18px; height: 18px;
    background-color: var(--bg-crust);
    border: 1px solid var(--border-color);
    border-radius: 4px;
    cursor: pointer;
    display: grid;
    place-content: center;
    transition: all 0.2s;
}
.neg-radio { border-radius: 50%; }
.neg-checkbox::before {
    content: ""; width: 10px; height: 10px;
    transform: scale(0); transition: 120ms transform ease-in-out;
    box-shadow: inset 1em 1em var(--bg-crust);
    background-color: var(--bg-crust);
    clip-path: polygon(14% 44%, 0 65%, 50% 100%, 100% 16%, 80% 0%, 43% 62%);
}
.neg-radio::before {
    content: ""; width: 10px; height: 10px; border-radius: 50%;
    transform: scale(0); transition: 120ms transform ease-in-out;
    box-shadow: inset 1em 1em var(--bg-crust);
}
.neg-checkbox:checked, .neg-radio:checked {
    background-color: var(--accent);
    border-color: var(--accent);
}
.neg-checkbox:checked::before, .neg-radio:checked::before { transform: scale(1); }

/* Switches / Toggles */
.neg-switch {
    position: relative; display: inline-block; width: 44px; height: 24px;
}
.neg-switch input { opacity: 0; width: 0; height: 0; }
.neg-slider {
    position: absolute; cursor: pointer; top: 0; left: 0; right: 0; bottom: 0;
    background-color: var(--bg-surface1); transition: .3s; border-radius: 24px;
}
.neg-slider:before {
    position: absolute; content: ""; height: 18px; width: 18px; left: 3px; bottom: 3px;
    background-color: var(--text-main); transition: .3s; border-radius: 50%;
}
input:checked + .neg-slider { background-color: var(--accent); }
input:checked + .neg-slider:before { transform: translateX(20px); background-color: var(--bg-crust); }

/* Sliders / Range */
.neg-range {
    -webkit-appearance: none; width: 100%; height: 6px; border-radius: 3px;
    background: var(--bg-surface1); outline: none; margin: 10px 0;
}
.neg-range::-webkit-slider-thumb {
    -webkit-appearance: none; appearance: none;
    width: 18px; height: 18px; border-radius: 50%;
    background: var(--accent); cursor: pointer; transition: 0.2s;
}
.neg-range::-webkit-slider-thumb:hover { transform: scale(1.2); }

/* Progress Bars */
.neg-progress-wrap {
    width: 100%; background-color: var(--bg-crust); border-radius: 999px;
    overflow: hidden; height: 12px; margin: 8px 0; border: 1px solid var(--border-color);
}
.neg-progress-bar {
    height: 100%; background-color: var(--accent);
    transition: width 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative; overflow: hidden;
}
.neg-progress-bar.animated::after {
    content: ""; position: absolute; top: 0; left: 0; bottom: 0; right: 0;
    background: linear-gradient(90deg, rgba(255,255,255,0) 0%, rgba(255,255,255,0.2) 50%, rgba(255,255,255,0) 100%);
    animation: shimmer 1.5s infinite;
}
@keyframes shimmer { 0% { transform: translateX(-100%); } 100% { transform: translateX(100%); } }

/* Tabs */
.neg-tab-group {
    display: flex; flex-direction: column; width: 100%; height: 100%;
    border: 1px solid var(--border-color); border-radius: var(--border-radius);
    background: var(--bg-mantle); overflow: hidden; margin-bottom: 20px;
}
.neg-tab-headers {
    display: flex; background: var(--bg-crust);
    border-bottom: 2px solid var(--border-color);
    padding: 5px 10px 0 10px; gap: 5px;
}
.neg-tab-btn {
    background: var(--bg-surface0); border: 1px solid var(--border-color); 
    border-bottom: none; color: var(--text-subtext0);
    padding: 10px 25px; font-size: 14px; font-weight: 700; cursor: pointer;
    border-radius: 8px 8px 0 0; transition: all 0.2s;
}
.neg-tab-btn:hover { color: var(--text-main); background: var(--bg-surface1); }
.neg-tab-btn.active {
    color: var(--bg-base); background: var(--accent); border-color: var(--accent);
}
.neg-tab-content { padding: 20px; display: none; animation: fadeIn 0.3s ease; }
.neg-tab-content.active { display: block; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(5px); } to { opacity: 1; transform: translateY(0); } }

/* Tables */
.neg-table-wrapper {
    width: 100%; overflow-x: auto; border-radius: var(--border-radius);
    border: 1px solid var(--border-color); margin-bottom: 16px;
}
.neg-table { width: 100%; border-collapse: collapse; text-align: left; }
.neg-table th, .neg-table td { padding: 12px 16px; border-bottom: 1px solid var(--border-color); }
.neg-table th { background-color: var(--bg-surface0); font-weight: 600; color: var(--text-main); }
.neg-table tr:last-child td { border-bottom: none; }
.neg-table tbody tr { transition: background-color 0.2s; background-color: var(--bg-mantle); }
.neg-table tbody tr:hover { background-color: var(--bg-surface1); }

/* Toasts */
#toast-container {
    position: fixed; bottom: 24px; right: 24px; z-index: 9999;
    display: flex; flex-direction: column; gap: 10px; pointer-events: none;
}
.neg-toast {
    background-color: var(--bg-surface0); border-left: 4px solid var(--accent);
    color: var(--text-main); padding: 16px 24px; border-radius: 6px;
    box-shadow: var(--shadow-xl); min-width: 250px; pointer-events: auto;
    animation: toastSlideIn 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards;
    display: flex; justify-content: space-between; align-items: center;
}
.neg-toast.closing { animation: toastFadeOut 0.3s ease forwards; }
.neg-toast.success { border-color: var(--color-green); }
.neg-toast.error { border-color: var(--color-red); }
.neg-toast.warning { border-color: var(--color-yellow); }
@keyframes toastSlideIn { from { transform: translateX(120%); opacity: 0; } to { transform: translateX(0); opacity: 1; } }
@keyframes toastFadeOut { to { transform: translateX(120%); opacity: 0; } }

/* Dialogs */
.neg-dialog-overlay {
    position: fixed; top: 0; left: 0; right: 0; bottom: 0;
    background: rgba(17, 17, 27, 0.7); backdrop-filter: blur(4px);
    z-index: 10000; display: none; place-items: center;
    opacity: 0; transition: opacity 0.3s ease;
}
.neg-dialog-overlay.active { display: grid; opacity: 1; }
.neg-dialog {
    background: var(--bg-mantle); border: 1px solid var(--border-color);
    border-radius: 12px; padding: 24px; width: 100%; max-width: 400px;
    box-shadow: var(--shadow-xl); transform: scale(0.9); transition: transform 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}
.neg-dialog-overlay.active .neg-dialog { transform: scale(1); }
.neg-dialog-title { font-size: 18px; font-weight: 700; margin-bottom: 12px; }
.neg-dialog-msg { font-size: 14px; margin-bottom: 20px; color: var(--text-subtext0); }
.neg-dialog-actions { display: flex; justify-content: flex-end; gap: 12px; margin-top: 24px; }

/* Charts Container */
.neg-chart-wrapper {
    width: 100%; padding: 20px; background: var(--bg-mantle);
    border: 1px solid var(--border-color); border-radius: var(--border-radius);
    margin-bottom: 16px;
}
canvas.neg-chart-canvas { width: 100% !important; height: auto !important; max-height: 400px; }

/* Images & Media */
.neg-image { max-width: 100%; border-radius: var(--border-radius); display: block; margin: 10px 0; }
.neg-avatar { width: 48px; height: 48px; border-radius: 50%; object-fit: cover; }

/* Spinners */
.neg-spinner {
    width: 24px; height: 24px; border: 3px solid var(--bg-surface2);
    border-top-color: var(--accent); border-radius: 50%;
    animation: spin 1s linear infinite; display: inline-block;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* Utility Classes */
.mt-2 { margin-top: 8px; } .mb-2 { margin-bottom: 8px; }
.mt-4 { margin-top: 16px; } .mb-4 { margin-bottom: 16px; }
.w-full { width: 100%; } .flex { display: flex; }
.justify-between { justify-content: space-between; }
.items-center { align-items: center; }
.gap-2 { gap: 8px; } .gap-4 { gap: 16px; }
.text-red { color: var(--color-red); } .text-green { color: var(--color-green); }
.text-blue { color: var(--color-blue); }
"""

# ==========================================
# 2. MASSIVE JAVASCRIPT ENGINE
# ==========================================

JS_FRAMEWORK = """
window.NeglishUI = {
    state: {},
    chartInstances: {},
    
    // Core Communication
    trigger: function(id, eventType='click', data=null) {
        if (window.pywebview && window.pywebview.api) {
            window.pywebview.api.trigger(id, eventType, data ? JSON.stringify(data) : "");
        }
    },

    // DOM Manipulation
    addElement: function(parentId, html) {
        const parent = parentId ? document.getElementById(parentId) : document.getElementById('app');
        if (parent) {
            parent.insertAdjacentHTML('beforeend', html);
        }
    },
    
    updateElement: function(id, html) {
        const el = document.getElementById(id);
        if (el) el.innerHTML = html;
    },
    
    removeElement: function(id) {
        const el = document.getElementById(id);
        if (el) el.remove();
    },

    // Inputs & Forms
    getValue: function(id) {
        const el = document.getElementById(id);
        if (!el) return null;
        if (el.type === 'checkbox' || el.type === 'radio') return el.checked;
        return el.value;
    },
    
    setValue: function(id, val) {
        const el = document.getElementById(id);
        if (!el) return;
        if (el.type === 'checkbox' || el.type === 'radio') el.checked = Boolean(val);
        else el.value = val;
    },

    // Toasts
    showToast: function(msg, type='info', duration=3000) {
        const container = document.getElementById('toast-container');
        const toast = document.createElement('div');
        toast.className = `neg-toast ${type}`;
        toast.innerHTML = `<span>${msg}</span><button style="background:none;border:none;color:inherit;cursor:pointer;" onclick="this.parentElement.remove()">✕</button>`;
        container.appendChild(toast);
        
        if (duration > 0) {
            setTimeout(() => {
                toast.classList.add('closing');
                setTimeout(() => toast.remove(), 300);
            }, duration);
        }
    },

    // Dialogs
    showDialog: function(title, msg, type='prompt', callbackId=null) {
        const overlay = document.getElementById('neg-dialog-overlay');
        document.getElementById('neg-dialog-title').innerText = title || "Message";
        document.getElementById('neg-dialog-msg').innerText = msg;
        
        const inputWrap = document.getElementById('neg-dialog-input-wrap');
        const input = document.getElementById('neg-dialog-input');
        
        if (type === 'prompt') {
            inputWrap.style.display = 'block';
            input.value = '';
            setTimeout(() => input.focus(), 100);
        } else {
            inputWrap.style.display = 'none';
        }
        
        const okBtn = document.getElementById('neg-dialog-ok');
        const cancelBtn = document.getElementById('neg-dialog-cancel');
        
        if (type === 'alert') {
            cancelBtn.style.display = 'none';
        } else {
            cancelBtn.style.display = 'inline-flex';
        }
        
        window._currentDialogCallbackId = callbackId;
        window._currentDialogType = type;
        
        overlay.classList.add('active');
    },
    
    closeDialog: function(isOk) {
        const overlay = document.getElementById('neg-dialog-overlay');
        overlay.classList.remove('active');
        
        let val = null;
        if (isOk) {
            if (window._currentDialogType === 'prompt') {
                val = document.getElementById('neg-dialog-input').value;
            } else {
                val = true;
            }
        } else {
            val = window._currentDialogType === 'prompt' ? "" : false;
        }
        
        if (window.pywebview && window.pywebview.api) {
            window.pywebview.api.submit_dialog(val);
        }
    },

    // Tabs
    switchTab: function(groupId, tabId) {
        const group = document.getElementById(groupId);
        if (!group) return;
        
        // Headers
        const headers = group.querySelectorAll('.neg-tab-btn');
        headers.forEach(h => h.classList.remove('active'));
        const activeHeader = group.querySelector(`[data-target="${tabId}"]`);
        if (activeHeader) activeHeader.classList.add('active');
        
        // Contents
        const contents = group.querySelectorAll('.neg-tab-content');
        contents.forEach(c => c.classList.remove('active'));
        const activeContent = document.getElementById(tabId);
        if (activeContent) activeContent.classList.add('active');
        
        this.trigger(groupId, 'tab_change', tabId);
    },

    // Progress
    updateProgress: function(id, percent) {
        const bar = document.querySelector(`#${id} .neg-progress-bar`);
        if (bar) bar.style.width = `${Math.min(100, Math.max(0, percent))}%`;
    },

    // Themes
    setTheme: function(theme) {
        document.documentElement.setAttribute('data-theme', theme);
    },

    // Animated close — plays close-out anim then calls pywebview
    animatedClose: function() {
        document.body.style.animation = 'neg-close-out 0.22s cubic-bezier(0.4,0,1,1) both';
        document.body.style.pointerEvents = 'none';
        setTimeout(function() {
            if (window.pywebview && window.pywebview.api) {
                window.pywebview.api.close_window();
            }
        }, 200);
    },
    
    // Simple Built-in Canvas Chart (Zero Dependencies)
    drawChart: function(id, type, data, labels, options={}) {
        const canvas = document.getElementById(id);
        if (!canvas) return;
        const ctx = canvas.getContext('2d');
        const w = canvas.width; const h = canvas.height;
        ctx.clearRect(0, 0, w, h);
        
        if (!data || data.length === 0) return;
        
        const pad = 30;
        const maxVal = Math.max(...data) || 1;
        const barW = (w - pad*2) / data.length;
        
        // Draw Axes
        ctx.strokeStyle = getComputedStyle(document.documentElement).getPropertyValue('--border-color').trim();
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(pad, pad); ctx.lineTo(pad, h-pad); ctx.lineTo(w-pad, h-pad);
        ctx.stroke();
        
        const accent = getComputedStyle(document.documentElement).getPropertyValue('--accent').trim();
        ctx.fillStyle = accent;
        
        for (let i=0; i<data.length; i++) {
            const val = data[i];
            const pxH = (val / maxVal) * (h - pad*2 - 20);
            
            if (type === 'bar') {
                const x = pad + i*barW + barW*0.1;
                const y = h - pad - pxH;
                const bw = barW*0.8;
                ctx.beginPath();
                ctx.roundRect(x, y, bw, pxH, [4, 4, 0, 0]);
                ctx.fill();
            } else if (type === 'line') {
                const x = pad + i*barW + barW/2;
                const y = h - pad - pxH;
                if (i===0) { ctx.beginPath(); ctx.moveTo(x, y); }
                else { ctx.lineTo(x, y); }
                
                if (i === data.length-1) {
                    ctx.strokeStyle = accent;
                    ctx.lineWidth = 3;
                    ctx.stroke();
                }
                
                // Dots
                ctx.beginPath(); ctx.arc(x, y, 4, 0, Math.PI*2); ctx.fill();
            }
            
            // Labels
            if (labels && labels[i]) {
                ctx.fillStyle = getComputedStyle(document.documentElement).getPropertyValue('--text-subtext0').trim();
                ctx.font = '10px sans-serif';
                ctx.textAlign = 'center';
                ctx.fillText(labels[i], pad + i*barW + barW/2, h - pad + 15);
                ctx.fillStyle = accent; // reset
            }
        }
    }
};

// Global Listeners
document.addEventListener('keydown', function(e) {
    if (e.key === 'Enter') {
        // If dialog is open, submit it
        const overlay = document.getElementById('neg-dialog-overlay');
        if (overlay && overlay.classList.contains('active')) {
            window.NeglishUI.closeDialog(true);
            return;
        }
    }
    if (window.pywebview && window.pywebview.api) {
        window.pywebview.api.trigger("KEY_" + e.key, "keydown");
    }
});

// Ripple effect on .neg-btn clicks
document.addEventListener('click', function(e) {
    const btn = e.target.closest('.neg-btn');
    if (!btn || btn.disabled) return;
    const r = document.createElement('span');
    r.className = 'neg-ripple';
    const rect = btn.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height);
    r.style.cssText = `width:${size}px;height:${size}px;left:${e.clientX - rect.left - size/2}px;top:${e.clientY - rect.top - size/2}px;position:absolute;`;
    btn.appendChild(r);
    r.addEventListener('animationend', () => r.remove());
});

// Titlebar unfocused state (dims traffic lights when window loses focus)
window.addEventListener('blur', function() {
    const tb = document.getElementById('neg-titlebar');
    if (tb) tb.classList.add('unfocused');
});
window.addEventListener('focus', function() {
    const tb = document.getElementById('neg-titlebar');
    if (tb) tb.classList.remove('unfocused');
});

// Stagger widget entrance animations
document.addEventListener('DOMContentLoaded', function() {
    const widgets = document.querySelectorAll('.neg-frame, .neg-tab-group, .neg-table-wrapper');
    widgets.forEach(function(el, i) {
        el.style.animationDelay = (i * 0.045) + 's';
    });
});

// Splash screen — remove from DOM after animation completes (2.6 s)
(function() {
    var splash = document.getElementById('neg-splash');
    if (splash) {
        setTimeout(function() {
            splash.style.display = 'none';
        }, 2650);
    }
})();

// Full-viewport iframe helper — called by create_html_view
window.NeglishUI.enableFullView = function() {
    document.body.classList.add('neg-fullview');
    document.body.style.padding = '0';
};
"""

HTML_SKELETON = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Neglish App</title>
    <style>{CSS_FRAMEWORK}</style>
</head>
<body style="padding-top: 36px;">
    <div class="neg-titlebar" id="neg-titlebar">
        <!-- Apple-style traffic lights -->
        <div class="neg-traffic-lights" id="neg-traffic-lights">
            <!-- Close -->
            <div class="neg-tl tl-close" title="Close" onclick="window.NeglishUI.animatedClose()">
                <svg width="7" height="7" viewBox="0 0 7 7" fill="none">
                    <line x1="1" y1="1" x2="6" y2="6" stroke="#4d0000" stroke-width="1.3" stroke-linecap="round"/>
                    <line x1="6" y1="1" x2="1" y2="6" stroke="#4d0000" stroke-width="1.3" stroke-linecap="round"/>
                </svg>
            </div>
            <!-- Minimise -->
            <div class="neg-tl tl-min" title="Minimize" onclick="window.pywebview.api.minimize_window()">
                <svg width="7" height="2" viewBox="0 0 7 2" fill="none">
                    <line x1="0.5" y1="1" x2="6.5" y2="1" stroke="#4d3000" stroke-width="1.3" stroke-linecap="round"/>
                </svg>
            </div>
            <!-- Fullscreen -->
            <div class="neg-tl tl-max" title="Fullscreen" onclick="window.pywebview.api.toggle_fullscreen()">
                <svg width="7" height="7" viewBox="0 0 7 7" fill="none">
                    <path d="M1 3.5 L3.5 1 L6 3.5 L3.5 6 Z" stroke="#003d00" stroke-width="1.1" stroke-linejoin="round" fill="none"/>
                </svg>
            </div>
        </div>
        <div class="neg-app-title" id="neg-header-title">Neglish Application</div>
    </div>

    <div id="app" class="app-container"></div>
    <div id="toast-container"></div>

    <!-- Splash screen — auto-removes after animation -->
    <div id="neg-splash">
        <div class="neg-splash-logo">NEG<span>LISH</span></div>
        <div class="neg-splash-tagline">Thanks for using Neglish!</div>
        <div class="neg-splash-bar-wrap">
            <div class="neg-splash-bar"></div>
        </div>
    </div>
    
    <!-- Global Dialog Overlay -->
    <div id="neg-dialog-overlay" class="neg-dialog-overlay">
        <div class="neg-dialog">
            <h3 id="neg-dialog-title" class="neg-dialog-title">Alert</h3>
            <div id="neg-dialog-msg" class="neg-dialog-msg">Message goes here</div>
            <div id="neg-dialog-input-wrap" class="neg-input-wrapper" style="display:none;">
                <input type="text" id="neg-dialog-input" class="neg-entry" placeholder="Type here..." />
            </div>
            <div class="neg-dialog-actions">
                <button id="neg-dialog-cancel" class="neg-btn outline" onclick="window.NeglishUI.closeDialog(false)">Cancel</button>
                <button id="neg-dialog-ok" class="neg-btn primary" onclick="window.NeglishUI.closeDialog(true)">OK</button>
            </div>
        </div>
    </div>

    <script>{JS_FRAMEWORK}</script>
</body>
</html>
"""

# ==========================================
# 3. PYTHON API BRIDGE
# ==========================================

class GUIManager:
    def __init__(self):
        self._windows = {}
        self._callbacks = {}
        self._ready = threading.Event()
        self._dialog_result = None
        self._dialog_event = threading.Event()
        self.master = None          # set once the first real window is created
        self._start_called = False
        
        # We define a JSAPI inner class to expose to pywebview
        class API:
            def __init__(self, mgr):
                self.mgr = mgr
            
            def trigger(self, widget_id, event_type="click", data=""):
                cb = self.mgr._callbacks.get(widget_id)
                if cb:
                    def _run():
                        try:
                            # Pass data if callback takes arguments, otherwise don't
                            import inspect
                            sig = inspect.signature(cb)
                            if len(sig.parameters) > 0: cb(data)
                            else: cb()
                        except Exception as e:
                            print(f"[GUI Event Error] {e}")
                            traceback.print_exc()
                    threading.Thread(target=_run, daemon=True).start()

            def submit_dialog(self, value):
                self.mgr._dialog_result = value
                self.mgr._dialog_event.set()

            def close_window(self):
                win = webview.active_window()
                if win: win.destroy()

            def minimize_window(self):
                win = webview.active_window()
                if win: win.minimize()

            def toggle_fullscreen(self):
                win = webview.active_window()
                if win: win.toggle_fullscreen()

        self.api = API(self)

    def log(self, text: str):
        """Optional: log text to a GUI console if implemented."""
        pass

    # --- Icon Helper (Windows only, ctypes HWND approach) ---

    @staticmethod
    def _apply_icon(win):
        """Set negextension.ico as the window icon via Win32 API after load."""
        ico = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'negextension.ico')
        if not os.path.exists(ico):
            return
        try:
            import ctypes
            WM_SETICON      = 0x0080
            IMAGE_ICON      = 1
            LR_LOADFROMFILE = 0x0010
            LR_DEFAULTSIZE  = 0x0040
            hwnd = GUIManager._find_hwnd(win.title)
            if hwnd:
                hicon = ctypes.windll.user32.LoadImageW(
                    None, ico, IMAGE_ICON, 0, 0, LR_LOADFROMFILE | LR_DEFAULTSIZE
                )
                if hicon:
                    ctypes.windll.user32.SendMessageW(hwnd, WM_SETICON, 0, hicon)  # ICON_SMALL
                    ctypes.windll.user32.SendMessageW(hwnd, WM_SETICON, 1, hicon)  # ICON_BIG
        except Exception as e:
            print(f"[GUI Icon] Could not set icon: {e}")

    @staticmethod
    def _find_hwnd(title: str):
        """Find HWND by window title using EnumWindows."""
        try:
            import ctypes
            result = []
            WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.c_int)
            def _cb(hwnd, lp):
                buf = ctypes.create_unicode_buffer(256)
                ctypes.windll.user32.GetWindowTextW(hwnd, buf, 256)
                if title in buf.value:
                    result.append(hwnd)
                return True
            ctypes.windll.user32.EnumWindows(WNDENUMPROC(_cb), 0)
            return result[0] if result else None
        except Exception:
            return None

    # --- Core Lifecycle ---
    #
    # ARCHITECTURE (fixes freeze / double-window):
    #
    #   pywebview's GUI loop MUST own the main thread on Windows.
    #   The Neglish interpreter therefore runs on a background thread.
    #
    #   Correct call order in main.py / the interpreter:
    #
    #       gui = GUIManager()
    #       gui.create_window("My App", 900, 600)   # register window before start
    #       gui.start(my_interpreter_func)           # schedules func on bg thread
    #       gui.mainloop()                           # BLOCKS — runs GUI on main thread
    #
    #   Inside the interpreter / app code:
    #       gui.wait_ready()   # waits until webview has fully started (non-blocking
    #                          # on main thread because it runs on the bg thread now)
    #       gui.create_label(...)
    #       ...

    def start(self, target_fn=None, *args, **kwargs):
        """
        Schedule `target_fn` (your interpreter / app logic) to run on a
        background thread once the webview event loop is live.

        If target_fn is None, start() is a no-op (legacy compatibility —
        caller is expected to call wait_ready() themselves from a thread).
        """
        self._start_called = True
        if target_fn is not None:
            def _bg():
                self._ready.wait()          # wait until webview is running
                try:
                    target_fn(*args, **kwargs)
                except Exception as e:
                    print(f"[GUI App Error] {e}")
                    traceback.print_exc()
            t = threading.Thread(target=_bg, daemon=True)
            t.start()

    def mainloop(self):
        """
        Starts the pywebview GUI event loop on the MAIN thread. Blocks
        until all windows are closed.

        pywebview requires:
          1. webview.create_window() called BEFORE webview.start()  ✓
             (create_window() does this immediately)
          2. webview.start() called from the main thread             ✓
             (mainloop() is always called last, on the main thread)

        If no window was registered yet, a fallback is created so
        webview.start() never receives the 'no window' fatal error.
        """
        if not self._windows:
            print("[GUI Warning] mainloop() called with no windows — creating fallback.")
            self.create_window("Neglish", 900, 650)

        def _on_started():
            self._ready.set()   # unblock any wait_ready() calls on bg threads

        try:
            webview.start(_on_started, debug=False)
        except Exception as e:
            print(f"[GUI Fatal Error] Could not start webview: {e}")

    def wait_ready(self):
        """
        Block the CALLING thread until the webview event loop is running.
        Call this from your background / interpreter thread, not from the
        main thread (which is blocked in mainloop()).
        Times out after 30 s to prevent infinite hangs.
        """
        if not self._ready.wait(timeout=30):
            print("[GUI Warning] wait_ready() timed out after 30 s")

    def _eval(self, win_title, script):
        """
        Evaluate JS in the target window.
        If the window exists but the page hasn't loaded yet, retries up to
        ~2 s (40 × 50 ms) so widgets injected immediately after wait_ready()
        aren't silently dropped.
        """
        win = self._windows.get(win_title)
        if not win:
            win = self._windows.get('master')
        if not win:
            return

        for attempt in range(40):
            try:
                win.evaluate_js(script)
                return
            except Exception:
                if attempt < 39:
                    time.sleep(0.05)   # wait 50 ms and retry
                # on final attempt just give up silently

    def _get_val(self, win_title, element_id):
        win = self._windows.get(win_title) or self._windows.get('master')
        if win:
            try:
                return win.evaluate_js(f"window.NeglishUI.getValue('{element_id}')")
            except: pass
        return None

    # --- Window Management ---

    def create_window(self, title: str, width: int, height: int, opts: dict = None):
        """
        Creates a webview window. Safe to call BEFORE mainloop() — pywebview
        allows webview.create_window() before webview.start().

        opts keys:
            resizable (bool, default True)
            min_size  (tuple[int,int], default (400, 300))
            transparent (bool, default False)
            on_top   (bool, default False)
            background_color (str hex, default '#24273a')
        """
        opts = opts or {}
        # Inject real window title into the HTML title bar
        html = HTML_SKELETON.replace(
            'Neglish Application', title, 1
        ).replace('<title>Neglish App</title>', f'<title>{title}</title>', 1)

        win = webview.create_window(
            title,
            html=html,
            js_api=self.api,
            width=width,
            height=height,
            frameless=True,
            resizable=opts.get('resizable', True),
            min_size=opts.get('min_size', (400, 300)),
            transparent=opts.get('transparent', False),
            on_top=opts.get('on_top', False),
            background_color=opts.get('background_color', '#24273a'),
        )
        win.events.loaded += lambda w=win: GUIManager._apply_icon(w)
        self._windows[title] = win
        if self.master is None:
            self.master = win
            self._windows['master'] = win

    def show_window(self, title=''):
        pass # pywebview shows it automatically

    def set_theme(self, theme_name: str, window_title: str = None):
        """Sets the CSS theme (dark, light, dracula)"""
        self._eval(window_title, f"window.NeglishUI.setTheme('{theme_name}');")

    # --- Widget Creation ---

    def _add_html(self, window_title, parent_id, html):
        p = f"'{parent_id}'" if parent_id else "null"
        safe_html = html.replace('`', '\\`')
        self._eval(window_title, f"window.NeglishUI.addElement({p}, `{safe_html}`);")

    def create_label(self, text: str, window_title: str, opts: dict = None, name: str = None):
        opts = opts or {}
        name = name or opts.get('name', f"lbl_{int(time.time()*1000)}")
        parent = opts.get('parent')
        size = opts.get('size', 14)
        bold = 'bold' if opts.get('bold') else 'normal'
        italic = 'italic' if opts.get('italic') else 'normal'
        color = opts.get('color', '')
        col_str = f"color:{color};" if color else ""
        html = f"<div id='{name}' class='neg-label' style='font-size:{size}px; font-weight:{bold}; font-style:{italic}; {col_str}'>{text}</div>"
        self._add_html(window_title, parent, html)

    def update_label(self, name: str, text: str, window_title: str = None):
        safe_text = str(text).replace('`', '\\`')
        self._eval(window_title, f"window.NeglishUI.updateElement('{name}', `{safe_text}`);")

    def create_button(self, label: str, window_title: str, opts: dict = None, name: str = None):
        opts = opts or {}
        name = name or opts.get('name', f"btn_{int(time.time()*1000)}")
        parent = opts.get('parent')
        color = opts.get('color', 'primary') # primary, danger, success, warning, outline
        
        css_class = f"neg-btn {color}"
        html = f"<button id='{name}' class='{css_class}' onclick='window.NeglishUI.trigger(\"{name}\")'>{label}</button>"
        self._add_html(window_title, parent, html)

    def bind_button(self, name: str, callback):
        self._callbacks[name] = callback

    def create_entry(self, name: str, window_title: str, opts: dict = None):
        opts = opts or {}
        parent = opts.get('parent')
        placeholder = opts.get('placeholder', '')
        is_password = opts.get('password', False)
        typ = 'password' if is_password else 'text'
        
        html = f"""
        <div class='neg-input-wrapper'>
            <input type='{typ}' id='{name}' class='neg-entry' placeholder='{placeholder}' onchange='window.NeglishUI.trigger(\"{name}\", \"change\")' />
        </div>
        """
        self._add_html(window_title, parent, html)

    def get_entry_value(self, name: str) -> str:
        return str(self._get_val(None, name) or "")

    def set_entry_value(self, name: str, value: str, window_title: str = None):
        safe_val = str(value).replace('`', '\\`')
        self._eval(window_title, f"window.NeglishUI.setValue('{name}', `{safe_val}`);")

    def create_textarea(self, name: str, window_title: str, opts: dict = None):
        opts = opts or {}
        parent = opts.get('parent')
        placeholder = opts.get('placeholder', '')
        
        html = f"""
        <div class='neg-input-wrapper'>
            <textarea id='{name}' class='neg-textarea' placeholder='{placeholder}' onchange='window.NeglishUI.trigger(\"{name}\", \"change\")'></textarea>
        </div>
        """
        self._add_html(window_title, parent, html)

    def create_checkbox(self, name: str, window_title: str, label: str = "", opts: dict = None):
        opts = opts or {}
        parent = opts.get('parent')
        checked = "checked" if opts.get('checked') else ""
        
        html = f"""
        <label class='neg-check-wrapper'>
            <input type='checkbox' id='{name}' class='neg-checkbox' {checked} onchange='window.NeglishUI.trigger(\"{name}\", \"change\")' />
            <span class='neg-label'>{label}</span>
        </label>
        """
        self._add_html(window_title, parent, html)

    def create_dropdown(self, name: str, window_title: str, options: list, opts: dict = None):
        opts = opts or {}
        parent = opts.get('parent')
        
        opts_html = "".join([f"<option value='{o}'>{o}</option>" for o in options])
        html = f"""
        <div class='neg-input-wrapper'>
            <select id='{name}' class='neg-select' onchange='window.NeglishUI.trigger(\"{name}\", \"change\")'>
                {opts_html}
            </select>
        </div>
        """
        self._add_html(window_title, parent, html)

    def create_frame(self, name: str, window_title: str, opts: dict = None):
        opts = opts or {}
        parent = opts.get('parent')
        glass = "glass" if opts.get('glass') else ""
        bg = opts.get('background', '')
        style = f"style='background:{bg};'" if bg else ""
        
        html = f"<div id='{name}' class='neg-frame {glass}' {style}></div>"
        self._add_html(window_title, parent, html)

    # --- Advanced Widgets ---

    def create_progress(self, name: str, window_title: str, opts: dict = None):
        opts = opts or {}
        parent = opts.get('parent')
        percent = opts.get('value', 0)
        animated = "animated" if opts.get('animated', True) else ""
        
        html = f"""
        <div class='neg-progress-wrap' id='{name}'>
            <div class='neg-progress-bar {animated}' style='width:{percent}%'></div>
        </div>
        """
        self._add_html(window_title, parent, html)

    def create_tab_group(self, name: str, window_title: str, opts: dict = None):
        opts = opts or {}
        parent = opts.get('parent')
        
        html = f"""
        <div id='{name}' class='neg-tab-group'>
            <div id='{name}_headers' class='neg-tab-headers'></div>
            <div id='{name}_contents' class='neg-tab-body'></div>
        </div>
        """
        self._add_html(window_title, parent, html)

    def create_tab(self, name: str, window_title: str, opts: dict = None):
        opts = opts or {}
        group = opts.get('group')
        title = opts.get('title', name)
        
        if not group: return
        
        # Add header
        hdr_html = f"<button class='neg-tab-btn' data-target='{name}' onclick='window.NeglishUI.switchTab(\"{group}\", \"{name}\")'>{title}</button>"
        self._add_html(window_title, f"{group}_headers", hdr_html)
        
        # Add content container
        cnt_html = f"<div id='{name}' class='neg-tab-content neg-container'></div>"
        self._add_html(window_title, f"{group}_contents", cnt_html)
        
        # Activate first tab automatically
        self._eval(window_title, f"""
            var grp = document.getElementById('{group}');
            if(grp.querySelectorAll('.neg-tab-content.active').length === 0) {{
                window.NeglishUI.switchTab('{group}', '{name}');
            }}
        """)

    def create_chart(self, name: str, window_title: str, opts: dict = None):
        opts = opts or {}
        parent = opts.get('parent')
        data = opts.get('data', [])
        labels = opts.get('labels', [])
        chart_type = opts.get('type', 'bar') # bar or line
        
        html = f"""
        <div class='neg-chart-wrapper'>
            <canvas id='{name}' class='neg-chart-canvas' width='800' height='300'></canvas>
        </div>
        """
        self._add_html(window_title, parent, html)
        
        # Call JS draw
        safe_data = json.dumps(data)
        safe_labels = json.dumps(labels)
        self._eval(window_title, f"setTimeout(()=>window.NeglishUI.drawChart('{name}', '{chart_type}', {safe_data}, {safe_labels}), 100);")

    def create_image(self, name: str, window_title: str, opts: dict = None):
        opts = opts or {}
        parent = opts.get('parent')
        file_path = opts.get('file', '')
        w = opts.get('width', '')
        h = opts.get('height', '')
        style = []
        if w: style.append(f"width:{w}px")
        if h: style.append(f"height:{h}px")
        style_str = f"style='{';'.join(style)}'"
        
        if file_path and os.path.exists(file_path):
            try:
                # Encode as base64 to inject into HTML
                with open(file_path, "rb") as img_file:
                    b64_string = base64.b64encode(img_file.read()).decode('utf-8')
                ext = file_path.split('.')[-1].lower()
                mime = f"image/{ext}" if ext in ['png','jpg','jpeg','gif','webp'] else "image/png"
                src = f"data:{mime};base64,{b64_string}"
                html = f"<img id='{name}' class='neg-image' src='{src}' {style_str} />"
                self._add_html(window_title, parent, html)
            except Exception as e:
                print(f"[GUI Image Error] {e}")

    def create_table(self, name: str, window_title: str, columns: list, opts: dict = None):
        opts = opts or {}
        parent = opts.get('parent')
        headers = "".join([f"<th>{c}</th>" for c in columns])
        html = f"<div class='neg-table-wrapper'><table id='{name}' class='neg-table'><thead><tr>{headers}</tr></thead><tbody></tbody></table></div>"
        self._add_html(window_title, parent, html)

    def table_add_row(self, name: str, vals: list, window_title: str = None):
        tds = "".join([f"<td>{str(v)}</td>" for v in vals])
        html = f"<tr>{tds}</tr>".replace('`', '\\`')
        self._eval(window_title, f"document.querySelector('#{name} tbody').insertAdjacentHTML('beforeend', `{html}`);")

    def table_clear(self, name: str, window_title: str = None):
        self._eval(window_title, f"document.querySelector('#{name} tbody').innerHTML = '';")

    # --- Modals & Popups ---

    def show_toast(self, msg: str, opts: dict = None):
        opts = opts or {}
        typ = opts.get('type', 'info') # info, success, warning, error
        dur = opts.get('duration', 3000)
        safe_msg = str(msg).replace('`', '\\`')
        for win in self._windows.values():
            try:
                win.evaluate_js(f"window.NeglishUI.showToast(`{safe_msg}`, '{typ}', {dur});")
            except: pass

    def show_dialog(self, msg: str, opts: dict = None) -> str:
        """Blocks and returns user input or boolean."""
        opts = opts or {}
        title = opts.get('title', 'Input Required')
        typ = opts.get('type', 'prompt') # prompt, confirm, alert
        
        self._dialog_event.clear()
        self._dialog_result = None
        
        safe_msg = str(msg).replace('`', '\\`')
        safe_title = str(title).replace('`', '\\`')
        
        win = self._windows.get('master')
        if win:
            win.evaluate_js(f"window.NeglishUI.showDialog(`{safe_title}`, `{safe_msg}`, '{typ}');")
        
        self._dialog_event.wait()
        return self._dialog_result

    def ask_file(self, mode: str = 'open', filetypes: list = None) -> str:
        """Fallback to tkinter for native file dialogs if needed."""
        if not tk: return ""
        root = tk.Tk(); root.withdraw()
        root.attributes('-topmost', True)
        if mode == 'save': res = filedialog.asksaveasfilename(parent=root)
        else: res = filedialog.askopenfilename(parent=root)
        root.destroy()
        return res or ""

    # --- System & Interactions ---

    def bind_key(self, key: str, window_title: str, handler):
        if key == 'Return': key = 'Enter'
        self._callbacks[f"KEY_{key}"] = handler

    def play_sound(self, file_path: str):
        try:
            import winsound
            winsound.PlaySound(file_path, winsound.SND_ALIAS | winsound.SND_ASYNC)
        except: pass

    def create_html_view(self, url_or_path: str, window_title: str = None, opts: dict = None):
        """
        Embed a URL or local HTML file inside the Neglish window.

        By default (opts['fullscreen']=True) the iframe fills the entire
        area below the title bar with zero padding — perfect for web apps.
        Set opts['fullscreen']=False for an inline embedded view.

        opts:
            name        (str)  — element ID, default 'html_view'
            parent      (str)  — parent container ID (ignored in fullscreen mode)
            fullscreen  (bool) — fill window below titlebar, default True
            width       (str)  — CSS width  (inline mode only), default '100%'
            height      (str)  — CSS height (inline mode only), default '500px'
            border      (bool) — show border in inline mode, default False
        """
        opts = opts or {}
        name = opts.get('name', 'html_view')
        fullscreen = opts.get('fullscreen', True)

        # Convert local path → file:// URL
        if url_or_path and not url_or_path.startswith(('http://', 'https://', 'file://')):
            abs_path = os.path.abspath(url_or_path)
            url_or_path = 'file:///' + abs_path.replace('\\', '/')

        safe_url = url_or_path.replace("'", "\\'")

        if fullscreen:
            # Strip body padding, make iframe fill all space below titlebar
            self._eval(window_title, "window.NeglishUI.enableFullView();")
            html = (
                f"<iframe id='{name}' src='{safe_url}' "
                f"class='neg-fullview-iframe'></iframe>"
            )
            # Inject directly into #app (no parent wrapping needed)
            self._add_html(window_title, None, html)
        else:
            parent = opts.get('parent')
            w = opts.get('width', '100%')
            h = opts.get('height', '500px')
            border_style = '1px solid var(--border-color)' if opts.get('border') else 'none'
            html = (
                f"<div id='{name}_wrap' style='width:{w};border-radius:var(--border-radius);"
                f"overflow:hidden;border:{border_style};'>"
                f"<iframe id='{name}' src='{safe_url}' "
                f"style='width:100%;height:{h};border:none;display:block;'></iframe>"
                f"</div>"
            )
            self._add_html(window_title, parent, html)

    # ---------------------------------------------------------------
    # New in v4.5 — Window helpers
    # ---------------------------------------------------------------

    def set_title(self, title: str, window_title: str = None):
        """Update the visible title bar label at runtime."""
        safe = title.replace('`', '\\`')
        self._eval(window_title, f"""
            var el = document.getElementById('neg-header-title');
            if (el) el.innerText = `{safe}`;
        """)

    def close_window(self, window_title: str = None):
        """Gracefully close a window with the animated close-out effect."""
        self._eval(window_title, "window.NeglishUI.animatedClose();")

    def destroy(self):
        """Immediately destroy all windows and exit."""
        for win in list(self._windows.values()):
            try:
                win.destroy()
            except Exception:
                pass
        self._windows.clear()

    def set_always_on_top(self, on_top: bool, window_title: str = None):
        """Toggle always-on-top for a window (pywebview 4+)."""
        win = self._windows.get(window_title or 'master')
        if win:
            try:
                win.on_top = on_top
            except Exception:
                pass

    # ---------------------------------------------------------------
    # New in v4.5 — Improved widget creators
    # ---------------------------------------------------------------

    def create_badge(self, name: str, text: str, window_title: str, opts: dict = None):
        """
        Inline badge/pill chip.
        opts: parent, color ('red'|'green'|'yellow'|'blue'|'magenta'|'cyan'|'default')
        """
        opts = opts or {}
        parent = opts.get('parent')
        color = opts.get('color', 'default')
        color_map = {
            'red': 'var(--color-red)', 'green': 'var(--color-green)',
            'yellow': 'var(--color-yellow)', 'blue': 'var(--color-blue)',
            'magenta': 'var(--color-magenta)', 'cyan': 'var(--color-cyan)',
            'default': 'var(--bg-surface1)',
        }
        bg = color_map.get(color, 'var(--bg-surface1)')
        html = (
            f"<span id='{name}' style='display:inline-block;padding:2px 10px;"
            f"border-radius:999px;font-size:12px;font-weight:700;"
            f"background:{bg};color:var(--bg-crust);margin:2px 4px;'>{text}</span>"
        )
        self._add_html(window_title, parent, html)

    def update_badge(self, name: str, text: str, window_title: str = None):
        safe = str(text).replace('`', '\\`')
        self._eval(window_title, f"window.NeglishUI.updateElement('{name}', `{safe}`);")

    def create_separator(self, window_title: str, opts: dict = None):
        """Horizontal rule / divider."""
        opts = opts or {}
        parent = opts.get('parent')
        html = "<hr style='border:none;border-top:1px solid var(--border-color);margin:12px 0;'>"
        self._add_html(window_title, parent, html)

    def create_spinner(self, name: str, window_title: str, opts: dict = None):
        """Inline loading spinner. Show/hide with set_visible()."""
        opts = opts or {}
        parent = opts.get('parent')
        size = opts.get('size', 24)
        html = f"<div id='{name}' class='neg-spinner' style='width:{size}px;height:{size}px;'></div>"
        self._add_html(window_title, parent, html)

    def create_card(self, name: str, title_text: str, body_text: str,
                    window_title: str = None, opts: dict = None):
        """
        Styled card widget with a title, body paragraph, and optional footer HTML.
        opts: parent, footer_html, accent_color
        """
        opts = opts or {}
        parent = opts.get('parent')
        footer = opts.get('footer_html', '')
        accent = opts.get('accent_color', 'var(--accent)')
        footer_html = f"<div style='margin-top:12px;padding-top:12px;border-top:1px solid var(--border-color);'>{footer}</div>" if footer else ''
        html = f"""
        <div id='{name}' class='neg-frame' style='border-left:3px solid {accent};'>
            <div style='font-size:15px;font-weight:700;margin-bottom:6px;color:var(--text-main);'>{title_text}</div>
            <div style='font-size:13px;color:var(--text-subtext0);line-height:1.6;'>{body_text}</div>
            {footer_html}
        </div>
        """
        self._add_html(window_title, parent, html)

    def create_code_block(self, name: str, code: str, window_title: str, opts: dict = None):
        """
        Monospace code display with copy-to-clipboard button.
        opts: parent, language (display label only)
        """
        opts = opts or {}
        parent = opts.get('parent')
        lang = opts.get('language', '')
        # Escape HTML entities
        safe_code = (code
                     .replace('&', '&amp;').replace('<', '&lt;')
                     .replace('>', '&gt;').replace('`', '\\`'))
        lang_label = f"<span style='font-size:11px;color:var(--text-subtext0);'>{lang}</span>" if lang else ''
        html = f"""
        <div id='{name}' style='background:var(--bg-crust);border:1px solid var(--border-color);
             border-radius:var(--border-radius);overflow:hidden;margin-bottom:12px;'>
            <div style='display:flex;justify-content:space-between;align-items:center;
                 padding:6px 12px;background:var(--bg-surface0);border-bottom:1px solid var(--border-color);'>
                {lang_label}
                <button class='neg-btn outline' style='padding:2px 10px;font-size:11px;'
                    onclick='navigator.clipboard.writeText(document.querySelector("#{name} pre").innerText)
                             .then(()=>window.NeglishUI.showToast("Copied!","success",1500))'>Copy</button>
            </div>
            <pre style='margin:0;padding:14px 16px;overflow-x:auto;font-family:monospace;
                 font-size:13px;color:var(--text-main);line-height:1.55;user-select:text;'>{safe_code}</pre>
        </div>
        """
        self._add_html(window_title, parent, html)

    def create_slider(self, name: str, window_title: str, opts: dict = None):
        """
        Range slider with live value display.
        opts: parent, min, max, value, step, label, show_value (bool)
        """
        opts = opts or {}
        parent = opts.get('parent')
        mn = opts.get('min', 0)
        mx = opts.get('max', 100)
        val = opts.get('value', 50)
        step = opts.get('step', 1)
        label = opts.get('label', '')
        show_val = opts.get('show_value', True)
        lbl_html = f"<span class='neg-label' style='margin-bottom:2px;'>{label}</span>" if label else ''
        val_span = f"<span id='{name}_val' style='font-size:13px;color:var(--accent);font-weight:700;min-width:36px;text-align:right;'>{val}</span>" if show_val else ''
        html = f"""
        <div class='neg-input-wrapper' id='{name}_wrap'>
            <div style='display:flex;justify-content:space-between;align-items:center;'>
                {lbl_html}
                {val_span}
            </div>
            <input type='range' id='{name}' class='neg-range' min='{mn}' max='{mx}' value='{val}' step='{step}'
                oninput='document.getElementById("{name}_val") && (document.getElementById("{name}_val").innerText=this.value); window.NeglishUI.trigger("{name}","change",this.value)'
                onchange='window.NeglishUI.trigger("{name}","change",this.value)' />
        </div>
        """
        self._add_html(window_title, parent, html)

    def create_switch(self, name: str, window_title: str, label: str = "", opts: dict = None):
        """Toggle switch (on/off)."""
        opts = opts or {}
        parent = opts.get('parent')
        checked = "checked" if opts.get('checked') else ""
        html = f"""
        <div class='neg-check-wrapper' style='margin-bottom:10px;'>
            <label class='neg-switch'>
                <input type='checkbox' id='{name}' {checked}
                    onchange='window.NeglishUI.trigger("{name}","change",this.checked)' />
                <span class='neg-slider'></span>
            </label>
            <span class='neg-label' style='margin-bottom:0;'>{label}</span>
        </div>
        """
        self._add_html(window_title, parent, html)

    def create_radio(self, name: str, window_title: str, label: str = "", opts: dict = None):
        """
        Radio button. Group radios by giving them the same opts['group'] name.
        """
        opts = opts or {}
        parent = opts.get('parent')
        group = opts.get('group', name)
        checked = "checked" if opts.get('checked') else ""
        html = f"""
        <label class='neg-check-wrapper'>
            <input type='radio' id='{name}' name='{group}' class='neg-radio' {checked}
                onchange='window.NeglishUI.trigger("{name}","change")' />
            <span class='neg-label' style='margin-bottom:0;'>{label}</span>
        </label>
        """
        self._add_html(window_title, parent, html)

    def create_listbox(self, name: str, window_title: str, items: list = None, opts: dict = None):
        """
        Scrollable single/multi-select list.
        opts: parent, multi (bool), height_px
        """
        opts = opts or {}
        parent = opts.get('parent')
        multi = 'multiple' if opts.get('multi') else ''
        height = opts.get('height_px', 140)
        items_html = "".join(
            [f"<option value='{i}'>{i}</option>" for i in (items or [])]
        )
        html = f"""
        <div class='neg-input-wrapper'>
            <select id='{name}' class='neg-select' {multi}
                style='height:{height}px;' size='5'
                onchange='window.NeglishUI.trigger("{name}","change")'>
                {items_html}
            </select>
        </div>
        """
        self._add_html(window_title, parent, html)

    def listbox_add_item(self, name: str, item: str, window_title: str = None):
        safe = str(item).replace('`', '\\`').replace("'", "\\'")
        self._eval(window_title, f"""
            var sel = document.getElementById('{name}');
            if (sel) {{ var o = document.createElement('option'); o.value=`{safe}`; o.text=`{safe}`; sel.add(o); }}
        """)

    def listbox_clear(self, name: str, window_title: str = None):
        self._eval(window_title, f"""
            var sel = document.getElementById('{name}'); if(sel) sel.innerHTML='';
        """)

    def create_tooltip(self, target_name: str, tooltip_text: str, window_title: str = None):
        """
        Attaches a CSS tooltip to an existing element by ID.
        Must be called after the target widget has been added.
        """
        safe = tooltip_text.replace("'", "\\'").replace('"', '&quot;')
        self._eval(window_title, f"""
            var el = document.getElementById('{target_name}');
            if (el) {{
                el.setAttribute('title', '{safe}');
                el.style.position = 'relative';
                el.setAttribute('data-tooltip', '{safe}');
            }}
        """)

    def create_html_block(self, name: str, html_content: str, window_title: str, opts: dict = None):
        """Inject arbitrary HTML into the layout (escape-safe wrapper)."""
        opts = opts or {}
        parent = opts.get('parent')
        html = f"<div id='{name}'>{html_content}</div>"
        self._add_html(window_title, parent, html)

    # ---------------------------------------------------------------
    # New in v4.5 — Element visibility / state helpers
    # ---------------------------------------------------------------

    def set_visible(self, name: str, visible: bool, window_title: str = None):
        """Show or hide any widget by ID."""
        display = 'block' if visible else 'none'
        self._eval(window_title, f"""
            var el = document.getElementById('{name}');
            if (el) el.style.display = '{display}';
        """)

    def set_enabled(self, name: str, enabled: bool, window_title: str = None):
        """Enable or disable any input/button by ID."""
        val = 'false' if enabled else 'true'
        self._eval(window_title, f"""
            var el = document.getElementById('{name}');
            if (el) el.disabled = {val};
        """)

    def set_style(self, name: str, css_props: dict, window_title: str = None):
        """Apply inline CSS properties to any element. e.g. {'color': 'red', 'font-size': '20px'}"""
        style_str = ';'.join(f"{k}:{v}" for k, v in css_props.items())
        safe = style_str.replace('`', '\\`')
        self._eval(window_title, f"""
            var el = document.getElementById('{name}');
            if (el) Object.assign(el.style, JSON.parse(decodeURIComponent(`{{}}`)));
        """)
        # More direct approach:
        for prop, val in css_props.items():
            safe_val = str(val).replace('`', '\\`').replace("'", "\\'")
            self._eval(window_title, f"""
                var el = document.getElementById('{name}');
                if (el) el.style['{prop}'] = '{safe_val}';
            """)

    def scroll_to(self, name: str, window_title: str = None):
        """Smoothly scroll an element into view."""
        self._eval(window_title, f"""
            var el = document.getElementById('{name}');
            if (el) el.scrollIntoView({{behavior:'smooth', block:'center'}});
        """)

    def focus(self, name: str, window_title: str = None):
        """Focus an input element."""
        self._eval(window_title, f"""
            var el = document.getElementById('{name}'); if (el) el.focus();
        """)

    def update_progress(self, name: str, percent: float, window_title: str = None):
        """Update a progress bar value (0–100)."""
        self._eval(window_title, f"window.NeglishUI.updateProgress('{name}', {percent});")

    def get_switch_value(self, name: str) -> bool:
        """Return the checked state of a switch/checkbox."""
        val = self._get_val(None, name)
        return bool(val)

    def get_slider_value(self, name: str) -> float:
        """Return the current value of a slider."""
        try:
            return float(self._get_val(None, name) or 0)
        except (TypeError, ValueError):
            return 0.0

    def get_dropdown_value(self, name: str) -> str:
        """Return the selected value of a dropdown/select."""
        return str(self._get_val(None, name) or "")

    def eval_js(self, script: str, window_title: str = None):
        """Execute arbitrary JavaScript in a window."""
        self._eval(window_title, script)

    def notify(self, title: str, msg: str, opts: dict = None):
        """
        Show a desktop OS notification (Windows toast / macOS Notification Center).
        Falls back to a GUI toast if not supported.
        """
        opts = opts or {}
        try:
            # Windows 10+ WinRT notification
            from windows_toasts import Toast, WindowsToaster  # type: ignore
            toaster = WindowsToaster('Neglish')
            t = Toast()
            t.text_fields = [title, msg]
            toaster.show_toast(t)
            return
        except ImportError:
            pass
        try:
            # macOS
            import subprocess
            subprocess.run(['osascript', '-e',
                            f'display notification "{msg}" with title "{title}"'],
                           check=False)
            return
        except Exception:
            pass
        # Fallback: in-app toast
        self.show_toast(f"{title}: {msg}", opts)

    # ---------------------------------------------------------------
    # Fallbacks for unmodified Neglish v4.1 core logic
    # ---------------------------------------------------------------
    def alert(self, msg): self.show_dialog(msg, {'type': 'alert', 'title': 'Alert'})
    def confirm(self, msg): return self.show_dialog(msg, {'type': 'confirm', 'title': 'Confirm'})