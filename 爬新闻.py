# %%
import requests
from bs4 import BeautifulSoup
import os, re
from openai import OpenAI
import time  
from datetime import datetime  

# %% [markdown]
# # 'https://menet.com.cn

# %%
host ='https://www.menet.com.cn'

# %%
def get_list():
    host ='https://www.menet.com.cn/news'
    response = requests.post(host)
    soup = BeautifulSoup(response.text, 'html.parser')
    news_list = soup.find_all('h3')
    return soup, news_list

# %%
soup, news_list = get_list()

# %%
news_list = [_ for _ in news_list if "登录" not in _.text]

# %%
def get_info(item, host ='https://www.menet.com.cn'):
    link = host + item.a['href']
    title = item.text
    date = item.a['href'].split('/')[3][:8]
    return {
    "title": title,
    'url': link,
    'date':date
}

# %%
result1 = get_info))

# %%
for num, item in enumerate(soup.find_all(lambda tag: tag.has_attr('class') and len(tag)==1 and tag['class'] == ["item_time"])):
    result1[num]['date'] = item.text

# %%


# %% [markdown]
# # https://www.pharnexcloud.com/zixun

# %%
r = requests.get('https://www.pharnexcloud.com/zixun')

# %%
soup = BeautifulSoup(r.text, 'html.parser')

# %%
dates = soup.find_all(lambda tag:tag.has_attr('class') and tag['class']==['date'])

# %%


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
res = list(map(query_tilte_url, result))

# %%
for no, item in enumerate(res):
    
    item['date'] = dates[no]

# %%
result2 = res

# %% [markdown]
# ---

# %% [markdown]
# # https://bydrug.pharmcube.com/

# %%
r = requests.get('https://bydrug.pharmcube.com/')

# %%
soup = BeautifulSoup(r.text, 'html.parser')

# %%
datas = soup.find_all('div', class_= 'mf-flex mf-items-center')

# %%
def get_tilte_and_url(item):
    title = item.text.strip()
    url = item.a['href']
    return {
        'title': title,
        'url': url
    }

# %%
res = list(map(get_tilte_and_url, datas))

# %%
for no, _ in enumerate(res):
    _['date'] = dates[no]

# %%
result3 = res

# %%
import pandas as pd

# %%
df = pd.DataFrame(result1+result2+result3)

# %% [markdown]
# ---

# %%
# 用r.jina转换成ai友好格式，并用通义千问进行总结

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
    with open('output.md', 'w') as f:  
        # 使用 print 函数，将输出重定向到文件  
        print(completion.choices[0].message.content, file=f)  
        
    return completion.choices[0].message.content

# %%
df

# %%
result = result1 + result2 + result3

# %%
def get_and_send(item):
    url = item['url']
    title= item['title']
    summary = summarize(url)
    return summary

# %%
li = result = result1 + result2 + result3

# %%
li[3]

# %%
title, url, date = li[3].values()

# %%
title

# %%
url

# %%
date

# %%
l = li[:10]

# %%
summary = get_and_send(li[3])

# %%
l

# %%
for k, v in l[0].items():
    print(k, v)

# %%
no = [str(_)+'.' for _ in range(1, 11)] 

# %%
li = [f"[{_['title']}]({_['url']})" for _ in l ]

# %%
li = [b[:1] + a+ b[1:] for a, b in zip(no, li)]

# %%
li

# %%
li = [_ + '\n\n' for _ in li ]

# %%
li

# %%
url2 = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=660ed8dd-be77-4f1b-8de8-774d53f1f39c'

# %%


# %%
send_markdown_to_wechat(f"# [{title}]({url})", )

# %%
send_markdown_to_wechat(f"### [{title}]({url})", url )

# %%
link = f"### [{title}]({url})"

# %%
title

# %%
link+= '/n'

# %%
link

# %%


# %%
send_card_to_wechat()

# %%
def send_markdown_to_wechat(msg='test', webhook_url='https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=a0ad9b92-b9a5-43d3-a129-98c954ecb159'):
    
    headers = {  
        'Content-Type': 'application/json',  
    }

    data = dic
   
    response = requests.post(webhook_url, json=data, headers=headers)

# %%
send_markdown_to_wechat(msg = "".join(li))

# %%
send_markdown_to_wechat(msg = "".join(li), webhook_url='https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=660ed8dd-be77-4f1b-8de8-774d53f1f39c')

# %%
s

# %%


# %%


# %%



