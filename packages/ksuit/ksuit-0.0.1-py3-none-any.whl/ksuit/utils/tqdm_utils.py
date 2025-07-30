from typing import Self


class NoopTqdm:
    def __init__(self, iterable):
        self.iterable = iterable

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *_, **__) -> None:
        pass

    def noop(self, *_, **__) -> None:
        pass

    def __getattr__(self, *_, **__):
        return self.noop

    def __iter__(self):
        yield from self.iterable
