import os
import glob
from colorama import Fore, Style, init

# 初始化colorama，以便在Windows上也能使用ANSI颜色代码
init(autoreset=True)  # autoreset意味着在每次打印后自动重置颜色 

target_directory = "../png"

def clear_png_files(directory):
    #png_files = glob.glob(os.path.join(directory, "*.png"))
    #print(png_files)
    # 下面使用迭代iglob()适用于处理大量文件时，可以节省内存开销
    # 对于大型目录，一次性获取所有匹配的文件列表可能会占用大量内存。
    # 在这种情况下，可以使用iglob()函数来进行迭代获取。iglob()返回一个迭代器，逐个返回匹配的文件名。
    png_files = glob.iglob(os.path.join(directory, "*.png"))
    for file in png_files:
        print(file)
    sure = input(Fore.GREEN + "\nAre you sure to clean the aboving files?(y,n): " + Style.RESET_ALL)
    if sure=='y':
        print(Fore.RED + "Cleaning png files......\n" + Style.RESET_ALL)
        # 使用iglob的坏处就是，迭代完成之后返回值里面是空的，所以在这里需要打印的时候
        # 需要重新调用接口iglob获取，所以这里仅仅做展示用
        png_files = glob.iglob(os.path.join(directory, "*.png"))
        for file in png_files:
            try:
                os.remove(file)
                print(Fore.RED + f"Removed: {file}" + Style.RESET_ALL)
            except Exception as e:
                print(f"Error removing {file}: {e}")
    else:
        print(Fore.GREEN + "Bye bye" + Style.RESET_ALL)
    print(Fore.GREEN + f"Finished" + Style.RESET_ALL)


if __name__ == "__main__":
    clear_png_files(target_directory)
    
