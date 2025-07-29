from types import SimpleNamespace
from json import load, loads, JSONEncoder, dump, dumps
from .cjsify import Undefined

class SimplifiedObject(SimpleNamespace):
    """
    An extension of SimpleNamespace that mimics JavaScript-like property access.

    This class behaves like a dynamic object whose attributes can be set and retrieved.
    If an attribute is accessed that does not exist, it returns the singleton `Undefined`
    object instead of raising an `AttributeError`. This enables safe chaining of attribute
    access in deeply nested structures, similar to how missing properties return `undefined`
    in JavaScript.

    When a dictionary is deserialized into a SimplifiedObject, its keys become attributes.
    Any missing attribute will yield `Undefined`.

    Attributes
    ----------
    <dynamic> : Any
        All fields are dynamically set as attributes. Missing fields yield `Undefined`.

    See Also
    --------
    jsify.cjsify.Undefined : The singleton returned for missing attributes.
    """

    def __getattr__(self, item):
        """
        Return the `Undefined` singleton for any missing attribute.

        Parameters
        ----------
        item : str
            The attribute name.

        Returns
        -------
        Any
            The value of the attribute if it exists, or `Undefined` if not.
        """
        return Undefined


class SimplifiedEncoder(JSONEncoder):
    """
    JSON encoder for structures containing SimplifiedObject and Undefined.

    This encoder customizes JSON serialization for types relevant to the
    simplified object pattern:
      - The `Undefined` singleton is encoded as `null` in JSON.
      - Any instance of `SimplifiedObject` is serialized as a JSON object using
        its internal attribute dictionary.
      - Other types are handled by the standard JSONEncoder.

    This allows Python objects using this pattern to be safely and predictably
    encoded to JSON for interoperability or storage.

    Parameters
    ----------
    skipkeys : bool, optional
        Skip keys not of a basic type if True.
    ensure_ascii : bool, optional
        Escape all non-ASCII characters if True.
    check_circular : bool, optional
        Check for circular references if True.
    allow_nan : bool, optional
        Allow NaN and Infinity values if True.
    sort_keys : bool, optional
        Sort output dictionary keys if True.
    indent : int or str, optional
        Indentation level for pretty-printing.
    """

    def default(self, obj):
        """
        Return a serializable form of `SimplifiedObject` or `Undefined`.

        - If `obj` is `Undefined`, return None (serialized as `null` in JSON).
        - If `obj` is a `SimplifiedObject`, serialize using its `__dict__`.
        - Otherwise, use the standard JSONEncoder behavior.

        Parameters
        ----------
        obj : Any
            The object to serialize.

        Returns
        -------
        Any
            JSON-serializable representation of `obj`.
        """
        if obj is Undefined:
            return None
        if isinstance(obj, SimplifiedObject):
            return obj.__dict__
        return super().default(obj)


def simplified_dumps(obj, **kwargs):
    """
    Serialize an object as a JSON string using the SimplifiedEncoder.

    This function provides JSON serialization for objects that may contain
    `SimplifiedObject` and `Undefined` values. The encoder ensures that `Undefined`
    is represented as `null` and all `SimplifiedObject` instances are serialized
    as JSON objects. Additional keyword arguments are passed to `json.dumps`.

    Parameters
    ----------
    obj : Any
        The object to serialize to JSON.
    **kwargs
        Any additional keyword arguments for `json.dumps`.

    Returns
    -------
    str
        JSON-formatted string representing the object.
    """
    return dumps(obj, cls=SimplifiedEncoder, **kwargs)


def simplified_dump(fp, obj, **kwargs):
    """
    Serialize an object as JSON and write it to a file using SimplifiedEncoder.

    This function writes the JSON serialization of an object to a file or file-like
    object, using the same rules as `simplified_dumps`. It handles `Undefined` as `null`
    and serializes `SimplifiedObject` instances as objects.

    Parameters
    ----------
    fp : typing.IO[str]
        File or file-like object to write the JSON output to.
    obj : Any
        The object to serialize.
    **kwargs
        Any additional keyword arguments for `json.dump`.

    Returns
    -------
    None
    """
    return dump(fp, obj, cls=SimplifiedEncoder, **kwargs)


def object_hook_convert_to_simple(obj):
    """
    Object hook for JSON deserialization to convert dicts to SimplifiedObject.

    When used as the `object_hook` in `json.load` or `json.loads`, this function
    replaces every dictionary with a `SimplifiedObject`, so that all fields can
    be accessed as attributes and any missing attribute access will yield `Undefined`.

    Parameters
    ----------
    obj : dict
        The dictionary object parsed from JSON.

    Returns
    -------
    SimplifiedObject
        The dictionary converted to a SimplifiedObject.
    """
    if isinstance(obj, dict):
        return SimplifiedObject(**obj)


def load_simplified(fp, *args, **kwargs):
    """
    Load JSON from a file and produce a structure of SimplifiedObject instances.

    This function behaves like `json.load`, but ensures that every dictionary in the
    resulting object tree is converted to a `SimplifiedObject`. Attribute access is
    available throughout, and missing attributes yield `Undefined`.

    Parameters
    ----------
    fp : typing.IO[str]
        File or file-like object to read JSON from.
    *args
        Additional positional arguments to `json.load`.
    **kwargs
        Additional keyword arguments to `json.load`.

    Returns
    -------
    Any
        The parsed and converted JSON object structure.
    """
    return load(fp, *args, object_hook=object_hook_convert_to_simple, **kwargs)


def loads_simplified(s, *args, **kwargs):
    """
    Load JSON from a string and produce a structure of SimplifiedObject instances.

    This function behaves like `json.loads`, but ensures that every dictionary in the
    resulting object tree is converted to a `SimplifiedObject`. All fields are accessible
    as attributes, and missing fields yield `Undefined`.

    Parameters
    ----------
    s : str
        JSON string to parse.
    *args
        Additional positional arguments to `json.loads`.
    **kwargs
        Additional keyword arguments to `json.loads`.

    Returns
    -------
    Any
        The parsed and converted JSON object structure.
    """
    return loads(s, *args, object_hook=object_hook_convert_to_simple, **kwargs)
