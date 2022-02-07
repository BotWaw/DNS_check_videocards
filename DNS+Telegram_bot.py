import time
import requests
import traceback
from selenium import webdriver
import re
import os.path
from selenium.webdriver.support.ui import WebDriverWait


URL_3090='https://www.dns-shop.ru/search/?q=3090+rtx&order=price-asc&category=17a89aab16404e77&f[mv]=udtje'
URL_3080Ti='https://www.dns-shop.ru/search/?q=rtx+3080&order=price-asc&stock=soft&category=17a89aab16404e77&f[mv]=13n3m1'
URL_3080='https://www.dns-shop.ru/search/?q=rtx+3080&order=price-asc&stock=soft&category=17a89aab16404e77&f[mv]=udtf8'
URL_3070Ti='https://www.dns-shop.ru/search/?q=rtx+3070&order=price-asc&stock=soft&category=17a89aab16404e77&f[mv]=145iin'
URL_3070='https://www.dns-shop.ru/search/?q=rtx+3070&order=price-asc&stock=soft&category=17a89aab16404e77&f[mv]=uiykt'
URL_3060Ti='https://www.dns-shop.ru/search/?q=rtx+3060ti&order=price-asc&category=17a89aab16404e77&f[mv]=v7hg2'
URL_3060='https://www.dns-shop.ru/search/?q=rtx+3060&order=price-asc&stock=soft&category=17a89aab16404e77&f[mv]=zyyhm'
URL_3050='https://www.dns-shop.ru/catalog/17a89aab16404e77/videokarty/?order=6&stock=now-today-lte3-gt3-out_of_stock&f[mv]=1cwhi2'
all_URL = [URL_3090, URL_3080Ti,URL_3080, URL_3070Ti, URL_3070, URL_3060Ti, URL_3060,URL_3050]
all_model = ['3090', '3080Ti', '3080', '3070Ti', '3070', '3060Ti', '3060','3050']


def check_and_read_config(): # Проверка существования файла конфигурации (с токеном, chatID и ценами). Если файл существует, то предлагается загрузить настройки из файла
    if os.path.exists('config.txt')==True: # Проверка существования файла
        answer=''

        while answer != "да" and answer != "Да" and answer != "ДА" and answer != 'нет' and answer != 'Нет' and answer != 'НЕТ':
            answer = input("Вы хотите загрузить из файла сохраненные настройки? Напишите 'да' или 'нет'\n")
            if answer == 'да' or answer == 'Да' or answer == 'ДА':
                file = open('config.txt', 'r', encoding='utf-8')
                config = [line.strip() for line in file.readlines()]
                return(config)
            elif answer == 'нет' or answer == 'Нет' or answer == 'НЕТ':
                return(0)
            else:
                print('Неверная фраза')
    elif os.path.exists('config.txt')==False:
        return(0)


def config_bot_Telegram(): # Настройка и проверка работоспособности бота Telegram
    token = input("Введите токен вашего бота Telegram\n")
    chat_id = input('Введите ваш Chat ID\n')
    requests.get("https://api.telegram.org/bot"+token+"/sendMessage?chat_id="+chat_id+"&text=Бот работает")  # Проверка бота

    print('Для проверки работоспособности ваш бот отправил вам сообщение, проверьте пришло ли оно. Подождите 2-3 минуты, если вы не получили сообщение сразу\n')
    answer=''

    while answer!="да" and answer!="Да" and answer!="ДА": # Здесь указано только "да" для того, чтобы цикл каждый раз отправлял сообщение и требовал проверить данные
        answer=input('Вы получили сообщение от бота? Напишите "да" или "нет"\n')

        if answer=='да' or answer=='Да' or answer=='ДА':
            print('Отлично, продолжаем!')
            break
        elif answer=='нет' or answer=='Нет' or answer=='НЕТ':
            print('Проверьте, верно ли вы ввели токен бота и Chat ID')
            print(f'Токен бота:{token}')
            print(f'ChatID:{chat_id}')
            requests.get(f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text=Бот работает")
            print('Если все введено верно, то подождите чуть дольше. Я отправил вам сообщение повторно')
            print('Если спустя 10 минут сообщения не пришли, попробуйте запустить программу позже\n')
        else:
            print('Неверная фраза')
    return(token,chat_id)


def config_price(): # Настройка цен на видеокарты, при достижении которой пользователю будет приходить уведомление. Также настроиваем временной интервал обновления цен
    all_price_videocards=[]
    for cards in all_model:
        flag = True
        while flag==True: # Цикл для проверки корректности введенных данных, если данные корректны, переходим к следующей карте
            price=input('Введите цену для RTX '+cards+', при достижении которой нужно отправить вам уведомление\n')
            if price.isdigit() == False or int(price)<=0: # Проверяем, не ввел ли пользователь какую-нибудь ерунду
                print('Неверное значение цены, введите цену заново')
                flag = True
            else:
                flag=False

        all_price_videocards.append(price)

    flag = True
    while flag == True: # Цикл для проверки корректности введенного временного интервала обновления цен
        time_up=input('С каким интервалом следует проверять цены (в секундах)? Минимальное значение - 60 сек., максимальное - 86400 сек.\n')
        if time_up.isdigit() == False or int(time_up)<60 or int(time_up)>86400:
            print('Неверное значение, введите интервал обновления заново')
            flag = True
        else:
            flag = False

    return(all_price_videocards,time_up)


def save_config(token,chat_id,time_up,all_price_videocards): # Сохранение файла конфигурации
    answer=''
    while answer != "да" and answer != "Да" and answer != "ДА" and answer != 'нет' and answer != 'Нет' and answer != 'НЕТ':
        answer=input("Хотите ли вы сохранить настройки, чтобы не вводить их при следующем запуске программы? Напишите 'да' или 'нет'\n")

        if answer == 'да' or answer == 'Да' or answer == 'ДА':
            file=open('config.txt','w',encoding='utf-8')
            file.write(token+'\n')
            file.write(chat_id+'\n')
            file.write(time_up+'\n')
            for price in all_price_videocards:
                file.write(price+'\n')
            file.close()
            print('Файл настройки сохранен')
            break
        elif answer == 'нет' or answer == 'Нет' or answer == 'НЕТ':
            break
        else:
            print('Неверная фраза')



def check_price(token, chat_id,time_up,all_price_videocards):
    flag = True
    for a in range(len(all_model)):  # Цикл перебирает модели видеокарт (3090, 3080Ti и т.д.)
        URL = all_URL[a]

        if a == 0:  # Если браузер еще вообще не открыт, только запускаем процесс проверки
            driver = webdriver.Chrome()
            driver.get(URL)
            wait = WebDriverWait(driver, 100)
            time.sleep(1)
        else:  # Если хотя бы одна вкладка в браузере уже открыта
            driver.execute_script("window.open('about:blank');")  # Открываем новую вкладку
            tabs = driver.window_handles  # ПОлучаем список вкладок
            driver.switch_to.window(tabs[a])  # Переключаемся на вторую вкладку и т.д.
            driver.get(URL)
            time.sleep(1)

    while flag == True:  # Цикл, чтобы программа просто работала постоянно
        for a in range(len(all_model)):  # Цикл перебирает модели видеокарт (3090, 3080Ti и т.д.)
            error = True # Нужено для проверки, что инфа о видеокарте собралась и не произошло никакой ошибки или зависания
            model = all_model[a]  # Получаем нужную модель из списка
            driver.switch_to.window(tabs[a])  # Делаем активной нужную вкладку
            time.sleep(1)
            driver.refresh()
            time.sleep(3)

            while error==True:
                try:
                    names = driver.find_elements_by_partial_link_text('GeForce RTX')  # Название модели видеокарты
                    prices = driver.find_elements_by_class_name('product-buy__price')  # Цена
                    availability = driver.find_elements_by_class_name('order-avail-wrap')  # Есть ли в наличии

                    for name, price,avail in zip(names, prices,availability):
                        price=''.join(price.text.split())
                        temp_price=(re.findall('\d+', price))
                        out_price=int(temp_price[0])
                        out_name=name.text

                        if model=='3090' and out_price<=int(all_price_videocards[0]):
                            requests.get(f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={out_name} по цене: {out_price}")
                        elif model=='3080Ti' and out_price<=int(all_price_videocards[1]):
                            requests.get(f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={out_name} по цене: {out_price}")
                        elif model=='3080' and out_price<=int(all_price_videocards[2]):
                            requests.get(f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={out_name} по цене: {out_price}")
                        elif model=='3070Ti' and out_price<=int(all_price_videocards[3]):
                            requests.get(f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={out_name} по цене: {out_price}")
                        elif model=='3070' and out_price<=int(all_price_videocards[4]):
                            requests.get(f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={out_name} по цене: {out_price}")
                        elif model=='3060Ti' and out_price<=int(all_price_videocards[5]):
                            requests.get(f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={out_name} по цене: {out_price}")
                        elif model=='3060' and out_price<=int(all_price_videocards[6]):
                            requests.get(f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={out_name} по цене: {out_price}")
                        elif model=='3050' and out_price<=int(all_price_videocards[7]):
                            requests.get(f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={out_name} по цене: {out_price}")
                    error=False

                except Exception as e:
                    print('Ошибка:\n', traceback.format_exc())
                    error=True
                    driver.refresh()
        time.sleep(int(time_up)) # Время ожидания (интервал обновления)


out_config=check_and_read_config()
if out_config==0:
    token,chat_id = config_bot_Telegram()
    all_price_videocards,time_up = config_price()
    save_config(token, chat_id, time_up, all_price_videocards)
    check_price(token, chat_id, time_up, all_price_videocards)
else:
    token=out_config[0]
    chat_id=out_config[1]
    time_up=out_config[2]
    all_price_videocards=out_config[3:]
    check_price(token, chat_id, time_up, all_price_videocards)







