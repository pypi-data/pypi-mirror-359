from mps import inject, pattern
from mps.ext import preference

translate = pattern("translate")
editor = preference("text-editor")

print(inject(translate, lang_code="en-US"))
print(inject(editor, editor="neovim"))
