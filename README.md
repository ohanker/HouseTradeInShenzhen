	1.这个工具的数据来源是【深圳房地产信息平台】https://zjj.sz.gov.cn:8004/
	2.该平台每天会公布前一天的深圳一手房和二手房网签数据（cookie会过期，当发现过期可以在web端登录操作之后复用其cookie即可）
	3.安装python以及相关必要的组件库
 	4.执行python szzfxxw.py 会从上述地址去获取每日新鲜数据
![1728627145724](https://github.com/user-attachments/assets/3a531352-c6ac-43f5-97a4-9ab28d006c7b)
	你可以根据需要决定是否要将获取到的数据写入到本地文件，以及可以对重复的数据dismiss
 
	5.而如果你没有每日跟踪，有数据遗漏，你可以执行 python queryGuidePrice.py 该基本去从一个微博账号获取数据。在图形界面填写你想要更新的最近几条数据即可，当然如果对方微博账号也没有按时发布数据，只能你自己从其他渠道来补全数据了
	下面是根据需要生成的统计数据图表
![weekly_data_residential](https://github.com/user-attachments/assets/890d30eb-10d1-4661-b40e-b058540ed4eb)
![daily_total_house_data](https://github.com/user-attachments/assets/b4ee05d5-9457-4433-adcb-448bb87dc031)
![combined_old_pie_chart](https://github.com/user-attachments/assets/18fdb18c-333d-4a92-9b55-fd6a99dbb947)
![all_trends](https://github.com/user-attachments/assets/e39262d2-6dad-4b1c-a09c-083674174a2f)

	6.使用GUI工具可以同步漏掉的最近几天的数据，以及可以查询官方的每个小区的指导价，以及可以按月统计成交数据
![1729231557636](https://github.com/user-attachments/assets/9ba8d859-a0de-4543-867d-6f4bdd4506dc)



