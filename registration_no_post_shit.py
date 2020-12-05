import requests
import random
import time
import json
import datetime
import os
from multiprocessing import Queue
from PyQt5 import QtWidgets
import sys

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QFileDialog, QMessageBox

import disposablemail
import threading
import gui
from requests.adapters import HTTPAdapter
requests.adapters.DEFAULT_RETRIES=10
global path
sbf = datetime.datetime.now()
path =str(sbf.day)+'_'+str(sbf.month)+'_'+str(sbf.year)+'/'+str(sbf.hour)+'_'+str(sbf.minute)+'_'+str(sbf.second)

from random_username.generate import generate_username
global window
global rucaptcha_key
rucaptcha_key  = ""
global user_names,passwords, verify, proxies, email_list,amount,total_started,start_threads_flag
global proxy_path,proxies, timeout, proxy_type, retries
global errors,good
start_threads_flag = True
errors = 0
good = 0
proxy_type="http"
timeout = 20
proxy_path = ''
#proxies = open(proxy_path,"r").read().split('\n')
proxies = []
print(proxies)
total_started = 0
user_names = []
passwords = []
email_list = []
verify = True
retries = 10

from random import sample

ALPHNUM = (
    'qgftmrnzclwukphoydixavsbej' + \
    'ABCDEFGHIJKLMNOPQRSTUVWXYZ' + \
    '01234567890'
)
def generatePassWord(count=1, length=12, chars=ALPHNUM):
    """ Generate password

    Kwargs:
        count (int)::
            How many passwords should be returned?
        length (int)::
            How many characters should the password contain
        allowed_chars (str)::
            Characters

    Returns:
        String with the password. If count > 1 then the return value will be auto_now=
        list of strings.
    """
    if count == 1:
        return ''.join(sample(chars, length))

    passwords = []
    while count > 0:
        passwords.append(''.join(sample(chars, length)))
        count -= 1

    return passwords
def get_username():
    global user_names
    if len(user_names)>0:
        temp = user_names[0]
        user_names.pop(0)
        return temp
    else:
        return generate_username()[0]
def get_password():
    global passwords
    if len(passwords)>0:
        temp = passwords[0]
        passwords.pop(0)
        return temp
    else:
        return generatePassWord()
def get_email(proxy):
    global email_list
    if len(email_list)>0:
        temp = email_list[0]
        email_list.pop(0)
        return temp
    else:
        for i in range(retries):
            try:
                result = disposablemail.get_adr(proxy)
                break
            except Exception as e:
                if i== retries:
                    raise Exception("GettingEmailError:"+str(e))
                pass
        return result
def get_proxy():

    global proxies
    if len(proxies)==0:
        proxies = open(proxy_path,"r").read().split('\n')
    proxy = proxies[0]
    proxies.pop(0)
    return proxy
class Registrtaion:
    global proxy_type,errors,window,start_threads_flag
    def __init__(self):
        global errors,start_threads_flag
        self.session = requests.session()
        self.username = get_username()
        self.password = get_password()
        while True:
            if start_threads_flag==False:
                print("Останавливаю потоки(медленно)")
                exit()
            try:
                try:
                    temp = get_proxy()
                except:
                    return
                if proxy_type=="http":
                    self.proxy = {
                    "http": "http://"+temp,
                    "https": "https://" + temp
                    }
                if proxy_type=="socks":
                    self.proxy={
                        "https": "socks4://" + temp
                    }
                print(self.proxy)
                requests.get('https://www.twitch.tv/',proxies=self.proxy,timeout=timeout-5)
                #requests.get('https://post-shift.ru/api.php?action=new&type=json',proxies=self.proxy,timeout=10)
                print("Запустился один хороший поток.")
                break

            except Exception as e:
                #print(temp+" плохая прокси "+str(e))
                errors+=1

                print(str(e))
                pass
        self.email, self.key = self.username+"@gmail.com", "123a123aes123"#get_email(self.proxy)
    def validate_username(self):
        global retries
        data = [{
            "operationName": "UsernameValidator_User",
            "extensions":{
                "persistedQuery":{
                    "sha256Hash":"fd1085cf8350e309b725cf8ca91cd90cac03909a3edeeedbd0872ac912f3d660",
                    "version":1
                }
            },
            "operationName": "UsernameValidator_User",
            "variables":{
                'username':self.username
            }
        }]
        headers = {"Accept": "*/*",
                   "Content-Type": "text/plain;charset=UTF-8",
                  "Client-Id": "kimne78kx3ncx6brgo4mv6wki5h1ko",
                   "Referer": "https://www.twitch.tv/signup",
                   'sec-fetch-dest': 'empty',
                   'sec-fetch-mode': 'cors',
                   'sec-fetch-site': 'same-site',
                   'X-Device-Id': '25abf78f8feaa150'
                   }
        for i in range(retries):
            try:
                valid_req = requests.post("https://gql.twitch.tv/gql",data = json.dumps(data),headers=headers,proxies=self.proxy,timeout=timeout)
                break
            except Exception as e:
                if i == retries:
                    raise Exception("TimedOutWithRegister:"+str(e))
                pass
        return  valid_req.json()[0]['data']['isUsernameAvailable']
    def get_tokens(self):

        #self.token_link_container = self.session.get("https://www.twitch.tv/signup",proxies=self.proxy,timeout=timeout).text
        #ark_caps_token_link = self.token_link_container[self.token_link_container.rfind(',45:"')+5:self.token_link_container.rfind('",46:')]
        #caps_token_page = self.session.get("https://static.twitchcdn.net/assets/features.auth.components.auth-form.components.login-"+ark_caps_token_link+".js",proxies=self.proxy,timeout=timeout).text
        #self.caps_token = caps_token_page[
        #                  caps_token_page.find('FunCaptchaScriptType.SIGNUP,publicKey:"') + 39:caps_token_page.find(
        #                      '"},d=function(e)')]
        self.caps_token = "E5554D43-23CC-1982-971D-6A2262A2CA24"
        
    def register(self,session, ark_token):
        global errors
        headers = {
                   'origin': 'https://www.twitch.tv', 'referer': 'https://www.twitch.tv/', 'sec-fetch-dest': 'empty',
                   'sec-fetch-mode': 'cors', 'sec-fetch-site': 'cross-site'
                   }
        while True:
            if self.validate_username():
                break
            else:
                self.username = get_username()
                print(self.username)


        data1= '{"username":"' + \
               self.username + '","password":"' + self.password + '","email":"' + self.email + '","birthday":{"day":' + str(random.randint(1, 28)) + ',"month":' + str(random.randint(1, 12)) + ',"year":' + str(random.randint(1980, 2000)) + '},"client_id":"kimne78kx3ncx6brgo4mv6wki5h1ko","include_verification_code":true,"arkose":{"token":"' + ark_token + '"}}'
        data ={
            "arkose":{"token":ark_token,},
            "birthday":{"day":random.randint(1,28),"month":random.randint(1,12),"year":random.randint(1980,2000)},
            "client_id":"kimne78kx3ncx6brgo4mv6wki5h1ko",
            "email":self.email,
            "include_verification_code":"true",
            "password": self.password,
            "username": self.username
        }
        print(data)
        for i in range(retries):
            time.sleep(0.5)
            try:
                session_result = session.post("https://passport.twitch.tv/register",data=data1,headers=headers,proxies=self.proxy,timeout=timeout)
                break
            except Exception as e:
                errors+=1
                if i == retries:
                    raise Exception("TimedOutWithRegister:"+str(e))
        if('ip associated with signup throttled') in session_result.text:
            errors+=1

            raise Exception("IP-Blocked")
        print(session_result.json())
        try:
            os.makedirs(path)
        except:
            pass
        if "error_code" in session_result.text:
            open(path+"/errors.txt",'a').write(self.email+":"+self.username+":"+self.password+":"+session_result.text)
            if "Please complete the CAPTCHA correctly" in session_result:
                requests.post("http://rucaptcha.com/res.php?key="+rucaptcha_key+"&action=reportbad&id="+str(self.recived_captcha_id))
        else:
            file = open(path+"/log_pass.txt",'a')
            file.write('\n' + self.username + ":" + self.password)
            file.close()
            file = open(path+"/tokens.txt",'a')
            file.write('\n'+session_result.json()['access_token'])
            file.close()
            self.auth = session_result.json()['access_token']
    def Solve_Captcha(self):
        global retries, errors
        i=0
        while True:
            try:
                send_captcha = requests.get("https://rucaptcha.com/in.php?key="+rucaptcha_key+"&method=funcaptcha&publickey="+self.caps_token+"&surl=https://client-api.arkoselabs.com&pageurl=https://www.twitch.tv/signup?no-mobile-redirect=true&json=1",proxies=self.proxy,timeout=timeout)
                break
            except:
                if i>retries:
                    errors+=1

                    raise Exception("TimeOut.")
                i+=1
        captcha_id = send_captcha.json()['request']

        print(send_captcha.text)
        print("rucaptcha id:" + captcha_id + "arkose captcha token" + self.caps_token)
        while True:
            time.sleep(5)
            print("Ожидаю капчу.")
            try:
                recived_captcha = requests.get("https://rucaptcha.com/res.php?key="+rucaptcha_key+"&action=get&id="+captcha_id+"&json=1",proxies=self.proxy,timeout=timeout)
            except:
                continue
            if (recived_captcha.json()["request"] == "ERROR_CAPTCHA_UNSOLVABLE"):
                errors+=1

                raise Exception("CaptchaUnsolvable")
            if recived_captcha.json()['status']==1:
                print(recived_captcha.json())
                self.recived_captcha_id = captcha_id
                return recived_captcha.json()['request']
    def Verify(self):
        #тут проверка верификации.
        global retries
        time.sleep(5)
        verification = None
        i = 0
        while verification ==None:
            time.sleep(5)
            for i in range(retries):
                try:
                    verification = disposablemail.get_messages_list(self.key)
                    message = disposablemail.get_message_by_text(self.key,"twitch")
                    break
                except Exception as e:
                    if i ==retries:
                        return
                    pass
            if("Twitch" not in verification):
                verification=None
            else:
                verification_code = str(verification[verification.find("\nSubject: ")+10:verification.find("\nSubject: ")+16])

            i+=1
            if i>12:
                errors+=1

                raise Exception("Coudln't verify")
        print("TAG:"+verification)
        print("Verification_Code:"+verification_code)
        headers = {"Accept": "*/*",
                   'Authorization': 'OAuth ' + self.auth,
                   "Content-Type": "text/plain;charset=UTF-8",
                  "Client-Id": "kimne78kx3ncx6brgo4mv6wki5h1ko",
                   "Referer": "https://www.twitch.tv/",
                   'sec-fetch-dest': 'empty',
                   'sec-fetch-mode': 'cors',
                   'sec-fetch-site': 'same-site',
                   'X-Device-Id': '3744cfaeea4e0415',
                   }
        print(message)
        start = message.find('user_id=')+8
        end = message.find('&amp;',start)
        #
        print(start)
        print(end)
        print(message[start:end])
        user_id_key= message[start:end]
        #data1 = '[{"operationName":"ValidateVerificationCode","extensions":{"persistedQuery":{"version":"1","sha256Hash": "05eba55c37ee4eff4dae260850dd6703d99cfde8b8ec99bc97a67e584ae9ec31"}}, "variables":{"input":{"code":'+str(verification_code)+',"key":'+str(user_id_key)+',"address":'+self.email+'}}}]'
        data = '[{"operationName":"ValidateVerificationCode","variables":{"input":{"code":"'+verification_code+'","key":"'+user_id_key+'","address":"'+self.email+'"}},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"05eba55c37ee4eff4dae260850dd6703d99cfde8b8ec99bc97a67e584ae9ec31"}}}]'
        print(str(data))
        for i in range(retries):
            try:
                print(requests.post("https://gql.twitch.tv/gql",headers=headers,data=data,proxies=self.proxy,timeout=timeout+15).text)
                break
            except Exception as e:
                if i == retries:
                    return
                pass
        x=open(path+"/verified.txt",'a')
        x.write(self.username + ":" + self.password+'\n')
        x.close()
        file = open(path + "/verified_tokens.txt", 'a')
        file.write('\n' + self.auth)
        file.close()
    # def Follow(self,user):
    #     target_id = requests.get('https://api.twitch.tv/helix/users?login="'+user+'"',headers = {"Client-Id": "kimne78kx3ncx6brgo4mv6wki5h1ko"}).text
    #     print(target_id)
    #     headers = {"Accept": "*/*",
    #                'Authorization': 'OAuth ' + self.auth,
    #                "Content-Type": "text/plain;charset=UTF-8",
    #                "Client-Id": "kimne78kx3ncx6brgo4mv6wki5h1ko",
    #                "Referer": "https://www.twitch.tv/mikecoxlonk/",
    #
    #                'sec-fetch-dest': 'empty',
    #                'sec-fetch-mode': 'cors',
    #                'sec-fetch-site': 'same-site',
    #                'X-Device-Id': '3744cfaeea4e0415',
    #                }
    #     requests.post()
def Thread_Starter():
    #try:
        global amount, good, errors
        Reg1 = Registrtaion()
        for i in range(retries):
            try:
                Reg1.get_tokens()
                break
            except:
                if i ==retries:
                    errors+=1

                    raise Exception("GetTokensTimedOut")
                pass
        for i in range(retries):
            try:
                Reg1.validate_username()
                break
            except:
                if i ==retries:
                    errors+=1

                    raise Exception("GetTokensTimedOut")
                pass


        Reg1.register(Reg1.session, Reg1.Solve_Captcha())
        #Reg1.Verify()
        amount-=1
        good+=1



        return True
    #except Exception as e:
        #return e
global threads_list
threads_list = []
def start_threads(threads):
    global total_started, amount,start_threads_flag,errors,threads_list
    errors = 0
    while amount>0:
        if start_threads_flag==False:
            break
        my_thread = threading.Thread(target=Thread_Starter)
        my_thread.setDaemon(True)
        threads_list.append(my_thread)
        my_thread.start()

        total_started +=1
        time.sleep(1)
        while threading.activeCount()-1>threads:
            print("\n----------------------------------------------------------\nЗапущено "+str(threading.activeCount())+" потоков.")


            time.sleep(3)
            if amount == 0:
                return
class ExampleApp(QtWidgets.QMainWindow, gui.Ui_MainWindow):

    def __init__(self):

        super().__init__()

        self.setupUi(self)
        self.pushButton.clicked.connect(self.get_proxy_path)
        self.pushButtonStart.clicked.connect(self.start_program)
        self.pushButtonStopThreads.clicked.connect(self.disable_thread_start)

        self.stat_updater_timer = QTimer()
        self.stat_updater_timer.setInterval(1000)
        self.stat_updater_timer.timeout.connect(self.stat_updater)
        self.stat_updater_timer.start()
    def get_proxy_path(self):
        global proxy_path, proxies
        while True:
            try:
                proxy_path = QFileDialog.getOpenFileName(self, "Choose proxy file")[0]
                proxies = open(proxy_path,"r").read().split('\n')

                print(proxies)
                self.label_3.setText("Proxies:"+str(len(proxies)))
                break
            except:
                msgBox = QMessageBox()
                msgBox.setText("Произошла ошибка во время загрузки прокси, проверьте//\nThere was an error while importing proxies.");
                msgBox.exec();
    def start_program(self):
        global amount,rucaptcha_key, proxy_type,path,start_threads_flag
        try:
            amount = int(self.accounts_input.text())
            threads = int(self.threads_input.text())
        except:
            msgBox = QMessageBox()
            msgBox.setText(
                "Введите правильные значения для потоков и аккаунтов.\nUse integers for accounts and threads.");
            msgBox.exec();
            return
        if threads>amount:
            msgBox = QMessageBox()
            msgBox.setText(
                "Введите правильные значения для потоков и аккаунтов.\nEnter correct values for threads and accounts.");
            msgBox.exec();
            return

        proxy_type = self.comboBox.currentText()
        rucaptcha_key = self.lineEdit.text()
        print("Accounts:"+str(amount)+"\nThreads:"+str(threads)+"\nRucaptcha key:"+rucaptcha_key)
        sbf = datetime.datetime.now()
        path = str(sbf.day) + '_' + str(sbf.month) + '_' + str(sbf.year) + '/' + str(sbf.hour) + '_' + str(
            sbf.minute) + '_' + str(sbf.second)
        start_threads_flag = True
        my_thread = threading.Thread(target=start_threads, args={threads})
        my_thread.setDaemon(True)
        my_thread.start()
        self.pushButtonStart.setDisabled(True)
    def disable_thread_start(self):
        global start_threads_flag
        start_threads_flag = False



    def stat_updater(self):
        global good,errors
        self.label_2.setText("Errors:" + str(errors))
        self.label.setText("Accounts:" + str(good))
        self.label_4.setText("Threads:" + str(threading.activeCount() - 1))
        if threading.activeCount()==1 and not self.pushButtonStart.isEnabled():
            time.sleep(2)
            if threading.activeCount() == 1:
                self.pushButtonStart.setDisabled(False)
def main():
    global window
    app = QtWidgets.QApplication(sys.argv)
    window = ExampleApp()
    window.show()

    app.exec_()
if __name__ == '__main__':
    main()
#global amount

#amount  = 1

#start_threads(int(input("Сколько потоков:")))
#Reg1 = Registrtaion()
#Reg1.Follow("mikecoxlonk")
#Reg1.register()

#Reg1.register(Reg1.ark_token,Reg1.ClientId,"Pa$$W0rD","globgabgalab228","globgabgalab228@mail.ru",Reg1.session)

