import requests

url = "http://localhost/dashboard.php"

payload  = {'email': 'John@gmail.com','pass': '1234'}

r = requests.post(url, data = payload)