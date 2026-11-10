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

    def do_execute(self, code, silent, store_history=True,
                   user_expressions=None, allow_stdin=False):
        stdout = io.StringIO()
        stderr = io.StringIO()

        # Базовый Kernel не подменяет builtins.input сам (это делает
        # IPythonKernel), поэтому подключаем stdin Jupyter вручную.
        self._allow_stdin = allow_stdin
        self.user_ns['input'] = self._algrus_input

        try:
            # 1. Лексический и синтаксический анализ.
            ast = Parser(Lexer(code), symbol_table=self.symbol_table).parse()

            # 2. Трансляция в Python. В ячейке выполняем операторы на
            # верхнем уровне, без обёртки в main(), чтобы переменные
            # оставались доступны следующим ячейкам.
            python_code = PythonCodeGenerator(wrap_main=False).generate(ast)

            # 3. Выполнение в общем пространстве имён.
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
