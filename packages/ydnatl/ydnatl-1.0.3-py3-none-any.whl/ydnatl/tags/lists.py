from ydnatl.core.element import HTMLElement


class UnorderedList(HTMLElement):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **{**kwargs, "tag": "ul"})

    @classmethod
    def with_items(cls, *items, **kwargs):
        ul = cls(**kwargs)
        for item in items:
            if isinstance(item, HTMLElement):
                ul.append(item)
            else:
                ul.append(ListItem(item))
        return ul


class OrderedList(HTMLElement):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **{**kwargs, "tag": "ol"})

    @classmethod
    def with_items(cls, *items, **kwargs):
        ol = cls(**kwargs)
        for item in items:
            if isinstance(item, HTMLElement):
                ol.append(item)
            else:
                ol.append(ListItem(item))
        return ol


class ListItem(HTMLElement):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **{**kwargs, "tag": "li"})


class Datalist(HTMLElement):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **{**kwargs, "tag": "datalist"})


class DescriptionDetails(HTMLElement):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **{**kwargs, "tag": "dd"})


class DescriptionList(HTMLElement):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **{**kwargs, "tag": "dl"})


class DescriptionTerm(HTMLElement):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **{**kwargs, "tag": "dt"})
