from typing import TypeVar

K = TypeVar("K")
V = TypeVar("V")


class InjectiveDict[K, V]:
    """Bidirectional mapping between keys and values, where the type of keys/values decides the direction of the map.
    """

    def __init__(self, source: dict[K, V]):
        super().__init__()
        unique_key_types = {type(key) for key in source.keys()}
        unique_value_types = {type(value) for value in source.values()}
        if len(unique_key_types) > 1:
            raise ValueError(
                f"{type(self).__name__} requires distinct key types. "
                f"Found multiple key types: {list(sorted(map(lambda t: t.__name__, unique_key_types)))}"
            )
        if len(unique_value_types) > 1:
            raise ValueError(
                f"{type(self).__name__} requires distinct value types. "
                f"Found multiple value types: {list(sorted(map(lambda t: t.__name__, unique_value_types)))}"
            )
        # instantiate types
        self.key_type = next(iter(unique_key_types))
        self.value_type = next(iter(unique_value_types))
        if self.key_type is self.value_type:
            raise ValueError(f"Key and value types need to be different. Both are: '{self.key_type.__name__}'")
        # instantiates dicts
        self._keys_to_values = dict(source)
        self._values_to_keys = {value: key for key, value in source.items()}

    def __len__(self) -> int:
        return len(self._keys_to_values)

    def __setitem__(self, arg1: K | V, arg2: K | V) -> None:
        # checks
        if not isinstance(arg1, self.key_type | self.value_type):
            raise ValueError(
                f"Invalid type ('{type(arg1).__name__}') for 'arg1'. "
                f"Expected '{self.key_type.__name__}' or '{self.value_type.__name__}'."
            )
        if not isinstance(arg2, self.key_type | self.value_type):
            raise ValueError(
                f"Invalid type ('{type(arg2).__name__}') for 'arg2'. "
                f"Expected '{self.key_type.__name__}' or '{self.value_type.__name__}'."
            )
        if type(arg1) is type(arg2):
            raise ValueError(f"Expected different types for 'arg1' and 'arg2'. Bot are: '{type(arg1).__name__}'.")

        # update dicts
        if isinstance(arg1, self.key_type):
            self._keys_to_values[arg1] = arg2
            self._values_to_keys[arg2] = arg1
        else:
            self._keys_to_values[arg2] = arg1
            self._values_to_keys[arg1] = arg2

    def __getitem__(self, arg: K | V) -> K | V:
        # checks
        if not isinstance(arg, self.key_type | self.value_type):
            raise ValueError(
                f"Invalid type '{type(arg).__name__}'. "
                f"Expected '{self.key_type.__name__}' or '{self.value_type.__name__}'."
            )

        # retrieve
        if isinstance(arg, self.key_type):
            return self._keys_to_values[arg]
        return self._values_to_keys[arg]

    def to_dict(self, key_type: type[K] | type[V]) -> dict[K, V] | dict[V, K]:
        if key_type is self.key_type:
            return dict(self._keys_to_values)
        return dict(self._values_to_keys)