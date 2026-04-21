# Neglish Language Support for VS Code

Full syntax highlighting, snippets, and theme for the Neglish (`.neg`) programming language.

## Installation (Manual — No Marketplace Required)

### Method 1: Copy to Extensions Folder

1. Copy the entire `vscode-extension/` folder to:
   - **Windows**: `%USERPROFILE%\.vscode\extensions\neglish-language-2.0.0`
   - **macOS/Linux**: `~/.vscode/extensions/neglish-language-2.0.0`
2. Restart VS Code
3. Open any `.neg` file — syntax highlighting activates automatically!

### Method 2: Package as VSIX (Optional)

```bash
npm install -g @vscode/vsce
cd vscode-extension
vsce package
code --install-extension neglish-language-2.0.0.vsix
```

---

## Features

| Feature | Description |
|---------|-------------|
| 🎨 Syntax Highlighting | Full color-coded highlighting for all Neglish keywords |
| 📝 35+ Snippets | Type prefix + Tab to insert code templates |
| 🌙 Neglish Dark Theme | Custom dark theme optimized for Neglish |
| 🔤 Bracket Matching | Auto-close `[]`, `{}`, `()`, `""`, `''` |
| 📁 Code Folding | Fold `if/while/define/repeat` blocks |
| ▶ Run Commands | `Ctrl+Shift+P` → "Run Neglish File" |
| 📊 Status Bar | Click `▶ Run Neglish` button in status bar |

---

## Syntax Color Guide

| Color | Meaning |
|-------|---------|
| 🔴 **Red/Orange** | Control flow: `if`, `while`, `end`, `return`, `break` |
| 🟣 **Purple** | Function definition: `define`, `function`, `with` |
| 🔵 **Blue** | Function names, `call`, list/string functions |
| 🟢 **Green** | I/O keywords: `show`, `say`, `ask`, `print`, `log` |
| 🟡 **Yellow** | Numbers, constants: `true`, `false`, `null`, `PI` |
| 🟠 **Orange** | GUI keywords: `create`, `window`, `button`, `when` |
| 🩵 **Light Blue** | Strings |
| ⚪ **White** | Variables and identifiers |
| ⬛ **Gray Italic** | Comments |

---

## Snippet Reference

| Prefix | What it inserts |
|--------|----------------|
| `show` | show statement |
| `set` | set variable |
| `if` | if...end block |
| `ife` | if...else...end |
| `ifee` | if...elseif...else...end |
| `while` | while loop |
| `repeat` | repeat N times |
| `repeati` | repeat with index var |
| `forr` | for range loop |
| `fors` | for range with step |
| `fore` | for each loop |
| `forever` | infinite loop |
| `def` | define function |
| `defn` | function no params |
| `call` | call function |
| `ask` | ask for input |
| `list` | create list |
| `dict` | create map/dict |
| `try` | try/catch block |
| `switch` | switch/match |
| `win` | create GUI window |
| `btn` | create button |
| `click` | button click event |
| `emit` | emit event |
| `on` | on event handler |
| `fwrite` | file write |
| `fread` | file read |
| `jsave` | JSON save |
| `jload` | JSON load |
| `color` | colored output |
| `sleep` | sleep/pause |
| `fmt` | format string |
| `assert` | assert statement |
| `import` | import module |
| `debug` | debug variable |
| `inspect` | inspect variable |
| `ml` | multiline string |

---

## Activating Neglish Dark Theme

1. Press `Ctrl+K Ctrl+T`
2. Select **"Neglish Dark"**
