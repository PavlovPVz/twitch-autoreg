import requests


def get_adr(proxy=""):
    if proxy!="":
        print(proxy)
        res = requests.get("https://post-shift.ru/api.php?action=new&type=json",proxies=proxy,timeout=15)
    else:
        res = requests.get("https://post-shift.ru/api.php?action=new&type=json")
    if("exceeded_the_limit_for_one_person") in res.text:
        raise Exception("Too many requests wait 10 minutes")
    print(res.json())
    try:
        return res.json()['email'], res.json()['key']
    except:
        return res.json()['error']


def get_message_by_text(key, text):
    res = requests.get("https://post-shift.ru/api.php?action=getlist&key=" + key + "&type=json")
    if 'key_not_found' in res.text:
        raise Exception("InvalidKey")
    if "the_list_is_empty" in res.text:
        return None

    num = 1
    for i in res.json():
        message = requests.get("https://post-shift.ru/api.php?action=getmail&key=" + key + "&type=json&id=" + str(num))
        if text in message.json()['message']:
            return message.json()['message']
        num += 1
    return "not_found"


def get_messages_list(key):
    return requests.get("https://post-shift.ru/api.php?action=getlist&key=" + key).text
# def get_message_by_sender(key,message_sender):

# email,key = get_adr()
# print(email+ "  "+key)
