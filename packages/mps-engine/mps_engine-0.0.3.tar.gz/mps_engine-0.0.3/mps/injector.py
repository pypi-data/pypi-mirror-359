"""Pattern injector module."""

from copy import deepcopy
from typing import Any, Protocol, TypeVar

from jinja2 import Template


class Injectable(Protocol):
    """Protocol defining any kind of object that contains a content able to inject in."""

    content: str


T = TypeVar("T", bound=Injectable)


def inject(miniature: T, **vars: str) -> T:
    """Inject values into variables defined in a markdown file.

    Variables are annotated by double curly brackets {{}} inside markdown file.


    Args:
        miniature: the injectable miniature containing {{}} notations to inject
        vars: the values to inject into variables {{}}
        inplace:
            whether or not to override the miniature content with the newly injected
            variables
    Note:
        inject does not support inplace update and auto miniature variables dictionary
        update, use the object oriented interface instead (Pattern(...).inject()).

    """
    # FIXME: stopped working properly injects None at placeholders same goes for
    # variables attribute in a miniature. When _inplace is set to False
    return _inject(miniature, "content", _inplace=True, **vars)


def _inject(
    _obj: Any, _key: str = "content", _inplace: bool = False, **vars: str
) -> Any:
    """Inject into an object value retrived by key_ as string template.

    Note:
    Paramaters prefixed for safety reason in case a template variable was named 'key'
    or 'obj' or 'inplace' this could cause conflicts...

    """
    if not _inplace:
        _obj = deepcopy(_obj)
    template = Template(getattr(_obj, _key))
    rendered = template.render(**vars)
    setattr(_obj, _key, rendered)
    return _obj
