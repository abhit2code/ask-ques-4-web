import asyncio
from playwright.async_api import async_playwright
import trafilatura
from bs4 import BeautifulSoup
import httpx
from typing import List, Dict, Any
from src.config.settings import settings
import re

class ContentProcessor:
    def __init__(self):
        self.chunk_size = settings.chunk_size
        self.chunk_overlap = settings.chunk_overlap
    
    async def fetch_content(self, url: str) -> str:
        """Try to get content from a URL - first with simple HTTP, then with browser if needed"""
        try:
            # Quick attempt with httpx first since it's way faster
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.get(url)
                if resp.status_code == 200:
                    html_content = resp.text
                    # trafilatura is pretty good at extracting main content
                    extracted = trafilatura.extract(html_content)
                    if extracted and len(extracted.strip()) > 100:
                        return extracted
            
            # If that didn't work, probably need JS rendering
            return await self._scrape_with_browser(url)
            
        except Exception as e:
            raise Exception(f"Couldn't fetch content from {url}: {str(e)}")
    
    async def _scrape_with_browser(self, url: str) -> str:
        """Use Playwright when the site needs JavaScript"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            try:
                # Wait for network to be mostly idle
                await page.goto(url, wait_until="networkidle", timeout=30000)
                html_content = await page.content()
                
                # Clean up the HTML with BeautifulSoup
                soup = BeautifulSoup(html_content, 'html.parser')
                
                # Remove stuff we don't want
                for unwanted in soup(["script", "style", "nav", "footer", "header"]):
                    unwanted.decompose()
                
                # Get the text
                text = soup.get_text()
                
                # Basic cleanup - remove extra whitespace
                lines = (line.strip() for line in text.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                cleaned_text = ' '.join(chunk for chunk in chunks if chunk)
                
                return cleaned_text
                
            finally:
                await browser.close()
    
    def chunk_content(self, content: str, url: str) -> List[Dict[str, Any]]:
        """Break content into smaller pieces for better search"""
        text_chunks = self._split_into_chunks(content)
        
        docs = []
        for idx, chunk in enumerate(text_chunks):
            if len(chunk.strip()) > 50:  # Skip tiny chunks
                docs.append({
                    "content": chunk,
                    "url": url,
                    "chunk_index": idx,
                    "metadata": {
                        "total_chunks": len(text_chunks),
                        "chunk_length": len(chunk)
                    }
                })
        
        return docs
    
    def _split_into_chunks(self, text: str) -> List[str]:
        """Split text into overlapping chunks - nothing fancy but it works"""
        # Try to split on paragraphs first
        paragraphs = re.split(r'\n\s*\n', text)
        chunks = []
        current_chunk = ""
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
                
            # Would this chunk be too big?
            if len(current_chunk) + len(para) > self.chunk_size:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                    # Add some overlap from the previous chunk
                    overlap_part = current_chunk[-self.chunk_overlap:] if len(current_chunk) > self.chunk_overlap else current_chunk
                    current_chunk = overlap_part + " " + para
                else:
                    # This paragraph is huge, need to split it up
                    sentences = re.split(r'[.!?]+', para)
                    for sentence in sentences:
                        sentence = sentence.strip()
                        if not sentence:
                            continue
                        if len(current_chunk) + len(sentence) > self.chunk_size:
                            if current_chunk:
                                chunks.append(current_chunk.strip())
                                current_chunk = sentence
                            else:
                                # Even the sentence is too long, split by words
                                words = sentence.split()
                                for word in words:
                                    if len(current_chunk) + len(word) > self.chunk_size:
                                        if current_chunk:
                                            chunks.append(current_chunk.strip())
                                            current_chunk = word
                                        else:
                                            current_chunk = word
                                    else:
                                        current_chunk += " " + word if current_chunk else word
                        else:
                            current_chunk += ". " + sentence if current_chunk else sentence
            else:
                current_chunk += "\n\n" + para if current_chunk else para
        
        # Don't forget the last chunk
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks
