import re
import string
import numpy as np

alternative_names = \
    {'Bảo hành cũ': 'used_warranty',
     'Giá máy cũ': 'used_price',
     'Tên': 'name',
     'Giá máy mới': "new_price",
     'Bảo hành mới': "new_warranty",
     'Tiết kiệm': "savings",
     'Công nghệ CPU': 'cpu_type',
     'Số nhân': 'num_core',
     'Số luồng': 'num_thread',
     'Tốc độ CPU': "cpu_speed",
     'Tốc độ tối đa': "max_cpu_speed",
     'Bộ nhớ đệm': "cached_cpu",
     'RAM': 'ram',
     'Loại RAM': 'ram_type',
     'Tốc độ Bus RAM': 'ram_speed',
     'Hỗ trợ RAM tối đa': 'max_ram',
     'Ổ cứng': 'storage',
     'Màn hình': 'screen_size',
     'Độ phân giải': 'resolution',
     'Tần số quét': "scan_frequency",
     'Công nghệ màn hình': 'screen_tech',
     'Màn hình cảm ứng': 'has_touchscreen',
     'Card màn hình': 'gpu_type',
     'Công nghệ âm thanh': 'audio_tech',
     'Cổng giao tiếp': 'ports',
     'Kết nối không dây': 'wireless',
     'Khe đọc thẻ nhớ': 'sd_slot',
     'Webcam': 'webcam',
     'Tính năng khác': 'others',
     'Đèn bàn phím': 'has_lightning',
     'Kích thước, trọng lượng': 'size_weight',
     'Chất liệu': 'material',
     'Thông tin Pin': 'battery',
     'Hệ điều hành': 'os',
     'Thời điểm ra mắt': 'released'
     }

ordered_columns = \
    ['brand', 'cpu_type', 'cpu_speed', 'max_cpu_speed', 'num_core', 'num_thread', 'cached_cpu',
     'gpu_type', 'ram_type', 'ram', 'max_ram', 'ram_speed', 'storage',
     'screen_size', 'resolution', 'scan_frequency', 'webcam', 'sd_slot', 'material', 'battery', 'os',
     'audio_tech', 'bluetooth_tech', 'wifi_tech', 'weight', 'thickness', 'width', 'length', 'released',
     'has_lightning', 'has_thundebolt', 'has_touchscreen', 'has_fingerprint', 'has_camera_lock', 'has_180_degree',
     'has_face_id', 'has_antiglare',
     'saved_percent', 'saved_money', 'new_warranty', 'used_warranty', 'new_price', 'used_price']

ordered_columns_step_2 = \
    ['brand', 'cpu_type', 'cpu_speed', 'max_cpu_speed', 'num_core', 'num_thread', 'cached_cpu',
     'gpu_type', 'ram_type', 'ram', 'max_ram', 'ram_speed', 'storage',
     'screen_size', 'resolution', 'scan_frequency', 'webcam', 'num_sd_slot', 'material', 'battery', 'os',
     'audio_tech', 'bluetooth_tech', 'wifi_tech', 'weight', 'thickness', 'width', 'length', 'released', 'ppi',
     'has_lightning', 'has_thundebolt', 'has_touchscreen', 'has_fingerprint', 'has_camera_lock', 'has_180_degree',
     'has_face_id', 'has_antiglare',
     'saved_percent', 'saved_money', 'new_warranty', 'used_warranty', 'new_price', 'used_price']


def rename_columns(df, alternative_name, inplace=False):
    """
    Đổi tên các cột từ tiếng Việt sang tiếng Anh
    """
    return df.rename(columns=alternative_name, inplace=inplace)


def remove_duplicate_laptops(df):
    df = df.groupby("name", as_index=False).first()
    return df


def correct_dtypes(df):
    df['cpu_speed'] = df['cpu_speed'].astype('object')
    df['max_cpu_speed'] = df['max_cpu_speed'].astype('object')
    df['ram'] = df['ram'].astype('object')
    df['ram_speed'] = df['ram_speed'].astype('object')
    df['storage'] = df['storage'].astype('object')
    df['screen_size'] = df['screen_size'].astype('object')
    df['bluetooth_tech'] = df['bluetooth_tech'].astype('object')
    df['released'] = df['released'].astype('object')
    df['has_lightning'] = df['has_lightning'].astype('object')
    df['has_thundebolt'] = df['has_thundebolt'].astype('object')
    df['has_touchscreen'] = df['has_touchscreen'].astype('object')
    df['has_fingerprint'] = df['has_fingerprint'].astype('object')
    df['has_camera_lock'] = df['has_camera_lock'].astype('object')
    df['has_180_degree'] = df['has_180_degree'].astype('object')
    df['has_face_id'] = df['has_face_id'].astype('object')
    df['has_antiglare'] = df['has_antiglare'].astype('object')
    df['new_warranty'] = df['new_warranty'].astype('object')
    df['used_warranty'] = df['used_warranty'].astype('object')
    df['released'] = df['released'].astype('object')
    df['num_sd_slot'] = df['num_sd_slot'].astype('object')

    return df


############# PREPROCESS FEATURES #############

def preprocess_name(string_in):
    """
        Trích ra hãng sản xuất laptop
    """
    brand_name = np.nan
    if string_in is not None:
        name_lowercased = string_in.lower()
        brand_name = string_in.split()[0]
        # Gom "Microsoft Surface... " và "Surface..." => "Microsoft"
        if "surface" in name_lowercased:
            brand_name = "Microsoft"
        # "Vivobook... " => "Asus"
        if "vivobook" in name_lowercased:
            brand_name = "Asus"
        if "macbook" in name_lowercased:
            brand_name = "Apple"
        # Trừ "HP", "MSI", "LG", Chỉ có chữ đầu tiên của các tên hãng đều được in hoa
        if str(brand_name) != "nan" and brand_name not in ["HP", "MSI", "LG"]:
            brand_name = brand_name.capitalize()
    return brand_name


def preprocess_ram_type(string_in):
    """
    Trích ra loại RAM
    """

    types_of_ram = ["LPDDR3", "DDR3L", "DDR3", "LPDDR4X", "DDR4"]
    ram_new = np.nan
    if string_in is None or str(string_in) == "nan":
        return ram_new

    ram_upercased = string_in.upper()
    for _type in types_of_ram:
        if _type in ram_upercased:
            ram_new = _type
            break
    return ram_new


def preprocess_storage(string_in):
    """
        Trích ra dung lượng ổ cứng
    """
    common_drive_capacity = ["128GB", "256GB", "512GB", "1TB"]
    new_drive = np.nan
    if string_in is not None and str(string_in) != "nan":
        drive_tight_uppercased = string_in.replace(" ", "").upper()
        for capacity in common_drive_capacity:
            if capacity in drive_tight_uppercased:
                if capacity != '1TB':
                    new_drive = capacity
                else:
                    new_drive = '1024GB'
                break
    if str(new_drive) == 'nan':
        return new_drive
    else:
        return int(re.search('\d+', new_drive).group())


def preprocess_os(string_in):
    """
        Trích ra tên hệ điều hành
    """
    if string_in is None or str(string_in) == "nan":
        return np.nan
    else:
        string_in = string_in.lower()

        # Nếu có 'mac' -> MacOS
        if 'mac' in string_in:
            return 'MacOS'
        # Nếu có 'win' -> Windows
        elif 'win' in string_in:
            return 'Windows'
        # FreeDOS -> np.nan
        else:
            return np.nan


def preprocess_webcam(string_in):
    """
        Trích ra độ phân giải của webcam
    """

    if string_in is None or str(string_in) == "nan":
        return np.nan
    else:
        string_in = string_in.lower().replace(',', '')
        substrings = string_in.split()

        # Nếu có là 'vga', 'webcam', '0.3mp', '1mp' -> 'VGA'
        if 'vga' in substrings or \
                len(substrings) == 1 or \
                '0.3 mp' in string_in or \
                '1 mp' in string_in:
            return 'VGA'
        # Nếu có 'fhd' -> 'FHD'
        elif 'fhd' in substrings:
            return 'FHD'
        # Nếu có '720p', 'hd', '5mp', 'IR', 'Webcam Stereo 3D' -> 'HD'
        elif 'hd' in substrings or \
                '720p' in substrings or \
                '5 mp' in string_in or \
                'IR'.lower() in string_in or \
                'Webcam Stereo 3D'.lower() in string_in:
            return 'HD'
            # Các trường hợp còn lại -> np.nan
        else:
            return np.nan


def preprocess_resolution(string_in):
    """
        Trích ra độ phân giải màn hình
    """
    if not string_in:
        return np.nan
    else:
        import re

        # Độ phân giải 2K
        if "2K" in string_in:
            return "2160 x 1440"

        # Độ phân giải 4K
        if "4K/UHD" in string_in:
            return "3840 x 2160"

        # Tìm các chuỗi số trong string_in
        numbers = re.findall(r'\d+', string_in)
        return f'{numbers[0]} x {numbers[1]}'


def preprocess_battery(string_in):
    """
        Trích ra dung lượng của pin, tính theo Whr
    """

    if not string_in or str(string_in) == "nan":
        return np.nan

    string_in = string_in.lower()
    if 'wh' not in string_in:
        return np.nan

    string_in = string_in.replace(',', '')
    string_in = string_in.replace('(', '')
    string_in = string_in.replace(')', '')
    string_in = string_in.replace('whrs', 'wh')
    string_in = string_in.replace('whr', 'wh')
    string_in = string_in.replace('whs', 'wh')
    string_in = string_in.replace('-watt-hour lithium-polymer', 'wh')
    string_in = string_in.replace('wh integrated', 'wh')
    string_in = string_in.replace('wh li-ion', 'wh')
    string_in = string_in.replace(" wh", "wh")

    splits = string_in.split()
    for split in splits:
        if "wh" in split:
            return split.replace("wh", "")

    return string_in


def preprocessing_size_weight(string_in):
    """
        Trích ra khối lượng, chiều dày, chiều rộng, chiều dài của laptop
    """

    if not string_in or str(string_in) == "nan":
        return [np.nan, np.nan, np.nan, np.nan]
    string_in = string_in.replace(',', '.')

    # Xử lí trường hợp có 2 giá trị về chiều dày của Laptop apple)
    # 'Dài 304.1 mm - Rộng 212.4 mm - Dày 4.1 mm đến 16.1 mm - Nặng 1.29 kg'
    # => Lấy độ dày dày nhất
    string_in = string_in.replace('Dày 4.1', '')

    # Xử lí trường hợp gõ nhầm giá trị chiều rộng của máy Asus VivoBook S530F i5 8265U/8GB+16GB/1TB/Win10 (BQ400T)
    # 'Rộng 143 mm' = > 'Rộng 243 mm' (Đã kiểm tra lại)
    string_in = string_in.replace('Rộng 143 mm', 'Rộng 243 mm')

    # Chuyển đơn vị g (gram) lên kg (kilogram)
    weight_part = string_in.split('-')[-1]
    weight_part = float(re.findall("\\d*\\.?,?\\d+", weight_part)[0])
    if weight_part > 500:  # Dấu hiệu của đơn vị gram
        g = float(string_in.split()[-2])
        kg = g / 1000
        string_in = string_in + str(kg)

    sizes = re.findall("\\d*\\.?,?\\d+", string_in)
    sizes = [x.replace(",", ".") for x in sizes]
    sizes = list(map(lambda x: float(x), sizes))
    sizes = sorted(sizes)[:4]
    sizes = sizes + [np.nan] * (4 - len(sizes))

    # Chuyển xử lí trường hợp lỗi đánh máy chiều dày laptop từ 20mm lên 200mm (20cm)
    thickness_part = sizes[1]
    if thickness_part > 100:
        sizes[1] = thickness_part / 10

    return sizes


def preprocess_thunderbolt(string_in):
    """
    Trích ra giá trị phân biệt giữa
    laptop có cổng thunderbolt (1) và laptop không có cổng thunderbolt (0)
    """
    if not string_in or str(string_in) == "nan":
        return np.nan
    else:
        string_in = string_in.lower()
        # Kiểm tra trong chuỗi có 'thunderbolt' hay không
        if 'thunderbolt' in string_in:
            return 1  # Có -> trả về 1
        else:
            return 0  # Không -> trả về 0


def preprocess_antiglare(string_in):
    """
    Trích ra giá trị phân biệt giữa
    laptop có chống chói (1) và laptop không có chống chói (0)
    """
    if not string_in or str(string_in) == "nan":
        return np.nan
    else:
        string_in = string_in.lower()
        # Kiểm tra trong chuỗi có 'chống chói' hay 'anti glare' không
        if 'chống chói' in string_in or 'anti glare' in string_in:
            return 1  # Có -> trả về 1
        else:
            return 0  # Không -> trả về 0


def preprocess_cpu_type(string_in):
    """
        Trích ra công nghệ CPU
    """
    if not string_in or str(string_in) == "nan":
        return np.nan
    else:
        string_in = string_in.lower()
        # Kiểm tra Apple
        if 'apple' in string_in or 'm1' in string_in:
            return 'M1'
            # Kiểm tra Intel Core i7
        elif 'i7' in string_in:
            return 'i7'
            # Kiểm tra Intel Core i5
        elif 'i5' in string_in:
            return 'i5'
        # Kiểm tra Intel Core i3
        elif 'i3' in string_in:
            return 'i3'
        elif 'pentium' in string_in:
            return 'pentium'
        # Kiểm tra AMD Ryzen 3
        elif 'ryzen 3' in string_in:
            return 'R3'
        # Kiểm tra AMD Ryzen 5
        elif 'ryzen 5' in string_in:
            return 'R5'
        # Kiểm tra AMD Ryzen 7
        elif 'ryzen 7' in string_in:
            return 'R7'
        # Kiểm tra AMD Ryzen 9
        elif 'ryzen 9' in string_in:
            return 'R9'
        elif 'microsoft' in string_in:
            return 'Microsoft'
        else:
            # print(string_in)
            return np.nan


def preprocess_cpu_speed(string_in):
    if string_in is None or str(string_in) == 'nan':  # None hoặc nan -> np.nan
        return np.nan

    output = re.findall("\\d*\\.?,?\\d+", string_in)  # trả về list chỉ chứa số
    output = [x.replace(",", ".") for x in output]  # thay dấu , = .
    output = list(map(lambda x: float(x), output))  # ép kiểu các số trong list -> float
    output = output[0]  # lấy phần tử đầu tiên của list vì list chỉ có 1 phần tử

    return output


def preprocess_max_cpu_speed(string_in):
    if string_in is None or str(string_in) == "nan":
        return np.nan
    output = re.findall("\\d*\\.?,?\\d+", string_in)
    output = [x.replace(",", ".") for x in output]
    output = list(map(lambda x: float(x), output))
    output = output[0]

    return output


def preprocess_cached_cpu(string_in):
    """
    Trích ra dung lượng bộ nhớ đệm trong CPU
    """
    if string_in is None or str(string_in) == "nan":
        return np.nan

    # Trích số thực
    output = re.findall("\\d*\\.?,?\\d+", string_in)
    output = [x.replace(",", ".") for x in output]
    # print(output)
    output = list(map(lambda x: float(x), output))
    if len(output) == 0:
        return np.nan
    else:
        return output[0]


def preprocess_gpu_type(string_in):
    """
        Trích ra tên GPU (Card đồ họa)
    """
    if not string_in or str(string_in) == "nan":
        return np.nan
    else:
        string_in = string_in.lower()
        # Kiểm tra Apple GPU
        if 'apple' in string_in or 'm1' in string_in:
            return 'Apple'
            # Kiểm tra AMD GPU
        elif 'amd' in string_in:
            return 'AMD'
            # Kiểm tra NVIDIA GPU
        elif ('nvidia' in string_in) or ('geforce' in string_in):
            if 'rtx' in string_in:
                return 'NVIDIA RTX'
            elif 'gtx' in string_in:
                return 'NVIDIA GTX'
            elif 'mx' in string_in:
                return 'NVIDIA MX'
            elif 'quadro' in string_in:
                return "NVIDIA Quadro"
            else:
                print(string_in)
        # Kiểm tra Intel GPU
        elif ('intel' in string_in) or ('onboard' in string_in) or ('tích hợp' in string_in):
            return 'Intel'
        # Kiểm tra Microsoft GPU
        elif 'microsoft' in string_in:
            return 'Microsoft'
        else:
            return np.nan


def preprocess_audio_tech(string_in):
    """
        Trích ra công nghệ âm thanh
    """
    auto_tech_types = ["DTS", "Realtek", "Nahimic", "Dolby", "Harman", "Stereo", "TrueHarmony", "SonicMaster",
                       "Bang & Olufsen", "Smart AMP", "Waves MaxxAudio",
                       "HP Audio Boost"]

    if string_in is not None and str(string_in) != "nan":
        # Format nhiều cách thể hiện => 1 kiểu duy nhất
        string_in = string_in.replace("High Definition", "Realtek High Definition")
        string_in = string_in.replace("High-definition", "Realtek High Definition")

        for _type in auto_tech_types:
            if _type.lower() in string_in.lower():
                return _type
        else:
            string_in = "Other"
    return string_in


def preprocess_ram_speed(string_in):
    """
        Trích ra tốc độ RAM
    """
    if not string_in or str(string_in) == "nan":
        return np.nan

    string_in = string_in.lower()
    bus = re.match(r'\d+ ?mhz', string_in)
    if bus:
        bus = int(bus.group().replace('mhz', ''))
    else:
        bus = np.nan
    return bus


def preprocess_wifi_tech(string_in):
    """
        Trích ra chuẩn Wi-fi
    """
    if string_in is None or str(string_in) == "nan":
        return np.nan
    else:
        string_in = string_in.lower().replace(" ", "")
        for punc in string.punctuation:
            string_in = string_in.replace(punc, "")
        # "ax" là chuẩn của Wi-Fi 6
        if "wifi6" in string_in or "ax" in string_in:
            string_in = "Wi-Fi 6"
        # "ac" là chuẩn của Wi-Fi 5
        elif "wifi5" in string_in or "ac" in string_in:
            string_in = "Wi-Fi 5"
        else:
            string_in = "Wi-Fi 5"
    return string_in


def preprocess_bluetooth_tech(string_in):
    """
        Trích ra chuẩn Wi-fi
    """
    if string_in is None or str(string_in) == "nan":
        return np.nan
    # Trích số thực
    string_in = re.findall("\\d*\\.?,?\\d+", string_in)
    string_in = sorted(string_in)
    if string_in:  # Trích thành công
        # Xử lí trường hợp chỉ trích được ra loại wifi, không có thông tin Bluetooth
        if str(string_in[0]) == "802.11":
            string_in = np.nan
        else:
            string_in = string_in[0]
    return string_in


def preprocess_wireless(string_in):
    """
        Trích ra chuẩn Bluetooth và chuẩn Wi-fi
    """

    bluetooth = preprocess_bluetooth_tech(string_in)
    wifi = preprocess_wifi_tech(string_in)

    return bluetooth, wifi


def preprocess_has_lightning(string_in):
    """
    Trích ra giá trị phân biệt giữa
    laptop có đèn bàn phím (1) và laptop không có đèn bàn phím (0)
    """
    # Kiểm tra giá trị trong ô trước khi bắt đầu xử lí
    # 2 trường hợp nan duy nhât trong bộ dữ liệu là Apple Macbook Air 2015
    # sản phẩm này có hỗ trợ đèn bàn phím => điền 1
    if string_in is None or str(string_in) == "nan":
        return 1

    # Cột has_lightning chỉ có 3 giá trị: 'Có', 'Không có đèn' và nan
    # Có đèn thì return 1, không có đèn return 0
    if len(string_in) == 2:
        return 1
    else:
        return 0


def preprocess_new_warranty(string_in):
    """
    Trích ra thời gian bảo hành mới của laptop, tính theo tháng
    """
    # Kiểm tra giá trị trong ô trước khi bắt đầu xử lí
    if string_in is None or str(string_in) == "nan":
        return np.nan
    # Trả về số năm bảo hành, sau đó chuyển sang tháng
    return int(re.search('\d+', string_in).group()) * 12


def preprocess_material(string_in):
    """
    Trích ra chất liệu laptop
    """
    # Kiểm tra giá trị trong ô trước khi bắt đầu xử lí
    if string_in is None or str(string_in) == "nan":
        return np.nan

    # Chia material thành 3 nhóm: Kim loại, hợp kim và nhựa

    string_in = string_in.lower()
    if ('nhôm' in string_in) or ('magie' in string_in) or ('hợp kim' in string_in):
        return 'Hợp kim'
    elif 'nhựa' in string_in:
        return 'Nhựa'
    else:
        return 'Kim loại'


def preprocess_ram(string_in):
    if string_in is None or str(string_in) == "nan":
        return np.nan
    output = re.findall("\\d*\\.?,?\\d+", string_in)  # trả về list
    output = [x.replace(",", ".") for x in output]
    output = list(map(lambda x: float(x), output))
    output = int(output[0])

    return output


def preprocess_max_ram(string_in):
    if string_in is None or str(string_in) == "nan":
        return np.nan
    output = re.findall("\\d*\\.?,?\\d+", string_in)  # trả về list
    output = [x.replace(",", ".") for x in output]
    output = list(map(lambda x: float(x), output))

    # Nếu không hổ trợ nâng cấp ram -> np.nan
    if not output:
        return np.nan
    else:
        output = int(output[0])

    return output


def preprocess_new_price(string_in):
    if string_in is None or str(string_in) == "nan":
        return np.nan
    # Trích số thực
    output = re.findall("\\d*\\.?\\d+\\.?\d+", string_in)
    output = [x.replace(".", "") for x in output]
    output = list(map(lambda x: float(x), output))

    # Xử lí trường hợp máy đã ngừng kinh doanh, không có giá
    if len(output) == 0:
        return np.nan
    else:
        return output[0]


def preprocess_used_price(string_in):
    if string_in is None or str(string_in) == "nan":
        return np.nan
    # Trích số thực
    output = re.findall("\\d*\\.?\\d+\\.?\d+", string_in)
    output = [x.replace(".", "") for x in output]
    output = list(map(lambda x: float(x), output))

    # Xử lí trường hợp không có giá
    if len(output) == 0:
        return np.nan
    else:
        return output[0]


def preprocess_used_warranty(string_in):
    """
        Trích ra thời gian bảo hành cũ của laptop, tính theo tháng
    """
    if string_in is None or str(string_in) == "nan":
        return np.nan
    # Trích số thực
    output = re.findall("\\d*\\.?,?\\d+", string_in)
    output = [x.replace(",", ".") for x in output]
    # print(output)
    output = list(map(lambda x: float(x), output))

    # Xử lí trường hợp không có thời gian bảo hành còn lại
    if len(output) == 0:
        return np.nan
    else:
        return output[0]


def preprocess_savings(string_in):
    """
    Trích ra phần trăm tiết kiệm và lượng tiền tiết kiệm khi mua máy cữ
    """

    if string_in is None or str(string_in) == "nan":
        return np.nan, np.nan
    # Trích số thực
    output = re.findall("\\d*\\.?\\d+\\.?\d+", string_in)
    output = [x.replace(".", "") for x in output]
    output = list(map(lambda x: float(x), output))
    output = sorted(output)

    # Xử lí trường hợp chỉ có 1 trong 2 thuộc tính
    if len(output) == 1:
        if output[0] < 100:
            output = (output[0], np.nan)
        else:
            output = (np.nan, output[0])
    else:
        output = tuple(output)
    return output


def preprocess_has_touchscreen(string_in):
    """
    Trích ra giá trị phân biệt giữa
    laptop có hỗ trợ cảm ứng (1) và laptop không có hỗ trợ cảm ứng (0)
    """
    return string_in
    # if string_in is None or str(string_in) == "nan":
    #     return 0
    # else:
    #     return 1


def preprocess_sd_slot(string_in):
    """
    Trích ra số lượng các loại khe cảm thẻ nhớ được hỗ trợ
    """
    return string_in
    # if string_in is None or str(string_in) == "nan":
    #     return 0
    # else:
    #     return len(string_in.split('\n'))


def preprocess_screen_size(string_in):
    """
    Trích ra kích thước của màn hình laptop, tính theo inch
    """
    if string_in is None or str(string_in) == "nan":
        return np.nan

    # Trích số thực
    output = re.findall("\\d*\\.?,?\\d+", string_in)
    output = [x.replace(",", ".") for x in output]
    # print(output)
    output = list(map(lambda x: float(x), output))
    if len(output) == 0:
        return np.nan
    else:
        return output[0]


def preprocess_others(string_in):
    """
    Trích ra các tính năng đặc biệt của laptop
    """
    if string_in is None or str(string_in) == "nan":
        return 0, 0, 0, 0

    string_in = string_in.lower()

    fingerprint = 0
    if 'vân tay' in string_in:
        fingerprint = 1

    camera_lock = 0
    if 'khóa camera' in string_in:
        camera_lock = 1

    _180deg = 0
    if '180' in string_in:
        _180deg = 1

    face_id = 0
    if 'khuôn mặt' in string_in:
        face_id = 1

    return fingerprint, camera_lock, _180deg, face_id


def preprocess_scan_frequency(string_in):
    """
    Trích ra tần số quét của màn hình
    """
    if string_in is None or str(string_in) == "nan":
        return np.nan

    # Trích số thực
    output = re.findall("\\d*\\.?,?\\d+", string_in)
    output = [x.replace(",", ".") for x in output]
    # print(output)
    output = list(map(lambda x: float(x), output))
    if len(output) == 0:
        return np.nan
    else:
        return output[0]

# #%%
# def preprocess_cpu_speed(string_in):
#     if string_in is None or str(string_in) == 'nan':  # None hoặc nan -> np.nan
#         return np.nan
#
#     output = string_in
#     # output = re.findall("\\d*\\.?,?\\d+", string_in)  # trả về list chỉ chứa số
#     # output = [x.replace(",", ".") for x in output]  # thay dấu , = .
#     # output = list(map(lambda x: float(x), output))  # ép kiểu các số trong list -> float
#     # output = output[0]  # lấy phần tử đầu tiên của list vì list chỉ có 1 phần tử
#
#     if 1 <= output < 1.5:
#         return "[1, 1.5) GHz"
#     elif 1.5 <= output < 2:
#         return "[1.5, 2) GHz"
#     elif 2 <= output < 2.5:
#         return "[2, 2.5) GHz"
#     elif 2.5 <= output < 3:
#         return "[2.5, 3) GHz"
#     else:
#         return "[3, inf) GHz"
#
#     return output
