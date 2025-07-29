import json
from types import SimpleNamespace
from typing import Any

from .cjsify import Undefined, unjsify
from .cjsify import Object


class ObjectEncoder(json.JSONEncoder):
    """
    Custom JSON encoder supporting jsify objects, omitting `Undefined` values.

    This encoder serializes:
      - `Undefined` as `null` in JSON, unless omitted.
      - `Object` (from jsify) by recursively converting them to plain Python objects using `unjsify`.
      - `SimpleNamespace` as a dictionary of its attributes.
      - All other types using standard JSON encoding.

    The `omit_undefined` parameter controls whether fields or items with `Undefined` values
    are included in the output. If `omit_undefined` is True, all such values are omitted
    from dictionaries, lists, and tuples at all nesting levels before encoding.

    Parameters
    ----------
    omit_undefined : bool, optional
        If True, any field/item with value `Undefined` is omitted from the output (default: True).
    *args
        Additional positional arguments passed to `json.JSONEncoder`.
    **kwargs
        Additional keyword arguments passed to `json.JSONEncoder`.
    """

    def __init__(self, omit_undefined=True, *args, **kwargs):
        """
        Initialize the encoder with an option to omit `Undefined` values.

        Parameters
        ----------
        omit_undefined : bool, optional
            If True, `Undefined` values are omitted from output (default: True).
        *args
            Additional positional arguments for the parent constructor.
        **kwargs
            Additional keyword arguments for the parent constructor.
        """
        super().__init__(*args, **kwargs)
        self.omit_undefined = omit_undefined

    def iterencode(self, o, _one_shot=False):
        """
        Recursively remove all `Undefined` values (if enabled) before serialization.

        Parameters
        ----------
        o : Any
            The object to encode.
        _one_shot : bool, optional
            Passed through to the base class.

        Returns
        -------
        generator
            An iterator yielding encoded JSON chunks.

        Notes
        -----
        - Converts all `Object` instances to plain Python objects using `unjsify`.
        - Omits fields/items with `Undefined` values if `omit_undefined` is True.
        - Handles all nested containers recursively.
        """

        def deeply_unjsify_with_omit(o):
            if isinstance(o, Object):
                o = unjsify(o)
            if self.omit_undefined:
                if isinstance(o, tuple):
                    o = o.__class__(deeply_unjsify_with_omit(value) for value in o if value is not Undefined)
                elif isinstance(o, list):
                    o = o.__class__(deeply_unjsify_with_omit(value) for value in o if value is not Undefined)
                elif isinstance(o, dict):
                    o = o.__class__({key: deeply_unjsify_with_omit(value) for key, value in o.items() if value is not Undefined})
            return o

        return super().iterencode(deeply_unjsify_with_omit(o), _one_shot)

    def default(self, o: Any) -> Any:
        """
        Custom default handler for objects not serializable by default.

        Parameters
        ----------
        o : Any
            The object to encode.

        Returns
        -------
        Any
            A JSON-serializable value.

        Notes
        -----
        - Returns None for `Undefined` (serialized as `null` in JSON).
        - Returns unjsified value for `Object` instances.
        - Serializes `SimpleNamespace` as its attribute dictionary.
        - Falls back to the base encoder otherwise.
        """
        if o is Undefined:
            return None
        elif isinstance(o, Object):
            return unjsify(o)
        elif isinstance(o, SimpleNamespace):
            return o.__dict__
        else:
            return super().default(o)


def jsified_dumps(o, *args, omit_undefined=True, **kwargs):
    """
    Serialize an object as a JSON string using ObjectEncoder.

    Handles jsified objects and omits `Undefined` values if specified.
    All nested structures are unjsified recursively and can be filtered.

    Parameters
    ----------
    o : Any
        The object to serialize.
    *args
        Additional positional arguments passed to `json.dumps`.
    omit_undefined : bool, optional
        Whether to omit `Undefined` values (default: True).
    **kwargs
        Additional keyword arguments passed to `json.dumps`.

    Returns
    -------
    str
        The JSON-formatted string.
    """
    return json.dumps(o, *args, cls=ObjectEncoder, omit_undefined=omit_undefined, **kwargs)


def jsified_dump(o, *args, omit_undefined=True, **kwargs):
    """
    Serialize an object as JSON and write it to a file using ObjectEncoder.

    Handles jsified objects and omits `Undefined` values if specified.
    All nested structures are unjsified recursively and can be filtered.

    Parameters
    ----------
    o : Any
        The object to serialize.
    *args
        Additional positional arguments passed to `json.dump`.
    omit_undefined : bool, optional
        Whether to omit `Undefined` values (default: True).
    **kwargs
        Additional keyword arguments passed to `json.dump`.

    Returns
    -------
    None
    """
    return json.dump(o, *args, cls=ObjectEncoder, omit_undefined=omit_undefined, **kwargs)
