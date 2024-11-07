import asyncio
import logging
import re
from typing import List, Set

import aiohttp
import requests
from bs4 import BeautifulSoup


class GetProxies:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)
        self.proxies: Set[str] = set()
        self._fetch_proxies()
        self.validated_proxies: List[str] = []

    def _fetch_proxies(self) -> None:
        """Fetch proxies from multiple sources"""
        # Try free-proxy-list.net
        self._fetch_from_free_proxy_list()
        # Try sslproxies.org
        self._fetch_from_ssl_proxies()
        # Try spys.me
        self._fetch_from_spys_me()

        self.logger.info(f"Found {len(self.proxies)} potential proxies")

    def _fetch_from_free_proxy_list(self) -> None:
        try:
            response = requests.get(
                "https://free-proxy-list.net/",
                timeout=10,
                headers={'User-Agent': 'Mozilla/5.0'}
            )
            soup = BeautifulSoup(response.text, "html.parser")
            for row in soup.find("table", {"class": "table"}).find_all("tr")[1:]:
                cols = row.find_all("td")
                if len(cols) >= 7:
                    ip = cols[0].text.strip()
                    port = cols[1].text.strip()
                    https = cols[6].text.strip()
                    if https == "yes":
                        self.proxies.add(f"http://{ip}:{port}")
        except Exception as e:
            self.logger.error(f"Error fetching from free-proxy-list: {str(e)}")

    def _fetch_from_ssl_proxies(self) -> None:
        try:
            response = requests.get(
                "https://www.sslproxies.org/",
                timeout=10,
                headers={'User-Agent': 'Mozilla/5.0'}
            )
            soup = BeautifulSoup(response.text, "html.parser")
            for row in soup.find("table", {"class": "table"}).find_all("tr")[1:]:
                cols = row.find_all("td")
                if len(cols) >= 7:
                    ip = cols[0].text.strip()
                    port = cols[1].text.strip()
                    self.proxies.add(f"http://{ip}:{port}")
        except Exception as e:
            self.logger.error(f"Error fetching from sslproxies: {str(e)}")

    def _fetch_from_spys_me(self) -> None:
        try:
            response = requests.get(
                "https://spys.me/proxy.txt",
                timeout=10,
                headers={'User-Agent': 'Mozilla/5.0'}
            )
            # Parse IP:Port format
            pattern = r'(\d+\.\d+\.\d+\.\d+:\d+)'
            matches = re.findall(pattern, response.text)
            for proxy in matches:
                self.proxies.add(f"http://{proxy}")
        except Exception as e:
            self.logger.error(f"Error fetching from spys.me: {str(e)}")

    async def validate_proxy(self, proxy: str) -> bool:
        """Validate a single proxy"""
        try:
            timeout = aiohttp.ClientTimeout(total=5)  # Reduced timeout
            connector = aiohttp.TCPConnector(ssl=False)
            async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
                try:
                    async with session.get(
                        "http://httpbin.org/ip",  # Changed to non-SSL endpoint
                        proxy=proxy,
                    ) as response:
                        if response.status == 200:
                            self.logger.info(f"Valid proxy found: {proxy}")
                            return True
                except Exception as e:
                    self.logger.debug(f"Proxy {proxy} failed: {str(e)}")
                    return False
        except Exception as e:
            self.logger.debug(f"Proxy {proxy} validation error: {str(e)}")
            return False
        return False

    async def validate_proxies(self, batch_size: int = 10) -> List[str]:
        """Validate proxies in batches"""
        valid_proxies = []
        proxies_list = list(self.proxies)

        for i in range(0, len(proxies_list), batch_size):
            batch = proxies_list[i:i + batch_size]
            tasks = [self.validate_proxy(proxy) for proxy in batch]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            for proxy, is_valid in zip(batch, results):
                if isinstance(is_valid, bool) and is_valid:
                    valid_proxies.append(proxy)

            self.logger.info(f"Validated batch {i//batch_size + 1}, "
                           f"found {len(valid_proxies)} valid proxies so far")

        self.validated_proxies = valid_proxies
        return valid_proxies

async def main():
    proxy_getter = GetProxies()
    print(f"Found {len(proxy_getter.proxies)} potential proxies")

    validated_proxies = await proxy_getter.validate_proxies(batch_size=5)
    print(f"\nValidated proxies ({len(validated_proxies)}):")
    for proxy in validated_proxies:
        print(proxy)

if __name__ == "__main__":
    asyncio.run(main())
