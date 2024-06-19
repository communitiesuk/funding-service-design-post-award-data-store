import dataclasses


@dataclasses.dataclass
class NextPageCondition:
    field: str
    value_to_path_mapping: dict

    @classmethod
    def load_from_json(cls, json_data: dict) -> "NextPageCondition":
        return cls(field=json_data["field"], value_to_path_mapping=json_data["value_to_path_mapping"])
