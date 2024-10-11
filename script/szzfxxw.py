import requests
import time
from bs4 import BeautifulSoup
import pandas as pd
from colorama import Fore, Style, init
from matplotlib import pyplot as plt
from matplotlib.font_manager import FontProperties
import matplotlib.font_manager as fm
import parseDailyData
import queryGuidePrice
from tabulate import tabulate

font_path = 'C:/Windows/Fonts/simhei.ttf'  # 请根据系统的实际字体路径设置

g_myFont = FontProperties(fname=font_path)

# 初始化colorama，以便在Windows上也能使用ANSI颜色代码
init(autoreset=True)  # autoreset意味着在每次打印后自动重置颜色 

g_date = ""
g_saveData = "../data/dataHouse.txt"    
g_dpi = 600
g_currentTimestamp = int(time.time() * 1000)
g_firstDetail = None
g_secondDetail = None

def get_house_json_info(url, referer_url):
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Content-Length": "0",
        "Cookie": "_trs_uv=lopia6mg_2292_996d; Hm_lvt_ddaf92bcdd865fd907acdaba0285f9b1=1722214531; szfdc-session-id=4bbcba1e-4c45-401b-ad76-82e61d730867; cookie_3.36_8080=85416329; ASP.NET_SessionId=w4h5fi3oqq3ypdj1iua1yz45; AD_insert_cookie_89188=52028530",
        "Host": "zjj.sz.gov.cn:8004",
        "Origin": "http://zjj.sz.gov.cn:8004",
        "Proxy-Connection": "keep-alive",
        "Referer": referer_url,
        "Sec-Ch-Ua-Mobile":"?0",
        "Sec-Ch-Ua": "\"Not/A)Brand\";v=\"8\", \"Chromium\";v=\"126\", \"Google Chrome\";v=\"126\"",  
        "Sec-Ch-Ua-Platform":"Windows",
        "Sec-Fetch-Dest":"empty",
        "Sec-Fetch-Mode":"cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    }

    response = requests.post(url, headers=headers)
    print(response.text)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"请求失败，状态码: {response.status_code}")
        return None

def get_new_house_json_info():
    url = "https://zjj.sz.gov.cn:8004/api/marketInfoShow/getYsfCjxxGsData"
    referer_url = f"https://zjj.sz.gov.cn:8004/marketInfoShow/Ysfcjxxgs.html?t={g_currentTimestamp}"
    return get_house_json_info(url, referer_url)

def get_old_house_json_info():
    url = "https://zjj.sz.gov.cn:8004/api/marketInfoShow/getEsfCjxxGsData"
    referer_url = f"https://zjj.sz.gov.cn:8004/marketInfoShow/Esfcjxxgs.html?t={g_currentTimestamp}"
    return get_house_json_info(url, referer_url)

#获取二手房当天成交分类详情数据
def get_second_hand_detail_info():
    esf_url = "https://zjj.sz.gov.cn/ris/szfdc/showcjgs/esfcjgs.aspx"
    esf_headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Cookie": "_trs_uv=lopia6mg_2292_996d; cookie_3.36_8080=85416332; ASP.NET_SessionId=1na1r045msidde45tcyxktjw; Path=/; Hm_lvt_ddaf92bcdd865fd907acdaba0285f9b1=1722214531; HMACCOUNT=DB45B4A4784D4E40; arialoadData=false; szfdc-session-id=f757f8f9-f7a4-4ec2-83eb-70348a7b15e8; Hm_lpvt_ddaf92bcdd865fd907acdaba0285f9b1=1722215373; AD_insert_cookie_89188=27956347",
        "Host": "zjj.sz.gov.cn",
        "Proxy-Connection": "keep-alive",
        "Referer": f"https://zjj.sz.gov.cn:8004/marketInfoShow/Esfcjxxgs.html?t={g_currentTimestamp}",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    }
    esf_response = requests.get(esf_url, headers=esf_headers)

    if esf_response.status_code == 200:
        soup = BeautifulSoup(esf_response.content, 'html.parser')
        lblCurTime1 = soup.find('span', {'id': 'lblCurTime1'})
        date_text = lblCurTime1.text.strip() if lblCurTime1 else ""
        table = soup.find('table', {'class': 'table ta-c bor-b-1 table-white'})
        if lblCurTime1 and table:
            table_headers = [th.text.strip() for th in table.find_all('th')]
            table_rows = []
            for row in table.find_all('tr')[1:]:
                columns = row.find_all('td')
                if columns and all(col.text.strip() for col in columns):
                    table_rows.append([col.text.strip() for col in columns])
            
            # 打印表格内容
            df = pd.DataFrame(table_rows, columns=table_headers)
            #print(df)
            
            residential_sales = df[df['用途'] == '住宅']['成交套数'].values[0]
            total_sales = df[df['用途'] == '小计']['成交套数'].values[0]

            return df, date_text, f"深圳二手房成交{total_sales}套，二手住宅成交{residential_sales}套"
        else:
            print("未找到 <span id='lblCurTime1'></span> 或表格内容")
            return None, None
    else:
        print(f"请求失败，状态码: {esf_response.status_code}")
        return None, None


#获取一手新房当天成交分类详情数据
def get_first_hand_detail_info():
    ysf_url = "https://zjj.sz.gov.cn/ris/szfdc/showcjgs/ysfcjgs.aspx"
    ysf_headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Cookie": "_trs_uv=lopia6mg_2292_996d; cookie_3.36_8080=85416332; ASP.NET_SessionId=1na1r045msidde45tcyxktjw; Path=/; Hm_lvt_ddaf92bcdd865fd907acdaba0285f9b1=1722214531; HMACCOUNT=DB45B4A4784D4E40; arialoadData=false; szfdc-session-id=f757f8f9-f7a4-4ec2-83eb-70348a7b15e8; Hm_lpvt_ddaf92bcdd865fd907acdaba0285f9b1=1722215373; AD_insert_cookie_89188=27956347",
        "Host": "zjj.sz.gov.cn",
        "Proxy-Connection": "keep-alive",
        "Referer": f"https://zjj.sz.gov.cn:8004/marketInfoShow/Ysfcjxxgs.html?t={g_currentTimestamp}",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    }
    ysf_response = requests.get(ysf_url, headers=ysf_headers)

    if ysf_response.status_code == 200:
        soup = BeautifulSoup(ysf_response.content, 'html.parser')
        lblCurTime1 = soup.find('span', {'id': 'ctl03_lblCurTime2'})
        date_text = lblCurTime1.text.strip() if lblCurTime1 else ""
        g_date = date_text
        table = soup.find('table', {'class': 'table ta-c bor-b-1 table-white'})
        if lblCurTime1 and table:
            table_headers = [th.text.strip() for th in table.find_all('th')]
            table_rows = []
            for row in table.find_all('tr')[1:]:
                columns = row.find_all('td')
                if columns and all(col.text.strip() for col in columns):
                    table_rows.append([col.text.strip() for col in columns])
            
            # 打印表格内容
            df = pd.DataFrame(table_rows, columns=table_headers)
            #print(df)
            residential_sales = df[df['用途'] == '住宅']['认购网签套数'].values[0]
            total_sales = df[df['用途'] == '小计']['认购网签套数'].values[0]

            return df, f"每日深圳#房产数据#：{date_text}，深圳一手房成交{total_sales}套，一手住宅成交{residential_sales}套"
        else:
            print("未找到 <span id='lblCurTime1'></span> 或表格内容")
            return None, None
    else:
        print(f"请求失败，状态码: {ysf_response.status_code}")
        return None, None

#判断要写入的内容有没有重复，根据每一行的内容，我们以中文字符逗号做分割
#如果分割后的字符串数组的第一个相同（包含日期的部分）则判断为重复。
def check_duplicate_content(new_content):
    with open(g_saveData, "r", encoding="utf-8") as f:
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
            confirm_overwrite = input("是否确定写入？ (y/n): ")
            if confirm_overwrite.lower() == "y":
                return True
            else:
                return False

    return True

# 将格式化数据写入文件
def write_posts_to_file(posts):
    print("\n"+Fore.GREEN + posts + Style.RESET_ALL)
    if check_duplicate_content(posts):
        # 今天获取到的内容写入到dataHouse.txt文件的头部
        with open(g_saveData, "r+", encoding="utf-8") as file:
            content = file.read()
            file.seek(0, 0)
            file.write(f"{posts}\n")
            file.write(content)
        print("Filtered posts have been written to dataHouse.txt")
    else:
        print(Fore.GREEN + "用户已取消写入" + Style.RESET_ALL)

# 生成饼图的函数。单独生成一手房套数，面积，二手房套数，面积饼图的时候需要使用到该函数
def create_pie_chart(data, title, filename, date, is_units):
    if is_units==1 :
        labels = [f"{item['name']}({item['value']})" for item in data]
    else :
        labels = [item['name'] for item in data]
        
    
    values = [item['value'] for item in data]
    total = sum(values)
    percentages = [value / total * 100 for value in values]

 # 增加对相邻0值部分的分离处理
    explode = []
    previous_was_zero = False
    for value in values:
        if value > 0:
            explode.append(0.2)
            previous_was_zero = False
        else:
            if previous_was_zero:
                explode.append(0.3)  # 增大饼块之间的分离距离
            else:
                explode.append(0.1)
            previous_was_zero = True

    plt.figure(figsize=(14, 7), dpi=g_dpi)

    wedges, texts, autotexts = plt.pie(values, labels=labels, autopct='%1.1f%%', startangle=140, textprops={'fontproperties': g_myFont}, explode=explode)
    for text in texts:
        text.set_fontproperties(g_myFont)
    for autotext in autotexts:
        autotext.set_fontproperties(g_myFont)
        
    plt.title(title + f" ({date})", fontproperties=g_myFont, pad=20, fontsize=16)  # Adjust pad and fontsize here
    plt.axis('equal')
    plt.savefig(filename)
    plt.close()


#公共的打印表格接口
#使用 tabulate 打印表格
def print_dataframe(df):
    # 设置列宽和对齐方式
    # colwidths = [15] * len(df.columns)  # 假设每列宽度为15，可以根据实际需要调整
    alignments = ["left"] * len(df.columns)  # 所有列左对齐

    print(tabulate(df, headers='keys', tablefmt='grid', showindex=False, colalign=alignments))

def main():
    print("\n" + Fore.GREEN + "Preparing Raw Data From Shenzhen Real Estate Information Platform......\n" + Style.RESET_ALL)

    new_house_json_info = get_new_house_json_info()
    if new_house_json_info:
        print(Fore.GREEN + "Retrieving yesterday's json data [NEW House] success" + Style.RESET_ALL)
        #print(new_house_json_info)

        print(Fore.YELLOW + "      1.Creating pie charts for yesterday's data [NEW House] ......" + Style.RESET_ALL)

        date = new_house_json_info['data']['xmlDateDay']
        dataMj = new_house_json_info['data']['dataMj']
        dataTs = new_house_json_info['data']['dataTs']
            
        # 生成两个饼图，最后一个参数用于控制成交套数 需要展示 套数数据
        #create_pie_chart(dataMj, "每日/新房过户/网签面积", '../png/new_area_pie_chart.png', date, is_units=0)
        #create_pie_chart(dataTs, "每日/新房过户/网签套数", '../png/new_units_pie_chart.png', date, is_units=1)
        
        # 将两个饼图合并到一个图片上
        fig, axs = plt.subplots(1, 2, figsize=(20, 10), dpi=g_dpi)
        fig.subplots_adjust(top=1,bottom=0)

        explode_area = []
        previous_was_zero = False
        for value in [item['value'] for item in dataMj]:
            if value > 0:
                explode_area.append(0)
                previous_was_zero = False
            else:
                if previous_was_zero:
                    explode_area.append(0.25)
                else:
                    explode_area.append(0)
                previous_was_zero = True

        # 面积饼图
        axs[0].pie([item['value'] for item in dataMj], labels=[item['name'] for item in dataMj], autopct='%1.1f%%', startangle=140, textprops={'fontproperties': g_myFont}, explode=explode_area)
        axs[0].set_title(f"每日/新房过户/网签面积 ({date})", fontproperties=g_myFont, pad=50, fontsize=16)  # Adjust pad and fontsize here 调整标题的字体大小和距离
        
        # 套数饼图 调整两个相邻为0值的位置，使得不挤在一起
        explode_units = []
        previous_was_zero = False
        for value in [item['value'] for item in dataTs]:
            if value > 0:
                explode_units.append(0)
                previous_was_zero = False
            else:
                if previous_was_zero:
                    explode_units.append(0.25)
                else:
                    explode_units.append(0)
                previous_was_zero = True
        
        # 套数饼图  区域上面不加数字 labels=[item['name'] for item in dataTs], 
        labelsWithNum = [f"{item['name']} ({item['value']})" for item in dataTs]
        axs[1].pie([item['value'] for item in dataTs], labels = labelsWithNum, autopct='%1.1f%%', startangle=140, textprops={'fontproperties': g_myFont}, explode=explode_units)
        axs[1].set_title(f"每日/新房过户/网签套数 ({date})", fontproperties=g_myFont, pad=50, fontsize=16)  # Adjust pad and fontsize here 调整标题的字体大小和距离
        
        plt.savefig('../png/combined_new_pie_chart.png')
        plt.close()
        print(Fore.YELLOW + "      2.NEW HOUSE PIE CHARTS SUCCESS\n" + Style.RESET_ALL)

    else:
        print(Fore.RED + "Retrieving yesterday's json data [NEW House] failed" + Style.RESET_ALL)

    old_house_json_info = get_old_house_json_info()
    if old_house_json_info:
        
        print(Fore.GREEN + "Retrieving yesterday's json data [OLD House] success" + Style.RESET_ALL)
        #print(old_house_json_info)

        print(Fore.YELLOW + "      1.Creating pie charts for yesterday's data [OLD House] ......" + Style.RESET_ALL)

        date = old_house_json_info['data']['xmlDateDay']
        dataMj = old_house_json_info['data']['dataMj']
        dataTs = old_house_json_info['data']['dataTs']

        # 生成两个饼图 注释掉，生成费时间
        #create_pie_chart(dataMj, "每日-二手房过户/网签面积", '../png/old_area_pie_chart.png', date, is_units=0)
        #create_pie_chart(dataTs, "每日-二手房过户/网签套数", '../png/old_units_pie_chart.png', date, is_units=1)
        
        # 将两个饼图合并到一个图片上
        fig, axs = plt.subplots(1, 2, figsize=(20, 10), dpi=g_dpi)  
        fig.subplots_adjust(top=1,bottom=0)
        # 面积饼图 调整两个相邻为0值的位置，使得不挤在一起
        explode_mj = []
        previous_was_zero = False
        previous_value = 0
        for value in [item['value'] for item in dataTs]:
            if value > 5:
                explode_mj.append(0)
                previous_was_zero = False
            else:
                if value==previous_value:
                    explode_mj.append(0.1)
                elif previous_was_zero:
                    explode_mj.append(0.2)
                else:
                    explode_mj.append(0)
                previous_was_zero = True
            previous_value = value

        axs[0].pie([item['value'] for item in dataMj], labels=[item['name'] for item in dataMj], autopct='%1.1f%%', startangle=140, textprops={'fontproperties': g_myFont}, explode=explode_mj)
        #axs[0].pie([item['value'] for item in dataMj], labels=[item['name'] for item in dataMj], autopct='%1.1f%%', startangle=140, textprops={'fontproperties': g_myFont}, explode=[0.2 if item['value'] > 0 and item['value'] < 5 else 0 for item in dataMj])
        axs[0].set_title(f"每日/二手房过户/网签面积 ({date})", fontproperties=g_myFont, pad=50, fontsize=16)  # Adjust pad and fontsize here 调整标题的字体大小和距离
        
        
        # 套数饼图 调整两个相邻为0值的位置，使得不挤在一起
        explode_ts = []
        previous_was_zero = False
        for value in [item['value'] for item in dataTs]:
            if value > 5:
                explode_ts.append(0)
                previous_was_zero = False
            else:
                if value==previous_value:
                    explode_ts.append(0.1)
                elif previous_was_zero:
                    explode_ts.append(0.2)
                else:
                    explode_ts.append(0)
                previous_was_zero = True
            previous_value = value
        # 套数饼图  区域上没有数字 labels=[item['name'] for item in dataTs], 
        labelsWithNum = [f"{item['name']} ({item['value']})" for item in dataTs]
        axs[1].pie([item['value'] for item in dataTs], labels=labelsWithNum, autopct='%1.1f%%', startangle=140, textprops={'fontproperties': g_myFont}, explode=explode_ts)
        #axs[1].pie([item['value'] for item in dataTs], labels=labelsWithNum, autopct='%1.1f%%', startangle=140, textprops={'fontproperties': g_myFont}, explode=[0.2 if item['value'] >= 0 and item['value'] <= 5 else 0 for item in dataTs])
        axs[1].set_title(f"每日/二手房过户/网签套数 ({date})", fontproperties=g_myFont, pad=50, fontsize=16)  # Adjust pad and fontsize here 调整标题的字体大小和距离
        
        plt.savefig('../png/combined_old_pie_chart.png')
        plt.close()
        print(Fore.YELLOW + "      2.OLD HOUSE PIE CHARTS SUCCESS\n" + Style.RESET_ALL)

    else:
        print(Fore.RED + "Retrieving yesterday's json data [OLD House] failed" + Style.RESET_ALL)

    # 需要显式地声明这些变量为全局变量，才能在main里面使用全局变量
    global g_firstDetail, g_secondDetail
    # 获取一手新房成交套数表格数据
    try:
        jdata, g_firstDetail = get_first_hand_detail_info()  
        if not jdata.empty and g_firstDetail:  
            print(Fore.GREEN + "Extracted yesterday's transaction records successfully [new house]" + Style.RESET_ALL)  
            print_dataframe(jdata)
        else:  
            print(Fore.RED + "Unable to obtain yesterday's transaction information [new house]. (maybe data null or other reason)" + Style.RESET_ALL)  
    except Exception as e:  
        print(Fore.RED + f"Getting 1st Excel data error：{e}" + Style.RESET_ALL)
    
    #获取二手房成交套数表格数据
    try:
        jdata, text, g_secondDetail = get_second_hand_detail_info()  
        if not jdata.empty and text and g_secondDetail:  
            print(Fore.GREEN + "Extracted yesterday's transaction records successfully [old house]" + Style.RESET_ALL)  
            print_dataframe(jdata)
        else:  
            print(Fore.RED + "Unable to obtain yesterday's transaction information [old house]. (maybe data null or other reason)" + Style.RESET_ALL)  
    except Exception as e:  
        print(Fore.RED + f"Getting 2nd Excel data error：{e}" + Style.RESET_ALL)

#未来需要加入的数据分析
#香港中原的指数https://hk.centanet.com/CCI/index
if __name__ == "__main__":
    main()
    writeable = (input("Do you want to write today's data into local file?(y,n)："))
    if writeable == 'y':
        print(Fore.RED + "Writting data to local file......" + Style.RESET_ALL)
        write_posts_to_file(g_date + g_firstDetail+ "。" +g_secondDetail)

    generate_more_charts = (input("Do you want to generate more bar charts?(y,n)："))
    if generate_more_charts== 'y':
        parseDailyData.main()

    query_guide_price = (input("Do you want to query guide price?(y,n)："))
    if query_guide_price== 'y':
        queryGuidePrice.create_main_window()
    
    print(Fore.GREEN + "-_- -_- -_- -_- -_- -_- -_-" + Style.RESET_ALL)
    print(Fore.GREEN + "++ Bye See you next time ++" + Style.RESET_ALL)
    print(Fore.GREEN + "-_- -_- -_- -_- -_- -_- -_-" + Style.RESET_ALL)