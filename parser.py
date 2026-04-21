# parser.py — Neglish v2 Parser
# Converts token list → AST node list

from lexer import TT_KEYWORD, TT_STRING, TT_NUMBER, TT_IDENT, TT_OP, TT_NEWLINE, TT_EOF


class ParseError(Exception):
    def __init__(self, msg, line=0):
        super().__init__(f"[Line {line}] Parse Error: {msg}")


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos    = 0

    # ──────────────────────────────────────────── helpers
    def _skip_nl(self):
        while self.pos < len(self.tokens) and self.tokens[self.pos].type == TT_NEWLINE:
            self.pos += 1

    def _cur(self):
        self._skip_nl()
        return self.tokens[self.pos] if self.pos < len(self.tokens) else self.tokens[-1]

    def _adv(self):
        t = self.tokens[self.pos]
        self.pos += 1
        return t

    def _adv_skip(self):
        self._skip_nl()
        return self._adv()

    def _expect_kw(self, *kws):
        self._skip_nl()
        t = self._adv()
        if t.value not in kws:
            raise ParseError(f"Expected {kws}, got {t.value!r}", t.line)
        return t

    def _match_kw(self, *kws):
        self._skip_nl()
        if self.pos < len(self.tokens) and self.tokens[self.pos].type == TT_KEYWORD \
                and self.tokens[self.pos].value in kws:
            return self._adv()
        return None

    def _match_op(self, *ops):
        self._skip_nl()
        if self.pos < len(self.tokens) and self.tokens[self.pos].type == TT_OP \
                and self.tokens[self.pos].value in ops:
            return self._adv()
        return None

    def _at_end(self):
        self._skip_nl()
        return self.pos >= len(self.tokens) or self.tokens[self.pos].type == TT_EOF

    def _at_block_end(self):
        self._skip_nl()
        if self.pos >= len(self.tokens): return True
        t = self.tokens[self.pos]
        return t.type == TT_EOF or (
            t.type == TT_KEYWORD and
            t.value in ('end', 'else', 'elseif', 'elif', 'otherwise', 'also',
                        'catch', 'case', 'default')
        )

    def _peek_kw(self, *kws):
        self._skip_nl()
        if self.pos < len(self.tokens):
            t = self.tokens[self.pos]
            return t.type == TT_KEYWORD and t.value in kws
        return False

    # ──────────────────────────────────────────── expression
    def _parse_primary(self):
        self._skip_nl()
        t = self.tokens[self.pos]

        # unary not
        if t.type == TT_KEYWORD and t.value == 'not':
            self._adv()
            operand = self._parse_primary()
            return {'type': 'unary', 'op': 'not', 'operand': operand, 'line': t.line}

        # unary minus
        if t.type == TT_OP and t.value == '-':
            self._adv()
            operand = self._parse_primary()
            return {'type': 'unary', 'op': '-', 'operand': operand, 'line': t.line}

        # parenthesised expression
        if t.type == TT_OP and t.value == '(':
            self._adv()
            expr = self._parse_logic()
            self._match_op(')')
            return expr

        # list literal  [ a, b, c ]
        if t.type == TT_OP and t.value == '[':
            self._adv()
            items = []
            while not (self.tokens[self.pos].type == TT_OP and self.tokens[self.pos].value == ']'):
                items.append(self._parse_logic())
                self._match_op(',')
            self._adv()  # ]
            return {'type': 'list_literal', 'items': items, 'line': t.line}

        # dict literal  { key: val, ... }
        if t.type == TT_OP and t.value == '{':
            self._adv()
            pairs = []
            while not (self.tokens[self.pos].type == TT_OP and self.tokens[self.pos].value == '}'):
                k = self._parse_logic()
                self._match_op(':')
                v = self._parse_logic()
                pairs.append((k, v))
                self._match_op(',')
            self._adv()  # }
            return {'type': 'dict_literal', 'pairs': pairs, 'line': t.line}

        # item N of list  — only if next token is number/ident (not keyword like 'to')
        if t.type == TT_KEYWORD and t.value == 'item':
            # peek: if next real token is a number or non-block ident followed by 'of', parse as list access
            pos_save = self.pos
            self._adv()
            self._skip_nl()
            next_t = self.tokens[self.pos] if self.pos < len(self.tokens) else None
            # Only treat as list access if followed by number or ident then eventually 'of'
            if next_t and next_t.value not in ('to','in','from','and','or','end','then','with','by',','):
                idx = self._parse_primary()
                self._skip_nl()
                if self.pos < len(self.tokens) and self.tokens[self.pos].value == 'of':
                    self._adv()
                    name_tok = self._adv_skip()
                    return {'type': 'list_access', 'list': name_tok.value, 'index': idx, 'line': t.line}
                else:
                    # not a list access - treat 'item' as a variable
                    self.pos = pos_save
                    self._adv()
                    return {'type': 'var', 'name': 'item', 'line': t.line}
            else:
                # 'item' used as variable name
                return {'type': 'var', 'name': 'item', 'line': t.line}

        # length of x  /  type of x  (only when followed by 'of')
        if t.type == TT_KEYWORD and t.value in ('length', 'type'):
            peek_pos = self.pos + 1
            while peek_pos < len(self.tokens) and self.tokens[peek_pos].type == TT_NEWLINE:
                peek_pos += 1
            if peek_pos < len(self.tokens) and self.tokens[peek_pos].value == 'of':
                fn = 'length' if t.value == 'length' else 'type_of'
                self._adv(); self._match_kw('of')
                expr = self._parse_primary()
                return {'type': 'builtin_call', 'fn': fn, 'args': [expr], 'line': t.line}

        # math builtins:  sqrt of / abs of / floor of / ceil of / round of
        math_fns = (
            # math
            'sqrt','abs','floor','ceil','round','log10','log2',
            'sin','cos','tan','asin','acos','atan','degrees','radians',
            'sign','factorial','fibonacci','is_prime','is_even','is_odd',
            # string transforms
            'uppercase','lowercase','trim','trim_left','trim_right',
            'reverse','titlecase','camelcase','snakecase',
            'split_lines','uuid','hash_of',
            # list ops
            'first','last','sum','average','median','stdev','variance',
            'unique','flatten','flatten_deep','sort','sort_desc',
            'shuffle','count','compact',
            # type
            'to_bool','is_number','is_string','is_list','is_dict',
            'is_null','is_bool','to_list',
            # dict
            'dict_keys','dict_values','dict_size','dict_to_list',
            # time  
            'now','today','timestamp','time_ms','year','month','day',
            'hour','minute','second','weekday',
            # system
            'platform','username','hostname','pid','cwd','sep',
            # file
            'file_exists','is_file','is_dir','file_size','file_ext',
            'file_name','file_dir','list_dir','read_file',
            # misc
            'json_parse','json_stringify','json_pretty',
            'max_of','min_of',
        )
        if t.type == TT_KEYWORD and t.value in math_fns:
            # ONLY treat as builtin if the very next non-whitespace token is 'of'
            # otherwise let it fall through to be a variable name
            peek_pos = self.pos + 1
            while peek_pos < len(self.tokens) and self.tokens[peek_pos].type == TT_NEWLINE:
                peek_pos += 1
            if peek_pos < len(self.tokens) and self.tokens[peek_pos].value == 'of':
                fn = t.value
                self._adv()
                self._match_kw('of')
                arg = self._parse_primary()
                return {'type': 'builtin_call', 'fn': fn, 'args': [arg], 'line': t.line}
            # else fall through to treat as identifier

        # two-arg math builtins: 'gcd of A and B', 'lcm of A and B', 'max of A and B', 'min of A and B'
        two_arg_fns = ('gcd', 'lcm', 'max', 'min', 'power', 'clamp', 'lerp',
                       'contains_all', 'contains_any', 'intersection', 'difference', 'union',
                       'zip_pairs', 'dict_merge', 'path_join', 'number_format',
                       'index_of', 'pad_left', 'pad_right', 'repeat_str', 'count_of',
                       'replace_regex', 'find_all')
        if t.type == TT_KEYWORD and t.value in two_arg_fns:
            peek_pos = self.pos + 1
            while peek_pos < len(self.tokens) and self.tokens[peek_pos].type == TT_NEWLINE:
                peek_pos += 1
            if peek_pos < len(self.tokens) and self.tokens[peek_pos].value == 'of':
                fn = t.value
                self._adv()
                self._match_kw('of')
                a1 = self._parse_primary()
                self._match_kw('and', 'by', 'with')
                a2 = self._parse_primary()
                return {'type': 'builtin_call', 'fn': fn, 'args': [a1, a2], 'line': t.line}

        # IDENT-form builtins: when an identifier is followed by 'of' and is a known stdlib fn
        # e.g. is_prime of 97, fibonacci of 10, uuid of, etc.
        IDENT_BUILTINS_1ARG = {
            'is_prime','is_even','is_odd','factorial','fibonacci',
            'median','stdev','variance','max_of','min_of',
            'sort_desc','flatten_deep','compact','dict_keys','dict_values',
            'to_number','to_string','to_bool','to_list',
            'is_number','is_string','is_list','is_dict','is_null','is_bool',
            'split_lines','read_file','list_dir',
            'file_exists','is_file','is_dir','file_size','file_ext',
            'file_name','file_dir','env_get','json_parse','json_stringify','json_pretty',
            'sort_desc','flatten_deep','compact','max_of','min_of',
            'dict_keys','dict_values','dict_size','dict_to_list',
            'timestamp','time_ms',
        }
        IDENT_BUILTINS_0ARG = {'uuid','now','today','year','month','day',
                               'hour','minute','second','weekday','timestamp',
                               'time_ms','platform','username','hostname','pid','cwd','sep'}
        IDENT_BUILTINS_2ARG = {
            'gcd_fn':'gcd','lcm_fn':'lcm','index_of':'index_of',
            'pad_left':'pad_left','pad_right':'pad_right',
            'repeat_str':'repeat_str','count_of':'count_of',
            'contains_all':'contains_all','contains_any':'contains_any',
            'intersection':'intersection','difference':'difference',
            'union':'union','zip_pairs':'zip_pairs',
            'dict_merge':'dict_merge','number_format':'number_format',
            'pluralize':'pluralize','percent_of':'percent_of',
            'replace_regex':'replace_regex','find_all':'find_all',
        }
        if t.type == TT_IDENT:
            peek_pos = self.pos + 1
            while peek_pos < len(self.tokens) and self.tokens[peek_pos].type == TT_NEWLINE:
                peek_pos += 1
            if peek_pos < len(self.tokens) and self.tokens[peek_pos].value == 'of':
                fn_name = t.value
                if fn_name in IDENT_BUILTINS_0ARG:
                    self._adv(); self._match_kw('of')
                    # consume optional empty string arg
                    self._skip_nl()
                    if self.pos < len(self.tokens) and self.tokens[self.pos].type == TT_STRING:
                        self._adv()  # consume empty string
                    return {'type': 'builtin_call', 'fn': fn_name, 'args': [], 'line': t.line}
                if fn_name in IDENT_BUILTINS_1ARG:
                    self._adv(); self._match_kw('of')
                    arg = self._parse_primary()
                    return {'type': 'builtin_call', 'fn': fn_name, 'args': [arg], 'line': t.line}
                if fn_name in IDENT_BUILTINS_2ARG:
                    real_fn = IDENT_BUILTINS_2ARG[fn_name]
                    self._adv(); self._match_kw('of')
                    a1 = self._parse_primary()
                    self._match_kw('and','by','with')
                    a2 = self._parse_primary()
                    return {'type': 'builtin_call', 'fn': real_fn, 'args': [a1, a2], 'line': t.line}
                # check if it's any named builtin followed by 'of'
                # (e.g. user-defined fn names - don't intercept those)

        # random between a and b
        if t.type == TT_KEYWORD and t.value == 'random':
            self._adv()
            self._match_kw('between')
            lo = self._parse_primary()
            self._match_kw('and')
            hi = self._parse_primary()
            return {'type': 'builtin_call', 'fn': 'random_between', 'args': [lo, hi], 'line': t.line}

        # power of a by b
        if t.type == TT_KEYWORD and t.value == 'power':
            self._adv()
            self._match_kw('of')
            base = self._parse_primary()
            self._match_kw('by')
            exp  = self._parse_primary()
            return {'type': 'builtin_call', 'fn': 'power', 'args': [base, exp], 'line': t.line}

        # max of a and b  /  min of a and b
        if t.type == TT_KEYWORD and t.value in ('max', 'min'):
            fn = t.value
            self._adv()
            self._match_kw('of')
            a = self._parse_primary()
            self._match_kw('and')
            b = self._parse_primary()
            return {'type': 'builtin_call', 'fn': fn, 'args': [a, b], 'line': t.line}

        # number of x  /  string of x  (only when followed by 'of')
        if t.type == TT_KEYWORD and t.value in ('number', 'string'):
            peek_pos = self.pos + 1
            while peek_pos < len(self.tokens) and self.tokens[peek_pos].type == TT_NEWLINE:
                peek_pos += 1
            if peek_pos < len(self.tokens) and self.tokens[peek_pos].value == 'of':
                fn = t.value
                self._adv(); self._match_kw('of')
                arg = self._parse_primary()
                return {'type': 'builtin_call', 'fn': 'to_' + fn, 'args': [arg], 'line': t.line}

        # contains check:  x contains y  (parsed as infix — handled in parse_condition)
        # split x by y
        if t.type == TT_KEYWORD and t.value == 'split':
            self._adv()
            s = self._parse_primary()
            self._match_kw('by')
            sep = self._parse_primary()
            return {'type': 'builtin_call', 'fn': 'split', 'args': [s, sep], 'line': t.line}

        # join list with sep
        if t.type == TT_KEYWORD and t.value == 'join':
            self._adv()
            lst = self._parse_primary()
            self._match_kw('with')
            sep = self._parse_primary()
            return {'type': 'builtin_call', 'fn': 'join', 'args': [lst, sep], 'line': t.line}

        # substring of s from a to b
        if t.type == TT_KEYWORD and t.value == 'substring':
            self._adv()
            self._match_kw('of')
            s = self._parse_primary()
            self._match_kw('from')
            start = self._parse_primary()
            self._match_kw('to')
            end = self._parse_primary()
            return {'type': 'builtin_call', 'fn': 'substring', 'args': [s, start, end], 'line': t.line}

        # replace in s find x with y
        if t.type == TT_KEYWORD and t.value == 'replace':
            self._adv()
            self._match_kw('in')
            s = self._parse_primary()
            self._match_kw('find')
            find = self._parse_primary()
            self._match_kw('with')
            rep = self._parse_primary()
            return {'type': 'builtin_call', 'fn': 'replace', 'args': [s, find, rep], 'line': t.line}

        # index of x in list
        if t.type == TT_KEYWORD and t.value == 'index':
            self._adv()
            self._match_kw('of')
            val = self._parse_primary()
            self._match_kw('in')
            lst = self._parse_primary()
            return {'type': 'builtin_call', 'fn': 'index_of', 'args': [val, lst], 'line': t.line}

        # slice of list from a to b
        if t.type == TT_KEYWORD and t.value == 'slice':
            self._adv()
            self._match_kw('of')
            lst = self._parse_primary()
            self._match_kw('from')
            start = self._parse_primary()
            self._match_kw('to')
            end = self._parse_primary()
            return {'type': 'builtin_call', 'fn': 'slice', 'args': [lst, start, end], 'line': t.line}

        # time / date / now
        if t.type == TT_KEYWORD and t.value in ('now', 'today', 'time', 'date'):
            fn = t.value
            self._adv()
            return {'type': 'builtin_call', 'fn': fn, 'args': [], 'line': t.line}

        # pi constant
        if t.type == TT_KEYWORD and t.value == 'pi':
            self._adv()
            import math as _m
            return {'type': 'number', 'value': _m.pi, 'line': t.line}

        # format string:  format "template {}" with a, b
        if t.type == TT_KEYWORD and t.value == 'format':
            self._adv()
            template = self._parse_primary()
            self._match_kw('with')
            args = [self._parse_primary()]
            while self._match_op(','):
                args.append(self._parse_primary())
            return {'type': 'builtin_call', 'fn': 'format_str', 'args': [template] + args, 'line': t.line}

        # key "k" of dict
        if t.type == TT_KEYWORD and t.value == 'key':
            self._adv()
            k = self._parse_primary()
            self._expect_kw('of')
            d = self._adv_skip()
            return {'type': 'dict_access', 'dict': d.value, 'key': k, 'line': t.line}

        # keys of dict / values of dict
        if t.type == TT_KEYWORD and t.value in ('keys', 'values'):
            fn = t.value
            self._adv()
            self._match_kw('of')
            d = self._adv_skip()
            return {'type': 'builtin_call', 'fn': 'dict_' + fn, 'args': [{'type': 'var', 'name': d.value, 'line': d.line}], 'line': t.line}

        # call expression (inline, returns value)
        if t.type == TT_KEYWORD and t.value == 'call':
            self._adv()
            name_tok = self._adv_skip()
            name = name_tok.value
            # handle dotted: call mod.fn
            while self.pos < len(self.tokens) and self.tokens[self.pos].type == TT_OP and self.tokens[self.pos].value == '.':
                self._adv()
                member = self._adv_skip()
                name = name + '.' + member.value
            args = []
            if self._match_kw('with'):
                args.append(self._parse_logic())
                while self._match_op(','):
                    args.append(self._parse_logic())
            return {'type': 'call_expr', 'name': name, 'args': args, 'line': t.line}

        # input inline
        if t.type == TT_KEYWORD and t.value == 'input':
            self._adv()
            prompt = self._parse_primary()
            return {'type': 'builtin_call', 'fn': 'input_inline', 'args': [prompt], 'line': t.line}

        if t.type == TT_STRING:
            self._adv()
            return {'type': 'string', 'value': t.value, 'line': t.line}

        if t.type == TT_NUMBER:
            self._adv()
            return {'type': 'number', 'value': t.value, 'line': t.line}

        if t.type == TT_KEYWORD and t.value in ('true', 'false'):
            self._adv()
            return {'type': 'bool', 'value': t.value == 'true', 'line': t.line}

        if t.type == TT_KEYWORD and t.value in ('null', 'none'):
            self._adv()
            return {'type': 'null', 'line': t.line}

        if t.type in (TT_IDENT, TT_KEYWORD):
            # Do NOT consume block/control keywords as variable names
            # These raise an error if hit in expression context
            STOP_KEYWORDS = {'then','do','end','else','elseif','elif','otherwise','also',
                             'catch','case','default','where','store'}
            if t.type == TT_KEYWORD and t.value in STOP_KEYWORDS:
                raise ParseError(f"Unexpected keyword '{t.value}' in expression", t.line)
            self._adv()
            # check for dot-access: name.prop
            node = {'type': 'var', 'name': t.value, 'line': t.line}
            while self._match_op('.'):
                prop_tok = self._adv_skip()
                node = {'type': 'attr_access', 'obj': node, 'attr': prop_tok.value, 'line': t.line}
            # check for index: name[expr]
            while self.pos < len(self.tokens) and self.tokens[self.pos].type == TT_OP and self.tokens[self.pos].value == '[':
                self._adv()
                idx = self._parse_logic()
                self._match_op(']')
                node = {'type': 'index_access', 'obj': node, 'index': idx, 'line': t.line}
            return node

        raise ParseError(f"Unexpected token: {t.value!r}", t.line)

    def _parse_arith(self):
        left = self._parse_primary()
        while True:
            op = self._match_op('+', '-', '*', '/', '%', '**', '^')
            if op:
                right = self._parse_primary()
                left = {'type': 'binop', 'op': op.value, 'left': left, 'right': right, 'line': op.line}
            else:
                break
        return left

    def _parse_compare(self):
        left = self._parse_arith()
        self._skip_nl()

        if self._match_kw('is'):
            neg = self._match_kw('not')
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
                return {'type': 'builtin_call', 'fn': 'is_empty', 'args': [left], 'line': 0}
            elif self._match_kw('null', 'none'):
                op = '!=' if neg else '=='
                return {'type': 'compare', 'op': op, 'left': left,
                        'right': {'type': 'null'}, 'line': 0}
            elif self._match_kw('a', 'an'):
                type_tok = self._adv_skip()
                return {'type': 'type_check', 'expr': left, 'expected': type_tok.value, 'negate': bool(neg), 'line': 0}
            else:
                op = '!=' if neg else '=='
            right = self._parse_arith()
            return {'type': 'compare', 'op': op, 'left': left, 'right': right}

        # contains
        if self._match_kw('contains'):
            right = self._parse_arith()
            return {'type': 'builtin_call', 'fn': 'contains', 'args': [left, right], 'line': 0}

        # starts with / ends with
        if self._match_kw('starts'):
            self._match_kw('with')
            right = self._parse_arith()
            return {'type': 'builtin_call', 'fn': 'starts_with', 'args': [left, right], 'line': 0}
        if self._match_kw('ends'):
            self._match_kw('with')
            right = self._parse_arith()
            return {'type': 'builtin_call', 'fn': 'ends_with', 'args': [left, right], 'line': 0}

        op_tok = self._match_op('==', '!=', '>=', '<=', '>', '<')
        if op_tok:
            right = self._parse_arith()
            return {'type': 'compare', 'op': op_tok.value, 'left': left, 'right': right}

        return left

    def _parse_logic(self):
        left = self._parse_compare()
        while True:
            # Peek: 'and'/'or' only consumed as logic if NOT followed by 'store','in','then','do'
            self._skip_nl()
            if self.pos < len(self.tokens) and self.tokens[self.pos].type == TT_KEYWORD and self.tokens[self.pos].value in ('and','both'):
                # check next-next token
                nx = self.pos + 1
                while nx < len(self.tokens) and self.tokens[nx].type == TT_NEWLINE: nx += 1
                if nx < len(self.tokens) and self.tokens[nx].value in ('store','in','then','do','end'):
                    break  # 'and' belongs to ask/other construct
                self._adv(); self._skip_nl()
                right = self._parse_compare()
                left = {'type': 'logic', 'op': 'and', 'left': left, 'right': right}
            elif self.pos < len(self.tokens) and self.tokens[self.pos].type == TT_KEYWORD and self.tokens[self.pos].value in ('or','either'):
                self._adv(); self._skip_nl()
                right = self._parse_compare()
                left = {'type': 'logic', 'op': 'or', 'left': left, 'right': right}
            else:
                break
        return left

    def _parse_expr(self):
        return self._parse_logic()

    # ──────────────────────────────────────────── block
    def _parse_block(self):
        stmts = []
        while not self._at_block_end() and not self._at_end():
            s = self._parse_stmt()
            if s: stmts.append(s)
        return stmts

    # ──────────────────────────────────────────── statements
    def _parse_stmt(self):
        self._skip_nl()
        if self._at_end(): return None

        t = self.tokens[self.pos]

        if t.type == TT_NEWLINE:
            self._adv(); return None

        if t.type == TT_KEYWORD and t.value == 'end':
            self._adv(); return None

        if t.type == TT_KEYWORD:
            kw = t.value
            self._adv()
            dispatch = {
                'show': self._ps_show, 'say': self._ps_show, 'print': self._ps_show,
                'log': self._ps_show,
                'set': self._ps_set,
                'let': self._ps_set,
                'const': self._ps_set,
                'increase': self._ps_increase,
                'decrease': self._ps_decrease,
                'if': self._ps_if,
                'repeat': self._ps_repeat,
                'while': self._ps_while,
                'for': self._ps_for,
                'loop': self._ps_forever,
                'forever': self._ps_forever,
                'define': self._ps_define,
                'call': self._ps_call,
                'return': self._ps_return,
                'break': lambda ln: {'type': 'break', 'line': ln},
                'continue': lambda ln: {'type': 'continue', 'line': ln},
                'ask': self._ps_ask,
                'input': self._ps_ask_kw,
                'create': self._ps_create,
                'when': self._ps_when,
                'add': self._ps_add,
                'remove': self._ps_remove,
                'insert': self._ps_insert,
                'pop': self._ps_pop,
                'sort': self._ps_sort_stmt,
                'shuffle': self._ps_shuffle_stmt,
                'open': self._ps_file_open,
                'write': self._ps_file_write,
                'append': self._ps_file_append,
                'close': self._ps_file_close,
                'read': self._ps_file_read,
                'delete': self._ps_delete,
                'try': self._ps_try,
                'throw': self._ps_throw,
                'raise': self._ps_throw,
                'import': self._ps_import,
                'use': self._ps_import,
                'sleep': self._ps_sleep,
                'wait': self._ps_sleep,
                'pause': self._ps_sleep,
                'exit': lambda ln: {'type': 'exit', 'line': ln},
                'quit': lambda ln: {'type': 'exit', 'line': ln},
                'clear': lambda ln: {'type': 'clear', 'line': ln},
                'debug': self._ps_debug,
                'inspect': self._ps_inspect,
                'assert': self._ps_assert,
                'switch': self._ps_switch,
                'match': self._ps_switch,
                'emit': self._ps_emit,
                'on': self._ps_on,
                'set_key': self._ps_set_key,
                'global': self._ps_global,
                'colored': self._ps_colored_show,
                'show_window': lambda ln: {'type': 'show_window', 'name': '', 'line': ln},
                'hide': self._ps_hide,
                'alert': self._ps_alert,
                'confirm': self._ps_confirm,
                'run': self._ps_run_cmd,
                'save': self._ps_json_save,
                'load': self._ps_json_load,
                'fetch': self._ps_fetch,
                'filter': self._ps_pipe_filter,
                'map_fn': self._ps_pipe_map,
                'reduce': self._ps_pipe_reduce,
                'collect': self._ps_collect,
                'pipe': self._ps_pipe,
                'test': self._ps_test,
                'describe': self._ps_describe,
                'expect': self._ps_expect,
                'check': self._ps_check,
                'watch': self._ps_watch,
                'once': self._ps_once,
                'async': self._ps_async_def,
                'spawn': self._ps_spawn,
                'after': self._ps_after,
                'every': self._ps_every,
                'freeze': self._ps_freeze,
                'benchmark': self._ps_benchmark,
                'export': self._ps_export,
                'package': self._ps_package,
                'memo': self._ps_memo,
                'class': self._ps_class,
                'new': self._ps_new,
                'update': self._ps_update,
                'get': self._ps_get_entry_stmt,
            }
            if kw in dispatch:
                return dispatch[kw](t.line)

            # fallback: treat as ident
            return self._ps_ident_stmt(kw, t.line)

        if t.type == TT_IDENT:
            name = t.value
            self._adv()
            # compound assignment: name += / -= / *= / /=
            op = self._match_op('+=', '-=', '*=', '/=', '=')
            if op:
                expr = self._parse_expr()
                return {'type': 'compound_assign', 'name': name, 'op': op.value, 'expr': expr, 'line': t.line}
            # dict key set: name[key] = expr
            if self._match_op('['):
                key = self._parse_expr()
                self._match_op(']')
                self._match_op('=')
                val = self._parse_expr()
                return {'type': 'index_assign', 'name': name, 'key': key, 'value': val, 'line': t.line}
            return self._ps_ident_stmt(name, t.line)

        self._adv()
        return None

    # ──────────────────────────────────────────── individual parsers
    def _ps_show(self, line):
        parts = [self._parse_expr()]
        while self._match_op(','):
            parts.append(self._parse_expr())
        return {'type': 'show', 'parts': parts, 'line': line}

    def _ps_set(self, line):
        from lexer import TT_KEYWORD, TT_IDENT, TT_OP
        # handle: set key "k" of dict to val
        if self._match_kw('key'):
            k = self._parse_primary()
            self._expect_kw('of')
            d = self._adv_skip().value
            self._expect_kw('to')
            v = self._parse_expr()
            return {"type": "dict_set", "dict": d, "key": k, "value": v, "line": line}
        name_tok = self._adv_skip()
        name = name_tok.value
        # handle dot-property: set obj.prop to val
        self._skip_nl()
        if self.pos < len(self.tokens) and self.tokens[self.pos].type == TT_OP and self.tokens[self.pos].value == '.':
            self._adv()  # consume dot
            prop_tok = self._adv_skip()
            self._expect_kw('to')
            v = self._parse_expr()
            return {'type': 'obj_prop_set', 'obj': name, 'prop': prop_tok.value, 'expr': v, 'line': line}
        self._expect_kw('to')
        expr = self._parse_expr()
        return {'type': 'set', 'name': name, 'expr': expr, 'line': line}

    def _ps_increase(self, line):
        name_tok = self._adv_skip()
        self._expect_kw('by')
        expr = self._parse_expr()
        return {'type': 'increase', 'name': name_tok.value, 'expr': expr, 'line': line}

    def _ps_decrease(self, line):
        name_tok = self._adv_skip()
        self._expect_kw('by')
        expr = self._parse_expr()
        return {'type': 'decrease', 'name': name_tok.value, 'expr': expr, 'line': line}

    def _ps_if(self, line):
        cond = self._parse_expr()
        self._match_kw('then')
        body = self._parse_block()
        elseif_branches = []
        else_body = []

        while True:
            self._skip_nl()
            if self.pos >= len(self.tokens): break
            t = self.tokens[self.pos]
            if t.type == TT_KEYWORD and t.value in ('elseif', 'elif'):
                self._adv()
                ec = self._parse_expr()
                self._match_kw('then')
                eb = self._parse_block()
                elseif_branches.append({'cond': ec, 'body': eb})
            elif t.type == TT_KEYWORD and t.value in ('else', 'otherwise', 'also'):
                self._adv()
                else_body = self._parse_block()
                break
            else:
                break

        self._match_kw('end')
        return {'type': 'if', 'cond': cond, 'body': body,
                'elseif': elseif_branches, 'else': else_body, 'line': line}

    def _ps_repeat(self, line):
        count = self._parse_expr()
        self._match_kw('times')
        # optional loop variable: repeat 5 times as i
        var = None
        if self._match_kw('as'):
            var = self._adv_skip().value
        body = self._parse_block()
        self._match_kw('end')
        return {'type': 'repeat', 'count': count, 'var': var, 'body': body, 'line': line}

    def _ps_while(self, line):
        cond = self._parse_expr()
        self._match_kw('do')
        body = self._parse_block()
        self._match_kw('end')
        return {'type': 'while', 'cond': cond, 'body': body, 'line': line}

    def _ps_for(self, line):
        # for each item in list  OR  for i from 1 to 10  OR  for i from 1 to 10 step 2
        if self._match_kw('each'):
            var_tok = self._adv_skip()
            self._expect_kw('in')
            lst = self._parse_expr()
            body = self._parse_block()
            self._match_kw('end')
            return {'type': 'for_each', 'var': var_tok.value, 'list': lst, 'body': body, 'line': line}
        else:
            var_tok = self._adv_skip()
            self._expect_kw('from')
            start = self._parse_expr()
            self._expect_kw('to')
            end = self._parse_expr()
            step = None
            if self._match_kw('step'):
                step = self._parse_expr()
            body = self._parse_block()
            self._match_kw('end')
            return {'type': 'for_range', 'var': var_tok.value, 'start': start, 'end': end,
                    'step': step, 'body': body, 'line': line}

    def _ps_forever(self, line):
        body = self._parse_block()
        self._match_kw('end')
        return {'type': 'forever', 'body': body, 'line': line}

    def _ps_define(self, line):
        self._match_kw('function')
        name_tok = self._adv_skip()
        params = []
        if self._match_kw('with'):
            while True:
                self._skip_nl()
                t = self.tokens[self.pos]
                if t.type in (TT_IDENT, TT_KEYWORD) and t.value not in ('end',):
                    params.append(self._adv().value)
                    if not self._match_op(','):
                        break
                else:
                    break
        body = self._parse_block()
        self._match_kw('end')
        return {'type': 'define', 'name': name_tok.value, 'params': params, 'body': body, 'line': line}

    def _ps_call(self, line):
        from lexer import TT_OP
        name_tok = self._adv_skip()
        name = name_tok.value
        # handle dotted call: call module.fn  or  call obj.method
        self._skip_nl()
        while self.pos < len(self.tokens) and self.tokens[self.pos].type == TT_OP and self.tokens[self.pos].value == '.':
            self._adv()  # dot
            member = self._adv_skip()
            name = name + '.' + member.value
        args = []
        if self._match_kw('with'):
            args.append(self._parse_expr())
            while self._match_op(','):
                args.append(self._parse_expr())
        return {'type': 'call', 'name': name, 'args': args, 'line': line}

    def _ps_return(self, line):
        self._skip_nl()
        t = self.tokens[self.pos]
        if t.type in (TT_NEWLINE, TT_EOF):
            return {'type': 'return', 'expr': None, 'line': line}
        expr = self._parse_expr()
        return {'type': 'return', 'expr': expr, 'line': line}

    def _ps_ask(self, line):
        prompt = self._parse_expr()
        self._match_kw('and')
        self._expect_kw('store')
        self._expect_kw('in')
        name_tok = self._adv_skip()
        return {'type': 'ask', 'prompt': prompt, 'var': name_tok.value, 'line': line}

    def _ps_ask_kw(self, line):
        # input store in name
        self._match_kw('store'); self._match_kw('in')
        name_tok = self._adv_skip()
        return {'type': 'ask', 'prompt': {'type': 'string', 'value': '', 'line': line},
                'var': name_tok.value, 'line': line}

    def _ps_create(self, line):
        self._skip_nl()
        t = self.tokens[self.pos]
        if t.type == TT_KEYWORD and t.value == 'window':
            self._adv()
            title_tok = self._adv_skip()
            w, h = 800, 600
            if self._match_kw('with'):
                if self._match_kw('width'):  w = self._parse_expr()
                if self._match_kw('height'): h = self._parse_expr()
            return {'type': 'create_window', 'title': title_tok.value, 'width': w, 'height': h, 'line': line}

        if t.type == TT_KEYWORD and t.value == 'button':
            self._adv()
            label_tok = self._adv_skip()
            self._match_kw('in'); self._match_kw('window')
            win_tok = self._adv_skip()
            opts = {}
            if self._match_kw('with'):
                opts = self._parse_opts()
            return {'type': 'create_button', 'label': label_tok.value, 'window': win_tok.value,
                    'opts': opts, 'line': line}

        if t.type == TT_KEYWORD and t.value == 'label':
            self._adv()
            text_expr = self._parse_expr()
            self._match_kw('in'); self._match_kw('window')
            win_tok = self._adv_skip()
            opts = {}
            if self._match_kw('with'):
                opts = self._parse_opts()
            return {'type': 'create_label', 'text': text_expr, 'window': win_tok.value,
                    'opts': opts, 'line': line}

        if t.type == TT_KEYWORD and t.value in ('entry', 'textbox'):
            self._adv()
            name_tok = self._adv_skip()
            self._match_kw('in'); self._match_kw('window')
            win_tok = self._adv_skip()
            return {'type': 'create_entry', 'name': name_tok.value, 'window': win_tok.value, 'line': line}

        if t.type == TT_KEYWORD and t.value == 'list':
            self._adv()
            name_tok = self._adv_skip()
            items = []
            if self._match_kw('with'):
                # Only parse items if next token is NOT a newline or block keyword
                pos_before = self.pos
                raw_pos = self.pos
                # peek without skipping newlines
                while raw_pos < len(self.tokens) and self.tokens[raw_pos].type == TT_NEWLINE:
                    raw_pos += 1
                # if no more tokens on same logical line, it's an empty list
                has_items = (raw_pos < len(self.tokens) and
                    self.tokens[raw_pos].type not in ('EOF',) and
                    self.tokens[raw_pos].value not in (
                        'end','else','elseif','for','while','if','repeat',
                        'define','call','show','set','increase','decrease',
                        'create','add','remove','return','export','colored',
                        'benchmark','describe','test','try','switch','class',
                        'loop','forever','after','every','spawn','sleep',
                        'open','write','close','emit','on','import'))
                if has_items:
                    items.append(self._parse_expr())
                    while self._match_op(','):
                        items.append(self._parse_expr())
            return {'type': 'create_list', 'name': name_tok.value, 'items': items, 'line': line}

        if t.type == TT_KEYWORD and t.value in ('map', 'dict'):
            self._adv()
            name_tok = self._adv_skip()
            pairs = []
            if self._match_kw('with'):
                k = self._parse_expr()
                self._match_op(':'); self._match_kw('as')
                v = self._parse_expr()
                pairs.append((k, v))
                while self._match_op(','):
                    k = self._parse_expr()
                    self._match_op(':'); self._match_kw('as')
                    v = self._parse_expr()
                    pairs.append((k, v))
            return {'type': 'create_dict', 'name': name_tok.value, 'pairs': pairs, 'line': line}

        if t.type == TT_KEYWORD and t.value == 'progress':
            self._adv()
            name_tok = self._adv_skip()
            self._match_kw('in'); self._match_kw('window')
            win_tok = self._adv_skip()
            return {'type': 'create_progress', 'name': name_tok.value, 'window': win_tok.value, 'line': line}

        self._adv()
        return None

    def _parse_opts(self):
        opts = {}
        known = ('color', 'background', 'foreground', 'font', 'size', 'width', 'height',
                 'bold', 'italic', 'x', 'y', 'row', 'column')
        while True:
            self._skip_nl()
            t = self.tokens[self.pos]
            if t.type == TT_KEYWORD and t.value in known:
                key = t.value
                self._adv()
                val = self._parse_primary()
                opts[key] = val
            else:
                break
        return opts

    def _ps_when(self, line):
        self._match_kw('button')
        label_tok = self._adv_skip()
        self._expect_kw('is')
        self._match_kw('clicked', 'pressed', 'submitted')
        body = self._parse_block()
        self._match_kw('end')
        return {'type': 'when_clicked', 'label': label_tok.value, 'body': body, 'line': line}

    def _ps_add(self, line):
        val = self._parse_expr()
        self._expect_kw('to')
        name_tok = self._adv_skip()
        return {'type': 'list_add', 'list': name_tok.value, 'value': val, 'line': line}

    def _ps_remove(self, line):
        val = self._parse_expr()
        self._expect_kw('from')
        name_tok = self._adv_skip()
        return {'type': 'list_remove', 'list': name_tok.value, 'value': val, 'line': line}

    def _ps_insert(self, line):
        val = self._parse_expr()
        self._expect_kw('at')
        idx = self._parse_expr()
        self._expect_kw('in')
        name_tok = self._adv_skip()
        return {'type': 'list_insert', 'list': name_tok.value, 'value': val, 'index': idx, 'line': line}

    def _ps_pop(self, line):
        self._match_kw('from')
        name_tok = self._adv_skip()
        var = None
        if self._match_kw('store', 'and'):
            self._match_kw('store'); self._match_kw('in')
            var = self._adv_skip().value
        return {'type': 'list_pop', 'list': name_tok.value, 'var': var, 'line': line}

    def _ps_sort_stmt(self, line):
        name_tok = self._adv_skip()
        return {'type': 'list_sort', 'list': name_tok.value, 'line': line}

    def _ps_shuffle_stmt(self, line):
        name_tok = self._adv_skip()
        return {'type': 'list_shuffle', 'list': name_tok.value, 'line': line}

    def _ps_file_open(self, line):
        path = self._parse_expr()
        self._match_kw('as')
        name_tok = self._adv_skip()
        mode = 'r'
        # Peek ahead WITHOUT skipping newlines to find 'for' on the same line
        from lexer import TT_NEWLINE, TT_KEYWORD
        p = self.pos
        while p < len(self.tokens) and self.tokens[p].type not in (TT_NEWLINE,) and self.tokens[p].value != 'for':
            if self.tokens[p].type == TT_NEWLINE:
                break
            p += 1
        if p < len(self.tokens) and self.tokens[p].value == 'for':
            # Check next token is a mode word
            q = p + 1
            if q < len(self.tokens) and self.tokens[q].value in ('write', 'read', 'append'):
                self.pos = p + 2  # consume 'for' and mode
                mode = {'write': 'w', 'read': 'r', 'append': 'a'}[self.tokens[q].value]
        return {'type': 'file_open', 'path': path, 'name': name_tok.value, 'mode': mode, 'line': line}

    def _ps_file_write(self, line):
        expr = self._parse_expr()
        self._expect_kw('to')
        name_tok = self._adv_skip()
        return {'type': 'file_write', 'file': name_tok.value, 'expr': expr, 'line': line}

    def _ps_file_append(self, line):
        expr = self._parse_expr()
        self._expect_kw('to')
        name_tok = self._adv_skip()
        return {'type': 'file_append', 'file': name_tok.value, 'expr': expr, 'line': line}

    def _ps_file_close(self, line):
        name_tok = self._adv_skip()
        return {'type': 'file_close', 'file': name_tok.value, 'line': line}

    def _ps_file_read(self, line):
        name_tok = self._adv_skip()
        self._match_kw('store', 'and')
        self._match_kw('store'); self._match_kw('in')
        var = self._adv_skip().value
        return {'type': 'file_read', 'file': name_tok.value, 'var': var, 'line': line}

    def _ps_delete(self, line):
        # delete file "path"  OR  delete variable name
        if self._match_kw('file'):
            path = self._parse_expr()
            return {'type': 'file_delete', 'path': path, 'line': line}
        name_tok = self._adv_skip()
        return {'type': 'delete_var', 'name': name_tok.value, 'line': line}

    def _ps_try(self, line):
        body = self._parse_block()
        catch_var = None
        catch_body = []
        if self._match_kw('catch'):
            self._match_kw('error')
            if self._match_kw('as'):
                catch_var = self._adv_skip().value
            catch_body = self._parse_block()
        self._match_kw('end')
        return {'type': 'try', 'body': body, 'catch_var': catch_var, 'catch': catch_body, 'line': line}

    def _ps_throw(self, line):
        expr = self._parse_expr()
        return {'type': 'throw', 'expr': expr, 'line': line}

    def _ps_import(self, line):
        name_tok = self._adv_skip()
        alias = name_tok.value
        if self._match_kw('as'):
            alias = self._adv_skip().value
        return {'type': 'import', 'module': name_tok.value, 'alias': alias, 'line': line}

    def _ps_sleep(self, line):
        dur = self._parse_expr()
        unit = 'seconds'
        if self._match_kw('seconds', 'milliseconds', 'ms'):
            unit = self.tokens[self.pos - 1].value
        return {'type': 'sleep', 'duration': dur, 'unit': unit, 'line': line}

    def _ps_debug(self, line):
        expr = self._parse_expr()
        return {'type': 'debug', 'expr': expr, 'line': line}

    def _ps_inspect(self, line):
        name_tok = self._adv_skip()
        return {'type': 'inspect', 'name': name_tok.value, 'line': line}

    def _ps_assert(self, line):
        cond = self._parse_expr()
        msg = None
        if self._match_kw('else', 'otherwise', 'with'):
            msg = self._parse_expr()
        return {'type': 'assert', 'cond': cond, 'msg': msg, 'line': line}

    def _ps_switch(self, line):
        expr = self._parse_expr()
        cases = []
        default_body = []
        self._skip_nl()
        while True:
            self._skip_nl()
            if self.tokens[self.pos].value == 'end': break
            if self._match_kw('case', 'when'):
                val = self._parse_expr()
                self._match_op(':'); self._match_kw('then')
                body = self._parse_block()
                cases.append({'value': val, 'body': body})
            elif self._match_kw('default', 'otherwise'):
                self._match_op(':'); self._match_kw('then')
                default_body = self._parse_block()
                break
            else:
                break
        self._match_kw('end')
        return {'type': 'switch', 'expr': expr, 'cases': cases, 'default': default_body, 'line': line}

    def _ps_emit(self, line):
        event_tok = self._adv_skip()
        data = None
        if self._match_kw('with'):
            data = self._parse_expr()
        return {'type': 'emit', 'event': event_tok.value, 'data': data, 'line': line}

    def _ps_on(self, line):
        event_tok = self._adv_skip()
        body = self._parse_block()
        self._match_kw('end')
        return {'type': 'on_event', 'event': event_tok.value, 'body': body, 'line': line}

    def _ps_set_key(self, line):
        # set key "k" of dict to val
        k = self._parse_expr()
        self._expect_kw('of')
        d = self._adv_skip().value
        self._expect_kw('to')
        v = self._parse_expr()
        return {'type': 'dict_set', 'dict': d, 'key': k, 'value': v, 'line': line}

    def _ps_global(self, line):
        name_tok = self._adv_skip()
        return {'type': 'global_decl', 'name': name_tok.value, 'line': line}

    def _ps_colored_show(self, line):
        color_tok = self._adv_skip()
        expr = self._parse_expr()
        return {'type': 'colored_show', 'color': color_tok.value, 'expr': expr, 'line': line}

    def _ps_hide(self, line):
        widget_tok = self._adv_skip()
        return {'type': 'gui_hide', 'name': widget_tok.value, 'line': line}

    def _ps_alert(self, line):
        expr = self._parse_expr()
        return {'type': 'gui_alert', 'expr': expr, 'line': line}

    def _ps_confirm(self, line):
        expr = self._parse_expr()
        self._match_kw('store'); self._match_kw('in')
        var = self._adv_skip().value
        return {'type': 'gui_confirm', 'expr': expr, 'var': var, 'line': line}

    def _ps_run_cmd(self, line):
        expr = self._parse_expr()
        var = None
        if self._match_kw('store', 'and'):
            self._match_kw('store'); self._match_kw('in')
            var = self._adv_skip().value
        return {'type': 'run_cmd', 'expr': expr, 'var': var, 'line': line}

    def _ps_json_save(self, line):
        name_tok = self._adv_skip()
        self._expect_kw('to')
        path = self._parse_expr()
        return {'type': 'json_save', 'name': name_tok.value, 'path': path, 'line': line}

    def _ps_json_load(self, line):
        path = self._parse_expr()
        self._expect_kw('in')
        name_tok = self._adv_skip()
        return {'type': 'json_load', 'path': path, 'name': name_tok.value, 'line': line}

    def _ps_fetch(self, line):
        url = self._parse_expr()
        var = None
        if self._match_kw('store', 'and'):
            self._match_kw('store'); self._match_kw('in')
            var = self._adv_skip().value
        return {'type': 'fetch_url', 'url': url, 'var': var, 'line': line}

    def _ps_update(self, line):
        # update label NAME with EXPR
        if self._match_kw('label'):
            name_tok = self._adv_skip()
            self._match_kw('with')
            expr = self._parse_expr()
            return {'type': 'update_label', 'name': name_tok.value, 'expr': expr, 'line': line}
        return None

    def _ps_get_entry_stmt(self, line):
        # get entry NAME store in VAR
        if self._match_kw('entry'):
            name_tok = self._adv_skip()
            self._match_kw('store')
            self._match_kw('in')
            var_tok = self._adv_skip()
            return {'type': 'read_entry', 'entry': name_tok.value, 'var': var_tok.value, 'line': line}
        return None


    # ─── pipe / functional ───────────────────────────────────────────────
    def _ps_pipe_filter(self, line):
        # filter LISTVAR where VAR comparator EXPR as RESULT
        lst = self._parse_expr()
        self._match_kw('where')
        var_tok = self._adv_skip()
        left_node = {'type': 'var', 'name': var_tok.value, 'line': var_tok.line}
        cond = self._parse_compare_with_left(left_node)
        result_var = None
        if self._match_kw('as'): result_var = self._adv_skip().value
        return {'type':'pipe_filter','list':lst,'var':var_tok.value,'cond':cond,'result':result_var,'line':line}

    def _ps_pipe_map(self, line):
        # map_fn LISTVAR with VAR as EXPR store in RESULT
        lst = self._parse_expr()
        self._match_kw('with')
        var_tok = self._adv_skip()
        self._match_kw('as')
        transform = self._parse_expr()
        result_var = None
        if self._match_kw('store'): self._match_kw('in'); result_var = self._adv_skip().value
        return {'type':'pipe_map','list':lst,'var':var_tok.value,'transform':transform,'result':result_var,'line':line}

    def _ps_pipe_reduce(self, line):
        # reduce LIST with INIT using ITEM as ACCUMULATOR_EXPR store in RESULT
        # e.g.: reduce nums with 0 using n as acc + n store in total
        lst = self._parse_expr()
        self._match_kw('with','starting')
        start = self._parse_expr()
        self._match_kw('using')
        var_tok = self._adv_skip()   # loop variable (e.g. n)
        self._match_kw('as')
        op_expr = self._parse_expr()  # accumulator expression using acc and var
        result_var = None
        if self._match_kw('store'): self._match_kw('in'); result_var = self._adv_skip().value
        elif self._match_kw('as'): result_var = self._adv_skip().value
        return {'type':'pipe_reduce','list':lst,'start':start,'var':var_tok.value,'op_expr':op_expr,'result':result_var,'line':line}

    def _ps_collect(self, line):
        # collect VAR from LIST where COND as RESULT
        var_tok = self._adv_skip()
        self._match_kw('from')
        lst = self._parse_expr()
        cond = None
        if self._match_kw('where'): cond = self._parse_expr()
        result_var = None
        if self._match_kw('as','store'):
            self._match_kw('in')
            result_var = self._adv_skip().value
        return {'type':'collect','var':var_tok.value,'list':lst,'cond':cond,'result':result_var,'line':line}

    def _ps_pipe(self, line):
        # pipe EXPR through FUNC1, FUNC2, ... store in RESULT
        expr = self._parse_expr()
        self._expect_kw('through')
        fns = [self._adv_skip().value]
        while self._match_op(','): fns.append(self._adv_skip().value)
        result_var = None
        if self._match_kw('store'): self._match_kw('in'); result_var = self._adv_skip().value
        return {'type':'pipe','expr':expr,'fns':fns,'result':result_var,'line':line}

    # ─── testing framework ───────────────────────────────────────────────
    def _ps_test(self, line):
        name = self._parse_expr()
        body = self._parse_block()
        self._match_kw('end')
        return {'type':'test_block','name':name,'body':body,'line':line}

    def _ps_describe(self, line):
        name = self._parse_expr()
        body = self._parse_block()
        self._match_kw('end')
        return {'type':'describe_block','name':name,'body':body,'line':line}

    def _ps_expect(self, line):
        expr = self._parse_expr()
        self._match_kw('should','to')
        self._match_kw('be','equal')
        self._match_kw('to','equal_to')
        expected = self._parse_expr()
        return {'type':'expect_stmt','expr':expr,'expected':expected,'line':line}

    def _ps_check(self, line):
        expr = self._parse_expr()
        msg = None
        if self._match_kw('else','otherwise','with'): msg = self._parse_expr()
        return {'type':'check_stmt','expr':expr,'msg':msg,'line':line}

    # ─── observer / reactivity ────────────────────────────────────────────
    def _ps_watch(self, line):
        name_tok = self._adv_skip()
        body = self._parse_block()
        self._match_kw('end')
        return {'type':'watch','name':name_tok.value,'body':body,'line':line}

    def _ps_once(self, line):
        name_tok = self._adv_skip()
        return {'type':'once_decl','name':name_tok.value,'line':line}

    # ─── async / concurrency ─────────────────────────────────────────────
    def _ps_async_def(self, line):
        self._match_kw('function')
        name_tok = self._adv_skip()
        params = []
        if self._match_kw('with'):
            while True:
                t = self.tokens[self.pos]
                if t.type in ('IDENT','KEYWORD') and t.value not in ('end',):
                    params.append(self._adv().value)
                    if not self._match_op(','): break
                else: break
        body = self._parse_block()
        self._match_kw('end')
        return {'type':'async_define','name':name_tok.value,'params':params,'body':body,'line':line}

    def _ps_spawn(self, line):
        name = self._adv_skip().value
        args = []
        if self._match_kw('with'):
            args.append(self._parse_expr())
            while self._match_op(','): args.append(self._parse_expr())
        return {'type':'spawn','name':name,'args':args,'line':line}

    def _ps_after(self, line):
        delay = self._parse_expr()
        self._match_kw('seconds','milliseconds','ms')
        body = self._parse_block()
        self._match_kw('end')
        return {'type':'after_delay','delay':delay,'body':body,'line':line}

    def _ps_every(self, line):
        interval = self._parse_expr()
        self._match_kw('seconds','milliseconds','ms')
        body = self._parse_block()
        self._match_kw('end')
        return {'type':'every_interval','interval':interval,'body':body,'line':line}

    # ─── freeze / const ────────────────────────────────────────────────
    def _ps_freeze(self, line):
        name_tok = self._adv_skip()
        return {'type':'freeze','name':name_tok.value,'line':line}

    # ─── benchmark ─────────────────────────────────────────────────────
    def _ps_benchmark(self, line):
        name = self._parse_expr()
        body = self._parse_block()
        self._match_kw('end')
        return {'type':'benchmark','name':name,'body':body,'line':line}

    # ─── module system ─────────────────────────────────────────────────
    def _ps_export(self, line):
        name_tok = self._adv_skip()
        return {'type':'export','name':name_tok.value,'line':line}

    def _ps_package(self, line):
        name_tok = self._adv_skip()
        return {'type':'package_decl','name':name_tok.value,'line':line}

    def _ps_memo(self, line):
        self._match_kw('function')
        name_tok = self._adv_skip()
        params = []
        if self._match_kw('with'):
            while True:
                t = self.tokens[self.pos]
                if t.type in ('IDENT','KEYWORD') and t.value not in ('end',):
                    params.append(self._adv().value)
                    if not self._match_op(','): break
                else: break
        body = self._parse_block()
        self._match_kw('end')
        return {'type':'memo_define','name':name_tok.value,'params':params,'body':body,'line':line}

    # ─── OOP lite ──────────────────────────────────────────────────────
    def _ps_class(self, line):
        name_tok = self._adv_skip()
        parent = None
        if self._match_kw('inherit','extend','extends'): parent = self._adv_skip().value
        body = self._parse_block()
        self._match_kw('end')
        return {'type':'class_def','name':name_tok.value,'parent':parent,'body':body,'line':line}

    def _ps_new(self, line):
        class_tok = self._adv_skip()
        args = []
        if self._match_kw('with'):
            args.append(self._parse_expr())
            while self._match_op(','): args.append(self._parse_expr())
        result_var = None
        if self._match_kw('as','store'):
            self._match_kw('in')
            result_var = self._adv_skip().value
        return {'type':'new_obj','class':class_tok.value,'args':args,'result':result_var,'line':line}

    def _ps_ident_stmt(self, name, line):
        if self._match_kw('with'):
            args = [self._parse_expr()]
            while self._match_op(','):
                args.append(self._parse_expr())
            return {'type': 'call', 'name': name, 'args': args, 'line': line}
        op = self._match_op('+=', '-=', '*=', '/=')
        if op:
            expr = self._parse_expr()
            return {'type': 'compound_assign', 'name': name, 'op': op.value, 'expr': expr, 'line': line}
        return None

    # ──────────────────────────────────────────── entry
    def parse(self):
        stmts = []
        while not self._at_end():
            s = self._parse_stmt()
            if s: stmts.append(s)
        return stmts

    def _parse_compare_with_left(self, left):
        """Parse comparison starting from an already-parsed left operand."""
        self._skip_nl()
        if self._match_kw('is'):
            neg = self._match_kw('not')
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
                return {'type': 'builtin_call', 'fn': 'is_empty', 'args': [left], 'line': 0}
            elif self._match_kw('null', 'none'):
                op = '!=' if neg else '=='
                return {'type': 'compare', 'op': op, 'left': left, 'right': {'type': 'null'}}
            else:
                op = '!=' if neg else '=='
            right = self._parse_arith()
            return {'type': 'compare', 'op': op, 'left': left, 'right': right}
        if self._match_kw('contains'):
            right = self._parse_arith()
            return {'type': 'builtin_call', 'fn': 'contains', 'args': [left, right], 'line': 0}
        op_tok = self._match_op('==', '!=', '>=', '<=', '>', '<')
        if op_tok:
            right = self._parse_arith()
            return {'type': 'compare', 'op': op_tok.value, 'left': left, 'right': right}
        return left
