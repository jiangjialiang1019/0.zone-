# 0.zone数据采集
0.zone数据采集

本脚本程序是基于0.zone的开放API来编写的针对指定企业的外部攻击面数据获取。

了解0.zone的api，请移步：https://0.zone/apply

主要的能力包括获取：移动应用、域名、邮箱、信息系统、代码文档等信息；

程序执行流程为：

1、获取企业列表数据；

2、按照顺序获取企业外部攻击面数据：

 2.1 获取移动应用数据：基于企业名称获取移动应用数据，并保存为表格；
 
 2.2 获取域名数据：基于企业名称获取域名数据，并保存为表格；
 
 2.3 获取邮箱数据：基于企业名称获取邮箱数据，并保存为表格；
 
 2.4 获取信息系统数据：基于企业名称、移动应用、域名查询结果整理的关键词获取信息系统数据，并保存为表格；
 
 2.5 文档和代码数据：基于企业名称、移动应用、域名查询和信息系统中的url和ip地址作为关键词，去获取文档和代码数据，并保存为表格；
 


使用环境 python 3.0

使用方法：

1、按照格式编辑公司目录：

![image](https://github.com/user-attachments/assets/cc1a90f1-c167-4db3-b210-bb655f5db803)

设置关键差数：my_0zone_key="d8dc137676xxxxxxe794ef8e17dc8c"
my_0zone_key 异步0.zone获取：https://0.zone/plug-in-unit


org_file='公司目录.xlsx' #公司目录名称

save_file="测试文件夹"  #数据存放目录

reda_xlsx_001(org_file,save_file)
