import requests
import api_key
from urllib.parse import urlencode
api_key=api_key.api['api_key']
from random import random
def tgGetJsonResponse(path):
    url = "https://api.telegram.org/bot{}/{}".format(api_key, path)
    print(url)
    response = requests.get(url, timeout=60)
    status = response.status_code
    json = response.json()
    if status != 200:
      print('error getting response', json)
    return json

def tgGetMessages(offset = None):
  offsetParam = "&offset={}".format(offset) if offset else ""
  return tgGetJsonResponse('getUpdates?allowed_updates=message{}'.format(offsetParam))['result']

def tgSendMessage(params):
  query = urlencode(params)
  path = 'sendMessage?{}'.format(query)
  return tgGetJsonResponse(path)

def tgSendSimpleMessage(chat_id, text):
  return tgSendMessage({ 
        'chat_id': chat_id, 
        'text': text
    })

def tgSendSimpleReply(chat_id, text, message_id):
  return tgSendMessage({ 
        'chat_id': chat_id, 
        'reply_to_message_id': message_id,
        'text': text,
    })

def tgGetChatMembersCount(chat_id):
  return tgGetJsonResponse('getChatMembersCount?chat_id={}'.format(str(chat_id)))['result']
