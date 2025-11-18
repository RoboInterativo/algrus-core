from lexer import Lexer
from parser import Parser
from gen import *

def main():
    # Пример программы на алгоритмическом языке с русской нотацией
    program_text = """
АЛГ Пример
НАЧ
| Объявление переменных
ЦЕЛ а, б, результат;
ВЕЩ вещ_число;
ЛОГ флаг;

| Основная программа
а := 10;
б := 5;
вещ_число := 3.14;
флаг := ИСТИНА;

| Условный оператор
ЕСЛИ а > б ТО
    результат := а + б;
ИНАЧЕ
    результат := а - б;
ВСЕ;

| Цикл while
ПОКА результат < 100 ДЕЛАТЬ
    результат := результат * 2;
КОН_ПОКА;

| Цикл for
ДЛЯ i ОТ 1 ДО 5 ШАГ 1 ДЕЛАТЬ
    ВЫВОД "Итерация: ", i;
КОН_ДЛЯ;

| Ввод и вывод
ВВОД а, б;
ВЫВОД "Результат: ", результат;

КОН.
"""

    try:
        lexer = Lexer(program_text)
        parser = Parser(lexer)
        ast = parser.parse()
        print("Программа успешно разобрана!")
        print("Абстрактное синтаксическое дерево:")
        print(ast)
        generator = PythonCodeGenerator()
        python_code = generator.generate(ast)
        print(python_code)

        # Вывод токенов для демонстрации
        # print("\nТокены:")
        # lexer = Lexer(program_text)
        # token = lexer.get_next_token()
        # while token.type != lexer.token_type.КОНЕЦ_ФАЙЛА:
        #     print(token)
        #     token = lexer.get_next_token()

    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == "__main__":
    main()
