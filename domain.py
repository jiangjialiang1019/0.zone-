import hashlib
import warnings
warnings.filterwarnings("ignore")
from lxml import etree
import tld
from urllib.parse import urlparse


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

