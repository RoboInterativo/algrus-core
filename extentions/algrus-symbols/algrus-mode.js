import { LanguageSupport, StreamLanguage } from '@codemirror/language';

// Ключевые слова АлгРус (лексика algrus_core/lexer.py).
const KEYWORDS = new Set([
  'АЛГ', 'НАЧ', 'КОН',
  'ЕСЛИ', 'ТО', 'ИНАЧЕ', 'ВСЕ',
  'ПОКА', 'ДЕЛАТЬ', 'КОН_ПОКА',
  'ДЛЯ', 'ОТ', 'ДО', 'ШАГ', 'КОН_ДЛЯ',
  'ВЫВОД', 'ВВОД',
  'АРГ', 'РЕЗ',
  'НЦ', 'КЦ', 'ТАБ'
]);

const TYPES = new Set(['ЦЕЛ', 'ВЕЩ', 'ЛОГ', 'СИМВ', 'ЛИТ', 'НАТ']);
const BOOLEANS = new Set(['ИСТИНА', 'ЛОЖЬ']);
const OPERATORS = new Set(['И', 'ИЛИ', 'НЕ']);

export const algrusStreamParser = {
  name: 'algrus',

  startState() {
    return {};
  },

  token(stream) {
    // Комментарий — «|» до конца строки.
    if (stream.match('|')) {
      stream.skipToEnd();
      return 'comment';
    }

    // Строки: "…", «…», „…“ и „…"
    if (
      stream.match(/^"[^"]*"/) ||
      stream.match(/^«[^»]*»/) ||
      stream.match(/^„[^“"]*[“"]/)
    ) {
      return 'string';
    }

    // Числа: 42, 3.14
    if (stream.match(/^\d+(?:\.\d+)?/)) {
      return 'number';
    }

    // Идентификаторы и ключевые слова (кириллица и латиница).
    if (stream.match(/^[а-яА-ЯёЁa-zA-Z_][а-яА-ЯёЁa-zA-Z0-9_]*/)) {
      const word = stream.current().toUpperCase();

      if (KEYWORDS.has(word)) return 'keyword';
      if (TYPES.has(word)) return 'typeName';
      if (BOOLEANS.has(word)) return 'bool';
      if (OPERATORS.has(word)) return 'operator';

      return 'variableName';
    }

    // Операторы: := ** <= >= <> ≠ ≤ ≥ + - * / = ^
    if (stream.match(/^(?::=|\*\*|<=|>=|<>|≠|≤|≥|[+\-*/=^])/)) {
      return 'operator';
    }

    stream.next();
    return null;
  },

  languageData: {
    commentTokens: { line: '|' }
  }
};

// JupyterLab 4 ожидает именно LanguageSupport, а StreamLanguage.define()
// возвращает Language.
export const algrusLanguage = new LanguageSupport(
  StreamLanguage.define(algrusStreamParser)
);
