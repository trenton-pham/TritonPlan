from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base


class Course(Base):
    __tablename__ = "courses"

    id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    subject: Mapped[str] = mapped_column(String(16), nullable=False)
    number: Mapped[str] = mapped_column(String(16), nullable=False)
    code: Mapped[str] = mapped_column(String(32), nullable=False, unique=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    units: Mapped[int] = mapped_column(Integer, nullable=False)

    department: Mapped[str | None] = mapped_column(String(120))
    division: Mapped[str | None] = mapped_column(String(32))
    description: Mapped[str | None] = mapped_column(Text)

    known_offering_terms: Mapped[list[str]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
    )
    source_refs: Mapped[list[str]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
    )
    data_confidence: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="unknown",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    prerequisite: Mapped[CoursePrerequisite | None] = relationship(
        back_populates="course",
        cascade="all, delete-orphan",
        uselist=False,
    )

    __table_args__ = (
        UniqueConstraint("subject", "number", name="uq_courses_subject_number"),
        CheckConstraint("units > 0", name="ck_courses_units_positive"),
    )


class CoursePrerequisite(Base):
    __tablename__ = "course_prerequisites"

    id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    course_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        ForeignKey("courses.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )

    expression: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    source_refs: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    data_confidence: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="unknown",
    )

    course: Mapped[Course] = relationship(back_populates="prerequisite")