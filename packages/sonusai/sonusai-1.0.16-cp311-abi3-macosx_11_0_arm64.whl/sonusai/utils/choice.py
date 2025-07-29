from abc import ABC
from abc import abstractmethod
from typing import Any


class BaseChoice(ABC):
    def __init__(self, data: list):
        self.data = data
        self.index = 0
        self.choices: list = []

    @abstractmethod
    def next(self) -> Any:
        pass


class RandomChoice(BaseChoice):
    def __init__(self, data: list, repetition: bool = False):
        from random import sample

        super().__init__(data)
        self.repeat = repetition
        self.choices = sample(self.data, len(self.data))

    def next(self) -> Any:
        from random import choice
        from random import sample

        if self.repeat:
            return choice(self.data)  # noqa: S311

        if self.index >= len(self.data):
            self.choices = sample(self.data, len(self.data))
            self.index = 0

        item = self.choices[self.index]
        self.index += 1

        return item


class SequentialChoice(BaseChoice):
    def __init__(self, data: list):
        super().__init__(data)

    def next(self) -> Any:
        if self.index >= len(self.data):
            self.index = 0
        item = self.data[self.index]
        self.index += 1
        return item
