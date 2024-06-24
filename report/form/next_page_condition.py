import dataclasses

from report.interfaces import Loadable


@dataclasses.dataclass
class NextPageCondition(Loadable):
    field: str
    value_to_id_mapping: dict

    @classmethod
    def load_from_json(cls, json_data: dict) -> "NextPageCondition":
        return cls(field=json_data["field"], value_to_id_mapping=json_data["value_to_id_mapping"])
