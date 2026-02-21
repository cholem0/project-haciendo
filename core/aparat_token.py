import httpx
import json
import core.config
from utils.misc import get_random_ua
import os
from bs4 import BeautifulSoup
from dotenv import load_dotenv


RETRY = 0

def extract_cookies(cookies):
    cookies_dict = {}
    for x in cookies.keys():
        cookies_dict[x] = cookies.get(x)
    return cookies_dict

def get_guid():
    headers=get_random_ua()
    guid_resp = httpx.get("https://www.aparat.com/login" , headers=headers)
    soup = BeautifulSoup(guid_resp.text , 'html.parser')
    script_tag = soup.find('script', string=lambda text: text and 'window.__AUTH_CONFIG__' in text)
    guid = script_tag.string.split('guid:')[1].split(',')[0].strip().strip('"')
    return guid , headers , guid_resp.cookies

def get_account_token(email :str , password : str):
    guid , headers , cookies = get_guid()
    data = {'guid' : guid}
    
    req_cookies = extract_cookies(cookies)
    res = httpx.get(f"https://aparat.com/api/fa/v1/user/Authenticate/ui_config?guid={guid}" , headers=headers , cookies=req_cookies , follow_redirects=True)
    new_cookies = extract_cookies(res.cookies)
    req_cookies.update(new_cookies)
    
    temp_id_resp = httpx.post(f"https://www.aparat.com/api/fa/v1/user/Authenticate/auth" ,data = data , headers=headers , cookies=req_cookies , follow_redirects=True)
    temp_id_json = json.loads(temp_id_resp.text)
    temp_id_attr = temp_id_json.get('data').get('attributes')
    temp_id = temp_id_attr.get('temp_id')
    guid = temp_id_attr.get('GUID')
    login_1st_data = {
        'account' : email,
        'temp_id': temp_id,
        'guid' : guid
    }
    login_1st_resp = httpx.post(f"https://www.aparat.com/api/fa/v1/user/Authenticate/signin_step1" ,data = login_1st_data , headers=headers , cookies=req_cookies , follow_redirects=True)
    if login_1st_resp.status_code == 200:
        login_1st_json = json.loads(login_1st_resp.text)
        login_1st_attr = login_1st_json.get('data').get('attributes')
        login_2nd_data = {
            'temp_id' : login_1st_attr.get('temp_id'),
            'account' : email,
            'codepass_type' : 'pass',
            'code' : password,
            'guid' : login_1st_data.get('guid')
        }
        login_2nd_resp = httpx.post(f"https://www.aparat.com/api/fa/v1/user/Authenticate/signin_step2" ,data = login_2nd_data , headers=headers , cookies=req_cookies , follow_redirects=True)
        if login_2nd_resp.status_code == 200:
            return json.loads(login_2nd_resp.text).get('data').get('attributes').get('token')
    return login_2nd_resp


def get_chat_auth(auth_token , streamer_name = 'cholemo'):
    cookies = {'AuthV1' : auth_token}
    headers = get_random_ua()
    resp = httpx.get(f"https://www.aparat.com/api/fa/v2/Live/LiveStream/show/username/{streamer_name}" , cookies=cookies , headers=headers)
    if resp.status_code == 200:
        user_data_dict = json.loads(resp.text).get('user_data')
        return user_data_dict
    else:
        return ''

def is_login_check():
    resp = httpx.get("https://www.aparat.com/api/fa/v1/etc/page/config/mode/full")
    data = json.loads(resp.text)

    if data.get('data').get('relationships').get("profileInformation").get('data'):
         return True
    return False


def get_user_data():

    if os.path.exists(core.config.HACIENDO_ENV_PATH):
        load_dotenv(dotenv_path=core.config.HACIENDO_ENV_PATH)

        core.config.APARAT_LUSER = os.getenv("luser")
        core.config.APARAT_LTOKEN = os.getenv("ltoken")
        if core.config.APARAT_LUSER and core.config.APARAT_LTOKEN:
            return 1
        else: return 0
    else:
        auth_v1 = get_account_token(core.config.APARAT_EMAIL , core.config.APARAT_PASS)
        if auth_v1:
            user_data = get_chat_auth(auth_token=auth_v1)
            if user_data:
                with open(core.config.HACIENDO_ENV_PATH , 'w') as f:
                    f.write(
                        f"luser='{user_data.get('luser')}'\nltoken='{user_data.get('ltoken')}'"
                    )
                core.config.APARAT_LUSER = user_data.get('luser')
                core.config.APARAT_LTOKEN = user_data.get('ltoken')
        return 1
         
