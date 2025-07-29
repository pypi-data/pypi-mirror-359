from typing import Any, Iterator as Iter, Tuple as Tup


class Object:
    """
    Jsify wrapper for Python objects providing JavaScript-like attribute and item access.

    This class encapsulates Python objects, enabling attribute and indexing operations typical in JavaScript.
    """

    def __init__(self, orig: Any):
        """
        Initialize an Object instance by wrapping the given Python object.

        Parameters
        ----------
        orig : Any
            The Python object to be wrapped.

        Notes
        -----
        - The `orig` parameter is stored directly and accessed via Jsify wrapper methods.
        """


class Dict(Object):
    """
    Jsify wrapper specifically for Python dictionaries enabling JavaScript-like attribute access.

    Extends the general `Object` wrapper to specialize behavior for dictionary objects, allowing
    direct attribute-style access to dictionary keys.

    Parameters
    ----------
    orig : dict
        The Python dictionary to be wrapped.
    """

    def __init__(self, orig: dict):
        """
        Initialize a Dict instance by wrapping a Python dictionary.

        Parameters
        ----------
        orig : dict
            The Python dictionary to wrap.

        Raises
        ------
        TypeError
            If `orig` is not a dictionary.

        Notes
        -----
        - Stores the dictionary directly for attribute and item-based access.
        """


class Tuple(Object):
    """
    Jsify wrapper specifically for Python tuples enabling JavaScript-like attribute access.

    Extends the general `Object` wrapper to specialize behavior for tuple objects, providing
    attribute and indexing operations.

    Parameters
    ----------
    orig : tuple
        The Python tuple to be wrapped.

    Methods
    -------
    count(value)
        Return the number of occurrences of `value`.
    index(value)
        Return the first index of `value`.

    """

    def __init__(self, orig: tuple):
        """
        Initialize a Tuple instance by wrapping a Python tuple.

        Parameters
        ----------
        orig : tuple
            The Python tuple to wrap.

        Raises
        ------
        TypeError
            If `orig` is not a tuple.

        Notes
        -----
        - Stores the tuple directly for attribute and item-based access.
        """

    def count(self, value: Any) -> int:
        """
        Return the number of occurrences of `value` in the tuple.

        Parameters
        ----------
        value : Any
            The value to count occurrences of.

        Returns
        -------
        int
            Number of occurrences of `value`.
        """

    def index(self, value: Any) -> int:
        """
        Return the first index of `value` in the tuple.

        Parameters
        ----------
        value : Any
            The value to find the index of.

        Returns
        -------
        int
            Index of the first occurrence of `value`.

        Raises
        ------
        ValueError
            If `value` is not found in the tuple.
        """


class List(Object):
    """
    Jsify wrapper for Python lists enabling JavaScript-like attribute access and manipulation.

    Extends the general `Object` wrapper to specialize behavior for list objects, providing
    attribute and indexing operations.

    Methods
    -------
    append(obj: Any) -> None
        Append an object to the list.
    clear() -> None
        Remove all items from the list.
    count(value: Any) -> int
        Return the number of occurrences of `value`.
    extend(iterable: Any) -> None
        Extend the list by appending elements from an iterable.
    index(value: Any) -> int
        Return the first index of `value`.
    insert(index: int, obj: Any) -> None
        Insert an object at a given position.
    pop(index: int = -1) -> Any
        Remove and return item at `index` (default last).
    remove(value: Any) -> None
        Remove the first occurrence of `value`.
    reverse() -> None
        Reverse the list in place.
    sort(*, key: Any = None, reverse: bool = False) -> None
        Sort the list in place.
    """

    def __init__(self, orig: list):
        """
        Initialize a List instance.

        Parameters
        ----------
        orig : list
            The Python list to wrap.

        Raises
        ------
        TypeError
            If `orig` is not a list.
        """

    def append(self, obj: Any) -> None:
        """
        Append an object to the list.

        Parameters
        ----------
        obj : Any
            The object to append.
        """

    def clear(self) -> None:
        """
        Remove all items from the list.
        """

    def count(self, value: Any) -> int:
        """
        Return the number of occurrences of `value`.

        Parameters
        ----------
        value : Any
            The value to count.

        Returns
        -------
        int
            Number of occurrences of `value`.
        """

    def extend(self, iterable: Any) -> None:
        """
        Extend the list by appending elements from an iterable.

        Parameters
        ----------
        iterable : Any
            The iterable of elements to append.
        """

    def index(self, value: Any) -> int:
        """
        Return the first index of `value`.

        Parameters
        ----------
        value : Any
            The value to find.

        Returns
        -------
        int
            Index of the first occurrence of `value`.

        Raises
        ------
        ValueError
            If `value` is not found in the list.
        """

    def insert(self, index: int, obj: Any) -> None:
        """
        Insert an object at a given position.

        Parameters
        ----------
        index : int
            Position at which to insert.
        obj : Any
            The object to insert.
        """

    def pop(self, index: int = -1) -> Any:
        """
        Remove and return item at `index` (default last).

        Parameters
        ----------
        index : int, optional
            The index of the item to remove (default is last).

        Returns
        -------
        Any
            The removed item.

        Raises
        ------
        IndexError
            If the list is empty or index is out of range.
        """

    def remove(self, value: Any) -> None:
        """
        Remove the first occurrence of `value`.

        Parameters
        ----------
        value : Any
            The value to remove.

        Raises
        ------
        ValueError
            If `value` is not found in the list.
        """

    def reverse(self) -> None:
        """
        Reverse the list in place.
        """

    def sort(self, *, key: Any = None, reverse: bool = False) -> None:
        """
        Sort the list in place.

        Parameters
        ----------
        key : Any, optional
            Function of one argument that is used to extract a comparison key (default is None).
        reverse : bool, optional
            If True, the list elements are sorted as if each comparison were reversed (default is False).
        """


class Iterator(Object):
    """
    Jsify wrapper for Python iterators enabling JavaScript-like iteration semantics.

    Extends the general `Object` wrapper to specialize behavior for iterator objects, providing
    support for use in Python and JavaScript-like iteration contexts.

    Methods
    -------
    __iter__() -> Iterator
        Return the iterator itself.
    __next__() -> Any
        Return the next item from the iterator.
    """

    def __init__(self, orig: Any):
        """
        Initialize an Iterator instance.

        Parameters
        ----------
        orig : Any
            The Python iterator to wrap.

        Raises
        ------
        TypeError
            If `orig` is not an iterator.
        """


class Undefined(Object):
    """
    Singleton jsify wrapper representing JavaScript-like 'undefined'.

    Extends the general `Object` wrapper to provide a singleton that behaves like JavaScript's
    `undefined` value. This object is returned for missing attributes or items, evaluates as
    `False` in boolean context, and compares equal to `None` or itself.

    Notes
    -----
    - All attribute or item access on this object returns itself.
    - Used to explicitly indicate the absence of a value in jsified structures.
    """

    def __init__(self):
        """
        Initialize the Undefined singleton.

        Notes
        -----
        - Instantiation is restricted; the singleton instance is provided by the library.
        """


Undefined: Undefined


def jsify(obj: Any) -> Any:
    """
    Wrap a Python object in a Jsify-compatible wrapper for JavaScript-like behavior.

    Conditionally wraps built-in types (`dict`, `list`, `tuple`, iterators) into Jsify wrappers (`Dict`, `List`, `Tuple`, `Iterator`).
    Primitive types (`None`, numeric types, `str`, `bool`) and already-wrapped types (`Object`, `Undefined`) are returned unchanged.

    Parameters
    ----------
    obj : Any
        The Python object to wrap.

    Returns
    -------
    Any
        Jsify-wrapped object or the original object if wrapping is unnecessary.

    Raises
    ------
    TypeError
        If the object type is unsupported.

    Notes
    -----
    - Returned object is a new reference; caller must manage reference count.
    - Returns `Py_None` as a new reference if input is `NULL`.

    See Also
    --------
    unjsify : Convert Jsify-wrapped object back to original Python object.
    """


def unjsify(obj: Any) -> Any:
    """
    Convert a Jsify-wrapped object to its original Python representation.

    If the input is a jsified Object, Dict, List, Tuple, or Iterator, returns the original wrapped Python object.
    For primitive types and objects not wrapped by Jsify, returns the object unchanged. For the singleton
    Undefined, returns the singleton itself.

    Parameters
    ----------
    obj : Any
        The object to convert.

    Returns
    -------
    Any
        The original Python object if the input was jsified; otherwise, the input itself.

    Notes
    -----
    - Always returns a new reference to the result.
    - If the input is Undefined, returns the singleton Undefined.
    - No effect on primitive types (int, float, str, bool, None).
    """


def jsified_copy(obj: Any) -> Any:
    """
    Create a shallow copy of the original Python object and wrap it as a jsified object.

    Calls Python's standard `copy.copy()` on the unjsified version of `obj`, then wraps the result in the appropriate
    jsified wrapper. The copy is shallow: for containers, contained objects are not copied recursively.

    Parameters
    ----------
    obj : Any
        The object to copy (can be jsified or plain Python object).

    Returns
    -------
    Any
        A jsified shallow copy of the object.

    Raises
    ------
    TypeError
        If the object type does not support shallow copying.

    Notes
    -----
    - If the input is already a jsified object, its underlying original object is copied and re-wrapped.
    - If the input is a primitive type, the value is simply returned (since primitives are immutable).
    """


def jsified_deepcopy(obj: Any) -> Any:
    """
    Create a deep copy of the original Python object and wrap it as a jsified object.

    Calls Python's standard `copy.deepcopy()` on the unjsified version of `obj`, then wraps the result in the appropriate
    jsified wrapper. All contained objects are recursively copied.

    Parameters
    ----------
    obj : Any
        The object to deepcopy (can be jsified or plain Python object).

    Returns
    -------
    Any
        A jsified deep copy of the object.

    Raises
    ------
    TypeError
        If the object type does not support deep copying.

    Notes
    -----
    - If the input is already a jsified object, its underlying original object is deeply copied and re-wrapped.
    - If the input is a primitive type, the value is simply returned (since primitives are immutable).
    """


def jsified_get(obj: Any, key: Any, default: Any = None) -> Any:
    """
    Retrieve a value from a jsified dictionary-like object by key, returning a jsified result.

    If the object is jsified or a plain dictionary, attempts to retrieve the value for `key`. If the key
    does not exist, returns `default`. The result is always wrapped as a jsified object (or returned as-is for primitives).

    Parameters
    ----------
    obj : Any
        The jsified or plain dictionary object.
    key : Any
        The key to look up.
    default : Any, optional
        Value to return if the key does not exist (default: None).

    Returns
    -------
    Any
        The value corresponding to `key`, jsified; or the default if not found.

    Raises
    ------
    TypeError
        If `obj` is not a dictionary or jsified dictionary-like object.

    Notes
    -----
    - The result is always returned as a jsified object (unless it's a primitive type).
    """


def jsified_pop(obj: Any, key: Any, default: Any = None) -> Any:
    """
    Remove the specified key from a jsified dictionary-like object and return its value as a jsified object.

    If the key exists, its value is removed and returned. If the key does not exist, returns `default` if provided,
    otherwise raises a `KeyError`. The result is always wrapped as a jsified object (unless it is a primitive type).

    Parameters
    ----------
    obj : Any
        The jsified or plain dictionary object.
    key : Any
        The key to remove and return.
    default : Any, optional
        Value to return if the key does not exist (default: None).

    Returns
    -------
    Any
        The removed value, jsified; or the default if the key is not found.

    Raises
    ------
    TypeError
        If `obj` is not a dictionary or jsified dictionary-like object.
    KeyError
        If the key is not found and no default is provided.

    Notes
    -----
    - The result is always returned as a jsified object (unless it's a primitive type).
    - Removes the item from the underlying dictionary.
    """


def jsified_popitem(obj: Any) -> Any:
    """
    Remove and return an arbitrary key-value pair from a jsified dictionary-like object, as a jsified tuple.

    Removes and returns the last inserted (key, value) pair in Python 3.7+ (arbitrary pair in earlier versions).
    The result is always wrapped as a jsified tuple. Raises `KeyError` if the dictionary is empty.

    Parameters
    ----------
    obj : Any
        The jsified or plain dictionary object.

    Returns
    -------
    Any
        The removed (key, value) pair as a jsified tuple.

    Raises
    ------
    TypeError
        If `obj` is not a dictionary or jsified dictionary-like object.
    KeyError
        If the dictionary is empty.

    Notes
    -----
    - The result is always returned as a jsified tuple.
    - Removes the item from the underlying dictionary.
    """


def jsified_setdefault(obj: Any, key: Any, default: Any) -> Any:
    """
    If the key is in the jsified dictionary-like object, return its value (jsified). If not, insert key with a value of
    default and return default (jsified).

    Equivalent to dict.setdefault, but always returns a jsified object. If the key is missing, the default value is
    inserted and returned.

    Parameters
    ----------
    obj : Any
        The jsified or plain dictionary object.
    key : Any
        The key to search for or insert.
    default : Any
        The value to set and return if the key is not present.

    Returns
    -------
    Any
        The value for the key (existing or newly set), as a jsified object.

    Raises
    ------
    TypeError
        If `obj` is not a dictionary or jsified dictionary-like object.

    Notes
    -----
    - Always returns a jsified object (unless the value is a primitive type).
    - May insert a new key-value pair into the underlying dictionary.
    """


def jsified_update(obj: Any, update: Any) -> None:
    """
    Update a jsified dictionary-like object with the key-value pairs from another mapping or iterable.

    Equivalent to dict.update(). The source can be another dictionary or any iterable of key-value pairs.
    Modifies the dictionary in place.

    Parameters
    ----------
    obj : Any
        The jsified or plain dictionary object to update.
    update : Any
        A mapping or iterable of key-value pairs.

    Returns
    -------
    None
        This function returns None.

    Raises
    ------
    TypeError
        If `obj` is not a dictionary or jsified dictionary-like object.
        If `update` is not a mapping or iterable of key-value pairs.

    Notes
    -----
    - Modifies the underlying dictionary directly.
    """



def jsified_values(obj: Any) -> Any:
    """
    Return a jsified list of all values from a jsified dictionary-like object.

    Equivalent to dict.values(), but returns a jsified list of the values.

    Parameters
    ----------
    obj : Any
        The jsified or plain dictionary object.

    Returns
    -------
    Any
        A jsified list of all values in the dictionary.

    Raises
    ------
    TypeError
        If `obj` is not a dictionary or jsified dictionary-like object.

    Notes
    -----
    - The result is always a jsified list.
    """


def jsified_keys(obj: Any) -> Any:
    """
    Return a jsified list of all keys from a jsified dictionary-like object.

    Equivalent to dict.keys(), but returns a jsified list of the keys.

    Parameters
    ----------
    obj : Any
        The jsified or plain dictionary object.

    Returns
    -------
    Any
        A jsified list of all keys in the dictionary.

    Raises
    ------
    TypeError
        If `obj` is not a dictionary or jsified dictionary-like object.

    Notes
    -----
    - The result is always a jsified list.
    """


def jsified_items(obj: Any) -> Any:
    """
    Return a jsified list of all key-value pairs from a jsified dictionary-like object.

    Equivalent to dict.items(), but returns a jsified list of (key, value) pairs.

    Parameters
    ----------
    obj : Any
        The jsified or plain dictionary object.

    Returns
    -------
    Any
        A jsified list of (key, value) pairs in the dictionary.

    Raises
    ------
    TypeError
        If `obj` is not a dictionary or jsified dictionary-like object.

    Notes
    -----
    - The result is always a jsified list of pairs.
    """

def unjsify_deepcopy(obj: Any) -> Any:
    """
    Recursively convert a jsified object into a pure Python structure, performing a deep copy.

    Traverses jsified (and plain) dictionaries, lists, tuples, and iterators recursively, producing
    a deep-copied structure of built-in Python types. For primitive types and Undefined, returns the object as-is.

    Parameters
    ----------
    obj : Any
        The jsified or plain Python object to deepcopy and convert.

    Returns
    -------
    Any
        A pure Python deep-copied object, with all nested jsified containers and values unwrapped.

    Notes
    -----
    - All containers are recursively traversed and copied.
    - Primitives and Undefined are not copied, only their reference is returned.
    - For unknown or unsupported types, the input object is returned unchanged.
    """
