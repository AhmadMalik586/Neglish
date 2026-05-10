# lexer.py — Neglish v4.1 Tokeniser
# Full OOP, lambdas, pattern matching, natural language flexibility

TT_KEYWORD = 'KEYWORD'
TT_STRING  = 'STRING'
TT_NUMBER  = 'NUMBER'
TT_IDENT   = 'IDENT'
TT_OP      = 'OP'
TT_NEWLINE = 'NEWLINE'
TT_EOF     = 'EOF'

KEYWORDS = {
    # core output (synonyms)
    'show','say','print','log','display','output','echo',
    # variables
    'set','to','let','const','increase','decrease','by',
    # control
    'if','then','else','elseif','elif','otherwise','also','end',
    'unless',
    # loops
    'repeat','times','while','do','for','each','in','from','step','until',
    'loop','forever',
    # functions
    'define','function','with','call','return','break','continue',
    # OOP
    'class','new','self','super','inherit','extends','extend','has',
    'constructor','property','method','instanceof','object',
    # input
    'ask','and','store','input','prompt',
    # logic
    'not','or','both','either','is','true','false','null','none',
    'greater','than','less','equal','at','least','most',
    'between','within',
    # articles (silently consumed)
    'the','a','an',
    # module
    'import','use','module','export','from','package','as',
    # collections
    'list','item','of','add','remove','insert','at','pop','create',
    'map','dict','key','value','keys','values',
    'sort','shuffle','count','index','slice','unique','flatten',
    'sum','average','first','last','empty','reverse','contains',
    'starts','ends','length','items',
    # math
    'sqrt','abs','floor','ceil','round','power','random',
    'pi','max','min','mod','log10','log2','sin','cos','tan',
    'degrees','radians','clamp','lerp','sign','gcd','lcm',
    'asin','acos','atan',
    # string
    'uppercase','lowercase','trim','split','join','replace','substring',
    'number','string','type','titlecase','camelcase','snakecase',
    'repeat_str','pad_left','pad_right','count_of','char_at','char_code',
    'from_code','number_format','pluralize','format_str',
    'regex','matches','find_all','replace_regex','split_lines',
    # type checks
    'to_bool','to_list',
    'is_number','is_string','is_list','is_dict','is_null','is_bool',
    'is_prime','is_even','is_odd','factorial','fibonacci',
    # file
    'open','file','read','write','append','close','delete',
    'read_file','write_file','append_file',
    'file_exists','is_file','is_dir','file_size','file_ext',
    'file_name','file_dir','list_dir','path_join',
    # json
    'json_parse','json_stringify','json_pretty','save','load',
    # error
    'try','catch','error','throw','raise','assert',
    # time
    'now','today','sleep','wait','seconds','milliseconds','ms',
    'timestamp','time_ms','year','month','day','hour','minute','second','weekday',
    # system
    'exit','quit','clear','run','env_get',
    'platform','username','hostname','pid','cwd','sep',
    # pattern matching
    'match','when','case','default','pattern','where',
    # GUI
    'window','button','label','entry','progress',
    'width','height','color','background','foreground',
    'font','size','bold','italic','x','y','row','column',
    'hide','title','resize','alert','confirm','update','get',
    'clicked','changed','submitted', 'frame', 'tab_group', 'tab',
    'image', 'chart', 'dialog', 'toast', 'bind_key', 'play_sound',
    # lambda
    'lambda','fn','given','using',
    # pipelines
    'filter','collect','pipe','through','reduce','map_fn','zip_with',
    'group_by','order_by','take','drop','chunk',
    # concurrency
    'spawn','after','every','async',
    # reactive
    'watch','freeze','memo','benchmark',
    # events
    'emit','on','listen',
    # networking (v4.1)
    'fetch','post','put','delete','patch','request',
    'http_get','http_post','http_put','http_delete','http_patch',
    'fetch_json','json_api','websocket','ws_send','ws_close',
    'download','upload','base64_encode','base64_decode',
    'url_encode','url_decode','parse_url','build_url',
    # web/full-stack (v4.3)
    'html','css','javascript','js','frontend','backend','serve','host',
    'website','webview','template','static','assets','api','endpoint',
    'port','localhost','open_url','stop_server','fusion',
    # debug
    'debug','inspect','trace',
    'uuid','hash_of',
    # test
    'describe','test','expect','check','should','be','equal_to',
    # extra list builtins
    'max_of','min_of','median','stdev','variance',
    'sort_desc','flatten_deep','compact','sample',
    'contains_all','contains_any','intersection','difference','union',
    'zip_pairs','enumerate_list','range_list','pluck',
    'weighted_choice','choice',
    # misc
    'percent','percent_of','run_cmd','sleep_ms','global',
    'dict_has','dict_merge','dict_size','dict_to_list',
    'dict_keys','dict_values',
}

SYNONYMS = {
    'display': 'show', 'output': 'show', 'echo': 'show',
    'let':     'set',
    'extends': 'inherit', 'extend': 'inherit',
    'fn':      'lambda', 'given': 'lambda', 'using': 'lambda',
    'prompt':  'ask',
    'also':    'else', 'otherwise': 'else',
    'True':    'true', 'False': 'false', 'None': 'null',
    'unless':  'unless',
}

class Token:
    def __init__(self, type_, value, line=0):
        self.type = type_; self.value = value; self.line = line
    def __repr__(self):
        return f'Token({self.type}, {self.value!r}, line={self.line})'

class Lexer:
    def __init__(self, source):
        self.source = source; self.pos = 0; self.line = 1; self.tokens = []

    def peek(self, o=0):
        i = self.pos + o
        return self.source[i] if i < len(self.source) else ''

    def advance(self):
        ch = self.source[self.pos]; self.pos += 1
        if ch == '\n': self.line += 1
        return ch

    def skip_ws(self):
        while self.pos < len(self.source) and self.peek() in (' ','\t','\r'):
            self.advance()

    def read_string(self, q):
        self.advance()
        buf = []
        while self.pos < len(self.source):
            ch = self.advance()
            if ch == q: break
            if ch == '\\':
                e = self.advance()
                buf.append({'n':'\n','t':'\t','r':'\r','\\':'\\','"':'"',"'":"'",'0':'\0'}.get(e,e))
            else: buf.append(ch)
        return ''.join(buf)

    def read_triple(self):
        # consume the opening triple-quote (3 chars already peeked)
        self.pos += 3
        buf = []
        while self.pos < len(self.source):
            # check for closing triple-quote
            if (self.source[self.pos] == '"' and 
                self.pos + 2 < len(self.source) and
                self.source[self.pos+1] == '"' and
                self.source[self.pos+2] == '"'):
                self.pos += 3
                break
            ch = self.source[self.pos]
            self.pos += 1
            if ch == '\n':
                self.line += 1
            buf.append(ch)
        return ''.join(buf)

    def read_heredoc(self):
        for _ in range(3): self.advance()  # consume <<<
        self.skip_ws()
        label = []
        while self.pos < len(self.source) and self.peek() not in ('\n',' ','\t'):
            label.append(self.advance())
        label = ''.join(label).strip()
        if self.peek() == '\n': self.advance()
        buf = []
        while self.pos < len(self.source):
            line_buf = []
            while self.pos < len(self.source) and self.peek() != '\n':
                line_buf.append(self.advance())
            if ''.join(line_buf).strip() == label: break
            buf.append(''.join(line_buf))
            if self.peek() == '\n': buf.append('\n'); self.advance()
        return ''.join(buf)

    def read_number(self):
        buf = []
        while self.pos < len(self.source) and (self.peek().isdigit() or self.peek() == '.'):
            buf.append(self.advance())
        raw = ''.join(buf)
        if not raw: return 0
        if raw == '0' and self.peek() in ('x','X'):
            self.advance()
            h = []
            while self.pos < len(self.source) and self.peek() in '0123456789abcdefABCDEF':
                h.append(self.advance())
            return int(''.join(h),16) if h else 0
        if raw == '.': return 0.0
        try: return float(raw) if '.' in raw else int(raw)
        except: return 0

    def read_word(self):
        buf = []
        while self.pos < len(self.source) and (self.peek().isalnum() or self.peek() == '_'):
            buf.append(self.advance())
        return ''.join(buf)

    def skip_line(self):
        while self.pos < len(self.source) and self.peek() != '\n': self.advance()

    def tokenize(self):
        src = self.source
        while self.pos < len(src):
            self.skip_ws()
            if self.pos >= len(src): break
            ch = self.peek(); line = self.line

            if ch == '#': self.advance(); self.skip_line(); continue
            if ch == '/' and self.peek(1) == '/': self.advance(); self.advance(); self.skip_line(); continue
            if ch == '/' and self.peek(1) == '*':
                self.advance(); self.advance()
                while self.pos < len(src)-1:
                    if src[self.pos:self.pos+2] == '*/': self.advance(); self.advance(); break
                    self.advance()
                continue

            if ch == '\n':
                self.advance()
                if self.tokens and self.tokens[-1].type != TT_NEWLINE:
                    self.tokens.append(Token(TT_NEWLINE,'\n',line))
                continue

            # heredoc <<<LABEL
            if src[self.pos:self.pos+3] == '<<<':
                self.tokens.append(Token(TT_STRING, self.read_heredoc(), line)); continue

            # triple string
            if src[self.pos:self.pos+3] == '"""':
                self.tokens.append(Token(TT_STRING, self.read_triple(), line)); continue

            if ch in ('"',"'"):
                self.tokens.append(Token(TT_STRING, self.read_string(ch), line)); continue

            if ch.isdigit():
                self.tokens.append(Token(TT_NUMBER, self.read_number(), line)); continue

            # negative literal (only in operator context)
            if ch == '-' and self.peek(1).isdigit():
                pt = self.tokens[-1].type if self.tokens else None
                pv = self.tokens[-1].value if self.tokens else None
                ctx_kws = {'to','by','with','and','return','show','say','print','log',
                           'in','from','store','at','of','do','then','display','output','echo'}
                if pt not in (TT_NUMBER,TT_STRING,TT_IDENT) or pv in ctx_kws:
                    self.advance()
                    self.tokens.append(Token(TT_NUMBER,-self.read_number(),line)); continue

            if ch.isalpha() or ch == '_':
                word = self.read_word()
                lower = word.lower()
                canonical = SYNONYMS.get(lower, lower)
                ttype = TT_KEYWORD if canonical in KEYWORDS else TT_IDENT
                self.tokens.append(Token(ttype, canonical if ttype==TT_KEYWORD else word, line))
                continue

            two = src[self.pos:self.pos+2]
            if two in ('<=','>=','!=','==','+=','-=','*=','/=','**','->','=>','..','::','??','|>'):
                self.advance(); self.advance()
                self.tokens.append(Token(TT_OP,two,line)); continue

            if ch in ('+','-','*','/','=','<','>','!',',','(',')','[',']',
                      '{','}',':','.','%','^','&','|','~','@','?','\\'):
                self.advance(); self.tokens.append(Token(TT_OP,ch,line)); continue

            self.advance()

        self.tokens.append(Token(TT_EOF,None,self.line))
        return self.tokens
