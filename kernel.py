import sys
import os
# Добавьте путь к родительской директории
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from .parser import Parser, Lexer
from .gen import PythonCodeGenerator

from ipykernel.kernelbase import Kernel

class YourLanguageKernel(Kernel):
    implementation = 'YourLanguage'
    implementation_version = '1.0'
    language = 'your_language'
    language_version = '1.0'
    language_info = {
        'name': 'your_language',
        'mimetype': 'text/x-yourlang',
        'file_extension': '.alg',
    }
    banner = "Your Language Kernel"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.parser = Parser()
        self.translator = PythonCodeGenerator()

    def do_execute(self, code, silent, store_history=True,
                   user_expressions=None, allow_stdin=False):

        if not silent:
            try:
                # 1. Парсинг
                lexer = Lexer(code)
                parser = Parser(lexer)
                ast = parser.parse()

                # 2. Трансляция в Python
                python_code = self.translator.generate(ast)

                # 3. Выполнение
                result = self.execute_python(python_code)

                # 4. Отправка результата в Jupyter
                self.send_response(self.iopub_socket, 'stream', {
                    'name': 'stdout',
                    'text': result
                })

            except Exception as e:
                self.send_response(self.iopub_socket, 'stream', {
                    'name': 'stderr',
                    'text': f"Error: {str(e)}"
                })

        return {
            'status': 'ok',
            'execution_count': self.execution_count,
            'payload': [],
            'user_expressions': {},
        }

    def execute_python(self, code):
        # Простое выполнение Python кода
        try:
            import io
            from contextlib import redirect_stdout, redirect_stderr

            f = io.StringIO()
            with redirect_stdout(f), redirect_stderr(f):
                exec(code, {})
            return f.getvalue()
        except Exception as e:
            return f"Execution error: {str(e)}"
