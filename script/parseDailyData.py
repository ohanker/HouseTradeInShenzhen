import re
import datetime
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from collections import defaultdict
from colorama import Fore, Style, init

# 设置中文字体
font_path = 'C:/Windows/Fonts/simhei.ttf'  # 请根据系统的实际字体路径设置
my_font = FontProperties(fname=font_path)
def_dpi=1000

# 初始化colorama，以便在Windows上也能使用ANSI颜色代码
init(autoreset=True)  # autoreset意味着在每次打印后自动重置颜色 

# 读取文件并解析数据
def read_data_from_file(file_path):
    print(Fore.GREEN + "\n\nAnalyzing raw data......" + Style.RESET_ALL)
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    daily_data = []

    for line in lines:
        text = line.strip()
        if '每日深圳#房产数据#' in text:
            date_match = re.search(r'(\d{1,2})月(\d{1,2})日', text)
            if date_match:
                month, day = date_match.groups()
                today = datetime.date.today()
                date = datetime.date(today.year, int(month), int(day))

                try:
                    new_house = int(re.search(r'一手房成交(\d+)套', text).group(1))
                    new_residential_house = int(re.search(r'一手住宅成交(\d+)套', text).group(1))
                    old_house = int(re.search(r'二手房成交(\d+)套', text).group(1))
                    old_residential_house = int(re.search(r'二手住宅成交(\d+)套', text).group(1))

                    daily_data.append({
                        'date': date,
                        'new_house': new_house,
                        'new_residential_house': new_residential_house,
                        'old_house': old_house,
                        'old_residential_house': old_residential_house
                    })
                except (AttributeError, ValueError):
                    continue

    return daily_data

# 生成每日新房数据的柱状图
def plot_daily_new_house_data(data):
    if not data:
        print(Fore.RED + "No data available for plotting" + Style.RESET_ALL)
        return
    print(Fore.GREEN + "Generating daily new housing transaction data bar chart......"+ Style.RESET_ALL)
    data.sort(key=lambda x: x['date'])  # 按日期排序
    dates = [entry['date'] for entry in data]
    new_house = [entry['new_house'] for entry in data]
    new_residential_house = [entry['new_residential_house'] for entry in data]

    plt.figure(figsize=(12, 6), dpi=def_dpi)
    bar_width = 0.4  # 设置柱状图的宽度
    indices = range(len(dates))
    plt.bar([i - bar_width / 2 for i in indices], new_house, width=bar_width, label='一手房', color='#33ADFF', alpha=0.7)
    plt.bar([i + bar_width / 2 for i in indices], new_residential_house, width=bar_width, label='一手住宅', color='#FF3333', alpha=0.7)
    plt.xlabel('日期', fontproperties=my_font)
    plt.ylabel('过户/网签套数', fontproperties=my_font)
    plt.title('每日-深圳一手房-过户/网签数据', fontproperties=my_font)
    plt.legend(prop=my_font)

    # 显示日期标签，逢5的倍数显示，并加粗这些日期的标线
    date_labels = [date.strftime('%m-%d') if date.day % 5 == 0 else '' for date in dates]
    ax = plt.gca()
    ax.set_xticks(indices)
    ax.set_xticklabels(date_labels, rotation=45, fontproperties=my_font)
    
    # 加粗能被5整除的日期标线
    for i, date in enumerate(dates):
        if date.day % 5 == 0:
            plt.plot([i, i], [0, 0.01], color='black', linewidth=1.5, transform=ax.get_xaxis_transform(), clip_on=False)  # 设置短标线

    # 在柱状图上添加数据标签
    for i, (x, y) in enumerate(zip(indices, new_house)):
        plt.text(x - bar_width / 2, y, str(y), ha='center', va='bottom', fontproperties=my_font, fontsize=6)

    for i, (x, y) in enumerate(zip(indices, new_residential_house)):
        plt.text(x + bar_width / 2, y, str(y), ha='center', va='bottom', fontproperties=my_font, fontsize=6)

    plt.yticks(fontproperties=my_font)
    plt.tight_layout()
    plt.savefig('../png/daily_new_house_data.png')
    plt.close()


# 生成每日二手房数据的柱状图
def plot_daily_old_house_data(data):
    if not data:
        print(Fore.RED + "No data available for plotting" + Style.RESET_ALL)
        return
    print(Fore.GREEN + "Generating daily second-hand housing transaction data bar chart......" + Style.RESET_ALL)

    data.sort(key=lambda x: x['date'])  # 按日期排序
    dates = [entry['date'] for entry in data]
    old_house = [entry['old_house'] for entry in data]
    old_residential_house = [entry['old_residential_house'] for entry in data]

    plt.figure(figsize=(12, 6), dpi=def_dpi)
    bar_width = 0.4  # 设置柱状图的宽度
    indices = range(len(dates))
    #plt.bar([i - bar_width / 2 for i in indices], old_house, width=bar_width, label='二手房成交', alpha=0.7)
    #plt.bar([i + bar_width / 2 for i in indices], old_residential_house, width=bar_width, label='二手住宅成交', alpha=0.7)
    plt.bar([i - bar_width / 2 for i in indices], old_house, width=bar_width, label='二手房', color='#FFBD33', alpha=1)  # 调亮的蓝色
    plt.bar([i + bar_width / 2 for i in indices], old_residential_house, width=bar_width, label='二手住宅', color='#33ADFF', alpha=1)
    plt.xlabel('日期', fontproperties=my_font)
    plt.ylabel('过户/网签套数', fontproperties=my_font)
    plt.title('每日-深圳二手房-过户/网签数据', fontproperties=my_font)
    plt.legend(prop=my_font)

    # 显示日期标签，逢5的倍数显示，并加粗这些日期的标线
    date_labels = [date.strftime('%m-%d') if date.day % 5 == 0 else '' for date in dates]
    ax = plt.gca()
    ax.set_xticks(indices)
    ax.set_xticklabels(date_labels, rotation=45, fontproperties=my_font)
    
    # 加粗能被5整除的日期标线
    for i, date in enumerate(dates):
        if date.day % 5 == 0:
            plt.plot([i, i], [0, 0.01], color='black', linewidth=1.5, transform=ax.get_xaxis_transform(), clip_on=False)  # 设置短标线

    # 在柱状图上添加数据标签
    for i, (x, y) in enumerate(zip(indices, old_house)):
        plt.text(x - bar_width / 2, y, str(y), ha='center', va='bottom', fontproperties=my_font, fontsize=6)

    for i, (x, y) in enumerate(zip(indices, old_residential_house)):
        plt.text(x + bar_width / 2, y, str(y), ha='center', va='bottom', fontproperties=my_font, fontsize=6)

    plt.yticks(fontproperties=my_font)
    plt.tight_layout()
    plt.savefig('../png/daily_old_house_data.png')
    plt.close()

# 生成每日总房产成交数据的柱状图
def plot_daily_total_house_data(data):
    if not data:
        print(Fore.RED + "No data available for plotting" + Style.RESET_ALL)
        return
    print(Fore.GREEN + "Generating daily total transaction data bar chart......" + Style.RESET_ALL)

    data.sort(key=lambda x: x['date'])  # 按日期排序
    dates = [entry['date'] for entry in data]
    total_house = [entry['new_house'] + entry['old_house'] for entry in data]

    plt.figure(figsize=(12, 6), dpi=def_dpi)
    bar_width = 0.4  # 设置柱状图的宽度
    indices = range(len(dates))
    plt.bar(indices, total_house, width=bar_width, label='所有类型住宅', alpha=0.7)
    plt.xlabel('日期', fontproperties=my_font)
    plt.ylabel('过户/网签套数', fontproperties=my_font)
    plt.title('每日-深圳房产-过户/网签总套数(含住宅和公寓)', fontproperties=my_font)
    plt.legend(prop=my_font)

    # 显示日期标签，逢5的倍数显示，并加粗这些日期的标线
    date_labels = [date.strftime('%m-%d') if date.day % 5 == 0 else '' for date in dates]
    ax = plt.gca()
    ax.set_xticks(indices)
    ax.set_xticklabels(date_labels, rotation=45, fontproperties=my_font)
    
    # 加粗能被5整除的日期标线
    for i, date in enumerate(dates):
        if date.day % 5 == 0:
            plt.plot([i, i], [0, 0.01], color='black', linewidth=1.5, transform=ax.get_xaxis_transform(), clip_on=False)  # 调整0.01这个参数可以设置短标线

    # 在柱状图上添加数据标签
    for i, (x, y) in enumerate(zip(indices, total_house)):
        plt.text(x, y, str(y), ha='center', va='bottom', fontproperties=my_font, fontsize=6)

    plt.yticks(fontproperties=my_font)
    plt.tight_layout()
    plt.savefig('../png/daily_total_house_data.png')
    plt.close()
# 生成每周数据的柱状图
def plot_weekly_data(data):
    if not data:
        print(Fore.RED + "No data available for plotting" + Style.RESET_ALL)
        return

    print(Fore.GREEN + "Generating weekly transaction charts [including apartments]......" + Style.RESET_ALL)

    # 将数据按周聚合
    weekly_data = defaultdict(lambda: {'new_house': 0, 'old_house': 0})
    for entry in data:
        year, week, _ = entry['date'].isocalendar()
        week_key = (year, week)
        weekly_data[week_key]['new_house'] += entry['new_house']
        weekly_data[week_key]['old_house'] += entry['old_house']

    # 转换为列表并按年份和周排序
    sorted_weekly_data = sorted(weekly_data.items(), key=lambda x: (x[0][0], x[0][1]))

    weeks = [f"{year}-W{week}" for (year, week), _ in sorted_weekly_data]
    new_house = [entry['new_house'] for _, entry in sorted_weekly_data]
    old_house = [entry['old_house'] for _, entry in sorted_weekly_data]

    plt.figure(figsize=(12, 6), dpi=def_dpi)
    bars_new = plt.bar(weeks, new_house, label='一手房', alpha=0.7)
    bars_old = plt.bar(weeks, old_house, label='二手房', alpha=0.7, bottom=new_house)

    plt.xlabel('周', fontproperties=my_font)
    plt.ylabel('过户/网签套数', fontproperties=my_font)
    plt.title('每周-深圳房产-过户/网签数据(含公寓)', fontproperties=my_font)
    plt.legend(prop=my_font)
    plt.xticks(rotation=45, fontproperties=my_font)
    plt.yticks(fontproperties=my_font)
    plt.tight_layout()

    # 在柱状图的顶部添加总成交数据
    for i, (bar_new, bar_old) in enumerate(zip(bars_new, bars_old)):
        height_new = bar_new.get_height()
        height_old = bar_old.get_height()
        total_height = height_new + height_old

        plt.text(bar_new.get_x() + bar_new.get_width() / 2, total_height, f'{total_height}', ha='center', va='bottom', fontproperties=my_font)
        plt.text(bar_new.get_x() + bar_new.get_width() / 2, height_new / 2, f'{new_house[i]}', ha='center', va='center', fontproperties=my_font, color='white')
        plt.text(bar_old.get_x() + bar_old.get_width() / 2, height_new + height_old / 2, f'{old_house[i]}', ha='center', va='center', fontproperties=my_font, color='white')

    plt.savefig('../png/weekly_data.png')
    plt.close()


# 周数据仅包括住宅
# 生成每周数据的柱状图
def plot_weekly_residential_data(data):
    if not data:
        print(Fore.RED + "No data available for plotting" + Style.RESET_ALL)
        return

    print(Fore.GREEN + "Generating weekly residential transaction charts......" + Style.RESET_ALL)
    # 将数据按周聚合
    weekly_data = defaultdict(lambda: {'new_residential_house': 0, 'old_residential_house': 0})
    for entry in data:
        year, week, _ = entry['date'].isocalendar()
        week_key = (year, week)
        weekly_data[week_key]['new_residential_house'] += entry['new_residential_house']
        weekly_data[week_key]['old_residential_house'] += entry['old_residential_house']

    # 转换为列表并按年份和周排序
    sorted_weekly_data = sorted(weekly_data.items(), key=lambda x: (x[0][0], x[0][1]))

    weeks = [f"{year}-W{week}" for (year, week), _ in sorted_weekly_data]
    new_residential_house = [entry['new_residential_house'] for _, entry in sorted_weekly_data]
    old_residential_house = [entry['old_residential_house'] for _, entry in sorted_weekly_data]

    plt.figure(figsize=(12, 6), dpi=def_dpi)
    bars_new = plt.bar(weeks, new_residential_house, label='一手住宅', alpha=0.7)
    bars_old = plt.bar(weeks, old_residential_house, label='二手住宅', alpha=0.7, bottom=new_residential_house)

    plt.xlabel('周', fontproperties=my_font)
    plt.ylabel('过户/网签套数', fontproperties=my_font)
    plt.title('每周-深圳房产-过户/网签数据(仅住宅)', fontproperties=my_font)
    plt.legend(prop=my_font)
    plt.xticks(rotation=45, fontproperties=my_font)
    plt.yticks(fontproperties=my_font)
    plt.tight_layout()

    # 在柱状图的顶部添加总成交数据
    for i, (bar_new, bar_old) in enumerate(zip(bars_new, bars_old)):
        height_new = bar_new.get_height()
        height_old = bar_old.get_height()
        total_height = height_new + height_old

        plt.text(bar_new.get_x() + bar_new.get_width() / 2, total_height, f'{total_height}', ha='center', va='bottom', fontproperties=my_font)
        plt.text(bar_new.get_x() + bar_new.get_width() / 2, height_new / 2, f'{new_residential_house[i]}', ha='center', va='center', fontproperties=my_font, color='white')
        plt.text(bar_old.get_x() + bar_old.get_width() / 2, height_new + height_old / 2, f'{old_residential_house[i]}', ha='center', va='center', fontproperties=my_font, color='white')

    plt.savefig('../png/weekly_data_residential.png')
    plt.close()


# 生成所有走势图
def plot_all_trends(data):
    if not data:
        print(Fore.RED + "No data available for plotting" + Style.RESET_ALL)
        return
    print(Fore.GREEN + "Generating comparison charts for all property transaction trends......" + Style.RESET_ALL)

    data.sort(key=lambda x: x['date'])  # 按日期排序
    dates = [entry['date'] for entry in data]
    new_house = [entry['new_house'] for entry in data]
    new_residential_house = [entry['new_residential_house'] for entry in data]
    old_house = [entry['old_house'] for entry in data]
    old_residential_house = [entry['old_residential_house'] for entry in data]

    plt.figure(figsize=(12, 6), dpi=def_dpi)
    plt.plot(dates, new_house, marker='o', linestyle='-', color='#FFBD33', label='一手房')
    plt.plot(dates, new_residential_house, marker='o', linestyle='-', color='#6495ED', label='一手住宅')
    plt.plot(dates, old_house, marker='o', linestyle='-', color='#33ADFF', label='二手房')
    plt.plot(dates, old_residential_house, marker='o', linestyle='-', color='#FF3333', label='二手住宅')
    plt.xlabel('日期', fontproperties=my_font)
    plt.ylabel('过户/网签套数', fontproperties=my_font)
    plt.title('每日-深圳房产-过户/网签数据走势', fontproperties=my_font)
    plt.legend(prop=my_font)

    # 显示日期标签，逢5的倍数显示
    date_labels = [date.strftime('%m-%d') if date.day % 5 == 0 else '' for date in dates]
    ax = plt.gca()
    ax.set_xticks(dates)
    ax.set_xticklabels(date_labels, rotation=45, fontproperties=my_font)
    
    # 在曲线图上添加数据标签
    """
    for i, (x, y) in enumerate(zip(dates, new_house)):
        plt.text(x, y, str(y), ha='center', va='bottom', fontproperties=my_font, fontsize=6)

    for i, (x, y) in enumerate(zip(dates, new_residential_house)):
        plt.text(x, y, str(y), ha='center', va='bottom', fontproperties=my_font, fontsize=6)

    for i, (x, y) in enumerate(zip(dates, old_house)):
        plt.text(x, y, str(y), ha='center', va='bottom', fontproperties=my_font, fontsize=6)

    for i, (x, y) in enumerate(zip(dates, old_residential_house)):
        plt.text(x, y, str(y), ha='center', va='bottom', fontproperties=my_font, fontsize=6)
    """
    plt.yticks(fontproperties=my_font)
    plt.tight_layout()
    plt.savefig('../png/all_trends.png')
    plt.close()


def main():
    # 执行解析并生成图表
    data_file_path = '../data/dataHouse.txt'  # 替换为你的txt文件路径
    data = read_data_from_file(data_file_path)
    plot_daily_new_house_data(data)
    plot_daily_old_house_data(data)
    plot_daily_total_house_data(data)
    plot_weekly_data(data)
    plot_weekly_residential_data(data)
    plot_all_trends(data)

if __name__ == "__main__":
    main()

