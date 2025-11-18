class PythonCodeGenerator:
    def __init__(self):
        self.indent_level = 0
        self.lines = []

    def indent(self):
        self.indent_level += 1

    def dedent(self):
        self.indent_level -= 1

    def add_line(self, line):
        indent = "    " * self.indent_level
        self.lines.append(f"{indent}{line}")

    def generate(self, node):
        method_name = f'visit_{type(node).__name__}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        raise Exception(f'No visit method for {type(node).__name__}')

    def visit_Program(self, node):
        # Генерируем основной код программы
        self.add_line("# Generated from Russian Algorithmic Language")
        self.add_line("")

        # Объявления переменных (в Python не нужны, но можно инициализировать)
        for decl in node.declarations:
            self.generate(decl)

        self.add_line("")
        self.add_line("def main():")
        self.indent()

        # Основные операторы
        for stmt in node.statements:
            self.generate(stmt)

        self.dedent()
        self.add_line("")
        self.add_line("if __name__ == '__main__':")
        self.add_line("    main()")

        return "\n".join(self.lines)

    def visit_VarDeclaration(self, node):
        # В Python объявления не нужны, но можно инициализировать None
        type_map = {
            'ЦЕЛ': '0',
            'ВЕЩ': '0.0',
            'ЛОГ': 'False',
            'СИМВ': "''"
        }

        init_value = type_map.get(node.var_type.name, 'None')
        for ident in node.identifiers:
            self.add_line(f"{ident} = {init_value}")

    def visit_Assignment(self, node):
        left = self.generate(node.left)
        right = self.generate(node.right)
        self.add_line(f"{left} = {right}")

    def visit_BinaryOp(self, node):
        left = self.generate(node.left)
        right = self.generate(node.right)

        op_map = {
            'ПЛЮС': '+',
            'МИНУС': '-',
            'УМНОЖИТЬ': '*',
            'РАЗДЕЛИТЬ': '/',
            'РАВНО': '==',
            'НЕ_РАВНО': '!=',
            'БОЛЬШЕ': '>',
            'МЕНЬШЕ': '<',
            'БОЛЬШЕ_РАВНО': '>=',
            'МЕНЬШЕ_РАВНО': '<=',
            'И': 'and',
            'ИЛИ': 'or'
        }

        op_symbol = op_map.get(node.op.type.name, node.op.value)
        return f"({left} {op_symbol} {right})"

    def visit_UnaryOp(self, node):
        expr = self.generate(node.expr)

        op_map = {
            'ПЛЮС': '+',
            'МИНУС': '-',
            'НЕ': 'not '
        }

        op_symbol = op_map.get(node.op.type.name, node.op.value)
        return f"({op_symbol}{expr})"

    def visit_IfStatement(self, node):
        condition = self.generate(node.condition)
        self.add_line(f"if {condition}:")
        self.indent()

        for stmt in node.then_branch:
            self.generate(stmt)

        self.dedent()

        if node.else_branch:
            self.add_line("else:")
            self.indent()
            for stmt in node.else_branch:
                self.generate(stmt)
            self.dedent()

    def visit_WhileStatement(self, node):
        condition = self.generate(node.condition)
        self.add_line(f"while {condition}:")
        self.indent()

        for stmt in node.body:
            self.generate(stmt)

        self.dedent()

    def visit_ForStatement(self, node):
        var = self.generate(node.var)
        start = self.generate(node.start)
        end = self.generate(node.end)

        if node.step:
            step = self.generate(node.step)
            self.add_line(f"for {var} in range({start}, {end} + 1, {step}):")
        else:
            self.add_line(f"for {var} in range({start}, {end} + 1):")

        self.indent()
        for stmt in node.body:
            self.generate(stmt)
        self.dedent()

    def visit_InputStatement(self, node):
        for var in node.variables:
            var_name = self.generate(var)
            self.add_line(f"{var_name} = int(input('Введите {var_name}: '))")

    def visit_OutputStatement(self, node):
        parts = []
        for expr in node.expressions:
            parts.append(self.generate(expr))

        output_str = ", ".join(parts)
        self.add_line(f"print({output_str})")

    def visit_Variable(self, node):
        return node.name

    def visit_Number(self, node):
        return str(node.value)

    def visit_String(self, node):
        return f'"{node.value}"'

    def visit_Boolean(self, node):
        return "True" if node.value else "False"
