tools = [
  "header",
  "list",
  "image",
  "checklist",
  "link",
  "quote",
  "simple-image",
  "code",
  "table",
];

function loadScript(scriptUrl) {
  const script = document.createElement("script");
  script.src = scriptUrl;
  document.body.appendChild(script);
  return new Promise((res, rej) => {
    script.onload = function () {
      res();
    };
    script.onerror = function () {
      rej();
    };
  });
}

function initEditorjs() {
  Array.from(document.getElementsByTagName("textarea")).forEach((node, index) => {
    if (node.getAttribute("data-cubicweb:type") == "editorjs") {
      const editor = document.createElement("div");
      node.style.display = "none";
      node.parentNode.appendChild(editor);
      const editorJsConfig = {
        /**
         * Id of Element that should contain Editor instance
         */
        holder: editor,
        tools: {
          header: Header,
          list: List,
          image: SimpleImage,
          checklist: Checklist,
          quote: Quote,
          linkTool: LinkTool,
          code: CodeTool,
          table: Table,
        },
        onChange: (api) => {
          api.saver.save().then((outputData) => {
            node.innerHTML = JSON.stringify(outputData);
          });
        },
      };
      if (node.innerHTML !== "") {
        try {
          editorJsConfig.data = JSON.parse(node.value);
        } catch (e) {
          console.error(
            "Existing content for editor.js init data is not a valid JSON. See DOM node",
            node.id
          );
        }
      }
      if (node.getAttribute("data-cubicweb:mode") == "read") {
        editorJsConfig.readOnly = true;
      }
      new EditorJS(editorJsConfig);
    }
  });
}
window.addEventListener("DOMContentLoaded", () => {
  loadScript(
    "https://cdn.jsdelivr.net/npm/@editorjs/editorjs@latest"
  ).then(() =>
    Promise.all(
      tools.map((tool) =>
        loadScript(`https://cdn.jsdelivr.net/npm/@editorjs/${tool}@latest`)
      )
    ).then(initEditorjs)
  )
}
);
