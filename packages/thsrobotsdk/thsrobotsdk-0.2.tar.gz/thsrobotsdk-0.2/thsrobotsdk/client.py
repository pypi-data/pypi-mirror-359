import hashlib
import hmac
import time
import uuid
from urllib.parse import urlparse, parse_qs, urlencode

import requests
from requests.auth import AuthBase

from .exceptions import RequestError


class SignAuth(AuthBase):
    def __init__(self, secret_id: str, secret_key: str):
        self.secret_id = secret_id
        self.secret_key = secret_key

    def __call__(self, r):
        # 获取当前时间戳和nonce
        timestamp = str(int(time.time()))
        nonce = str(uuid.uuid4())
        body = r.body or b""

        parsed_url = urlparse(r.url)
        query_params = parse_qs(parsed_url.query)  # 获取查询参数字典
        # 对查询参数进行排序
        sorted_query_params = dict(sorted(query_params.items()))
        # 将排序后的查询参数重新编码为字符串
        sorted_params_str = urlencode(sorted_query_params, doseq=True)

        # 构造待签名字符串
        sign_data = [
            r.method,
            r.path_url.split("?")[0],
            sorted_params_str,
            timestamp,
            nonce,
            body.decode('utf-8') if isinstance(body, bytes) else body
        ]

        sign_data = '\n'.join(sign_data)

        # 使用HMAC算法和SHA256哈希函数创建签名
        signature = hmac.new(self.secret_key.encode('utf-8'), sign_data.encode('utf-8'), hashlib.sha256)

        # 将签名转换为十六进制字符串
        signature = signature.digest().hex()

        # 添加必要的认证头
        authorization = f"hmac id=\"{self.secret_id}\", ts=\"{timestamp}\", nonce=\"{nonce}\", sig=\"{signature}\""

        r.headers['Authorization'] = authorization

        return r


class ThsrobotSDK:
    def __init__(self, server_ip, secret_id: str, secret_key: str, port: int = 80):
        self.server_ip = server_ip
        self.port = port
        self.secret_id = secret_id
        self.secret_key = secret_key
        self.auth = SignAuth(secret_id, secret_key)

    def _request(self, method: str, endpoint: str, json_data=None):
        url = f'http://{self.server_ip}:{self.port}/api/v1/{endpoint}'
        try:
            if method == 'GET':
                response = requests.get(url, auth=self.auth)
            elif method == 'POST':
                response = requests.post(url, json=json_data, auth=self.auth)
            else:
                raise ValueError("Unsupported HTTP method")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise RequestError(response.status_code, str(e)) from e

    def buy(self, stock_code: str, price: str, vol: int, accept_risk: bool = False):
        """
        买入股票的方法。

        :param stock_code: 股票代码
        :param price: 买入价格
        :param vol: 买入数量
        :param accept_risk: 是否接受风险，如果true，表示提示风险也委托交易，默认 false
        :return: 服务器响应的 JSON 数据
        """
        start_time = time.time()
        print(f'开始买入:{stock_code} 价格：{price} 数量：{vol}')
        result = self._request('POST', 'buy', {
            "code": stock_code,
            "price": price,
            "volume": vol,
            "acceptRisk": accept_risk,
        })
        end_time = time.time()
        print(f"买入执行耗时: {end_time - start_time} 秒")
        return result

    def sync_buy(self, stock_code: str, price: float, vol: int, accept_risk: bool = False):
        """
        异步买入股票的方法。

        :param stock_code: 股票代码
        :param price: 买入价格
        :param vol: 买入数量
        :param accept_risk: 是否接受风险，如果true，表示提示风险也委托交易，默认 false
        :return: 服务器响应的 JSON 数据
        """
        start_time = time.time()
        print(f'开始买入:{stock_code} 价格：{price} 数量：{vol}')
        result = self._request('POST', 'sync/buy', {
            "code": stock_code,
            "price": price,
            "volume": vol,
            "acceptRisk": accept_risk,
        })
        end_time = time.time()
        print(f"买入执行耗时: {end_time - start_time} 秒")
        return result

    def sell(self, stock_code, price, vol):
        """
        卖出股票的方法。

        :param stock_code: 股票代码
        :param price: 卖出价格
        :param vol: 卖出数量
        :return: 服务器响应的 JSON 数据
        """
        start_time = time.time()
        stock_code = stock_code[:6]
        print(f'开始卖出:{stock_code} 价格：{price} 数量：{vol}')
        result = self._request('POST', 'sell', {
            "code": stock_code,
            "price": price,
            "volume": vol
        })
        end_time = time.time()
        print(f"卖出执行耗时: {end_time - start_time} 秒")
        return result

    def sync_sell(self, stock_code, price, vol):
        """
        异步卖出股票的方法。

        :param stock_code: 股票代码
        :param price: 卖出价格
        :param vol: 卖出数量
        :return: 服务器响应的 JSON 数据
        """
        start_time = time.time()
        stock_code = stock_code[:6]
        print(f'开始卖出:{stock_code} 价格：{price} 数量：{vol}')
        result = self._request('POST', 'sync/sell', {
            "code": stock_code,
            "price": price,
            "volume": vol
        })
        end_time = time.time()
        print(f"卖出执行耗时: {end_time - start_time} 秒")
        return result

    def cancel(self, cancelType):
        """
        委撤撤单的方法。
        :param cancelType: 撤单类型 cancelType：0=全部撤单，1=撤买入单，2=撤卖出单
        :return: 服务器响应的 JSON 数据
        """
        start_time = time.time()
        print('开始全部撤单')
        result = self._request('POST', 'cancel', {
            "cancelType": cancelType
        })
        end_time = time.time()
        print(f"撤单执行耗时: {end_time - start_time} 秒")
        return result

    def sync_cancel(self, cancelType):
        """
        委撤撤单的方法。
        :param cancelType: 撤单类型 cancelType：0=全部撤单，1=撤买入单，2=撤卖出单
        :return: 服务器响应的 JSON 数据
        """
        start_time = time.time()
        print('开始全部撤单')
        result = self._request('POST', 'sync/cancel', {
            "cancelType": cancelType
        })
        end_time = time.time()
        print(f"撤单执行耗时: {end_time - start_time} 秒")
        return result

    def get_assets(self):
        """
        获取账户资金的方法。

        :return: 账户资金数据
        """
        result = self._request('GET', 'assets')
        return result['data']

    def get_order(self):
        """
        获取委托信息的方法。

        :return: 委托信息数据，如果不存在则返回 None
        """
        result = self._request('GET', 'order')
        return result.get('data')

    def get_position(self):
        """
        获取持仓信息的方法。

        :return: 持仓信息数据
        """
        result = self._request('GET', 'position')
        return result['data']
