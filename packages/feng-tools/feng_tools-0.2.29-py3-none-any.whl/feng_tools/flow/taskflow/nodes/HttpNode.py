from datetime import datetime
from typing import Optional

import requests
from pydantic import Field, BaseModel
from requests import request

from feng_tools.flow.taskflow.base.Node import Node
from feng_tools.flow.taskflow.schemas.enums import HttpMethod


class InputParam(BaseModel):
    """HTTP请求输入参数，对应requests.request方法的参数"""
    url: str = Field(title='请求链接', description='HTTP请求的URL链接')
    method: Optional[HttpMethod] = Field(HttpMethod.GET, title='请求方法', description='HTTP请求的方法，如GET、POST等')
    
    # 请求参数
    params: Optional[dict] = Field(None, title='查询参数', description='URL查询字符串参数，会附加到URL后')
    headers: Optional[dict[str, str]] = Field(None, title='请求头', description='HTTP请求的头信息')
    cookies: Optional[dict[str, str]] = Field(None, title='Cookies', description='请求的Cookie信息')
    
    # 请求体数据
    data: Optional[dict] = Field(None, title='表单数据', description='请求体数据，用于表单提交')
    json_data: Optional[dict] = Field(None, title='JSON数据', description='JSON格式的请求体数据，会自动序列化')
    files: Optional[dict] = Field(None, title='上传文件', description='要上传的文件，用于multipart/form-data请求')
    
    # 认证与安全
    auth: Optional[tuple] = Field(None, title='认证信息', description='HTTP认证信息，通常为(username, password)元组')
    verify: Optional[bool] = Field(False, title='验证SSL证书', description='是否验证SSL证书，可设为False跳过验证')
    cert: Optional[tuple] = Field(None, title='客户端证书', description='SSL客户端证书，可以是路径字符串或(cert, key)元组')
    
    # 请求控制
    timeout: Optional[float] = Field(None, title='超时时间', description='请求超时时间，单位为秒')
    allow_redirects: Optional[bool] = Field(True, title='允许重定向', description='是否允许请求重定向')
    proxies: Optional[dict[str, str]] = Field(None, title='代理设置', description='代理服务器设置，如{"http": "http://proxy.example.com:8080"}',
                                              examples={"http": "http://proxy.example.com:8080"})
    stream: Optional[bool] = Field(False, title='流式请求', description='是否立即下载响应内容')
    is_json_response: Optional[bool] = Field(True, title='json响应', description='是否是json响应')
    encoding: Optional[str] = Field('utf-8', title='响应内容编码', description='响应内容编码，默认是utf-8')

class OutputResult(BaseModel):
    request_param:InputParam = Field(None, title='请求参数', description='请求参数')
    response_status:Optional[int] = Field(None, title='响应码', description='HTTP请求的响应码')
    response_headers: Optional[dict[str, str]] = Field(None, title='响应头', description='HTTP请求的响应头')
    response_content: Optional[bytes] = Field(None, title='响应二进制内容', description='HTTP请求的响应二进制内容')
    response_data: Optional[bytes|str|dict] = Field(None, title='响应内容', description='HTTP请求的响应内容')
    redirect_count: Optional[int] = Field(None, title='请求重定向次数', description='HTTP请求的重定向次数')

class HttpNode(Node):
    def input(self, param: InputParam):
        self.log_list.append(f'[{datetime.now().strftime("%Y-%m-%d, %H:%M:%S")}]开始请求...')
        self.log_list.append(f'请求url:{param.url}')
        self.log_list.append(f'请求方法:{param.method.name}')
        self.log_list.append(f'请求参数:{param.params}')
        response =  request(param.method.value.value, param.url,
                            params=param.params,
                            data=param.data,
                            json=param.json_data,
                            files=param.files,
                            headers=param.headers,
                            cookies=param.cookies,
                            timeout=param.timeout,
                            allow_redirects=param.allow_redirects,
                            proxies=param.proxies,
                            stream=param.stream,
                            auth=param.auth,
                            verify=param.verify,
                            cert=param.cert)
        self.log_list.append(f'[{datetime.now().strftime("%Y-%m-%d, %H:%M:%S")}]请求结束')
        self.log_list.append(f'响应码：{response.status_code}')
        response.encoding = param.encoding
        self.log_list.append(f'响应内容：{response.text}')
        self.output_result = OutputResult(request_param=param, response_status=response.status_code,
                                          response_headers=response.headers,
                                          response_content=response.content,
                                          redirect_count=response.raw.retries.total if response.raw else None)
        if param.is_json_response:
            try:
                self.output_result.response_data = response.json()
            except requests.exceptions.JSONDecodeError:
                # 如果JSON解析失败，回退到使用文本响应
                self.output_result.response_data = response.text
                print(f"警告: 响应内容不是有效的JSON格式，已回退到文本响应。响应状态码: {response.status_code}")
        else:
            self.output_result.response_data = response.text

    def output(self) -> OutputResult:
        return self.output_result

if __name__ == '__main__':
    # 测试 JSON 响应
    print("\n=== 测试 JSON 响应 ===")
    json_node = HttpNode('test_json', 'test_json')
    json_param = InputParam(
        url='https://jsonplaceholder.typicode.com/posts/1',
        headers={'accept': 'application/json'},
        is_json_response=True
    )
    json_node.input(json_param)
    json_out = json_node.output()
    print(f"JSON响应状态码: {json_out.response_status}")
    print(f"JSON响应类型: {type(json_out.response_data)}")
    print(f"JSON响应内容: {json_out.response_data}")
    
    # 测试非 JSON 响应（HTML）
    print("\n=== 测试非 JSON 响应（HTML） ===")
    html_node = HttpNode('test_html', 'test_html')
    html_param = InputParam(
        url='https://example.com',
        headers={'accept': 'text/html'},
        is_json_response=True  # 故意设置为True，测试错误处理
    )
    html_node.input(html_param)
    html_out = html_node.output()
    print(f"HTML响应状态码: {html_out.response_status}")
    print(f"HTML响应类型: {type(html_out.response_data)}")
    print(f"HTML响应前100个字符: {html_out.response_data[:100] if isinstance(html_out.response_data, str) else '非文本内容'}")
    log_result = html_node.log()
    print('\n'.join(log_result.log_list))