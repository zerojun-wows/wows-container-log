from typing import List

from src.models.container import ContainerType
from src.storage.databases import get_container_session
from sqlmodel import select

def list_containers() -> List[ContainerType]:
    with get_container_session() as session:
        stmt = select(ContainerType)
        return list(session.exec(stmt))