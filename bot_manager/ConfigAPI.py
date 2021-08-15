import os
import json
from typing import Any


class Config:
    def __init__(self, path: str, default: dict):
        self.__data__: dict = {}
        self.__default__ = default
        self.__filepath__ = path
        self.load()

    def get(self, item) -> Any:
        return self.__getitem__(item)

    def pop(self, key):
        self.__data__.pop(key)
        self.save()

    def __getitem__(self, item) -> Any:
        if item in self.__data__:
            return self.__data__.get(item)
        if item in self.__default__:
            self.__setitem__(item, self.__default__.get(item))
            return self.__data__.get(item)
        return None

    def __setitem__(self, key, value):
        self.__data__[key] = value
        self.save()

    def load(self):
        if os.path.isfile(self.__filepath__):
            with open(self.__filepath__, 'r', encoding='utf-8') as f:
                self.__data__ = json.load(f)
        else:
            self.__data__ = self.__default__
            for i in self.__default__:
                if i not in self.__data__:
                    self.__data__[i] = self.__default__[i]
            self.save()

    def save(self):
        with open(self.__filepath__, 'w', encoding='utf-8') as f:
            json.dump(self.__data__, f, indent=4, ensure_ascii=False)
