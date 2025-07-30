from ydnatl.core.element import HTMLElement


class HTML(HTMLElement):
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            **{
                **kwargs | {"lang": "en", "dir": "ltr"},
                "tag": "html",
                "self_closing": False
            },
        )
        self._prefix = "<!DOCTYPE html>"


class Head(HTMLElement):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **{**kwargs, "tag": "head"})


class Body(HTMLElement):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **{**kwargs, "tag": "body"})


class Title(HTMLElement):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **{**kwargs, "tag": "title"})


class Meta(HTMLElement):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **{**kwargs, "tag": "meta", "self_closing": True})


class Link(HTMLElement):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **{**kwargs, "tag": "link", "self_closing": True})


class Script(HTMLElement):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **{**kwargs, "tag": "script"})


class Style(HTMLElement):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **{**kwargs, "tag": "style"})


class IFrame(HTMLElement):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **{**kwargs, "tag": "iframe"})
