import requests
import re
import jieba
import jieba.analyse
import os
import collections
import numpy as np
import PIL.Image as Image
# from matplotlib import pyplot as plt
from wordcloud import WordCloud


def words_freq_plot(content):
    # 文本分词
    cut_txt = jieba.cut(content, cut_all=False)
    object_list = []
    remove_words = ["方便面", "拉面", "面条", "康师傅", "汤达人", "吃", "味道", "泡面", "这", "没", "的", '是', u'也', u'都', u'就是', u'在', u'了']

    # 词频统计
    for word in cut_txt:
        if word not in remove_words:
            object_list.append(word)

    word_counts = collections.Counter(object_list)

    wd = WordCloud(
        font_path=font_path,  # 设置字体格式，不然会乱码
        background_color="white",  # 设置背景颜色
        mask=background_image  # 设置背景图
    ).generate_from_frequencies(word_counts)
    return wd


def analysis_plot(content):
    tags = jieba.analyse.extract_tags(content, topK=50, withWeight=False)
    text = " ".join(tags)
    wd = WordCloud(
        font_path=font_path,  # 设置字体格式，不然会乱码
        background_color="white",  # 设置背景颜色
        mask=background_image  # 设置背景图
    ).generate(text)
    return wd


# 泡面的路由和一些参数
rank_base_url = "https://mapi.dianping.com/ranklist/spurank.spulist"
typeid = "100096"
rankType = "1"  # 1好评2踩雷3热销
cateid = "32423"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.94 Safari/537.36",
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive"
}
params = {
    "typeid": typeid,
    "rankType": rankType,
    "cateid": cateid
}


response = requests.get(rank_base_url, params=params, headers=headers)

noodle_list = response.json().get("spuRankItemDOS") or []
rank_list = []
spuid_list = []
rec_reason_list = []
title_list = []
content_list = []

for noodle in noodle_list:
    rank_list.append(noodle.get("spuName"))
    spuid_list.append(noodle.get("spuId"))
    rec_reason_list.append(noodle.get("recReason"))


detail_base_url = "https://mapi.dianping.com/mapi/note/goodsdetailreviewmodule.bin"

for spuid in spuid_list:
    params = {
        "referid": spuid,
        "referType": 1
    }
    response = requests.get(detail_base_url, params=params, headers=headers)
    review_list = response.json().get("reviewList") or []
    title_list.append([review.get("title", "") for review in review_list])
    content_list.append([review.get("content", "") for review in review_list])

for i in range(10):

    # 定义词频背景
    background_image = np.array(Image.open("duck_image.jpg"))
    font_path = os.path.join(os.path.dirname(__file__), "SIMSUN.TTC")
    # 文本预处理
    content = rec_reason_list[i]+"".join(title_list[i])+"".join(content_list[i])
    remove_words = ["方便面", "拉面", "面皮", "面条", "阿宽", "康师傅", "汤达人", "吃", "味道", "泡面",
                    "这", "没", "的", '是', u'也', u'都', u'就是', u'在', u'了',
                    "\[[\w\s]+\]"]
    content = re.sub("|".join(remove_words), '', content)
    content = re.sub(r'[^\w\s]', '', content)
    wd1 = words_freq_plot(content)
    wd2 = analysis_plot(content)

    # 保存词云图
    wd1.to_file('pics/rank_%s_freq.png' % i)
    wd2.to_file('pics/rank_%s_ana.png' % i)
    # 显示词云图
    # plt.imshow(wd, interpolation="bilinear")
    # plt.axis("off")
    # plt.show()
