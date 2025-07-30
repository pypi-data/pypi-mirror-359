from collections.abc import MutableMapping
from copy import deepcopy
from pathlib import Path
from typing import Any, Self

from loguru import logger
from pydantic import BaseModel, Field, model_validator


class _HasVariablesMixin(BaseModel):
    variables: MutableMapping[str, Any] = Field(default_factory=dict, alias="vars")

    def _extract_vars(self, from_: str) -> dict[str, None]:
        def _preprocess(s: str) -> str:
            s = s.strip()
            stop_chars = (".", "!", "?")
            for c in stop_chars:
                s = s.rstrip(c)
            return s

        def _is_var(s: str) -> bool:
            return s.startswith("{{") and s.endswith("}}")

        def _extract_var(template_str: str) -> str:
            return template_str.strip("{{").rstrip("}}").strip()  # noqa

        content_parts: list[str] = from_.split()
        return dict.fromkeys(
            {
                _extract_var(p)
                for part in content_parts
                if _is_var(p := _preprocess(part))
            }
        )

    def __setitem__(self, key: Any, value: Any, /) -> None:
        self.variables.__setitem__(key, value)

    def __getitem__(self, key: Any, /) -> Any:
        return self.variables.__getitem__(key)

    def inject(self, strict: bool = False, **vars: Any) -> Self:
        """Inject variables into miniature content that has variable placeholders.

        Args:
            strict:
                if set to true, throws an error if the passed variables are not part of
                the loaded miniature. Defaults to False.
            vars: the variables to inject into miniature content



        Raises:
            ValueError:
                if strict is set to True, and there exists no placeholder inside the
                miniature content that matches the passed variable

        Returns:
            The miniature with the injected variables.

        """
        err = (
            "variable '{}' does not exist, skipping injection... available variables {}"
        )
        for k, v in vars.items():
            if k not in self.variables:
                msg = err.format(k, tuple(self.variables.keys()))
                if strict:
                    raise ValueError(msg)

                logger.warning(msg)
                continue
            self.__setitem__(k, v)
        return self


class _HasVariablesMixinCallbacks(BaseModel):
    _auto_populate_vars: bool
    """Auto populate variables dictionary from content with default None values."""
    _auto_sync_vars_on_update: bool
    """Auto update the content by injecting the updated value in variables."""

    def __init__(self, /, **data: Any) -> None:
        super().__init__(**data)
        if self._auto_populate_vars is True:
            self._auto_populate()
        if self._auto_sync_vars_on_update is True:
            self._add_on_update_callback()

    def __new__(cls, *args: Any, **kwargs: Any) -> Self:
        required_parents = (_HasVariablesMixinCallbacks, _HasContentMixin)
        if not issubclass(cls, required_parents):
            raise TypeError(
                f"{cls.__name__} must be used only when it inherits from "
                f"{tuple(required_parents)}"
            )
        return super().__new__(cls)

    def _auto_populate(self) -> bool:
        def _prepoulate_validator() -> None:
            assert hasattr(self, "variables"), (
                "To start auto populating, an attribute 'variables' must be a part of "
                f"class {self.__class__.__name__}"
            )

        try:
            _prepoulate_validator()
        except AssertionError as e:
            logger.error(e)
            return False

        self.variables = self._extract_vars(self.content)  # type: ignore
        return True

    def _add_on_update_callback(self) -> bool:
        from mps.utils.dicttools import CallbackDict

        self.variables: MutableMapping

        def on_var_update(key: Any, value: Any) -> None:
            from .injector import _inject

            _inject(self, _inplace=True, **{key: value})

        callback_dict = CallbackDict(callback=on_var_update)
        callback_dict.update(self.variables)

        self.variables = callback_dict
        return True


class _HasContentMixin(BaseModel):
    content: str

    def __str__(self) -> str:
        return self.content

    def __or__(self, other: Any, /) -> Any:
        new = deepcopy(self)
        new.content += "\n" + str(other)
        return new


class _ContentAndVarsMixin(_HasContentMixin, _HasVariablesMixin): ...


class _ContentAndAutoVarsMixin(_ContentAndVarsMixin, _HasVariablesMixinCallbacks):
    _auto_populate_vars: bool = True
    _auto_sync_vars_on_update: bool = True


class _BaseMpsComponent(BaseModel):
    name: str | None = None
    description: str | None = None
    source_path: Path | None = None

    @model_validator(mode="after")
    def _auto_set_name(self) -> Self:
        from mps.utils.miniatures import get_miniature_name_from_path

        if self.source_path:
            self.name = str(get_miniature_name_from_path(self.source_path))
        return self


class _BaseMpsExtensionComponent(_BaseMpsComponent): ...
