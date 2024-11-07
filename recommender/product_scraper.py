import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union

import aiohttp
from bs4 import BeautifulSoup
from bs4.element import NavigableString, Tag

from recommender.proxies import GetProxies
from recommender.proxy_manager import ProxyManager
from recommender.rate_limiter import RateLimiter


class AmazonURLBuilder:
    BASE_URL = "https://www.amazon.com"

    @staticmethod
    def search_url(query: str) -> str:
        """Create search URL from query"""
        return f"{AmazonURLBuilder.BASE_URL}/s?k={query.replace(' ', '+')}"

    @staticmethod
    def product_url(asin: str) -> str:
        """Create product URL from ASIN"""
        return f"{AmazonURLBuilder.BASE_URL}/dp/{asin}"


class DataSaver:
    def __init__(self, base_dir: str = "data/products"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def save_product_data(self, product_data: Dict) -> None:
        """Save product data to JSON file"""
        if not product_data or "title" not in product_data:
            return

        # Create a safe filename from the title
        safe_title = "".join(
            c if c.isalnum() else "_" for c in product_data["title"][:50]
        )
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{safe_title}_{timestamp}.json"

        file_path = self.base_dir / filename

        # Add timestamp to the data
        product_data["scraped_at"] = datetime.now().isoformat()

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(product_data, f, indent=2, ensure_ascii=False)

        logging.info(f"Saved product data to {file_path}")


class AmazonScraper:
    def __init__(
        self,
        rate_limiter: Optional[RateLimiter] = None,
        proxy_manager: Optional[ProxyManager] = None,
    ):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Cache-Control": "max-age=0",
        }
        self.cookies = {}  # Will store session cookies
        self.url_builder = AmazonURLBuilder()
        self.data_saver = DataSaver()
        self.rate_limiter = rate_limiter or RateLimiter(
            requests_per_second=0.2
        )  # Slower rate
        self.proxy_manager = proxy_manager

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
        )
        self.logger = logging.getLogger(__name__)

    async def _get_page(self, url: str) -> Optional[BeautifulSoup]:
        """Fetch the page content with improved error handling and retry logic"""
        max_retries = 5  # Increased retries
        backoff_factor = 2

        for attempt in range(max_retries):
            try:
                await self.rate_limiter.acquire()

                proxy = None
                if self.proxy_manager:
                    proxy = self.proxy_manager.get_next_proxy()

                timeout = aiohttp.ClientTimeout(total=30)

                # Configure session with better options
                session_kwargs = {
                    "timeout": timeout,
                    "headers": self.headers,
                    "cookies": self.cookies,
                    "trust_env": True,
                }

                async with aiohttp.ClientSession(**session_kwargs) as session:
                    request_kwargs: Optional[Dict] = {"ssl": False}
                    if proxy:
                        request_kwargs["proxy"] = proxy
                    async with session.get(url, **request_kwargs) as response:
                        # Store cookies from response
                        self.cookies.update(response.cookies)

                        if response.status == 200:
                            content = await response.text()
                            soup = BeautifulSoup(content, "html.parser")

                            # Check for CAPTCHA or other blocking pages
                            if self._is_blocked(soup):
                                self.logger.warning(
                                    "Detected blocking page, rotating proxy..."
                                )
                                await asyncio.sleep(backoff_factor**attempt)
                                continue

                            return soup

                        elif response.status in [503, 403, 202]:
                            self.logger.warning(
                                f"Access denied (Status: {response.status}) on attempt {attempt + 1}. "
                                "Rotating proxy and waiting..."
                            )
                            await asyncio.sleep(backoff_factor**attempt)

                        else:
                            self.logger.error(
                                f"Failed to fetch page. Status code: {response.status}"
                            )

                # Switch proxy after each failed attempt
                if self.proxy_manager:
                    self.proxy_manager.rotate_proxy()

            except Exception as e:
                self.logger.error(f"Attempt {attempt + 1} failed: {str(e)}")
                await asyncio.sleep(backoff_factor**attempt)
                continue

        return None

    def _is_blocked(self, soup: BeautifulSoup) -> bool:
        """Check if the page is a blocking page (CAPTCHA, robot check, etc.)"""
        blocking_indicators = [
            "robot check",
            "captcha",
            "verify you're a human",
            "automated access",
            "unusual activity",
        ]

        page_text = soup.get_text().lower()
        return any(indicator in page_text for indicator in blocking_indicators)

    def _extract_asin(
        self, element: Union[Tag, NavigableString]
    ) -> Optional[str]:
        """Helper method to safely extract ASIN"""
        if isinstance(element, Tag):
            asin = element.get("data-asin") or element.get("data-component-id")
            if isinstance(asin, str) and len(asin) == 10:
                return asin
        return None

    async def search_product(self, query: str) -> Optional[str]:
        """Search for a product and return its ASIN"""
        search_url = self.url_builder.search_url(query)
        self.logger.info(f"Searching for product: {query}")

        soup = await self._get_page(search_url)
        if not soup:
            return None

        # Try different patterns to find product ASIN
        patterns = [
            ("div", {"data-asin": True}),
            ("div", {"data-component-id": True}),
            ("a", {"data-asin": True}),
        ]

        for tag, attrs in patterns:
            element = soup.find(tag, attrs)
            if element and isinstance(element, Tag):
                asin = self._extract_asin(element)
                if asin:  # Valid ASIN is 10 characters
                    self.logger.info(f"Found ASIN: {asin}")
                    return asin

        self.logger.error("No valid ASIN found in search results")
        return None

    async def scrape_product(
        self, product_identifier: str, is_asin: bool = False
    ) -> Optional[Dict]:
        """
        Scrape product information from Amazon product page

        Args:
            product_identifier: Either an ASIN or product search query
            is_asin: Boolean indicating if product_identifier is an ASIN
        """
        try:
            if is_asin:
                product_url = self.url_builder.product_url(product_identifier)
                asin = product_identifier
            else:
                asin = await self.search_product(product_identifier)
                if not asin:
                    self.logger.error(
                        f"Could not find ASIN for query: {product_identifier}"
                    )
                    return None
                product_url = self.url_builder.product_url(asin)

            self.logger.info(f"Scraping product URL: {product_url}")
            soup = await self._get_page(product_url)
            if not soup:
                return None

            product_data = {
                "url": product_url,
                "asin": asin,
                "title": self._extract_title(soup),
                "price": self._extract_price(soup),
                "currency": self._extract_currency(soup),
                "rating": self._extract_rating(soup),
                "review_count": self._extract_review_count(soup),
                "availability": self._extract_availability(soup),
                "description": self._extract_description(soup),
                "features": self._extract_features(soup),
                "categories": self._extract_categories(soup),
                "brand": self._extract_brand(soup),
                "scraped_at": datetime.now().isoformat(),
            }

            # Validate essential fields
            if not product_data["title"]:
                self.logger.error("Failed to extract product title")
                return None

            # Save the data
            self.data_saver.save_product_data(product_data)

            self.logger.info(
                f"Successfully scraped product: {product_data['title']}"
            )
            return product_data

        except Exception as e:
            self.logger.error(f"Failed to scrape product. Error: {str(e)}")
            return None

    def _extract_title(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract product title"""
        title_element = soup.find("span", {"id": "productTitle"})
        return title_element.get_text().strip() if title_element else None

    def _extract_price(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract product price"""
        price_patterns = [
            ("span", {"class": "a-price-whole"}),
            ("span", {"class": "a-offscreen"}),
            ("span", {"id": "priceblock_ourprice"}),
            ("span", {"id": "priceblock_dealprice"}),
        ]

        for tag, attrs in price_patterns:
            price_element = soup.find(tag, attrs)
            if price_element:
                price_text = price_element.get_text().strip()
                # Remove currency symbols and convert to decimal
                price_text = "".join(
                    filter(lambda x: x.isdigit() or x == ".", price_text)
                )
                return price_text
        return None

    def _extract_currency(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract price currency"""
        currency_element = soup.find("span", {"class": "a-price-symbol"})
        return currency_element.get_text().strip() if currency_element else None

    def _extract_rating(self, soup: BeautifulSoup) -> Optional[float]:
        """Extract product rating"""
        rating_element = soup.find("span", {"class": "a-icon-alt"})
        if rating_element:
            try:
                rating_text = rating_element.get_text().strip()
                return float(rating_text.split(" ")[0])
            except (ValueError, IndexError):
                return None
        return None

    def _extract_review_count(self, soup: BeautifulSoup) -> Optional[int]:
        """Extract product review count"""
        review_count_element = soup.find(
            "span", {"id": "acrCustomerReviewText"}
        )
        if review_count_element:
            try:
                count_text = (
                    review_count_element.get_text().split()[0].replace(",", "")
                )
                return int(count_text)
            except (ValueError, IndexError):
                return None
        return None

    def _extract_availability(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract product availability"""
        availability_element = soup.find(
            "div", {"id": "availability"}
        ) or soup.find("span", {"class": "a-size-medium a-color-success"})
        return (
            availability_element.get_text().strip()
            if availability_element
            else None
        )

    def _extract_description(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract product description"""
        description_element = soup.find(
            "div", {"id": "productDescription"}
        ) or soup.find("div", {"id": "feature-bullets"})
        return (
            description_element.get_text().strip()
            if description_element
            else None
        )

    def _extract_features(self, soup: BeautifulSoup) -> List[str]:
        """Extract product features"""
        features = []
        feature_list = soup.find("div", {"id": "feature-bullets"})
        if feature_list and isinstance(feature_list, Tag):
            for feature in feature_list.find_all(
                "span", {"class": "a-list-item"}
            ):
                if isinstance(feature, Tag):
                    feature_text = feature.get_text().strip()
                    if feature_text:
                        features.append(feature_text)
        return features

    def _extract_categories(self, soup: BeautifulSoup) -> List[str]:
        """Extract product categories"""
        categories = []
        breadcrumb = soup.find(
            "div", {"id": "wayfinding-breadcrumbs_feature_div"}
        )
        if breadcrumb and isinstance(breadcrumb, Tag):
            for category in breadcrumb.find_all("a"):
                if isinstance(category, Tag):
                    category_text = category.get_text().strip()
                    if category_text:
                        categories.append(category_text)
        return categories

    def _extract_brand(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract product brand"""
        brand_element = soup.find("a", {"id": "bylineInfo"})
        return brand_element.get_text().strip() if brand_element else None


async def main():
    logger = logging.getLogger(__name__)

    try:
        get_proxies = GetProxies()
        logger.info("Fetching and validating proxies...")
        validated_proxies = await get_proxies.validate_proxies(batch_size=5)

        if not validated_proxies:
            logger.warning("No valid proxies found. Running without proxy.")
            proxy_manager = None
        else:
            logger.info(f"Found {len(validated_proxies)} valid proxies")
            proxy_manager = ProxyManager(validated_proxies)

        rate_limiter = RateLimiter(requests_per_second=0.2)  # Slower rate
        scraper = AmazonScraper(
            rate_limiter=rate_limiter, proxy_manager=proxy_manager
        )

        # Example URLs to scrape with more variety
        products_to_scrape = [
            # Search queries with multiple attempts
            ("Samsung Galaxy S24 Ultra", False),
            ("Samsung Galaxy S24", False),  # Alternative if Ultra fails
            ("iPhone 15 Pro Max", False),
            ("iPhone 15", False),  # Alternative if Pro Max fails
            # Direct ASINs (verified working ones)
            ("B0CHX3QBCH", True),
            ("B0CMKR9F8X", True),
        ]

        # Scrape products with better error handling
        for product_id, is_asin in products_to_scrape:
            try:
                logger.info(
                    f"Scraping {'ASIN' if is_asin else 'product'}: {product_id}"
                )

                # Multiple attempts for each product
                for attempt in range(3):
                    product_data = await scraper.scrape_product(
                        product_identifier=product_id, is_asin=is_asin
                    )

                    if product_data:
                        logger.info(
                            f"Successfully scraped: {product_data.get('title')}"
                        )
                        break

                    logger.warning(
                        f"Attempt {attempt + 1} failed for {product_id}"
                    )
                    await asyncio.sleep(5)  # Wait between attempts

                    if not product_data:
                        logger.error(f"All attempts failed for: {product_id}")

                # Longer delay between products
                await asyncio.sleep(5)

            except Exception as e:
                logger.error(f"Error processing {product_id}: {str(e)}")
                continue

        logger.info("Scraping completed")

    except Exception as e:
        logger.error(f"Scraping failed: {str(e)}")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Scraping interrupted by user")
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
