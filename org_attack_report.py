import xlrd
import re
import os
import openpyxl
import requests
import time
import json
import warnings
warnings.filterwarnings("ignore")


def remove_control_chars(s):  
    control_chars = ''.join(chr(i) for i in range(0, 32))  # 创建包含所有控制字符的字符串  
    trans_table = str.maketrans('', '', control_chars)    # 创建一个翻译表，将控制字符映射为空字符串  
    return s.translate(trans_table)  

###保存查询到的内容到表格中
def input_xlsx(have_data,path_file):
    url=path_file
    try:
        workbook=openpyxl.load_workbook(url)
    except:
        wb = openpyxl.Workbook()
        wb.save(url)
        workbook=openpyxl.load_workbook(url)
    worksheet=workbook.worksheets[0]
    hang=0
    for i in have_data:
        hang=hang+1
        lie=0
        if hang%5000==0:
            print(hang)
        for j in i:
            lie=lie+1
            if isinstance(j, list): 
                j_str=""
                for j_l in j:
                    j_str=j_str+j_l+" | "
                s_clean = remove_control_chars(j_str)
            else:
                s_clean = remove_control_chars(str(j))

            worksheet.cell(hang,lie,s_clean)
    workbook.save(filename=url)
    print("结束保存",path_file)


####从0zone的api里获取数据
def data_api_by_0zone(next=0,query_type="site",query="",size=100):
    my_0zone_key="d8dc137676b66d23d8e794ef8e17dc8c"
    headers = {'Content-Type': 'application/json'}
    url="https://0.zone/api/data/"
    time.sleep(1)
    payload=json.dumps({"query_type":query_type, "query":query, "next":next, "pagesize":size, "zone_key_id":my_0zone_key, "zb_pay": 1 })
    response = requests.request("post", url, headers=headers, data=payload,verify=False).json()

    return response

###通过对应数据类型获取数据
def retrieve_data(keylist,query_type,query_str):
    have_data=[]
    max_num=100
    response=data_api_by_0zone(0,query_type,query_str)
    
    all_hits_total=int(response['total'])

    all_results = response['data']
    


    while len(all_results) > 0:
        last_sort_value = response['next']

        o_index=0
        for i in all_results:
            data_i=i
            csv_li=[]
            for k in keylist:
                key_vlue=""
                key_vlue_str=""
                if "." not in k:
                    if k in data_i:
                        key_vlue=data_i[k]
                else:
                    
                    k_0=re.split(r'[.]+',k)
                    k1=k_0[0]
                    k2=k_0[1]
                    if k1 in data_i:
                        if k2 in data_i[k1]:
                            key_vlue=data_i[k1][k2]
                if isinstance(key_vlue, list):
                    for p in key_vlue:
                        if key_vlue_str=="":
                            key_vlue_str=p
                        else:
                            key_vlue_str=key_vlue_str+" / "+p
                    if key_vlue==[]:
                        key_vlue_str=""
                if isinstance(key_vlue, dict):
                    key_vlue_str=json.dump(key_vlue)
                else:
                    key_vlue_str=key_vlue
                csv_li.append(key_vlue_str)

            if csv_li not in have_data:
                have_data.append(csv_li)

        
        if len(all_results)==max_num and all_hits_total>max_num:
            response=data_api_by_0zone(last_sort_value,query_type,query_str)
            all_results = response['data']
        else:
            all_results=[]



    return have_data


#####获取代码和文档数据
def code_s_mapping(company_name,new_file,app_list,domain_list,ip_list):
    
    query_type="code"
    have_data=[]
    have_data_duibi=[]
    keylist=[
        "name","url","type","source","tags","file_extension","detail_parsing.domain_list","detail_parsing.email_list","detail_parsing.ip_list"
    ]
    keylist_name=[
        "文档","地址","类型","来源","标签","后缀","原文包含的域名","原文包含的邮箱","原文包含的IP","关键词"
    ]
    have_data.append(keylist_name)
    for i in company_name:
        query_str="code_detail=="+str(i)+"||repository.description=="+str(i)
        have_data_li=retrieve_data(keylist,query_type,query_str)
        for h in have_data_li:
            input_i=h
            if h not in have_data_duibi:
                have_data_duibi.append(i)
                input_i.append(i)
                if input_i not in have_data:
                    have_data.append(input_i)


    for i in domain_list:
        query_str="code_detail=="+str(i)+"||repository.description=="+str(i)
        
        have_data_li=retrieve_data(keylist,query_type,query_str)
        for h in have_data_li:
            input_i=h
            if h not in have_data_duibi:
                have_data_duibi.append(i)
                input_i.append(i)
                if input_i not in have_data:
                    have_data.append(input_i)

    for i in app_list:
        query_str="code_detail=="+str(i)+"||repository.description=="+str(i)
        have_data_li=retrieve_data(keylist,query_type,query_str)
        for h in have_data_li:
            input_i=h
            if h not in have_data_duibi:
                have_data_duibi.append(i)
                input_i.append(i)
                if input_i not in have_data:
                    have_data.append(input_i)
                    
    for i in ip_list:
        if i!="":
            query_str="code_detail=="+str(i)+"||repository.description=="+str(i)
            have_data_li=retrieve_data(keylist,query_type,query_str)
            for h in have_data_li:
                input_i=h
                if h not in have_data_duibi:
                    have_data_duibi.append(i)
                    input_i.append(i)
                    if input_i not in have_data:
                        have_data.append(input_i)

    
    input_xlsx(have_data,new_file)
    return len(have_data)-1
    

#####获取信息系统数据
def site_s_mapping(company_name,new_file,app_list,domain_list):
    ctx={
        "ip_list":[],
        "num":0
    }
    query_type="site"
    ip_list=[]
    have_data_duibi=[]
    have_data=[]
    keylist=[
        "url","ip","port","title","company","country","city","os","tags","service","status_code"
    ]
    keylist_name=[
        "URL","IP","端口","网页标题","所属公司","国家","城市","操作系统","标签","服务","网络请求状态码","关键词"
    ]
    have_data.append(keylist_name)


    for i in company_name:
        query_str="company="+str(i)

        have_data_li=retrieve_data(keylist,query_type,query_str)
        for h in have_data_li:
            url_str=h[0]
            ip_str=re.split(r'[:]+',h[1])[0]
            input_i=h

            if url_str not in ip_list:
                ip_list.append(url_str)

            if ip_str not in ip_list:
                ip_list.append(ip_str)

            if h not in have_data_duibi:
                have_data_duibi.append(i)
                input_i.append(i)
                if input_i not in have_data:
                    have_data.append(input_i)

    for i in company_name:
        query_str="html_banner=="+str(i)+"||banner=="+str(i)

        have_data_li=retrieve_data(keylist,query_type,query_str)
        for h in have_data_li:
            input_i=h
            if h not in have_data_duibi:
                have_data_duibi.append(i)
                input_i.append(i)
                if input_i not in have_data:
                    have_data.append(input_i)

    for i in domain_list:
        query_str="(company="")&&url_analyzer=="+str(i)
        
        have_data_li=retrieve_data(keylist,query_type,query_str)
        for h in have_data_li:
            input_i=h
            if h not in have_data_duibi:
                have_data_duibi.append(i)
                input_i.append(i)
                if input_i not in have_data:
                    have_data.append(input_i)

    for i in app_list:
        query_str="(company="")&&(html_banner=="+str(i)+"||banner=="+str(i)+")"
        have_data_li=retrieve_data(keylist,query_type,query_str)
        for h in have_data_li:
            input_i=h
            if h not in have_data_duibi:
                have_data_duibi.append(i)
                input_i.append(i)
                if input_i not in have_data:
                    have_data.append(input_i)

    input_xlsx(have_data,new_file)
    ctx["ip_list"]=ip_list
    ctx["num"]=len(have_data)-1
    return ctx
    


#####获取移动应用数据
def app_s_mapping(company_name,new_file):
    
    query_type="apk"

    have_data=[]
    keylist=[
        "title","type","company","msg.introduction","source","msg.app_url"
    ]
    keylist_name=[
        "应用名称","类型","所属公司","简介","来源","来源地址"
    ]
    have_data.append(keylist_name)
    query_str=""
    for i in company_name:
        if query_str=="":
            query_str="company="+str(i)+"||description=="+(i)
        else:
            query_str=query_str+"||company="+str(i)+"||description=="+(i)

    have_data_li=retrieve_data(keylist,query_type,query_str)
    keyword_list=[]
    for i in have_data_li:
        if i not in have_data:
            have_data.append(i)
        new_key=i[0]
        if new_key not in keyword_list:
            if "title"!=new_key:
                keyword_list.append(new_key)

    input_xlsx(have_data,new_file)
    return keyword_list
    


#####获取域名数据
def domain_s_mapping(company_name,new_file):
    ctx={
        "num":0,
        "domain_list":[]
    }
    query_type="domain"

    have_data=[]
    keylist=[
        "root_domain","domain","company","level","icp","title","msg.ip"
    ]
    keylist_name=[
        "根域名","域名","所属公司","级别","备案","网页标题","解析IP"
    ]
    have_data.append(keylist_name)
    query_str=""
    for i in company_name:
        if query_str=="":
            query_str="company="+str(i)
        else:
            query_str=query_str+"||company="+str(i)
    have_data_li=retrieve_data(keylist,query_type,query_str)
    
    keyword_list=[]

    for i in have_data_li:
        if i not in have_data:
            have_data.append(i)
        new_key=i[0]
        if new_key not in keyword_list:
            if "domain"!=new_key and new_key[-1]!=".":
                keyword_list.append(new_key)

    input_xlsx(have_data,new_file)
    ctx["domain_list"]=keyword_list
    ctx["num"]=len(have_data)-1
    return ctx

##获取邮箱数据
def email_s_mapping(company_name,new_file,domain_list):
    
    query_type="email"

    have_data=[]
    keylist=[
        "email","company","leakage_num","mail_domain"
    ]
    keylist_name=[
        "邮箱","所属公司","泄露次数","邮箱域"
    ]
    have_data.append(keylist_name)
    query_str=""
    for i in company_name:
        if query_str=="":
            query_str="company="+str(i)
        else:
            query_str=query_str+"||company="+str(i)


    for i in domain_list:
        if query_str=="":
            query_str="email_domain=="+str(i)
        else:
            query_str=query_str+"||email_domain=="+str(i)


    have_data_li=retrieve_data(keylist,query_type,query_str)
    
    for i in have_data_li:
        if i not in have_data:
            have_data.append(i)
    input_xlsx(have_data,new_file)
    
    return len(have_data)-1



def reda_xlsx_001(org_file,save_file):
    url = org_file
    workbook = xlrd.open_workbook(url)
    lei_num=0
    sheet_i=0
        
    for sheet1 in workbook.sheets():
        title=sheet1.name
        print(title)
        company = sheet1.col_values(0) # 
        key = sheet1.col_values(1) # 

        
        leni=len(company)

        for i in range(leni):
            if i>0:
                company_name=company[i]
                old_company_name=key[i]
                company_name_list=[]
                company_name_list.append(company_name)
                if old_company_name!="-" and len(old_company_name)>1:
                    company_name_list.append(company_name)

                juedui = 'data/'+save_file+'/'+company_name # 文件夹路径

                if os.path.exists(juedui):
                    juedui=juedui
                else:
                    print('文件夹不存在',juedui)
                    os.makedirs(juedui, exist_ok=True)

                ##记录任务执行情况，可用统计反馈
                workbook=openpyxl.load_workbook(url)
                worksheet=workbook.worksheets[sheet_i]
                
                new_file=juedui+"/移动应用.xlsx"
                app_list=app_s_mapping(company_name_list,new_file)
                worksheet.cell(1,4,str("移动应用"))
                worksheet.cell(i+1,4,str(len(app_list)))
                print(company_name,"移动应用",str(len(app_list)))

                
                new_file=juedui+"/域名.xlsx"
                domain_res=domain_s_mapping(company_name_list,new_file)
                domain_list=domain_res["domain_list"]
                worksheet.cell(1,5,str("域名"))
                worksheet.cell(i+1,5,str(domain_res["num"]))
                print(company_name,"域名",domain_res["num"])


                new_file=juedui+"/邮件.xlsx"
                email_num=email_s_mapping(company_name_list,new_file,domain_list)
                worksheet.cell(1,6,str("邮箱"))
                worksheet.cell(i+1,6,str(email_num))
                print(company_name,"邮箱",email_num)


                new_file=juedui+"/信息系统.xlsx"
                ip_res=site_s_mapping(company_name_list,new_file,app_list,domain_list)
                worksheet.cell(1,7,str("信息系统"))
                worksheet.cell(i+1,7,str(ip_res["num"]))
                print(company_name,"信息系统",ip_res["num"])
                

                new_file=juedui+"/代码和文档.xlsx"
                code_num=code_s_mapping(company_name_list,new_file,app_list,domain_list,ip_res["ip_list"])
                worksheet.cell(1,8,str("代码和文档"))
                worksheet.cell(i+1,8,str(code_num))
                print(company_name,"信息系统",code_num)


                workbook.save(filename=url)

                print("==========================完成一个目标=============================")


        sheet_i=sheet_i+1###进入下一个页签的光标

###组织目标内容
org_file='公司目录.xlsx'
save_file="测试文件夹"
reda_xlsx_001(org_file,save_file)
