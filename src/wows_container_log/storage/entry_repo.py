from sqlmodel import select
from typing import List

from wows_container_log.models.container import RewardEntry
from wows_container_log.storage import group_repo, item_repo
from wows_container_log.storage.databases import get_container_session

# ----------------------------------------------------------------
# Exceptions
# ----------------------------------------------------------------


class CyclicGroupError(Exception):
    """Wird geworfen, wenn ein RewardEntry eine zyklische Gruppenstruktur erzeugen würde."""


class DuplicateGroupChildError(Exception):
    """Wird geworfen, wenn eine Untergruppe mehrfach in derselben Gruppe eingetragen werden soll."""


class DuplicateItemChildError(Exception):
    """Wird geworfen, wenn ein Item mehrfach in derselben Gruppe eingetragen werden soll."""


# ----------------------------------------------------------------
# public methods or functions
# ----------------------------------------------------------------


def create_entry_by_reward_entry(new_entry: RewardEntry) -> RewardEntry:

    parent_group_id = new_entry.group_id

    if new_entry.kind == "group":
        _validate_group_child_entry(new_entry, parent_group_id)

    elif new_entry.kind == "item":
        _validate_item_child_entry(new_entry, parent_group_id)

    with get_container_session() as session:
        session.add(new_entry)
        session.commit()
        session.refresh(new_entry)
        return new_entry


def get_all_entries_by_group_id(group_id: str) -> List[RewardEntry] | None:
    with get_container_session() as session:
        statement = select(RewardEntry).where(RewardEntry.group_id == group_id)
        return list(session.exec(statement))


def has_group_child(parent_group_id: str, child_group_id: str) -> bool:
    """
    Prüft, ob es bereits einen RewardEntry mit kind='group' gibt,
    der parent_group_id -> child_group_id abbildet.
    """
    entries = get_all_entries_by_group_id(parent_group_id) or []
    return any(
        entry.kind == "group" and entry.ref_id == child_group_id for entry in entries
    )


def has_item_child(parent_group_id: str, item_id: str) -> bool:
    """
    Prüft, ob es bereits einen RewardEntry mit kind='item' gibt,
    der parent_group_id -> item_id abbildet.
    """
    entries = get_all_entries_by_group_id(parent_group_id) or []
    return any(entry.kind == "item" and entry.ref_id == item_id for entry in entries)


def resolve_entry_name_by_reward_entry(entry: RewardEntry) -> str | None:

    if entry.kind == "group":
        if group_name := group_repo.get_group_by_id(entry.ref_id):
            return group_name.name

    if entry.kind == "item":
        if item_name := item_repo.get_item_by_id(entry.ref_id):
            return item_name.name


def resolve_entry_name_by_kind_and_ref_id(kind: str, ref_id) -> str | None:

    if kind == "group":
        if group_name := group_repo.get_group_by_id(ref_id):
            return group_name.name
    elif kind == "item":
        if item_name := item_repo.get_item_by_id(ref_id):
            return item_name.name


def would_create_cycle(parent_group_id: str, child_group_id: str) -> bool:

    # Trivialfall: Gruppe darf nicht Kind von sich selbst werden
    if parent_group_id == child_group_id:
        return True

    # DFS/BFS durch die Gruppenstruktur, ausgehend von child_group_id,
    # um zu sehen, ob wir irgendwann wieder parent_group_id erreichen.
    to_visit: list[str] = [child_group_id]
    visited: set[str] = set()

    while to_visit:
        current_id = to_visit.pop()
        if current_id in visited:
            continue
        visited.add(current_id)

        # alle RewardEntries, deren parent = current_id ist
        entries = get_all_entries_by_group_id(current_id) or []
        for entry in entries:
            if entry.kind != "group":
                continue

            subgroup_id = entry.ref_id
            if subgroup_id == parent_group_id:
                return True  # Zyklus gefunden

            to_visit.append(subgroup_id)

    return False  # kein Zyklus


# ----------------------------------------------------------------
# private methods or functions
# ----------------------------------------------------------------


def _validate_group_child_entry(
    entry: RewardEntry, parent_group_id: str | None
) -> None:

    child_group_id = entry.ref_id

    if parent_group_id is None or child_group_id is None:
        raise ValueError("group_id und ref_id dürfen für kind='group' nicht None sein.")

    if would_create_cycle(
        parent_group_id=parent_group_id, child_group_id=child_group_id
    ):
        raise CyclicGroupError(
            f"Die Zuordnung {parent_group_id!r} -> {child_group_id!r} würde eine zyklische Gruppenstruktur erzeugen."
        )

    if has_group_child(parent_group_id=parent_group_id, child_group_id=child_group_id):
        raise DuplicateGroupChildError(
            f"Die Untergruppe {child_group_id!r} ist in der Gruppe {parent_group_id!r} bereits eingetragen."
        )


def _validate_item_child_entry(entry: RewardEntry, parent_group_id: str | None) -> None:

    item_id = entry.ref_id

    if parent_group_id is None or item_id is None:
        raise ValueError("group_id und ref_id dürfen für kind='item' nicht None sein.")

    if has_item_child(parent_group_id=parent_group_id, item_id=item_id):
        raise DuplicateItemChildError(
            f"Der Gegenstand {item_id!r} ist in der Gruppe {parent_group_id!r} bereits eingetragen."
        )
