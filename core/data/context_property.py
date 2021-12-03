import weakref


class ContextProperty:
    def __init__(self, property_type: type = None):
        self.__name: str = ''
        self.__property_type: type = property_type
        self.__values = weakref.WeakKeyDictionary()

    def __set_name__(self, owner, name: str):
        self.__name = name
        if name in owner.__annotations__ and self.__property_type is None:
            self.__property_type = owner.__annotations__[name]

    def __get__(self, view, owner):
        if view not in self.__values:
            self.__values[view] = self.__fetch_value(view)
        return self.__values[view]

    def __fetch_value(self, view):
        current_view = view
        while current_view:
            value = current_view.get_context_property(self.__property_type)
            if value is not None:
                return value
            current_view = current_view.parent
        return None
