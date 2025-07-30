from sqlalchemy import ForeignKey, Text, Integer, DateTime, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from .base import Base
from ..utils.constants import SeriesStatus, SeriesType

class Series(Base):
    __tablename__ = "series"
    ###          1:1 GRID          ###
    id: Mapped[str] = mapped_column(Text, primary_key=True)
    type: Mapped[SeriesType] # GRID SeriesType
    # Some of the older series have null start times when data is not available
    scheduled_start_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    format: Mapped[int] = mapped_column(Integer) # Best of number
    tournament_id: Mapped[str] = mapped_column(Text, ForeignKey("tournaments.id"))
    external_links = mapped_column(JSONB)

    ###     Processing status      ###
    status: Mapped[SeriesStatus]

    ###           Debug            ###
    updated: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())