from sqlmodel import select
from typing import List

from wows_container_log.models.container import RewardGroup
from wows_container_log.storage.databases import get_container_session

def create_group_by_reward_group(new_group: RewardGroup) -> RewardGroup:
    with get_container_session() as session:
        existing = session.get(RewardGroup, new_group.id)
        if existing is not None:
            raise ValueError(f"RewardGroup '{new_group.id}' existiert bereits.")

        session.add(new_group)
        session.commit()
        session.refresh(new_group)
        return new_group


def get_all_groups() -> List[RewardGroup]:
    with get_container_session() as session:
        statement = select(RewardGroup).order_by(RewardGroup.name)
        return list(session.exec(statement))

def get_group_by_id(group_id: str) -> RewardGroup | None:
    with get_container_session() as session:
        return session.get(RewardGroup, group_id)

def is_group_unique_by_id(group_id: str) -> bool:
    with get_container_session() as session:
        statement = select(RewardGroup).where(RewardGroup.id == group_id)
        if session.exec(statement).first():
            return False

    return True