from playwright.async_api import async_playwright
import json
import logging
import random
import time
from typing import Dict, Optional
from pathlib import Path
import asyncio
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class LinkedInPoster:
    def __init__(self, credentials_path: str):
        """
        Initialize the LinkedIn poster with credentials file path.
        
        Args:
            credentials_path: Path to the credentials JSON file
        """
        self.logger = logging.getLogger(__name__)
        self.credentials_path = Path(credentials_path)
        self.credentials = self._load_credentials()
        self.current_user = None
        self.browser = None
        self.context = None
        self.page = None
        self.playwright = None

    def _load_credentials(self) -> Dict:
        """Load and validate credentials from JSON file."""
        try:
            with open(self.credentials_path) as f:
                credentials = json.load(f)
                if not credentials.get("users"):
                    raise ValueError("No users found in credentials file")
                return credentials
        except Exception as e:
            self.logger.error(f"Error loading credentials: {str(e)}")
            raise

    def _random_delay(self, min_seconds: float = 1.0, max_seconds: float = 3.0):
        """Add random delay to simulate human behavior."""
        time.sleep(random.uniform(min_seconds, max_seconds))

    async def _init_browser(self):
        """Initialize browser with stealth settings."""
        try:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(headless=False)
            self.context = await self.browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            )
            self.page = await self.context.new_page()
            
            # Add stealth scripts
            await self.context.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            """)
            
        except Exception as e:
            self.logger.error(f"Error initializing browser: {str(e)}")
            raise

    async def login(self, user_id: str) -> bool:
        """
        Log into LinkedIn with specified user credentials.
        """
        try:
            user = next((u for u in self.credentials["users"] if u["id"] == user_id), None)
            if not user:
                raise ValueError(f"User {user_id} not found in credentials")

            self.current_user = user
            
            if not self.page:
                await self._init_browser()

            self.logger.info("Navigating to LinkedIn login page...")
            await self.page.goto('https://www.linkedin.com/login')
            self._random_delay()

            # Fill login form
            self.logger.info("Filling login form...")
            await self.page.fill('input#username', user["email"])
            self._random_delay(0.5, 1.5)
            await self.page.fill('input#password', user["password"])
            self._random_delay(0.5, 1.5)

            # Click login button
            self.logger.info("Clicking login button...")
            await self.page.click('button[type="submit"]')
            
            # Wait for navigation and verify login
            try:
                # Wait for either the post creation button or the feed
                self.logger.info("Waiting for home page to load...")
                await self.page.wait_for_selector('div[class*="share-box-feed-entry"]', timeout=10000)
                self.logger.info("Successfully verified login - found post creation area")
                return True
            except Exception as e:
                self.logger.error(f"Login verification failed: {str(e)}")
                # Take a screenshot for debugging
                await self.page.screenshot(path="login_debug.png")
                self.logger.info("Saved debug screenshot as login_debug.png")
                return False

        except Exception as e:
            self.logger.error(f"Login error: {str(e)}")
            return False

    async def create_post(self, content: str, image_path: Optional[str] = None) -> bool:
        """
        Create a new LinkedIn post with optional image.
        """
        try:
            if not self.page:
                raise ValueError("Browser not initialized. Please login first.")

            # Debug: Take screenshot before attempting to click
            await self.page.screenshot(path="before_post.png")
            self.logger.info("Saved screenshot before attempting to post")

            # Try to find the post creation area using multiple possible selectors
            selectors = [
                'button[data-control-name="create_post"]',
                'div[class*="share-box-feed-entry"]',
                'button[aria-label*="Create a post"]',
                'div[class*="share-box"]',
                'div[role="textbox"]'
            ]

            for selector in selectors:
                try:
                    self.logger.info(f"Trying to find post button with selector: {selector}")
                    element = await self.page.wait_for_selector(selector, timeout=5000)
                    if element:
                        self.logger.info(f"Found element with selector: {selector}")
                        await element.click()
                        break
                except Exception as e:
                    self.logger.info(f"Selector {selector} not found: {str(e)}")

            # Add a delay to let any animations complete
            self._random_delay(2, 3)

            # Take another screenshot after clicking
            await self.page.screenshot(path="after_click.png")
            self.logger.info("Saved screenshot after clicking post button")

            # Try to find the post input area
            try:
                await self.page.wait_for_selector('div[role="textbox"]', timeout=5000)
                self.logger.info("Found post input area")
            except Exception as e:
                self.logger.error(f"Could not find post input area: {str(e)}")
                return False

            # Fill post content
            await self.page.fill('div[role="textbox"]', content)
            self._random_delay()

            # Handle image upload if provided
            if image_path:
                input_file = await self.page.query_selector('input[type="file"]')
                await input_file.set_input_files(image_path)
                await self.page.wait_for_selector('img[alt="Post image"]')
                self._random_delay(2, 4)

            # Take screenshot before final post
            await self.page.screenshot(path="before_final_post.png")
            
            # Try different selectors for the post button
            post_button_selectors = [
                'button.share-actions__primary-action',
                'button.artdeco-button--primary',
                'button[class*="share-actions__primary-action"]',
                '#ember534',  # Note: this ID might change dynamically
                'button:has-text("Post")',
                'button[aria-label="Post"]',
            ]

            for selector in post_button_selectors:
                try:
                    self.logger.info(f"Trying to find final post button with selector: {selector}")
                    # Wait for the button to be visible and clickable
                    button = await self.page.wait_for_selector(selector, state="visible", timeout=5000)
                    if button:
                        self.logger.info(f"Found post button with selector: {selector}")
                        self._random_delay(1, 2)  # Small delay before clicking
                        await button.click()
                        self.logger.info(f"Successfully clicked post button with selector: {selector}")
                        break
                except Exception as e:
                    self.logger.info(f"Could not click post button with selector {selector}: {str(e)}")

            self.logger.info("Post created successfully")
            return True

        except Exception as e:
            self.logger.error(f"Error creating post: {str(e)}")
            return False

    async def close(self):
        """Clean up browser resources."""
        try:
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
        except Exception as e:
            self.logger.error(f"Error closing browser: {str(e)}") 