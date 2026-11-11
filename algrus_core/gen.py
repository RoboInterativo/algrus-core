import re

from .lexer import fold_identifier
from .parser import Variable


class PythonCodeGenerator:
    BUILTIN_FUNCTIONS = {
        'sqrt': 'math.sqrt',
        'abs': 'abs',
        'min': 'min',
        'max': 'max',
        'round': 'round',
        'pow': 'pow',
        'sin': 'math.sin',
        'cos': 'math.cos',
        'tan': 'math.tan',
        'log': 'math.log',
        'exp': 'math.exp',
        'len': 'len',
        'int': 'int',
        'float': 'float',
        'str': 'str',
        # русские псевдонимы
        'корень': 'math.sqrt',
        'квкорень': 'math.sqrt',
        'корквадр': 'math.sqrt',
        'квадратный_корень': 'math.sqrt',
        'модуль': 'abs',
        'мин': 'min',
        'макс': 'max',
        'округлить': 'round',
        'степень': 'pow',
        'синус': 'math.sin',
        'косинус': 'math.cos',
        'тангенс': 'math.tan',
        'логарифм': 'math.log',
        'экспонента': 'math.exp',
        'длина': 'len',
    }

    def __init__(self, wrap_main=True):
        self.indent_level = 0
        self.lines = []
        # wrap_main=True  — программы для запуска как отдельного файла;
        # wrap_main=False — тело программы верхнего уровня для Jupyter.
        self.wrap_main = wrap_main
        self.var_types = {}
        self.table_names = set()
        self.tmp_counter = 0

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
    def visit_ProcedureCall(self, node):
        target = self.BUILTIN_FUNCTIONS.get(node.name)
        if target is None:
            target = self.sanitize_name(node.name)

        args = ', '.join(self.generate(arg) for arg in node.arguments)
        self.add_line(f"{target}({args})")

    def visit_Program(self, node):
        # Генератор переиспользуется между вызовами, поэтому начинаем заново.
        self.indent_level = 0
        self.lines = []
        self.tmp_counter = 0
        self.var_types = {
            param.name: param.var_type
            for param in node.params
            if param.var_type
        }
        self.table_names = {
            param.name for param in node.params if param.is_table
        }
        for decl in node.declarations:
            if hasattr(decl, 'tables'):
                for table in decl.tables:
                    self.var_types[table.name] = decl.var_type.name
                    self.table_names.add(table.name)
            else:
                for ident in decl.identifiers:
                    self.var_types[ident] = decl.var_type.name

        self.add_line("# Generated from Russian Algorithmic Language")
        self.add_line("import math")
        self.add_line("")

        args = node.args or [param.name for param in node.params]
        results = node.results

        # Функция ({алг цел f}) возвращает значение через переменную "знач".
        if node.return_type is not None:
            value_key = fold_identifier('знач')
            for result in results:
                if fold_identifier(result) == value_key:
                    self.var_types.setdefault(result, node.return_type)
                    break

        # Алгоритм с аргументами/результатами оформляем как функцию:
        # её можно вызвать из следующей ячейки.
        if args or results:
            self._emit_algorithm(node, args, results)
            return "\n".join(self.lines)

        if not self.wrap_main:
            self._emit_declarations(node.declarations)
            self._emit_statements(node.statements)
            return "\n".join(self.lines)

        self.add_line("def main():")
        self.indent()
        self._emit_declarations(node.declarations)
        if node.declarations and node.statements:
            self.add_line("")
        self._emit_statements(node.statements)
        self.dedent()
        self.add_line("")
        self.add_line("if __name__ == '__main__':")
        self.add_line("    main()")

        return "\n".join(self.lines)

    def _emit_algorithm(self, node, args, results):
        function_name = self.sanitize_name(node.name)
        if function_name != node.name:
            self.add_line(f"# Алгоритм: {node.name}")

        self.add_line(f"def {function_name}({', '.join(args)}):")
        self.indent()

        # Результаты, которых нет среди аргументов, нужно создать заранее:
        # ветка алгоритма может их не заполнить.
        for result in results:
            if result not in args:
                default = self.default_value(self.var_types.get(result))
                self.add_line(f"{result} = {default}")

        self._emit_declarations(node.declarations)
        self._emit_statements(node.statements)

        if results:
            self.add_line(f"return {', '.join(results)}")

        self.dedent()

    @staticmethod
    def sanitize_name(name):
        """Превращает имя алгоритма в допустимое имя Python-функции."""
        cleaned = ''.join(
            ch if (ch.isalnum() or ch == '_') else '_'
            for ch in name
        )
        cleaned = re.sub(r'_+', '_', cleaned).strip('_')
        if not cleaned:
            cleaned = 'algorithm'
        if cleaned[0].isdigit():
            cleaned = '_' + cleaned
        return cleaned

    @staticmethod
    def default_value(var_type):
        return {
            'ЦЕЛ': '0',
            'НАТ': '0',
            'ВЕЩ': '0.0',
            'ЛОГ': 'False',
            'СИМВ': "''",
            'ЛИТ': "''",
        }.get(var_type, 'None')

    def _emit_declarations(self, declarations):
        for decl in declarations:
            self.generate(decl)

    def _emit_statements(self, statements):
        if not statements:
            self.add_line("pass")
            return
        for stmt in statements:
            self.generate(stmt)

    def visit_VarDeclaration(self, node):
        # В Python объявления не нужны, но можно инициализировать None
        type_map = {
            'ЦЕЛ': '0',
            'НАТ': '0',
            'ВЕЩ': '0.0',
            'ЛОГ': 'False',
            'СИМВ': "''",
            'ЛИТ': "''",
        }

        init_value = type_map.get(node.var_type.name, 'None')
        for ident in node.identifiers:
            self.add_line(f"{ident} = {init_value}")

    def visit_TableDeclaration(self, node):
        default = self.default_value(node.var_type.name)
        for table in node.tables:
            expression = self.table_expression(table.bounds, default)
            self.add_line(f"{table.name} = {expression}")

    def table_expression(self, bounds, default, depth=0):
        """Строит вложенные списки Python для таблицы с 1-индексацией.

        Нижняя граница в классических задачах равна 1; чтобы обращение
        A[i] работало напрямую, список создаётся размером upper + 1.
        """
        if depth >= len(bounds):
            return default

        upper = self.generate(bounds[depth][1])
        inner = self.table_expression(bounds, default, depth + 1)
        loop_var = f"__alg_i{depth}"
        return f"[{inner} for {loop_var} in range(({upper}) + 1)]"

    def visit_IndexAccess(self, node):
        indices = ''.join(f"[{self.generate(index)}]" for index in node.indices)
        return f"{node.name}{indices}"

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
            'СТЕПЕНЬ': '**',
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
        self._emit_statements(node.then_branch)
        self.dedent()

        if node.else_branch:
            self.add_line("else:")
            self.indent()
            self._emit_statements(node.else_branch)
            self.dedent()

    def visit_WhileStatement(self, node):
        condition = self.generate(node.condition)
        self.add_line(f"while {condition}:")
        self.indent()
        self._emit_statements(node.body)
        self.dedent()

    def visit_ForStatement(self, node):
        var = self.generate(node.var)
        start = self.generate(node.start)
        end = self.generate(node.end)

        # Шаг не указан — обычный целочисленный диапазон.
        if node.step is None:
            self.add_line(f"for {var} in range({start}, ({end}) + 1):")
            self.indent()
            self._emit_statements(node.body)
            self.dedent()
            return

        step_value = self._literal_step(node.step)

        if step_value == 0:
            raise ValueError('Шаг цикла не может быть равен нулю')

        # Целый литеральный шаг — можно использовать range().
        if isinstance(step_value, int) and not isinstance(step_value, bool):
            end_bound = f"({end}) - 1" if step_value < 0 else f"({end}) + 1"
            self.add_line(f"for {var} in range({start}, {end_bound}, {step_value}):")
            self.indent()
            self._emit_statements(node.body)
            self.dedent()
            return

        # Вещественный шаг или шаг-выражение: range() не подходит.
        step = self.generate(node.step)
        self.tmp_counter += 1
        n = self.tmp_counter
        start_name = f"__alg_start_{n}"
        end_name = f"__alg_end_{n}"
        step_name = f"__alg_step_{n}"

        self.add_line(f"{start_name} = {start}")
        self.add_line(f"{end_name} = {end}")
        self.add_line(f"{step_name} = {step}")
        self.add_line(
            f"if {step_name} == 0: "
            f"raise ValueError('Шаг цикла не может быть равен нулю')"
        )
        self.add_line(f"{var} = {start_name}")
        self.add_line(
            f"while ({var} <= {end_name}) if {step_name} > 0 "
            f"else ({var} >= {end_name}):"
        )
        self.indent()
        self._emit_statements(node.body)
        self.add_line(f"{var} += {step_name}")
        self.dedent()

    @staticmethod
    def _literal_step(node):
        """Возвращает числовое значение шага, если он записан литералом."""
        if node is None:
            return None
        if type(node).__name__ == 'Number':
            return node.value
        if type(node).__name__ == 'UnaryOp' and type(node.expr).__name__ == 'Number':
            if node.op.type.name == 'МИНУС':
                return -node.expr.value
            if node.op.type.name == 'ПЛЮС':
                return node.expr.value
        return None

    def visit_InputStatement(self, node):
        cast = {
            'ЦЕЛ': 'int',
            'НАТ': 'int',
            'ВЕЩ': 'float',
            'ЛОГ': 'bool',
            'СИМВ': 'str',
            'ЛИТ': 'str',
        }
        for var in node.variables:
            var_name = self.generate(var)
            base_name = getattr(var, 'name', var_name)

            if type(var).__name__ == 'Variable' and base_name in self.table_names:
                raise TypeError(
                    f'Нельзя ввести таблицу {base_name} целиком. '
                    f'Используйте {base_name}[i].'
                )

            caster = cast.get(self.var_types.get(base_name), 'int')
            prompt = f"input('Введите {var_name}: ')"

            if caster == 'bool':
                expression = (
                    f"{prompt}.strip().lower() "
                    f"in ('1', 'истина', 'true', 'да', 'д')"
                )
            else:
                expression = f"{caster}({prompt})"

            self.add_line(f"{var_name} = {expression}")

    def visit_OutputStatement(self, node):
        # КуМир-семантика: ВЫВОД склеивает значения без разделителей и без
        # автоматического перевода строки. Служебное имя «нс» в списке вывода
        # печатает перевод строки (завершает текущую строку).
        parts = []
        for expr in node.expressions:
            # «нс» — новая строка.
            if isinstance(expr, Variable) and \
                    fold_identifier(expr.name) == fold_identifier('нс'):
                parts.append('"\\n"')
            else:
                parts.append(self.generate(expr))

        if not parts:
            self.add_line("print('')")
            return
        # sep='' — без разделителей; end='' — без авто-переноса (его даёт «нс»).
        self.add_line(f"print({', '.join(parts)}, sep='', end='')")

    def visit_Variable(self, node):
        return node.name

    def visit_FunctionCall(self, node):
        target = self.BUILTIN_FUNCTIONS.get(node.name)
        if target is None:
            target = self.sanitize_name(node.name)
        arguments = ', '.join(self.generate(arg) for arg in node.arguments)
        return f"{target}({arguments})"

    def visit_Number(self, node):
        return str(node.value)

    def visit_String(self, node):
        return repr(node.value)

    def visit_Boolean(self, node):
        return "True" if node.value else "False"
