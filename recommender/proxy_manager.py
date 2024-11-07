from typing import List, Optional


class ProxyManager:
    def __init__(self, proxies: List[str], max_uses: int = 3):
        self.proxies = proxies
        self.max_uses = max_uses
        self._current_index = 0
        self._uses = 0
        self._working_proxies = set(proxies)
        self._failed_proxies = set()

    def get_next_proxy(self) -> Optional[str]:
        if not self._working_proxies:
            self._recover_failed_proxies()
            if not self._working_proxies:
                return None

        if self._uses >= self.max_uses:
            self.rotate_proxy()

        proxy = list(self._working_proxies)[self._current_index]
        self._uses += 1
        return proxy

    def rotate_proxy(self):
        """Force rotation to next proxy"""
        self._current_index = (self._current_index + 1) % len(
            self._working_proxies
        )
        self._uses = 0

    def mark_proxy_failed(self, proxy: str):
        """Mark a proxy as failed"""
        if proxy in self._working_proxies:
            self._working_proxies.remove(proxy)
            self._failed_proxies.add(proxy)

    def _recover_failed_proxies(self):
        """Recover failed proxies after a cooldown"""
        self._working_proxies.update(self._failed_proxies)
        self._failed_proxies.clear()
        self._current_index = 0
        self._uses = 0
