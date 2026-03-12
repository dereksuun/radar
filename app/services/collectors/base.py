from abc import ABC, abstractmethod

from app.schemas.job_posting import JobPostingIngestion


class BaseCollector(ABC):
    def __init__(self, source_name: str, base_url: str, config: dict | None = None):
        self.source_name = source_name
        self.base_url = base_url
        self.config = config or {}

    @abstractmethod
    def fetch_jobs(self) -> list[JobPostingIngestion]:
        raise NotImplementedError
