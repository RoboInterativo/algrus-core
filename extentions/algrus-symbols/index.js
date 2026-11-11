import { IEditorLanguageRegistry } from '@jupyterlab/codemirror';
import { Widget } from '@lumino/widgets';

import { algrusLanguage } from './algrus-mode';

const MIME = 'text/x-algrus';

// Кнопки со спецсимволами. cursorBack сдвигает курсор внутрь пары.
const SYMBOLS = [
  { label: '≠', text: '≠' },
  { label: '≤', text: '≤' },
  { label: '≥', text: '≥' },
  { label: ':=', text: ':=' },
  { label: '«»', text: '«»', cursorBack: 1 },
  { label: '^', text: '^' }
];

function insertSymbol(panel, symbol) {
  const cell = panel.content && panel.content.activeCell;
  const editor = cell && cell.editor;
  if (!editor || !editor.replaceSelection) {
    return;
  }

  editor.replaceSelection(symbol.text);

  if (symbol.cursorBack) {
    const position = editor.getCursorPosition();
    editor.setCursorPosition({
      line: position.line,
      column: Math.max(0, position.column - symbol.cursorBack)
    });
  }

  editor.focus();
}

function createButton(panel, symbol) {
  const node = document.createElement('button');
  node.type = 'button';
  node.className = 'jp-ToolbarButtonComponent';
  node.textContent = symbol.label;
  node.title = `Вставить ${symbol.text}`;
  node.addEventListener('click', () => insertSymbol(panel, symbol));

  // Toolbar.addItem принимает Widget, а не DOM-узел.
  return new Widget({ node });
}

const plugin = {
  id: 'algrus-symbols:plugin',
  description: 'Подсветка синтаксиса и спецсимволы АлгРус',
  autoStart: true,
  requires: [IEditorLanguageRegistry],

  activate(app, languages) {
    // --- 1. Регистрация языка ---
    if (!languages.findByMIME(MIME, true)) {
      languages.addLanguage({
        name: 'algrus',
        displayName: 'АлгРус',
        mime: MIME,
        extensions: ['alg'],
        support: algrusLanguage
      });
    }

    // --- 2. Кнопки в панели инструментов блокнота ---
    const addButtons = (panel) => {
      if (!panel || !panel.node) {
        return;
      }
      if (!panel.node.classList.contains('jp-NotebookPanel')) {
        return;
      }
      if (panel.node.dataset.algrusButtons || !panel.toolbar) {
        return;
      }
      panel.node.dataset.algrusButtons = 'true';

      SYMBOLS.forEach((symbol, index) => {
        panel.toolbar.addItem(
          `algrus-symbol-${index}`,
          createButton(panel, symbol)
        );
      });
    };

    app.shell.widgets('main').forEach(addButtons);
    app.shell.currentChanged.connect((sender, change) => {
      addButtons(change && change.newValue);
    });
  }
};

export default plugin;
