from copy import deepcopy
from django.conf import settings
from django.contrib import auth
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpRequest
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import functional, http
import importlib
import json
import re
from typing import Callable, Iterable


def _dict_lazy_value_to_str(in_dict: dict):
    for key, value in in_dict.items():
        if isinstance(value, functional.Promise):
            in_dict[key] = str(value)
        elif isinstance(value, dict):
            in_dict[key] = _dict_lazy_value_to_str(value)
    return in_dict


def dict_subset(in_dict: dict,
                keys: int | str | Iterable,
                ignore_missing_keys: bool = False) -> dict:
    if not isinstance(keys, Iterable):
        keys = [keys]

    return {key: in_dict[key] for key in keys if key in in_dict} \
        if ignore_missing_keys \
        else {key: in_dict[key] for key in keys}


def dict_to_str(in_dict: dict):
    return json.dumps(_dict_lazy_value_to_str(deepcopy(in_dict)))


def get_current_scheme_site(request: HttpRequest):
    return request.scheme + "://" + get_current_site(request).name


def get_form_fields(form) -> list:
    fields = list(form.base_fields)
    fields += [field for field in form.declared_fields if field not in fields]
    return fields


def get_module_names(name: str, package: str) -> dict:
    try:
        env_settings_module = importlib.import_module(name, package)
        if "__all__" in env_settings_module.__dict__:
            names = env_settings_module.__dict__["__all__"]
        else:
            names = [name for name in env_settings_module.__dict__
                     if not name.startswith("_")]

        return {name: getattr(env_settings_module, name) for name in names}
    except ModuleNotFoundError:
        return {}


def is_ajax(request: HttpRequest):
    return request.headers.get("x-requested-with") == "XMLHttpRequest"


def match_dict_keys(dict1: dict,
                    dict2: dict,
                    keys: int | str | Iterable) -> bool:
    return dict_subset(dict1, keys) == dict_subset(dict2, keys)


def redirect_next(*args,
                  to: str | None = None,
                  permanent: bool = False,
                  request: HttpRequest | None = None,
                  params: dict | None = None,
                  **kwargs):
    to = (to or
          (request and
           (request.POST.get(auth.REDIRECT_FIELD_NAME) or
            request.GET.get(auth.REDIRECT_FIELD_NAME))) or
          (request and
           request.user.is_authenticated and                                    # NOQA
           settings.LOGIN_REDIRECT_URL) or
          "/")
    if params is not None:
        to = reverse(to) + "?" + http.urlencode(params)

    return redirect(to, permanent=permanent, *args, **kwargs)


def tokenize(string: str, map_fn: Callable | None = None) -> list:
    string = str(string)
    tokens = []
    quote_opened = False
    while string:
        quote_index = string.find('"')
        if quote_index == -1:
            tokens.extend(string.split())
            string = ""
        else:
            string_before = string[:quote_index]
            string = string[quote_index + 1:]
            if quote_opened:
                tokens.append(string_before)
            else:
                tokens.extend(string_before.split())
            quote_opened = not quote_opened

    tokens.sort(key=len, reverse=True)

    if callable(map_fn):
        tokens = map(map_fn, tokens)

    return tokens


def _lower_delim_separated(in_str: str, delim: str):
    if not in_str:
        return

    out_str = re.sub("[^a-zA-Z0-9]", delim, in_str)
    out_str = re.sub("(?<!^)(?=[A-Z][a-z0-9])", delim, out_str)
    out_str = re.sub(f"{delim}{{2,}}", delim, out_str)
    return out_str.strip(delim).lower()


def kebab_case(in_str: str):
    return _lower_delim_separated(in_str, "-")


def snake_case(in_str: str):
    return _lower_delim_separated(in_str, "_")
