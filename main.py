#!/usr/bin/env python3
# main.py — Neglish v4.2 Entry Point
#
#  neglish program.neg              ← run a .neg file from anywhere
#  neglish program.neg --nogui      ← force console only
#  neglish --repl                   ← interactive shell
#  neglish --version                ← print version
#  neglish --check file.neg         ← parse-check only
#  neglish --tokens file.neg        ← dump token stream (debug)
#  neglish --ast file.neg           ← dump AST as JSON (debug)
#  neglish --profile file.neg       ← run with timing info
#  neglish --install                ← install to PATH (Windows)
#  neglish --uninstall              ← remove from PATH (Windows)

import sys, os, threading, time, hashlib

VERSION = "4.2"
BUILD   = "2026"
_AST_CACHE = {}
_AST_CACHE_ORDER = []
_AST_CACHE_MAX = 128

BANNER = """\033[96m
  ███╗   ██╗███████╗ ██████╗ ██╗     ██╗███████╗██╗  ██╗
  ████╗  ██║██╔════╝██╔════╝ ██║     ██║██╔════╝██║  ██║
  ██╔██╗ ██║█████╗  ██║  ███╗██║     ██║███████╗███████║
  ██║╚██╗██║██╔══╝  ██║   ██║██║     ██║╚════██║██╔══██║
  ██║ ╚████║███████╗╚██████╔╝███████╗██║███████║██║  ██║
  ╚═╝  ╚═══╝╚══════╝ ╚═════╝ ╚══════╝╚═╝╚══════╝╚═╝  ╚═╝
\033[0m\033[2m  v{v}  —  English-like Programming Language  |  {b}\033[0m
""".format(v=VERSION, b=BUILD)

GUI_TRIGGER_TYPES = frozenset({
    'create_window','show_window','create_button','create_label',
    'create_entry','create_progress','create_textarea','create_checkbox',
    'create_dropdown','create_image','create_canvas','create_table',
    'when_clicked','gui_alert','gui_confirm','set_theme','create_menu',
    'create_tab','create_statusbar','fusion','open_webview',
})


def run_source(source, filepath='<stdin>', use_gui=True,
               extra_args=None, run_tests=False, profile=False,
               permissive_mode=True, strict_mode=False):
    from lexer       import Lexer
    from parser      import Parser
    from interpreter import Interpreter

    src_dir = os.path.dirname(os.path.abspath(filepath)) if filepath != '<stdin>' else os.getcwd()

    try:
        t0 = time.perf_counter()
        source_hash = hashlib.sha256(source.encode('utf-8')).hexdigest()
        cache_key = f"{filepath}:{source_hash}:{strict_mode}:{permissive_mode}"
        ast = _AST_CACHE.get(cache_key)
        if ast is None:
            tokens = Lexer(source).tokenize()
            parser = Parser(tokens, permissive_mode=permissive_mode, strict_mode=strict_mode)
            ast = parser.parse()
            _AST_CACHE[cache_key] = ast
            _AST_CACHE_ORDER.append(cache_key)
            if len(_AST_CACHE_ORDER) > _AST_CACHE_MAX:
                evicted = _AST_CACHE_ORDER.pop(0)
                _AST_CACHE.pop(evicted, None)
        else:
            tokens = []
        if profile:
            print(f"\033[2m[profile] parse: {(time.perf_counter()-t0)*1000:.2f}ms\033[0m")
    except Exception as e:
        _print_error(e); sys.exit(1)

    gui = None
    if use_gui and any(s.get('type') in GUI_TRIGGER_TYPES for s in _walk_stmts(ast)):
        try:
            from gui import GUIManager
            gui = GUIManager()
        except Exception as e:
            print(f"\033[93m[Warning] GUI unavailable: {e}\033[0m")

    interp = Interpreter(gui_manager=gui, source_dir=src_dir)
    interp.global_env.set('__file__', filepath)
    interp.global_env.set('__version__', VERSION)
    interp.global_env.set('ARGS', extra_args or [])

    def _run():
        t2 = time.perf_counter()
        interp.run(ast)
        if profile:
            print(f"\033[2m[profile] exec: {(time.perf_counter()-t2)*1000:.2f}ms\033[0m")

    if gui:
        def bg():
            gui.wait_ready()
            try:   _run()
            except SystemExit: pass
            except Exception as ex: _print_error(ex)
            finally: interp.print_test_summary()
        threading.Thread(target=bg, daemon=True).start()
        gui.start(); gui.mainloop()
    else:
        try:   _run()
        except SystemExit: pass
        except Exception as ex: _print_error(ex)
        finally: interp.print_test_summary()


def _print_error(e):
    print(f"\033[91m✗ {e}\033[0m", file=sys.stderr)


def _walk_stmts(stmts, depth=0):
    if depth > 20 or not isinstance(stmts, list): return
    for s in stmts:
        if not isinstance(s, dict): continue
        yield s
        for key in ('body','else','catch','finally'):
            sub = s.get(key)
            if isinstance(sub, list):   yield from _walk_stmts(sub, depth+1)
            elif isinstance(sub, dict): yield from _walk_stmts([sub], depth+1)
        for branch in s.get('elseif', []):
            yield from _walk_stmts(branch.get('body',[]), depth+1)
        for case in s.get('cases', []):
            yield from _walk_stmts(case.get('body',[]), depth+1)


def repl():
    from lexer       import Lexer
    from parser      import Parser
    from interpreter import Interpreter

    print(BANNER)
    print("  Commands: \033[96mexit  help  vars  clear  load <file>\033[0m\n")

    interp  = Interpreter()
    buf, in_block = [], 0

    OPENERS = ('if ','repeat ','while ','for ','define ','loop','forever',
               'try','switch','when ','describe ','test ','benchmark ','class ','async ')

    while True:
        try:
            prompt = "... " if buf else ">>> "
            line   = input(f"\033[96m{prompt}\033[0m")
        except (EOFError, KeyboardInterrupt):
            print("\n\033[90mBye!\033[0m"); break

        s = line.strip().lower()

        if s in ('exit','quit'):    print("\033[90mBye!\033[0m"); break
        if s == 'help':             _repl_help(); continue
        if s == 'vars':             _repl_vars(interp); continue
        if s == 'clear':            os.system('cls' if os.name=='nt' else 'clear'); continue
        if s.startswith('load '):
            path = line.strip()[5:].strip()
            _repl_load(path, interp); continue

        buf.append(line)
        if any(s.startswith(o) for o in OPENERS): in_block += 1
        if s == 'end' or s.startswith('end'):     in_block = max(0, in_block-1)
        if in_block > 0: continue

        source = '\n'.join(buf)
        try:
            ast = Parser(Lexer(source).tokenize()).parse()
            interp.run(ast)
        except Exception as ex:
            _print_error(ex)
        buf = []; in_block = 0


def _repl_help():
    print("""
\033[96m  REPL Commands\033[0m
  exit / quit     — leave the REPL
  help            — show this message
  vars            — list all defined variables
  clear           — clear screen
  load <file>     — load & run a .neg file

\033[96m  Quick examples\033[0m
  set x to 42
  show x
  if x > 10 then
    show "big number"
  end
  define greet with name
    show "Hello " + name
  end
  call greet with "World"
""")


def _repl_vars(interp):
    items = {k: v for k, v in interp.global_env.vars.items()
             if not callable(v) and not k.startswith('__')}
    if not items:
        print("  \033[2m(no variables defined)\033[0m"); return
    for k, v in items.items():
        print(f"  \033[96m{k}\033[0m \033[2m({type(v).__name__})\033[0m = {repr(v)}")


def _repl_load(path, interp):
    from lexer  import Lexer
    from parser import Parser
    if not os.path.exists(path):
        print(f"\033[91m✗ File not found: {path}\033[0m"); return
    with open(path, 'r', encoding='utf-8') as f:
        src = f.read()
    try:
        interp.run(Parser(Lexer(src).tokenize()).parse())
        print(f"\033[92m✓ Loaded {path}\033[0m")
    except Exception as ex:
        _print_error(ex)


def check_syntax(filepath):
    from lexer  import Lexer
    from parser import Parser
    with open(filepath, 'r', encoding='utf-8') as f:
        source = f.read()
    try:
        tokens = Lexer(source).tokenize()
        ast    = Parser(tokens).parse()
        print(f"\033[92m✓ Syntax OK — {len(tokens)} tokens, {len(ast)} statements: {filepath}\033[0m")
    except Exception as e:
        _print_error(e); sys.exit(1)


def dump_tokens(filepath):
    from lexer import Lexer
    with open(filepath, 'r', encoding='utf-8') as f:
        source = f.read()
    tokens = Lexer(source).tokenize()
    for tok in tokens:
        print(f"  {tok.line:>4}  {tok.type:<10}  {tok.value!r}")


def dump_ast(filepath):
    from lexer  import Lexer
    from parser import Parser
    import json
    with open(filepath, 'r', encoding='utf-8') as f:
        source = f.read()
    ast = Parser(Lexer(source).tokenize()).parse()
    def _fix(o):
        if isinstance(o, dict): return {k: _fix(v) for k,v in o.items()}
        if isinstance(o, list): return [_fix(i) for i in o]
        return o
    print(json.dumps(_fix(ast), indent=2))


def _install_to_path():
    """Install neglish.exe to a user directory and add it to the system PATH."""
    import shutil, winreg
    if os.name != 'nt':
        print("\033[91m✗ --install is only supported on Windows.\033[0m")
        print("  On Linux/macOS, add the directory containing neglish to your PATH manually.")
        sys.exit(1)

    # Determine install location
    install_dir = os.path.join(os.environ.get('LOCALAPPDATA', os.path.expanduser('~')), 'Neglish')
    os.makedirs(install_dir, exist_ok=True)

    # Copy the exe (frozen) or the main script
    if getattr(sys, 'frozen', False):
        src = sys.executable
        dst = os.path.join(install_dir, 'neglish.exe')
        shutil.copy2(src, dst)
        # Also copy stdlib if it was packed alongside
        stdlib_src = os.path.join(os.path.dirname(src), 'stdlib')
        if os.path.isdir(stdlib_src):
            stdlib_dst = os.path.join(install_dir, 'stdlib')
            if os.path.exists(stdlib_dst): shutil.rmtree(stdlib_dst)
            shutil.copytree(stdlib_src, stdlib_dst)
    else:
        print("\033[93m⚠ Run --install from a built neglish.exe, not from source.\033[0m")
        sys.exit(1)

    # Add install_dir to user PATH via registry
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                             r'Environment', 0, winreg.KEY_READ | winreg.KEY_WRITE)
        try:
            current_path, _ = winreg.QueryValueEx(key, 'Path')
        except FileNotFoundError:
            current_path = ''
        paths = [p for p in current_path.split(';') if p and p != install_dir]
        paths.append(install_dir)
        winreg.SetValueEx(key, 'Path', 0, winreg.REG_EXPAND_SZ, ';'.join(paths))
        winreg.CloseKey(key)
        print(f"\033[92m✓ Neglish installed to: {install_dir}\033[0m")
        print(f"\033[92m✓ Added to user PATH.\033[0m")
        print("\033[2m  Open a new terminal to use 'neglish' from anywhere.\033[0m")
    except Exception as e:
        print(f"\033[91m✗ Could not update PATH: {e}\033[0m")
        print(f"  Add this manually to your PATH: {install_dir}")


def _uninstall_from_path():
    """Remove neglish from PATH and delete the install directory."""
    import shutil
    if os.name != 'nt':
        print("\033[91m✗ --uninstall is only supported on Windows.\033[0m")
        sys.exit(1)
    import winreg
    install_dir = os.path.join(os.environ.get('LOCALAPPDATA', os.path.expanduser('~')), 'Neglish')
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                             r'Environment', 0, winreg.KEY_READ | winreg.KEY_WRITE)
        try:
            current_path, _ = winreg.QueryValueEx(key, 'Path')
        except FileNotFoundError:
            current_path = ''
        paths = [p for p in current_path.split(';') if p and p.rstrip('\\') != install_dir.rstrip('\\')]
        winreg.SetValueEx(key, 'Path', 0, winreg.REG_EXPAND_SZ, ';'.join(paths))
        winreg.CloseKey(key)
    except Exception as e:
        print(f"\033[93m⚠ Could not update PATH registry: {e}\033[0m")
    if os.path.isdir(install_dir):
        shutil.rmtree(install_dir, ignore_errors=True)
        print(f"\033[92m✓ Removed {install_dir}\033[0m")
    print("\033[92m✓ Neglish uninstalled.\033[0m")
    print("\033[2m  Open a new terminal for the PATH change to take effect.\033[0m")


def main():
    args = sys.argv[1:]

    if not args or args[0] == '--repl':
        repl(); return

    if args[0] == '--version':
        print(BANNER.strip())
        print(f"\n  Version {VERSION}  |  Python {sys.version.split()[0]}  |  Build {BUILD}")
        return

    if args[0] == '--install':
        _install_to_path(); return

    if args[0] == '--uninstall':
        _uninstall_from_path(); return

    flags     = {a for a in args if a.startswith('--')}
    files     = [a for a in args if not a.startswith('--')]
    use_gui   = '--nogui' not in flags
    run_tests = '--test' in flags
    profile   = '--profile' in flags
    strict_mode = '--strict' in flags
    permissive_mode = '--no-permissive' not in flags

    if not files:
        repl(); return

    filepath = files[0]
    if not os.path.exists(filepath):
        print(f"\033[91m✗ File not found: '{filepath}'\033[0m"); sys.exit(1)

    if not filepath.endswith('.neg'):
        print(f"\033[93m⚠ '{filepath}' does not have .neg extension\033[0m")

    if '--check'  in flags: check_syntax(filepath); return
    if '--tokens' in flags: dump_tokens(filepath);  return
    if '--ast'    in flags: dump_ast(filepath);     return

    with open(filepath, 'r', encoding='utf-8') as f:
        source = f.read()

    run_source(source, filepath=filepath, use_gui=use_gui,
               extra_args=files[1:], run_tests=run_tests, profile=profile,
               permissive_mode=permissive_mode, strict_mode=strict_mode)


if __name__ == '__main__':
    main()
