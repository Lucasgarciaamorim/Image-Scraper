import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager


class GoogleImageScraper:
    def __init__(self):
        options = Options()
        options.add_argument("--window-size=800,600")
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    def build_search_url(self, query: str) -> str:
        return f"https://www.google.com/search?q={query}&udm=2&tbm=isch"

    def fetch_first_valid_image(self, query: str) -> str | None:
        self.driver.get(self.build_search_url(query))
        time.sleep(0.5)

        thumbnails = self.driver.find_elements(By.CSS_SELECTOR, "img.YQ4gaf")
        for thumb in thumbnails:
            try:
                width = int(thumb.get_attribute("width") or 0)
                height = int(thumb.get_attribute("height") or 0)
                if width < 70 or height < 70:
                    continue
                self.driver.execute_script("arguments[0].scrollIntoView(true);", thumb)
                ActionChains(self.driver).move_to_element(thumb).perform()
                thumb.click()
                time.sleep(0.5)
                images = self.driver.find_elements(By.CSS_SELECTOR, "img.sFlh5c.FyHeAf.iPVvYb")
                for img in images:
                    src = img.get_attribute("src")
                    if src and src.startswith("http"):
                        return src
            except Exception:
                continue
        return None

    def close(self):
        self.driver.quit()
