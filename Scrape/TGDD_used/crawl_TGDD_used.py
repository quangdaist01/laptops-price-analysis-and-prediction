import pandas as pd
from Scrape.utils.base_class import BaseScraper
from Scrape.utils import convert


class TGDD_Scraper(BaseScraper):
    def __init__(self):
        super(TGDD_Scraper, self).__init__(driver_type="edge")
        self.driver.get("https://www.thegioididong.com/may-doi-tra/laptop")
        self._wait_and_click(".dong")
        try:
            while True:
                self._wait_and_click(".btnviewmoresp")
        except:
            self.laptops = self.driver.find_elements_by_css_selector('.products > li')

    def _parse_all_(self, sub_products):

        results = []

        name = self.driver.find_element_by_css_selector(".titleimei > h1").text
        for product in sub_products:
            try:
                self._wait_to_be_clickable(".products > li")

                result = {'Tên': name, "Giá máy cũ": product.find_element_by_css_selector("div:nth-child(2)").text}

                # Trích tiết kiệm
                discount = product.find_elements_by_css_selector('li > label:nth-child(3) > span')
                if discount:
                    result["Tiết kiệm"] = discount[0].text
                else:
                    result["Tiết kiệm"] = ''

                # Lấy thời gian bảo hành còn lại
                used_info = product.find_elements_by_tag_name("label")
                result["Bảo hành cũ"] = ""
                for info in used_info:
                    if "bảo hành:" in info.text.lower():
                        result["Bảo hành cũ"] = info.text

                results.append(result)
            except BaseException as e:
                # raise e
                failed_laptop = product.find_element_by_tag_name("img").get_attribute("alt")
                results.append(failed_laptop)
        return results

    def _parse_base_info(self):
        # Chuyển sang tab máy mới
        new_laptop_link = self.driver.find_element_by_link_text("Xem chi tiết máy mới").get_attribute("href")
        self._go_to_new_tab(link=new_laptop_link)

        # Lấy giá máy mới
        new_price = self.driver.find_elements_by_css_selector('.box-price-present')
        base_info = {"Giá máy mới": new_price[0].text if new_price else ''}

        # Lấy bảo hành của máy mới
        try:
            warranty = self.driver.find_element_by_css_selector(
                "ul.policy__list > li:nth-child(2) > p > b").text
            base_info["Bảo hành mới"] = warranty
        except:
            print("")
        try:
            warranty = self.driver.find_element_by_css_selector(".warranty")
            if warranty:
                base_info["Bảo hành mới"] = warranty.text
        except:
            # print("Không tìm thấy thông tin bảo hành")
            print("")

        # Lấy phần trăm + số tiền tiết kiệm
        if "ngừng" in base_info["Giá máy mới"]:
            discount = self.driver.find_elements_by_css_selector(".box_oldproduct > a > i > b")
            if discount:
                base_info["Tiết kiệm"] = discount[0].text

        # Lấy thông tin cấu hình
        specs = self._parse_similar_specifications()
        base_info.update(specs)

        self.driver.close()
        self._go_to_last_tab()

        return base_info

    def _parse_similar_specifications(self):
        specifications = {}
        self._wait_and_click(".btn-short-spec")
        self._wait_to_be_visible(".parameter-all li")
        specs = self.driver.find_elements_by_css_selector(".parameter-all li")
        for spec in specs:
            name = spec.find_element_by_class_name("ctLeft").text[:-1]
            info = spec.find_element_by_class_name("ctRight").text
            specifications[name] = info

        return specifications

    def parse(self, *args, export=False) -> None:
        num_laptops = len(self.laptops)
        for index, laptop in enumerate(self.laptops):
            # if index == 2:
            # self.driver.close()
            # print(f'Đã crawl xong 2 loại máy laptops.\n Cám ơn thầy đã xem')
            # break
            try:
                print(f'Crawling {index + 1}/{num_laptops}...')
                self._go_to_new_tab(link=laptop.find_element_by_tag_name("a").get_attribute("href"))
                sub_products = self.driver.find_elements_by_css_selector(".products > li")
                used_laptop_infos = self._parse_all_(sub_products)
                new_laptop_info = self._parse_base_info()
                result = self.combine_info(used_laptop_infos, new_laptop_info)
                self._write(result)

            except BaseException as e:
                # raise e
                print("Lỗi load trang")
            finally:
                self.driver.close()

            self._go_to_first_tab()

    def _write(self, results):
        for result in results:
            if isinstance(result, dict):
                self._append_jsonl_file("TGDD_used.jsonl", result)
            elif isinstance(result, str):
                self._log_errors("TGDD_used_log.txt", result)

    @staticmethod
    def combine_info(used_laptop_infos, new_laptop_info):
        used_laptop_infos = used_laptop_infos.copy()
        for info in used_laptop_infos:
            info.update(new_laptop_info)
        return used_laptop_infos


bot = TGDD_Scraper()
bot.parse(export=True)

# %% Convert raw jsonlines to csv

raw_data = convert.read_results("Scrape/TGDD_used/TGDD_used.jsonl")
max_columns = convert.get_spec_fields(raw_data)
df = convert.make_frame(raw_data, max_columns)
df.to_csv("raw_data_TGDD_all_used.csv", index=False)

# %%

# Lấy trung bình giá cũ của các máy cùng loại
df = pd.read_csv("Dataset/Raw/raw_data_TGDD_used_renamed.csv")
df_take_first_occurence = df.groupby("name")[df.COLUMNS].first()

df.to_csv("raw_data_TGDD_used.csv", index=False)
