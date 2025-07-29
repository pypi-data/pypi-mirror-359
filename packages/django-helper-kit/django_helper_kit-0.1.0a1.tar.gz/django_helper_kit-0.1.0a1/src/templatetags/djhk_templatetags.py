from django import template
from django.utils import translation
from ..utils import dict_to_str

register = template.Library()


@register.simple_tag(name="djhk_define")
def define(val=None):
    if isinstance(val, str):
        val_upper = val.upper()
        if val_upper in ["TRUE", "YES"]:
            val = True
        elif val_upper in ["FALSE", "NO"]:
            val = False
    return val


@register.filter(name="djhk_json_dumps")
def json_dumps(in_dict: dict):
    return dict_to_str(in_dict)


# Not used anymore after PageContext implementation, kept here for future
# reference.
# @register.simple_tag(name="x_doc_title")
# def doc_title(*parts: tuple[str]):
#     parts = [part.strip()
#              for part in (list(reversed(parts)) + [settings.X_APP_NAME])
#              if part]
#     return (" | " if settings.X_TITLE_SEPARATOR is None
#             else settings.X_TITLE_SEPARATOR).join(parts)


@register.simple_tag(name="djhk_if_rtl")
def if_rtl(when_true: str, when_false: str):
    return when_true if translation.get_language_bidi() == "rtl" \
        else when_false


@register.simple_tag(name="dk_append")
def append(src: str, add: str, separator: str = " "):
    return f"{src}{separator}{add}" if add else src


@register.simple_tag(name="djhk_prepend")
def prepend(src: str, add: str, separator: str = " "):
    return f"{add}{separator}{src}" if add else src


@register.simple_tag(name="djhk_insert_class")
def insert_class(src: str, add: str, position: int = -1):
    if position == -1:
        return append(src=src, add=add, separator=" ")
    elif position == 0:
        return prepend(src=src, add=add, separator=" ")

    src_arr = src.split()
    if position < 0:
        position = len(src_arr) + 1 + position
        if position < 0:
            position = 0

    return " ".join(src_arr[:position]
                    + add.split()
                    + src_arr[position:]) + " "


@register.simple_tag(name="djhk_remove_class")
def remove_class(from_class: str, minus_class: str):
    from_class_arr = from_class.split()
    minus_class_arr = minus_class.split()

    for _minus_class in minus_class_arr:
        if _minus_class in from_class_arr:
            from_class_arr.remove(_minus_class)

    return " ".join(from_class_arr) + " "


@register.simple_tag(name="djhk_field_verbose_name")
def field_verbose_name(instance, field_name):
    return instance._meta.get_field(field_name).verbose_name.capitalize()       # NOQA
