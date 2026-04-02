"""
This module contains the models for the drops database.
"""

from typing import Optional

from sqlmodel import Field, SQLModel

# ============================================
# 4. Tatsächliche Öffnungen und Drops
# ============================================


class ContainerOpen(SQLModel, table=True):  # pyright: ignore[reportCallIssue, reportGeneralTypeIssues]
    """Öffnung der Container"""

    id: Optional[int] = Field(default=None, primary_key=True)
    opened_at: str  # ISO-String (Datum/Zeit)
    container_id: str = Field(foreign_key="containertype.id")
    context: Optional[str] = Field(
        default=None, description="optional (Account, Event, Notiz)"
    )


class SlotPick(SQLModel, table=True):  # pyright: ignore[reportCallIssue, reportGeneralTypeIssues]
    """Drop-Details pro Gegenstandsposition"""

    id: Optional[int] = Field(default=None, primary_key=True)
    container_open_id: int = Field(foreign_key="containeropen.id")
    item_index: int  # 1..items, Gegenstandsposition
    group_id: str = Field(foreign_key="rewardgroup.id")
    entry_id: int = Field(foreign_key="rewardentry.id")
    item_id: Optional[str] = Field(default=None, foreign_key="rewarditem.id")
    amount: int  # effektiv gedroppte Menge
    extra: Optional[str] = None  # z.B. konkrete Zahl bei 'x Freie EP'


__all__ = ["ContainerOpen", "SlotPick"]
