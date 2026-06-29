from pydantic import BaseModel, ConfigDict

class CourseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    code: str
    subject: str
    number: str
    title: str
    units: int
    department: str | None = None
    division: str | None = None
    description: str | None = None
    known_offering_terms: list[str]
    source_refs: list[str]
    data_confidence: str