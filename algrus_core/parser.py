from .lexer import Lexer, TokenType, fold_identifier

class ASTNode:
    pass

class Param(ASTNode):
    def __init__(self, name, var_type=None, is_table=False, bounds=None):
        self.name = name
        self.var_type = var_type
        self.is_table = is_table
        self.bounds = bounds or []

    def __str__(self):
        return f"Param({self.name}, {self.var_type}, table={self.is_table}, {self.bounds})"

class Program(ASTNode):
    def __init__(self, name, declarations, statements,
                 params=None, args=None, results=None):
        self.name = name
        self.declarations = declarations
        self.statements = statements
        self.params = params or []
        self.args = args or []
        self.results = results or []

    def __str__(self):
        return f"Program({self.name}, {self.params}, {self.args}, {self.results}, {self.declarations}, {self.statements})"

class VarDeclaration(ASTNode):
    def __init__(self, var_type, identifiers):
        self.var_type = var_type
        self.identifiers = identifiers

    def __str__(self):
        return f"VarDeclaration({self.var_type}, {self.identifiers})"

class TableSpec(ASTNode):
    def __init__(self, name, bounds):
        self.name = name
        self.bounds = bounds  # список пар (нижняя, верхняя) — AST-выражения

    def __str__(self):
        return f"TableSpec({self.name}, {self.bounds})"

class TableDeclaration(ASTNode):
    def __init__(self, var_type, tables):
        self.var_type = var_type
        self.tables = tables

    def __str__(self):
        return f"TableDeclaration({self.var_type}, {self.tables})"

class IndexAccess(ASTNode):
    def __init__(self, name, indices):
        self.name = name
        self.indices = indices

    def __str__(self):
        return f"IndexAccess({self.name}, {self.indices})"

class Assignment(ASTNode):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __str__(self):
        return f"Assignment({self.left}, {self.right})"

class BinaryOp(ASTNode):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

    def __str__(self):
        return f"BinaryOp({self.left}, {self.op}, {self.right})"

class UnaryOp(ASTNode):
    def __init__(self, op, expr):
        self.op = op
        self.expr = expr

    def __str__(self):
        return f"UnaryOp({self.op}, {self.expr})"

class IfStatement(ASTNode):
    def __init__(self, condition, then_branch, else_branch=None):
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch

    def __str__(self):
        return f"IfStatement({self.condition}, {self.then_branch}, {self.else_branch})"

class WhileStatement(ASTNode):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

    def __str__(self):
        return f"WhileStatement({self.condition}, {self.body})"

class ForStatement(ASTNode):
    def __init__(self, var, start, end, step, body):
        self.var = var
        self.start = start
        self.end = end
        self.step = step
        self.body = body

    def __str__(self):
        return f"ForStatement({self.var}, {self.start}, {self.end}, {self.step}, {self.body})"

class InputStatement(ASTNode):
    def __init__(self, variables):
        self.variables = variables

    def __str__(self):
        return f"InputStatement({self.variables})"

class OutputStatement(ASTNode):
    def __init__(self, expressions):
        self.expressions = expressions

    def __str__(self):
        return f"OutputStatement({self.expressions})"

class Variable(ASTNode):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return f"Variable({self.name})"

class Number(ASTNode):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return f"Number({self.value})"

class String(ASTNode):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return f"String({self.value})"

class Boolean(ASTNode):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return f"Boolean({self.value})"

class FunctionCall(ASTNode):
    def __init__(self, name, arguments):
        self.name = name
        self.arguments = arguments

    def __str__(self):
        return f"FunctionCall({self.name}, {self.arguments})"

class Parser:
    TYPE_TOKENS = (
        TokenType.ЦЕЛ, TokenType.ВЕЩ, TokenType.ЛОГ,
        TokenType.СИМВ, TokenType.ЛИТ, TokenType.НАТ,
    )

    def __init__(self, lexer, symbol_table=None):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()
        # Общая таблица имён: одна и та же переменная, набранная кириллицей
        # и латиницей, должна обозначать один и тот же объект.
        self.symbols = symbol_table if symbol_table is not None else {}

    def resolve_name(self, name):
        key = fold_identifier(name)
        return self.symbols.setdefault(key, name)

    def error(self, message):
        raise Exception(f'Синтаксическая ошибка: {message} в строке {self.current_token.line}')

    def eat(self, token_type):
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error(f"Ожидался {token_type}, получен {self.current_token.type}")

    def program(self):
        """program : АЛГ name (params)? (АРГ names)? (РЕЗ names)? НАЧ ... КОН."""
        self.eat(TokenType.АЛГ)

        name_parts = []
        while self.current_token.type == TokenType.ИДЕНТ:
            name_parts.append(self.resolve_name(self.current_token.value))
            self.eat(TokenType.ИДЕНТ)
        if not name_parts:
            self.error('Ожидалось имя алгоритма')
        program_name = ' '.join(name_parts)

        params = []
        if self.current_token.type == TokenType.СКОБКА_ЛЕВ:
            params = self.parameter_list()

        args = []
        if self.current_token.type == TokenType.АРГ:
            args = self.identifier_list(TokenType.АРГ)

        results = []
        if self.current_token.type == TokenType.РЕЗ:
            results = self.identifier_list(TokenType.РЕЗ)

        self.eat(TokenType.НАЧ)

        declarations = self.declarations()
        statements = self.statements()

        self.eat(TokenType.КОН)
        self.optional_end()
        if self.current_token.type == TokenType.ТОЧКА:
            self.eat(TokenType.ТОЧКА)

        return Program(program_name, declarations, statements,
                       params=params, args=args, results=results)

    def parameter_list(self):
        """parameter_list : СКОБКА_ЛЕВ (type? ТАБ? ИДЕНТ bounds? (ЗАПЯТАЯ ...)*)? СКОБКА_ПРАВ"""
        self.eat(TokenType.СКОБКА_ЛЕВ)
        params = []
        current_type = None
        current_is_table = False

        if self.current_token.type == TokenType.СКОБКА_ПРАВ:
            self.eat(TokenType.СКОБКА_ПРАВ)
            return params

        while True:
            if self.current_token.type in self.TYPE_TOKENS:
                current_type = self.current_token.type.name
                current_is_table = False
                self.eat(self.current_token.type)

                if self.current_token.type == TokenType.ТАБ:
                    current_is_table = True
                    self.eat(TokenType.ТАБ)

            name = self.resolve_name(self.current_token.value)
            self.eat(TokenType.ИДЕНТ)

            bounds = []
            if current_is_table:
                if self.current_token.type != TokenType.СКОБКА_КВ_ЛЕВ:
                    self.error(f'Для таблицы {name} не указаны границы')
                bounds = self.table_bounds()
            elif self.current_token.type == TokenType.СКОБКА_КВ_ЛЕВ:
                current_is_table = True
                bounds = self.table_bounds()

            params.append(Param(name, current_type, current_is_table, bounds))

            if self.current_token.type != TokenType.ЗАПЯТАЯ:
                break
            self.eat(TokenType.ЗАПЯТАЯ)

        self.eat(TokenType.СКОБКА_ПРАВ)
        return params

    def identifier_list(self, keyword):
        """identifier_list : (АРГ | РЕЗ) идентификатор (ЗАПЯТАЯ идентификатор)*"""
        self.eat(keyword)
        names = [self.resolve_name(self.current_token.value)]
        self.eat(TokenType.ИДЕНТ)

        while self.current_token.type == TokenType.ЗАПЯТАЯ:
            self.eat(TokenType.ЗАПЯТАЯ)
            names.append(self.resolve_name(self.current_token.value))
            self.eat(TokenType.ИДЕНТ)

        return names

    def optional_end(self):
        """Необязательная точка с запятой (в новых программах её может не быть)."""
        while self.current_token.type == TokenType.КОНЕЦ_СТРОКИ:
            self.eat(TokenType.КОНЕЦ_СТРОКИ)

    def declarations(self):
        """declarations : (var_declaration)*"""
        declarations = []
        while self.current_token.type in self.TYPE_TOKENS:
            declarations.append(self.var_declaration())
        return declarations

    def var_declaration(self):
        """var_declaration : type identifiers | type ТАБ table (ЗАПЯТАЯ table)*"""
        var_type = self.current_token.type
        self.eat(var_type)

        if self.current_token.type == TokenType.ТАБ:
            self.eat(TokenType.ТАБ)
            return self.table_declaration(var_type)

        identifiers = [self.resolve_name(self.current_token.value)]
        self.eat(TokenType.ИДЕНТ)

        while self.current_token.type == TokenType.ЗАПЯТАЯ:
            self.eat(TokenType.ЗАПЯТАЯ)
            identifiers.append(self.resolve_name(self.current_token.value))
            self.eat(TokenType.ИДЕНТ)

        self.optional_end()
        return VarDeclaration(var_type, identifiers)

    def table_declaration(self, var_type):
        """table_declaration : идентификатор bounds (ЗАПЯТАЯ идентификатор bounds)*"""
        tables = []

        while True:
            name = self.resolve_name(self.current_token.value)
            self.eat(TokenType.ИДЕНТ)
            bounds = self.table_bounds()
            tables.append(TableSpec(name, bounds))

            if self.current_token.type != TokenType.ЗАПЯТАЯ:
                break
            self.eat(TokenType.ЗАПЯТАЯ)

        self.optional_end()
        return TableDeclaration(var_type, tables)

    def table_bounds(self):
        """table_bounds : СКОБКА_КВ_ЛЕВ expression ДВОЕТОЧИЕ expression (ЗАПЯТАЯ ...)* СКОБКА_КВ_ПРАВ"""
        self.eat(TokenType.СКОБКА_КВ_ЛЕВ)
        bounds = []

        while True:
            lower = self.expression()
            self.eat(TokenType.ДВОЕТОЧИЕ)
            upper = self.expression()
            bounds.append((lower, upper))

            if self.current_token.type != TokenType.ЗАПЯТАЯ:
                break
            self.eat(TokenType.ЗАПЯТАЯ)

        self.eat(TokenType.СКОБКА_КВ_ПРАВ)
        return bounds

    def index_indices(self):
        """index_indices : СКОБКА_КВ_ЛЕВ expression (ЗАПЯТАЯ expression)* СКОБКА_КВ_ПРАВ"""
        self.eat(TokenType.СКОБКА_КВ_ЛЕВ)
        indices = [self.expression()]

        while self.current_token.type == TokenType.ЗАПЯТАЯ:
            self.eat(TokenType.ЗАПЯТАЯ)
            indices.append(self.expression())

        self.eat(TokenType.СКОБКА_КВ_ПРАВ)
        return indices

    def lvalue(self):
        """lvalue : идентификатор (СКОБКА_КВ_ЛЕВ indices СКОБКА_КВ_ПРАВ)?"""
        name = self.resolve_name(self.current_token.value)
        self.eat(TokenType.ИДЕНТ)

        if self.current_token.type == TokenType.СКОБКА_КВ_ЛЕВ:
            return IndexAccess(name, self.index_indices())

        return Variable(name)

    def statements(self):
        """statements : (statement)*"""
        statements = []

        # Список токенов, которые означают конец блока операторов
        end_tokens = {
            TokenType.КОН, TokenType.КОН_ПОКА, TokenType.КОН_ДЛЯ,
            TokenType.ВСЕ, TokenType.ИНАЧЕ, TokenType.КЦ,
            TokenType.КОНЕЦ_ФАЙЛА
        }

        while self.current_token.type != TokenType.КОНЕЦ_ФАЙЛА:
            self.optional_end()
            if self.current_token.type in end_tokens:
                break
            statements.append(self.statement())

        return statements

    def statement(self):
        """statement : assignment | if_statement | while_statement | for_statement | input_statement | output_statement"""
        token_type = self.current_token.type

        if token_type == TokenType.ИДЕНТ:
            return self.assignment()
        elif token_type == TokenType.ЕСЛИ:
            return self.if_statement()
        elif token_type == TokenType.ПОКА:
            return self.while_statement()
        elif token_type == TokenType.ДЛЯ:
            return self.for_statement()
        elif token_type == TokenType.ВВОД:
            return self.input_statement()
        elif token_type == TokenType.ВЫВОД:
            return self.output_statement()
        else:
            self.error(f"Ожидался оператор, получен {token_type}")

    def assignment(self):
        """assignment : lvalue (ПРИСВОИТЬ | РАВНО) expression (КОНЕЦ_СТРОКИ)?"""
        left = self.lvalue()

        if self.current_token.type in (TokenType.ПРИСВОИТЬ, TokenType.РАВНО):
            self.eat(self.current_token.type)
        else:
            self.error('Ожидался оператор присваивания := или =')

        expr = self.expression()
        self.optional_end()
        return Assignment(left, expr)

    def if_statement(self):
        """if_statement : ЕСЛИ condition ТО statements (ИНАЧЕ statements)? ВСЕ (КОНЕЦ_СТРОКИ)?"""
        self.eat(TokenType.ЕСЛИ)
        condition = self.condition()
        self.eat(TokenType.ТО)

        then_branch = self.statements()

        else_branch = None
        if self.current_token.type == TokenType.ИНАЧЕ:
            self.eat(TokenType.ИНАЧЕ)
            else_branch = self.statements()

        self.eat(TokenType.ВСЕ)
        self.optional_end()

        return IfStatement(condition, then_branch, else_branch)

    def while_statement(self):
        """while_statement : ПОКА condition ((ДЕЛАТЬ statements КОН_ПОКА) | (НЦ statements КЦ))"""
        self.eat(TokenType.ПОКА)
        condition = self.condition()

        if self.current_token.type == TokenType.ДЕЛАТЬ:
            self.eat(TokenType.ДЕЛАТЬ)

        if self.current_token.type == TokenType.НЦ:
            self.eat(TokenType.НЦ)
            body = self.statements()
            self.eat(TokenType.КЦ)
        else:
            body = self.statements()
            self.eat(TokenType.КОН_ПОКА)

        self.optional_end()
        return WhileStatement(condition, body)

    def for_statement(self):
        """for_statement : ДЛЯ идентификатор ОТ expression ДО expression (ШАГ expression)? ДЕЛАТЬ? (statements КОН_ДЛЯ | НЦ statements КЦ)"""
        self.eat(TokenType.ДЛЯ)
        var_name = self.resolve_name(self.current_token.value)
        self.eat(TokenType.ИДЕНТ)
        self.eat(TokenType.ОТ)
        start = self.expression()
        self.eat(TokenType.ДО)
        end = self.expression()

        step = None
        if self.current_token.type == TokenType.ШАГ:
            self.eat(TokenType.ШАГ)
            step = self.expression()

        if self.current_token.type == TokenType.ДЕЛАТЬ:
            self.eat(TokenType.ДЕЛАТЬ)

        if self.current_token.type == TokenType.НЦ:
            self.eat(TokenType.НЦ)
            body = self.statements()
            self.eat(TokenType.КЦ)
        else:
            body = self.statements()
            self.eat(TokenType.КОН_ДЛЯ)

        self.optional_end()
        return ForStatement(Variable(var_name), start, end, step, body)

    def input_statement(self):
        """input_statement : ВВОД variables (КОНЕЦ_СТРОКИ)?"""
        self.eat(TokenType.ВВОД)
        variables = self.variables()
        self.optional_end()
        return InputStatement(variables)

    def output_statement(self):
        """output_statement : ВЫВОД expressions (КОНЕЦ_СТРОКИ)?"""
        self.eat(TokenType.ВЫВОД)
        expressions = self.expressions()
        self.optional_end()
        return OutputStatement(expressions)

    def variables(self):
        """variables : lvalue (ЗАПЯТАЯ lvalue)*"""
        variables = [self.lvalue()]

        while self.current_token.type == TokenType.ЗАПЯТАЯ:
            self.eat(TokenType.ЗАПЯТАЯ)
            variables.append(self.lvalue())

        return variables

    def expressions(self):
        """expressions : expression (ЗАПЯТАЯ expression)*"""
        expressions = [self.expression()]

        while self.current_token.type == TokenType.ЗАПЯТАЯ:
            self.eat(TokenType.ЗАПЯТАЯ)
            expressions.append(self.expression())

        return expressions

    def condition(self):
        """condition : and_condition (ИЛИ and_condition)*"""
        node = self.and_condition()

        while self.current_token.type == TokenType.ИЛИ:
            op = self.current_token
            self.eat(TokenType.ИЛИ)
            node = BinaryOp(node, op, self.and_condition())

        return node

    def and_condition(self):
        """and_condition : comparison (И comparison)*"""
        node = self.comparison()

        while self.current_token.type == TokenType.И:
            op = self.current_token
            self.eat(TokenType.И)
            node = BinaryOp(node, op, self.comparison())

        return node

    def comparison(self):
        """comparison : expression ((РАВНО | НЕ_РАВНО | БОЛЬШЕ | МЕНЬШЕ | БОЛЬШЕ_РАВНО | МЕНЬШЕ_РАВНО) expression)?"""
        left = self.expression()

        if self.current_token.type in (TokenType.РАВНО, TokenType.НЕ_РАВНО,
                                     TokenType.БОЛЬШЕ, TokenType.МЕНЬШЕ,
                                     TokenType.БОЛЬШЕ_РАВНО, TokenType.МЕНЬШЕ_РАВНО):
            op = self.current_token
            self.eat(self.current_token.type)
            right = self.expression()
            return BinaryOp(left, op, right)

        return left

    def expression(self):
        """expression : term ((ПЛЮС | МИНУС) term)*"""
        node = self.term()

        while self.current_token.type in (TokenType.ПЛЮС, TokenType.МИНУС):
            op = self.current_token
            self.eat(self.current_token.type)
            node = BinaryOp(node, op, self.term())

        return node

    def term(self):
        """term : factor ((УМНОЖИТЬ | РАЗДЕЛИТЬ) factor)*"""
        node = self.factor()

        while self.current_token.type in (TokenType.УМНОЖИТЬ, TokenType.РАЗДЕЛИТЬ):
            op = self.current_token
            self.eat(self.current_token.type)
            node = BinaryOp(node, op, self.factor())

        return node

    def factor(self):
        """factor : (ПЛЮС | МИНУС | НЕ) factor
                  | primary (СТЕПЕНЬ factor)?
        """
        token = self.current_token

        if token.type in (TokenType.ПЛЮС, TokenType.МИНУС, TokenType.НЕ):
            self.eat(token.type)
            return UnaryOp(token, self.factor())

        node = self.primary()

        if self.current_token.type == TokenType.СТЕПЕНЬ:
            op = self.current_token
            self.eat(TokenType.СТЕПЕНЬ)
            # Правая ассоциативность: 2^3^2 = 2^(3^2).
            node = BinaryOp(node, op, self.factor())

        return node

    def primary(self):
        """primary : ЧИСЛО | ВЕЩ_ЧИСЛО | СТРОКА | ИСТИНА | ЛОЖЬ
                   | идентификатор (СКОБКА_КВ_ЛЕВ indices СКОБКА_КВ_ПРАВ)?
                   | идентификатор СКОБКА_ЛЕВ arguments СКОБКА_ПРАВ
                   | СКОБКА_ЛЕВ expression СКОБКА_ПРАВ
        """
        token = self.current_token

        if token.type == TokenType.ЧИСЛО:
            self.eat(TokenType.ЧИСЛО)
            return Number(token.value)
        elif token.type == TokenType.ВЕЩ_ЧИСЛО:
            self.eat(TokenType.ВЕЩ_ЧИСЛО)
            return Number(token.value)
        elif token.type == TokenType.СТРОКА:
            self.eat(TokenType.СТРОКА)
            return String(token.value)
        elif token.type == TokenType.ИСТИНА:
            self.eat(TokenType.ИСТИНА)
            return Boolean(True)
        elif token.type == TokenType.ЛОЖЬ:
            self.eat(TokenType.ЛОЖЬ)
            return Boolean(False)
        elif token.type == TokenType.ИДЕНТ:
            name = self.resolve_name(token.value)
            self.eat(TokenType.ИДЕНТ)
            if self.current_token.type == TokenType.СКОБКА_КВ_ЛЕВ:
                return IndexAccess(name, self.index_indices())
            if self.current_token.type == TokenType.СКОБКА_ЛЕВ:
                return FunctionCall(name, self.arguments())
            return Variable(name)
        elif token.type == TokenType.СКОБКА_ЛЕВ:
            self.eat(TokenType.СКОБКА_ЛЕВ)
            node = self.expression()
            self.eat(TokenType.СКОБКА_ПРАВ)
            return node
        else:
            self.error("Ожидался фактор")

    def arguments(self):
        """arguments : СКОБКА_ЛЕВ (expression (ЗАПЯТАЯ expression)*)? СКОБКА_ПРАВ"""
        self.eat(TokenType.СКОБКА_ЛЕВ)
        args = []

        if self.current_token.type != TokenType.СКОБКА_ПРАВ:
            args.append(self.expression())
            while self.current_token.type == TokenType.ЗАПЯТАЯ:
                self.eat(TokenType.ЗАПЯТАЯ)
                args.append(self.expression())

        self.eat(TokenType.СКОБКА_ПРАВ)
        return args

    def parse(self):
        return self.program()
