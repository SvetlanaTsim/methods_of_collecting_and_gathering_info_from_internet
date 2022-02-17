# 2. Изучить список открытых API (https://www.programmableweb.com/category/all/apis).
# Найти среди них любое, требующее авторизацию (любого типа).
# Выполнить запросы к нему, пройдя авторизацию. Ответ сервера записать в файл.
# Если нет желания заморачиваться с поиском,
# возьмите API вконтакте (https://vk.com/dev/first_guide).
# Сделайте запрос, чтобы получить список всех сообществ на которые вы подписаны.

import requests
import json


url = 'https://api.vk.com/method/groups.get'

with open('user_id.txt') as f:
    user_id = f.read()

v = '5.131'
with open('secret_data.txt') as f:
    access_token = f.read()

params = {'user_id': user_id, 'v': v, 'access_token': access_token}
response = requests.get(url, params=params)
j_data = response.json()
print(j_data)

with open('vk_data.json', 'w') as f:
    json.dump(j_data, f)
