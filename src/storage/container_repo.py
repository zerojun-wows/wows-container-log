from typing import List, Optional

from src.models.container import ContainerType
from src.storage.databases import get_container_session
from sqlmodel import select


def list_containers() -> List[ContainerType]:
    with get_container_session() as session:
        stmt = select(ContainerType)
        return list(session.exec(stmt))


def get_container_by_id(container_id: str) -> Optional[ContainerType]:
    with get_container_session() as session:
        return session.get(ContainerType, container_id)


def save_container(container: ContainerType) -> ContainerType:
    # sourcery skip: extract-duplicate-method
    with get_container_session() as session:
        existing_container = session.get(ContainerType, container.id)

        if existing_container is None:
            session.add(container)
            session.commit()
            session.refresh(container)
            return container

        existing_container.name = container.name
        existing_container.premium = container.premium
        existing_container.items = container.items
        existing_container.description = container.description

        session.commit()
        session.refresh(existing_container)

        return existing_container
