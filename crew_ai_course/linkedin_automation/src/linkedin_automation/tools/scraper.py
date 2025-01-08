from crewai.tools import BaseTool
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup  # For processing the HTML content

class PlaywrightScraperTool(BaseTool):
    name: str = "Playwright Web Scraper"
    description: str = "Scrapes content from a specified URL using Playwright."

    async def _run(self, task_config: dict) -> dict:
        url = task_config.get("url")
        if not url:
            return {"error": "No URL provided in the task configuration."}

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(url, wait_until="networkidle")
            content = await page.content()
            await browser.close()

        # Parse the content using BeautifulSoup
        soup = BeautifulSoup(content, "html.parser")
        main_content = soup.get_text(separator="\n", strip=True)
        headings = [h.get_text(strip=True) for h in soup.find_all(["h1", "h2", "h3"])]
        links = [a["href"] for a in soup.find_all("a", href=True)]

        return {
            "url": url,
            "headings": headings,
            "content": main_content[:2000],  # Truncate long content
            "links": links,
        }
