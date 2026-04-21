#!/usr/bin/env python3
# main.py — Neglish v3 Entry Point
#
#  python main.py program.neg          ← run (with GUI if needed)
#  python main.py program.neg --nogui  ← force console only
#  python main.py --repl               ← interactive shell
#  python main.py --version            ← print version
#  python main.py --test file.neg      ← run tests only (no GUI)
#  python main.py --check file.neg     ← parse-check only

import sys, os, threading

BANNER = """\033[96m
  ███╗   ██╗███████╗ ██████╗ ██╗     ██╗███████╗██╗  ██╗
  ████╗  ██║██╔════╝██╔════╝ ██║     ██║██╔════╝██║  ██║
  ██╔██╗ ██║█████╗  ██║  ███╗██║     ██║███████╗███████║
  ██║╚██╗██║██╔══╝  ██║   ██║██║     ██║╚════██║██╔══██║
  ██║ ╚████║███████╗╚██████╔╝███████╗██║███████║██║  ██║
  ╚═╝  ╚═══╝╚══════╝ ╚═════╝ ╚══════╝╚═╝╚══════╝╚═╝  ╚═╝
  v3.0  —  English-like Programming Language
\033[0m"""


def run_source(source: str, filepath: str = '<stdin>',
               use_gui: bool = True, extra_args=None, run_tests=False):
    from lexer       import Lexer
    from parser      import Parser
    from interpreter import Interpreter

    src_dir = os.path.dirname(os.path.abspath(filepath)) if filepath != '<stdin>' else os.getcwd()

    try:
        tokens = Lexer(source).tokenize()
        ast    = Parser(tokens).parse()
    except Exception as e:
        print(f"\033[91m{e}\033[0m", file=sys.stderr)
        sys.exit(1)

    gui = None
    # Only spin up GUI if the program actually creates windows
    needs_gui = use_gui and any(
        s.get('type') in ('create_window','show_window','create_button',
                          'create_label','create_entry','create_progress',
                          'when_clicked','gui_alert','gui_confirm')
        for s in _walk_stmts(ast)
    )

    if needs_gui:
        try:
            from gui import GUIManager
            gui = GUIManager()
        except Exception as e:
            print(f"\033[93m[Warning] GUI unavailable: {e}\033[0m")

    interp = Interpreter(gui_manager=gui, source_dir=src_dir)
    interp.global_env.set('__file__', filepath)
    interp.global_env.set('ARGS', extra_args or [])

    if gui:
        err = [None]
        def bg():
            gui.wait_ready()
            try:
                interp.run(ast)
            except SystemExit: pass
            except Exception as ex:
                err[0] = ex
                print(f"\033[91m{ex}\033[0m", file=sys.stderr)
            finally:
                interp.print_test_summary()

        t = threading.Thread(target=bg, daemon=True)
        t.start()
        gui.start()
        gui.mainloop()
    else:
        try:
            interp.run(ast)
        except SystemExit: pass
        except Exception as ex:
            print(f"\033[91m{ex}\033[0m", file=sys.stderr)
        finally:
            interp.print_test_summary()


def _walk_stmts(stmts, depth=0):
    """Flat walk of all AST nodes."""
    if depth > 10: return
    for s in stmts:
        yield s
        for key in ('body','else','catch','elseif'):
            sub = s.get(key)
            if isinstance(sub, list):
                yield from _walk_stmts(sub, depth+1)
            elif isinstance(sub, dict):
                yield from _walk_stmts([sub], depth+1)
        for branch in s.get('elseif', []):
            yield from _walk_stmts(branch.get('body', []), depth+1)
        for case in s.get('cases', []):
            yield from _walk_stmts(case.get('body', []), depth+1)


def repl():
    from lexer       import Lexer
    from parser      import Parser
    from interpreter import Interpreter

    print(BANNER)
    print("  Type Neglish code, 'exit' to quit, 'help' for commands\n")

    interp = Interpreter()
    buf    = []
    in_block = 0

    while True:
        try:
            prompt = "... " if buf else ">>> "
            line   = input(f"\033[96m{prompt}\033[0m")
        except (EOFError, KeyboardInterrupt):
            print("\n\033[90mBye!\033[0m"); break

        if line.strip().lower() in ('exit', 'quit'):
            print("\033[90mBye!\033[0m"); break

        if line.strip().lower() == 'help':
            print("\033[93m  Commands: exit, help, clear, vars\033[0m")
            print("  Write any Neglish code — multi-line blocks supported.")
            continue

        if line.strip().lower() == 'vars':
            for k, v in interp.global_env.vars.items():
                if not callable(v):
                    print(f"  \033[96m{k}\033[0m = {repr(v)}")
            continue

        if line.strip().lower() == 'clear':
            os.system('cls' if os.name == 'nt' else 'clear'); continue

        buf.append(line)

        # Track block depth
        stripped = line.strip().lower()
        block_openers = ('if ','repeat ','while ','for ','define ','loop','forever',
                         'try','switch','when ','describe ','test ','benchmark ','class ','async ')
        block_closers = ('end',)
        if any(stripped.startswith(o) for o in block_openers): in_block += 1
        if stripped in block_closers or stripped.startswith('end'): in_block = max(0, in_block - 1)

        if in_block > 0:
            continue  # keep buffering

        source = '\n'.join(buf)
        try:
            tokens = Lexer(source).tokenize()
            ast    = Parser(tokens).parse()
            interp.run(ast)
        except Exception as ex:
            print(f"\033[91m{ex}\033[0m")
        buf = []; in_block = 0


def check_syntax(filepath):
    from lexer  import Lexer
    from parser import Parser
    with open(filepath, 'r', encoding='utf-8') as f:
        source = f.read()
    try:
        tokens = Lexer(source).tokenize()
        Parser(tokens).parse()
        print(f"\033[92m✓ Syntax OK: {filepath}\033[0m")
    except Exception as e:
        print(f"\033[91m✗ Syntax Error: {e}\033[0m")
        sys.exit(1)


def main():
    args = sys.argv[1:]

    if not args or args[0] == '--repl':
        repl(); return

    if args[0] == '--version':
        print(BANNER.strip())
        print("  Version 3.0  |  Python runtime")
        return

    flags    = [a for a in args if a.startswith('--')]
    files    = [a for a in args if not a.startswith('--')]
    use_gui  = '--nogui' not in flags
    run_tests = '--test' in flags
    check    = '--check' in flags

    if not files:
        repl(); return

    filepath = files[0]
    if not os.path.exists(filepath):
        print(f"\033[91mError: File not found: '{filepath}'\033[0m")
        sys.exit(1)

    if not filepath.endswith('.neg'):
        print(f"\033[93mWarning: '{filepath}' does not have .neg extension\033[0m")

    if check:
        check_syntax(filepath); return

    with open(filepath, 'r', encoding='utf-8') as f:
        source = f.read()

    run_source(source, filepath=filepath, use_gui=use_gui,
               extra_args=files[1:], run_tests=run_tests)


if __name__ == '__main__':
    main()
