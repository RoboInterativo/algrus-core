import re
from enum import Enum

class TokenType(Enum):
    # Ключевые слова
    АЛГ = 'АЛГ'
    НАЧ = 'НАЧ'
    КОН = 'КОН'
    ЕСЛИ = 'ЕСЛИ'
    ТО = 'ТО'
    ИНАЧЕ = 'ИНАЧЕ'
    ВСЕ = 'ВСЕ'
    ПОКА = 'ПОКА'
    ДЕЛАТЬ = 'ДЕЛАТЬ'
    КОН_ПОКА = 'КОН_ПОКА'
    ДЛЯ = 'ДЛЯ'
    ОТ = 'ОТ'
    ДО = 'ДО'
    ШАГ = 'ШАГ'
    КОН_ДЛЯ = 'КОН_ДЛЯ'
    ВЫВОД = 'ВЫВОД'
    ВВОД = 'ВВОД'
    АРГ = 'АРГ'
    РЕЗ = 'РЕЗ'
    НЦ = 'НЦ'
    КЦ = 'КЦ'
    ТАБ = 'ТАБ'

    # Типы данных
    ЦЕЛ = 'ЦЕЛ'
    ВЕЩ = 'ВЕЩ'
    ЛОГ = 'ЛОГ'
    СИМВ = 'СИМВ'
    ЛИТ = 'ЛИТ'
    НАТ = 'НАТ'

    # Литералы
    ЧИСЛО = 'ЧИСЛО'
    ВЕЩ_ЧИСЛО = 'ВЕЩ_ЧИСЛО'
    СТРОКА = 'СТРОКА'
    ИСТИНА = 'ИСТИНА'
    ЛОЖЬ = 'ЛОЖЬ'

    # Идентификаторы
    ИДЕНТ = 'ИДЕНТ'

    # Операторы
    ПЛЮС = 'ПЛЮС'
    МИНУС = 'МИНУС'
    УМНОЖИТЬ = 'УМНОЖИТЬ'
    РАЗДЕЛИТЬ = 'РАЗДЕЛИТЬ'
    MOD = 'MOD'
    DIV = 'DIV'
    РАВНО = 'РАВНО'
    НЕ_РАВНО = 'НЕ_РАВНО'
    БОЛЬШЕ = 'БОЛЬШЕ'
    МЕНЬШЕ = 'МЕНЬШЕ'
    БОЛЬШЕ_РАВНО = 'БОЛЬШЕ_РАВНО'
    МЕНЬШЕ_РАВНО = 'МЕНЬШЕ_РАВНО'
    СТЕПЕНЬ = 'СТЕПЕНЬ'
    И = 'И'
    ИЛИ = 'ИЛИ'
    НЕ = 'НЕ'

    # Присваивание
    ПРИСВОИТЬ = 'ПРИСВОИТЬ'

    # Разделители
    ТОЧКА = 'ТОЧКА'
    ЗАПЯТАЯ = 'ЗАПЯТАЯ'
    ДВОЕТОЧИЕ = 'ДВОЕТОЧИЕ'
    СКОБКА_ЛЕВ = 'СКОБКА_ЛЕВ'
    СКОБКА_ПРАВ = 'СКОБКА_ПРАВ'
    СКОБКА_КВ_ЛЕВ = 'СКОБКА_КВ_ЛЕВ'
    СКОБКА_КВ_ПРАВ = 'СКОБКА_КВ_ПРАВ'

    # Конец строки
    КОНЕЦ_СТРОКИ = 'КОНЕЦ_СТРОКИ'
    КОНЕЦ_ФАЙЛА = 'КОНЕЦ_ФАЙЛА'

# Кириллица и латиница содержат визуально одинаковые буквы (а/a, с/c, х/x...).
# Для сравнения имён приводим их к одному ключу. Исходное написание при этом
# сохраняется — им пользуется генератор кода.
_CONFUSABLES = str.maketrans({
    'А': 'A', 'В': 'B', 'Е': 'E', 'К': 'K', 'М': 'M', 'Н': 'H',
    'О': 'O', 'Р': 'P', 'С': 'C', 'Т': 'T', 'У': 'Y', 'Х': 'X',
    'а': 'a', 'е': 'e', 'к': 'k', 'м': 'm', 'о': 'o', 'р': 'p',
    'с': 'c', 'т': 't', 'у': 'y', 'х': 'x',
    'і': 'i', 'ј': 'j', 'ѕ': 's',
})


def fold_identifier(name):
    """Ключ для сравнения имён без учёта кириллических/латинских двойников."""
    return name.translate(_CONFUSABLES)


class Token:
    def __init__(self, type, value, line, column):
        self.type = type
        self.value = value
        self.line = line
        self.column = column

    def __str__(self):
        return f"Token({self.type}, '{self.value}', {self.line}:{self.column})"

    def __repr__(self):
        return self.__str__()

class Lexer:
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.line = 1
        self.column = 1
        self.current_char = self.text[0] if text else None

        # Ключевые слова
        self.keywords = {
            'АЛГ': TokenType.АЛГ,
            'НАЧ': TokenType.НАЧ,
            'КОН': TokenType.КОН,
            'ЕСЛИ': TokenType.ЕСЛИ,
            'ТО': TokenType.ТО,
            'ИНАЧЕ': TokenType.ИНАЧЕ,
            'ВСЕ': TokenType.ВСЕ,
            'ПОКА': TokenType.ПОКА,
            'ДЕЛАТЬ': TokenType.ДЕЛАТЬ,
            'КОН_ПОКА': TokenType.КОН_ПОКА,
            'ДЛЯ': TokenType.ДЛЯ,
            'ОТ': TokenType.ОТ,
            'ДО': TokenType.ДО,
            'ШАГ': TokenType.ШАГ,
            'КОН_ДЛЯ': TokenType.КОН_ДЛЯ,
            'ВЫВОД': TokenType.ВЫВОД,
            'ВВОД': TokenType.ВВОД,
            'АРГ': TokenType.АРГ,
            'РЕЗ': TokenType.РЕЗ,
            'НЦ': TokenType.НЦ,
            'КЦ': TokenType.КЦ,
            'ТАБ': TokenType.ТАБ,
            'ЦЕЛ': TokenType.ЦЕЛ,
            'ВЕЩ': TokenType.ВЕЩ,
            'ЛОГ': TokenType.ЛОГ,
            'СИМВ': TokenType.СИМВ,
            'ЛИТ': TokenType.ЛИТ,
            'НАТ': TokenType.НАТ,
            'ИСТИНА': TokenType.ИСТИНА,
            'ЛОЖЬ': TokenType.ЛОЖЬ,
            'И': TokenType.И,
            'ИЛИ': TokenType.ИЛИ,
            'НЕ': TokenType.НЕ,
            'MOD': TokenType.MOD,
            'DIV': TokenType.DIV
        }

        # Операторы
        self.operators = {
            '+': TokenType.ПЛЮС,
            '-': TokenType.МИНУС,
            '*': TokenType.УМНОЖИТЬ,
            '/': TokenType.РАЗДЕЛИТЬ,
            '=': TokenType.РАВНО,
            '<>': TokenType.НЕ_РАВНО,
            '>': TokenType.БОЛЬШЕ,
            '<': TokenType.МЕНЬШЕ,
            '>=': TokenType.БОЛЬШЕ_РАВНО,
            '<=': TokenType.МЕНЬШЕ_РАВНО,
            'И': TokenType.И,
            'ИЛИ': TokenType.ИЛИ,
            'НЕ': TokenType.НЕ,
            ':=': TokenType.ПРИСВОИТЬ,
            '^': TokenType.СТЕПЕНЬ
        }
    def peek_token(self):
        """Возвращает следующий токен, не сдвигая текущую позицию."""
        pos, line, col, char = self.pos, self.line, self.column, self.current_char
        token = self.get_next_token()
        self.pos, self.line, self.column, self.current_char = pos, line, col, char
        return token
        
    def error(self, message):
        raise Exception(f'Лексическая ошибка: {message} в строке {self.line}, позиция {self.column}')

    def advance(self):
        if self.current_char == '\n':
            self.line += 1
            self.column = 0

        self.pos += 1
        if self.pos >= len(self.text):
            self.current_char = None
        else:
            self.current_char = self.text[self.pos]
            self.column += 1

    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    def skip_comment(self):
        while self.current_char is not None and self.current_char != '\n':
            self.advance()
        self.advance()  # Пропускаем символ новой строки

    def number(self):
        result = ''
        while self.current_char is not None and (self.current_char.isdigit() or self.current_char == '.'):
            result += self.current_char
            self.advance()

        if '.' in result:
            return Token(TokenType.ВЕЩ_ЧИСЛО, float(result), self.line, self.column)
        else:
            return Token(TokenType.ЧИСЛО, int(result), self.line, self.column)

    def string(self):
        result = ''
        opener = self.current_char
        closers = {
            '"': ('"',),
            '«': ('»',),
            '„': ('"', '“'),
        }[opener]

        self.advance()  # Пропускаем открывающую кавычку
        while self.current_char is not None and self.current_char not in closers:
            result += self.current_char
            self.advance()

        if self.current_char is None:
            self.error('Незакрытая строка')

        self.advance()  # Пропускаем закрывающую кавычку
        return Token(TokenType.СТРОКА, result, self.line, self.column)

    def identifier(self):
        result = ''
        while (self.current_char is not None and
               (self.current_char.isalnum() or self.current_char == '_')):
            result += self.current_char
            self.advance()

        # Проверяем, является ли идентификатор ключевым словом
        token_type = self.keywords.get(result.upper())
        if token_type:
            return Token(token_type, result, self.line, self.column)
        else:
            return Token(TokenType.ИДЕНТ, result, self.line, self.column)

    def get_next_token(self):
        while self.current_char is not None:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue

            if self.current_char == '|':
                self.skip_comment()
                continue

            # Числа
            if self.current_char.isdigit():
                return self.number()

            # Строки
            if self.current_char in '"«„':
                return self.string()

            # Идентификаторы и ключевые слова
            if self.current_char.isalpha() or self.current_char == '_':
                return self.identifier()
            # Операторы и присваивание
            if self.current_char in '+-*/<>=:≠≤≥^':  # Включаем двоеточие и степень
                # Сначала проверяем составные операторы
                if self.current_char == '*' and self.pos + 1 < len(self.text) and self.text[self.pos + 1] == '*':
                    token = Token(TokenType.СТЕПЕНЬ, '**', self.line, self.column)
                    self.advance()
                    self.advance()
                    return token

                if self.current_char == ':' and self.pos + 1 < len(self.text) and self.text[self.pos + 1] == '=':
                    token = Token(TokenType.ПРИСВОИТЬ, ':=', self.line, self.column)
                    self.advance()
                    self.advance()
                    return token

                if self.current_char == '≠':
                    token = Token(TokenType.НЕ_РАВНО, '≠', self.line, self.column)
                    self.advance()
                    return token

                if self.current_char == '≤':
                    token = Token(TokenType.МЕНЬШЕ_РАВНО, '≤', self.line, self.column)
                    self.advance()
                    return token

                if self.current_char == '≥':
                    token = Token(TokenType.БОЛЬШЕ_РАВНО, '≥', self.line, self.column)
                    self.advance()
                    return token

                if self.current_char == '<' and self.pos + 1 < len(self.text) and self.text[self.pos + 1] == '>':
                    token = Token(TokenType.НЕ_РАВНО, '<>', self.line, self.column)
                    self.advance()
                    self.advance()
                    return token

                if self.current_char == '>' and self.pos + 1 < len(self.text) and self.text[self.pos + 1] == '=':
                    token = Token(TokenType.БОЛЬШЕ_РАВНО, '>=', self.line, self.column)
                    self.advance()
                    self.advance()
                    return token

                if self.current_char == '<' and self.pos + 1 < len(self.text) and self.text[self.pos + 1] == '=':
                    token = Token(TokenType.МЕНЬШЕ_РАВНО, '<=', self.line, self.column)
                    self.advance()
                    self.advance()
                    return token

                # Одиночные операторы (ПОСЛЕ составных!)
                operator = self.current_char
                token_type = self.operators.get(operator)
                if token_type:
                    token = Token(token_type, operator, self.line, self.column)
                    self.advance()
                    return token

            # Отдельная обработка двоеточия (если не было :=)
            if self.current_char == ':':
                token = Token(TokenType.ДВОЕТОЧИЕ, ':', self.line, self.column)
                self.advance()
                return token
            # Операторы
            # if self.current_char in '+-*/<>=':
            #     # Обрабатываем составные операторы
            #     if self.current_char == ':' and self.pos + 1 < len(self.text) and self.text[self.pos + 1] == '=':
            #         token = Token(TokenType.ПРИСВОИТЬ, ':=', self.line, self.column)
            #         self.advance()
            #         self.advance()
            #         return token
            #
            #     if self.current_char == '<' and self.pos + 1 < len(self.text) and self.text[self.pos + 1] == '>':
            #         token = Token(TokenType.НЕ_РАВНО, '<>', self.line, self.column)
            #         self.advance()
            #         self.advance()
            #         return token
            #
            #     if self.current_char == '>' and self.pos + 1 < len(self.text) and self.text[self.pos + 1] == '=':
            #         token = Token(TokenType.БОЛЬШЕ_РАВНО, '>=', self.line, self.column)
            #         self.advance()
            #         self.advance()
            #         return token
            #
            #     if self.current_char == '<' and self.pos + 1 < len(self.text) and self.text[self.pos + 1] == '=':
            #         token = Token(TokenType.МЕНЬШЕ_РАВНО, '<=', self.line, self.column)
            #         self.advance()
            #         self.advance()
            #         return token
            #
            #     # Одиночные операторы
            #     operator = self.current_char
            #     token_type = self.operators.get(operator)
            #     if token_type:
            #         token = Token(token_type, operator, self.line, self.column)
            #         self.advance()
            #         return token

            # Разделители
            if self.current_char == '.':
                token = Token(TokenType.ТОЧКА, '.', self.line, self.column)
                self.advance()
                return token

            if self.current_char == ',':
                token = Token(TokenType.ЗАПЯТАЯ, ',', self.line, self.column)
                self.advance()
                return token

            if self.current_char == ':':
                token = Token(TokenType.ДВОЕТОЧИЕ, ':', self.line, self.column)
                self.advance()
                return token

            if self.current_char == '(':
                token = Token(TokenType.СКОБКА_ЛЕВ, '(', self.line, self.column)
                self.advance()
                return token

            if self.current_char == ')':
                token = Token(TokenType.СКОБКА_ПРАВ, ')', self.line, self.column)
                self.advance()
                return token

            if self.current_char == '[':
                token = Token(TokenType.СКОБКА_КВ_ЛЕВ, '[', self.line, self.column)
                self.advance()
                return token

            if self.current_char == ']':
                token = Token(TokenType.СКОБКА_КВ_ПРАВ, ']', self.line, self.column)
                self.advance()
                return token

            if self.current_char == ';':
                token = Token(TokenType.КОНЕЦ_СТРОКИ, ';', self.line, self.column)
                self.advance()
                return token

            self.error(f"Неизвестный символ: '{self.current_char}'")

        return Token(TokenType.КОНЕЦ_ФАЙЛА, None, self.line, self.column)
