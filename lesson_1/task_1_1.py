# 1. Посмотреть документацию к API GitHub, разобраться как вывести список репозиториев для конкретного пользователя,
# сохранить JSON-вывод в файле *.json.

import requests
import json

url = 'https://api.github.com'
user = 'defunkt'

response = requests.get(f'{url}/users/{user}/repos')

j_data = response.json()

for i in j_data:
    print(i['name'])

with open('repo_data.json', 'w') as f:
    json.dump(j_data, f)
