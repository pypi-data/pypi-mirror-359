# MPS Engine

The official engine implementation of Context Meta Pattern Strategy (MPS) architecture.

Context is an extension of the MPS architecture built on top of [Markitdown](<https://github.com/microsoft/markitdown.git>),
its whole purpose is to allow you to freely input any kind of file and the *mps-engine*
automatically fit it into the MPS architecture.

## MPS

```python
from mps import Mps, MPSHierarchy

mps = MPS()
# uses default hierarchy, you can import it and see it at <mps.MPSLocatorDefaults>

# or
mps = Mps.from_location("path/to/project/mps")

# or
mps = Mps.from_location(MPSHierarchy(
    base_dir = "mps",
    meta_dir = "meta",
    pattern_dir = "pattern",
    context_dir = "context",
    strategy_dir = "strategy"
))
```

### Context

#### Example

```python
from mps import context

# => Markdown file placed under mps/context/my_finances.md
c = context(name="my-finances")  # Context object
```

#### Supported Formats

* xml
* pdf
* html
* .mp4
* .mp3

### Pattern

#### Example

```python
from mps import pattern, inject

ta = pattern(name="teacher-assistant")  # => Pattern object

# or if a variable exist in the pattern
p = inject(pattern("translate"), lang_code="en-US")
```

### Strategy

#### Example

```python
from mps import strategy

cot = strategy(name="CoT")  # => Strategy object
```

## Integration

### Semantic Kernel

1. **Supplying kernel functions with more context**

```python
@context(name="my-details")
@kernel_function(name="greeter", description="Greets people")
def greet(name: str) -> str:
    return f"Hello {name}"
```

2. **Personalizing agents**

```python
from semantic_kernel.agents import ChatCompletionAgent
from mps import pattern

p = pattern("student-tutor")
# or
p = pattern("www.mydrive.com/student-tutor.md")
# or
p = pattern("www.mydrive.com/student-tutor.md", nopersist=True)  #* (not recommended)
# by default the engine thinks the url that you used for a pattern is useful so it persists
# this is due to the [reusability philosophy](<../../README.md#reusability-philosophy>)
# and the [insurance phiolosophy](<../../README.md#insurance-philosophy>)
# in the MPS architecture

student_tutor_agent = ChatCompletionAgent(
    instructions=pattern("student-tutor"),
)
```

3. **Giving agents a personality**

```python
from semantic_kernel.agents import ChatCompletionAgent
from mps import strategy, strategizer, context, pattern

finance_agent = ChatCompletionAgent(
    instructions=strategizer(
        context=context("my-monthly-billings"),
        pattern=pattern("finance-consultant"),
        strategy=startegy("AoT"),
    )
)
```

---

## Interfaces (Miniatures & MPS)

### Miniatures

```python
from mps import get_minatures_homeland, set_minatures_homeland, Miniatures

get_minatures_homeland()
set_minatures_homeland("path/to/project/miniatures/")

# or

Miniatures.homeland = "path/to/project/miniatures/"
print(Miniatures.homeland)
```

### MPS

```python
from mps import get_mps_basedir, set_mps_basedir, Mps

get_mps_basedir()
set_mps_basedir("path/to/project/mps/")


Mps.basedir = "/path/to/project/mps"
print(Mps.basedir)
```

## Roadmap

The following features are planned for future releases:

1. **Complete core functionality** - Finish any `NotImplementedError` or `@future` decorated functions
2. **Documentation sprint** - Focus on comprehensive documentation (also including CHANGELOG.md and breaking changes)
3. **Test coverage** - Aim for 80%+ test coverage on core functionality
4. **Community preparation** - Code of conduct, contribution guidelines
5. **CI/CD setup** - GitHub Actions for testing, linting, and deployment to PyPI

### Nice to have

1. **AsyncIO Support**: Full async API for all MPS operations
2. **Cache Support**: Cache frequently requested miniatures via HTTP
3. **Compilation Support**: Compile the mps/ directory into a python script to reduce io overhead,
    and a potentially use for direct imports.
4. **MPS Interface**: A friendly UI to show/filter/add/modify miniatures in your local mps collection.
5. **MPS Shop**: A remote website where you can pull miniatures made by community to your local mps collection.
6. **MCP Integration**: Have your local mps collection converted as MCP prompts.
