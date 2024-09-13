# %%
import os, re, time, requests,json
from bs4 import BeautifulSoup
from openai import OpenAI
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed  
import pandas as pd

# %% [markdown]
# # 爬取

# %% [markdown]
# ## 爬取menet.com

# %%
host = 'https://www.menet.com.cn/news'

# %%
def get_list(host):
    response = requests.post(host)
    soup = BeautifulSoup(response.text, 'html.parser')
    news_list = [_ for _ in soup.find_all('h3') if "登录" not in _.text]
    return soup, news_list

# %%
def get_info(item, host ='https://www.menet.com.cn'):
    link, title, date = host + item.a['href'], item.text,  item.a['href'].split('/')[3][:8]
    return {
    "title": title,
    'url': link,
    'date':date
}

# %%
soup, news_list = get_list(host)

# %%
result_menet = list(map(get_info, news_list))

# %%
for num, item in enumerate(soup.find_all(lambda tag: tag.has_attr('class') and len(tag)==1 and tag['class'] == ["item_time"])):
    result_menet[num]['date'] = item.text

# %%
for _ in result_menet: _['date'] = datetime.strptime(_['date'], '%Y-%m-%d').date()

# %% [markdown]
# ---

# %% [markdown]
# ## 爬取pharnexcloud

# %%
r = requests.get('https://www.pharnexcloud.com/zixun')

# %%
soup = BeautifulSoup(r.text, 'html.parser')

# %%
dates = soup.find_all(lambda tag:tag.has_attr('class') and tag['class']==['date'])
dates = [_.text for _ in dates]
dates = [_ for _  in dates if _ != '']
dates = [datetime.strptime(_.split(' ')[0], '%Y-%m-%d').date() for _ in dates]

# %%
result = soup.find_all('a', class_ = 'img-content')

# %%
def query_tilte_url(item):
    title = item.find_next()['alt']
    url = 'https://www.pharnexcloud.com' + item['href']
    return {
        'title': title,
        'url': url
    }

# %%
result_pharnexcloud = list(map(query_tilte_url, result))

# %%
for no, item in enumerate(result_pharnexcloud): item['date'] = dates[no]

# %% [markdown]
# ---

# %% [markdown]
# ## 爬取bydrug

# %%
r = requests.get('https://bydrug.pharmcube.com/')

# %%
soup = BeautifulSoup(r.text, 'html.parser')

# %%
datas = soup.find_all('div', class_= 'mf-flex mf-items-center')

# %%
datas = datas[1:]

# %%
item = datas[0]

# %%
def get_info(item):
    title = item.text.strip()
    url = item.find('a')['href']
    date = re.findall(r'\d{4}-\d{2}-\d{2}', requests.get(url).text) [0]
    date = datetime.strptime(date, '%Y-%m-%d').date()
    return {
        'title': title,
        'url': url,
        'date': date
    }

# %%
result_bydrug = [get_info(item) for _ in datas]

# %%
results = [*result_menet, *result_pharnexcloud, *result_bydrug]

# %% [markdown]
# ---

# %%
def get_yesterday():
    import datetime  
  
    # 获取当前日期  
    today = datetime.date.today()  
      
    # 获取昨天的日期  
    yesterday = today - datetime.timedelta(days=1)  
      
    # 将昨天的日期格式化为“年-月-日”  
    return yesterday

# %%
len(results)

# %%


# %%
results = [_ for _ in results if _['date'] == get_yesterday()]

# %%
len(results)

# %%
def summarize(url):
    context = requests.get('https://r.jina.ai/'+url).text
    url_pattern = re.compile(r'\bhttps?:\/\/[^\s/$.?#].[^\s]*\b')  
    cleaned_text = url_pattern.sub('', context)
    context = cleaned_text[:6000] if len(cleaned_text)>6000  else cleaned_text
    context = "请尽量简洁总结以下内容，并发表你的观点,文字不得超过150字\n"+context.replace("\n","")[:6000]
    client = OpenAI(
    api_key='sk-69c9bf69fa2b4d2985834d6dc17c0790', # 如何获取API Key：https://help.aliyun.com/zh/model-studio/developer-reference/get-api-key
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
    )
    completion = client.chat.completions.create(
        model="qwen-max", # 更多模型请参见模型列表文档。
        messages=[{"role": "user", "content": context}]
    )
    print(completion.choices[0].message.content)
    
    return completion.choices[0].message.content

# %%
for _ in results:
   try:
        _['context'] = summarize(_['url'])
      
   except Exception as e:
       print(e)
   print('------'*20)

# %%
def get_flag(item):
    
    title = item['title']
    url = item['url']
    date = item['date'].strftime('%Y-%m-%d')
    context = item['context']
    return f"""
  <h4 style="color:black; margin-top:10px">  
    {title}  
  </h4>  
  
  <span> {date}</span>  
  <div  style="margin-bottom: 20px;">  
    <p>  
      {context}  
    </p>  
    <span><a href={url}>👉查看更多内容</a></span>  
  </div>  
  <hr />  
  
  
""".strip()

# %%
htmls = [get_flag(item) for item in results]

# %%
htmls = "".join(htmls)

# %%


# %%


# %%
def get_token():
    corp_id = 'ww9bffa3285527b3c8'
    secret = '_uOqAIKUWnRgFIY23gItQ5fX4OeWRpYu1G86Gvk7EUw'
    url = f'https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={corp_id}&corpsecret={secret}'
    return requests.get(url).json()['access_token']

# %%


# %%


# %%
try:
    html_text = f"""  
<!DOCTYPE html>  
<html lang="en">  
  
<head>  
  <meta charset="UTF-8">  
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">  
  <title>Document</title>  
</head>  
<style>  
  /* 全局样式 */  
  * {{  
    margin: 0;  
    padding: 0;  
  }}  
  
  h4 {{  
    text-align: center;  
     text-shadow: 2px 2px 4px rgba(15, 47, 206, 0.5);
  }}  
  
  em {{  
    font-family: 'Franklin Gothic Medium', 'Arial Narrow', Arial, sans-serif;  
    color: silver;  
  }}  
  
  div > p {{  
    width: 96%;  
    padding: 2%;  
  }}  
  
  a {{  
    color: #1e90ff;  
    text-decoration: none;  
    transition: color 0.3s;  
  }}  
  
  a:hover {{  
    color: #ff6347;  
  }}  
  
  p {{  
    text-indent: 2em;  
    text-align: justify;  
  }}  

  div {{
      margin-bottom: 10px;
  }}
</style>  
  
<body>  
  <h4 style="color:pink;">  
    {title}  
  </h4>  
  
  <span> 🗓️ {date}</span>  
  <div>  
    <p>  
      {context}  
    </p>  
    <span><a href={url}>👉查看更多内容</a></span>  
  </div>  
  <hr />  
  
</body>  
  
</html>  
"""
except:
    pass

# %%
first = f"""  
<!DOCTYPE html>  
<html lang="en">  
  
<head>  
  <meta charset="UTF-8">  
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">  
  <title>Document</title>  
</head>  
<style>  
  /* 全局样式 */  
  * {{  
    margin: 0;  
    padding: 0;  
  }}  
  
  h4 {{  
    text-align: center;  
  }}  
  
  em {{  
    font-family: 'Franklin Gothic Medium', 'Arial Narrow', Arial, sans-serif;  
    color: silver;  
  }}  
  
  div > p {{  
    width: 96%;  
    padding: 2%;  
  }}  
  
  a {{  
    color: #1e90ff;  
    text-decoration: none;  
    transition: color 0.3s;  
  }}  
  
  a:hover {{  
    color: #ff6347;  
  }}  
  
  p {{  
    text-indent: 2em;  
    text-align: justify;  
  }}  
</style>  
  
<body>  
""".strip()

# %%
last = """</body>  
  
</html>  
""".strip()

# %%
html_text = first+htmls+last

# %%


# %%
html_text = html_text.replace('\n', '')

# %%
data = {
   "touser" : "@all",
   "toparty" : "PartyID1|PartyID2",
   "totag" : "TagID1 | TagID2",
   "msgtype" : "text",
   "agentid" : '1000002',
   "text" : {
       "content" : html_text
   },
   "safe":0,
   "enable_id_trans": 0,
   "enable_duplicate_check": 0,
   "duplicate_check_interval": 1800
}

# %%
from datetime import datetime

# %%
title  = datetime.now().strftime("%Y年%m月%d日") + '医疗行业资讯'

# %%
data = {
   "touser" : "@all",
   "toparty" : "PartyID1 | PartyID2",
   "totag": "TagID1 | TagID2",
   "msgtype" : "mpnews",
   "agentid" : 1000002,
   "mpnews" : {
       "articles":[
           {
               "title": title, 
               "thumb_media_id": "2tNI-yo4L7-cQmsgW2drOBeFz51E_R5vHa_mdIdU2pBdFUEPklOjTTM_SevJplbmb4khjjhmEVh_kZDALSuo8aQ",
               "author": "大倩倩",
               
               "content": html_text,
               "digest": " "
            }
       ]
   },
   "safe":0,
   "enable_id_trans": 0,
   "enable_duplicate_check": 0,
   "duplicate_check_interval": 1800
}


# %%


# %%
requests.post("https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token="+get_token(), data= json.dumps(data), ).json()

# %%


# %%


# %%


# %%


# %%



