import requests

# https://cloud.yandex.ru/docs/iam/operations/iam-token/create
# Получите OAuth-токен в сервисе Яндекс.OAuth. Для этого перейдите по ссылке:
# https://oauth.yandex.ru/authorize?response_type=token&client_id=
# нажмите "Разрешить" и скопируйте полученный OAuth-токен.
oauth_token = 'OAuth-token'

url = 'https://iam.api.cloud.yandex.net/iam/v1/tokens'
headers = { 'Content-Type': 'application/json' }
data = { 'yandexPassportOauthToken': oauth_token }
response = requests.post(url, headers=headers, json=data)
if response.status_code == 200:
    json = response.json()
    if 'iamToken' in json:
        print(json['iamToken'])
    else:
        print('Invalid response format:\n{}'.format(response.text))
else:
    print('Status [{}]: {}'.format(response.status_code, response.text))
