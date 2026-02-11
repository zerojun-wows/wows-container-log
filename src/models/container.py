"""
This module contains the models for the container database.
"""

from __future__ import annotations

from typing import Optional

from sqlmodel import Field, SQLModel


# ============================================
# 1. Container-Stammdaten
# ============================================

class ContainerType(SQLModel, table=True): # pyright: ignore[reportCallIssue, reportGeneralTypeIssues]
    """Container-Stammdaten"""

    id: str = Field(primary_key=True, description="z.B. 'more_coal'")
    name: str = Field(description="angezeigte Bezeichnung")
    remium: int = Field(description="0 = normal, 1 = premium")
    items: int = Field(description="Anzahl Gegenstände pro Öffnung (1..n)")
    description: str = Field(description="Beschreibung/Notizen")

# ============================================
# 2. Drop-Definition pro Container und Gegenstandsposition
# ============================================

class ContainerDropDef(SQLModel, table=True): # pyright: ignore[reportCallIssue, reportGeneralTypeIssues]
    """Drop-Definition pro Container und Gegenstandsposition"""
    
    id: Optional[int] = Field(default=None, primary_key=True)
    container_id: str = Field(foreign_key="containertype.id")
    item_index: int = Field(description="1..items (Gegenstandsposition)")
    root_group_id: str = Field(foreign_key="rewardgroup.id")


# ============================================
# 3. Dropbare Inhalte: Items, Gruppen, Einträge
# ============================================

class RewardItem(SQLModel, table=True): # pyright: ignore[reportCallIssue, reportGeneralTypeIssues]
    """Dropbare Inhalte: Items, Gruppen, Einträge"""

    id: str = Field(primary_key=True)   # z.B. 'item_coal_1500'
    name: str
    amount: int                         # Menge (z.B. 1500, 3, 1)
    meta: Optional[str] = Field(
        default=None,
        description="optional (JSON, Typ, etc.)"
    )
    unique_once: int = Field(
        default=0,
        description="0 = beliebig oft, 1 = nur einmal droppbar"
    )


class RewardGroup(SQLModel, table=True): # pyright: ignore[reportCallIssue, reportGeneralTypeIssues]
    """Dropbare Inhalte: Gruppen"""
    
    id: str = Field(primary_key=True)   # z.B. 'group_more_coal_slot2'
    name: str


class RewardEntry(SQLModel, table=True): # pyright: ignore[reportCallIssue, reportGeneralTypeIssues]
    """Dropbare Inhalte: Einträge"""
    
    id: Optional[int] = Field(default=None, primary_key=True)
    group_id: str = Field(foreign_key="rewardgroup.id")
    entry_key: str                        # technischer Schlüssel innerhalb der Gruppe
    kind: str                             # 'item' oder 'group'
    ref_id: str                           # reward_item.id oder reward_group.id
    amount: int                           # Menge (bei kind='item', sonst i.d.R. 1)
    probability: str                      # z.B. '5 %', '12,5 %'

    # Hinweis: uniqueness (group_id, entry_key) musst du aktuell per raw SQL schaffen


__all__ = [
    "ContainerType", 
    "ContainerDropDef", 
    "RewardItem", 
    "RewardGroup", 
    "RewardEntry"
]