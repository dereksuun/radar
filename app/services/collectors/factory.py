from app.models.job_source import JobSource
from app.services.collectors.base import BaseCollector
from app.services.collectors.greenhouse import GreenhouseCollector
from app.services.collectors.impulso import ImpulsoCollector
from app.services.collectors.lever import LeverCollector
from app.services.collectors.recruitee import RecruiteeCollector


def build_collector(source: JobSource) -> BaseCollector:
    source_type = source.source_type.strip().lower()

    collector_map = {
        "greenhouse": GreenhouseCollector,
        "lever": LeverCollector,
        "recruitee": RecruiteeCollector,
        "impulso": ImpulsoCollector,
    }

    collector_class = collector_map.get(source_type)
    if not collector_class:
        raise ValueError(f"Tipo de fonte não suportado: {source.source_type}")

    return collector_class(
        source_name=source.name,
        base_url=source.base_url,
        config=source.config,
    )
