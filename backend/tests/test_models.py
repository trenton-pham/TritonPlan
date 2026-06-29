from app.db.base import Base
from app.models import Course, CoursePrerequisite


def test_course_models_register_with_base_metadata() -> None:
    assert Course.__table__.metadata is Base.metadata
    assert CoursePrerequisite.__table__.metadata is Base.metadata
    assert "courses" in Base.metadata.tables
    assert "course_prerequisites" in Base.metadata.tables
