"""
B_HttpClient.py - 高级HTTP客户端封装
支持GET/POST请求、代理设置、多线程安全、自动重试
实现 __enter__ 和 __exit__ 方法的主要目的是：
    确保 HTTP 连接资源被可靠释放
    简化资源管理代码
    提供异常安全的保证
    支持 Pythonic 的 with 语句用法
    在多线程环境中安全地管理连接池
"""

import requests
from threading import local
import json
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class HttpClient:
    """
    线程安全的HTTP客户端，封装requests库
    支持GET/POST方法、代理设置、自动重试
    """

    def __init__(self, default_headers=None, default_timeout=10, max_retries=3):
        """
        初始化HTTP客户端

        :param default_headers: 默认请求头 (dict)
        :param default_timeout: 默认超时时间(秒) (int/float)
        :param max_retries: 最大重试次数 (int)
        """
        self._thread_local = local()  # 线程局部存储
        self.default_headers = default_headers or {}
        self.default_timeout = default_timeout
        self.max_retries = max_retries

    def __enter__(self):
        """上下文管理器入口"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器退出时自动关闭Session"""
        self.close()

    def _get_session(self):
        """获取当前线程的Session对象（线程安全）"""
        if not hasattr(self._thread_local, "session"):
            session = requests.Session()

            # 设置重试机制
            if self.max_retries > 0:
                retry_strategy = Retry(
                    total=self.max_retries,
                    status_forcelist=[429, 500, 502, 503, 504],
                    allowed_methods=["GET", "POST", "PUT", "DELETE"],
                    backoff_factor=0.3,
                    raise_on_status=False
                )
                adapter = HTTPAdapter(max_retries=retry_strategy)
                session.mount("http://", adapter)
                session.mount("https://", adapter)

            self._thread_local.session = session
        return self._thread_local.session

    def _merge_headers(self, headers):
        """合并默认请求头和自定义请求头"""
        merged = self.default_headers.copy()
        if headers:
            merged.update(headers)
        return merged

    def request(self, method, url, params=None, data=None, json=None,
                headers=None, proxies=None, timeout=None, **kwargs):
        """
        执行HTTP请求

        :param method: HTTP方法 (GET/POST/PUT/DELETE)
        :param url: 请求URL (str)
        :param params: URL查询参数 (dict)
        :param data: 表单数据 (dict/bytes)
        :param json: JSON数据 (dict)
        :param headers: 请求头 (dict)
        :param proxies: 代理设置 (dict) 格式: {'http': 'x.x.x.x:port', 'https': 'x.x.x.x:port'}
        :param timeout: 超时时间(秒) (int/float/tuple(connect, read))
        :param kwargs: 其他requests参数
        :return: requests.Response对象
        :raises: RuntimeError 当请求失败时
        """
        # 合并请求头
        headers = self._merge_headers(headers)
        # 设置超时
        timeout = timeout or self.default_timeout

        session = self._get_session()

        try:
            response = session.request(
                method=method.upper(),
                url=url,
                params=params,
                data=data,
                json=json,
                headers=headers,
                proxies=proxies,
                timeout=timeout,
                **kwargs
            )
            response.raise_for_status()  # 自动检查HTTP错误
            return response
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Request to {url} failed: {str(e)}") from e

    def get(self, url, params=None, headers=None, proxies=None, timeout=None, **kwargs):
        """
        执行GET请求

        :param url: 请求URL (str)
        :param params: URL查询参数 (dict)
        :return: requests.Response对象
        其他参数同request方法
        """
        return self.request('GET', url, params=params, headers=headers,
                            proxies=proxies, timeout=timeout, **kwargs)

    def post(self, url, data=None, json=None, headers=None, proxies=None, timeout=None, **kwargs):
        """
        执行POST请求

        :param url: 请求URL (str)
        :param data: 表单数据 (dict/bytes)
        :param json: JSON数据 (dict)
        :return: requests.Response对象
        其他参数同request方法
        """
        return self.request('POST', url, data=data, json=json, headers=headers,
                            proxies=proxies, timeout=timeout, **kwargs)

    def close(self):
        """关闭所有线程的Session（多线程环境结束时必须调用）"""
        if hasattr(self._thread_local, "session"):
            try:
                self._thread_local.session.close()
            finally:
                del self._thread_local.session

    @staticmethod
    def example_get_request():
        """
        GET请求使用示例
        功能: 演示如何使用HttpClient执行GET请求
        返回: None (打印结果到控制台)
        """
        print("\n" + "=" * 50)
        print("GET请求示例")
        print("=" * 50)

        # 创建客户端实例
        client = HttpClient(
            default_headers={'User-Agent': 'B_HttpClient/1.0'},
            default_timeout=15
        )

        try:
            # 执行GET请求
            response = client.get(
                url='https://httpbin.org/get',
                params={'param1': 'value1', 'param2': 'value2'}
            )

            # 处理响应
            print(f"状态码: {response.status_code}")
            print("响应头:")
            for key, value in response.headers.items():
                print(f"  {key}: {value}")

            print("\n响应内容:")
            print(json.dumps(response.json(), indent=2))

        except RuntimeError as e:
            print(f"请求失败: {e}")
        finally:
            client.close()

    @staticmethod
    def example_post_request():
        """
        POST请求使用示例
        功能: 演示如何使用HttpClient执行POST请求
        返回: None (打印结果到控制台)
        """
        print("\n" + "=" * 50)
        print("POST请求示例")
        print("=" * 50)

        # 创建客户端实例
        client = HttpClient(max_retries=2)

        try:
            # 执行POST请求
            response = client.post(
                url='https://httpbin.org/post',
                json={'username': 'test_user', 'action': 'login'},
                headers={
                    'Content-Type': 'application/json',
                    'X-Request-ID': '12345'
                }
            )

            # 处理响应
            print(f"状态码: {response.status_code}")
            print("响应内容:")
            data = response.json()
            print(f"请求URL: {data.get('url')}")
            print(f"发送的JSON数据: {json.dumps(data.get('json'), indent=2)}")
            print(f"请求头: {json.dumps(dict(data.get('headers')), indent=2)}")

        except RuntimeError as e:
            print(f"请求失败: {e}")
        finally:
            client.close()

    @staticmethod
    def example_proxy_request():
        """
        代理请求使用示例
        功能: 演示如何使用代理执行请求
        返回: None (打印结果到控制台)
        """
        print("\n" + "=" * 50)
        print("代理请求示例")
        print("=" * 50)

        # 注意: 这里的代理地址需要替换为实际可用的代理
        proxies = {
            'http': 'http://user:pass@proxy.example.com:8080',
            'https': 'http://user:pass@proxy.example.com:8080'
        }

        # 创建客户端实例
        client = HttpClient(
            default_headers={'User-Agent': 'ProxyClient/1.0'},
            default_timeout=20
        )

        try:
            # 尝试通过代理获取当前IP
            print("尝试通过代理获取IP信息...")
            response = client.get(
                url='https://httpbin.org/ip',
                proxies=proxies
            )

            ip_info = response.json()
            print(f"通过代理访问, 您的IP是: {ip_info.get('origin')}")

        except RuntimeError as e:
            print(f"代理请求失败: {e}")
            print("注意: 示例中使用了示例代理地址，请替换为实际可用的代理")
        finally:
            client.close()

    @staticmethod
    def example_thread_safe_usage():
        """
        多线程安全使用示例
        功能: 演示如何在多线程环境中安全使用HttpClient
        返回: None (打印结果到控制台)
        """
        print("\n" + "=" * 50)
        print("多线程使用示例")
        print("=" * 50)

        from concurrent.futures import ThreadPoolExecutor, as_completed

        # 要访问的URL列表
        urls = [
            'https://httpbin.org/get?thread=1',
            'https://httpbin.org/get?thread=2',
            'https://httpbin.org/get?thread=3',
            'https://httpbin.org/get?thread=4',
            'https://httpbin.org/get?thread=5'
        ]

        def worker(url):
            """线程工作函数"""
            # 每个线程创建自己的HttpClient实例
            with HttpClient() as client:
                try:
                    response = client.get(url)
                    return response.json().get('args', {}).get('thread')
                except RuntimeError:
                    return f"Failed: {url}"

        # 使用线程池执行
        with ThreadPoolExecutor(max_workers=3) as executor:
            # 提交任务
            futures = {executor.submit(worker, url): url for url in urls}

            print("多线程请求结果:")
            for future in as_completed(futures):
                url = futures[future]
                try:
                    result = future.result()
                    print(f"URL: {url} => Thread ID: {result}")
                except Exception as e:
                    print(f"处理{url}时出错: {str(e)}")


# if __name__ == "__main__":
#     # 运行所有示例
#     HttpClient.example_get_request()
#     HttpClient.example_post_request()
#     HttpClient.example_proxy_request()
#     HttpClient.example_thread_safe_usage()