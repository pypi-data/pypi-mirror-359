"""All MPS core and extension components models i.e., miniatures models."""

import json
from collections.abc import MutableMapping, Sequence
from copy import copy
from dataclasses import asdict, dataclass
from enum import StrEnum, auto
from functools import singledispatchmethod
from pathlib import Path
from typing import Annotated, Any, Self

from caseconverter import kebabcase
from loguru import logger
from pydantic import (
    AfterValidator,
    AliasChoices,
    AnyUrl,
    BaseModel,
    Field,
    ValidationError,
    field_validator,
    model_validator,
)

from mps._typing import PathLike
from mps.core.constants import EXTENSION_PREFIX
from mps.core.errors import MiniatureNotFoundError
from mps.utils.decorators import future

from ._base import (
    _BaseMpsComponent,
    _BaseMpsExtensionComponent,
    _ContentAndAutoVarsMixin,
    _HasContentMixin,
)


class MiniatureCommand:
    """Instruction of command."""

    name: Annotated[str, "The command file name"]
    cmd: Annotated[str | None, "The content/instructions of a command"] = None


class MiniatureName(BaseModel):
    """The name of a miniature."""

    name: Annotated[str | Self, AfterValidator(lambda x: kebabcase(str(x).lower()))]

    def __str__(self) -> str:
        """Get miniature name in string format."""
        return str(self.name)


class MiniatureKind(StrEnum):
    """Miniature kinds."""

    CONTEXT = auto()
    META = auto()
    PATTERN = auto()
    STRATEGY = auto()
    PREFERENCE = auto()
    CONFIGURATION = auto()

    @classmethod
    def iterable(cls) -> Sequence[str]:
        """Enable iterating over miniature kinds."""
        return tuple(mini.value for mini in cls)

    @classmethod
    def extensions(cls) -> Sequence[str]:
        """All miniatures that are considered an extension of the MPS architecture."""
        return (
            cls.PREFERENCE,
            cls.CONFIGURATION,
            cls.CONTEXT,
        )


class Meta(_BaseMpsComponent, _HasContentMixin):
    """Meta miniature for constructing new patterns with LLM assistance."""


class Pattern(_BaseMpsComponent, _ContentAndAutoVarsMixin):
    """Pattern miniature for providing the LLM a persona and instructions."""


class Strategy(_BaseMpsComponent):
    """Strategy miniature for telling the LLM how to use patterns."""

    prompt: str = Field(validation_alias=AliasChoices("content"))

    def __str__(self) -> str:
        """Core usage of a strategy is its prompt field."""
        return self.prompt

    def __add__(self, other: Any, /) -> Any:
        return self.prompt + other

    def __or__(self, other: Any, /) -> Any:
        """Add other miniatures to strategy by using the pipe operator."""
        new = copy(self)
        new.prompt += "\n\n" + str(other)
        return new


class Context(_BaseMpsExtensionComponent, _HasContentMixin):
    """Context miniature is used for providing the LLM with more context."""


class Preference(_BaseMpsExtensionComponent, _ContentAndAutoVarsMixin):
    """Preference is a special kind of pattern that does not require a schema.

    Used when you need to provide the LLM a more specific customization of its output
    such as a programming-language preference could instruct the LLM to always use
    'python' as an example in its responses.
    """


class Configuration(_BaseMpsExtensionComponent, _HasContentMixin):
    """Configuration is used to set the LLM execution settings."""

    temperature: int | None = None
    max_tokens: int | None = None
    top_p: int | None = None
    top_k: int | None = None
    stop_sequence: str | None = None
    seed: int | None = None
    frequency_penalty: int | None = None
    message: str | None = None

    @model_validator(mode="after")
    def parse_configs(self) -> Self:
        """Populate class fields from the configuration file content."""
        if not self.content:
            return self

        try:
            data = json.loads(self.content)
            for k, v in data.items():
                if not hasattr(self, k):
                    continue

                setattr(self, k, v)
        except json.JSONDecodeError:
            pass

        return self


class Mps(BaseModel):
    """Meta Pattern Strategy Architecture and its Extensions."""

    meta: MutableMapping[str, Meta]
    pattern: MutableMapping[str, Pattern]
    strategy: MutableMapping[str, Strategy]
    context: MutableMapping[str, Context]
    preference: MutableMapping[str, Preference]
    configuration: MutableMapping[str, Configuration]

    @future
    @classmethod
    def from_directory(cls, directory: PathLike) -> "Mps":
        """Populate Mps object with all its component from a local directory."""
        from mps.loader import _load

        return _load(directory)


@dataclass
class MpsLocator:
    """Dynamic placeholder for MPS structure."""

    base_dir: str
    meta_dir: str
    pattern_dir: str
    strategy_dir: str


class MpsHierarchy(BaseModel):
    """Defines and valides the adherence of MPS architecture standards."""

    # Set defaults here
    base_dir: PathLike | None = None
    meta_dir: PathLike | None = None
    pattern_dir: PathLike | None = None
    strategy_dir: PathLike | None = None

    @model_validator(mode="after")
    def validate_hierarchy(self) -> Self:
        """Validate the MPS structure using current config."""
        from mps import get_config

        config = get_config()

        # set any None values to config defaults
        if self.base_dir is None:
            self.base_dir = config.base_dir
        if self.meta_dir is None:
            self.meta_dir = config.meta_dir
        if self.pattern_dir is None:
            self.pattern_dir = config.pattern_dir
        if self.strategy_dir is None:
            self.strategy_dir = config.strategy_dir

        # convert all to Path objects
        self.base_dir = Path(self.base_dir)
        self.meta_dir = Path(self.meta_dir)
        self.pattern_dir = Path(self.pattern_dir)
        self.strategy_dir = Path(self.strategy_dir)

        return self

    @singledispatchmethod
    @classmethod
    def from_locator(cls, location: MutableMapping | MpsLocator) -> Self:
        """Get the hierarchy from dictionaries / any locator."""
        raise NotImplementedError

    @from_locator.register
    @classmethod
    def _(cls, location: MutableMapping) -> Self:
        new: Self

        try:
            new = cls.model_validate(location)
        except ValidationError as e:
            logger.error(e)
            raise

        return new

    @from_locator.register
    @classmethod
    def _(cls, location: MpsLocator) -> Self:
        new: Self
        try:
            new = cls.model_validate(asdict(location))
        except ValidationError as e:
            logger.error(e)
            raise

        return new

    # @model_validator(mode="after")
    # def validate_hierarchy(self) -> Self:
    #     """Validate the MPS structure."""
    #     base_dir: Path = Path(_MpsLocatorDefaults.base_dir)
    #     defaults = _MpsLocatorDefaults()
    #
    #     paths = {}
    #     for k, v in asdict(defaults).items():
    #         if getattr(self, k) is not None:
    #             continue
    #
    #         # do not prepend base_dir to itself
    #         if v == defaults.base_dir:
    #             paths[k] = base_dir
    #             continue
    #
    #         # prepend base_dir to others
    #         paths[k] = base_dir / str(v)
    #
    #     paths |= {k: Path(v) for k, v in paths.items()}
    #     self.__dict__.update(paths)
    #
    #     return self


class Miniature(BaseModel):
    """Miniatures properties."""

    homeland: Path
    """The homeland of all miniatures"""
    minikind: Annotated[MiniatureKind, AfterValidator(lambda x: MiniatureKind(x))]
    """Miniature home"""
    mininame: MiniatureName
    """Miniature name"""
    minicmdname: str
    """Command name"""

    @field_validator("homeland", mode="before")
    @classmethod
    def ensure_homeland_set(cls, value: Any) -> Path:
        """Make sure homeland is automatically set if not provided."""
        if not value:
            from mps import get_config

            return get_config().base_dir

        return Path(value).resolve()

    def __init__(self, /, **data: Any) -> None:
        if "homeland" not in data or data["homeland"] is None:
            from mps import get_config

            data["homeland"] = get_config().base_dir

        super().__init__(**data)

    @property
    def cmdpath(self) -> Path:
        """Get miniature's command path."""
        mininame = str(self.mininame)
        home = self.home

        if self.minikind in (MiniatureKind.STRATEGY, *MiniatureKind.extensions()):
            mininame = ""

        return home / mininame / self.minicmdname

    @property
    def home(self) -> Path:
        """Get miniature's home."""
        if self.minikind in MiniatureKind.extensions():
            return self.homeland / EXTENSION_PREFIX / self.minikind

        return self.homeland / self.minikind

    def read(self) -> str:
        """Read miniature's command."""
        from mps import loader

        return loader.read_miniature(self)

    @classmethod
    def from_path(cls, path: PathLike) -> Self:
        """Get a miniature object from a path.

        Raises:
            MiniatureNotFoundError: if the path you provided does not exist.

        """
        from mps.utils.miniatures import (
            get_miniature_cmdname,
            get_miniature_kind_from_path,
            get_miniature_name_from_path,
        )

        mininame = get_miniature_name_from_path(path)
        minikind = get_miniature_kind_from_path(path)
        minicmdname = get_miniature_cmdname(minikind, mininame)
        return cls(mininame=mininame, minikind=minikind, minicmdname=minicmdname)

    @classmethod
    def from_url(cls, url: AnyUrl) -> Self:
        """Get a miniature object from a url."""
        raise NotImplementedError

    @classmethod
    def from_miniature_name(
        cls, mininame: MiniatureName | str, minikind: MiniatureKind
    ) -> Self:
        """Get a miniature object from name and kind."""
        from mps.utils.miniatures import get_miniature_cmdname

        mininame = MiniatureName(name=mininame)

        try:
            minicmdname = get_miniature_cmdname(minikind, mininame)
        except MiniatureNotFoundError:
            # when a context miniature is not found, create a new one.
            minicmdname = f"{mininame}.md"
        return cls(mininame=mininame, minikind=minikind, minicmdname=minicmdname)

    @classmethod
    def from_mps_component(cls, component: _BaseMpsComponent) -> Self:
        """Get a miniature from mps component."""
        return cls.from_miniature_name(
            mininame=str(component.name),
            minikind=MiniatureKind(component.__class__.__name__.lower()),
        )


class Homeless:
    """Miniatures that does not adhere to MPS structure.

    Those can be miniatures that are on the internet or from anywhere on your machine.
    """
