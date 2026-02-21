from fake_useragent import UserAgent

def get_random_ua(header = True):
    ua = UserAgent()
    if header: return {"User-Agent" : ua.random}
    else : return ua.random