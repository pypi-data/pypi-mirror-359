# aiwenSDK

埃文商业API的Python SDK，提供对埃文商业API的网络请求封装，方便调用。

## 安装

```bash
pip install aiwenSDK
```

## 快速开始

```python
from aiwenSDK import aiwenClient, aiwenKey

# 设置API密钥
key = aiwenKey(api_key="your_api_key")

# 创建客户端实例
client = aiwenClient(key)

# 调用API
# ...具体使用方法请参考相关文档
```

## 主要模块

- **client**: API客户端模块
- **awEnum**: 枚举类型定义
- **awModel**: 数据模型和密钥管理
- **awException**: 异常处理

## 开发者

- 作者: aiwen
- 邮箱: sales@ipplus360.com
- 网站: https://www.ipplus360.com

## 许可证

请查看项目许可证文件了解详情。