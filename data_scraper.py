import requests
from bs4 import BeautifulSoup
import re
import os

class DataScraper:
    def __init__(self, base_url="https://www.ca.gov/lafires/"):
        self.base_url = base_url
        self.visited_urls = set()
        self.data_dir = "data"
        os.makedirs(self.data_dir, exist_ok=True)
        
    def get_page_content(self, url):
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None
    
    def extract_text(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.extract()
            
        # Get text
        text = soup.get_text()
        
        # Break into lines and remove leading/trailing space
        lines = (line.strip() for line in text.splitlines())
        # Break multi-headlines into a line each
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        # Remove blank lines
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        return text
    
    def extract_links(self, html_content, current_url):
        soup = BeautifulSoup(html_content, 'html.parser')
        links = []
        
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            
            # Handle relative URLs
            if href.startswith('/'):
                href = f"https://www.ca.gov{href}"
            elif not href.startswith(('http://', 'https://')):
                href = f"{current_url.rstrip('/')}/{href.lstrip('/')}"
                
            # Only include links from the same domain
            if href.startswith(self.base_url) and href not in self.visited_urls:
                links.append(href)
                
        return links
    
    def scrape_site(self, max_pages=50):
        """Scrape the LA Fires website and save content to files"""
        queue = [self.base_url]
        page_count = 0
        
        while queue and page_count < max_pages:
            url = queue.pop(0)
            if url in self.visited_urls:
                continue
                
            print(f"Scraping: {url}")
            self.visited_urls.add(url)
            
            html_content = self.get_page_content(url)
            if not html_content:
                continue
                
            # Extract and save text content
            text_content = self.extract_text(html_content)
            
            # Create a filename from the URL
            filename = re.sub(r'[^\w]', '_', url.replace(self.base_url, ''))
            if not filename:
                filename = "index"
            
            with open(f"{self.data_dir}/{filename}.txt", 'w', encoding='utf-8') as f:
                f.write(text_content)
            
            # Extract links and add to queue
            links = self.extract_links(html_content, url)
            queue.extend(links)
            
            page_count += 1
            
        print(f"Scraped {page_count} pages")

if __name__ == "__main__":
    scraper = DataScraper()
    scraper.scrape_site()