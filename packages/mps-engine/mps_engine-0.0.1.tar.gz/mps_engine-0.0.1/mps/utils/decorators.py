from collections.abc import Callable
from functools import partial, wraps


def future(
    func: Callable | None = None, *, message: str | None = None, verbose: bool = True
) -> Callable:
    if not func:
        return partial(future, message=message)

    if not message:
        message = f"{func.__module__}:{func.__name__} is planned for a future release"
    if verbose:
        message += (
            "\nFollow our GitHub repository for updates on when this feature will be "
            "available: https://github.com/mghalix/mps"
        )

    @wraps(func)
    def wrapper(*args, **kwargs):
        raise NotImplementedError(message)

    return wrapper
