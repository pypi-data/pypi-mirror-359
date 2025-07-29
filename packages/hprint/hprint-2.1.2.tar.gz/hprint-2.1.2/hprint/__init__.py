from typing import Any, Union
from functools import partial
from tabulate import tabulate
import json
import copy
from pprint import pformat
import os
import traceback
import logging
import textwrap
from .utils import chain_get


DEFAULTS = {
    'tablefmt': 'simple',
    'disable_numparse': True
    # 'intfmt': '',
    # 'floatfmt': '',
}

_MISSING_VALUE = '[none]'

_print = partial(print, flush=True)

HPRINT_WRAP = int(os.getenv("HPRINT_WRAP", 50))

logger = logging.getLogger(__name__)

HPRINT_DEBUG = os.getenv("HPRINT_DEBUG")

__all__ = ['pretty_print', 'hprint']


def _format_numeric(value: Union[int, float], tabulate_kwargs: dict) -> Any:
    """
    Format numeric values according to the provided tabulate kwargs.
    """
    if 'floatfmt' in tabulate_kwargs and isinstance(value, float):
        return f"{value:{tabulate_kwargs['floatfmt']}}"
    elif 'intfmt' in tabulate_kwargs and isinstance(value, int):
        return f"{value:{tabulate_kwargs['intfmt']}}"
    return value


def _if_null(x, default):
    return default if x is None else x


def _no_convertion_func(x):
    return x


def _pprint(obj):
    _print(pformat(obj, indent=4))


def json_print(data):
    if isinstance(data, dict):
        _print(json.dumps(data, indent=4, sort_keys=True, default=str, ensure_ascii=False))
    elif isinstance(data, list):
        try:
            _print(json.dumps([dict(d) for d in data], indent=4, sort_keys=True, default=str, ensure_ascii=False))
        except Exception:
            try:
                _pprint([dict(d) for d in data])
            except Exception:
                _pprint(data)
    else:
        _pprint(data)


def _get(obj, key):
    if not key:
        return obj
    return chain_get(obj, key)


def tabulate_numbered_print(data, mappings, offset=0, convert=True, missing_value=_MISSING_VALUE, raw=False, **tabulate_kwargs):
    if not data:
        return
    if not mappings:
        mappings = {k: k for k in data[0]}
    mappings = {'No': '_no', **mappings}
    headers = mappings.keys()
    tabdata = []
    for idx, item in enumerate(data, start=1 + offset):
        attrs = []
        item['_no'] = idx
        for h in headers:
            k = mappings[h]
            if isinstance(k, (tuple, list)):
                if len(k) == 2:
                    default = missing_value
                    (k0, func) = k
                elif len(k) == 3:
                    (k0, default, func) = k
                else:
                    raise ValueError(f"Invalid mapping {k}")
                if not convert:
                    func = _no_convertion_func
                attrs.append(func(_if_null(_format_numeric(_get(item, k0), tabulate_kwargs), default)))
            else:
                attrs.append(_if_null(_format_numeric(_get(item, k), tabulate_kwargs), missing_value))
        tabdata.append(attrs)
    if 'floatfmt' in tabulate_kwargs:
        del tabulate_kwargs['floatfmt']
    if 'intfmt' in tabulate_kwargs:
        del tabulate_kwargs['intfmt']
    output = tabulate(tabdata, headers=headers, **tabulate_kwargs)
    if raw:
        return output
    _print(output)


def _len(x):
    return min(len(str(x)), HPRINT_WRAP)


def _indent(s: str, indent_cols, max_cols):
    lines = s.splitlines()
    if len(lines) <= 1:
        lines = textwrap.wrap(s, max_cols)
        if len(lines) <= 1:
            return s.ljust(max_cols)
    return lines[0] + '\n' + '\n'.join([(' ' * indent_cols + "| " + line) for line in lines[1:]])


def x_print(records, headers, offset=0, header=True):
    headers = list(headers)
    left_max_len = max(len(max(headers, key=len)), len(f"-[ RECORD {len(records)} ]-")) + 1
    right_max_len = max(_len(max(record, key=_len)) for record in records) + 1
    output = []
    for i, record in enumerate(records, 1 + offset):
        if header:
            output.append(f'-[ RECORD {i} ]'.ljust(left_max_len, '-') + '+' + '-' * right_max_len)
            # _print(f'-[ RECORD {i} ]'.ljust(left_max_len, '-') + '+' + '-' * right_max_len)
        for j, v in enumerate(record):
            # _print(f'{headers[j]}'.ljust(left_max_len) + '| ' + str(v).ljust(right_max_len))
            output.append(f'{headers[j]}'.ljust(left_max_len) + '| ' + _indent(str(v), left_max_len, right_max_len))
            # _print(f'{headers[j]}'.ljust(left_max_len) + '| ' + _indent(str(v), left_max_len, right_max_len))
    return os.linesep.join(output)


def tabulate_print(
        data, mappings, x=False, offset=0, header=True, raw=False,
        convert=True, missing_value=_MISSING_VALUE,
        **tabulate_kwargs,
):
    if not data:
        return
    if not mappings:
        mappings = {}
        for entry in data:
            for k in entry.keys():
                mappings[k] = k
    headers = mappings.keys()
    tabdata = []
    for item in data:
        attrs = []
        for h in headers:
            k = mappings[h]
            if isinstance(k, (tuple, list)):
                if len(k) == 2:
                    default = missing_value
                    (k0, func) = k
                elif len(k) == 3:
                    (k0, default, func) = k
                else:
                    raise ValueError(f"Invalid mapping {k}")
                if not convert:
                    func = _no_convertion_func
                attrs.append(func(_if_null(_format_numeric(_get(item, k0), tabulate_kwargs), default)))
            else:
                attrs.append(_if_null(_format_numeric(_get(item, k), tabulate_kwargs), missing_value))
        tabdata.append(attrs)
    if x:
        output = x_print(tabdata, headers, offset=offset, header=header)
    else:
        if 'floatfmt' in tabulate_kwargs:
            del tabulate_kwargs['floatfmt']
        if 'intfmt' in tabulate_kwargs:
            del tabulate_kwargs['intfmt']
        output = tabulate(tabdata, headers=headers if header else (), **tabulate_kwargs)
    if raw:
        return output
    _print(output)


def _set_defaults(tabulate_kwargs: dict[str, Any]) -> None:
    for k, d in DEFAULTS.items():
        if k not in tabulate_kwargs:
            tabulate_kwargs[k] = d


def hprint(
        data,
        *,
        mappings=None,
        json_format=False,
        as_json=False,
        x=False,
        offset=0,
        numbered=False,
        missing_value=_MISSING_VALUE,
        header=True,
        raw=False,
        convert=True,
        **tabulate_kwargs
):
    _set_defaults(tabulate_kwargs)
    as_json = as_json or json_format
    if not data:
        return
    try:
        if as_json:
            if raw:
                return data
            json_print(data)
        elif not x and numbered:
            return tabulate_numbered_print(
                copy.deepcopy(data), mappings, offset=offset, convert=convert, missing_value=missing_value, raw=raw,
                **tabulate_kwargs
            )
        else:
            return tabulate_print(
                data, mappings=mappings, x=x, offset=offset, header=header, raw=raw,
                convert=convert, missing_value=missing_value,
                **tabulate_kwargs
            )
    except Exception:
        json_print(data)
        if HPRINT_DEBUG or logger.isEnabledFor(logging.DEBUG):
            traceback.print_exc()


pretty_print = hprint
