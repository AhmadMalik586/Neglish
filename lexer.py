# lexer.py — Neglish v3 Tokeniser
# Supports every keyword needed for the full language

TT_KEYWORD = 'KEYWORD'
TT_STRING  = 'STRING'
TT_NUMBER  = 'NUMBER'
TT_IDENT   = 'IDENT'
TT_OP      = 'OP'
TT_NEWLINE = 'NEWLINE'
TT_EOF     = 'EOF'

KEYWORDS = {
    # core
    'set','to','show','say','print','log','increase','decrease','by',
    'if','then','else','elseif','elif','otherwise','also','end',
    'repeat','times','while','do','for','each','in','from','step',
    'define','function','with','call','return','break','continue',
    'ask','and','store','input','not','or','as',
    # logic
    'both','either','neither','all','any','is','true','false','null','none',
    'greater','than','less','equal',
    # loops
    'loop','forever','until',
    # list/dict
    'list','item','of','add','remove','insert','at','pop','create',
    'map','dict','key','value','keys','values','has',
    'sort','shuffle','count','index','slice','unique','flatten',
    'sum','average','first','last','empty','reverse','contains',
    'starts','ends','length',
    # math
    'sqrt','abs','floor','ceil','round','power','random','between',
    'pi','max','min','mod','log10','log2','sin','cos','tan',
    'degrees','radians','clamp','lerp','sign','gcd','lcm',
    # string
    'uppercase','lowercase','trim','split','join','replace','substring',
    'number','string','boolean','convert','format','type','repeat_str',
    'pad_left','pad_right','count_of','char','code','regex','matches',
    # type system
    'number_type','string_type','list_type','dict_type','bool_type','null_type',
    # file
    'open','file','read','write','append','close','exists','delete','lines','copy',
    'move','rename','mkdir','listdir','isfile','isdir','size_of','ext_of',
    # json
    'json','parse','stringify','load','save','dump',
    # error
    'try','catch','error','throw','raise','finally',
    # modules (native Neglish)
    'import','use','module','export','from','package',
    # time
    'time','date','now','today','sleep','wait','seconds','milliseconds','ms',
    'timestamp','year','month','day','hour','minute','second','weekday',
    # system
    'exit','quit','clear','run','command','env','args','argument','platform',
    'username','hostname','pid','cwd','sep',
    # GUI
    'window','button','label','entry','textbox','checkbox','dropdown',
    'image','canvas','frame','progress','menu','menubar','separator',
    'tab','width','height','color','background','foreground','font',
    'size','bold','italic','x','y','row','column',
    'hide','destroy','focus','title','icon','resize',
    'alert','confirm','info','warning','update',
    'when','clicked','changed','submitted','on','emit','trigger','event','listen',
    'show','get',
    # math ops (word form)
    'plus','minus','times_word','divided','by',
    # network
    'fetch','url','post','send','receive','response','request','header',
    'body','status','method',
    # concurrent / async
    'async','await','parallel','task','spawn','after','every','timeout',
    'cancel','join_tasks',
    # data pipeline
    'pipe','filter','map_fn','reduce','each_do','collect','zip_with',
    'take','drop','chunk','group_by','order_by','where',
    # scope / variables
    'global','local','const','let','freeze',
    # OOP-lite
    'object','property','method','class','inherit','extend','self','new',
    # pattern match
    'switch','match','case','default','when',
    # assertions / test
    'assert','test','describe','expect','should','be','equal_to',
    'pass','fail','check',
    # color terminal
    'red','green','blue','yellow','cyan','magenta','white','black','colored',
    # debug
    'debug','inspect','trace','benchmark','profile',
    # misc unique
    'memo','cache','once','throttle','debounce',
    'watch','changed','observe',
    'range','enumerate','zip_pairs',
    'flatten_deep','compact','pluck',
    'uuid','hash_of','encrypt','decrypt',
    'number_format','pluralize','titlecase','camelcase','snakecase',
}

class Token:
    def __init__(self, type_, value, line=0):
        self.type  = type_
        self.value = value
        self.line  = line
    def __repr__(self):
        return f'Token({self.type}, {self.value!r}, line={self.line})'


class Lexer:
    def __init__(self, source: str):
        self.source = source
        self.pos    = 0
        self.line   = 1
        self.tokens = []

    def peek(self, offset=0):
        idx = self.pos + offset
        return self.source[idx] if idx < len(self.source) else ''

    def advance(self):
        ch = self.source[self.pos]; self.pos += 1
        if ch == '\n': self.line += 1
        return ch

    def skip_ws(self):
        while self.pos < len(self.source) and self.peek() in (' ', '\t', '\r'):
            self.advance()

    def read_string(self, quote):
        self.advance()
        buf = []
        while self.pos < len(self.source):
            ch = self.advance()
            if ch == quote: break
            if ch == '\\':
                esc = self.advance()
                buf.append({'n':'\n','t':'\t','r':'\r','\\':'\\',
                            '"':'"',"'":"'",'0':'\0'}.get(esc, esc))
            else:
                buf.append(ch)
        return ''.join(buf)

    def read_triple_string(self):
        for _ in range(3): self.advance()
        buf = []
        while self.pos < len(self.source) - 2:
            if self.source[self.pos:self.pos+3] == '"""':
                for _ in range(3): self.advance()
                break
            buf.append(self.advance())
        return ''.join(buf)

    def read_number(self):
        buf = []
        while self.pos < len(self.source) and (self.peek().isdigit() or self.peek() == '.'):
            buf.append(self.advance())
        raw = ''.join(buf)
        if not raw: return 0
        if raw == '0' and self.peek() in ('x','X'):
            self.advance()
            hb = []
            while self.pos < len(self.source) and self.peek() in '0123456789abcdefABCDEF':
                hb.append(self.advance())
            return int(''.join(hb), 16) if hb else 0
        if raw == '0' and self.peek() in ('b','B'):
            self.advance()
            bb = []
            while self.pos < len(self.source) and self.peek() in '01':
                bb.append(self.advance())
            return int(''.join(bb), 2) if bb else 0
        if raw == '.': return 0.0
        return float(raw) if '.' in raw else int(raw)

    def read_word(self):
        buf = []
        while self.pos < len(self.source) and (self.peek().isalnum() or self.peek() == '_'):
            buf.append(self.advance())
        return ''.join(buf)

    def skip_line(self):
        while self.pos < len(self.source) and self.peek() != '\n':
            self.advance()

    def tokenize(self):
        src = self.source
        while self.pos < len(src):
            self.skip_ws()
            if self.pos >= len(src): break

            ch   = self.peek()
            line = self.line

            # comments
            if ch == '#':
                self.advance(); self.skip_line(); continue
            if ch == '/' and self.peek(1) == '/':
                self.advance(); self.advance(); self.skip_line(); continue
            if ch == '/' and self.peek(1) == '*':
                self.advance(); self.advance()
                while self.pos < len(src) - 1:
                    if src[self.pos:self.pos+2] == '*/':
                        self.advance(); self.advance(); break
                    self.advance()
                continue

            # newline
            if ch == '\n':
                self.advance()
                if self.tokens and self.tokens[-1].type != TT_NEWLINE:
                    self.tokens.append(Token(TT_NEWLINE, '\n', line))
                continue

            # triple-string
            if src[self.pos:self.pos+3] == '"""':
                self.tokens.append(Token(TT_STRING, self.read_triple_string(), line))
                continue

            # strings
            if ch in ('"', "'"):
                self.tokens.append(Token(TT_STRING, self.read_string(ch), line))
                continue

            # positive number
            if ch.isdigit():
                self.tokens.append(Token(TT_NUMBER, self.read_number(), line))
                continue

            # negative number literal (only after operators / keywords)
            if ch == '-' and self.peek(1).isdigit():
                prev_type = self.tokens[-1].type if self.tokens else None
                prev_val  = self.tokens[-1].value if self.tokens else None
                value_types = (TT_NUMBER, TT_STRING, TT_IDENT)
                value_kws   = {'to','by','with','and','return','show','say','print',
                               'log','in','from','store','at','of','do','then'}
                if prev_type not in value_types or prev_val in value_kws:
                    self.advance()
                    self.tokens.append(Token(TT_NUMBER, -self.read_number(), line))
                    continue

            # word / keyword
            if ch.isalpha() or ch == '_':
                word  = self.read_word()
                lower = word.lower()
                ttype = TT_KEYWORD if lower in KEYWORDS else TT_IDENT
                self.tokens.append(Token(ttype, lower if ttype == TT_KEYWORD else word, line))
                continue

            # two-char ops
            two = src[self.pos:self.pos+2]
            if two in ('<=','>=','!=','==','+=','-=','*=','/=','**','->','=>','..','::'):
                self.advance(); self.advance()
                self.tokens.append(Token(TT_OP, two, line))
                continue

            # single-char
            if ch in ('+','-','*','/','=','<','>','!',',','(',')','[',']',
                      '{','}',':','.','%','^','&','|','~','@','?','\\'):
                self.advance()
                self.tokens.append(Token(TT_OP, ch, line))
                continue

            self.advance()  # skip unknown

        self.tokens.append(Token(TT_EOF, None, self.line))
        return self.tokens
