import urllib.request  # библиотеки для открытия url
import urllib.error  # классы исключения библиотеки urllib.request
from datetime import date  # библиотека даты и времени
import re  # библиотека регулярных выражений
import csv  # библиотека записи csv-файлах


url = 'https://www.zakon.kz/news'  # веб-страница парсинга
proxy = {'https': 'https://185.212.128.43:3128'}  # свободный прокси

# через бесконечный цикл запрос проходит через свободный прокси с обработкой исключений
while True:
    try:
        proxy_support = urllib.request.ProxyHandler(proxy)
        opener = urllib.request.build_opener(proxy_support)
        urllib.request.install_opener(opener)
        req = urllib.request.Request(url)
        resp = urllib.request.urlopen(req)
    except urllib.error.HTTPError:
        continue
    except urllib.error.URLError:
        continue
    break


respData = resp.read()  # html-текст веб-страницы
respData = respData.decode("utf-8")  # байтовый тип конвертируем в string
# comment_nums = re.findall(r'<span class=comm_num>(.*?)</span>',str(respData))
paragraphs = re.findall(r'<a(.*?)</a>',str(respData))  # через рег. выражения находим все ссылки
dates = re.findall(r'<span(.*?</span>)',str(respData))  # через рег. выражения находим все времена
# сохраняем в массив времена из dates
pubDates = []
for i in dates:
    if i.__contains__('n3'):
        pubDates.append(str(re.split(">|<",i)[1]))

iter = 0  # итерируемая переменная для вызова элементов pubDates
f = open('zakon.csv','w',newline='',encoding="utf-8")  # открываем новый файл zakon.csv для записи с кодировкой utf-8
writer = csv.writer(f,delimiter=',',  # функция записи данных в файл
           quoting=csv.QUOTE_MINIMAL)
writer.writerow(['Заголовок','Текст','Дата публикации'])  # записываем первую строку - названия столбцов

# проходим через все ссылки
for each in paragraphs:
    if each.__contains__("html") and each.__contains__("target='_blank"):  # открываем лишь ссылки на новостные страницы
        head = re.split("/|>|'",each)[8]  # выбираем заголовок из ссылки
        # link = "https://www.zakon.kz/"+re.split("/|>|'",each)[6]
        text = ""
        # сохраняем весь текст в переменную text, на каждый запрос переходим через прокси
        while True:
            try:
                proxy_support = urllib.request.ProxyHandler(proxy)
                opener = urllib.request.build_opener(proxy_support)
                urllib.request.install_opener(opener)
                curReq = urllib.request.Request("https://www.zakon.kz/"+re.split("/|>|'",each)[6])
                curResp = urllib.request.urlopen(curReq)
            except urllib.error.HTTPError:
                continue
            except urllib.error.URLError:
                continue
            break
        curRespData = curResp.read()
        curRespData = curRespData.decode("utf-8")
        curParagraphs = re.findall('<p>(.*?)</p>',str(curRespData))  # находим текст в текстовых абзацах
        # сохраняем каждый текст
        for y in curParagraphs:
            text += re.sub('<[^>]+>','',str(y))  # удаляем все ссылки и теги из текста
            # print(re.sub('<[^>]+>','',str(y)))
        writer.writerow([head,text,str(date.today())+" "+pubDates[iter]])  # записываем все получившиеся данные в следующую строку
        iter += 1  # присваиваем +1 для перехода на следующую дату
f.close()  # закрываем файл
