from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

from Scrape.utils import convert
from Scrape.utils.base_class import BaseScraper


# %%

class DienMayXanhScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.driver.get("https://www.dienmayxanh.com/laptop/")
        try:
            while True:
                WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "view-more")))
                self.driver.find_element_by_class_name("view-more").click()
        except:
            self.laptops = self.driver.find_elements_by_xpath('//*[@id="categoryPage"]/div[3]/ul/li/a[1]')

    def parse(self, *args, export=False) -> None:
        for i, laptop in enumerate(self.laptops):
            print(f"Crawling {i + 1}/{len(self.laptops)}...")
            link = laptop.get_attribute("href")
            self._go_to_new_tab(link=link)
            try:
                result = {}
                name = self.driver.find_element_by_css_selector(".detail > h1").text
                price = self.driver.find_element_by_class_name("box-price-present").text
                result["Tên"] = name
                result["Giá"] = price

                self.driver.find_element_by_class_name("btn-short-spec").click()
                WebDriverWait(self.driver, 20).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "parameter-all"))
                )
                specs = self.driver.find_element_by_class_name("parameter-all").find_elements_by_tag_name("li")
                for spec in specs:
                    name = spec.find_element_by_class_name("ctLeft").text[:-1]
                    info = spec.find_element_by_class_name("ctRight").text
                    result[name] = info
                self._append_jsonl_file("DMX_new.jsonl", result) if export else print(result)
            except NoSuchElementException or TimeoutException:
                print("Sản phẫm lỗi")
                self._log_errors("DMX_new_log.txt", link)

            self._go_to_first_tab()
        self.driver.quit()


# %%
bot = DienMayXanhScraper()
bot.parse(export=True)

# %%

raw_data = convert.read_results("Scrape/DMX_new/log/DMX_new.jsonl")
max_columns = convert.get_spec_fields(raw_data)
df = convert.make_frame(raw_data, max_columns)
df.to_csv("raw_data_DMX_new.csv", index=False)
