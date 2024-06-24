import dataclasses


@dataclasses.dataclass
class ReportPage:
    page_id: str
    form_data: dict

    @classmethod
    def load_from_json(cls, json_data: dict) -> "ReportPage":
        page_id = json_data["page_id"]
        form_data = json_data["form_data"]
        return cls(page_id=page_id, form_data=form_data)

    def serialize(self) -> dict:
        return {"page_id": self.page_id, "form_data": self.form_data}
