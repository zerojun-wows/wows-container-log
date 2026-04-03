from sqlmodel import select
from typing import List

from wows_container_log.models.container import RewardItem
from wows_container_log.storage.databases import get_container_session


def get_all_items() -> List[RewardItem]:
    with get_container_session() as session:
        statement = select(RewardItem).order_by(RewardItem.name)
        return list(session.exec(statement))
