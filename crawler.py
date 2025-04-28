# crawler.py

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, parse_qs
import time

def get_all_links(start_url, max_pages=20):
    visited = set()
    to_visit = [start_url]
    domain = urlparse(start_url).netloc
    results = {}

    while to_visit and len(visited) < max_pages:
        current_url = to_visit.pop(0)

        if current_url in visited:
            continue

        try:
            response = requests.get(current_url, timeout=5)
            if response.status_code != 200:
                continue

            visited.add(current_url)
            soup = BeautifulSoup(response.text, "html.parser")

            # Parse parameters
            parsed_url = urlparse(current_url)
            params = parse_qs(parsed_url.query)
            flat_params = {key: val[0] if val else "" for key, val in params.items()}
            results[current_url] = flat_params

            # Find all internal links
            for link in soup.find_all("a", href=True):
                href = link["href"]
                full_url = urljoin(current_url, href)
                parsed = urlparse(full_url)

                if parsed.netloc == domain and full_url not in visited and full_url not in to_visit:
                    to_visit.append(full_url)

            # Be nice to servers
            time.sleep(0.5)

        except Exception as e:
            print(f"[!] Error crawling {current_url}: {e}")
            continue

    return results
