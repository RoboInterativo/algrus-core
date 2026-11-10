import io
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

from algrus_core import Lexer, Parser, PythonCodeGenerator
from algrus_core.kernel import AlgrusKernel, YourLanguageKernel, main as kernel_main


PROGRAM = '''АЛГ Пример
НАЧ
ЦЕЛ а, б, результат;
ВЕЩ вещ_число;
ЛОГ флаг;
а := 10;
б := 5;
вещ_число := 3.14;
флаг := ИСТИНА;
ЕСЛИ а > б И НЕ флаг ТО
    результат := а + б;
ИНАЧЕ
    результат := а - б;
ВСЕ;
ПОКА результат < 20 ДЕЛАТЬ
    результат := результат * 2;
КОН_ПОКА;
ДЛЯ i ОТ 1 ДО 3 ШАГ 1 ДЕЛАТЬ
    ВЫВОД "Итерация: ", i;
КОН_ДЛЯ;
ВЫВОД "Результат: ", результат;
КОН.
'''


SQ_PROGRAM = '''АЛГ решение квадратного уравнения (вещ а, b, с, х1, х2, лит y)
АРГ a, b, с
РЕЗ x1 , х2,у
НАЧ
    ВЕЩ D
    D = b*b -4*a*c
    ЕСЛИ D < 0 ТО 
        y:= "нет решения"
    ИНАЧЕ y:= "есть решение"
        x1=(-b+sqrt(D) )/(2*a)
        x2=(-b-sqrt(D) )/(2*a)

    ВСЕ
КОН.
'''


GCD_PROGRAM = '''алг нахождение наибольшего общего делителя (нат M, N, нат НОД)
арг M, N
рез НОД
нач нат x, y
    x := M; y := N
    пока x ≠ y
      нц
        если x > y
          то x := x - y
          иначе y := y - x
        все
      кц
    НОД := x
кон
'''


def compile_program(source, wrap_main=False):
    ast = Parser(Lexer(source)).parse()
    return PythonCodeGenerator(wrap_main=wrap_main).generate(ast)


class PipelineTest(unittest.TestCase):
    def test_generates_runnable_module(self):
        code = compile_program(PROGRAM, wrap_main=True)
        self.assertIn('def main():', code)
        self.assertIn("if __name__ == '__main__':", code)
        compile(code, '<test>', 'exec')

    def test_generates_top_level_code(self):
        code = compile_program(PROGRAM, wrap_main=False)
        self.assertNotIn('def main():', code)
        compile(code, '<test>', 'exec')

    def test_executes_with_expected_output(self):
        code = compile_program(PROGRAM)
        output = io.StringIO()
        namespace = {}
        with redirect_stdout(output):
            exec(compile(code, '<test>', 'exec'), namespace)

        self.assertEqual(namespace['результат'], 20)
        text = output.getvalue()
        self.assertIn('Итерация:  1', text)
        self.assertIn('Результат:  20', text)

    def test_logical_operators(self):
        code = compile_program(PROGRAM)
        namespace = {}
        exec(compile(code, '<test>', 'exec'), namespace)
        # а > б = True, НЕ флаг = False => ветка ИНАЧЕ дала 5, затем *2^2.
        self.assertEqual(namespace['результат'], 20)

    def test_negative_step(self):
        code = compile_program('''АЛГ Обратный
НАЧ
ЦЕЛ i, сумма;
сумма := 0;
ДЛЯ i ОТ 3 ДО 1 ШАГ -1 ДЕЛАТЬ
    сумма := сумма + i;
КОН_ДЛЯ;
ВЫВОД сумма;
КОН.
''')
        namespace = {}
        exec(compile(code, '<test>', 'exec'), namespace)
        self.assertEqual(namespace['сумма'], 6)

    def test_string_escaping(self):
        code = compile_program('''АЛГ Строка
НАЧ
ВЫВОД "Он сказал 'привет'";
КОН.
''')
        namespace = {}
        output = io.StringIO()
        with redirect_stdout(output):
            exec(compile(code, '<test>', 'exec'), namespace)
        self.assertIn('привет', output.getvalue())

    def test_syntax_error_has_location(self):
        with self.assertRaises(Exception) as ctx:
            compile_program('''АЛГ Плохо
НАЧ
ВЫВОД 1 + ;
КОН.
''')
        self.assertIn('строке 3', str(ctx.exception))

    def test_extended_header_with_params_and_results(self):
        ast = Parser(Lexer(SQ_PROGRAM)).parse()
        self.assertEqual(ast.name, 'решение квадратного уравнения')
        self.assertEqual(ast.args, ['а', 'b', 'с'])
        self.assertEqual(ast.results, ['х1', 'х2', 'y'])
        self.assertEqual(
            [(param.name, param.var_type) for param in ast.params],
            [('а', 'ВЕЩ'), ('b', 'ВЕЩ'), ('с', 'ВЕЩ'),
             ('х1', 'ВЕЩ'), ('х2', 'ВЕЩ'), ('y', 'ЛИТ')],
        )

    def test_extended_program_generates_callable_function(self):
        code = compile_program(SQ_PROGRAM)
        namespace = {}
        exec(compile(code, '<test>', 'exec'), namespace)

        solve = namespace['решение_квадратного_уравнения']
        self.assertEqual(solve(1, -5, 6), (3.0, 2.0, 'есть решение'))
        self.assertEqual(solve(1, -2, 1), (1.0, 1.0, 'есть решение'))
        self.assertEqual(solve(1, 2, 5), (0.0, 0.0, 'нет решения'))

    def test_statements_without_semicolons(self):
        code = compile_program('''АЛГ Без точек с запятой
НАЧ
ЦЕЛ x
x = 2
ЕСЛИ x > 1 ТО
    ВЫВОД "да"
ИНАЧЕ
    ВЫВОД "нет"
ВСЕ
КОН
''')
        namespace = {}
        output = io.StringIO()
        with redirect_stdout(output):
            exec(compile(code, '<test>', 'exec'), namespace)
        self.assertEqual(namespace['x'], 2)
        self.assertIn('да', output.getvalue())

    def test_confusable_cyrillic_and_latin_names(self):
        # а/b/с/x1/x2 набраны в разных местах то кириллицей, то латиницей.
        code = compile_program('''АЛГ Проверка
НАЧ
ВЕЩ а, b;
а = 2
b = 3
ВЫВОД a + b
КОН.
''')
        namespace = {}
        output = io.StringIO()
        with redirect_stdout(output):
            exec(compile(code, '<test>', 'exec'), namespace)
        self.assertEqual(namespace['а'], 2)
        self.assertEqual(namespace['b'], 3)
        self.assertIn('5', output.getvalue())

    def test_builtin_function_call(self):
        code = compile_program('''АЛГ Корень
НАЧ
ВЫВОД sqrt(81)
ВЫВОД корень(81)
ВЫВОД квкорень(81)
ВЫВОД корквадр(81)
КОН.
''')
        namespace = {}
        output = io.StringIO()
        with redirect_stdout(output):
            exec(compile(code, '<test>', 'exec'), namespace)
        self.assertEqual(output.getvalue().splitlines(), ['9.0'] * 4)

    def test_kumir_style_gcd(self):
        ast = Parser(Lexer(GCD_PROGRAM)).parse()
        self.assertEqual(ast.name, 'нахождение наибольшего общего делителя')
        self.assertEqual(ast.args, ['M', 'N'])
        self.assertEqual(ast.results, ['НОД'])
        self.assertEqual(
            [(param.name, param.var_type) for param in ast.params],
            [('M', 'НАТ'), ('N', 'НАТ'), ('НОД', 'НАТ')],
        )

        code = compile_program(GCD_PROGRAM)
        namespace = {}
        exec(compile(code, '<test>', 'exec'), namespace)
        gcd = namespace['нахождение_наибольшего_общего_делителя']

        self.assertEqual(gcd(48, 18), 6)
        self.assertEqual(gcd(1071, 462), 21)
        self.assertEqual(gcd(5, 5), 5)
        self.assertEqual(gcd(270, 192), 6)

    def test_kumir_style_for_block(self):
        code = compile_program('''АЛГ Сумма
НАЧ
ЦЕЛ s, i
s := 0
ДЛЯ i ОТ 1 ДО 3
НЦ
    s := s + i
КЦ
ВЫВОД s
КОН
''')
        namespace = {}
        output = io.StringIO()
        with redirect_stdout(output):
            exec(compile(code, '<test>', 'exec'), namespace)
        self.assertEqual(namespace['s'], 6)
        self.assertIn('6', output.getvalue())

    def test_one_dimensional_table(self):
        code = compile_program('''АЛГ Таблица
НАЧ
  ЦЕЛ таб A[1:5]
  ЦЕЛ i, s
  s := 0
  ДЛЯ i ОТ 1 ДО 5
  НЦ
    A[i] := i^2
    s := s + A[i]
  КЦ
  ВЫВОД s
КОН
''')
        namespace = {}
        output = io.StringIO()
        with redirect_stdout(output):
            exec(compile(code, '<test>', 'exec'), namespace)
        self.assertEqual(namespace['A'], [0, 1, 4, 9, 16, 25])
        self.assertEqual(namespace['s'], 55)
        self.assertIn('55', output.getvalue())

    def test_two_dimensional_table(self):
        code = compile_program('''АЛГ Матрица
НАЧ
  ВЕЩ таб B[1:3, 1:3]
  B[2, 3] := 1.5
  ВЫВОД B[2, 3]
КОН
''')
        namespace = {}
        output = io.StringIO()
        with redirect_stdout(output):
            exec(compile(code, '<test>', 'exec'), namespace)
        self.assertEqual(namespace['B'][2][3], 1.5)
        self.assertEqual(len(namespace['B']), 4)
        self.assertIn('1.5', output.getvalue())

    def test_table_bound_from_expression(self):
        code = compile_program('''АЛГ Граница
НАЧ
  ЦЕЛ таб A[1:2+2]
  ЦЕЛ i, сумма
  сумма := 0
  ДЛЯ i ОТ 1 ДО 4
  НЦ
    A[i] := i
    сумма := сумма + A[i]
  КЦ
  ВЫВОД сумма
КОН
''')
        namespace = {}
        output = io.StringIO()
        with redirect_stdout(output):
            exec(compile(code, '<test>', 'exec'), namespace)
        self.assertEqual(namespace['сумма'], 10)
        self.assertEqual(len(namespace['A']), 5)

    def test_for_float_step(self):
        code = compile_program('''АЛГ ДробныйШаг
НАЧ
  ВЕЩ x
  ДЛЯ x ОТ 1 ДО 2 ШАГ 0.5
  НЦ
    ВЫВОД x
  КЦ
КОН
''')
        namespace = {}
        output = io.StringIO()
        with redirect_stdout(output):
            exec(compile(code, '<test>', 'exec'), namespace)
        self.assertEqual(output.getvalue().splitlines(), ['1', '1.5', '2.0'])

    def test_for_variable_step(self):
        code = compile_program('''АЛГ ПеременныйШаг
НАЧ
  ВЕЩ x, d
  d := 0.5
  ДЛЯ x ОТ 2 ДО 1 ШАГ -d
  НЦ
    ВЫВОД x
  КЦ
КОН
''')
        namespace = {}
        output = io.StringIO()
        with redirect_stdout(output):
            exec(compile(code, '<test>', 'exec'), namespace)
        self.assertEqual(output.getvalue().splitlines(), ['2', '1.5', '1.0'])

    def test_input_logical(self):
        code = compile_program('''АЛГ Логика
НАЧ
  ЛОГ флаг
  ВВОД флаг
КОН
''')
        namespace = {}
        with patch('builtins.input', return_value='да'):
            exec(compile(code, '<test>', 'exec'), namespace)
        self.assertIs(namespace['флаг'], True)

        with patch('builtins.input', return_value='ложь'):
            exec(compile(code, '<test>', 'exec'), namespace)
        self.assertIs(namespace['флаг'], False)

    def test_input_whole_table_is_rejected(self):
        with self.assertRaises(TypeError) as ctx:
            compile_program('''АЛГ ВводТаблицы
НАЧ
  ЦЕЛ таб A[1:3]
  ВВОД A
КОН
''')
        self.assertIn('Используйте A[i]', str(ctx.exception))

    def test_table_parameter_horner(self):
        code = compile_program('''АЛГ СхемаГорнера (ЦЕЛ n, ВЕЩ x, ВЕЩ ТАБ a[0:n], ВЕЩ y)
АРГ n, a, x
РЕЗ y
НАЧ
  ЦЕЛ i
  i := 0
  y := a[0]
  ПОКА i <> n НЦ
    i := i + 1
    y := y * x + a[i]
  КЦ
КОН
''')
        namespace = {}
        exec(compile(code, '<test>', 'exec'), namespace)
        horner = namespace['СхемаГорнера']
        # 2x^3 - 3x^2 + 4x - 5 при x = 2 равно 7.
        self.assertEqual(horner(3, [2, -3, 4, -5], 2), 7)

    def test_power_precedence(self):
        code = compile_program('''АЛГ Степень
НАЧ
  ВЫВОД -2^2
  ВЫВОД 2^3^2
  ВЫВОД (2^3)^2
КОН
''')
        namespace = {}
        output = io.StringIO()
        with redirect_stdout(output):
            exec(compile(code, '<test>', 'exec'), namespace)
        self.assertEqual(output.getvalue().splitlines(), ['-4', '512', '64'])

    def test_alternative_string_quotes(self):
        code = compile_program('''АЛГ Кавычки
НАЧ
  ВЫВОД «привет»
  ВЫВОД „пока"
КОН
''')
        namespace = {}
        output = io.StringIO()
        with redirect_stdout(output):
            exec(compile(code, '<test>', 'exec'), namespace)
        self.assertEqual(output.getvalue().splitlines(), ['привет', 'пока'])


class KernelTest(unittest.TestCase):
    def setUp(self):
        self.kernel = AlgrusKernel()
        self.kernel.iopub_socket = None
        self.sent = []
        self.kernel.send_response = (
            lambda socket, msg_type, content=None, **kwargs:
            self.sent.append((msg_type, content))
        )

    def test_alias_and_entry_point(self):
        self.assertIs(YourLanguageKernel, AlgrusKernel)
        self.assertTrue(callable(kernel_main))

    def test_state_is_shared_between_cells(self):
        first = self.kernel.do_execute(
            'АЛГ Ячейка1\nНАЧ\nЦЕЛ x;\nx := 41;\nКОН.\n',
            silent=False,
        )
        second = self.kernel.do_execute(
            'АЛГ Ячейка2\nНАЧ\nx := x + 1;\nВЫВОД x;\nКОН.\n',
            silent=False,
        )

        self.assertEqual(first['status'], 'ok')
        self.assertEqual(second['status'], 'ok')
        self.assertEqual(self.kernel.user_ns['x'], 42)
        self.assertEqual(self.sent[-1], ('stream', {'name': 'stdout', 'text': '42\n'}))

    def test_silent_cell_does_not_send_output(self):
        result = self.kernel.do_execute(
            'АЛГ Тихая\nНАЧ\nВЫВОД 1;\nКОН.\n',
            silent=True,
        )
        self.assertEqual(result['status'], 'ok')
        self.assertEqual(self.sent, [])

    def test_error_cell_returns_error_status(self):
        result = self.kernel.do_execute(
            'АЛГ Плохо\nНАЧ\nВЫВОД 1 + ;\nКОН.\n',
            silent=False,
        )
        self.assertEqual(result['status'], 'error')
        self.assertIn('Синтаксическая ошибка', result['evalue'])
        self.assertEqual(self.sent[-1][0], 'stream')
        self.assertEqual(self.sent[-1][1]['name'], 'stderr')

    def test_algorithm_defined_in_one_cell_is_callable_from_next(self):
        first = self.kernel.do_execute(SQ_PROGRAM, silent=False)
        second = self.kernel.do_execute(
            'АЛГ Вызов\n'
            'НАЧ\n'
            'ВЫВОД решение_квадратного_уравнения(1, -5, 6);\n'
            'КОН.\n',
            silent=False,
        )

        self.assertEqual(first['status'], 'ok')
        self.assertEqual(second['status'], 'ok')
        self.assertIn('решение_квадратного_уравнения', self.kernel.user_ns)
        self.assertIn('(3.0, 2.0,', self.sent[-1][1]['text'])

    def test_input_uses_jupyter_stdin(self):
        prompts = []

        def fake_raw_input(prompt=''):
            prompts.append(prompt)
            return '7'

        self.kernel.raw_input = fake_raw_input
        result = self.kernel.do_execute(
            'АЛГ ТестВвода\nНАЧ\nЦЕЛ x;\nВВОД x;\nВЫВОД x * 6;\nКОН.\n',
            silent=False,
            allow_stdin=True,
        )

        self.assertEqual(result['status'], 'ok')
        self.assertEqual(prompts, ['Введите x: '])
        self.assertEqual(self.kernel.user_ns['x'], 7)
        self.assertEqual(self.sent[-1], ('stream', {'name': 'stdout', 'text': '42\n'}))

    def test_input_without_stdin_reports_clear_error(self):
        result = self.kernel.do_execute(
            'АЛГ ТестВвода\nНАЧ\nЦЕЛ x;\nВВОД x;\nКОН.\n',
            silent=False,
            allow_stdin=False,
        )

        self.assertEqual(result['status'], 'error')
        self.assertIn('ВВОД', result['evalue'])
        self.assertIn('stdin', result['evalue'])


if __name__ == '__main__':
    unittest.main()
