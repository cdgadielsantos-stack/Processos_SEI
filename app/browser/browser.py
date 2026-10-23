from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from pathlib import Path
import time
import logging

logger = logging.getLogger(__name__)

class ANEELBrowser:
    def __init__(self, headless=False):
        """
        Initialize the browser wrapper.
        :param headless: Run browser in headless mode (False for CAPTCHA solving).
        """
        self.headless = headless
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    def launch(self):
        """Launch the browser and create a new page."""
        logger.info(f"Launching Playwright browser (headless={self.headless})")
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=self.headless)
        self.context = self.browser.new_context(
            viewport={'width': 1280, 'height': 720},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        self.page = self.context.new_page()
        # Set default timeout
        self.page.set_default_timeout(30000)  # 30 seconds

    def close(self):
        """Close the browser and cleanup."""
        logger.info("Closing browser")
        if self.page:
            self.page.close()
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
        self.page = None
        self.context = None
        self.browser = None
        self.playwright = None

    def navigate_to(self, url):
        """Navigate to a URL."""
        logger.info(f"Navigating to: {url}")
        self.page.goto(url, wait_until="networkidle")

    def fill_date_fields(self, data_inicial, data_final):
        """
        Fill the date input fields.
        Assumes the page has inputs with IDs or placeholders for dates.
        Based on inspection of SEI page, the fields have IDs:
        - txtDataInicial
        - txtDataFinal
        """
        logger.info(f"Filling date fields: {data_inicial} to {data_final}")
        self.page.fill("#txtDataInicial", data_inicial)
        self.page.fill("#txtDataFinal", data_final)

    def click_search(self):
        """Click the search button."""
        logger.info("Clicking search button")
        # The search button has ID: btnPesquisar
        self.page.click("#btnPesquisar")
        # Wait for navigation or loading
        self.page.wait_for_load_state("networkidle")

    def wait_for_human_captcha(self, timeout=300):
        logger.info(
            "Resolva o CAPTCHA e clique em Pesquisar."
        )

        input(
            "\nQuando os resultados estiverem visíveis, pressione ENTER no terminal..."
        )

        return True

        raise TimeoutError("CAPTCHA solving timeout exceeded.")

    def wait_for_results(self, timeout=30):
        """
        Wait for the search results to load after clicking search.
        """
        logger.info("Waiting for search results...")
        try:
            # Wait for the results table to be visible
            self.page.wait_for_selector("table.tblResultado, table#tblResultado", timeout=timeout*1000)
            return True
        except PlaywrightTimeoutError:
            logger.warning("Timeout waiting for results.")
            return False

    def collect_process_links(self):
        """
        Collect all process links from the results table.
        Each row in the results table has a link to the process details.
        Returns a list of URLs.
        """
        logger.info("Collecting process links from results page")
        links = []
        # Find all links that point to process details.
        # The SEI results table has links with class 'linkProcesso' or similar.
        # We'll use a generic selector: anchor tags within the results table.
        rows = self.page.query_selector_all("table.tblResultado tbody tr, table#tblResultado tbody tr")
        for row in rows:
            # Find the link in the row (usually in the second column)
            link_elem = row.query_selector("a")
            if link_elem:
                href = link_elem.get_attribute("href")
                if href:
                    # Make absolute URL if relative
                    if href.startswith("http"):
                        links.append(href)
                    else:
                        # Base URL from SEI
                        base = "https://sei.aneel.gov.br"
                        links.append(base + href)
        # Also try alternative selector: any link with 'acao=protocolo' or 'visualizar'
        if not links:
            anchors = self.page.query_selector_all("a[href*='acao=protocolo'], a[href*='visualizar']")
            for a in anchors:
                href = a.get_attribute("href")
                if href:
                    if href.startswith("http"):
                        links.append(href)
                    else:
                        base = "https://sei.aneel.gov.br"
                        links.append(base + href)
        # Deduplicate
        links = list(dict.fromkeys(links))
        logger.info(f"Collected {len(links)} unique process links.")
        return links

    def get_page(self):
        """Return the current page object for use by scraper."""
        return self.page