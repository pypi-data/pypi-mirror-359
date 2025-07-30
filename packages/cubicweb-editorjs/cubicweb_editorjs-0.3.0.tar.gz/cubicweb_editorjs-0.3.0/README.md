** Warning this cube is not intended for use in production currently **

Summary
-------
Add editorjs format for RichString.
This cube adds the application/vnd.cubicweb.editorjs mimetype to the available
formats for RichStrings.
It also adds a widget which allows to edit the RichString using the EditorJS library (a WYSIWYG editor).

Status of this project
----------------------

This project has been initiated as a POC to test integration of EditorJS in CubicWeb.

Features:
- [X] setting the format of a RichString to application/vnd.cubicweb.editorjs
- [X] edition on an **already existing** RichString attribute with EditorJS
- [X] rendering a RichString using this mime type in some conditions (see below)
- [ ] RQL plugin allowing to edit and execute RQL queries



Known bugs:
- when switching to application/vnd.cubicweb.editorjs the editor is not loaded
  which means that only already saved attributes can be edited with EditorJS
- the rich string is not rendered when it is asynchroneously loaded (after the
  page's scripts have run). This happens with CubicWeb web in tab views.
- the breadcrumb displays the json instead of a rendered version of the RichString
- it makes automatic tests of client cubes fail

Implementation flaws:

- the implementation use monkeypatches to
    - add the application/vnd.cubicweb.editorjs format to the known format list
    - override some views
    - override entities `printable_value` method (might not be the best place
      to add the widget)
- missing mttransforms for application/vnd.cubicweb.editorjs to html
- images uploads are not supported

Usage in react applications
---------------------------

React applications don't suffer most of the problems seen above as they handle the rendering themselves.
Displaying an EditorJS is as easy as:

```tsx
function Edit() {
  const instanceRef = React.useRef<EditorJS | null>(null);
  async function handleSave() {
    if (instanceRef.current !== null) {
      const savedData = await instanceRef.current.save();
      rqlClient.queryRows(
        `Set X content %(content)s Where X is BlogEntry, X eid ${eid}`,
        { content: JSON.stringify(savedData) }
      );
    }
  }
  return (
    <>
      <EditorJs
          instanceRef={(instance) => (instanceRef.current = instance)}
          data={JSON.parse(blogEntry.content)}
      />
      <button onClick={handleSave}>Save</button>
    </>
  )
}
```

For rendering, a library like https://github.com/jeremyrajan/editorjs2html can be used.
```
if (contentFormat === "application/vnd.cubicweb.editorjs") {
    const edjsParser = EditorJsToHTML();
    const html = edjsParser.parse(JSON.parse(blogEntry.content)).join("");
    return <div dangerouslySetInnerHTML={{ __html: html }} />;
}
```


