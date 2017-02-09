import requests
import functools
import lxml.html
import datetime
import pickle
import re


def parse_one_news(main_page, links):
    result = []
    for link in links:
        news_page = main_page + link
        print(news_page)
        response = requests.get(news_page)
        print(response.status_code)
        tree = lxml.html.fromstring(response.text)
        category = tree.xpath('/html/body/div[@class="g-application js-root"]'
                              '/section[@class="b-header-inner js-header"]'
                              '/div/div/div/a/text()')
        if category:
            category = category[0]
        title = tree.xpath('/html/body/div[@class="g-application js-root"]'
                           '/div[@class="b-topic-layout js-topic"]/div'
                           '/div[@class="row"]/div[@class="span8"]/div'
                           '/div[@class="b-topic__content"]'
                           '/div[@class="b-topic__header js-topic__header"]/h1/text()')
        if title:
            title = title[0].replace('\xa0', ' ')
        text = tree.xpath('/html/body/div[@class="g-application js-root"]'
                          '/div[@class="b-topic-layout js-topic"]/div'
                          '/div[@class="row"]/div[@class="span8"]/div'
                          '/div[@class="b-topic__content"]'
                          '/div[@class="b-text clearfix js-topic__text"]/p/text()')
        if text:
            text = functools.reduce(lambda x, y: x + y, text)

        result.append([category, title, text])
    return result


def parse_daily_news(main_page, link):
    print(link)
    response = requests.get(link)
    print(response.status_code)
    tree = lxml.html.fromstring(response.text)
    all_links = tree.xpath('/html/body/div[@class="g-application js-root"]'
                           '/section[@class="b-layout js-layout b-layout_archive"]'
                           '/div[@class="g-layout"]/div'
                           '/div/section/div/div[@class="titles"]/h3/a/@href')

    news_pattern = re.compile('/news.*')  # parse only news, without articles and columns
    findall_news = list(map(lambda s: re.findall(news_pattern, s), all_links))
    news_links = [link[0] for link in findall_news if link != []]
    print(news_links)
    return parse_one_news(main_page, news_links)


def parse_news_site(main_page='https://www.lenta.ru/', first_day="2015-12-15", last_day="2016-12-15"):
    print(main_page)
    response = requests.get(main_page)
    print(response.status_code)
    tree = lxml.html.fromstring(response.text)
    categories = tree.xpath('/html/body/div[@class="g-application js-root"]/nav[@class="b-sidebar-menu js-sidebar"]'
                            '/div[@class="b-sidebar-menu_origin b-menu-decorator js-menu"]'
                            '/div[@class="b-sidebar-menu__wrap"]'
                            '/ul[@class="b-sidebar-menu__list"]'
                            '/li[@class="b-sidebar-menu__list-item" and position() > 1]'
                            '/a/text()')
    # first element li<> don't contain category, it's an aggregator
    categories = list(map(lambda s: s.strip(), categories))

    last_day = datetime.datetime.strptime(last_day, "%Y-%m-%d")
    first_day = datetime.datetime.strptime(first_day, "%Y-%m-%d")
    it = first_day  # iterator
    title_dict = {i: [] for i in categories}
    text_dict = {i: [] for i in categories}

    while it < last_day:
        it += datetime.timedelta(days=1)
        [year, month, day] = it.strftime('%Y-%m-%d').split('-')

        news_day_link = 'https://lenta.ru/' + year + '/' + month + '/' + day + '/'
        buffer = parse_daily_news(main_page, news_day_link)
        for i in range(len(buffer)):
            if buffer[i][0] in categories:  # some old pages have category what haven't now
                title_dict[buffer[i][0]].append(buffer[i][1])
                text_dict[buffer[i][0]].append(buffer[i][2])

    with open('title_base.pickle', 'wb') as f:
        pickle.dump(title_dict, f)
    with open('text_base.pickle', 'wb') as f:
        pickle.dump(text_dict, f)
