"""Jupyter-ядро для алгоритмического языка русской нотации (АлгРус)."""

import io
import traceback
from contextlib import redirect_stderr, redirect_stdout

from ipykernel.kernelbase import Kernel

from .gen import PythonCodeGenerator
from .lexer import Lexer
from .parser import Parser


class AlgrusKernel(Kernel):
    implementation = 'algrus-core'
    implementation_version = '0.1.0'
    language = 'algrus'
    language_version = '0.1.0'
    language_info = {
        'name': 'algrus',
        'mimetype': 'text/x-algrus',
        'file_extension': '.alg',
        'codemirror_mode': 'text/x-algrus',
    }
    banner = 'АлгРус — алгоритмический язык русской нотации'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Пространство имён общее для всех ячеек: значения сохраняются
        # между выполнениями, как в обычном Python-ядре.
        self.user_ns = {'__name__': '__main__'}
        # Общая таблица имён для всех ячеек: кириллица и латиница,
        # визуально совпадающие в именах, считаются одной переменной.
        self.symbol_table = {}
        # --- Робот ---
        self._create_robot()

    def _create_robot(self):
        """Создаёт робота заново и обновляет ссылки в user_ns.

        Вызывается при старте ядра и перед каждой ячейкой с командами робота,
        чтобы повторный запуск начинался с чистого поля, а не с состояния
        прошлого выполнения.
        """
        from .widgets.robot import RobotWidget

        self.robot = RobotWidget(size=10, publish=self._publish_display)
        self.robot.step_delay = 0.1

        self.user_ns['робот'] = self.robot
        # Алиасы для удобства (чтобы писать `вперед` вместо `робот.вперед`)
        self.user_ns['вперед'] = self.robot.вперед
        self.user_ns['влево'] = self.robot.влево
        self.user_ns['вправо'] = self.robot.вправо
        self.user_ns['закрасить'] = self.robot.закрасить
        self.user_ns['стена_впереди'] = self.robot.стена_впереди
        self.user_ns['клетка_закрашена'] = self.robot.клетка_закрашена
        # Датчики для обхода лабиринта.
        self.user_ns['впереди_свободно'] = self.robot.впереди_свободно
        self.user_ns['справа_свободно'] = self.robot.справа_свободно
        self.user_ns['слева_свободно'] = self.robot.слева_свободно
        self.user_ns['на_выходе'] = self.robot.на_выходе
        self.user_ns['сброс'] = self.robot.сброс
        self.user_ns['карта'] = self.robot.задать_карту
        self.user_ns['залить'] = self.robot.залить
        self.user_ns['залей'] = self.robot.залить
        self.user_ns['найти_выход'] = self.robot.найти_выход
        self.user_ns['выйти'] = self.robot.найти_выход
        return self.robot

    # def do_execute(self, code, silent, store_history=True,
    #                user_expressions=None, allow_stdin=False):
    #     stdout = io.StringIO()
    #     stderr = io.StringIO()
    #
    #     # Базовый Kernel не подменяет builtins.input сам (это делает
    #     # IPythonKernel), поэтому подключаем stdin Jupyter вручную.
    #     self._allow_stdin = allow_stdin
    #     self.user_ns['input'] = self._algrus_input
    #
    #     try:
    #         # 1. Лексический и синтаксический анализ.
    #         ast = Parser(Lexer(code), symbol_table=self.symbol_table).parse()
    #
    #         # 2. Трансляция в Python. В ячейке выполняем операторы на
    #         # верхнем уровне, без обёртки в main(), чтобы переменные
    #         # оставались доступны следующим ячейкам.
    #         python_code = PythonCodeGenerator(wrap_main=False).generate(ast)
    #
    #         # 3. Выполнение в общем пространстве имён.
    #         with redirect_stdout(stdout), redirect_stderr(stderr):
    #             exec(compile(python_code, '<algrus>', 'exec'), self.user_ns)
    #
    #         self._send_stream(stdout.getvalue(), 'stdout', silent)
    #         self._send_stream(stderr.getvalue(), 'stderr', silent)
    #
    #         return {
    #             'status': 'ok',
    #             'execution_count': self.execution_count,
    #             'payload': [],
    #             'user_expressions': {},
    #         }
    def do_execute(self, code, silent, store_history=True,
                   user_expressions=None, allow_stdin=False):
        stdout = io.StringIO()
        stderr = io.StringIO()

        self._allow_stdin = allow_stdin
        self.user_ns['input'] = self._algrus_input

        try:
            # 1. Лексический и синтаксический анализ.
            ast = Parser(Lexer(code), symbol_table=self.symbol_table).parse()

            # 2. Трансляция в Python.
            python_code = PythonCodeGenerator(wrap_main=False).generate(ast)

            # 3. Показываем робота, если код его использует.
            if any(word in code for word in (
                    'вперед', 'влево', 'вправо', 'закрасить', 'робот',
                    'карта', 'залить', 'залей', 'на_выходе',
                    'найти_выход', 'выйти',
                    'впереди_свободно', 'справа_свободно', 'слева_свободно',
                    'стена_впереди', 'клетка_закрашена')):
                # Пересоздаём робота, чтобы стереть память прошлых запусков
                # и нарисовать чистого робота в текущей ячейке.
                self._create_robot()
                self.robot.show()

            # 4. Выполнение.
            with redirect_stdout(stdout), redirect_stderr(stderr):
                exec(compile(python_code, '<algrus>', 'exec'), self.user_ns)

            self._send_stream(stdout.getvalue(), 'stdout', silent)
            self._send_stream(stderr.getvalue(), 'stderr', silent)

            return {
                'status': 'ok',
                'execution_count': self.execution_count,
                'payload': [],
                'user_expressions': {},
            }
        except Exception as exc:
            self._send_stream(stdout.getvalue(), 'stdout', silent)

            error_text = ''.join(traceback.format_exception_only(type(exc), exc))
            self._send_stream(error_text, 'stderr', silent)

            return {
                'status': 'error',
                'execution_count': self.execution_count,
                'ename': type(exc).__name__,
                'evalue': str(exc),
                'traceback': [
                    line.rstrip('\n')
                    for line in traceback.format_exception(type(exc), exc, exc.__traceback__)
                ],
            }

    def _publish_display(self, msg_type, content):
        """Отправляет display_data/update_display_data в iopub (виджет робота)."""
        self.send_response(self.iopub_socket, msg_type, content)

    def _algrus_input(self, prompt=''):
        """input() для оператора ВВОД: запрашивает строку у фронтенда Jupyter."""
        if not self._allow_stdin:
            raise RuntimeError(
                'Оператор ВВОД требует интерактивного фронтенда Jupyter '
                'с поддержкой stdin (allow_stdin=True).'
            )
        return self.raw_input(prompt)

    def _send_stream(self, text, name, silent):
        if silent or not text:
            return
        self.send_response(self.iopub_socket, 'stream', {
            'name': name,
            'text': text,
        })


# Обратная совместимость со старым именем класса.
YourLanguageKernel = AlgrusKernel


def main():
    """Запуск ядра (используется Jupyter и консольной командой ``algrus``)."""
    from ipykernel.kernelapp import IPKernelApp
    IPKernelApp.launch_instance(kernel_class=AlgrusKernel)


if __name__ == '__main__':
    main()
