import re
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup

from app.schemas.job_posting import JobPostingIngestion
from app.services.collectors.base import BaseCollector


class ImpulsoCollector(BaseCollector):
    """
    Estratégia:
    1. Busca a página de listagem pública de oportunidades
    2. Extrai links /profissionais/oportunidade/... ou /pt/profissionais/oportunidade/...
    3. Visita cada vaga e extrai os dados principais

    Fallback:
    - se a listagem não trouxer links no HTML, usa config["seed_job_urls"] se existir
    """

    LISTING_PATHS = [
        "/pt/profissionais/oportunidades",
        "/profissionais/oportunidades",
    ]

    JOB_PATH_PATTERNS = (
        "/profissionais/oportunidade/",
        "/pt/profissionais/oportunidade/",
    )

    def fetch_jobs(self) -> list[JobPostingIngestion]:
        company_name = self.config.get("company_name", "Impulso")

        with httpx.Client(
            timeout=30.0,
            follow_redirects=True,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (X11; Linux x86_64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/142.0.0.0 Safari/537.36"
                )
            },
        ) as client:
            job_urls = self._collect_job_urls(client)

            jobs: list[JobPostingIngestion] = []
            for job_url in job_urls:
                try:
                    job = self._fetch_job_detail(
                        client=client,
                        job_url=job_url,
                        company_name=company_name,
                    )
                    if job:
                        jobs.append(job)
                except Exception:
                    # segue o baile; uma vaga quebrada não deve matar a coleta inteira
                    continue

        return jobs

    def _collect_job_urls(self, client: httpx.Client) -> list[str]:
        candidate_urls = self._build_listing_urls()
        discovered_urls: list[str] = []

        for listing_url in candidate_urls:
            response = client.get(listing_url)
            response.raise_for_status()

            urls = self._extract_job_urls_from_listing_html(
                html=response.text,
                page_url=str(response.url),
            )
            discovered_urls.extend(urls)

        if not discovered_urls:
            seed_job_urls = self.config.get("seed_job_urls") or []
            if isinstance(seed_job_urls, list):
                discovered_urls.extend(
                    [str(url).strip() for url in seed_job_urls if str(url).strip()]
                )

        return self._dedupe_urls(discovered_urls)

    def _build_listing_urls(self) -> list[str]:
        base = self.base_url.rstrip("/")
        urls = []

        if any(base.endswith(path) for path in self.LISTING_PATHS):
            urls.append(base)
        else:
            for path in self.LISTING_PATHS:
                urls.append(f"{base}{path}")

        return list(dict.fromkeys(urls))

    def _extract_job_urls_from_listing_html(self, *, html: str, page_url: str) -> list[str]:
        soup = BeautifulSoup(html, "html.parser")
        urls: list[str] = []

        for anchor in soup.find_all("a", href=True):
            href = anchor["href"].strip()
            absolute_url = urljoin(page_url, href)

            if self._is_job_url(absolute_url):
                urls.append(self._normalize_job_url(absolute_url))

        return self._dedupe_urls(urls)

    def _fetch_job_detail(
        self,
        *,
        client: httpx.Client,
        job_url: str,
        company_name: str,
    ) -> JobPostingIngestion | None:
        response = client.get(job_url)
        response.raise_for_status()

        html = response.text
        soup = BeautifulSoup(html, "html.parser")
        text = self._extract_text(soup)

        title = self._extract_title(soup, text)
        if not title:
            return None

        external_id = self._extract_external_id(job_url)
        location_raw = self._extract_location(text)
        description_raw = self._extract_description(text)

        raw_payload = {
            "source_url": job_url,
            "title": title,
            "location_raw": location_raw,
            "description_raw": description_raw,
        }

        return JobPostingIngestion(
            external_id=external_id,
            title=title,
            company=company_name,
            url=self._normalize_job_url(job_url),
            location_raw=location_raw,
            description_raw=description_raw,
            published_at=None,
            raw_payload=raw_payload,
        )

    @staticmethod
    def _extract_text(soup: BeautifulSoup) -> str:
        text = soup.get_text("\n", strip=True)
        text = re.sub(r"\n{2,}", "\n\n", text)
        return text.strip()

    def _extract_title(self, soup: BeautifulSoup, text: str) -> str | None:
        # tenta headings primeiro
        for tag_name in ("h1", "h2", "h3"):
            for tag in soup.find_all(tag_name):
                value = tag.get_text(" ", strip=True)
                if value and re.search(r"\d+\s*-\s*", value):
                    return self._clean_title(value)
                if value and "Pessoa " in value:
                    return self._clean_title(value)

        # fallback por regex no texto corrido
        patterns = [
            r"###\s*(\d+\s*-\s*.+)",
            r"(\d+\s*-\s*Pessoa[^\n]+)",
            r"(\d+\s*-\s*\[?[^\n]+)",
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return self._clean_title(match.group(1))

        return None

    @staticmethod
    def _clean_title(value: str) -> str:
        value = re.sub(r"^#+\s*", "", value).strip()
        return re.sub(r"\s{2,}", " ", value)

    @staticmethod
    def _extract_external_id(job_url: str) -> str | None:
        path = urlparse(job_url).path
        match = re.search(r"/oportunidade/(\d+)", path)
        if match:
            return match.group(1)
        return None

    @staticmethod
    def _extract_location(text: str) -> str | None:
        patterns = [
            r"(100%\s*Remoto)",
            r"(Remoto\s*-\s*[^\n]+)",
            r"(Híbrido\s*-\s*[^\n]+)",
            r"(Presencial\s*-\s*[^\n]+)",
        ]
        for pattern in patterns:
            match = re.search(pattern, text, flags=re.IGNORECASE)
            if match:
                return match.group(1).strip()

        return None

    @staticmethod
    def _extract_description(text: str) -> str | None:
        start_markers = [
            "## Perfil que precisamos",
            "Perfil que buscamos:",
            "1. Resumo da Posição",
            "Resumo da Posição",
        ]
        end_markers = [
            "### Impulser Professional",
            "### Benefícios Exclusivos",
            "### Sobre a Impulso",
            "### Não quer se cadastrar em uma nova plataforma?",
        ]

        start_index = -1
        for marker in start_markers:
            idx = text.find(marker)
            if idx != -1:
                start_index = idx
                break

        if start_index == -1:
            return None

        sliced = text[start_index:]

        end_index = len(sliced)
        for marker in end_markers:
            idx = sliced.find(marker)
            if idx != -1:
                end_index = min(end_index, idx)

        description = sliced[:end_index].strip()
        description = re.sub(r"\n{3,}", "\n\n", description)

        return description or None

    def _is_job_url(self, url: str) -> bool:
        parsed = urlparse(url)
        path = parsed.path

        return any(pattern in path for pattern in self.JOB_PATH_PATTERNS)

    @staticmethod
    def _normalize_job_url(url: str) -> str:
        parsed = urlparse(url)
        clean_path = parsed.path.rstrip("/")
        return f"{parsed.scheme}://{parsed.netloc}{clean_path}"

    @staticmethod
    def _dedupe_urls(urls: list[str]) -> list[str]:
        cleaned = []
        seen = set()

        for url in urls:
            normalized = url.strip()
            if not normalized or normalized in seen:
                continue
            seen.add(normalized)
            cleaned.append(normalized)

        return cleaned
