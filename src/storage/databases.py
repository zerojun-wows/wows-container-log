"""
This module contains session information and initialization of both databases
"""

from __future__ import annotations

from src.models.container import (
    ContainerDropDef,
    ContainerType,
    RewardEntry,
    RewardGroup,
    RewardItem,
)
from src.models.drops import ContainerOpen, SlotPick
from sqlmodel import create_engine, Session


CONTAINERDATA_URL = "sqlite:///containerdata.db"
DROPDATA_URL = "sqlite:///dropdata.db"

containerdata_engine = create_engine(CONTAINERDATA_URL, echo=True)
dropdata_engine = create_engine(DROPDATA_URL, echo=True)


def init_databases() -> None:
    """
    Erzeuge die Tabellen in den jeweiligen Datenbanken, falls sie noch nicht existieren.
    """
    # Stammdaten-Tabellen in containerdata.db
    ContainerType.__table__.create(containerdata_engine, checkfirst=True)
    ContainerDropDef.__table__.create(containerdata_engine, checkfirst=True)
    RewardItem.__table__.create(containerdata_engine, checkfirst=True)
    RewardGroup.__table__.create(containerdata_engine, checkfirst=True)
    RewardEntry.__table__.create(containerdata_engine, checkfirst=True)

    # Log-Tabellen in dropdata.db
    ContainerOpen.__table__.create(dropdata_engine, checkfirst=True)
    SlotPick.__table__.create(dropdata_engine, checkfirst=True)


def get_container_session() -> Session:
    """
    Liefert eine neue Session für die Stammdaten-Datenbank (containerdata.db).
    """
    return Session(containerdata_engine)


def get_drop_session() -> Session:
    """
    Liefert eine neue Session für die Log-Datenbank (dropdata.db).
    """
    return Session(dropdata_engine)
