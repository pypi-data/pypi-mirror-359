"""cubicweb-editorjs application package

Add editorjs format for RichString
"""

import copy

from logilab.common.decorators import monkeypatch

from cubicweb import cwconfig, entity
from cubicweb_web import formfields, formwidgets as fw
from cubicweb_web.views import forms

from yams import constraints

NEW_PERSISTENT_OPTIONS = []
for option in cwconfig.PERSISTENT_OPTIONS:
    if option[0] == "default-text-format":
        option = ("default-text-format", copy.deepcopy(option[1]))
        option[1]["choices"] += ("application/vnd.cubicweb.editorjs",)
    NEW_PERSISTENT_OPTIONS.append(option)


formfields.EditableFileField.editable_formats += ("application/vnd.cubicweb.editorjs",)

forms.FieldsForm.needs_js += ("cubes.editorjs.js",)

constraints.FormatConstraint.regular_formats += ("application/vnd.cubicweb.editorjs",)


def use_editorjs(rich_text_field, form):
    """return True if editor.js should be used to edit entity's attribute named
    `attr`
    """
    return rich_text_field.format(form) == "application/vnd.cubicweb.editorjs"


class EditorJS(fw.TextArea):
    """EditorJS enabled <textarea>, will return a unicode string containing
    HTML formated text.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.attrs["cubicweb:type"] = "editorjs"

    def _render(self, form, field, renderer):
        return super()._render(form, field, renderer)


old_get_widget = formfields.RichTextField.get_widget


@monkeypatch(formfields.RichTextField)
def get_widget(self, form):
    if self.widget is None:
        if use_editorjs(self, form):
            return EditorJS()
    return old_get_widget(self, form)


old_get_format_field = formfields.RichTextField.get_format_field


@monkeypatch(formfields.RichTextField)
def get_format_field(self, form):
    if self.format_field:
        return self.format_field
    # we have to cache generated field since it's use as key in the
    # context dictionary
    req = form._cw
    try:
        return req.data[self]
    except KeyError:
        fkwargs = {"eidparam": self.eidparam, "role": self.role}
        if use_editorjs(self, form):
            fkwargs["widget"] = fw.HiddenInput()
            fkwargs["value"] = "application/vnd.cubicweb.editorjs"
            fkwargs["eidparam"] = self.eidparam
            field = formfields.StringField(name=self.name + "_format", **fkwargs)
            req.data[self] = field
            return field
        else:
            return old_get_format_field(self, form)


old_printable_value = entity.Entity.printable_value


@monkeypatch(entity.Entity)
def printable_value(
    self,
    attr,
    value=entity._marker,
    attrtype=None,
    format="text/html",
    displaytime=True,
):  # XXX cw_printable_value
    """return a displayable value (i.e. unicode string) which may contains
    html tags
    """
    attr = str(attr)
    if value is entity._marker:
        value = getattr(self, attr)
    if isinstance(value, str):
        value = value.strip()
    if value is None or value == "":  # don't use "not", 0 is an acceptable value
        return ""
    if attrtype is None:
        attrtype = self.e_schema.destination(attr)
    props = self.e_schema.relation_definition(attr)
    if attrtype == "String":
        # internalinalized *and* formatted string such as schema
        # description...
        if props.internationalizable:
            value = self._cw._(value)
        attrformat = self.cw_attr_metadata(attr, "format")
        if attrformat:
            if attrformat == "application/vnd.cubicweb.editorjs":
                if format == "text/plain":
                    return "EditorJS content"
                self._cw.add_js("cubes.editorjs.js")
                return f'<textarea data-cubicweb:type="editorjs" data-cubicweb:mode="read">{value}</textarea>'  # noqa
    return old_printable_value(self, attr, value, attrtype, format, displaytime)


def includeme(config):
    pass
