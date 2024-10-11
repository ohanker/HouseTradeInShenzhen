import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
from tkinter import messagebox
from colorama import Fore, Style, init
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd

init(autoreset=True)  # autoreset意味着在每次打印后自动重置颜色

# 读取Excel文件内容
file_path = '../data/referencePrice.xlsx'
save_data = "../data/dataHouse.txt"
df = pd.read_excel(file_path, header=1)  # 从excel文件第三行开始读取实际的数据

# 确保列名没有额外的空格或其他字符
df.columns = df.columns.str.strip()

# 去重，获取所有的行政区、街道和小区
districts = df['行政区'].unique().tolist()
streets = {district: df[df['行政区'] == district]['街道'].unique().tolist() for district in districts}
communities = {street: df[df['街道'] == street]['小区名称'].unique().tolist() for street_list in streets.values() for street in street_list}

# 定义一个函数来读取文件并计算数据
def calculate_house_sales(month, type_of_house):
    total_sales = 0
    with open(save_data, 'r', encoding='utf-8') as file:
        for line in file:
            # 检查该行是否包含指定月份的日期
            if f'{month}月' in line:
                # 提取一手或二手住宅的成交套数
                if type_of_house == '一手住宅':
                    sales_str = line.split('一手住宅成交')[1].split('套')[0].strip()
                elif type_of_house == '二手住宅':
                    sales_str = line.split('二手住宅成交')[1].split('套')[0].strip()  # 注意这里可能需要根据实际文本格式调整
                else:
                    print("无效的住宅类型，请输入'一手'或'二手'。")
                    return None
                # 将字符串转换为整数并累加
                total_sales += int(sales_str)
    return total_sales

# 处理按钮点击事件
def on_calculate(month_var, type_var, result_label):
    month = month_var.get()
    house_type = type_var.get()
    if month and house_type:
        total_sales = calculate_house_sales(month, house_type)
        typeH = "一手" if house_type == '一手住宅' else "二手"
        if total_sales is not None:
            result_label.config(text=f"{month}月份的{typeH}住宅总成交套数为：{total_sales}套", bootstyle="info")
    else:
        result_label.config(text="请选择月份和住宅类型", bootstyle="danger")

def fetch_weibo_data(user_id, page):
    url = f"https://m.weibo.cn/api/container/getIndex?containerid=107603{user_id}&page={page}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch data: {response.status_code}")
        return None

def filter_weibo_posts(data, keyword):
    if not data or "cards" not in data:
        print("No cards found in data.")
        return []
    
    weibo_posts = data["cards"]
    filtered_posts = []

    for post in weibo_posts:
        if "mblog" in post and keyword in post["mblog"]["text"]:
            # 使用BeautifulSoup去除HTML标签
            soup = BeautifulSoup(post["mblog"]["text"], "html.parser")
            cleaned_text = soup.get_text()
            filtered_posts.append(cleaned_text)
    
    return filtered_posts

#原始没有判断内容重复的
def write_posts_to_filexx(posts):
    # 获取当前日期并格式化
    #current_date = datetime.now().strftime("%Y-%m-%d")

    # 将微博内容写入到dataHouse.txt文件的头部
    with open(save_data, "r+", encoding="utf-8") as file:
        content = file.read()
        file.seek(0, 0)
        # 将当前日期的微博放在第一行
        #file.write(f"{posts[0]}\n")
        # 将其他微博内容逐行写入
        for post in posts[0:]:
            file.write(f"{post}\n")
        file.write(content)
    print("Filtered posts have been written to dataHouse.txt")

# 将格式化数据写入文件
def write_posts_to_file(posts):
    
    # 获取当前日期并格式化
    #current_date = datetime.now().strftime("%Y-%m-%d")

    # 将微博内容写入到dataHouse.txt文件的头部
    with open(save_data, "r+", encoding="utf-8") as file:
        content = file.read()
        file.seek(0, 0)
        # 将当前日期的微博放在第一行
        #file.write(f"{posts[0]}\n")
        # 将其他微博内容逐行写入
        for post in posts[0:]:
            if check_duplicate_content(post):
                file.write(f"{post}\n")
                print("Filtered posts have been written to dataHouse.txt")
            else:
                print(Fore.GREEN + "用户已取消写入" + Style.RESET_ALL)    
        file.write(content)
#判断要写入的内容有没有重复，根据每一行的内容，我们以中文字符逗号做分割
#如果分割后的字符串数组的第一个相同（包含日期的部分）则判断为重复。
#增加对于第[1]部分重复的判断避免第[0]日期格式虽然不一样，但是其实内容是一样的
def check_duplicate_content(new_content):
    with open(save_data, "r", encoding="utf-8") as f:
        existing_lines = f.readlines()

    new_content_split = new_content.split("，")
    if len(new_content_split) < 2:
        print("Error: Invalid format for new content.")
        return False

    for existing_line in existing_lines:
        existing_line_split = existing_line.strip().split("，")
        if len(existing_line_split) < 2:
            continue

        if new_content_split[0] == existing_line_split[0] or new_content_split[1] == existing_line_split[1]:
            print("Duplicate content detected:")
            print(f"[exsist data] {new_content}")
            confirm_overwrite = input("是否确定写入？ (yes/no): ")
            if confirm_overwrite.lower() == "yes":
                return True
            else:
                return False

    return True

def fetch_and_update_data(posts_entry, result_label):
    #global posts_entry, result_label  # 如果函数没有参数，而需要使用外部的数据，则声明外部参数为全局变量，否则不能引用。
    user_id = "6177021066"  # 微博用户ID
    keyword = "#房产数据#"
    page = 1
    filtered_posts_count = 0
    try:
        max_posts = int(posts_entry.get())
    except ValueError:
        result_label.config(text="请输入有效的数字", bootstyle="danger")
        return

    filtered_posts = []

    while filtered_posts_count < max_posts:
        data = fetch_weibo_data(user_id, page)
        if not data or data.get("ok") != 1:
            print("No more data or response not OK.")
            break

        posts = filter_weibo_posts(data.get("data", {}), keyword)
        if not posts:
            page += 1
            continue

        for post in posts:
            addOneCharacter = post.replace("二手住宅成", "二手住宅成交")
            print(addOneCharacter)
            filtered_posts.append(addOneCharacter)
            filtered_posts_count += 1
            if filtered_posts_count >= max_posts:
                break
        
        page += 1

    if filtered_posts_count == 0:
        print("No posts found with the specified keyword.")
    else:
        write_posts_to_file(filtered_posts)
        result_label.config(text="数据已更新", bootstyle="success")

def update_streets(event):
    #global street_combobox, community_combobox, street_var, community_var  # 声明为全局变量
    selected_district = district_var.get()
    street_combobox['values'] = streets.get(selected_district, [])
    street_var.set('')
    community_combobox['values'] = []
    community_var.set('')

def update_communities(event):
    global community_combobox, street_var  # 声明为全局变量
    selected_street = street_var.get()
    community_combobox['values'] = communities.get(selected_street, [])
    community_var.set('')

def create_main_window():
    print(Fore.GREEN + "正在使用 Tkinter GUI 创建交互界面......" + Style.RESET_ALL)
    global district_var, street_var, community_var, street_combobox, community_combobox  # 声明为全局变量
    # 创建主窗口
    # 主题 ['vista', 'classic', 'cyborg', 'journal', 'darkly', 'flatly', 'clam', 'alt', 'solar', 'minty', 'litera', 'united', 'xpnative', 'pulse', 'cosmo', 'lumen', 'yeti', 'superhero', 'winnative', 'sandstone', 'default']
    root = ttk.Window(themename="darkly")  # 使用一个现代的主题
    root.title("深圳房产数据统计")

    # 创建更新数据输入框和按钮，绑定相关的函数，传入参数。如果计算函数不设计为参数，则需要声明global参数，否则不能引用。
    update_label = ttk.Label(root, text="更新数据条数：")
    update_label.grid(row=0, column=0, padx=10, pady=5, sticky=W)
    posts_entry = ttk.Entry(root, bootstyle="primary", width=22)  # 设置宽度与下拉框一致
    posts_entry.grid(row=0, column=1, padx=10, pady=5, sticky=W)
    update_button = ttk.Button(root, text="更新数据", command=lambda: fetch_and_update_data(posts_entry, result_label), bootstyle="success")
    update_button.grid(row=0, column=2, padx=10, pady=5, sticky=W)

    # 创建月份选择框
    month_label = ttk.Label(root, text="选择月份：")
    month_label.grid(row=1, column=0, padx=10, pady=5, sticky=W)
    month_var = ttk.StringVar()
    month_combobox = ttk.Combobox(root, textvariable=month_var, values=[str(i) for i in range(1, 13)], bootstyle="info")
    month_combobox.grid(row=1, column=1, padx=10, pady=5, sticky=W)

    # 创建住宅类型选择框
    type_label = ttk.Label(root, text="选择住宅类型：")
    type_label.grid(row=2, column=0, padx=10, pady=5, sticky=W)
    type_var = ttk.StringVar()
    type_combobox = ttk.Combobox(root, textvariable=type_var, values=["一手住宅", "二手住宅"], bootstyle="info")
    type_combobox.grid(row=2, column=1, padx=10, pady=5, sticky=W)

    # 创建计算按钮，绑定计算函数，传入参数。如果计算函数不设计为参数，则需要声明global参数，否则不能引用。
    calculate_button = ttk.Button(root, text="统计成交", command=lambda: on_calculate(month_var, type_var, result_label), bootstyle="primary")
    calculate_button.grid(row=2, column=2, padx=10, pady=5, sticky=W)

    # 创建结果标签
    result_label = ttk.Label(root, text="", bootstyle="info")
    result_label.grid(row=3, column=0, columnspan=3, padx=10, pady=10, sticky=W)

    # 创建查询区域
    query_frame = ttk.Frame(root)
    query_frame.grid(row=4, column=0, columnspan=3, padx=10, pady=10, sticky=W)

    # 区选择框
    district_label = ttk.Label(query_frame, text="选择行政区：")
    district_label.grid(row=0, column=0, padx=5, pady=5, sticky=W)

    district_var = ttk.StringVar()
    district_combobox = ttk.Combobox(query_frame, textvariable=district_var, bootstyle="info", width=20)  # 设置宽度
    district_combobox['values'] = districts
    district_combobox.grid(row=0, column=1, padx=35, pady=5, sticky=W)
    district_combobox.bind("<<ComboboxSelected>>", update_streets)

    # 街道选择框
    street_label = ttk.Label(query_frame, text="选择街道：")
    street_label.grid(row=1, column=0, padx=5, pady=5, sticky=W)

    street_var = ttk.StringVar()
    street_combobox = ttk.Combobox(query_frame, textvariable=street_var, bootstyle="info", width=20)  # 设置宽度
    street_combobox.grid(row=1, column=1, padx=35, pady=5, sticky=W)
    street_combobox.bind("<<ComboboxSelected>>", update_communities)

    # 小区选择框
    community_label = ttk.Label(query_frame, text="选择小区：")
    community_label.grid(row=2, column=0, padx=5, pady=5, sticky=W)

    community_var = ttk.StringVar()
    community_combobox = ttk.Combobox(query_frame, textvariable=community_var, bootstyle="info", width=20)  # 设置宽度
    community_combobox.grid(row=2, column=1, padx=35, pady=5, sticky=W)

    # 查询按钮和结果显示
    def query_price():
        district = district_var.get()
        street = street_var.get()
        community = community_var.get()

        result = df[(df['行政区'] == district) & (df['街道'] == street) & (df['小区名称'] == community)]
        if not result.empty:
            price = result.iloc[0]['成交参考价格']
            Messagebox.show_info(f"{district} {street} {community} 的 政府指导价格 为 {price} 元/平米", title="指导价格")
        else:
            Messagebox.show_info(f"未找到 {district} {street} {community} 的政府指导价格信息", title="指导价格")

    # 创建查指导价按钮
    check_price_button = ttk.Button(query_frame, text="查指导价", command=query_price, bootstyle="info")
    check_price_button.grid(row=2, column=2, padx=10, pady=5, sticky=W)  # 调整位置

    root.mainloop()

if __name__ == "__main__":
    create_main_window()
