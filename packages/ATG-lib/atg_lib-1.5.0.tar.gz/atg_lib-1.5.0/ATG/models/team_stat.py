from sqlalchemy import Integer, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base


class TeamStat(Base):
    __tablename__ = "team_stats"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    game_id: Mapped[str] = mapped_column(Text, ForeignKey("games.id"))
    team_id: Mapped[int] = mapped_column(Integer) # 100 / 200
    game_time: Mapped[int] = mapped_column(Integer)

    # Team stats from stat_update
    deaths: Mapped[int] = mapped_column(Integer)
    assists: Mapped[int] = mapped_column(Integer)
    champion_kills: Mapped[int] = mapped_column(Integer)

    total_gold: Mapped[int] = mapped_column(Integer)
    baron_kills: Mapped[int] = mapped_column(Integer)
    inhib_kills: Mapped[int] = mapped_column(Integer)
    tower_kills: Mapped[int] = mapped_column(Integer)
    dragon_kills: Mapped[int] = mapped_column(Integer)

    """

    'deaths': 8,
       'teamID': 100,
       'assists': 54,
       'totalGold': 55997,
       'baronKills': 1,
       'inhibKills': 1,
       'towerKills': 7,
       'dragonKills': 3,
       'championsKills': 21},"""
