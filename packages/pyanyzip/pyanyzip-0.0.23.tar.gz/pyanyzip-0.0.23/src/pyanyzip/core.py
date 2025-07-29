"""
Core functionality of pyanyzip
"""

import bz2

from pypipegzip import pypipegzip


methods = {
    "magic",
    "suffix",
}

zip_types = {
    "plain",
    "gzip",
    "bz2",
    "xz",
}


def _get_type(name, method):
    if method == 'suffix':
        if name.endswith('.gz'):
            return 'gzip'
        if name.endswith('.bz2'):
            return 'bz2'
        if name.endswith('.xz'):
            return 'xz'
        return 'plain'
    if method == 'magic':
        raise ValueError("magic is still not implemented")
    raise ValueError("method not supported")


def openzip(name: str, mode: str, method: str = 'suffix', zip_type: str | None = None,
            newline: str | None = None):
    assert method in methods
    if zip_type is None:
        zip_type = _get_type(name, method)
    else:
        assert zip_type in zip_types
    if zip_type == 'plain':
        # pylint: disable=consider-using-with
        return open(name, mode=mode, newline=newline)
    if type == "gzip":
        return pypipegzip.zipopen(filename=name, mode=mode, newline=newline)
    if type == "bzip2":
        return bz2.open(filename=name, mode=mode, newline=newline)
    raise ValueError("You should not be here")
