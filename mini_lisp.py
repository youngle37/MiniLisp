#!/usr/bin/env python3

debugging = False

def debug(*args, indent=0, **kwargs):
    if debugging:
        indent = '    ' * indent
        print(f'\033[2m---> {indent}{" ".join(map(str, args))}\033[0m', **kwargs)

def success(*args, **kwargs):
    print(f'\033[92m{" ".join(map(str, args))}\033[0m', **kwargs)

def warning(*args, **kwargs):
    print(f'\033[93m{" ".join(map(str, args))}\033[0m', **kwargs)

def parse_tree(code):
    tokens = code.replace('(', ' ( ').replace(')', ' ) ').split()
    tree_code = []
    for token in tokens:
        if token not in ['(', ')']:
            tree_code.append(f'"{token}"')
        else:
            tree_code.append(token)
        if token != '(':
            tree_code.append(',')
    return eval(''.join(['(', *tree_code, ')']))

def is_id(s):
    c, *r = s
    if not c.islower():
        return False
    for c in r:
        if not (c.islower() or c == '-'):
            return False
    return True


class Function:
    def __init__(self, name='annoymous', func=None, arg_type=None, n_args=''):
        self.name = name
        self.func = func
        self.arg_type = arg_type
        self.n_args = n_args

    def __call__(self, *args):
        self._check_args(args)
        return self.func(*args)
    
    def _check_args(self, args):
        n_args = len(args)
        assert eval(f'{n_args} {self.n_args}'), f'expect number of arguments {self.n_args}, got {n_args}'
        for i, arg in enumerate(args):
            if self.arg_type == 'same':
                assert type(arg) == type(args[0]), (
                    f'expect argument {i + 1} with type {type(args[0]).__name__}'
                    f' but got {type(arg).__name__}')
            elif self.arg_type is not None:
                assert type(arg) == self.arg_type, (
                    f'expect argument {i + 1} with type {self.arg_type.__name__}'
                    f' but got {type(arg).__name__}')

    def __str__(self):
        a_str = f' [n_args {self.n_args}]' if self.n_args is not None else ''
        t_str = f' [arg_type {self.arg_type.__name__}]' if self.arg_type is not None else ''
        return f'<function \'{self.name}\'{a_str}{t_str}>'


def init_scope():
    def _add(*args):
        return sum(args)

    def _mul(*args):
        n = 1
        for i in args:
            n *= i
        return n
    
    def _equ(*args):
        for n in args[1:]:
            if args[0] != n:
                return False
        return True
    
    def _and(*args):
        return all(args)
    
    def _or(*args):
        return any(args)
    
    return {
        '+':        Function('+', _add,                 int, '>= 2'),
        '-':        Function('-', lambda x, y: x - y,   int, '== 2'),
        '*':        Function('*', _mul,                 int, '>= 2'),
        '/':        Function('/', lambda x, y: x // y,  int, '== 2'),
        'mod':      Function('mod', lambda x, y: x % y, int, '== 2'),
        '=':        Function('=', _equ,                 'same', '>= 2'),
        '>':        Function('>', lambda x, y: x > y,   int, '== 2'),
        '<':        Function('<', lambda x, y: x < y,   int, '== 2'),
        'and':      Function('and', _and,               bool, '>= 2'),
        'or':       Function('or', _or,                 bool, '>= 2'),
        'not':      Function('not', lambda x: not x,    bool, '== 1'),
        'print-num': Function('print-num',   lambda x: print(x),      int, '== 1'),
        'print-bool': Function('print-bool', lambda x: print({True: '#t', False: '#f'}[x]), bool, '== 1')
    }


def evaluate(statement, scope, level=0):
    if isinstance(statement, tuple):
        debug('statement:', str(statement).replace(',', '').replace('\'', ''), indent=level)
        debug('| variables:', ' '.join(f'{name}={value}' for name, value in scope.items() if not callable(value)), indent=level)
        debug('| functions:', ' '.join(name for name, value in scope.items() if callable(value)), indent=level)

        assert len(statement), 'missing function'
        primary = statement[0]

        if primary == 'define':
            _, name, value = statement
            assert is_id(name), f'invalid id: {name}'
            if type(value) is tuple and value[0] == 'fun':
                scope[name] = Function(name)
                func = evaluate(value, scope, level + 1)
                scope[name].func = func.func
                scope[name].n_args = func.n_args
            else:
                scope[name] = evaluate(value, scope, level + 1)
            return

        if primary == 'fun':
            _, arg_names, *defines, exp = statement
            scope = scope.copy()
            n_args = len(arg_names)
            for define in defines:
                evaluate(define, scope, level + 1)
            def _func(*args):
                for arg_name, arg in zip(arg_names, args):
                    scope[arg_name] = evaluate(arg, scope, level + 1)
                return evaluate(exp, scope.copy(), level + 1)
            return Function(func=_func, n_args=f'== {n_args}')

        if primary == 'if':
            _, cond, true, false = statement
            if evaluate(cond, scope, level + 1):
                return evaluate(true, scope, level + 1)
            else:
                return evaluate(false, scope, level + 1)
        
        if isinstance(primary, tuple):
            assert primary[0] == 'fun', 'argument 0 should be fun'
            func, *args = statement
            func = evaluate(func, scope, level + 1)
            args = [evaluate(arg, scope, level + 1) for arg in args]
            return func(*args)
        
        if primary in scope:
            func, *args = statement
            args = [evaluate(arg, scope, level + 1) for arg in args]
            debug('| call:', primary, args, indent=level)
            value = scope[func](*args)
            debug('| return:',  value, indent=level)
            return value
        
        if is_id(primary):
            assert False, f'undefined function: {primary}'
        
        assert False, f'invalid function: {primary}'

    else:
        if callable(statement):
            return statement

        try:
            return int(statement)
        except:
            pass
        
        try:
            return {'#t': True, '#f': False}[statement]
        except:
            pass
            
        try:
            return scope[statement]
        except:
            pass
        
        if is_id(statement):
            assert False, f'undefined variable: {statement}'
        
        assert False, f'invalid syntax: {statement}'


def run(code, scope=init_scope(), interactive=False):
    try:
        statements = parse_tree(code)
    except:
        if not (interactive or debugging):
            print('Error:', 'invalid syntax')
        else:
            warning('Error:', 'invalid syntax')
        return
    for statement in statements:
        try:
            retval = evaluate(statement, scope)
            if (debugging or interactive) and retval is not None:
                success('===>', retval)
        except Exception as e:
            if debugging:
                import traceback
                warning(traceback.format_exc())
            elif interactive:
                warning('Error:', str(e) or 'invalid syntax')
            else:
                print('Error:', str(e) or 'invalid syntax')



if __name__ == '__main__':
    import sys, os, readline

    if len(sys.argv) > 1 and os.path.isfile(sys.argv[1]):
        run(open(sys.argv[1]).read())

    else:
        while True:
            try:
                run(input('MiniLisp> '), interactive=True)
            except:
                break
