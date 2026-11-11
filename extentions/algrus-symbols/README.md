# algrus-symbols

Расширение JupyterLab 4 для АлгРуса:

- подсветка синтаксиса для MIME `text/x-algrus` (его объявляет ядро
  `algrus_core`), файлы `*.alg`;
- кнопки `≠`, `≤`, `≥`, `:=`, `«»`, `^` на панели инструментов блокнота.

## Сборка

```bash
npm install
jupyter labextension build .
```

Результат сборки — каталог `labextension/`:

```text
labextension/
  package.json          # содержит jupyterlab._build
  static/
    remoteEntry.*.js
    *.js
```

`./build.sh` делает то же самое и копирует результат в Python-пакет
`extentions/algrus-symbols`, откуда его забирает `pip`.

```bash
./build.sh
pip install --force-reinstall --no-deps ../../extentions/algrus-symbols
```

## Почему не esbuild

JupyterLab 4 загружает только «федеративные» расширения: в `package.json`
должен быть блок `jupyterlab._build`, а в `static/` — `remoteEntry.*.js`,
собранный webpack'ом (`@jupyterlab/builder`). Простой бандл
`esbuild --format=cjs` с `require("@codemirror/language")` в браузере не
загрузится. Поэтому `index.build.js` — устаревший артефакт старой схемы.

## API JupyterLab 4

В JupyterLab 4 нет `IEditorServices.registerLanguage`. Язык регистрируется
через токен `IEditorLanguageRegistry`:

```js
requires: [IEditorLanguageRegistry],
activate(app, languages) {
  languages.addLanguage({
    name: 'algrus',
    mime: 'text/x-algrus',
    extensions: ['alg'],
    support: algrusLanguage   // LanguageSupport
  });
}
```

`StreamLanguage.define()` возвращает `Language`, поэтому его нужно обернуть
в `new LanguageSupport(...)`.
