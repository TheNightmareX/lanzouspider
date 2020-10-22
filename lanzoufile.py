import urllib.request
import urllib.parse
import re
import json


class LanzouFile:
    __USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.80 Safari/537.36 Edg/86.0.622.43'

    def __init__(self, url: str):
        self.url = url
        self.parsed_url = urllib.parse.urlparse(url)

    def __get(self, url: str):
        HEADERS = {
            'User-Agent': self.__USER_AGENT,
            'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
        }
        request = urllib.request.Request(url, None, HEADERS)
        response = urllib.request.urlopen(request)
        return response

    def __post(self, url: str, data: dict):
        HEADERS = {
            'User-Agent': self.__USER_AGENT,
            'referer': self.url
        }
        data = urllib.parse.urlencode(data).encode('utf-8')
        request = urllib.request.Request(url, data, HEADERS, method='post')
        response = urllib.request.urlopen(request)
        return response

    @property
    def iframe_url(self):
        """
        """
        html = self.__get(self.url).read().decode('utf-8')
        re_result = re.search('iframe.*name="\d{2,}" src="(.*?)(?=")', html)
        return f"{self.parsed_url.scheme}://{self.parsed_url.hostname}{re_result[1]}"

    @property
    def redirect_url(self):
        html = self.__get(self.iframe_url).read().decode('utf-8')
        json_response = self.__post(f"{self.parsed_url.scheme}://{self.parsed_url.hostname}/ajaxm.php", {
            'action': 'downprocess',
            'sign': re.search("ajaxdata = '(.*)'", html)[1],
            'ves': 1
        }).read().decode('utf-8')
        json_response = json.loads(json_response)
        return f"{json_response['dom']}/file/{json_response['url']}"

    @property
    def binary(self):
        return self.__get(self.redirect_url).read()