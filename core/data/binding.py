import weakref


class BindingError(Exception):
    pass


class DataBinding:
    def __init__(self, view, property_name: str):
        self.__owner = weakref.ref(view)
        self.__property_name = property_name

    def get(self):
        owner = self.__owner()
        if owner is None:
            raise BindingError(
                f'Cannot get value for DataBinding for field "{self.__property_name}". '
                f'Owner is dead.'
            )
        return getattr(owner, self.__property_name)

    def set(self, value):
        owner = self.__owner()
        if owner is None:
            raise BindingError(
                f'Cannot set value for DataBinding for field "{self.__property_name}". '
                'Owner is dead.'
            )
        setattr(owner, self.__property_name, value)


class Binding:
    def __init__(self):
        self.__data_bindings = weakref.WeakKeyDictionary()
        self.__name = ""

    def __set_name__(self, owner, name):
        self.__name = name

    def __set__(self, view, value):
        self.__check_data_binding(view)

        data_binding: DataBinding = self.__data_bindings[view]
        data_binding.set(value)

    def __get__(self, view, owner):
        if view is None:
            raise BindingError('Bindings can only be accessed on instances.')
        self.__check_data_binding(view)

        data_binding: DataBinding = self.__data_bindings[view]
        return data_binding.get()

    def __check_data_binding(self, view):
        if view not in self.__data_bindings:
            raise BindingError(f'DataBinding not set for Binding property {self.__name}')

    def set_data_binding(self, view, data_binding: DataBinding):
        if type(data_binding) != DataBinding:
            raise BindingError(
                f'"{view.__class__.__name__}.{self.__name}" property requires a DataBinding object '
                f'to be passed to __init__.',
            )

        self.__data_bindings[view] = data_binding
