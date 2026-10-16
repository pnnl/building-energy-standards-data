import logging, os


class OpenStudioStandardsDataException(Exception):
    def __init__(self, message):
        super().__init__(message)


class OpenStudioStandardsFormDataException(OpenStudioStandardsDataException):
    def __init__(self, message):
        super().__init__(message)


def assert_(b: bool, err_msg: str) -> None:
    """Assert a condition and raise an exception if false.

    Args:
        b: Boolean condition to assert.
        err_msg: Error message to include in the exception if condition is False.

    Raises:
        OpenStudioStandardsFormDataException: If condition is False.
    """
    if not b:
        logging.getLogger("debug")
        raise OpenStudioStandardsFormDataException(err_msg)


class MissingKeyException(OpenStudioStandardsDataException):
    def __init__(self, object_name, first_key):
        message = f"{object_name} is missing {'one of the fields in: ' if isinstance(first_key, list) else ''}{first_key}"
        super().__init__(message)


class PathNotFound(OpenStudioStandardsDataException):
    def __init__(self, path):
        message = f"The path {path} cannot be found"
        super().__init__(message)


def check_path(path: str) -> bool:
    """Verify that a path exists.

    Args:
        path: String representing the path to a directory.

    Returns:
        True if the path is valid.

    Raises:
        PathNotFound: If the path does not exist or is None.
    """
    if path is None:
        raise PathNotFound(path)
    if not os.path.exists(path):
        raise PathNotFound(path)
    return True


def getattr_(obj, obj_name: str, first_key, *remaining_keys):
    """Retrieve a value from a nested dictionary structure using a key path.

    Navigates through a potentially nested dictionary structure using a key path.
    At each level, the dictionary is assumed to have an id field.

    Args:
        obj: A potentially nested dictionary structure to search.
        obj_name: Name of the object being searched (used in error messages).
        first_key: The first key in the path.
        remaining_keys: Additional keys in the path.

    Returns:
        The value stored at the given key path.

    Raises:
        AssertionError: If obj is None.
        MissingKeyException: If any key in the path does not exist.
    """
    assert_(
        obj is not None,
        f"Object: {obj_name} provided is None, failed to search for key: {first_key}",
    )

    if first_key not in obj:
        raise MissingKeyException(obj_name, first_key)
    val = obj[first_key]

    return (
        val
        if len(remaining_keys) == 0
        else getattr_(val, first_key, remaining_keys[0], *remaining_keys[1:])
    )
