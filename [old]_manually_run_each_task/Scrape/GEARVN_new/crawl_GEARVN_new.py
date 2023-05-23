from Scrape.utils import convert
from Scrape.utils.base_class import BaseScraper


class GearvnScraper(BaseScraper):
    def __init__(self):
        super(GearvnScraper, self).__init__(driver_type="edge")
        self.main_laptop_links = ["https://gearvn.com/collections/laptop-hoc-tap-va-lam-viec-duoi-15tr",
                                  "https://gearvn.com/collections/laptop-hoc-tap-va-lam-viec-tu-15tr-den-20tr",
                                  "https://gearvn.com/collections/laptop-hoc-tap-va-lam-viec-tren-20-trieu",
                                  "https://gearvn.com/collections/macbook-air",
                                  "https://gearvn.com/collections/macbook-pro",
                                  "https://gearvn.com/collections/laptop-gaming-gia-duoi-20-trieu",
                                  "https://gearvn.com/collections/laptop-gaming-gia-tu-20-den-25-trieu",
                                  "https://gearvn.com/collections/laptop-gaming-gia-tu-25-den-35-trieu",
                                  "https://gearvn.com/collections/laptop-gaming-tren-35-trieu", ]

    def _write(self, base_info, specs):
        base_info.update(specs)
        self._append_jsonl_file("GEARVN_used.jsonl", base_info)

    def _parse_basic_info(self):
        warranty_raw = self.driver.find_elements_by_css_selector("div.product_parameters span")
        warranty = [span.text for span in warranty_raw if "bảo hành" in span.text.lower()]
        basic_info = {"Tên": self.driver.find_element_by_class_name("product_name").text,
                      "Giá": self.driver.find_element_by_class_name("product_sale_price").text,
                      "Bảo hành": warranty[0].split(":")[-1].strip() if len(warranty) > 0 else None}
        return basic_info

    def _parse_specifications(self):
        specs_info = {}
        table_specs = self.driver.find_elements_by_css_selector("table#tblGeneralAttribute>tbody>tr>td")
        table_specs_text = [spec.text for spec in table_specs]
        for i in range(0, len(table_specs_text), 2):
            specs_info[table_specs_text[i]] = table_specs_text[i + 1]
        return specs_info

    def parse(self, *args, export=False) -> None:
        for link in self.main_laptop_links:
            self._go_to_new_tab(link=link)
            laptops = self.driver.find_elements_by_class_name("content-product-list > div")
            try:
                for laptop in laptops:
                    link = laptop.find_element_by_css_selector("div:first-child>a:first-child").get_attribute("href")
                    self._go_to_new_tab(link=link)
                    basic_info = self._parse_basic_info()
                    specs = self._parse_specifications()
                    self.driver.close()
                    self._go_to_last_tab()
                    self._write(basic_info, specs)
                self.driver.close()
                self._go_to_first_tab()
            except BaseException as e:
                print(e)
                print("Lỗi sản phẩm")


# %%
bot = GearvnScraper()
bot.parse(export=True)

# %%
raw_data = convert.read_results("Scrape/GEARVN_new/GEARVN_used.jsonl")
max_columns = convert.get_spec_fields(raw_data)
df = convert.make_frame(raw_data, max_columns)
df.to_csv("raw_data_GEARVN_used.csv", index=False)


for i in range(len(df)):
    name = df.iloc[i, -1].lower()
    if "laptop gaming " in name:
        name = name.replace("laptop gaming ", "")
    if "laptop " in name:
        name = name.replace("laptop ", "")
    df.iloc[i, -1] = name
