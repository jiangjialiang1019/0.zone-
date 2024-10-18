from multiprocessing import Process
from elasticsearch import Elasticsearch
from elasticsearch import helpers
import re
import datetime
import hashlib
import warnings
warnings.filterwarnings("ignore")
from lxml import etree
import tld
from urllib.parse import urlparse
from setting_var import val_arry
from es_count_def import es_count

set_var=val_arry()
es = Elasticsearch(
    #['https://192.168.1.2:9200/'], 
    [set_var["es_link"]], 
    http_auth=(set_var["es_name"],set_var["es_pw"]),
    #use_ssl=False,
    #确保我们验证了SSL证书（默认关闭）
    verify_certs=False,
)


####解析一个URL中的内容
def url_analysis(url):
    ctx={
        "toplv_domain":"",
        "domain":"",
        "domain_id":"",
        "url_id":"",
        "code":"200",
    }

    if "mailbox://" in url.lower() or "imap://" in url.lower() or "ftp://" in url.lower() or "http://" in url.lower() or "https://" in url.lower() or "smtp://" in url.lower() or "pop3://" in url.lower() or "oauth://" in url.lower():
        pass
    elif "http://" not in url.lower() and "https://" not in url.lower():
        url="http://"+url
    try:
        ret = tld.get_tld(url, as_object=True)
        toplv_domain=ret.suffix
        root_domain=ret.fld

        uuidtxt=str(url).replace("http://", "", 2)
        uuidtxt=str(url).replace("https://", "", 2)
        uuidtxt=str(url).replace("/", "", 2)
        domain_id=uuidtxt.replace(".", "_", 88)

        url_id = hashlib.md5(url.encode(encoding='UTF-8')).hexdigest()

        ctx["toplv_domain"]=toplv_domain
        ctx["root_domain"]=root_domain
        ctx["domain_id"]=domain_id
        ctx["url_id"]=str(url_id)

        url_p=urlparse(url)

        ctx["scheme"]=url_p.scheme
        ctx["path"]=url_p.path
        ctx["query"]=url_p.query
        ctx["website_url"]=url_p.scheme+"://"+url_p.netloc
        ctx["domain"]=url_p.netloc
        ctx["url"]=url

    except:
        ctx["code"]="502"
    
    return ctx

# print(url_analysis("imap://mail.novalindia.com"))
####获取也一个页面中的url列表
def get_url(res_html,website_url):
    links=[]
    links_arr={}
    try:
        tree = etree.HTML(res_html)
        links_new = tree.xpath('//a')
        
        for i in links_new:
            url=i.attrib.get("href")
            title=""
            if url and url!="#" and url!="?":
                if i.text:
                    title=i.text
                    title = title.replace("\n", "", 999)
                    title = title.replace("\t", "", 999)

                if "http" not in url:
                    url=website_url+"/"+url

                if url not in links_arr:
                    if title=="":
                        links_arr[url]=[]
                    else:
                        links_arr[url]=[title]
                else:
                    if title!="" and title not in links_arr[url]:
                        links_arr[url].append(title)
                

        for v,k in links_arr.items():
            url_li={
                "url":v,
                "title":k
            }
            links.append(url_li)
    except:
        links=[]
    return links


#####检查url是否在信息系统数据库中
def cheack_site(url):
    have_id_res=es.search(index="assetmapping", query={
                        "bool": {
                            "must":[
                                {"match_phrase": {"url": {"query": url,"slop":1}}},
                            ],
                            "should":[],
                            "must_not":[
    
                            ],
                        }},
                _source =['url'],
                size = 1)
    if len(have_id_res["hits"]["hits"])>0:
        return True
    else:
        return False


###争对url下发Kmap任务
def input_iplist(iplist):

    data_li=[]
    iplist_str=""
    for i in iplist:
        if iplist_str=="":
            iplist_str="http://"+i
        else:
            iplist_str=iplist_str+",http://"+i
    yield_li= {
        "_index": "iplist",
        # "_id": i['_id'],
        "country":"china",
        "index_name":"domain_list",
        "iplist":iplist_str,
        "lenlist":len(iplist),
        "num":888,
        "priority":0,
        "port":"80-100,7497,8000-8005,8080-8085,8443,9000-9005,8888,8899,443,1443,2443,3443,4000,4022,4443,5443,6443,7001-7005,7443,9443",
        
    }
    data_li.append(yield_li)
    bulk_res=helpers.bulk(es, data_li)
    print("iplist下发的任务：",bulk_res,iplist_str)


#####找域名针对域名执行任务
def serch_domain():
    have_id_res=es.search(index="domain_mapping_alias", query={
                        "bool": {
                            "must":[
                                {"match_phrase": {"level": {"query": "根域","slop":1}}},
                                # {"exists": {"field": "company"}}
                                {"match_phrase": {"company": {"query": "学校","slop":1}}},

                            ],
                            "should":[],
                            "must_not":[
                                {"match_phrase": {"num": {"query": 1,"slop":1}}},
                            ],
                        }},
                _source =['url'],
                size = 100)
    need_iplist=[]
    data_li=[]
    for i in have_id_res["hits"]["hits"]:
        url=i["_source"]["url"]
        url_res=cheack_site(url)
        if url_res:
            print("有的："+url)
        else:
            print("-----------没的："+url)
            if url not in need_iplist and url!="":
                need_iplist.append(url)
        doc={
            "num":1
        }
        yield_li= {
            "_index": i['_index'],
            "_id": i['_id'],
            '_op_type': 'update',
            "doc": doc
        }
        data_li.append(yield_li)
    if need_iplist!=[]:
        input_iplist(need_iplist)
    
    bulk_res=helpers.bulk(es, data_li)
    es.indices.refresh(index="domain_mapping_alias")
    print(bulk_res)
    return len(need_iplist)





####仿冒域名生成
def counterfeiting(comapny):

    top_domain=[
        "ac.cn","art","asia","band","beer","biz","cc","center","chat","city",
        "cloud","club","cn","co","com","com.cn","company","cool","design","email",
        "fans","fit","fun","fund","games","gold","gov.cn","group","guru","host",
        "icu","info","ink","kim","law","life","live","love","ltd","luxe","market",
        "mobi","net","net.cn","news","online","org.cn","plus","press","pro","pub",
        "red","ren","run","shop","show","site","social","space","store","studio",
        "team","tech","today","top","tvNEW","video","vip","wang","website","wiki",
        "work","world","xin","xyz","yoga","zone","餐厅","佛山","公司","广东","集团",
        "企业","商标","商城","商店","网店","网络","网址","我爱你","游戏","娱乐","在线",
        "招聘","中国","中文网"
    ]

    doamin_list=[]
    old_domain_list=[]



    com_res=es.search( index="domain_mapping_alias",query={
            "bool": {
                "must":[
                    {"wildcard": {"company.keyword": comapny}},
                    {"wildcard": {"level.keyword": "根域"}},

                ],
                "must_not":[
                    ],
                "should":[],
                # "minimum_should_match":1
            }
        },
        # sort={"update.num_icp": {"order": "desc"}},
        size=100,
        source=["url"]
    )
    data_res=com_res["hits"]["hits"]

    for d in data_res:
        domain=d["_source"]["url"]
        old_domain_list.append(domain)

    for d in data_res:
        domain=d["_source"]["url"]
        url_res=url_analysis(domain)
        top_lv_domain=url_res["toplv_domain"]
        root_domain=url_res["root_domain"]
        
        last_num=0-len(top_lv_domain)-1

        domain_str=root_domain[0:last_num]

        
        ###将顶级域名换为其他顶级域名，如.com还为点.cn
        for i in top_domain:
            domain_new=domain_str+"."+i
            if domain_new not in old_domain_list:
                doamin_list.append(domain_new)


        ###替换 0换为o
        if "0" in domain_str:
            domain_new_str=domain_str.replace("0", "o", 88)
            for i in top_domain:
                domain_new=domain_new_str+"."+i
                if domain_new not in old_domain_list:
                    doamin_list.append(domain_new)

        ###替换 o换为0
        if "o" in domain_str:
            domain_new_str=domain_str.replace("o", "0", 88)
            for i in top_domain:
                domain_new=domain_new_str+"."+i
                if domain_new not in old_domain_list:
                    doamin_list.append(domain_new)

        ###替换 q换为p
        if "q" in domain_str:
            domain_new_str=domain_str.replace("q", "p", 88)
            for i in top_domain:
                domain_new=domain_new_str+"."+i
                if domain_new not in old_domain_list:
                    doamin_list.append(domain_new)

        ###替换 p换为q
        if "p" in domain_str:
            domain_new_str=domain_str.replace("p", "q", 88)
            for i in top_domain:
                domain_new=domain_new_str+"."+i
                if domain_new not in old_domain_list:
                    doamin_list.append(domain_new)

    

    print(doamin_list)


# counterfeiting("招商银行股份有限公司")





# domain_list=True
# lei_num=0
# while domain_list:
#     try:
#         lei_num_new=serch_domain()
#         lei_num=lei_num+lei_num_new
#         print("累计下单：",lei_num)
#     except:
#         print("异常")




def index_name_id(ip,port,url,protocol):#基于ip、端口、url生成 id和新的index_name和旧的index_name
    #print("-----------------------------index_name_id----------------------")
    data={
        "urlid":"",
        "nameindex":"",
        "extension":"",
        "domain":"",
        "subdomain":"",
        "toplv_domain":"无",
        "error":""
    }
    
    if ip=="":
        data["error"]="ip_error"
    url_res=url_analysis(url)

    if url_res["code"]=="200":###域名
        urlid=url.replace("https://", "", 1)
        urlid=urlid.replace("http://", "", 1)
        url_str=url
        houzui=urlid[0:1]
        houzui=houzui.lower()
        zmb=["0","1","2","3","4","5","6","7","8","9","a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","x","y","z"]
        if houzui not in zmb:
            houzui="other"

        urlid=url_str.replace("://", "--", 1)
        urlid=urlid.replace("/", "", 999)
        urlid=urlid.replace("\\", "", 999)
        nameindex="mapping_new_d_"+str(houzui)
        
        try:
            ret = tld.get_tld(url, as_object=True)
        except:
            ret=""

        data["urlid"]=urlid
        data["nameindex"]=nameindex

        if ret!="":
            data["extension"]=ret.extension
            data["domain"]=ret.fld
            data["subdomain"]=ret.subdomain+"."+ret.fld
            data["toplv_domain"]=ret.suffix
        else:
            data["extension"]=""
            data["domain"]=""
            data["subdomain"]=""
            data["toplv_domain"]="无"


    name=re.split(r'[.<>]+',ip)
    if len(name)==4 and url_res["code"]=="502":
        if int(name[1])<=85:
            houzui="_0"
        if int(name[1])>85 and int(name[1])<=170:
            houzui="_1"
        if int(name[1])>170 and int(name[1])<=255:
            houzui="_2"

        nameindex="mapping_new_"+name[0]+houzui

        protocol=protocol.upper()
        if protocol=="TCP":
            urlid=ip+':'+port
        else:
            urlid=str(protocol)+ip+':'+port

        data["urlid"]=urlid
        data["nameindex"]=nameindex

    return data

# url_list=[
#     "example.com",  
#     "sub.example.com",  
#     "example-domain.net",  
#     "domain.co.uk",  
#     "invalid-domain-name",  
#     "domain.name.with.too.many.parts",  
#     "domain.with.number123",  
#     "domain.with-dash-",  
#     "domain.with.trailing-dash-",  
#     "domain.with.leading-dash-",  
#     "123.domain.com",  
#     "-invalid-start",  
#     "invalid-end-",  
#     "domain.com/path",  
#     "http://example.com",
#     "12.中国",
#     "http://23.娱乐",
#     "http://233.12.33.12"
# ]
# for i in url_list:

#     print(i)
#     print(index_name_id("192.168.1.1","982",i,"TCP"))
#     print(index_name_id("","",i,""))


# print(url_analysis("www.icbc.co.nl"))