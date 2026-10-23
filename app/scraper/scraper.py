import re
from datetime import datetime
from typing import Optional, Dict
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)

class ProcessScraper:
    def __init__(self):
        pass

    def scrape_process_from_link(self, page, link: str) -> Optional[Dict]:
        """
        Scrape process details from the process page.
        :param page: Playwright page object (already on the process page or we need to goto).
        :param link: URL of the process page.
        :return: Dictionary with keys: numero, data, assunto, tipo or None if failed.
        """
        try:
            logger.info(f"Scraping process page: {link}")
            # Navigate to the link if not already there
            if page.url != link:
                page.goto(link, wait_until="networkidle")
            # Wait for main content to load
            page.wait_for_timeout(2000)  # small wait for dynamic content

            # Get page content
            content = page.content()
            soup = BeautifulSoup(content, 'html.parser')

            # Extract data using common patterns in SEI process pages
            # We'll try to find the numero do processo, data, assunto, tipo
            numero = self._extract_numero(soup)
            data = self._extract_data(soup)
            assunto = self._extract_assunto(soup)
            tipo = self._extract_tipo(soup)

            # If we couldn't find essential data, log and return None
            if not numero and not assunto:
                logger.warning("Could not extract essential process data (numero or assunto).")
                return None

            return {
                'numero': numero or '',
                'data': data,
                'assunto': assunto or '',
                'tipo': tipo or ''
            }
        except Exception as e:
            logger.exception(f"Error scraping process page {link}: {e}")
            return None

    def _extract_numero(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract the process number."""
        # Common patterns: label "Número:" or "Número do Processo:"
        # Look for text followed by the number in a sibling or parent element.
        # We'll search for elements containing "Número" and get the next sibling's text.
        labels = soup.find_all(string=re.compile(r'Número', re.I))
        for label in labels:
            # Get parent element and look for the value
            parent = label.parent
            # The value might be in the next sibling or in a span with class 'valor'
            # Try to find a sibling with class 'valor' or just get text after colon.
            next_sibling = parent.find_next_sibling()
            if next_sibling:
                text = next_sibling.get_text(strip=True)
                if text and re.search(r'\d{4}/\d+', text):  # pattern like 2026/0012345678
                    return text
            # Alternatively, the label and value might be in the same element separated by ':'
            full_text = parent.get_text(strip=True)
            if ':' in full_text:
                possible = full_text.split(':', 1)[1].strip()
                if possible and re.search(r'\d{4}/\d+', possible):
                    return possible
        # Fallback: search for pattern directly in page text
        import re
        text = soup.get_text()
        match = re.search(r'(\d{4}/\d{7,8})', text)
        if match:
            return match.group(1)
        return None

    def _extract_data(self, soup: BeautifulSoup) -> Optional[datetime]:
        """Extract the process date (data de distribuição or similar)."""
        labels = soup.find_all(string=re.compile(r'Data', re.I))
        for label in labels:
            parent = label.parent
            full_text = parent.get_text(strip=True)
            if ':' in full_text:
                possible = full_text.split(':', 1)[1].strip()
                # Try to parse date in format DD/MM/AAAA
                try:
                    return datetime.strptime(possible, "%d/%m/%Y")
                except ValueError:
                    pass
            # Look for next sibling with date pattern
            next_sibling = parent.find_next_sibling()
            if next_sibling:
                text = next_sibling.get_text(strip=True)
                try:
                    return datetime.strptime(text, "%d/%m/%Y")
                except ValueError:
                    pass
        # Fallback: search for date pattern in text
        import re
        text = soup.get_text()
        match = re.search(r'(\d{2}/\d{2}/\d{4})', text)
        if match:
            try:
                return datetime.strptime(match.group(1), "%d/%m/%Y")
            except ValueError:
                pass
        return None

    def _extract_assunto(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract the process subject/assunto."""
        labels = soup.find_all(string=re.compile(r'Assunto', re.I))
        for label in labels:
            parent = label.parent
            full_text = parent.get_text(strip=True)
            if ':' in full_text:
                possible = full_text.split(':', 1)[1].strip()
                if possible:
                    return possible
            next_sibling = parent.find_next_sibling()
            if next_sibling:
                text = next_sibling.get_text(strip=True)
                if text:
                    return text
        # Fallback: look for a textarea or div with id containing 'assunto'
        assunto_elem = soup.find('textarea', id=re.compile('assunto', re.I))
        if assunto_elem:
            return assunto_elem.get_text(strip=True)
        assunto_elem = soup.find('div', id=re.compile('assunto', re.I))
        if assunto_elem:
            return assunto_elem.get_text(strip=True)
        return None

    def _extract_tipo(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract the process type (tipo)."""
        labels = soup.find_all(string=re.compile(r'Tipo', re.I))
        for label in labels:
            parent = label.parent
            full_text = parent.get_text(strip=True)
            if ':' in full_text:
                possible = full_text.split(':', 1)[1].strip()
                if possible:
                    return possible
            next_sibling = parent.find_next_sibling()
            if next_sibling:
                text = next_sibling.get_text(strip=True)
                if text:
                    return text
        # Fallback: look for a field with name or id containing 'tipo'
        tipo_elem = soup.find('input', {'name': re.compile('tipo', re.I)})
        if tipo_elem and tipo_elem.get('value'):
            return tipo_elem['value']
        tipo_elem = soup.find('select', {'name': re.compile('tipo', re.I)})
        if tipo_elem:
            selected = tipo_elem.find('option', selected=True)
            if selected:
                return selected.get_text(strip=True)
        return None