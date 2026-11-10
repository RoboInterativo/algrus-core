# Примеры программ

| Файл | Назначение |
| --- | --- |
| `quadratic.alg` | Алгоритм решения квадратного уравнения с `АРГ`/`РЕЗ` |
| `quadratic_call.alg` | Вызов алгоритма из предыдущего файла |
| `gcd.alg` | НОД в стиле КуМир: `нат`, `≠`, блоки `нц … кц` |
| `gcd_call.alg` | Вызов алгоритма НОД |
| `array_min.alg` | Таблица `цел таб A[1:5]` и поиск минимума |
| `horner.alg` | Схема Горнера: таблица как параметр `ВЕЩ ТАБ a[0:n]` |
| `horner_call.alg` | Вызов схемы Горнера с таблицей коэффициентов |
| `demo.alg` | Демонстрация объявлений, условий, циклов и ввода/вывода |

Файлы `quadratic.alg` и `quadratic_call.alg` рассчитаны на выполнение
в Jupyter по порядку: сначала первый определяет функцию, затем второй
её вызывает.

Проверить разбор и генерацию кода без Jupyter:

```bash
python - <<'PY'
from pathlib import Path
from algrus_core import Lexer, Parser, PythonCodeGenerator

for path in sorted(Path('examples').glob('*.alg')):
    ast = Parser(Lexer(path.read_text(encoding='utf-8'))).parse()
    code = PythonCodeGenerator(wrap_main=False).generate(ast)
    print(f'=== {path} ===')
    print(code)
PY
```
