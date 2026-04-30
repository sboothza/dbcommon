from __future__ import annotations

import inspect
import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .repository_base import RepositoryBase


class RepositoryContext:
    repositories: dict[str, type] = {}  # entity type : repo type

    @staticmethod
    def get_repository(entity: type) -> RepositoryBase:
        return RepositoryContext.get_repository_by_name(entity.__name__)

    @staticmethod
    def get_repository_by_name(entity_type: str) -> RepositoryBase:
        if len(RepositoryContext.repositories) == 0:
            raise Exception(f"No repositories defined!")

        repo_type = RepositoryContext.repositories[entity_type]
        if repo_type is None:
            raise Exception(f"No repository defined for {entity_type}")
        return repo_type()

    @staticmethod
    def register_repository(repo:type) -> None:
        RepositoryContext.repositories[repo.__table__.__name__] = repo

    @staticmethod
    def register():
        from .repository_base import RepositoryBase

        for module in list(sys.modules.items()):
            for name, obj in inspect.getmembers(module[1]):
                if inspect.isclass(obj) and issubclass(obj, RepositoryBase) and obj != RepositoryBase:
                    entity = obj.__table__

                    if entity is not None:
                        if entity.__name__ not in RepositoryContext.repositories:
                            print(f"Registering repo type: {entity.__name__}")
                            RepositoryContext.repositories[entity.__name__] = obj

# RepositoryContext.register()