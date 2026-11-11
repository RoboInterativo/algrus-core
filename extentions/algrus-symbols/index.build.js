var __defProp = Object.defineProperty;
var __getOwnPropDesc = Object.getOwnPropertyDescriptor;
var __getOwnPropNames = Object.getOwnPropertyNames;
var __hasOwnProp = Object.prototype.hasOwnProperty;
var __export = (target, all) => {
  for (var name in all)
    __defProp(target, name, { get: all[name], enumerable: true });
};
var __copyProps = (to, from, except, desc) => {
  if (from && typeof from === "object" || typeof from === "function") {
    for (let key of __getOwnPropNames(from))
      if (!__hasOwnProp.call(to, key) && key !== except)
        __defProp(to, key, { get: () => from[key], enumerable: !(desc = __getOwnPropDesc(from, key)) || desc.enumerable });
  }
  return to;
};
var __toCommonJS = (mod) => __copyProps(__defProp({}, "__esModule", { value: true }), mod);

// index.js
var index_exports = {};
__export(index_exports, {
  default: () => index_default
});
module.exports = __toCommonJS(index_exports);

// algrus-mode.js
var import_language = require("@codemirror/language");
var algrusLanguage = import_language.StreamLanguage.define({
  name: "algrus",
  token: function(stream, state) {
    if (stream.match("|")) {
      stream.skipToEnd();
      return "comment";
    }
    if (stream.match(/^"[^"]*"/) || stream.match(/^«[^»]*»/) || stream.match(/^„[^“]*“/)) {
      return "string";
    }
    if (stream.match(/^\d+(\.\d+)?/)) {
      return "number";
    }
    if (stream.match(/^[а-яА-ЯёЁa-zA-Z_][а-яА-ЯёЁa-zA-Z0-9_]*/)) {
      const word = stream.current().toUpperCase();
      const keywords = [
        "\u0410\u041B\u0413",
        "\u041D\u0410\u0427",
        "\u041A\u041E\u041D",
        "\u0415\u0421\u041B\u0418",
        "\u0422\u041E",
        "\u0418\u041D\u0410\u0427\u0415",
        "\u0412\u0421\u0415",
        "\u041F\u041E\u041A\u0410",
        "\u0414\u0415\u041B\u0410\u0422\u042C",
        "\u041A\u041E\u041D_\u041F\u041E\u041A\u0410",
        "\u0414\u041B\u042F",
        "\u041E\u0422",
        "\u0414\u041E",
        "\u0428\u0410\u0413",
        "\u041A\u041E\u041D_\u0414\u041B\u042F",
        "\u0412\u042B\u0412\u041E\u0414",
        "\u0412\u0412\u041E\u0414",
        "\u0410\u0420\u0413",
        "\u0420\u0415\u0417",
        "\u041D\u0426",
        "\u041A\u0426",
        "\u0422\u0410\u0411"
      ];
      const types = ["\u0426\u0415\u041B", "\u0412\u0415\u0429", "\u041B\u041E\u0413", "\u0421\u0418\u041C\u0412", "\u041B\u0418\u0422", "\u041D\u0410\u0422"];
      const booleans = ["\u0418\u0421\u0422\u0418\u041D\u0410", "\u041B\u041E\u0416\u042C"];
      const operators = ["\u0418", "\u0418\u041B\u0418", "\u041D\u0415"];
      if (keywords.includes(word)) return "keyword";
      if (types.includes(word)) return "typeName";
      if (booleans.includes(word)) return "bool";
      if (operators.includes(word)) return "operator";
      return "variableName";
    }
    if (stream.match(/^(:=|<=|>=|<>|≠|≤|≥|\+|\-|\*|\/|=|\^)/)) {
      return "operator";
    }
    stream.next();
    return null;
  }
});

// index.js
var plugin = {
  id: "algrus-symbols:plugin",
  autoStart: true,
  requires: [IEditorServices],
  // <--- Добавляем зависимость
  activate: function(app, editorServices) {
    const mimeType = "text/x-algrus";
    const spec = {
      name: "algrus",
      mime: mimeType,
      mode: "algrus",
      extensions: ["alg"]
    };
    editorServices.registerLanguage(spec, algrusLanguage);
    const symbols = ["\u2260", "\u2264", "\u2265", ":=", "\xAB\xBB", "^"];
    const addButtons = (panel) => {
      if (!panel.node.classList.contains("jp-NotebookPanel")) return;
      if (panel.node.dataset.algrusButtons) return;
      panel.node.dataset.algrusButtons = "true";
      symbols.forEach((sym) => {
        const btn = document.createElement("button");
        btn.className = "jp-ToolbarButtonComponent";
        btn.textContent = sym;
        btn.onclick = () => {
          const cell = panel.content.activeCell;
          if (cell && cell.editor) cell.editor.replaceSelection(sym);
        };
        panel.toolbar.addItem(`algrus-${sym}`, { node: btn });
      });
    };
    app.shell.widgets("main").forEach(addButtons);
    app.shell.currentChanged.connect(() => {
      app.shell.widgets("main").forEach(addButtons);
    });
    console.log("Algrus: Syntax highlight & Buttons loaded!");
  }
};
var index_default = plugin;
