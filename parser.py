# parser.py — Neglish v4 Parser
# Full OOP, lambdas, pattern matching, natural language, symbol aliases

from lexer import (TT_KEYWORD as KW, TT_STRING as STR, TT_NUMBER as NUM,
                   TT_IDENT as ID, TT_OP as OP, TT_NEWLINE as NL, TT_EOF as EOF)

class ParseError(Exception):
    def __init__(self, msg, line=0):
        super().__init__(f"[Line {line}] Parse Error: {msg}")

class Parser:
    def __init__(self, tokens, permissive_mode=True, strict_mode=False):
        self.tokens = tokens
        self.pos = 0
        self.permissive_mode = permissive_mode
        self.strict_mode = strict_mode
        self.errors = []

    # ─── helpers ───────────────────────────────────────────────────────────────
    def _skip(self):
        while self.pos < len(self.tokens) and self.tokens[self.pos].type == NL:
            self.pos += 1

    def _cur(self):
        self._skip()
        return self.tokens[self.pos] if self.pos < len(self.tokens) else self.tokens[-1]

    def _adv(self):
        t = self.tokens[self.pos]; self.pos += 1; return t

    def _adv_skip(self):
        self._skip(); return self._adv()

    def _match_kw(self, *kws):
        self._skip()
        if self.pos < len(self.tokens) and self.tokens[self.pos].type == KW \
                and self.tokens[self.pos].value in kws:
            return self._adv()
        return None

    def _match_op(self, *ops):
        self._skip()
        if self.pos < len(self.tokens) and self.tokens[self.pos].type == OP \
                and self.tokens[self.pos].value in ops:
            return self._adv()
        return None

    def _expect_kw(self, *kws):
        self._skip()
        t = self._cur()
        if t.value in kws:
            return self._adv()
        if self.permissive_mode and not self.strict_mode:
            # Infer optional glue keywords in permissive mode.
            return t
        t = self._adv()
        raise ParseError(f"Expected {kws}, got {t.value!r}", t.line)

    def _peek_kw(self, *kws):
        self._skip()
        return self.pos < len(self.tokens) and \
               self.tokens[self.pos].type == KW and \
               self.tokens[self.pos].value in kws

    def _peek_op(self, *ops):
        self._skip()
        return self.pos < len(self.tokens) and \
               self.tokens[self.pos].type == OP and \
               self.tokens[self.pos].value in ops

    def _at_end(self):
        self._skip()
        return self.pos >= len(self.tokens) or self.tokens[self.pos].type == EOF

    def _at_block_end(self):
        self._skip()
        if self.pos >= len(self.tokens): return True
        t = self.tokens[self.pos]
        return t.type == EOF or (t.type == KW and t.value in (
            'end','else','elseif','elif','otherwise','also',
            'catch','case','default','when','on'))

    def _consume_articles(self):
        """Silently consume optional 'the', 'a', 'an'."""
        while self._match_kw('the', 'a', 'an'):
            pass

    # ─── expression parsing ────────────────────────────────────────────────────
    def _parse_primary(self):
        self._skip()
        if self.pos >= len(self.tokens):
            raise ParseError("Unexpected end of input")
        t = self.tokens[self.pos]

        # ── unary not / minus
        if t.type == KW and t.value == 'not':
            self._adv(); operand = self._parse_primary()
            return {'type':'unary','op':'not','operand':operand,'line':t.line}
        if t.type == OP and t.value == '-':
            self._adv(); operand = self._parse_primary()
            return {'type':'unary','op':'-','operand':operand,'line':t.line}

        # ── parenthesised
        if t.type == OP and t.value == '(':
            self._adv(); expr = self._parse_logic(); self._match_op(')'); return expr

        # ── list literal [a, b, c]
        if t.type == OP and t.value == '[':
            self._adv()
            items = []
            self._skip()
            while not (self.pos < len(self.tokens) and self.tokens[self.pos].type == OP and self.tokens[self.pos].value == ']'):
                if self._at_end(): break
                items.append(self._parse_logic())
                self._match_op(',')
                self._skip()
            self._match_op(']')
            return {'type':'list_literal','items':items,'line':t.line}

        # ── dict literal {key: val, ...}
        if t.type == OP and t.value == '{':
            self._adv(); pairs = []
            self._skip()
            while not (self.pos < len(self.tokens) and self.tokens[self.pos].type == OP and self.tokens[self.pos].value == '}'):
                if self._at_end(): break
                k = self._parse_logic(); self._match_op(':'); v = self._parse_logic()
                pairs.append((k,v)); self._match_op(','); self._skip()
            self._match_op('}')
            return {'type':'dict_literal','pairs':pairs,'line':t.line}

        # ── lambda expression:  lambda x, y -> expr  OR  fn x -> expr
        if t.type == KW and t.value == 'lambda':
            return self._parse_lambda_expr(t.line)

        # ── call expression (inline value)
        if t.type == KW and t.value == 'call':
            return self._parse_call_expr(t.line)

        # ── new ClassName with args (expression form)
        if t.type == KW and t.value == 'new':
            return self._parse_new_expr(t.line)

        # ── item N of list
        if t.type == KW and t.value == 'item':
            peek_pos = self.pos + 1
            while peek_pos < len(self.tokens) and self.tokens[peek_pos].type == NL:
                peek_pos += 1
            if peek_pos < len(self.tokens) and self.tokens[peek_pos].value not in (
                    'to','in','from','and','or','end','then','with','by',',','the','a','an'):
                self._adv()
                idx = self._parse_primary()
                self._skip()
                if self.pos < len(self.tokens) and self.tokens[self.pos].value == 'of':
                    self._adv()
                    name_tok = self._adv_skip()
                    return {'type':'list_access','list':name_tok.value,'index':idx,'line':t.line}
                else:
                    return {'type':'var','name':'item','line':t.line}
            else:
                self._adv(); return {'type':'var','name':'item','line':t.line}

        # ── two-arg builtins:  gcd of A and B
        TWO_ARG = {'gcd','lcm','max','min','power','clamp','lerp',
                   'contains_all','contains_any','intersection','difference','union',
                   'zip_pairs','dict_merge','number_format','pluralize',
                   'replace_regex','find_all','index_of','pad_left','pad_right',
                   'repeat_str','count_of','percent','percent_of',
                   'random_float','weighted_choice','sample','path_join'}
        if t.type == KW and t.value in TWO_ARG:
            peek_pos = self.pos+1
            while peek_pos < len(self.tokens) and self.tokens[peek_pos].type == NL: peek_pos+=1
            if peek_pos < len(self.tokens) and self.tokens[peek_pos].value == 'of':
                fn = t.value; self._adv(); self._match_kw('of')
                a1 = self._parse_primary(); self._match_kw('and','by','with')
                a2 = self._parse_primary()
                # optional third arg (clamp lo hi)
                args = [a1, a2]
                if self._match_kw('and','by'): args.append(self._parse_primary())
                return {'type':'builtin_call','fn':fn,'args':args,'line':t.line}

        # ── one-arg keyword builtins (must be followed by 'of')
        ONE_ARG_KW = {
            'sqrt','abs','floor','ceil','round','log10','log2',
            'sin','cos','tan','asin','acos','atan','degrees','radians','sign',
            'uppercase','lowercase','trim','trim_left','trim_right',
            'reverse','titlecase','camelcase','snakecase',
            'split_lines','length','type',
            'first','last','sum','average','median','stdev','variance',
            'unique','flatten','flatten_deep','sort','sort_desc',
            'shuffle','count','compact',
            'to_bool','to_list',
            'is_number','is_string','is_list','is_dict','is_null','is_bool',
            'is_prime','is_even','is_odd','factorial','fibonacci',
            'dict_keys','dict_values','dict_size','dict_to_list',
            'max_of','min_of','json_parse','json_stringify','json_pretty',
            'read_file','list_dir','file_exists','is_file','is_dir',
            'file_size','file_ext','file_name','file_dir',
            'number','string',
        }
        if t.type == KW and t.value in ONE_ARG_KW:
            pp = self.pos+1
            while pp < len(self.tokens) and self.tokens[pp].type == NL: pp+=1
            if pp < len(self.tokens) and self.tokens[pp].value == 'of':
                fn = 'type_of' if t.value == 'type' else \
                     'to_number' if t.value == 'number' else \
                     'to_string' if t.value == 'string' else t.value
                self._adv(); self._match_kw('of')
                arg = self._parse_primary()
                return {'type':'builtin_call','fn':fn,'args':[arg],'line':t.line}

        # ── zero-arg builtins: uuid, now, today, etc.  (followed by 'of' optionally)
        ZERO_ARG_KW = {'now','today','timestamp','time_ms','year','month','day',
                       'hour','minute','second','weekday','platform','username',
                       'hostname','pid','cwd','sep'}
        if t.type == KW and t.value in ZERO_ARG_KW:
            self._adv()
            # consume optional 'of ""'
            if self._match_kw('of'):
                self._skip()
                if self.pos < len(self.tokens) and self.tokens[self.pos].type == STR:
                    self._adv()
            return {'type':'builtin_call','fn':t.value,'args':[],'line':t.line}

        # ── IDENT-form builtins (is_prime, fibonacci, etc. with 'of')
        IDENT_1ARG = {
            'is_prime','is_even','is_odd','factorial','fibonacci',
            'to_number','to_string','to_bool','to_list',
            'is_number','is_string','is_list','is_dict','is_null','is_bool',
            'split_lines','read_file','list_dir',
            'file_exists','is_file','is_dir','file_size','file_ext',
            'file_name','file_dir','env_get','json_parse','json_stringify','json_pretty',
            'sort_desc','flatten_deep','compact','max_of','min_of',
            'dict_keys','dict_values','dict_size','dict_to_list',
            'median','stdev','variance','timestamp','time_ms','uuid','hash_of',
        }
        IDENT_0ARG = {'uuid','now','today','year','month','day','hour','minute',
                      'second','weekday','timestamp','time_ms','platform','username',
                      'hostname','pid','cwd','sep'}
        if t.type == ID:
            pp = self.pos+1
            while pp < len(self.tokens) and self.tokens[pp].type == NL: pp+=1
            if pp < len(self.tokens) and self.tokens[pp].value == 'of':
                fn_name = t.value
                if fn_name in IDENT_0ARG:
                    self._adv(); self._match_kw('of')
                    if self.pos<len(self.tokens) and self.tokens[self.pos].type==STR: self._adv()
                    return {'type':'builtin_call','fn':fn_name,'args':[],'line':t.line}
                if fn_name in IDENT_1ARG:
                    self._adv(); self._match_kw('of')
                    arg = self._parse_primary()
                    return {'type':'builtin_call','fn':fn_name,'args':[arg],'line':t.line}

        # ── random between A and B
        if t.type == KW and t.value == 'random':
            self._adv()
            if self._match_kw('between'):
                lo = self._parse_primary(); self._match_kw('and'); hi = self._parse_primary()
                return {'type':'builtin_call','fn':'random_between','args':[lo,hi],'line':t.line}
            if self._match_kw('float'):
                lo = self._parse_primary(); self._match_kw('and'); hi = self._parse_primary()
                return {'type':'builtin_call','fn':'random_float','args':[lo,hi],'line':t.line}
            return {'type':'builtin_call','fn':'random_between',
                    'args':[{'type':'number','value':0,'line':t.line},
                            {'type':'number','value':1,'line':t.line}],'line':t.line}

        # ── format_str "template" with a, b
        if t.type == KW and t.value == 'format_str':
            self._adv(); template = self._parse_primary()
            args = [template]
            if self._match_kw('with'):
                args.append(self._parse_primary())
                while self._match_op(','): args.append(self._parse_primary())
            return {'type':'builtin_call','fn':'format_str','args':args,'line':t.line}

        # ── split S by SEP
        if t.type == KW and t.value == 'split':
            pp=self.pos+1
            while pp<len(self.tokens) and self.tokens[pp].type==NL: pp+=1
            if pp<len(self.tokens) and self.tokens[pp].value not in ('by',):
                pass  # fall through to var
            else:
                self._adv(); s = self._parse_primary(); self._match_kw('by')
                sep = self._parse_primary()
                return {'type':'builtin_call','fn':'split','args':[s,sep],'line':t.line}

        # ── join LIST with SEP
        if t.type == KW and t.value == 'join':
            self._adv(); lst = self._parse_primary(); self._match_kw('with')
            sep = self._parse_primary()
            return {'type':'builtin_call','fn':'join','args':[lst,sep],'line':t.line}

        # ── replace in S find X with Y
        if t.type == KW and t.value == 'replace':
            self._adv(); self._match_kw('in')
            s = self._parse_primary(); self._match_kw('find')
            f = self._parse_primary(); self._match_kw('with')
            r = self._parse_primary()
            return {'type':'builtin_call','fn':'replace','args':[s,f,r],'line':t.line}

        # ── substring of S from A to B
        if t.type == KW and t.value == 'substring':
            self._adv(); self._match_kw('of')
            s = self._parse_primary(); self._match_kw('from')
            a = self._parse_primary(); self._match_kw('to')
            b = self._parse_primary()
            return {'type':'builtin_call','fn':'substring','args':[s,a,b],'line':t.line}

        # ── slice of LIST from A to B
        if t.type == KW and t.value == 'slice':
            self._adv(); self._match_kw('of')
            lst = self._parse_primary(); self._match_kw('from')
            a = self._parse_primary(); self._match_kw('to')
            b = self._parse_primary()
            return {'type':'builtin_call','fn':'slice','args':[lst,a,b],'line':t.line}

        # ── keys of DICT / values of DICT
        if t.type == KW and t.value in ('keys','values'):
            fn = 'dict_keys' if t.value=='keys' else 'dict_values'
            self._adv(); self._match_kw('of')
            d = self._adv_skip()
            return {'type':'builtin_call','fn':fn,'args':[{'type':'var','name':d.value,'line':d.line}],'line':t.line}

        # ── choice of LIST
        if t.type == KW and t.value == 'choice':
            self._adv(); self._match_kw('of')
            lst = self._parse_primary()
            return {'type':'builtin_call','fn':'choice','args':[lst],'line':t.line}

        # ── key "K" of DICT (dict access expression)
        if t.type == KW and t.value == 'key':
            self._adv()
            k = self._parse_primary()
            self._match_kw('of')
            d = self._adv_skip()
            return {'type':'dict_access','dict':d.value,'key':k,'line':t.line}

        # ── STOP keywords — should not appear in expression
        STOP = {'then','do','end','else','elseif','elif','otherwise','also',
                'catch','case','default','where','store'}
        if t.type == KW and t.value in STOP:
            raise ParseError(f"Unexpected keyword '{t.value}' in expression", t.line)

        # ── literals
        if t.type == STR:
            self._adv(); return {'type':'string','value':t.value,'line':t.line}
        if t.type == NUM:
            self._adv(); return {'type':'number','value':t.value,'line':t.line}
        if t.type == KW and t.value in ('true','false'):
            self._adv(); return {'type':'bool','value':t.value=='true','line':t.line}
        if t.type == KW and t.value in ('null','none'):
            self._adv(); return {'type':'null','line':t.line}

        # ── identifier / variable (with dot-chain and index)
        if t.type in (ID, KW):
            self._adv()
            node = {'type':'var','name':t.value,'line':t.line}
            # dot-access chain
            while self._peek_op('.'):
                self._adv()
                prop = self._adv_skip()
                node = {'type':'attr_access','obj':node,'attr':prop.value,'line':t.line}
            # index access
            while self._peek_op('['):
                self._adv()
                idx = self._parse_logic(); self._match_op(']')
                node = {'type':'index_access','obj':node,'index':idx,'line':t.line}
            return node

        raise ParseError(f"Unexpected token: {t.value!r}", t.line)

    def _parse_lambda_expr(self, line):
        """lambda x, y -> expr  OR  lambda -> expr  (no params)"""
        self._adv()  # consume 'lambda'/'fn'/'given'
        params = []
        # collect params until '->' or 'yields'
        self._skip()
        if self.pos < len(self.tokens) and self.tokens[self.pos].type not in (OP,) and \
                self.tokens[self.pos].value not in ('->','yields','then'):
            if self.tokens[self.pos].type in (ID, KW) and \
                    self.tokens[self.pos].value not in ('then','do','-','yields'):
                params.append(self._adv().value)
                while self._match_op(','):
                    params.append(self._adv_skip().value)
        self._match_op('->'); self._match_kw('yields','then')
        body_expr = self._parse_logic()
        return {'type':'lambda_expr','params':params,'body':body_expr,'line':line}

    def _parse_call_expr(self, line):
        """call fn.name with args — returns a value"""
        self._adv()  # consume 'call'
        name_tok = self._adv_skip()
        name = name_tok.value
        # dotted name: call obj.method
        while self._peek_op('.'):
            self._adv(); member = self._adv_skip(); name = name + '.' + member.value
        args = []
        if self._match_kw('with'):
            args.append(self._parse_logic())
            while self._match_op(','): args.append(self._parse_logic())
        return {'type':'call_expr','name':name,'args':args,'line':line}

    def _parse_new_expr(self, line):
        """new ClassName with args"""
        self._adv()  # consume 'new'
        cls_tok = self._adv_skip()
        args = []
        if self._match_kw('with'):
            args.append(self._parse_logic())
            while self._match_op(','): args.append(self._parse_logic())
        return {'type':'new_expr','class':cls_tok.value,'args':args,'line':line}

    def _parse_arith(self):
        left = self._parse_primary()
        while True:
            op = self._match_op('+','-','*','/','%','**','^')
            if op:
                right = self._parse_primary()
                left = {'type':'binop','op':op.value,'left':left,'right':right,'line':op.line}
            else: break
        return left

    def _parse_compare_with_left(self, left):
        """Parse comparison given already-parsed left side."""
        self._skip()
        line = left.get('line',0)

        if self._match_kw('is'):
            neg = self._match_kw('not')
            # is at least / is at most
            if self._match_kw('at'):
                qualifier = self._match_kw('least','most')
                op = '<=' if (qualifier and qualifier.value=='most') else '>='
                if neg: op = '>' if op=='>=' else '<'
                right = self._parse_arith()
                return {'type':'compare','op':op,'left':left,'right':right}
            # is between A and B
            if self._match_kw('between'):
                lo = self._parse_arith(); self._match_kw('and'); hi = self._parse_arith()
                return {'type':'between_check','left':left,'lo':lo,'hi':hi,'negate':bool(neg)}
            # is approximately / roughly / about
            if self._match_kw('approximately','roughly','about'):
                right = self._parse_arith()
                return {'type':'approx_check','left':left,'right':right,'negate':bool(neg)}
            if self._match_kw('greater'):
                self._match_kw('than')
                op = '<=' if neg else '>'
            elif self._match_kw('less'):
                self._match_kw('than')
                op = '>=' if neg else '<'
            elif self._match_kw('equal'):
                self._match_kw('to')
                op = '!=' if neg else '=='
            elif self._match_kw('empty'):
                return {'type':'builtin_call','fn':'is_empty','args':[left],'line':line}
            elif self._match_kw('null','none'):
                op = '!=' if neg else '=='
                return {'type':'compare','op':op,'left':left,'right':{'type':'null'}}
            else:
                op = '!=' if neg else '=='
            right = self._parse_arith()
            return {'type':'compare','op':op,'left':left,'right':right}

        # symbol operators: > < >= <= == != (also served as English aliases)
        op_tok = self._match_op('==','!=','>=','<=','>','<')
        if op_tok:
            right = self._parse_arith()
            return {'type':'compare','op':op_tok.value,'left':left,'right':right}

        if self._match_kw('contains'):
            right = self._parse_arith()
            return {'type':'builtin_call','fn':'contains','args':[left,right],'line':line}
        if self._match_kw('starts'):
            self._match_kw('with'); right = self._parse_arith()
            return {'type':'builtin_call','fn':'starts_with','args':[left,right],'line':line}
        if self._match_kw('ends'):
            self._match_kw('with'); right = self._parse_arith()
            return {'type':'builtin_call','fn':'ends_with','args':[left,right],'line':line}

        return left

    def _parse_compare(self):
        left = self._parse_arith()
        return self._parse_compare_with_left(left)

    def _parse_logic(self):
        left = self._parse_compare()
        while True:
            self._skip()
            if self.pos < len(self.tokens) and self.tokens[self.pos].type == KW \
                    and self.tokens[self.pos].value in ('and','both'):
                nx = self.pos+1
                while nx<len(self.tokens) and self.tokens[nx].type==NL: nx+=1
                if nx<len(self.tokens) and self.tokens[nx].value in ('store','in','then','do','end'):
                    break
                self._adv(); right = self._parse_compare()
                left = {'type':'logic','op':'and','left':left,'right':right}
            elif self._peek_kw('or','either'):
                self._adv(); right = self._parse_compare()
                left = {'type':'logic','op':'or','left':left,'right':right}
            elif self._match_op('??'):
                right = self._parse_compare()
                left = {'type':'null_coalesce','left':left,'right':right,'line':left.get('line',0)}
            elif self._match_op('|>'):
                # pipe: value |> funcName  →  call funcName(value)
                right = self._parse_primary()
                left = {'type':'pipe_expr','value':left,'func':right,'line':left.get('line',0)}
            else: break
        return left

    def _parse_expr(self): return self._parse_logic()

    # ─── block ────────────────────────────────────────────────────────────────
    def _parse_block(self):
        stmts = []
        while not self._at_block_end() and not self._at_end():
            s = self._parse_stmt()
            if s: stmts.append(s)
        return stmts

    # ─── statements ───────────────────────────────────────────────────────────
    def _parse_stmt(self):
        self._skip()
        if self._at_end(): return None
        t = self.tokens[self.pos]
        if t.type == NL: self._adv(); return None
        if t.type == KW and t.value == 'end': self._adv(); return None

        if t.type == KW:
            kw = t.value; self._adv()
            dispatch = {
                'show':      self._s_show,
                'say':       self._s_show,
                'print':     self._s_show,
                'log':       self._s_show,
                'display':   self._s_show,
                'output':    self._s_show,
                'echo':      self._s_show,
                'set':       self._s_set,
                'let':       self._s_set,
                'const':     self._s_set,
                'increase':  self._s_increase,
                'decrease':  self._s_decrease,
                'if':        self._s_if,
                'unless':    self._s_unless,
                'repeat':    self._s_repeat,
                'while':     self._s_while,
                'for':       self._s_for,
                'loop':      self._s_forever,
                'forever':   self._s_forever,
                'define':    self._s_define,
                'class':     self._s_class,
                'new':       self._s_new,
                'call':      self._s_call,
                'return':    self._s_return,
                'break':     lambda ln: {'type':'break','line':ln},
                'continue':  lambda ln: {'type':'continue','line':ln},
                'ask':       self._s_ask,
                'prompt':    self._s_ask,
                'create':    self._s_create,
                'when':      self._s_when,
                'add':       self._s_add,
                'remove':    self._s_remove,
                'insert':    self._s_insert,
                'pop':       self._s_pop,
                'sort':      self._s_sort_stmt,
                'shuffle':   self._s_shuffle_stmt,
                'open':      self._s_file_open,
                'write':     self._s_file_write,
                'append':    self._s_file_append,
                'close':     self._s_file_close,
                'read':      self._s_file_read,
                'delete':    self._s_delete,
                'save':      self._s_json_save,
                'load':      self._s_json_load,
                'try':       self._s_try,
                'throw':     self._s_throw,
                'raise':     self._s_throw,
                'assert':    self._s_assert,
                'import':    self._s_import,
                'use':       self._s_import,
                'export':    self._s_export,
                'package':   self._s_package,
                'sleep':     self._s_sleep,
                'wait':      self._s_sleep,
                'exit':      lambda ln: {'type':'exit','line':ln},
                'quit':      lambda ln: {'type':'exit','line':ln},
                'clear':     lambda ln: {'type':'clear','line':ln},
                'run':       self._s_run,
                'debug':     self._s_debug,
                'inspect':   self._s_inspect,
                'trace':     lambda ln: {'type':'trace','line':ln},
                'freeze':    self._s_freeze,
                'global':    self._s_global,
                'watch':     self._s_watch,
                'emit':      self._s_emit,
                'on':        self._s_on_event,
                'filter':    self._s_filter,
                'map_fn':    self._s_map_fn,
                'reduce':    self._s_reduce,
                'collect':   self._s_collect,
                'pipe':      self._s_pipe,
                'spawn':     self._s_spawn,
                'after':     self._s_after,
                'every':     self._s_every,
                'benchmark': self._s_benchmark,
                'memo':      self._s_memo,
                'describe':  self._s_describe,
                'test':      self._s_test,
                'expect':    self._s_expect,
                'check':     self._s_check,
                'match':     self._s_match,
                'update':    self._s_update_label,
                'get':       self._s_get_entry,
                'set_entry': self._s_set_entry,
                'alert':     self._s_alert,
                'confirm':   self._s_confirm,
                'hide':      self._s_hide,
                'toast':     self._s_toast,
                'dialog':    self._s_dialog,
                'bind_key':  self._s_bind_key,
                'play_sound':self._s_play_sound,
                'fetch':     self._s_fetch,
                'host':      self._s_host,
                'serve':     self._s_host,
                'webview':   self._s_webview,
                'open_url':  self._s_webview,
                'stop_server': self._s_stop_server,
                'fusion':    self._s_fusion,
            }
            if kw in dispatch:
                return dispatch[kw](t.line)
            return self._s_ident(kw, t.line)

        if t.type == ID:
            name = t.value; self._adv()
            # compound assignment: x += / -= etc
            op = self._match_op('+=','-=','*=','/=','=')
            if op:
                expr = self._parse_expr()
                return {'type':'compound_assign','name':name,'op':op.value,'expr':expr,'line':t.line}
            # dot assignment: obj.prop = val
            if self._peek_op('.'):
                self._adv(); prop = self._adv_skip()
                full = name + '.' + prop.value
                # more dots
                while self._peek_op('.'):
                    self._adv(); p2 = self._adv_skip(); full += '.' + p2.value
                op2 = self._match_op('=','+=','-=')
                val = self._parse_expr()
                op_str = op2.value if op2 else '='
                return {'type':'dot_assign','path':full,'op':op_str,'expr':val,'line':t.line}
            # index assignment: lst[i] = val
            if self._peek_op('['):
                self._adv(); key = self._parse_expr(); self._match_op(']')
                self._match_op('='); val = self._parse_expr()
                return {'type':'index_assign','name':name,'key':key,'value':val,'line':t.line}
            return self._s_ident(name, t.line)

        self._adv(); return None

    # ─── individual statement parsers ─────────────────────────────────────────
    def _s_show(self, line):
        self._consume_articles()
        parts = [self._parse_expr()]
        while self._match_op(','): parts.append(self._parse_expr())
        return {'type':'show','parts':parts,'line':line}

    def _s_set(self, line):
        # 'set key "k" of dict to val' — dict-key set
        if self._match_kw('key'):
            k = self._parse_primary(); self._expect_kw('of')
            d = self._adv_skip(); self._expect_kw('to'); v = self._parse_expr()
            return {'type':'dict_set','dict':d.value,'key':k,'value':v,'line':line}
        self._consume_articles()
        name_tok = self._adv_skip(); name = name_tok.value
        # dot-path: set obj.prop to val
        if self._peek_op('.'):
            self._adv(); prop = self._adv_skip()
            full = name + '.' + prop.value
            while self._peek_op('.'):
                self._adv(); p2 = self._adv_skip(); full += '.' + p2.value
            self._expect_kw('to'); v = self._parse_expr()
            return {'type':'dot_assign','path':full,'op':'=','expr':v,'line':line}
        self._expect_kw('to'); expr = self._parse_expr()
        return {'type':'set','name':name,'expr':expr,'line':line}

    def _s_increase(self, line):
        self._consume_articles()
        name_tok = self._adv_skip()
        name = name_tok.value
        if self._peek_op('.'):
            self._adv(); prop = self._adv_skip(); name = name + '.' + prop.value
        self._expect_kw('by'); expr = self._parse_expr()
        return {'type':'increase','name':name,'expr':expr,'line':line}

    def _s_decrease(self, line):
        self._consume_articles()
        name_tok = self._adv_skip()
        name = name_tok.value
        if self._peek_op('.'):
            self._adv(); prop = self._adv_skip(); name = name + '.' + prop.value
        self._expect_kw('by'); expr = self._parse_expr()
        return {'type':'decrease','name':name,'expr':expr,'line':line}

    def _s_if(self, line):
        cond = self._parse_expr(); self._match_kw('then')
        body = self._parse_block(); branches = []; else_body = []
        while True:
            self._skip()
            if self.pos >= len(self.tokens): break
            tv = self.tokens[self.pos].value
            if tv in ('elseif','elif'):
                self._adv(); ec = self._parse_expr(); self._match_kw('then')
                branches.append({'cond':ec,'body':self._parse_block()})
            elif tv in ('else','otherwise','also'):
                self._adv(); else_body = self._parse_block(); break
            else: break
        self._match_kw('end')
        return {'type':'if','cond':cond,'body':body,'elseif':branches,'else':else_body,'line':line}

    def _s_unless(self, line):
        """unless cond then ... end  →  if not cond then ... end"""
        cond = self._parse_expr(); self._match_kw('then')
        body = self._parse_block(); else_body = []
        if self._match_kw('else','otherwise','also'): else_body = self._parse_block()
        self._match_kw('end')
        neg_cond = {'type':'unary','op':'not','operand':cond,'line':line}
        return {'type':'if','cond':neg_cond,'body':body,'elseif':[],'else':else_body,'line':line}

    def _s_repeat(self, line):
        count = self._parse_expr(); self._match_kw('times')
        var = None
        if self._match_kw('as'): var = self._adv_skip().value
        body = self._parse_block(); self._match_kw('end')
        return {'type':'repeat','count':count,'var':var,'body':body,'line':line}

    def _s_while(self, line):
        cond = self._parse_expr(); self._match_kw('do')
        body = self._parse_block(); self._match_kw('end')
        return {'type':'while','cond':cond,'body':body,'line':line}

    def _s_for(self, line):
        if self._match_kw('each'):
            var_tok = self._adv_skip()
            idx_var = None
            if self._match_op(','):
                idx_var = self._adv_skip().value  # optional index variable
            self._expect_kw('in')
            lst = self._parse_expr(); body = self._parse_block(); self._match_kw('end')
            return {'type':'for_each','var':var_tok.value,'idx_var':idx_var,'list':lst,'body':body,'line':line}
        else:
            var_tok = self._adv_skip(); self._expect_kw('from')
            start = self._parse_expr(); self._expect_kw('to')
            end = self._parse_expr()
            step = None
            if self._match_kw('step'): step = self._parse_expr()
            body = self._parse_block(); self._match_kw('end')
            return {'type':'for_range','var':var_tok.value,'start':start,'end':end,
                    'step':step,'body':body,'line':line}

    def _s_forever(self, line):
        body = self._parse_block(); self._match_kw('end')
        return {'type':'forever','body':body,'line':line}

    def _s_define(self, line):
        self._match_kw('function')
        name_tok = self._adv_skip(); params = []; defaults = {}
        if self._match_kw('with','takes','given'):
            while True:
                self._skip()
                if self.pos >= len(self.tokens): break
                t2 = self.tokens[self.pos]
                if t2.type in (ID,KW) and t2.value not in ('end',):
                    pname = self._adv().value
                    params.append(pname)
                    # support default value: define func with x = 10
                    if self._match_op('='):
                        defaults[pname] = self._parse_arith()
                    if not self._match_op(','): break
                else: break
        body = self._parse_block(); self._match_kw('end')
        node = {'type':'define','name':name_tok.value,'params':params,'body':body,'line':line}
        if defaults: node['defaults'] = defaults
        return node

    # ─── OOP ──────────────────────────────────────────────────────────────────
    def _s_class(self, line):
        """define class Dog inherit Animal"""
        name_tok = self._adv_skip()
        parent = None
        if self._match_kw('inherit','extends','extend','implements'):
            parent = self._adv_skip().value
        body = self._parse_block(); self._match_kw('end')
        return {'type':'class_def','name':name_tok.value,'parent':parent,'body':body,'line':line}

    def _s_new(self, line):
        """new Dog with "Rex" as rex  OR  new Dog with "Rex" store in rex"""
        cls_tok = self._adv_skip(); args = []
        if self._match_kw('with'):
            args.append(self._parse_expr())
            while self._match_op(','): args.append(self._parse_expr())
        result_var = None
        if self._match_kw('as','store'):
            self._match_kw('in'); result_var = self._adv_skip().value
        return {'type':'new_obj','class':cls_tok.value,'args':args,'result':result_var,'line':line}

    # ─── function call ─────────────────────────────────────────────────────────
    def _s_call(self, line):
        name_tok = self._adv_skip(); name = name_tok.value
        while self._peek_op('.'):
            self._adv(); member = self._adv_skip(); name = name + '.' + member.value
        args = []
        if self._match_kw('with'):
            args.append(self._parse_expr())
            while self._match_op(','): args.append(self._parse_expr())
        # optional 'store in VAR'
        result_var = None
        if self._match_kw('store'): self._match_kw('in'); result_var = self._adv_skip().value
        elif self._match_kw('as'): result_var = self._adv_skip().value
        if result_var:
            return {'type':'call_store','name':name,'args':args,'var':result_var,'line':line}
        return {'type':'call','name':name,'args':args,'line':line}

    def _s_return(self, line):
        self._skip()
        t = self.tokens[self.pos]
        if t.type in (NL, EOF): return {'type':'return','expr':None,'line':line}
        expr = self._parse_expr()
        return {'type':'return','expr':expr,'line':line}

    def _s_ask(self, line):
        prompt = self._parse_expr(); self._match_kw('and')
        self._expect_kw('store'); self._expect_kw('in')
        name_tok = self._adv_skip()
        return {'type':'ask','prompt':prompt,'var':name_tok.value,'line':line}

    def _s_create(self, line):
        self._skip()
        t = self.tokens[self.pos]
        # ── create list NAME with items A, B, C
        if t.type == KW and t.value == 'list':
            self._adv()
            # detect 'create list with items A, B as name' (no explicit name before with)
            self._skip()
            next_val = self.tokens[self.pos].value if self.pos < len(self.tokens) else ''
            if next_val == 'with':
                # check if followed by 'items' or directly by expressions
                qq = self.pos + 1
                while qq < len(self.tokens) and self.tokens[qq].type == NL: qq += 1
                if qq < len(self.tokens) and self.tokens[qq].value == 'items':
                    self._adv()  # consume 'with'
                    self._adv()  # consume 'items'
                    items = [self._parse_expr()]
                    while self._match_op(','): items.append(self._parse_expr())
                    name = '_tmp'
                    if self._match_kw('as'): name = self._adv_skip().value
                    return {'type':'create_list','name':name,'items':items,'line':line}
            self._consume_articles(); name_tok = self._adv_skip()
            # handle dotted name: self.tricks
            name = name_tok.value
            if self._peek_op('.'):
                self._adv(); prop = self._adv_skip(); name = name + '.' + prop.value
            items = []
            if self._match_kw('with','containing','items'):
                self._match_kw('items')  # consume optional 'items' keyword
                # check if next real token is a block keyword
                pp = self.pos
                while pp<len(self.tokens) and self.tokens[pp].type==NL: pp+=1
                has_items = (pp<len(self.tokens) and self.tokens[pp].type not in (EOF,) and
                    self.tokens[pp].value not in ('end','else','elseif','for','while','if',
                        'repeat','define','call','show','set','increase','decrease','create',
                        'add','remove','return','export','colored','benchmark','describe',
                        'test','try','switch','class','loop','forever','after','every',
                        'spawn','sleep','open','write','close','emit','on','import','match'))
                if has_items:
                    items.append(self._parse_expr())
                    while self._match_op(','): items.append(self._parse_expr())
            return {'type':'create_list','name':name,'items':items,'line':line}

        # ── create map / dict NAME with "key" as val, ...
        if t.type == KW and t.value in ('map','dict'):
            self._adv(); self._consume_articles(); name_tok = self._adv_skip(); pairs = []
            if self._match_kw('with','containing'):
                while True:
                    self._skip()
                    if self._at_block_end() or self._at_end(): break
                    if not (self.pos<len(self.tokens) and
                            self.tokens[self.pos].type in (STR,NUM,ID,KW) and
                            self.tokens[self.pos].value not in ('end','else','elseif',
                                'for','while','if','repeat','define')):
                        break
                    k = self._parse_expr()
                    if not self._match_kw('as') and not self._match_op(':'):
                        break
                    v = self._parse_expr()
                    pairs.append((k,v))
                    if not self._match_op(','): break
            return {'type':'create_dict','name':name_tok.value,'pairs':pairs,'line':line}

        # ── create window / button / label / entry / progress
        if t.type == KW and t.value == 'window':
            self._adv(); self._consume_articles(); title_tok = self._adv_skip()
            w, h = 800, 600
            if self._match_kw('with'):
                if self._match_kw('width'): w = self._parse_expr()
                if self._match_kw('height'): h = self._parse_expr()
            return {'type':'create_window','title':title_tok.value,'width':w,'height':h,'line':line}
        if t.type == KW and t.value == 'button':
            self._adv(); self._consume_articles(); label_tok = self._adv_skip()
            self._match_kw('in'); self._match_kw('window')
            win_tok = self._adv_skip(); opts = {}
            if self._match_kw('with'): opts = self._parse_opts()
            return {'type':'create_button','label':label_tok.value,'window':win_tok.value,'opts':opts,'line':line}
        if t.type == KW and t.value == 'label':
            self._adv(); text = self._parse_expr()
            self._match_kw('in'); self._match_kw('window')
            win_tok = self._adv_skip(); opts = {}
            if self._match_kw('with'): opts = self._parse_opts()
            name = opts.pop('name', None) or str(text)[:25] if isinstance(text,str) else 'label'
            return {'type':'create_label','text':text,'window':win_tok.value,'opts':opts,'name':name,'line':line}
        if t.type == KW and t.value in ('entry','textbox'):
            self._adv(); self._consume_articles(); name_tok = self._adv_skip()
            self._match_kw('in'); self._match_kw('window'); win_tok = self._adv_skip()
            return {'type':'create_entry','name':name_tok.value,'window':win_tok.value,'line':line}
        if t.type == KW and t.value == 'progress':
            self._adv(); self._consume_articles(); name_tok = self._adv_skip()
            self._match_kw('in'); self._match_kw('window'); win_tok = self._adv_skip()
            return {'type':'create_progress','name':name_tok.value,'window':win_tok.value,'line':line}
        if t.type == KW and t.value in ('image', 'chart', 'frame', 'tab_group', 'tab'):
            kw = t.value
            self._adv(); self._consume_articles(); name_tok = self._adv_skip()
            self._match_kw('in'); self._match_kw('window'); win_tok = self._adv_skip()
            opts = {}
            if self._match_kw('with'): opts = self._parse_opts()
            return {'type': f'create_{kw}', 'name': name_tok.value, 'window': win_tok.value, 'opts': opts, 'line': line}
        if t.type == KW and t.value == 'object':
            return self._s_new(line)
        self._adv(); return None

    def _parse_opts(self):
        opts = {}
        known = ('color','background','foreground','font','size','width','height',
                 'bold','italic','x','y','row','column','name',
                 'parent', 'group', 'title', 'data', 'file', 'type', 
                 'placeholder', 'password', 'checked', 'animated', 'glass')
        while True:
            self._skip()
            if self.pos >= len(self.tokens): break
            t = self.tokens[self.pos]
            if t.type == KW and t.value in known:
                key = t.value; self._adv()
                val = self._parse_primary(); opts[key] = val
            else: break
        return opts

    def _s_when(self, line):
        self._match_kw('button'); self._consume_articles()
        label_tok = self._adv_skip(); self._expect_kw('is')
        self._match_kw('clicked','pressed','submitted')
        body = self._parse_block(); self._match_kw('end')
        return {'type':'when_clicked','label':label_tok.value,'body':body,'line':line}

    def _s_add(self, line):
        val = self._parse_expr(); self._expect_kw('to')
        self._consume_articles(); name_tok = self._adv_skip()
        name = name_tok.value
        if self._peek_op('.'):
            self._adv(); prop = self._adv_skip(); name = name + '.' + prop.value
        return {'type':'list_add','list':name,'value':val,'line':line}

    def _s_remove(self, line):
        val = self._parse_expr(); self._expect_kw('from')
        self._consume_articles(); name_tok = self._adv_skip()
        name = name_tok.value
        if self._peek_op('.'):
            self._adv(); prop = self._adv_skip(); name = name + '.' + prop.value
        return {'type':'list_remove','list':name,'value':val,'line':line}

    def _s_insert(self, line):
        val = self._parse_expr(); self._expect_kw('at')
        idx = self._parse_expr(); self._expect_kw('in')
        self._consume_articles(); name_tok = self._adv_skip()
        return {'type':'list_insert','list':name_tok.value,'value':val,'index':idx,'line':line}

    def _s_pop(self, line):
        self._match_kw('from'); self._consume_articles(); name_tok = self._adv_skip()
        var = None
        if self._match_kw('store','and'):
            self._match_kw('store'); self._match_kw('in'); var = self._adv_skip().value
        return {'type':'list_pop','list':name_tok.value,'var':var,'line':line}

    def _s_sort_stmt(self, line):
        self._consume_articles(); name_tok = self._adv_skip()
        return {'type':'list_sort','list':name_tok.value,'line':line}

    def _s_shuffle_stmt(self, line):
        self._consume_articles(); name_tok = self._adv_skip()
        return {'type':'list_shuffle','list':name_tok.value,'line':line}

    def _s_file_open(self, line):
        path = self._parse_expr(); self._match_kw('as'); name_tok = self._adv_skip()
        mode = 'r'
        pp = self.pos
        while pp<len(self.tokens) and self.tokens[pp].type==NL: pp+=1
        if pp<len(self.tokens) and self.tokens[pp].value=='for':
            q=pp+1
            while q<len(self.tokens) and self.tokens[q].type==NL: q+=1
            if q<len(self.tokens) and self.tokens[q].value in ('write','read','append'):
                self.pos = pp+2
                mode = {'write':'w','read':'r','append':'a'}[self.tokens[q].value]
        return {'type':'file_open','path':path,'name':name_tok.value,'mode':mode,'line':line}

    def _s_file_write(self, line):
        expr = self._parse_expr(); self._expect_kw('to'); name_tok = self._adv_skip()
        return {'type':'file_write','file':name_tok.value,'expr':expr,'line':line}

    def _s_file_append(self, line):
        expr = self._parse_expr(); self._expect_kw('to'); name_tok = self._adv_skip()
        return {'type':'file_append','file':name_tok.value,'expr':expr,'line':line}

    def _s_file_close(self, line):
        name_tok = self._adv_skip()
        return {'type':'file_close','file':name_tok.value,'line':line}

    def _s_file_read(self, line):
        name_tok = self._adv_skip()
        self._match_kw('and'); self._match_kw('store'); self._match_kw('in')
        var = self._adv_skip().value
        return {'type':'file_read','file':name_tok.value,'var':var,'line':line}

    def _s_delete(self, line):
        if self._match_kw('file'):
            path = self._parse_expr(); return {'type':'file_delete','path':path,'line':line}
        name_tok = self._adv_skip()
        return {'type':'delete_var','name':name_tok.value,'line':line}

    def _s_json_save(self, line):
        name_tok = self._adv_skip(); self._expect_kw('to'); path = self._parse_expr()
        return {'type':'json_save','name':name_tok.value,'path':path,'line':line}

    def _s_json_load(self, line):
        path = self._parse_expr(); self._expect_kw('in'); name_tok = self._adv_skip()
        return {'type':'json_load','path':path,'name':name_tok.value,'line':line}

    def _s_try(self, line):
        body = self._parse_block()
        catch_var = None; catch_body = []; finally_body = []
        if self._match_kw('catch'):
            self._match_kw('error')
            if self._match_kw('as'): catch_var = self._adv_skip().value
            catch_body = self._parse_block()
        if self._match_kw('finally'): finally_body = self._parse_block()
        self._match_kw('end')
        return {'type':'try','body':body,'catch_var':catch_var,'catch':catch_body,
                'finally_body':finally_body,'line':line}

    def _s_throw(self, line):
        expr = self._parse_expr()
        return {'type':'throw','expr':expr,'line':line}

    def _s_assert(self, line):
        cond = self._parse_expr(); msg = None
        if self._match_kw('else','otherwise','with'): msg = self._parse_expr()
        return {'type':'assert','cond':cond,'msg':msg,'line':line}

    def _s_import(self, line):
        name_tok = self._adv_skip()
        module_path = name_tok.value
        # Derive a safe alias from the module path (e.g. "libs/utils.neg" → "utils")
        import os as _os
        alias = module_path
        if '/' in str(module_path) or '\\' in str(module_path):
            alias = _os.path.splitext(_os.path.basename(str(module_path)))[0]
        elif str(module_path).endswith('.neg'):
            alias = str(module_path)[:-4]
        if self._match_kw('as'): alias = self._adv_skip().value
        return {'type':'import','module':module_path,'alias':alias,'line':line}

    def _s_export(self, line):
        name_tok = self._adv_skip()
        return {'type':'export','name':name_tok.value,'line':line}

    def _s_package(self, line):
        name_tok = self._adv_skip()
        return {'type':'package_decl','name':name_tok.value,'line':line}

    def _s_sleep(self, line):
        dur = self._parse_expr()
        unit = 'seconds'
        if self._match_kw('seconds','milliseconds','ms','second','millisecond'):
            unit = self.tokens[self.pos-1].value
        return {'type':'sleep','duration':dur,'unit':unit,'line':line}

    def _s_run(self, line):
        expr = self._parse_expr(); var = None
        if self._match_kw('store','and'):
            self._match_kw('store'); self._match_kw('in'); var = self._adv_skip().value
        return {'type':'run_cmd','expr':expr,'var':var,'line':line}

    def _s_debug(self, line):
        expr = self._parse_expr()
        return {'type':'debug','expr':expr,'line':line}

    def _s_inspect(self, line):
        name_tok = self._adv_skip()
        return {'type':'inspect','name':name_tok.value,'line':line}

    def _s_freeze(self, line):
        name_tok = self._adv_skip()
        return {'type':'freeze','name':name_tok.value,'line':line}

    def _s_global(self, line):
        name_tok = self._adv_skip()
        return {'type':'global_decl','name':name_tok.value,'line':line}

    def _s_watch(self, line):
        name_tok = self._adv_skip(); body = self._parse_block(); self._match_kw('end')
        return {'type':'watch','name':name_tok.value,'body':body,'line':line}

    def _s_emit(self, line):
        event_tok = self._adv_skip(); data = None
        if self._match_kw('with'): data = self._parse_expr()
        return {'type':'emit','event':event_tok.value,'data':data,'line':line}

    def _s_on_event(self, line):
        event_tok = self._adv_skip(); body = self._parse_block(); self._match_kw('end')
        return {'type':'on_event','event':event_tok.value,'body':body,'line':line}

    # ─── pipelines ─────────────────────────────────────────────────────────────
    def _s_filter(self, line):
        lst = self._parse_expr(); self._match_kw('where')
        var_tok = self._adv_skip()
        left_node = {'type':'var','name':var_tok.value,'line':var_tok.line}
        cond = self._parse_compare_with_left(left_node)
        result_var = None
        if self._match_kw('as'): result_var = self._adv_skip().value
        return {'type':'pipe_filter','list':lst,'var':var_tok.value,'cond':cond,'result':result_var,'line':line}

    def _s_map_fn(self, line):
        lst = self._parse_expr(); self._match_kw('with')
        var_tok = self._adv_skip(); self._match_kw('as','then')
        transform = self._parse_expr()
        result_var = None
        if self._match_kw('store'): self._match_kw('in'); result_var = self._adv_skip().value
        elif self._match_kw('as'): result_var = self._adv_skip().value
        return {'type':'pipe_map','list':lst,'var':var_tok.value,'transform':transform,'result':result_var,'line':line}

    def _s_reduce(self, line):
        lst = self._parse_expr(); self._match_kw('with','starting')
        start = self._parse_expr(); self._match_kw('using')
        var_tok = self._adv_skip(); self._match_kw('as')
        op_expr = self._parse_expr()
        result_var = None
        if self._match_kw('store'): self._match_kw('in'); result_var = self._adv_skip().value
        elif self._match_kw('as'): result_var = self._adv_skip().value
        return {'type':'pipe_reduce','list':lst,'start':start,'var':var_tok.value,
                'op_expr':op_expr,'result':result_var,'line':line}

    def _s_collect(self, line):
        var_tok = self._adv_skip(); self._expect_kw('from'); lst = self._parse_expr()
        cond = None
        if self._match_kw('where'):
            left = {'type':'var','name':var_tok.value,'line':var_tok.line}
            cond = self._parse_compare_with_left(left)
        result_var = None
        if self._match_kw('as','store'):
            self._match_kw('in'); result_var = self._adv_skip().value
        return {'type':'collect','var':var_tok.value,'list':lst,'cond':cond,'result':result_var,'line':line}

    def _s_pipe(self, line):
        expr = self._parse_expr(); self._expect_kw('through')
        fns = [self._adv_skip().value]
        while self._match_op(','): fns.append(self._adv_skip().value)
        result_var = None
        if self._match_kw('store'): self._match_kw('in'); result_var = self._adv_skip().value
        return {'type':'pipe','expr':expr,'fns':fns,'result':result_var,'line':line}

    # ─── async ─────────────────────────────────────────────────────────────────
    def _s_spawn(self, line):
        name = self._adv_skip().value; args = []
        if self._match_kw('with'):
            args.append(self._parse_expr())
            while self._match_op(','): args.append(self._parse_expr())
        return {'type':'spawn','name':name,'args':args,'line':line}

    def _s_after(self, line):
        delay = self._parse_expr(); self._match_kw('seconds','milliseconds','ms','second')
        unit = self.tokens[self.pos-1].value
        body = self._parse_block(); self._match_kw('end')
        return {'type':'after_delay','delay':delay,'unit':unit,'body':body,'line':line}

    def _s_every(self, line):
        interval = self._parse_expr(); self._match_kw('seconds','milliseconds','ms','second')
        body = self._parse_block(); self._match_kw('end')
        return {'type':'every_interval','interval':interval,'body':body,'line':line}

    def _s_benchmark(self, line):
        name = self._parse_expr(); body = self._parse_block(); self._match_kw('end')
        return {'type':'benchmark','name':name,'body':body,'line':line}

    def _s_memo(self, line):
        self._match_kw('function'); name_tok = self._adv_skip(); params = []
        if self._match_kw('with','takes'):
            while True:
                self._skip()
                if self.pos>=len(self.tokens): break
                t2 = self.tokens[self.pos]
                if t2.type in (ID,KW) and t2.value not in ('end',):
                    params.append(self._adv().value)
                    if not self._match_op(','): break
                else: break
        body = self._parse_block(); self._match_kw('end')
        return {'type':'memo_define','name':name_tok.value,'params':params,'body':body,'line':line}

    # ─── test framework ────────────────────────────────────────────────────────
    def _s_describe(self, line):
        name = self._parse_expr(); body = self._parse_block(); self._match_kw('end')
        return {'type':'describe_block','name':name,'body':body,'line':line}

    def _s_test(self, line):
        name = self._parse_expr(); body = self._parse_block(); self._match_kw('end')
        return {'type':'test_block','name':name,'body':body,'line':line}

    def _s_expect(self, line):
        expr = self._parse_expr(); self._match_kw('should','to')
        self._match_kw('be','equal','equal_to')
        self._match_kw('to')
        expected = self._parse_expr()
        return {'type':'expect_stmt','expr':expr,'expected':expected,'line':line}

    def _s_check(self, line):
        expr = self._parse_expr(); msg = None
        if self._match_kw('else','otherwise','with'): msg = self._parse_expr()
        return {'type':'check_stmt','expr':expr,'msg':msg,'line':line}

    # ─── pattern match ─────────────────────────────────────────────────────────
    def _s_match(self, line):
        """Advanced match / pattern matching block."""
        expr = self._parse_expr(); cases = []; default_body = []; guards = []
        self._skip()
        while True:
            self._skip()
            if self._at_end(): break
            t = self.tokens[self.pos]
            if t.type == KW and t.value == 'end': break

            # when VALUE [where GUARD] then BODY
            if self._match_kw('when','case','on'):
                # support '_' wildcard
                self._skip()
                if self.pos<len(self.tokens) and self.tokens[self.pos].value == '_':
                    self._adv(); val = {'type':'wildcard'}
                else:
                    val = self._parse_expr()
                guard = None
                if self._match_kw('where','if'):
                    guard = self._parse_expr()
                self._match_kw('then'); body = self._parse_block()
                cases.append({'value':val,'guard':guard,'body':body})
            elif self._match_kw('default','otherwise'):
                self._match_kw('then'); default_body = self._parse_block(); break
            else:
                self._adv()

        self._match_kw('end')
        return {'type':'match','expr':expr,'cases':cases,'default':default_body,'line':line}

    # ─── GUI extra ─────────────────────────────────────────────────────────────
    def _s_update_label(self, line):
        self._match_kw('label','button'); name_tok = self._adv_skip()
        self._match_kw('with','to'); expr = self._parse_expr()
        return {'type':'update_label','name':name_tok.value,'expr':expr,'line':line}

    def _s_get_entry(self, line):
        self._match_kw('entry','value')
        name_tok = self._adv_skip()
        self._match_kw('store','and'); self._match_kw('store'); self._match_kw('in')
        var = self._adv_skip().value
        return {'type':'read_entry','entry':name_tok.value,'var':var,'line':line}

    def _s_set_entry(self, line):
        self._consume_articles()
        name_tok = self._adv_skip()
        self._expect_kw('to')
        expr = self._parse_expr()
        return {'type':'set_entry','name':name_tok.value,'expr':expr,'line':line}

    def _s_alert(self, line):
        expr = self._parse_expr()
        return {'type':'gui_alert','expr':expr,'line':line}

    def _s_confirm(self, line):
        expr = self._parse_expr()
        self._match_kw('store'); self._match_kw('in'); var = self._adv_skip().value
        return {'type':'gui_confirm','expr':expr,'var':var,'line':line}

    def _s_hide(self, line):
        name_tok = self._adv_skip()
        return {'type':'gui_hide','name':name_tok.value,'line':line}

    def _s_toast(self, line):
        expr = self._parse_expr()
        return {'type':'gui_toast','expr':expr,'line':line}

    def _s_dialog(self, line):
        expr = self._parse_expr()
        self._match_kw('store'); self._match_kw('in'); var = self._adv_skip().value
        return {'type':'gui_dialog','expr':expr,'var':var,'line':line}

    def _s_bind_key(self, line):
        key = self._adv_skip().value
        self._match_kw('in'); self._match_kw('window'); win_tok = self._adv_skip()
        self._expect_kw('to')
        body = self._parse_block(); self._match_kw('end')
        return {'type':'bind_key','key':key,'window':win_tok.value,'body':body,'line':line}

    def _s_play_sound(self, line):
        file = self._parse_expr()
        return {'type':'play_sound','file':file,'line':line}

    def _s_fetch(self, line):
        url = self._parse_expr(); var = None
        if self._match_kw('store','and'):
            self._match_kw('store'); self._match_kw('in'); var = self._adv_skip().value
        return {'type':'fetch_url','url':url,'var':var,'line':line}

    def _s_host(self, line):
        # host "folder" on port 8080 as app
        folder = self._parse_expr()
        self._match_kw('on')
        self._match_kw('port')
        port = self._parse_expr()
        name = None
        if self._match_kw('as'):
            name = self._adv_skip().value
        return {'type':'host_static','folder':folder,'port':port,'name':name,'line':line}

    def _s_stop_server(self, line):
        name = self._adv_skip().value
        return {'type':'stop_server','name':name,'line':line}

    def _s_webview(self, line):
        # webview "url" in window "App"
        url = self._parse_expr()
        window = None
        if self._match_kw('in'):
            self._match_kw('window')
            window = self._adv_skip().value
        return {'type':'open_webview','url':url,'window':window,'line':line}

    def _s_fusion(self, line):
        # fusion "folder" as "Name" [on port 5000]
        folder = self._parse_expr()
        name = "Neglish Fusion App"
        if self._match_kw('as'):
            name = self._adv_skip().value
        
        port = None
        # Look for 'on port' as a specific sequence to avoid collision with 'on' event handlers
        if self._peek_kw('on'):
            # Look ahead to see if 'port' follows
            p_pos = self.pos + 1
            while p_pos < len(self.tokens) and self.tokens[p_pos].type == NL:
                p_pos += 1
            if p_pos < len(self.tokens) and self.tokens[p_pos].value == 'port':
                self._match_kw('on')
                self._match_kw('port')
                port = self._parse_expr()
        elif self._match_kw('port'):
            port = self._parse_expr()
            
        return {'type':'fusion', 'folder':folder, 'name':name, 'port':port, 'line':line}

    # ─── identifier fallback ───────────────────────────────────────────────────
    def _s_ident(self, name, line):
        # dotted call: obj.method with args
        if self._peek_op('.'):
            path = name
            while self._peek_op('.'):
                self._adv(); member = self._adv_skip(); path += '.' + member.value
            args = []
            if self._match_kw('with'):
                args.append(self._parse_expr())
                while self._match_op(','): args.append(self._parse_expr())
            return {'type':'call','name':path,'args':args,'line':line}
        # call with args
        if self._match_kw('with'):
            args = [self._parse_expr()]
            while self._match_op(','): args.append(self._parse_expr())
            return {'type':'call','name':name,'args':args,'line':line}
        # compound assign
        op = self._match_op('+=','-=','*=','/=')
        if op:
            expr = self._parse_expr()
            return {'type':'compound_assign','name':name,'op':op.value,'expr':expr,'line':line}
        return None

    def _recover_statement_boundary(self):
        while self.pos < len(self.tokens):
            t = self.tokens[self.pos]
            if t.type in (NL, EOF):
                if t.type == NL:
                    self.pos += 1
                break
            if t.type == KW and t.value in ('end', 'else', 'elseif', 'catch', 'default', 'when'):
                break
            self.pos += 1

    # ─── entry ─────────────────────────────────────────────────────────────────
    def parse(self):
        stmts = []
        while not self._at_end():
            try:
                s = self._parse_stmt()
                if s:
                    stmts.append(s)
            except ParseError as e:
                self.errors.append(str(e))
                if self.strict_mode:
                    raise
                self._recover_statement_boundary()
        return stmts
