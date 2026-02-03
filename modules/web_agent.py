
import asyncio
from playwright.async_api import async_playwright
import config

class WebAgent:
    def __init__(self):
        self.headless = False # Visible for demo
        
    async def run_task(self, url, task_description):
        """
        Navigates to a URL and performs actions.
        """
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.headless)
            page = await browser.new_page()
            
            try:
                await page.goto(url)
                
                # Simplified Logic: Just go there and screenshot for now
                # Real agent would use LLM to parse DOM
                await page.wait_for_load_state("networkidle")
                
                title = await page.title()
                return f"Visited {url}. Page Title: {title}"
                
            except Exception as e:
                return f"Web Task Failed: {e}"
            finally:
                await browser.close()

    def navigate(self, url):
        """Sync wrapper for navigation"""
        return asyncio.run(self.run_task(url, "open"))
