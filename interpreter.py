# interpreter.py — Neglish v4.1 Full Runtime
# Independent language: no Python imports needed in user code

from __future__ import annotations
import sys, os, math, random, time, json, subprocess, re, hashlib
import threading, copy, uuid as _uuid_mod, platform as _platform_mod
import importlib, traceback
from urllib.parse import urlparse
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler

# ══════════════════════════════════════════════ signals
class ReturnSignal(Exception):
    def __init__(self, v): self.value = v
class BreakSignal(Exception): pass
class ContinueSignal(Exception): pass
class ThrowSignal(Exception):
    def __init__(self, v): self.value = v
class NegRuntimeError(Exception):
    def __init__(self, msg, line=0):
        super().__init__(f"[Line {line}] Runtime Error: {msg}")

# ══════════════════════════════════════════════ ANSI
ANSI = {
    'red':'\033[91m','green':'\033[92m','yellow':'\033[93m',
    'blue':'\033[94m','magenta':'\033[95m','cyan':'\033[96m',
    'white':'\033[97m','black':'\033[30m','reset':'\033[0m',
    'bold':'\033[1m','italic':'\033[3m','dim':'\033[2m',
    'underline':'\033[4m','strike':'\033[9m',
    'bg_red':'\033[41m','bg_green':'\033[42m','bg_blue':'\033[44m',
    'bg_yellow':'\033[43m','bg_cyan':'\033[46m','bg_white':'\033[47m',
}
def colorize(color, text):
    code = ANSI.get(str(color).lower(), '')
    return f"{code}{text}{ANSI['reset']}" if code else str(text)

# ══════════════════════════════════════════════ smart coerce
def _num(v):
    if isinstance(v, bool): return int(v)
    if isinstance(v, (int, float)): return v
    if isinstance(v, str):
        s = v.strip()
        try: return int(s)
        except ValueError: pass
        try: return float(s)
        except ValueError: pass
    return v

def _add(a, b):
    an, bn = _num(a), _num(b)
    if isinstance(an, (int,float)) and isinstance(bn, (int,float)):
        return an + bn
    return str('' if a is None else a) + str('' if b is None else b)

def _arith(op, a, b):
    if op == '+': return _add(a, b)
    an, bn = _num(a) or 0, _num(b) or 0
    if op == '-': return an - bn
    if op == '*':
        if isinstance(an,(int,float)) and isinstance(bn,(int,float)): return an * bn
        if isinstance(a, str) and isinstance(bn,(int,float)): return a * int(bn)
        return 0
    if op == '/': return an / bn if bn else 0
    if op == '%': return an % bn if bn else 0
    if op in ('**','^'): return an ** bn
    return 0

def _truthy(v):
    if v is None or v is False: return False
    if v == 0 or v == '': return False
    if isinstance(v,(list,dict)) and len(v)==0: return False
    return True

# ══════════════════════════════════════════════ environment
class Environment:
    def __init__(self, parent=None):
        self.vars   = {}
        self.parent = parent
        self._frozen = set()

    def get(self, name):
        if name in self.vars: return self.vars[name]
        if self.parent: return self.parent.get(name)
        return None

    def set(self, name, value): self.vars[name] = value

    def assign(self, name, value):
        if name in self._frozen:
            raise NegRuntimeError(f"'{name}' is frozen (constant) and cannot be changed")
        if not self._update(name, value):
            self.vars[name] = value

    def _update(self, name, value):
        if name in self.vars:
            if name in self._frozen:
                raise NegRuntimeError(f"'{name}' is frozen")
            self.vars[name] = value; return True
        if self.parent: return self.parent._update(name, value)
        return False

    def freeze(self, name): self._frozen.add(name)
    def delete(self, name):
        if name in self.vars: del self.vars[name]

    def global_env(self):
        e = self
        while e.parent: e = e.parent
        return e

    def snapshot(self):
        """Return a plain dict snapshot of all visible vars."""
        d = {}
        if self.parent: d.update(self.parent.snapshot())
        d.update(self.vars)
        return d

# ══════════════════════════════════════════════ Neglish objects

class NegFunction:
    def __init__(self, name, params, body, closure, is_async=False, is_memo=False, defaults=None):
        self.name, self.params, self.body = name, params, body
        self.closure, self.is_async = closure, is_async
        self.defaults = defaults or {}
        self._cache = {} if is_memo else None
    def __repr__(self): return f"<function {self.name}>"

class NegClass:
    def __init__(self, name, parent, body, closure):
        self.name, self.parent = name, parent
        self.body, self.closure = body, closure
    def __repr__(self): return f"<class {self.name}>"

class NegObject:
    def __init__(self, class_name):
        self.class_name = class_name
        self.props = {}
    def get(self, k): return self.props.get(k)
    def set(self, k, v): self.props[k] = v
    def __repr__(self): return f"<{self.class_name} object>"

class NegLambda:
    """Anonymous function created by lambda expr."""
    def __init__(self, params, body_expr, closure):
        self.params = params
        self.body_expr = body_expr  # single expression (not a block)
        self.closure = closure
    def __repr__(self): return f"<lambda ({', '.join(self.params)})>"

class NegFile:
    def __init__(self, path, mode):
        self.path, self.mode = path, mode
        self.handle = open(path, mode, encoding='utf-8')
    def __repr__(self): return f"<file {self.path!r}>"

class NegModule:
    def __init__(self, name, env, exports=None):
        self.name, self.env = name, env
        self.exports = exports or list(env.vars.keys())
    def get(self, k):
        if k in self.exports or not self.exports:
            return self.env.vars.get(k)
        return None
    def __repr__(self): return f"<module {self.name}>"

class NegTask:
    def __init__(self, thread): self.thread = thread; self.result = None
    def join(self): self.thread.join(); return self.result
    def __repr__(self): return f"<task>"

# ══════════════════════════════════════════════ test runner
class TestRunner:
    def __init__(self):
        self.passed = 0; self.failed = 0; self.errors = []
        self._suite = None

    def begin_suite(self, name): self._suite = name

    def run_expect(self, got, expected, line=0):
        label = f"[{self._suite}] " if self._suite else ""
        if got == expected:
            self.passed += 1
            print(colorize('green', f"  ✓ {label}PASS"))
        else:
            self.failed += 1
            self.errors.append((line, got, expected))
            print(colorize('red', f"  ✗ {label}FAIL: expected {expected!r}, got {got!r}"))

    def run_check(self, val, msg=None, line=0):
        label = f"[{self._suite}] " if self._suite else ""
        if _truthy(val):
            self.passed += 1
            print(colorize('green', f"  ✓ {label}PASS"))
        else:
            self.failed += 1
            m = msg or "check failed"
            print(colorize('red', f"  ✗ {label}FAIL: {m}"))

    def summary(self):
        total = self.passed + self.failed
        print(colorize('bold', f"\n── Test Results: {self.passed}/{total} passed ──"))
        if self.failed == 0: print(colorize('green', "  All tests passed! ✓"))
        return self.failed == 0

# ══════════════════════════════════════════════ stdlib (100% Neglish-native)

# ── Networking stdlib helpers ─────────────────────────────────────────────────
def _http_get_fn(url, timeout=15, headers=None):
    import urllib.request
    hdr = {'User-Agent': 'Neglish/4.1'}
    if isinstance(headers, dict): hdr.update(headers)
    try:
        req = urllib.request.Request(str(url), headers=hdr)
        with urllib.request.urlopen(req, timeout=float(timeout)) as r:
            return {'body': r.read().decode('utf-8','replace'), 'status': r.status, 'ok': r.status < 400}
    except Exception as e:
        return {'body': str(e), 'status': 0, 'ok': False}

def _http_post_fn(url, data=None, json_data=None, headers=None, timeout=15):
    import urllib.request, urllib.parse, json as _json
    hdr = {'User-Agent': 'Neglish/4.1'}
    if json_data is not None:
        hdr['Content-Type'] = 'application/json'
        payload = _json.dumps(json_data).encode()
    elif isinstance(data, dict):
        hdr['Content-Type'] = 'application/x-www-form-urlencoded'
        payload = urllib.parse.urlencode(data).encode()
    else:
        payload = str(data or '').encode()
    if isinstance(headers, dict): hdr.update(headers)
    try:
        req = urllib.request.Request(str(url), data=payload, headers=hdr, method='POST')
        with urllib.request.urlopen(req, timeout=float(timeout)) as r:
            return {'body': r.read().decode('utf-8','replace'), 'status': r.status, 'ok': r.status < 400}
    except Exception as e:
        return {'body': str(e), 'status': 0, 'ok': False}

def _fetch_json_fn(url, timeout=15):
    import urllib.request, json as _json
    try:
        req = urllib.request.Request(str(url), headers={'User-Agent':'Neglish/4.1','Accept':'application/json'})
        with urllib.request.urlopen(req, timeout=float(timeout)) as r:
            return _json.loads(r.read().decode('utf-8','replace'))
    except Exception as e:
        return {'error': str(e)}

def _download_fn(url, dest_path, timeout=30):
    import urllib.request
    try:
        urllib.request.urlretrieve(str(url), str(dest_path))
        return True
    except Exception:
        return False

def _make_stdlib():
    return {
        # ── Math
        'length':         lambda a: len(a) if hasattr(a,'__len__') else 0,
        'sqrt':           lambda a: math.sqrt(float(_num(a))),
        'abs':            lambda a: abs(_num(a)),
        'floor':          lambda a: int(math.floor(float(_num(a)))),
        'ceil':           lambda a: int(math.ceil(float(_num(a)))),
        'round':          lambda a: round(float(_num(a))),
        'power':          lambda a,b: _num(a) ** _num(b),
        'random_between': lambda a,b: random.randint(int(_num(a)), int(_num(b))),
        'random_float':   lambda a,b: random.uniform(float(_num(a)), float(_num(b))),
        'max':            lambda a,b: max(_num(a), _num(b)),
        'min':            lambda a,b: min(_num(a), _num(b)),
        'clamp':          lambda v,lo,hi: max(_num(lo), min(_num(hi), _num(v))),
        'lerp':           lambda a,b,t: _num(a)+(_num(b)-_num(a))*_num(t),
        'sign':           lambda a: (1 if _num(a)>0 else -1 if _num(a)<0 else 0),
        'log10':          lambda a: math.log10(float(_num(a))),
        'log2':           lambda a: math.log2(float(_num(a))),
        'sin':            lambda a: math.sin(math.radians(float(_num(a)))),
        'cos':            lambda a: math.cos(math.radians(float(_num(a)))),
        'tan':            lambda a: math.tan(math.radians(float(_num(a)))),
        'asin':           lambda a: math.degrees(math.asin(float(_num(a)))),
        'acos':           lambda a: math.degrees(math.acos(float(_num(a)))),
        'atan':           lambda a: math.degrees(math.atan(float(_num(a)))),
        'degrees':        lambda a: math.degrees(float(_num(a))),
        'radians':        lambda a: math.radians(float(_num(a))),
        'gcd':            lambda a,b: math.gcd(int(_num(a)), int(_num(b))),
        'lcm':            lambda a,b: abs(int(_num(a))*int(_num(b)))//math.gcd(int(_num(a)),int(_num(b))) if _num(a) and _num(b) else 0,
        'mod':            lambda a,b: _num(a) % _num(b),
        'is_even':        lambda a: _num(a) % 2 == 0,
        'is_odd':         lambda a: _num(a) % 2 != 0,
        'is_prime':       lambda a: _is_prime(int(_num(a))),
        'factorial':      lambda a: math.factorial(int(_num(a))),
        'fibonacci':      lambda a: _fib(int(_num(a))),

        # ── Type conversion
        'to_number':      lambda a: _num(a) if isinstance(_num(a),(int,float)) else 0,
        'to_string':      lambda a: '' if a is None else str(a),
        'to_bool':        lambda a: _truthy(a),
        'to_list':        lambda a: list(a) if hasattr(a,'__iter__') and not isinstance(a,str) else [a],
        'type_of':        lambda a: (
            'number' if isinstance(a,(int,float)) and not isinstance(a,bool) else
            'bool'   if isinstance(a,bool) else
            'string' if isinstance(a,str)  else
            'list'   if isinstance(a,list) else
            'dict'   if isinstance(a,dict) else
            'null'   if a is None          else
            'function' if isinstance(a,NegFunction) else
            'object' if isinstance(a,NegObject) else 'object'),
        'is_number':      lambda a: isinstance(a,(int,float)) and not isinstance(a,bool),
        'is_string':      lambda a: isinstance(a,str),
        'is_list':        lambda a: isinstance(a,list),
        'is_dict':        lambda a: isinstance(a,dict),
        'is_null':        lambda a: a is None,
        'is_bool':        lambda a: isinstance(a,bool),

        # ── String
        'uppercase':      lambda a: str(a).upper(),
        'lowercase':      lambda a: str(a).lower(),
        'titlecase':      lambda a: str(a).title(),
        'camelcase':      lambda a: _to_camel(str(a)),
        'snakecase':      lambda a: re.sub(r'(?<!^)(?=[A-Z])','_',str(a)).lower(),
        'trim':           lambda a: str(a).strip(),
        'trim_left':      lambda a: str(a).lstrip(),
        'trim_right':     lambda a: str(a).rstrip(),
        'reverse':        lambda a: str(a)[::-1] if isinstance(a,str) else list(reversed(a)),
        'split':          lambda a,b: str(a).split(str(b)),
        'split_lines':    lambda a: str(a).splitlines(),
        'join':           lambda a,b: str(b).join(str(x) for x in a),
        'replace':        lambda a,b,c: str(a).replace(str(b),str(c)),
        'replace_regex':  lambda a,b,c: re.sub(str(b),str(c),str(a)),
        'contains':       lambda a,b: (str(b) in str(a)) if isinstance(a,str) else (b in a),
        'starts_with':    lambda a,b: str(a).startswith(str(b)),
        'ends_with':      lambda a,b: str(a).endswith(str(b)),
        'substring':      lambda a,b,c: str(a)[int(_num(b))-1:int(_num(c))],
        'char_at':        lambda a,b: str(a)[int(_num(b))-1] if 0<=int(_num(b))-1<len(str(a)) else '',
        'char_code':      lambda a: ord(str(a)[0]) if str(a) else 0,
        'from_code':      lambda a: chr(int(_num(a))),
        'index_of':       lambda a,b: (list(b).index(a)+1) if isinstance(b,list) else (str(b).find(str(a))+1),
        'slice':          lambda a,b,c: a[int(_num(b))-1:int(_num(c))],
        'pad_left':       lambda a,n,ch=' ': str(a).rjust(int(_num(n)),str(ch)[0]),
        'pad_right':      lambda a,n,ch=' ': str(a).ljust(int(_num(n)),str(ch)[0]),
        'repeat_str':     lambda a,n: str(a)*int(_num(n)),
        'count_of':       lambda a,b: str(a).count(str(b)) if isinstance(a,str) else list(a).count(b),
        'format_str':     lambda t,*args: str(t).format(*args),
        'matches':        lambda a,b: bool(re.fullmatch(str(b),str(a))),
        'find_all':       lambda a,b: re.findall(str(b),str(a)),
        'number_format':  lambda n,dp=2: f'{float(_num(n)):,.{int(_num(dp))}f}',
        'pluralize':      lambda w,n: str(w)+('s' if _num(n)!=1 else ''),
        'uuid':           lambda *_: str(_uuid_mod.uuid4()),
        'hash_of':        lambda a,algo='sha256': hashlib.new(str(algo),str(a).encode()).hexdigest(),

        # ── List
        'sum':            lambda a: sum(_num(x) for x in a) if isinstance(a,list) else 0,
        'average':        lambda a: (sum(_num(x) for x in a)/len(a)) if isinstance(a,list) and len(a) else 0,
        'median':         lambda a: _median(a),
        'variance':       lambda a: _variance(a),
        'stdev':          lambda a: math.sqrt(_variance(a)),
        'unique':         lambda a: list(dict.fromkeys(a)),
        'flatten':        lambda a: _flatten(a),
        'flatten_deep':   lambda a: _flatten_deep(a),
        'sort':           lambda a: sorted(a, key=lambda x:(_num(x) if isinstance(_num(x),(int,float)) else 0, str(x))),
        'sort_desc':      lambda a: sorted(a, key=lambda x:(_num(x) if isinstance(_num(x),(int,float)) else 0, str(x)), reverse=True),
        'shuffle':        lambda a: (random.shuffle(a),a)[1] if isinstance(a,list) else a,
        'count':          lambda a: len(a) if hasattr(a,'__len__') else 0,
        'first':          lambda a: a[0] if a else None,
        'last':           lambda a: a[-1] if a else None,
        'is_empty':       lambda a: (len(a)==0 if hasattr(a,'__len__') else a is None),
        'take':           lambda a,n: a[:int(_num(n))],
        'drop':           lambda a,n: a[int(_num(n)):],
        'chunk':          lambda a,n: [a[i:i+int(_num(n))] for i in range(0,len(a),int(_num(n)))],
        'compact':        lambda a: [x for x in a if _truthy(x)],
        'zip_pairs':      lambda a,b: list(zip(a,b)),
        'enumerate_list': lambda a: [[i+1,v] for i,v in enumerate(a)],
        'range_list':     lambda a,b,s=1: list(range(int(_num(a)),int(_num(b))+1,int(_num(s)))),
        'contains_all':   lambda a,b: all(x in a for x in b),
        'contains_any':   lambda a,b: any(x in a for x in b),
        'intersection':   lambda a,b: [x for x in a if x in b],
        'difference':     lambda a,b: [x for x in a if x not in b],
        'union':          lambda a,b: list(dict.fromkeys(list(a)+list(b))),
        'max_of':         lambda a: max((_num(x) for x in a),default=0),
        'min_of':         lambda a: min((_num(x) for x in a),default=0),
        'pluck':          lambda a,k: [x.get(k) if isinstance(x,dict) else None for x in a],

        # ── Dict
        'dict_keys':      lambda d: list(d.keys()) if isinstance(d,dict) else [],
        'dict_values':    lambda d: list(d.values()) if isinstance(d,dict) else [],
        'dict_has':       lambda d,k: k in d if isinstance(d,dict) else False,
        'dict_merge':     lambda a,b: {**a, **b},
        'dict_size':      lambda d: len(d) if isinstance(d,dict) else 0,
        'dict_to_list':   lambda d: [[k,v] for k,v in d.items()] if isinstance(d,dict) else [],

        # ── Time/Date
        'now':            lambda *_: time.strftime('%H:%M:%S'),
        'today':          lambda *_: time.strftime('%Y-%m-%d'),
        'timestamp':      lambda *_: int(time.time()),
        'time_ms':        lambda *_: int(time.time()*1000),
        'year':           lambda *_: int(time.strftime('%Y')),
        'month':          lambda *_: int(time.strftime('%m')),
        'day':            lambda *_: int(time.strftime('%d')),
        'hour':           lambda *_: int(time.strftime('%H')),
        'minute':         lambda *_: int(time.strftime('%M')),
        'second':         lambda *_: int(time.strftime('%S')),
        'weekday':        lambda *_: time.strftime('%A'),
        'date_format':    lambda fmt: time.strftime(str(fmt)),

        # ── System / OS
        'platform':       lambda *_: _platform_mod.system(),
        'username':       lambda *_: os.environ.get('USERNAME') or os.environ.get('USER','unknown'),
        'hostname':       lambda *_: _platform_mod.node(),
        'pid':            lambda *_: os.getpid(),
        'cwd':            lambda *_: os.getcwd(),
        'sep':            lambda *_: os.sep,
        'env_get':        lambda k: os.environ.get(str(k), ''),

        # ── File system
        'file_exists':    lambda p: os.path.exists(str(p)),
        'is_file':        lambda p: os.path.isfile(str(p)),
        'is_dir':         lambda p: os.path.isdir(str(p)),
        'file_size':      lambda p: os.path.getsize(str(p)) if os.path.exists(str(p)) else 0,
        'file_ext':       lambda p: os.path.splitext(str(p))[1],
        'file_name':      lambda p: os.path.basename(str(p)),
        'file_dir':       lambda p: os.path.dirname(str(p)),
        'list_dir':       lambda p: os.listdir(str(p)) if os.path.isdir(str(p)) else [],
        'path_join':      lambda *parts: os.path.join(*[str(p) for p in parts]),
        'read_file':      lambda p: open(str(p),'r',encoding='utf-8').read() if os.path.exists(str(p)) else '',
        'write_file':     lambda p,c: open(str(p),'w',encoding='utf-8').write(str(c)) and None,
        'append_file':    lambda p,c: open(str(p),'a',encoding='utf-8').write(str(c)) and None,

        # ── JSON
        'json_parse':     lambda s: json.loads(str(s)),
        'json_stringify': lambda v: json.dumps(v, ensure_ascii=False),
        'json_pretty':    lambda v: json.dumps(v, indent=2, ensure_ascii=False),

        # ── Input
        'input_inline':   lambda p='': input(str(p)+' ' if p else ''),

        # ── Misc unique
        'sleep_ms':       lambda ms: time.sleep(float(_num(ms))/1000),
        'run_cmd':        lambda cmd: subprocess.getoutput(str(cmd)),
        'env_get':        lambda k: os.environ.get(str(k),''),
        'choice':         lambda lst: random.choice(lst) if lst else None,
        'sample':         lambda lst,n: random.sample(lst, int(_num(n))),
        'weighted_choice':lambda items,weights: random.choices(items,weights=weights,k=1)[0],
        'between':        lambda v,lo,hi: _num(lo) <= _num(v) <= _num(hi),
        'percent_of':     lambda p,total: (_num(p)/_num(total)*100) if _num(total) else 0,
        'percent':        lambda p,total: round(_num(p)/_num(total)*100,2) if _num(total) else 0,
        'interpolate':    lambda t,a,b: str(a)+str(t)+str(b),

        # ── Networking builtins (v4.1)
        'url_encode':     lambda s: __import__('urllib.parse', fromlist=['quote']).quote(str(s), safe=''),
        'url_decode':     lambda s: __import__('urllib.parse', fromlist=['unquote']).unquote(str(s)),
        'base64_encode':  lambda s: __import__('base64').b64encode(str(s).encode()).decode(),
        'base64_decode':  lambda s: __import__('base64').b64decode(str(s)).decode('utf-8', errors='replace'),
        'parse_url':      lambda url: dict(zip(
            ['scheme','netloc','path','params','query','fragment'],
            __import__('urllib.parse', fromlist=['urlparse']).urlparse(str(url))
        )),
        'build_url':      lambda base, **kw: base + ('?' + __import__('urllib.parse', fromlist=['urlencode']).urlencode(kw) if kw else ''),
        'http_get':       _http_get_fn,
        'http_post':      _http_post_fn,
        'fetch_json':     _fetch_json_fn,
        'download':       _download_fn,
    }

# ── math helpers
def _is_prime(n):
    if n < 2: return False
    if n < 4: return True
    if n % 2 == 0 or n % 3 == 0: return False
    i = 5
    while i*i <= n:
        if n%i==0 or n%(i+2)==0: return False
        i += 6
    return True

def _fib(n):
    a, b = 0, 1
    for _ in range(n): a, b = b, a+b
    return a

def _flatten(lst):
    out = []
    for x in lst:
        if isinstance(x,list): out.extend(x)
        else: out.append(x)
    return out

def _flatten_deep(lst):
    out = []
    for x in lst:
        if isinstance(x,list): out.extend(_flatten_deep(x))
        else: out.append(x)
    return out

def _median(lst):
    if not lst: return 0
    s = sorted(_num(x) for x in lst)
    n = len(s)
    return s[n//2] if n%2 else (s[n//2-1]+s[n//2])/2

def _variance(lst):
    if not lst: return 0
    nums = [_num(x) for x in lst]
    avg = sum(nums)/len(nums)
    return sum((x-avg)**2 for x in nums)/len(nums)

def _to_camel(s):
    parts = re.split(r'[\s_-]+', s)
    return parts[0].lower() + ''.join(p.capitalize() for p in parts[1:])

# ══════════════════════════════════════════════ interpreter
class Interpreter:
    _MODULE_CACHE = {}

    def __init__(self, gui_manager=None, source_dir='.'):
        self.global_env  = Environment()
        self.gui         = gui_manager
        self._builtins   = _make_stdlib()
        self._events     = {}
        self._files      = {}
        self._classes    = {}
        self._once_done  = set()
        self._watchers   = {}   # var_name → [body, env]
        self._timers     = []
        self._test       = TestRunner()
        self._exports    = []
        self._pkg_name   = None
        self.source_dir  = source_dir
        self._frozen     = set()
        self._output     = []
        self._servers    = {}

        # Built-in constants
        G = self.global_env
        G.set('PI',      math.pi)
        G.set('E',       math.e)
        G.set('TAU',     math.tau)
        G.set('INF',     float('inf'))
        G.set('NAN',     float('nan'))
        G.set('NL',      '\n')
        G.set('TAB',     '\t')
        G.set('VERSION', '4.3')
        G.set('ARGS',    sys.argv[2:])
        G.set('TRUE',    True)
        G.set('FALSE',   False)
        G.set('NULL',    None)

    # ─────────────────────────────── output
    def _print(self, text):
        s = str(text)
        print(s)
        self._output.append(s)
        if self.gui: self.gui.log(s)

    # ─────────────────────────────── run
    def run(self, stmts):
        try:
            self.exec_block(stmts, self.global_env)
        except ReturnSignal:
            pass  # top-level return is allowed (module exit)

    def exec_block(self, stmts, env):
        for s in stmts:
            self.exec_stmt(s, env)

    def exec_stmt(self, stmt, env):  # noqa: C901
        t    = stmt['type']
        line = stmt.get('line', 0)

        # ── output ───────────────────────────────────────────────────
        if t == 'show':
            parts = [self.eval_expr(p, env) for p in stmt['parts']]
            out = ' '.join('' if p is None else str(p) for p in parts)
            self._print(out)

        elif t == 'colored_show':
            self._print(colorize(stmt['color'], self.eval_expr(stmt['expr'], env)))

        elif t == 'debug':
            val = self.eval_expr(stmt['expr'], env)
            self._print(colorize('cyan', f"[DEBUG] {repr(val)}"))

        elif t == 'inspect':
            name = stmt['name']
            val  = env.get(name)
            tp   = self._builtins['type_of'](val)
            self._print(colorize('yellow', f"[INSPECT] {name} = {repr(val)} ({tp})"))

        elif t == 'trace':
            snap = env.snapshot()
            self._print(colorize('dim', "[TRACE] " + json.dumps({k:str(v) for k,v in snap.items()}, indent=2)))

        # ── variables ────────────────────────────────────────────────
        elif t == 'set':
            val = self.eval_expr(stmt['expr'], env)
            env.assign(stmt['name'], val)
            self._notify_watchers(stmt['name'], val, env)

        elif t == 'increase':
            name = stmt['name']
            amt = _num(self.eval_expr(stmt['expr'], env))
            if '.' in str(name):
                parts = name.split('.')
                obj = env.get(parts[0])
                if isinstance(obj, NegObject):
                    cur = _num(obj.get(parts[1]) or 0)
                    obj.set(parts[1], cur + amt)
                else: env.assign(name, _num(env.get(name) or 0) + amt)
            else:
                env.assign(name, _num(env.get(name) or 0) + amt)

        elif t == 'decrease':
            name = stmt['name']
            amt = _num(self.eval_expr(stmt['expr'], env))
            if '.' in str(name):
                parts = name.split('.')
                obj = env.get(parts[0])
                if isinstance(obj, NegObject):
                    cur = _num(obj.get(parts[1]) or 0)
                    obj.set(parts[1], cur - amt)
                else: env.assign(name, _num(env.get(name) or 0) - amt)
            else:
                env.assign(name, _num(env.get(name) or 0) - amt)

        elif t == 'compound_assign':
            cur = env.get(stmt['name'])
            val = self.eval_expr(stmt['expr'], env)
            op  = stmt['op']
            new = val if op=='=' else _arith(op[0], cur, val)
            env.assign(stmt['name'], new)
            self._notify_watchers(stmt['name'], new, env)

        elif t == 'delete_var':
            env.delete(stmt['name'])

        elif t == 'global_decl':
            pass

        elif t == 'freeze':
            env.global_env().freeze(stmt['name'])
            self._frozen.add(stmt['name'])

        elif t == 'dot_assign':
            # set obj.prop to val  OR  class_instance.field = val
            parts = stmt['path'].split('.')
            obj = env.get(parts[0])
            val = self.eval_expr(stmt['expr'], env)
            op  = stmt.get('op', '=')
            if len(parts) == 2:
                prop = parts[1]
                if isinstance(obj, NegObject):
                    if op == '=':
                        obj.set(prop, val)
                    else:
                        cur = obj.get(prop) or 0
                        obj.set(prop, _arith(op[0], cur, val))
                elif isinstance(obj, dict):
                    if op == '=': obj[prop] = val
                    else: obj[prop] = _arith(op[0], obj.get(prop,0), val)
                else:
                    env.assign(parts[0] + '__' + prop, val)
            elif len(parts) >= 3:
                # deep: a.b.c = val
                cur = obj
                for part in parts[1:-1]:
                    if isinstance(cur, NegObject): cur = cur.get(part)
                    elif isinstance(cur, dict): cur = cur.get(part)
                last = parts[-1]
                if isinstance(cur, NegObject): cur.set(last, val)
                elif isinstance(cur, dict): cur[last] = val

        elif t == 'index_assign':
            c = env.get(stmt['name'])
            k = self.eval_expr(stmt['key'], env)
            v = self.eval_expr(stmt['value'], env)
            if isinstance(c, list):   c[int(_num(k))-1] = v
            elif isinstance(c, dict): c[k] = v

        elif t == 'update_label':
            if self.gui:
                self.gui.update_label(stmt['name'], str(self.eval_expr(stmt['expr'], env)))

        elif t == 'read_entry':
            if self.gui:
                raw = self.gui.get_entry_value(stmt['entry'])
                env.assign(stmt['var'], _num(raw) if raw.strip().lstrip('-').replace('.','',1).isdigit() else raw)

        elif t == 'set_entry':
            if self.gui:
                self.gui.set_entry_value(stmt['name'], str(self.eval_expr(stmt['expr'], env)))

        elif t == 'package_decl':
            self._pkg_name = stmt['name']

        elif t == 'export':
            self._exports.append(stmt['name'])

        # ── control flow ─────────────────────────────────────────────
        elif t == 'if':
            if self.eval_truthy(stmt['cond'], env):
                self.exec_block(stmt['body'], Environment(env))
            else:
                fired = False
                for branch in stmt.get('elseif', []):
                    if self.eval_truthy(branch['cond'], env):
                        self.exec_block(branch['body'], Environment(env))
                        fired = True; break
                if not fired and stmt.get('else'):
                    self.exec_block(stmt['else'], Environment(env))

        elif t == 'repeat':
            count = int(_num(self.eval_expr(stmt['count'], env)))
            var   = stmt.get('var')
            for i in range(count):
                local = Environment(env)
                if var: local.set(var, i+1)
                try:    self.exec_block(stmt['body'], local)
                except BreakSignal:    break
                except ContinueSignal: continue

        elif t == 'while':
            iters = 0
            while self.eval_truthy(stmt['cond'], env):
                iters += 1
                if iters > 2_000_000: raise NegRuntimeError("Infinite loop guard (>2M iters)", line)
                try:    self.exec_block(stmt['body'], Environment(env))
                except BreakSignal:    break
                except ContinueSignal: continue

        elif t == 'for_each':
            lst = self.eval_expr(stmt['list'], env)
            it  = list(lst.keys()) if isinstance(lst, dict) else (list(lst) if isinstance(lst,(list,str)) else [])
            idx_var = stmt.get('idx_var')
            for idx, item in enumerate(it):
                local = Environment(env)
                local.set(stmt['var'], item)
                if idx_var: local.set(idx_var, idx)
                try:    self.exec_block(stmt['body'], local)
                except BreakSignal:    break
                except ContinueSignal: continue

        elif t == 'for_range':
            start = int(_num(self.eval_expr(stmt['start'], env)))
            end   = int(_num(self.eval_expr(stmt['end'],   env)))
            step  = int(_num(self.eval_expr(stmt['step'],  env))) if stmt.get('step') else 1
            for i in range(start, end+1, step):
                local = Environment(env)
                local.set(stmt['var'], i)
                try:    self.exec_block(stmt['body'], local)
                except BreakSignal:    break
                except ContinueSignal: continue

        elif t == 'forever':
            iters = 0
            while True:
                iters += 1
                if iters > 2_000_000: raise NegRuntimeError("Infinite loop guard", line)
                try:    self.exec_block(stmt['body'], Environment(env))
                except BreakSignal:  break
                except ContinueSignal: continue

        elif t == 'match':
            val = self.eval_expr(stmt['expr'], env)
            fired = False
            for case in stmt['cases']:
                cv = case['value']
                # wildcard _ matches everything
                if cv.get('type') == 'wildcard':
                    if case.get('guard'):
                        if not self.eval_truthy(case['guard'], env): continue
                    self.exec_block(case['body'], Environment(env))
                    fired = True; break
                # tuple/range: [lo, hi]
                case_val = self.eval_expr(cv, env)
                if val == case_val:
                    if case.get('guard'):
                        local = Environment(env)
                        local.set('it', val)
                        if not self.eval_truthy(case['guard'], local): continue
                    self.exec_block(case['body'], Environment(env))
                    fired = True; break
                # type-based matching: is_number, is_string, etc.
            if not fired and stmt.get('default'):
                self.exec_block(stmt['default'], Environment(env))

        elif t == 'switch':
            val = self.eval_expr(stmt['expr'], env)
            fired = False
            for case in stmt['cases']:
                cv = self.eval_expr(case['value'], env)
                if val == cv:
                    self.exec_block(case['body'], Environment(env))
                    fired = True; break
            if not fired and stmt.get('default'):
                self.exec_block(stmt['default'], Environment(env))

        elif t == 'break':    raise BreakSignal()
        elif t == 'continue': raise ContinueSignal()

        # ── functions ─────────────────────────────────────────────────
        elif t == 'define':
            defaults_raw = stmt.get('defaults', {})
            defaults_evaled = {k: self.eval_expr(v, env) for k, v in defaults_raw.items()}
            fn = NegFunction(stmt['name'], stmt['params'], stmt['body'], env, defaults=defaults_evaled)
            env.assign(stmt['name'], fn)

        elif t == 'async_define':
            defaults_raw = stmt.get('defaults', {})
            defaults_evaled = {k: self.eval_expr(v, env) for k, v in defaults_raw.items()}
            fn = NegFunction(stmt['name'], stmt['params'], stmt['body'], env, is_async=True, defaults=defaults_evaled)
            env.assign(stmt['name'], fn)

        elif t == 'memo_define':
            defaults_raw = stmt.get('defaults', {})
            defaults_evaled = {k: self.eval_expr(v, env) for k, v in defaults_raw.items()}
            fn = NegFunction(stmt['name'], stmt['params'], stmt['body'], env, is_memo=True, defaults=defaults_evaled)
            env.assign(stmt['name'], fn)

        elif t == 'call':
            self._call_fn(stmt['name'], stmt['args'], env, line)

        elif t == 'call_store':
            result = self._call_fn(stmt['name'], stmt['args'], env, line)
            env.assign(stmt['var'], result)

        elif t == 'return':
            val = self.eval_expr(stmt['expr'], env) if stmt.get('expr') else None
            raise ReturnSignal(val)

        # ── data pipelines ─────────────────────────────────────────────
        elif t == 'pipe_filter':
            lst = self.eval_expr(stmt['list'], env)
            if not isinstance(lst, list): raise NegRuntimeError("filter requires a list", line)
            result = []
            for item in lst:
                local = Environment(env)
                local.set(stmt['var'], item)
                if self.eval_truthy(stmt['cond'], local):
                    result.append(item)
            if stmt.get('result'): env.assign(stmt['result'], result)
            else: env.assign('_', result)

        elif t == 'pipe_map':
            lst = self.eval_expr(stmt['list'], env)
            if not isinstance(lst, list): raise NegRuntimeError("map requires a list", line)
            result = []
            for item in lst:
                local = Environment(env)
                local.set(stmt['var'], item)
                result.append(self.eval_expr(stmt['transform'], local))
            if stmt.get('result'): env.assign(stmt['result'], result)
            else: env.assign('_', result)

        elif t == 'pipe_reduce':
            lst = self.eval_expr(stmt['list'], env)
            if not isinstance(lst, list): raise NegRuntimeError("reduce requires a list", line)
            acc = self.eval_expr(stmt['start'], env)
            for item in lst:
                local = Environment(env)
                local.set('acc', acc)
                local.set(stmt['var'], item)
                local.set('s', item)  # alias 's' for common use
                local.set('total', acc)  # alias 'total' for readability
                new_acc = self.eval_expr(stmt['op_expr'], local)
                acc = new_acc
            if stmt.get('result'): env.assign(stmt['result'], acc)
            else: env.assign('_', acc)

        elif t == 'collect':
            lst = self.eval_expr(stmt['list'], env)
            result = []
            for item in (lst if isinstance(lst, list) else []):
                local = Environment(env)
                local.set(stmt['var'], item)
                if stmt.get('cond') is None or self.eval_truthy(stmt['cond'], local):
                    result.append(item)
            target = stmt.get('result') or '_'
            env.assign(target, result)

        elif t == 'pipe':
            val = self.eval_expr(stmt['expr'], env)
            for fn_name in stmt['fns']:
                fn = env.get(fn_name)
                if isinstance(fn, NegFunction):
                    val = self._call_fn(fn_name, [], env, line, inject_first=val)
                else:
                    impl = self._builtins.get(fn_name)
                    if impl: val = impl(val)
            if stmt.get('result'): env.assign(stmt['result'], val)

        # ── input ─────────────────────────────────────────────────────
        elif t == 'ask':
            prompt = self.eval_expr(stmt['prompt'], env)
            if self.gui:
                raw = self.gui.ask_input(str(prompt))
            else:
                raw = input(str(prompt) + ' ' if prompt else '')
            val = _num(raw) if isinstance(raw, str) and raw.strip().lstrip('-').replace('.','',1).isdigit() else raw
            env.assign(stmt['var'], val)

        # ── testing framework ──────────────────────────────────────────
        elif t == 'describe_block':
            name = self.eval_expr(stmt['name'], env)
            self._test.begin_suite(str(name))
            print(colorize('bold', f"\n◈ {name}"))
            self.exec_block(stmt['body'], Environment(env))

        elif t == 'test_block':
            name = self.eval_expr(stmt['name'], env)
            print(colorize('dim', f"  ▸ {name}"))
            try:
                self.exec_block(stmt['body'], Environment(env))
            except ThrowSignal as e:
                self._test.failed += 1
                print(colorize('red', f"    ✗ THROW: {e.value}"))

        elif t == 'expect_stmt':
            got      = self.eval_expr(stmt['expr'], env)
            expected = self.eval_expr(stmt['expected'], env)
            self._test.run_expect(got, expected, line)

        elif t == 'check_stmt':
            val = self.eval_truthy(stmt['cond'], env) if 'cond' in stmt else self.eval_truthy(stmt['expr'], env)
            msg = self.eval_expr(stmt['msg'], env) if stmt.get('msg') else None
            self._test.run_check(val, msg, line)

        # ── observer / watcher ─────────────────────────────────────────
        elif t == 'watch':
            name = stmt['name']
            self._watchers.setdefault(name, []).append({'body': stmt['body'], 'env': env})

        elif t == 'once_decl':
            pass  # marks next call as run-once

        # ── async / timing ─────────────────────────────────────────────
        elif t == 'spawn':
            fn_name = stmt['name']
            args    = stmt['args']
            interp  = self
            def _bg(fn=fn_name, a=args, e=env):
                try: interp._call_fn(fn, a, e, line)
                except Exception as ex: interp._print(colorize('red', f"[Task Error] {ex}"))
            th = threading.Thread(target=_bg, daemon=True)
            th.start()
            env.assign('last_task', NegTask(th))

        elif t == 'after_delay':
            delay   = float(_num(self.eval_expr(stmt['delay'], env)))
            body    = stmt['body']
            interp  = self
            cap_env = env
            def _after():
                time.sleep(delay)
                try: interp.exec_block(body, Environment(cap_env))
                except Exception as ex: interp._print(colorize('red', f"[after] {ex}"))
            th = threading.Thread(target=_after, daemon=True)
            th.start()

        elif t == 'every_interval':
            interval = float(_num(self.eval_expr(stmt['interval'], env)))
            body     = stmt['body']
            interp   = self
            cap_env  = env
            stop_evt = threading.Event()
            env.assign('_stop_timer', stop_evt)
            def _every():
                while not stop_evt.is_set():
                    time.sleep(interval)
                    if stop_evt.is_set(): break
                    try: interp.exec_block(body, Environment(cap_env))
                    except Exception as ex: interp._print(colorize('red', f"[every] {ex}")); break
            th = threading.Thread(target=_every, daemon=True)
            th.start()

        # ── benchmark ──────────────────────────────────────────────────
        elif t == 'benchmark':
            name = self.eval_expr(stmt['name'], env)
            t0   = time.perf_counter()
            self.exec_block(stmt['body'], Environment(env))
            elapsed = (time.perf_counter() - t0) * 1000
            self._print(colorize('yellow', f"[BENCHMARK] {name}: {elapsed:.3f} ms"))

        # ── error handling ─────────────────────────────────────────────
        elif t == 'try':
            try:
                self.exec_block(stmt['body'], Environment(env))
            except ThrowSignal as ts:
                local = Environment(env)
                if stmt.get('catch_var'): local.set(stmt['catch_var'], ts.value)
                self.exec_block(stmt['catch'], local)
            except NegRuntimeError as e:
                local = Environment(env)
                if stmt.get('catch_var'): local.set(stmt['catch_var'], str(e))
                self.exec_block(stmt['catch'], local)
            except Exception as e:
                local = Environment(env)
                if stmt.get('catch_var'): local.set(stmt['catch_var'], str(e))
                self.exec_block(stmt['catch'], local)
            finally:
                if stmt.get('finally_body'):
                    self.exec_block(stmt['finally_body'], Environment(env))

        elif t == 'throw':
            raise ThrowSignal(self.eval_expr(stmt['expr'], env))

        elif t == 'assert':
            if not self.eval_truthy(stmt['cond'], env):
                msg = self.eval_expr(stmt['msg'], env) if stmt.get('msg') else 'Assertion failed'
                raise ThrowSignal(str(msg))

        # ── import (native .neg modules) ──────────────────────────────
        elif t == 'import':
            self._do_import(stmt['module'], stmt['alias'], env)

        # ── OOP ────────────────────────────────────────────────────────
        elif t == 'class_def':
            cls = NegClass(stmt['name'], stmt.get('parent'), stmt['body'], env)
            self._classes[stmt['name']] = cls
            env.assign(stmt['name'], cls)

        elif t == 'new_obj':
            cls_name = stmt['class']
            args = [self.eval_expr(a, env) for a in stmt['args']]
            obj = self._instantiate(cls_name, args, env, line)
            target = stmt.get('result') or cls_name.lower()
            env.assign(target, obj)

        # ── lists ─────────────────────────────────────────────────────
        elif t == 'create_list':
            items_val = [self.eval_expr(i, env) for i in stmt['items']]
            name = stmt['name']
            if '.' in str(name):
                parts = name.split('.')
                obj = env.get(parts[0])
                if isinstance(obj, NegObject): obj.set(parts[1], items_val)
                elif isinstance(obj, dict): obj[parts[1]] = items_val
                else: env.assign(name, items_val)
            else:
                env.assign(name, items_val)

        elif t == 'list_add':
            lst = self._resolve_list(stmt['list'], env, line)
            lst.append(self.eval_expr(stmt['value'], env))

        elif t == 'list_remove':
            lst = self._resolve_list(stmt['list'], env, line)
            val = self.eval_expr(stmt['value'], env)
            if val in lst: lst.remove(val)

        elif t == 'list_insert':
            lst = self._resolve_list(stmt['list'], env, line)
            val = self.eval_expr(stmt['value'], env)
            idx = int(_num(self.eval_expr(stmt['index'], env))) - 1
            lst.insert(idx, val)

        elif t == 'list_pop':
            lst = self._resolve_list(stmt['list'], env, line)
            if lst:
                val = lst.pop()
                if stmt.get('var'): env.assign(stmt['var'], val)

        elif t == 'list_sort':
            lst = self._resolve_list(stmt['list'], env, line)
            lst.sort(key=lambda x: (_num(x) if isinstance(_num(x),(int,float)) else 0, str(x)))

        elif t == 'list_shuffle':
            lst = self._resolve_list(stmt['list'], env, line)
            random.shuffle(lst)

        # ── dicts ─────────────────────────────────────────────────────
        elif t == 'create_dict':
            d = {}
            for k_node, v_node in stmt['pairs']:
                d[self.eval_expr(k_node, env)] = self.eval_expr(v_node, env)
            env.assign(stmt['name'], d)

        elif t == 'obj_prop_set':
            obj_name = stmt['obj']
            prop     = stmt['prop']
            val      = self.eval_expr(stmt['expr'], env)
            obj = env.get(obj_name)
            if isinstance(obj, NegObject):
                obj.set(prop, val)
            elif isinstance(obj, dict):
                obj[prop] = val
            else:
                # fallback: store as obj_name__prop in env
                env.assign(obj_name + '__' + prop, val)

        elif t == 'dict_set':
            d = env.get(stmt['dict'])
            if isinstance(d, dict):
                d[self.eval_expr(stmt['key'], env)] = self.eval_expr(stmt['value'], env)
            elif isinstance(d, NegObject):
                d.set(str(self.eval_expr(stmt['key'], env)), self.eval_expr(stmt['value'], env))

        # ── file I/O ──────────────────────────────────────────────────
        elif t == 'file_open':
            path = str(self.eval_expr(stmt['path'], env))
            try:
                f = NegFile(path, stmt['mode'])
                self._files[stmt['name']] = f
                env.assign(stmt['name'], f)
            except Exception as e:
                raise NegRuntimeError(f"Cannot open '{path}': {e}", line)

        elif t == 'file_write':
            f = self._get_file(stmt['file'], env, line)
            f.handle.write(str(self.eval_expr(stmt['expr'], env)) + '\n')
            f.handle.flush()

        elif t == 'file_append':
            f = self._get_file(stmt['file'], env, line)
            f.handle.write(str(self.eval_expr(stmt['expr'], env)) + '\n')
            f.handle.flush()

        elif t == 'file_close':
            f = self._get_file(stmt['file'], env, line)
            f.handle.close()
            self._files.pop(stmt['file'], None)

        elif t == 'file_read':
            f = self._get_file(stmt['file'], env, line)
            env.assign(stmt['var'], f.handle.read())

        elif t == 'file_delete':
            path = str(self.eval_expr(stmt['path'], env))
            if os.path.exists(path): os.remove(path)

        elif t == 'json_save':
            val  = env.get(stmt['name'])
            path = str(self.eval_expr(stmt['path'], env))
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(val, f, indent=2, ensure_ascii=False)

        elif t == 'json_load':
            path = str(self.eval_expr(stmt['path'], env))
            with open(path, 'r', encoding='utf-8') as f:
                env.assign(stmt['name'], json.load(f))

        # ── system ─────────────────────────────────────────────────────
        elif t == 'sleep':
            dur  = float(_num(self.eval_expr(stmt['duration'], env)))
            unit = stmt.get('unit', 'seconds')
            if unit in ('milliseconds', 'ms'): dur /= 1000
            time.sleep(max(0, dur))

        elif t == 'exit':    sys.exit(0)
        elif t == 'clear':   os.system('cls' if os.name == 'nt' else 'clear')

        elif t == 'run_cmd':
            cmd = str(self.eval_expr(stmt['expr'], env))
            result = subprocess.getoutput(cmd)
            if stmt.get('var'): env.assign(stmt['var'], result)
            else: self._print(result)

        elif t == 'fetch_url':
            self._do_fetch(stmt, env, line)
        elif t == 'host_static':
            self._do_host_static(stmt, env, line)
        elif t == 'stop_server':
            self._do_stop_server(stmt, env, line)
        elif t == 'open_webview':
            self._do_open_webview(stmt, env, line)
        elif t == 'fusion':
            self._do_fusion(stmt, env, line)

        # ── events ─────────────────────────────────────────────────────
        elif t == 'emit':
            event = stmt['event']
            data  = self.eval_expr(stmt['data'], env) if stmt.get('data') else None
            for handler in self._events.get(event, []):
                local = Environment(handler['env'])
                if data is not None: local.set('event_data', data)
                self.exec_block(handler['body'], local)

        elif t == 'on_event':
            self._events.setdefault(stmt['event'], []).append({'body':stmt['body'],'env':env})

        # ── GUI ───────────────────────────────────────────────────────
        elif t == 'create_window':
            w = stmt['width']
            h = stmt['height']
            w = int(_num(self.eval_expr(w, env))) if isinstance(w, dict) else int(_num(w))
            h = int(_num(self.eval_expr(h, env))) if isinstance(h, dict) else int(_num(h))
            if self.gui: self.gui.create_window(stmt['title'], w, h)
            else:        self._print(f"[GUI] Window '{stmt['title']}' {w}x{h}")

        elif t == 'show_window':
            if self.gui: self.gui.show_window(stmt.get('name',''))

        elif t == 'create_button':
            opts = {k: self.eval_expr(v, env) for k, v in stmt.get('opts',{}).items()}
            if self.gui: self.gui.create_button(stmt['label'], stmt['window'], opts)
            else:        self._print(f"[GUI] Button '{stmt['label']}'")

        elif t == 'create_label':
            text = self.eval_expr(stmt['text'], env)
            opts = {k: self.eval_expr(v, env) for k, v in stmt.get('opts',{}).items()}
            name = stmt.get('name', str(text)[:20])
            if self.gui: self.gui.create_label(str(text), stmt['window'], opts, name=name)
            else:        self._print(f"[GUI] Label '{text}'")

        elif t == 'create_entry':
            if self.gui: self.gui.create_entry(stmt['name'], stmt['window'])
            else:        self._print(f"[GUI] Entry '{stmt['name']}'")

        elif t == 'create_progress':
            if self.gui: self.gui.create_progress(stmt['name'], stmt['window'])
            else:        self._print(f"[GUI] Progress '{stmt['name']}'")

        elif t == 'when_clicked':
            if self.gui:
                body, interp, cap_env = stmt['body'], self, env
                def handler(b=body, e=cap_env):
                    try: interp.exec_block(b, Environment(e))
                    except Exception as ex: interp._print(colorize('red', f"[Button Error] {ex}"))
                self.gui.bind_button(stmt['label'], handler)

        elif t == 'gui_alert':
            msg = str(self.eval_expr(stmt['expr'], env))
            if self.gui: self.gui.alert(msg)
            else:        self._print(f"[ALERT] {msg}")

        elif t == 'gui_confirm':
            msg    = str(self.eval_expr(stmt['expr'], env))
            result = self.gui.confirm(msg) if self.gui else (input(f"[CONFIRM] {msg} (y/n): ").lower()=='y')
            env.assign(stmt['var'], result)

        elif t == 'gui_hide':
            if self.gui: self.gui.hide_widget(stmt['name'])

        elif t == 'create_image':
            opts = {k: self.eval_expr(v, env) for k, v in stmt.get('opts',{}).items()}
            if self.gui: self.gui.create_image(stmt['name'], stmt['window'], opts)

        elif t == 'create_chart':
            opts = {k: self.eval_expr(v, env) for k, v in stmt.get('opts',{}).items()}
            if self.gui: self.gui.create_chart(stmt['name'], stmt['window'], opts)

        elif t == 'create_frame':
            opts = {k: self.eval_expr(v, env) for k, v in stmt.get('opts',{}).items()}
            if self.gui: self.gui.create_frame(stmt['name'], stmt['window'], opts)

        elif t == 'create_tab_group':
            opts = {k: self.eval_expr(v, env) for k, v in stmt.get('opts',{}).items()}
            if self.gui: self.gui.create_tab_group(stmt['name'], stmt['window'], opts)

        elif t == 'create_tab':
            opts = {k: self.eval_expr(v, env) for k, v in stmt.get('opts',{}).items()}
            if self.gui: self.gui.create_tab(stmt['name'], stmt['window'], opts)

        elif t == 'gui_toast':
            msg = str(self.eval_expr(stmt['expr'], env))
            if self.gui: self.gui.show_toast(msg)
            else:        self._print(f"[TOAST] {msg}")

        elif t == 'gui_dialog':
            msg = str(self.eval_expr(stmt['expr'], env))
            result = self.gui.show_dialog(msg) if self.gui else input(f"[DIALOG] {msg}: ")
            env.assign(stmt['var'], result)

        elif t == 'bind_key':
            if self.gui:
                body, interp, cap_env = stmt['body'], self, env
                def handler(e=None, b=body, en=cap_env):
                    try: interp.exec_block(b, Environment(en))
                    except Exception as ex: interp._print(colorize('red', f"[Key Error] {ex}"))
                self.gui.bind_key(stmt['key'], stmt['window'], handler)

        elif t == 'play_sound':
            file = str(self.eval_expr(stmt['file'], env))
            if self.gui: self.gui.play_sound(file)
            else:        self._print(f"[SOUND] Playing: {file}")


        # ── v4.1 GUI additions ────────────────────────────────────────
        elif t == 'create_textarea':
            opts = {k: self.eval_expr(v, env) for k, v in stmt.get('opts',{}).items()}
            if self.gui: self.gui.create_textarea(stmt['name'], stmt['window'], opts)
            else:        self._print(f"[GUI] Textarea '{stmt['name']}'")

        elif t == 'create_checkbox':
            opts = {k: self.eval_expr(v, env) for k, v in stmt.get('opts',{}).items()}
            if self.gui: self.gui.create_checkbox(stmt['name'], stmt['window'],
                                                   stmt.get('label'), opts)
            else:        self._print(f"[GUI] Checkbox '{stmt['name']}'")

        elif t == 'create_dropdown':
            raw_opts = [self.eval_expr(o, env) for o in stmt.get('options', [])]
            opts     = {k: self.eval_expr(v, env) for k, v in stmt.get('opts',{}).items()}
            if self.gui: self.gui.create_dropdown(stmt['name'], stmt['window'], raw_opts, opts)
            else:        self._print(f"[GUI] Dropdown '{stmt['name']}'")

        elif t == 'create_table':
            cols = [self.eval_expr(c, env) for c in stmt.get('columns', [])]
            opts = {k: self.eval_expr(v, env) for k, v in stmt.get('opts',{}).items()}
            if self.gui: self.gui.create_table(stmt['name'], stmt['window'], cols, opts)
            else:        self._print(f"[GUI] Table '{stmt['name']}'")

        elif t == 'table_add_row':
            vals = [self.eval_expr(v, env) for v in stmt.get('values', [])]
            if self.gui: self.gui.table_add_row(stmt['name'], vals)

        elif t == 'table_clear':
            if self.gui: self.gui.table_clear(stmt['name'])

        elif t == 'create_canvas':
            w = int(_num(self.eval_expr(stmt['width'],  env)))
            h = int(_num(self.eval_expr(stmt['height'], env)))
            opts = {k: self.eval_expr(v, env) for k, v in stmt.get('opts',{}).items()}
            if self.gui: self.gui.create_canvas(stmt['name'], stmt['window'], w, h, opts)

        elif t == 'canvas_draw_rect':
            coords = [_num(self.eval_expr(stmt[k], env)) for k in ('x1','y1','x2','y2')]
            opts   = {k: self.eval_expr(v, env) for k, v in stmt.get('opts',{}).items()}
            if self.gui: self.gui.canvas_draw_rect(stmt['name'], *coords, opts)

        elif t == 'canvas_draw_oval':
            coords = [_num(self.eval_expr(stmt[k], env)) for k in ('x1','y1','x2','y2')]
            opts   = {k: self.eval_expr(v, env) for k, v in stmt.get('opts',{}).items()}
            if self.gui: self.gui.canvas_draw_oval(stmt['name'], *coords, opts)

        elif t == 'canvas_draw_line':
            coords = [_num(self.eval_expr(stmt[k], env)) for k in ('x1','y1','x2','y2')]
            opts   = {k: self.eval_expr(v, env) for k, v in stmt.get('opts',{}).items()}
            if self.gui: self.gui.canvas_draw_line(stmt['name'], *coords, opts)

        elif t == 'canvas_draw_text':
            x    = _num(self.eval_expr(stmt['x'], env))
            y    = _num(self.eval_expr(stmt['y'], env))
            text = str(self.eval_expr(stmt['text'], env))
            opts = {k: self.eval_expr(v, env) for k, v in stmt.get('opts',{}).items()}
            if self.gui: self.gui.canvas_draw_text(stmt['name'], x, y, text, opts)

        elif t == 'canvas_clear':
            if self.gui: self.gui.canvas_clear(stmt['name'])

        elif t == 'create_tab':
            if self.gui: self.gui.create_tab(stmt['name'], stmt['window'])

        elif t == 'add_tab':
            if self.gui: self.gui.add_tab(stmt['notebook'], stmt['title'])

        elif t == 'gui_toast':
            msg  = str(self.eval_expr(stmt['expr'], env))
            dur  = int(self.eval_expr(stmt['duration'], env)) if stmt.get('duration') else 3000
            col  = str(self.eval_expr(stmt['color'], env)) if stmt.get('color') else None
            if self.gui: self.gui.toast(msg, dur, col or '#3fb950')
            else:        self._print(f"[TOAST] {msg}")

        elif t == 'set_statusbar':
            text = str(self.eval_expr(stmt['text'], env))
            if self.gui: self.gui.set_statusbar(stmt['window'], text)

        elif t == 'close_window':
            if self.gui: self.gui.close_window(stmt.get('name',''))

        elif t == 'enable_button':
            enabled = bool(_truthy(self.eval_expr(stmt['value'], env))) if stmt.get('value') else True
            if self.gui: self.gui.enable_button(stmt['label'], enabled)

        elif t == 'set_label_color':
            col = str(self.eval_expr(stmt['color'], env))
            if self.gui: self.gui.set_label_color(stmt['name'], col)

        elif t == 'gui_ask_file':
            mode = stmt.get('mode', 'open')
            if self.gui:
                path = self.gui.ask_file(mode)
            else:
                path = input(f"[FILE {mode.upper()}] Enter path: ")
            if stmt.get('var'): env.assign(stmt['var'], path)

        elif t == 'gui_ask_color':
            if self.gui:
                col = self.gui.ask_color()
            else:
                col = input("[COLOR] Enter hex: ")
            if stmt.get('var'): env.assign(stmt['var'], col)

        elif t == 'get_textarea':
            val = self.gui.get_textarea_value(stmt['name']) if self.gui else ''
            env.assign(stmt['var'], val)

        elif t == 'set_textarea':
            text = str(self.eval_expr(stmt['text'], env))
            if self.gui: self.gui.set_textarea_value(stmt['name'], text)

        elif t == 'append_textarea':
            text = str(self.eval_expr(stmt['text'], env))
            if self.gui: self.gui.append_textarea(stmt['name'], text)

        elif t == 'get_checkbox':
            val = self.gui.get_checkbox_value(stmt['name']) if self.gui else False
            env.assign(stmt['var'], val)

        elif t == 'get_dropdown':
            val = self.gui.get_dropdown_value(stmt['name']) if self.gui else ''
            env.assign(stmt['var'], val)

        # ── v4.1 Networking ──────────────────────────────────────────
        elif t == 'http_request':
            self._do_http_request(stmt, env, line)

        elif t == 'fetch_json':
            self._do_json_api(stmt, env, line)

        elif t == 'fetch_url':
            self._do_fetch(stmt, env, line)

        else:
            pass  # unrecognised

    # ─────────────────────────────── eval
    def eval_expr(self, node, env):
        t = node['type']

        if t == 'string':
            val = node['value']
            # ${...} interpolation — evaluate embedded expressions
            if '${' in val:
                import re as _re
                def _interp(m):
                    expr_src = m.group(1)
                    try:
                        from lexer  import Lexer as _Lexer
                        from parser import Parser as _Parser
                        p = _Parser(_Lexer(expr_src).tokenize())
                        expr_ast = p._parse_expr()
                        result = self.eval_expr(expr_ast, env)
                        return '' if result is None else str(result)
                    except Exception:
                        return m.group(0)
                val = _re.sub(r'\$\{([^}]+)\}', _interp, val)
            return val
        if t == 'number':   return node['value']
        if t == 'bool':     return node['value']
        if t == 'null':     return None

        if t == 'lambda_expr':
            lam = NegLambda(node['params'], node['body'], env)
            return lam

        if t == 'wildcard': return None

        if t == 'between_check':
            left = self.eval_expr(node['left'], env)
            lo   = self.eval_expr(node['lo'],   env)
            hi   = self.eval_expr(node['hi'],   env)
            result = _num(lo) <= _num(left) <= _num(hi)
            return (not result) if node.get('negate') else result

        if t == 'approx_check':
            left  = self.eval_expr(node['left'],  env)
            right = self.eval_expr(node['right'], env)
            nl, nr = _num(left), _num(right)
            thresh = max(abs(nr) * 0.05, 0.01)
            result = abs(nl - nr) <= thresh
            return (not result) if node.get('negate') else result

        if t == 'new_expr':
            cls_name = node['class']
            args = [self.eval_expr(a, env) for a in node['args']]
            return self._instantiate(cls_name, args, env, node.get('line',0))

        if t == 'var':
            v = env.get(node['name'])
            return v  # NegLambda instances are returned as-is

        if t == 'list_literal':
            return [self.eval_expr(i, env) for i in node['items']]

        if t == 'dict_literal':
            return {self.eval_expr(k, env): self.eval_expr(v, env) for k,v in node['pairs']}

        if t == 'list_access':
            lst = env.get(node['list'])
            idx = int(_num(self.eval_expr(node['index'], env))) - 1
            if isinstance(lst, (list,str)) and 0 <= idx < len(lst): return lst[idx]
            return None

        if t == 'dict_access':
            d   = env.get(node['dict'])
            key = self.eval_expr(node['key'], env)
            if isinstance(d, dict):      return d.get(key)
            if isinstance(d, NegObject): return d.get(str(key))
            return None

        if t == 'attr_access':
            obj  = self.eval_expr(node['obj'], env)
            attr = node['attr']
            if obj is None: return None
            if isinstance(obj, NegObject): return obj.get(attr)
            if isinstance(obj, NegModule): return obj.get(attr)
            if isinstance(obj, dict): return obj.get(attr)
            if isinstance(obj, NegFunction): return None
            return getattr(obj, attr, None)

        if t == 'index_access':
            obj = self.eval_expr(node['obj'], env)
            idx = self.eval_expr(node['index'], env)
            if isinstance(obj, list): return obj[int(_num(idx))-1]
            if isinstance(obj, dict): return obj.get(idx)
            if isinstance(obj, str):  return obj[int(_num(idx))-1]
            if isinstance(obj, NegObject): return obj.get(str(idx))
            return None

        if t == 'unary':
            val = self.eval_expr(node['operand'], env)
            op  = node['op']
            if op == 'not': return not _truthy(val)
            if op == '-':   return -_num(val)
            return val

        if t == 'binop':
            left  = self.eval_expr(node['left'],  env)
            right = self.eval_expr(node['right'], env)
            return _arith(node['op'], left, right)

        if t == 'compare': return self._compare(node, env)

        if t == 'logic':
            if node['op'] == 'and':
                return _truthy(self.eval_expr(node['left'],env)) and _truthy(self.eval_expr(node['right'],env))
            if node['op'] == 'or':
                return _truthy(self.eval_expr(node['left'],env)) or  _truthy(self.eval_expr(node['right'],env))

        if t == 'null_coalesce':
            left = self.eval_expr(node['left'], env)
            return left if left is not None else self.eval_expr(node['right'], env)

        if t == 'pipe_expr':
            # value |> funcName  →  call funcName with value as first arg
            val  = self.eval_expr(node['value'], env)
            func_node = node['func']
            fname = func_node.get('name') or func_node.get('value')
            fn = env.get(fname) or self._builtins.get(fname)
            if callable(fn):  return fn(val)
            if isinstance(fn, NegFunction):
                local = Environment(fn.closure)
                if fn.params: local.set(fn.params[0], val)
                try: self.exec_block(fn.body, local)
                except ReturnSignal as r: return r.value
                return None
            raise NegRuntimeError(f"Pipe target '{fname}' is not callable", node.get('line',0))

        if t == 'builtin_call': return self._call_builtin(node, env)

        if t == 'call_expr':
            return self._call_fn(node['name'], node['args'], env, node.get('line',0))

        if t == 'type_check':
            val    = self.eval_expr(node['expr'], env)
            tp     = self._builtins['type_of'](val)
            result = (tp == node['expected'])
            return (not result) if node.get('negate') else result

        return None

    def eval_truthy(self, node, env): return _truthy(self.eval_expr(node, env))

    def _compare(self, node, env):
        left  = self.eval_expr(node['left'],  env)
        right = self.eval_expr(node['right'], env)
        op    = node['op']
        ln, rn = _num(left), _num(right)
        try:
            if op == '==': return left == right
            if op == '!=': return left != right
            if op == '>':  return ln > rn
            if op == '<':  return ln < rn
            if op == '>=': return ln >= rn
            if op == '<=': return ln <= rn
        except TypeError:
            return False
        return False

    def _call_builtin(self, node, env):
        fn   = node['fn']
        args = [self.eval_expr(a, env) for a in node['args']]
        impl = self._builtins.get(fn)
        if impl:
            try: return impl(*args)
            except Exception as e:
                raise NegRuntimeError(f"Built-in '{fn}': {e}", node.get('line',0))
        return None

    def _call_fn(self, name, arg_nodes, env, line=0, inject_first=None):
        return self._call_fn_v4(name, arg_nodes, env, line, inject_first)


    def _call_fn_obj(self, fn, arg_nodes, env, line, obj):
        args  = [self.eval_expr(a, env) for a in arg_nodes]
        local = Environment(fn.closure)
        local.set('self', obj)
        for p, v in zip(fn.params, args): local.set(p, v)
        try: self.exec_block(fn.body, local)
        except ReturnSignal as r: return r.value
        return None

    # ─────────────────────────────── helpers
    def _get_file(self, name, env, line):
        f = self._files.get(name) or env.get(name)
        if not isinstance(f, NegFile):
            raise NegRuntimeError(f"'{name}' is not an open file", line)
        return f

    def _notify_watchers(self, name, val, env):
        for handler in self._watchers.get(name, []):
            local = Environment(handler['env'])
            local.set('new_value', val)
            local.set(name, val)
            try: self.exec_block(handler['body'], local)
            except Exception: pass

    # ─────────────────────────────── import (native Neglish modules)
    def _do_import(self, module_name, alias, env):
        cache_key = os.path.normcase(str(module_name))
        if cache_key in Interpreter._MODULE_CACHE:
            env.assign(alias, Interpreter._MODULE_CACHE[cache_key])
            return

        mod_str = str(module_name)
        is_path = ('/' in mod_str or '\\' in mod_str or mod_str.endswith('.neg'))

        # Determine the base directory of the interpreter source (handles frozen .exe too)
        if getattr(sys, 'frozen', False):
            _interp_dir = sys._MEIPASS
        else:
            _interp_dir = os.path.dirname(os.path.abspath(__file__))

        if is_path:
            # Path-based: resolve relative to the currently-running file's directory
            candidate = mod_str if os.path.isabs(mod_str) else os.path.join(self.source_dir, mod_str)
            if not candidate.endswith('.neg'):
                candidate += '.neg'
            search_paths = [candidate]
        else:
            # Name-based: search local dir, then stdlib
            search_paths = [
                os.path.join(self.source_dir, mod_str + '.neg'),
                os.path.join(self.source_dir, 'stdlib', mod_str + '.neg'),
                os.path.join(_interp_dir, 'stdlib', mod_str + '.neg'),
                mod_str + '.neg',
            ]

        for neg_path in search_paths:
            if os.path.exists(neg_path):
                from lexer   import Lexer
                from parser  import Parser
                with open(neg_path, 'r', encoding='utf-8') as f:
                    source = f.read()
                tokens  = Lexer(source).tokenize()
                ast     = Parser(tokens).parse()
                sub     = Interpreter(source_dir=os.path.dirname(os.path.abspath(neg_path)))
                sub.run(ast)
                exports = sub._exports or list(sub.global_env.vars.keys())
                module  = NegModule(mod_str, sub.global_env, exports)
                env.assign(alias, module)
                Interpreter._MODULE_CACHE[cache_key] = module
                return

        self._print(colorize('yellow', f"[Warning] Module '{mod_str}' not found"))

    def _do_fetch(self, stmt, env, line):
        url = str(self.eval_expr(stmt['url'], env))
        if not self._is_network_allowed(url):
            data = "[FETCH ERROR] blocked by whitelist policy"
            if stmt.get('var'):
                env.assign(stmt['var'], data)
            else:
                self._print(data)
            return
        try:
            import urllib.request, urllib.error
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = resp.read().decode('utf-8', errors='replace')
        except Exception as e:
            data = f"[FETCH ERROR] {e}"
        if stmt.get('var'): env.assign(stmt['var'], data)
        else: self._print(data)

    def _is_network_allowed(self, url):
        whitelist = os.environ.get("NEGLISH_ALLOWED_DOMAINS", "").strip()
        if not whitelist:
            return True
        host = (urlparse(url).hostname or "").lower()
        if not host:
            return False
        allowed = [d.strip().lower() for d in whitelist.split(",") if d.strip()]
        return any(host == d or host.endswith("." + d) for d in allowed)

    def _do_host_static(self, stmt, env, line):
        folder = str(self.eval_expr(stmt['folder'], env))
        port = int(_num(self.eval_expr(stmt['port'], env)))
        name = stmt.get('name') or f"server_{port}"
        abs_folder = os.path.abspath(folder)
        if not os.path.isdir(abs_folder):
            raise NegRuntimeError(f"Host folder not found: {abs_folder}", line)

        class _StaticHandler(SimpleHTTPRequestHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, directory=abs_folder, **kwargs)
            def log_message(self, format, *args):
                return

        server = ThreadingHTTPServer(("127.0.0.1", port), _StaticHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        self._servers[name] = {"server": server, "thread": thread, "port": port, "folder": abs_folder}
        url = f"http://127.0.0.1:{port}/"
        env.assign(name, url)
        self._print(colorize('green', f"[HOST] {name} serving {abs_folder} at {url}"))

    def _do_stop_server(self, stmt, env, line):
        name = stmt['name']
        rec = self._servers.get(name)
        if not rec:
            self._print(colorize('yellow', f"[HOST] server '{name}' not found"))
            return
        rec["server"].shutdown()
        rec["server"].server_close()
        self._servers.pop(name, None)
        self._print(colorize('green', f"[HOST] server '{name}' stopped"))

    def _do_open_webview(self, stmt, env, line):
        url = str(self.eval_expr(stmt['url'], env))
        if self.gui:
            self.gui.create_html_view(url, window_title=stmt.get('window'))
        else:
            import webbrowser
            webbrowser.open(url)

    def _do_fusion(self, stmt, env, line):
        folder = str(self.eval_expr(stmt['folder'], env))
        name = stmt['name']
        
        # Determine port
        port_node = stmt.get('port')
        port = int(_num(self.eval_expr(port_node, env))) if port_node else 0
        
        if port == 0:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind(('', 0))
            port = sock.getsockname()[1]
            sock.close()

        # 1. Host the folder
        host_stmt = {
            'folder': stmt['folder'],
            'port': {'type':'number', 'value': port},
            'name': name
        }
        self._do_host_static(host_stmt, env, line)
        
        # 2. Open Webview
        url = f"http://127.0.0.1:{port}/"
        view_stmt = {
            'url': {'type':'string', 'value': url},
            'window': name
        }
        self._do_open_webview(view_stmt, env, line)
        
        self._print(colorize('cyan', f"[FUSION] App '{name}' fused from '{folder}' at {url}"))

    def print_test_summary(self):
        if self._test.passed + self._test.failed > 0:
            self._test.summary()

    # ─────────────────────────────── OOP instantiation
    def _instantiate(self, cls_name, args, env, line=0):
        """Create an instance of a Neglish class."""
        cls = env.get(cls_name) or self._classes.get(cls_name)
        if not isinstance(cls, NegClass):
            raise NegRuntimeError(f"'{cls_name}' is not a class", line)

        obj = NegObject(cls_name)
        obj_env = Environment(cls.closure)
        obj_env.set('self', obj)

        # ── inherit parent first
        if cls.parent:
            pcls = self._classes.get(cls.parent) or (env.get(cls.parent) if hasattr(env,'get') else None)
            if isinstance(pcls, NegClass):
                p_env = Environment(pcls.closure)
                p_env.set('self', obj)
                self.exec_block(pcls.body, p_env)
                for k, v in p_env.vars.items():
                    if k != 'self': obj.props[k] = v

        # ── run class body (defines methods/properties onto obj)
        self.exec_block(cls.body, obj_env)
        for k, v in obj_env.vars.items():
            if k != 'self': obj.props[k] = v

        # ── call constructor if defined
        for ctor_name in ('init','constructor','new','__init__'):
            ctor = obj.props.get(ctor_name)
            if isinstance(ctor, NegFunction):
                local = Environment(ctor.closure)
                local.set('self', obj)
                for p, v in zip(ctor.params, args): local.set(p, v)
                try: self.exec_block(ctor.body, local)
                except ReturnSignal: pass
                # sync any props set via 'self' in constructor
                for k, v in local.vars.items():
                    if k != 'self': obj.props[k] = v
                break

        return obj

    # ─────────────────────────────── enhanced _call_fn (lambdas + OOP methods)
    def _call_fn_v4(self, name, arg_nodes, env, line=0, inject_first=None):
        """v4 call: resolves lambdas, OOP methods, dotted names."""
        # ── dotted name resolution: obj.method  or  module.fn
        if '.' in str(name):
            parts = name.split('.')
            obj = env.get(parts[0]) or self.global_env.get(parts[0])
            for part in parts[1:-1]:
                if isinstance(obj, NegObject): obj = obj.get(part)
                elif isinstance(obj, NegModule): obj = obj.get(part)
                elif isinstance(obj, dict): obj = obj.get(part)
                else: obj = None
            member_name = parts[-1]
            fn = None
            if isinstance(obj, NegObject):
                fn = obj.get(member_name)
                if isinstance(fn, NegFunction):
                    args = ([inject_first] if inject_first is not None else []) + \
                           [self.eval_expr(a, env) for a in arg_nodes]
                    local = Environment(fn.closure)
                    local.set('self', obj)
                    for p, v in zip(fn.params, args): local.set(p, v)
                    try: self.exec_block(fn.body, local)
                    except ReturnSignal as r: return r.value
                    # sync self props
                    for k, v in local.vars.items():
                        if k != 'self': obj.props[k] = v
                    return None
                if isinstance(fn, NegLambda):
                    args = ([inject_first] if inject_first is not None else []) + \
                           [self.eval_expr(a, env) for a in arg_nodes]
                    return self._call_lambda(fn, args, env)
            elif isinstance(obj, NegModule):
                fn = obj.get(member_name)
            elif isinstance(obj, dict): fn = obj.get(member_name)

            if fn is None: raise NegRuntimeError(f"'{name}' not found", line)
            if isinstance(fn, NegFunction):
                args = [self.eval_expr(a, env) for a in arg_nodes]
                local = Environment(fn.closure)
                for i, p in enumerate(fn.params):
                    if i < len(args):
                        local.set(p, args[i])
                    elif p in fn.defaults:
                        local.set(p, fn.defaults[p])
                    else:
                        local.set(p, None)
                try: self.exec_block(fn.body, local)
                except ReturnSignal as r: return r.value
                return None
            if isinstance(fn, NegLambda):
                args = [self.eval_expr(a, env) for a in arg_nodes]
                return self._call_lambda(fn, args, env)
            if callable(fn):
                args = [self.eval_expr(a, env) for a in arg_nodes]
                return fn(*args)
            raise NegRuntimeError(f"'{name}' is not callable", line)

        # ── plain name resolution
        fn = env.get(name) or self.global_env.get(name)
        if fn is None: raise NegRuntimeError(f"Undefined: '{name}'", line)

        if isinstance(fn, NegLambda):
            args = ([inject_first] if inject_first is not None else []) + \
                   [self.eval_expr(a, env) for a in arg_nodes]
            return self._call_lambda(fn, args, env)

        if isinstance(fn, NegFunction):
            args = ([inject_first] if inject_first is not None else []) + \
                   [self.eval_expr(a, env) for a in arg_nodes]
            if fn._cache is not None:
                cache_key = tuple(str(a) for a in args)
                if cache_key in fn._cache: return fn._cache[cache_key]
            local = Environment(fn.closure)
            local.set('self', env.get('self'))
            for i, p in enumerate(fn.params):
                if i < len(args):
                    local.set(p, args[i])
                elif p in fn.defaults:
                    local.set(p, fn.defaults[p])
                else:
                    local.set(p, None)
            result = None
            try: self.exec_block(fn.body, local)
            except ReturnSignal as r: result = r.value
            if fn._cache is not None:
                fn._cache[tuple(str(a) for a in args)] = result
            return result

        if isinstance(fn, NegClass):
            args = [self.eval_expr(a, env) for a in arg_nodes]
            return self._instantiate(fn.name, args, env, line)

        if callable(fn):
            args = [self.eval_expr(a, env) for a in arg_nodes]
            return fn(*args)

        raise NegRuntimeError(f"'{name}' is not callable", line)

    def _call_lambda(self, lam, args, env):
        """Execute a NegLambda — evaluates its single body expression."""
        local = Environment(lam.closure)
        for p, v in zip(lam.params, args): local.set(p, v)
        return self.eval_expr(lam.body_expr, local)

    def _eval_attr(self, obj, attr):
        """Evaluate attribute access on an object."""
        if isinstance(obj, NegObject): return obj.get(attr)
        if isinstance(obj, NegModule): return obj.get(attr)
        if isinstance(obj, dict): return obj.get(attr)
        return getattr(obj, attr, None)


    def _resolve_list(self, name, env, line=0):
        """Resolve a list by name, supporting dotted paths like self.tricks."""
        if '.' in str(name):
            parts = name.split('.')
            obj = env.get(parts[0])
            if isinstance(obj, NegObject):
                lst = obj.get(parts[1])
                if not isinstance(lst, list):
                    raise NegRuntimeError(f"'{name}' is not a list", line)
                return lst
            elif isinstance(obj, dict):
                lst = obj.get(parts[1])
                if not isinstance(lst, list):
                    raise NegRuntimeError(f"'{name}' is not a list", line)
                return lst
        lst = env.get(name)
        if not isinstance(lst, list):
            raise NegRuntimeError(f"'{name}' is not a list", line)
        return lst
