from sqlmodel import select
from typing import List

from wows_container_log.models.container import RewardItem
from wows_container_log.storage.databases import get_container_session


def create_item_by_reward_item(item: RewardItem) -> RewardItem:
    with get_container_session() as session:
        existing = session.get(RewardItem, item.id)
        if existing is not None:
            raise ValueError(f"RewardItem '{item.id}' existiert bereits.")

        session.add(item)
        session.commit()
        session.refresh(item)
        return item


def delete_item_by_id(item_id: str) -> None:
    with get_container_session() as session:
        existing = session.get(RewardItem, item_id)
        if existing is None:
            return
        session.delete(existing)
        session.commit()


def get_all_items() -> List[RewardItem]:
    with get_container_session() as session:
        statement = select(RewardItem).order_by(RewardItem.name)
        return list(session.exec(statement))


def get_item_by_id(item_id: str) -> RewardItem | None:
    with get_container_session() as session:
        return session.get(RewardItem, item_id)


def is_item_unique_by_id(item_id: str) -> bool:
    with get_container_session() as session:
        statement = select(RewardItem).where(RewardItem.id == item_id)
        if session.exec(statement).first():
            return False

    return True


def update_item_by_reward_item(item: RewardItem) -> RewardItem:
    with get_container_session() as session:
        existing = session.get(RewardItem, item.id)
        if existing is None:
            raise ValueError(f"RewardItem '{item.id}' existiert nicht.")

        existing.name = item.name
        existing.amount = item.amount
        existing.meta = item.meta
        existing.unique_once = item.unique_once

        session.add(existing)
        session.commit()
        session.refresh(existing)
        return existing
