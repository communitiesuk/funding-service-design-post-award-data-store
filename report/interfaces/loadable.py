from abc import ABC, abstractmethod


class Loadable(ABC):
    @classmethod
    @abstractmethod
    def load_from_json(cls, json_data: dict) -> "Loadable":
        pass
