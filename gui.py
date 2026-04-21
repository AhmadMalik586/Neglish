# gui.py — Neglish v3 GUI Manager
# Output goes to terminal/cmd. No embedded console.
import tkinter as tk
from tkinter import simpledialog, messagebox, ttk
import threading, re, os

BG_DEEP='#0d1117'; BG_PANEL='#161b22'; BG_CARD='#1c2128'
BG_HOVER='#21262d'; BG_INPUT='#21262d'; ACCENT='#58a6ff'
ACCENT2='#3fb950'; DANGER='#f85149'; WARNING='#e3b341'
PURPLE='#bc8cff'; FG_MAIN='#e6edf3'; FG_DIM='#8b949e'
FG_DIMMER='#484f58'; BORDER='#30363d'

BTN_COLORS = {
    'default': ('#238636','#2ea043','#ffffff'),
    'green':   ('#238636','#2ea043','#ffffff'),
    'blue':    ('#1f6feb','#388bfd','#ffffff'),
    'red':     ('#b91c1c','#dc2626','#ffffff'),
    'gray':    ('#21262d','#30363d','#e6edf3'),
    'grey':    ('#21262d','#30363d','#e6edf3'),
    'purple':  ('#6e40c9','#8957e5','#ffffff'),
    'orange':  ('#d97706','#f59e0b','#ffffff'),
    'cyan':    ('#0891b2','#06b6d4','#ffffff'),
    'dark':    ('#161b22','#21262d','#e6edf3'),
    'yellow':  ('#92400e','#b45309','#ffffff'),
}

class HoverButton(tk.Button):
    def __init__(self, master, bg_normal, bg_hover, **kw):
        super().__init__(master, bg=bg_normal, **kw)
        self._n, self._h = bg_normal, bg_hover
        self.bind('<Enter>', lambda e: self.configure(bg=self._h))
        self.bind('<Leave>', lambda e: self.configure(bg=self._n))

class GUIManager:
    def __init__(self):
        self._root     = None
        self._windows  = {}
        self._labels   = {}
        self._widgets  = {}
        self._buttons  = {}
        self._entries  = {}
        self._progress = {}
        self._ready    = threading.Event()
        self._style    = None
        self._icon_set = False

    def start(self):
        self._root = tk.Tk()
        self._root.withdraw()
        self._root.title("Neglish v3")
        self._root.configure(bg=BG_DEEP)
        self._style = ttk.Style()
        self._style.theme_use('clam')
        self._style.configure('N.Horizontal.TProgressbar',
            background=ACCENT, troughcolor=BG_PANEL, borderwidth=0, thickness=14)
        # Neglish icon (embedded - a simple N shape)
        icon_data = """
R0lGODlhIAAgAMIAAAAAAP///0BAwP8A/wAA/////wAAAAAAACH5BAEAAAQALAAAAAAgACAAAAP/
SLrc/jDKSau9OOvNu/9gKI5kaZ5oqq5s675wLM90bd94ru987//AoHBILBqPyKRyyWw6n9Co
dEqtWq/YrHbL7Xq/4LB4TC6bz+i0es1uu9/wuHxOr9vv+Lx+z+/7/4CBgoOEhYaHiImKi4yN
jo+QkZKTlJWWl5iZmpucnZ6foKGio6SlpqeoqaqrrK2ur7CxsrO0tba3uLm6u7y9vr/AwcLDxA==
"""
        try:
            import base64
            icon_img = tk.PhotoImage(data=icon_data)
            self._root.iconphoto(True, icon_img)
            self._icon_set = True
        except Exception:
            pass
        self._ready.set()

    def mainloop(self):
        if self._root: self._root.mainloop()

    def wait_ready(self): self._ready.wait()

    def log(self, text):
        pass  # All output goes to terminal/cmd - no GUI console

    def create_window(self, title: str, width: int, height: int):
        def _do():
            win = tk.Toplevel(self._root)
            win.title(title)
            win.geometry(f"{width}x{height}")
            win.configure(bg=BG_DEEP)
            win.resizable(True, True)

            # Set icon on child window too
            if self._icon_set:
                try:
                    win.iconphoto(False, self._root.iconphoto.__self__)
                except Exception:
                    pass

            # Mac-style title bar
            title_bar = tk.Frame(win, bg=BG_PANEL)
            title_bar.pack(fill='x', side='top')
            dot_f = tk.Frame(title_bar, bg=BG_PANEL)
            dot_f.pack(side='left', padx=12, pady=10)
            for col in ('#f85149','#e3b341','#3fb950'):
                c = tk.Canvas(dot_f, width=12, height=12, bg=BG_PANEL, highlightthickness=0)
                c.create_oval(2,2,12,12, fill=col, outline='')
                c.pack(side='left', padx=2)
            tk.Label(title_bar, text=title, bg=BG_PANEL, fg=FG_MAIN,
                     font=('Helvetica',13,'bold')).pack(side='left', padx=8)
            tk.Frame(win, bg=BORDER, height=1).pack(fill='x')

            # Scrollable canvas
            canvas  = tk.Canvas(win, bg=BG_DEEP, highlightthickness=0, bd=0)
            vscroll = ttk.Scrollbar(win, orient='vertical', command=canvas.yview)
            content = tk.Frame(canvas, bg=BG_DEEP)
            content.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
            canvas.create_window((0,0), window=content, anchor='nw')
            canvas.configure(yscrollcommand=vscroll.set)
            canvas.pack(side='left', fill='both', expand=True)
            vscroll.pack(side='right', fill='y')
            win.bind('<MouseWheel>', lambda e: canvas.yview_scroll(int(-1*(e.delta/120)),'units'))

            win._content = content
            self._windows[title] = win
            win.deiconify(); win.lift()
        self._root.after(0, _do)

    def show_window(self, title=''):
        def _do():
            targets = ([self._windows[title]] if title and title in self._windows
                       else list(self._windows.values()))
            for w in targets: w.deiconify(); w.lift()
        self._root.after(0, _do)

    def create_button(self, label: str, window_title: str, opts: dict = None):
        opts = opts or {}
        def _do():
            win = self._windows.get(window_title)
            if not win: return
            frame = getattr(win,'_content', win)
            ck = str(opts.get('color','default')).lower()
            palette = BTN_COLORS.get(ck, BTN_COLORS['default'])
            bg_n, bg_h, fg = palette
            if ck.startswith('#'): bg_n = ck; bg_h = ck; fg = opts.get('foreground','#ffffff')
            fnt_size = int(opts.get('size',12))
            btn = HoverButton(frame, bg_normal=bg_n, bg_hover=bg_h,
                text=label, fg=fg, font=('Helvetica',fnt_size,'bold'),
                relief='flat', padx=20, pady=9, cursor='hand2',
                activeforeground=fg, borderwidth=0)
            if 'x' in opts and 'y' in opts:
                btn.place(x=int(opts['x']), y=int(opts['y']))
            elif 'row' in opts and 'column' in opts:
                btn.grid(row=int(opts['row']), column=int(opts['column']), padx=4, pady=4, sticky='ew')
            else:
                btn.pack(pady=5, padx=16, anchor='w')
            self._buttons[label] = btn
            self._widgets[label] = btn
        self._root.after(0, _do)

    def create_label(self, text: str, window_title: str, opts: dict = None, name: str = None):
        opts = opts or {}
        lbl_name = name or text[:30]
        def _do():
            win = self._windows.get(window_title)
            if not win: return
            frame = getattr(win,'_content', win)
            fg = str(opts.get('color', opts.get('foreground', FG_MAIN)))
            fnt_size = int(opts.get('size',12))
            bold = opts.get('bold', False)
            var = tk.StringVar(value=text)
            lbl = tk.Label(frame, textvariable=var, bg=BG_DEEP, fg=fg,
                font=('Helvetica', fnt_size, 'bold' if bold else 'normal'),
                wraplength=700, justify='left', anchor='w')
            if 'x' in opts and 'y' in opts:
                lbl.place(x=int(opts['x']), y=int(opts['y']))
            elif 'row' in opts and 'column' in opts:
                lbl.grid(row=int(opts['row']), column=int(opts['column']), padx=4, pady=2, sticky='w')
            else:
                lbl.pack(anchor='w', padx=16, pady=3)
            self._labels[lbl_name] = (lbl, var)
            self._widgets[lbl_name] = lbl
        self._root.after(0, _do)

    def update_label(self, name: str, text: str):
        def _do():
            pair = self._labels.get(name)
            if pair: pair[1].set(str(text))
        self._root.after(0, _do)

    def create_entry(self, name: str, window_title: str, opts: dict = None):
        opts = opts or {}
        def _do():
            win = self._windows.get(window_title)
            if not win: return
            frame = getattr(win,'_content', win)
            var = tk.StringVar()
            container = tk.Frame(frame, bg=BG_DEEP)
            tk.Label(container, text=name, bg=BG_DEEP, fg=FG_DIM,
                     font=('Helvetica',10)).pack(anchor='w')
            ef = tk.Frame(container, bg=BORDER, padx=1, pady=1)
            ef.pack(fill='x', pady=(2,8))
            entry = tk.Entry(ef, textvariable=var, bg=BG_INPUT, fg=FG_MAIN,
                font=('Courier New',13), relief='flat', insertbackground=ACCENT,
                borderwidth=0, highlightthickness=0)
            entry.pack(fill='x', padx=6, pady=6)
            entry.bind('<FocusIn>', lambda e: ef.configure(bg=ACCENT))
            entry.bind('<FocusOut>', lambda e: ef.configure(bg=BORDER))
            container.pack(fill='x', padx=16, pady=2)
            self._entries[name] = var
            self._widgets[name] = entry
        self._root.after(0, _do)

    def get_entry_value(self, name: str) -> str:
        var = self._entries.get(name)
        return var.get() if var else ''

    def set_entry_value(self, name: str, text: str):
        def _do():
            var = self._entries.get(name)
            if var: var.set(str(text))
        self._root.after(0, _do)

    def create_progress(self, name: str, window_title: str):
        def _do():
            win = self._windows.get(window_title)
            if not win: return
            frame = getattr(win,'_content', win)
            container = tk.Frame(frame, bg=BG_DEEP, padx=16, pady=4)
            tk.Label(container, text=name, bg=BG_DEEP, fg=FG_DIM,
                     font=('Helvetica',9)).pack(anchor='w')
            pb = ttk.Progressbar(container, length=500, mode='determinate',
                                 style='N.Horizontal.TProgressbar')
            pb.pack(fill='x', pady=(2,0))
            container.pack(fill='x')
            self._progress[name] = pb
            self._widgets[name]  = pb
        self._root.after(0, _do)

    def set_progress(self, name: str, value: float):
        def _do():
            pb = self._progress.get(name)
            if pb: pb['value'] = float(value)
        self._root.after(0, _do)

    def bind_button(self, label: str, callback):
        def _do():
            btn = self._buttons.get(label)
            if btn: btn.configure(command=callback)
        self._root.after(0, _do)

    def hide_widget(self, name: str):
        def _do():
            w = self._widgets.get(name)
            if w:
                try: w.pack_forget()
                except: w.place_forget()
        self._root.after(0, _do)

    def ask_input(self, prompt: str) -> str:
        result = ['']
        done = threading.Event()
        def _do():
            dlg = tk.Toplevel(self._root)
            dlg.title("Input"); dlg.configure(bg=BG_PANEL)
            dlg.resizable(False, False); dlg.grab_set()
            tk.Label(dlg, text=prompt, bg=BG_PANEL, fg=FG_MAIN,
                font=('Helvetica',12), wraplength=340).pack(padx=24, pady=(20,8))
            var = tk.StringVar()
            ef = tk.Frame(dlg, bg=BORDER, padx=1, pady=1)
            ef.pack(fill='x', padx=24)
            entry = tk.Entry(ef, textvariable=var, bg=BG_INPUT, fg=FG_MAIN,
                font=('Courier New',13), relief='flat', insertbackground=ACCENT, borderwidth=0)
            entry.pack(fill='x', padx=6, pady=6); entry.focus_set()
            def submit(*_): result[0]=var.get(); dlg.destroy(); done.set()
            def cancel(*_): result[0]=''; dlg.destroy(); done.set()
            entry.bind('<Return>', submit); entry.bind('<Escape>', cancel)
            row = tk.Frame(dlg, bg=BG_PANEL); row.pack(pady=12)
            HoverButton(row, '#21262d','#30363d', text='Cancel', fg=FG_DIM,
                font=('Helvetica',11), relief='flat', padx=16, pady=6,
                cursor='hand2', command=cancel, borderwidth=0).pack(side='left', padx=4)
            HoverButton(row, '#238636','#2ea043', text='OK', fg='white',
                font=('Helvetica',11,'bold'), relief='flat', padx=20, pady=6,
                cursor='hand2', command=submit, borderwidth=0).pack(side='left', padx=4)
            dlg.protocol('WM_DELETE_WINDOW', cancel)
            w, h = 400, 200
            x = self._root.winfo_screenwidth()//2-w//2
            y = self._root.winfo_screenheight()//2-h//2
            dlg.geometry(f"{w}x{h}+{x}+{y}")
        self._root.after(0, _do); done.wait(); return result[0]

    def alert(self, msg: str):
        done = threading.Event()
        def _do():
            dlg = tk.Toplevel(self._root)
            dlg.title("Alert"); dlg.configure(bg=BG_PANEL)
            dlg.resizable(False, False); dlg.grab_set()
            tk.Label(dlg, text="⚠", bg=BG_PANEL, fg=WARNING,
                font=('Helvetica',28)).pack(pady=(20,4))
            tk.Label(dlg, text=str(msg), bg=BG_PANEL, fg=FG_MAIN,
                font=('Helvetica',12), wraplength=340).pack(padx=24, pady=8)
            HoverButton(dlg, '#238636','#2ea043', text='OK', fg='white',
                font=('Helvetica',11,'bold'), relief='flat', padx=24, pady=8,
                cursor='hand2', command=lambda:(dlg.destroy(),done.set()),
                borderwidth=0).pack(pady=12)
            w,h=400,200; x=self._root.winfo_screenwidth()//2-w//2
            y=self._root.winfo_screenheight()//2-h//2
            dlg.geometry(f"{w}x{h}+{x}+{y}")
        self._root.after(0, _do); done.wait()

    def confirm(self, msg: str) -> bool:
        result=[False]; done=threading.Event()
        def _do():
            dlg=tk.Toplevel(self._root); dlg.title("Confirm")
            dlg.configure(bg=BG_PANEL); dlg.resizable(False,False); dlg.grab_set()
            tk.Label(dlg,text="?",bg=BG_PANEL,fg=ACCENT,font=('Helvetica',28)).pack(pady=(20,4))
            tk.Label(dlg,text=str(msg),bg=BG_PANEL,fg=FG_MAIN,
                font=('Helvetica',12),wraplength=340).pack(padx=24,pady=8)
            row=tk.Frame(dlg,bg=BG_PANEL); row.pack(pady=12)
            def yes(): result[0]=True; dlg.destroy(); done.set()
            def no(): result[0]=False; dlg.destroy(); done.set()
            HoverButton(row,'#21262d','#30363d',text='No',fg=FG_DIM,font=('Helvetica',11),
                relief='flat',padx=20,pady=8,cursor='hand2',command=no,borderwidth=0).pack(side='left',padx=4)
            HoverButton(row,'#1f6feb','#388bfd',text='Yes',fg='white',font=('Helvetica',11,'bold'),
                relief='flat',padx=20,pady=8,cursor='hand2',command=yes,borderwidth=0).pack(side='left',padx=4)
            dlg.protocol('WM_DELETE_WINDOW',no)
            w,h=420,210; x=self._root.winfo_screenwidth()//2-w//2
            y=self._root.winfo_screenheight()//2-h//2
            dlg.geometry(f"{w}x{h}+{x}+{y}")
        self._root.after(0, _do); done.wait(); return result[0]
