from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from Scrape.utils import convert
from Scrape.utils.base_class import BaseScraper


class FPTScraper(BaseScraper):
    def __init__(self):
        super(FPTScraper, self).__init__(driver_type="edge")
        self.driver.get("https://fptshop.com.vn/may-doi-tra/may-tinh-xach-tay-cu-gia-re")
        try:
            while True:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "cdt-product--loadmore")))
                self.driver.find_element_by_class_name("cdt-product--loadmore").click()
        except:
            self.laptops = self.driver.find_elements_by_css_selector(".mc-lprow>.mc-lpcol")

    def _write(self, base_info, results):
        for result in results:
            result.update(base_info)
        for result in results:
            if result.get("failed") is not None:
                self._append_jsonl_file("FPT_used.jsonl", result)
            else:
                self._log_errors("FPT_used_log.txt", result)

    def _parse_basic_info(self, laptop):
        basic_info = {"Tên": laptop.find_element_by_class_name("mc-lpiname").text,
                      "Giá mới": laptop.find_element_by_class_name("mc-lpri1").text}

        specs_info = {}
        # Search google with laptop's name plus "FPT" keyword
        self._go_to_new_tab(link="https://google.com")
        try:
            self._search_and_reach_laptop_page(basic_info["Tên"])
            specs_info = self._parse_specifications()
        except:
            print("Không trích được cấu hình chi tiết")
        finally:
            basic_info.update(specs_info)
            self.driver.close()
            self._go_to_first_tab()
        return basic_info

    def _parse_all_sub_laptops(self, laptop):
        self._go_to_new_tab(link=laptop.find_element_by_tag_name("a").get_attribute("href"))
        sub_laptops = self.driver.find_elements_by_css_selector(".mc-lprow>.mc-lpcol")
        results = []
        for laptop in sub_laptops:
            result = self._parse_a_sub_laptop(laptop)
            results.append(result)
        self.driver.close()
        self._go_to_first_tab()
        return results

    def _parse_a_sub_laptop(self, laptop):
        try:
            self._go_to_new_tab(link=laptop.find_element_by_tag_name("a").get_attribute("href"))
            WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, "mc-ctpri1")))
            result = {"Giá đã qua sử dụng": self.driver.find_element_by_class_name("mc-ctpri1").text,
                      "Hạn bảo hành": self.driver.find_element_by_css_selector(".mc-ctttm li:nth-of-type(2)").text}
            self.driver.close()
            self._go_to_last_tab()
        except BaseException as e:
            print(e)
            result = {"failed": laptop.text}
        return result

    def _search_and_reach_laptop_page(self, name):
        WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.NAME, "q")))
        search = self.driver.find_element_by_name("q")
        search.send_keys(name + " FPT")
        search.send_keys(Keys.RETURN)
        self.driver.implicitly_wait("5")
        first_result = self.driver.find_element_by_xpath(
            '/html/body/div[7]/div/div[9]/div[1]/div/div[2]/div[2]/div/div/div[1]').find_element_by_tag_name("a")
        first_result.click()

    def _parse_specifications(self):
        specs_info = {}

        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.LINK_TEXT, "Xem cấu hình chi tiết")))
        self.driver.find_element_by_link_text("Xem cấu hình chi tiết").click()
        WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located(
            (By.CSS_SELECTOR, "div.c-modal__content > div.c-modal__row > table.st-table td")))
        list_specs = self.driver.find_elements_by_css_selector(
            "div.c-modal__content > div.c-modal__row > table.st-table td")
        for i in range(0, len(list_specs) - 1, 2):
            specs_info[list_specs[i].text] = list_specs[i + 1].text

        table_specs = self.driver.find_elements_by_css_selector("ul.st-list > li")
        for info in table_specs:
            key, value = info.text.split(":  \n")
            specs_info[key] = value
        return specs_info

    def parse(self, *args, export=False) -> None:
        for laptop in self.laptops:
            try:
                basic_info = self._parse_basic_info(laptop)
                results = self._parse_all_sub_laptops(laptop)
                self._write(basic_info, results)
            except BaseException as e:
                print(e)
                print("Lỗi sản phẩm")


# %%
bot = FPTScraper()
bot.parse(export=True)

# %%

raw_data = convert.read_results("Scrape/FPT_used/FPT_used.jsonl")
max_columns = convert.get_spec_fields(raw_data)
df = convert.make_frame(raw_data, max_columns)
df.to_csv("raw_data_FPT_used.csv", index=False)
