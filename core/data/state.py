import weakref


class State:
    def __init__(self, initial_value):
        self.__initial_value = initial_value
        self.__values = weakref.WeakKeyDictionary()

    def __set_name__(self, owner, name):
        pass

    def __set__(self, view, value):
        print('state set', value)
        self.__values[view] = value
        view.invalidate_cache()

    def __get__(self, view, owner):
        if view not in self.__values:
            self.__values[view] = self.__initial_value
        return self.__values[view]
