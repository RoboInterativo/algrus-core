from .lexer import Lexer, TokenType

class ASTNode:
    pass

class Program(ASTNode):
    def __init__(self, name, declarations, statements):
        self.name = name
        self.declarations = declarations
        self.statements = statements

    def __str__(self):
        return f"Program({self.name}, {self.declarations}, {self.statements})"

class VarDeclaration(ASTNode):
    def __init__(self, var_type, identifiers):
        self.var_type = var_type
        self.identifiers = identifiers

    def __str__(self):
        return f"VarDeclaration({self.var_type}, {self.identifiers})"

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

class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()

    def error(self, message):
        raise Exception(f'Синтаксическая ошибка: {message} в строке {self.current_token.line}')

    def eat(self, token_type):
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error(f"Ожидался {token_type}, получен {self.current_token.type}")

    def program(self):
        """program : АЛГ идентификатор НАЧ declarations statements КОН"""
        self.eat(TokenType.АЛГ)
        program_name = self.current_token.value
        self.eat(TokenType.ИДЕНТ)
        self.eat(TokenType.НАЧ)

        declarations = self.declarations()
        statements = self.statements()

        self.eat(TokenType.КОН)
        self.eat(TokenType.ТОЧКА)

        return Program(program_name, declarations, statements)

    def declarations(self):
        """declarations : (var_declaration)*"""
        declarations = []
        while self.current_token.type in (TokenType.ЦЕЛ, TokenType.ВЕЩ, TokenType.ЛОГ, TokenType.СИМВ):
            declarations.append(self.var_declaration())
        return declarations

    def var_declaration(self):
        """var_declaration : type identifiers КОНЕЦ_СТРОКИ"""
        var_type = self.current_token.type
        self.eat(var_type)

        identifiers = [self.current_token.value]
        self.eat(TokenType.ИДЕНТ)

        while self.current_token.type == TokenType.ЗАПЯТАЯ:
            self.eat(TokenType.ЗАПЯТАЯ)
            identifiers.append(self.current_token.value)
            self.eat(TokenType.ИДЕНТ)

        self.eat(TokenType.КОНЕЦ_СТРОКИ)
        return VarDeclaration(var_type, identifiers)

    # def statements(self):
    #     """statements : (statement)*"""
    #     statements = []
    #     while self.current_token.type != TokenType.КОН:
    #         statements.append(self.statement())
    #     return statements
    def statements(self):
        """statements : (statement)*"""
        statements = []

        # Список токенов, которые означают конец блока операторов
        end_tokens = {
            TokenType.КОН, TokenType.КОН_ПОКА, TokenType.КОН_ДЛЯ,
            TokenType.ВСЕ, TokenType.ИНАЧЕ, TokenType.КОНЕЦ_ФАЙЛА
        }

        while self.current_token.type not in end_tokens:
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
    # def statement(self):
    #     """statement : assignment | if_statement | while_statement | for_statement | input_statement | output_statement"""
    #     if self.current_token.type == TokenType.ИДЕНТ:
    #         return self.assignment()
    #     elif self.current_token.type == TokenType.ЕСЛИ:
    #         return self.if_statement()
    #     elif self.current_token.type == TokenType.ПОКА:
    #         return self.while_statement()
    #     elif self.current_token.type == TokenType.ДЛЯ:
    #         return self.for_statement()
    #     elif self.current_token.type == TokenType.ВВОД:
    #         return self.input_statement()
    #     elif self.current_token.type == TokenType.ВЫВОД:
    #         return self.output_statement()
    #     else:
    #         self.error("Ожидался оператор")

    def assignment(self):
        """assignment : идентификатор ПРИСВОИТЬ expression КОНЕЦ_СТРОКИ"""
        var_name = self.current_token.value
        self.eat(TokenType.ИДЕНТ)
        self.eat(TokenType.ПРИСВОИТЬ)
        expr = self.expression()
        self.eat(TokenType.КОНЕЦ_СТРОКИ)
        return Assignment(Variable(var_name), expr)

    def if_statement(self):
        """if_statement : ЕСЛИ condition ТО statements (ИНАЧЕ statements)? ВСЕ КОНЕЦ_СТРОКИ"""
        self.eat(TokenType.ЕСЛИ)
        condition = self.condition()
        self.eat(TokenType.ТО)

        then_branch = self.statements()

        else_branch = None
        if self.current_token.type == TokenType.ИНАЧЕ:
            self.eat(TokenType.ИНАЧЕ)
            else_branch = self.statements()

        self.eat(TokenType.ВСЕ)
        self.eat(TokenType.КОНЕЦ_СТРОКИ)

        return IfStatement(condition, then_branch, else_branch)

    def while_statement(self):
        """while_statement : ПОКА condition ДЕЛАТЬ statements КОН_ПОКА КОНЕЦ_СТРОКИ"""
        self.eat(TokenType.ПОКА)
        condition = self.condition()
        self.eat(TokenType.ДЕЛАТЬ)
        body = self.statements()
        self.eat(TokenType.КОН_ПОКА)
        self.eat(TokenType.КОНЕЦ_СТРОКИ)
        return WhileStatement(condition, body)

    def for_statement(self):
        """for_statement : ДЛЯ идентификатор ОТ expression ДО expression (ШАГ expression)? ДЕЛАТЬ statements КОН_ДЛЯ КОНЕЦ_СТРОКИ"""
        self.eat(TokenType.ДЛЯ)
        var_name = self.current_token.value
        self.eat(TokenType.ИДЕНТ)
        self.eat(TokenType.ОТ)
        start = self.expression()
        self.eat(TokenType.ДО)
        end = self.expression()

        step = None
        if self.current_token.type == TokenType.ШАГ:
            self.eat(TokenType.ШАГ)
            step = self.expression()

        self.eat(TokenType.ДЕЛАТЬ)
        body = self.statements()
        self.eat(TokenType.КОН_ДЛЯ)
        self.eat(TokenType.КОНЕЦ_СТРОКИ)

        return ForStatement(Variable(var_name), start, end, step, body)

    def input_statement(self):
        """input_statement : ВВОД variables КОНЕЦ_СТРОКИ"""
        self.eat(TokenType.ВВОД)
        variables = self.variables()
        self.eat(TokenType.КОНЕЦ_СТРОКИ)
        return InputStatement(variables)

    def output_statement(self):
        """output_statement : ВЫВОД expressions КОНЕЦ_СТРОКИ"""
        self.eat(TokenType.ВЫВОД)
        expressions = self.expressions()
        self.eat(TokenType.КОНЕЦ_СТРОКИ)
        return OutputStatement(expressions)

    def variables(self):
        """variables : идентификатор (ЗАПЯТАЯ идентификатор)*"""
        variables = [Variable(self.current_token.value)]
        self.eat(TokenType.ИДЕНТ)

        while self.current_token.type == TokenType.ЗАПЯТАЯ:
            self.eat(TokenType.ЗАПЯТАЯ)
            variables.append(Variable(self.current_token.value))
            self.eat(TokenType.ИДЕНТ)

        return variables

    def expressions(self):
        """expressions : expression (ЗАПЯТАЯ expression)*"""
        expressions = [self.expression()]

        while self.current_token.type == TokenType.ЗАПЯТАЯ:
            self.eat(TokenType.ЗАПЯТАЯ)
            expressions.append(self.expression())

        return expressions

    def condition(self):
        """condition : expression ((РАВНО | НЕ_РАВНО | БОЛЬШЕ | МЕНЬШЕ | БОЛЬШЕ_РАВНО | МЕНЬШЕ_РАВНО) expression)?"""
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
        """factor : ПЛЮС factor
                  | МИНУС factor
                  | НЕ factor
                  | ЧИСЛО
                  | ВЕЩ_ЧИСЛО
                  | СТРОКА
                  | ИСТИНА
                  | ЛОЖЬ
                  | идентификатор
                  | СКОБКА_ЛЕВ expression СКОБКА_ПРАВ
        """
        token = self.current_token

        if token.type == TokenType.ПЛЮС:
            self.eat(TokenType.ПЛЮС)
            return UnaryOp(token, self.factor())
        elif token.type == TokenType.МИНУС:
            self.eat(TokenType.МИНУС)
            return UnaryOp(token, self.factor())
        elif token.type == TokenType.НЕ:
            self.eat(TokenType.НЕ)
            return UnaryOp(token, self.factor())
        elif token.type == TokenType.ЧИСЛО:
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
            self.eat(TokenType.ИДЕНТ)
            return Variable(token.value)
        elif token.type == TokenType.СКОБКА_ЛЕВ:
            self.eat(TokenType.СКОБКА_ЛЕВ)
            node = self.expression()
            self.eat(TokenType.СКОБКА_ПРАВ)
            return node
        else:
            self.error("Ожидался фактор")

    def parse(self):
        return self.program()
