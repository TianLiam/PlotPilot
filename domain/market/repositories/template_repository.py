from abc import ABC, abstractmethod
from typing import List, Optional
from domain.market.entities.template import Template


class TemplateRepository(ABC):
    @abstractmethod
    def save(self, template: Template) -> None:
        pass

    @abstractmethod
    def get_by_id(self, template_id: str) -> Optional[Template]:
        pass

    @abstractmethod
    def get_by_type(self, template_type: str) -> List[Template]:
        pass

    @abstractmethod
    def get_by_genre(self, genre: str) -> List[Template]:
        pass

    @abstractmethod
    def get_by_type_and_genre(self, template_type: str, genre: str) -> List[Template]:
        pass

    @abstractmethod
    def search(self, keyword: str) -> List[Template]:
        pass

    @abstractmethod
    def list_all(self) -> List[Template]:
        pass

    @abstractmethod
    def increment_usage(self, template_id: str) -> None:
        pass

    @abstractmethod
    def delete(self, template_id: str) -> None:
        pass