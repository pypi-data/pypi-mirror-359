#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SARM SDK - Security Asset Risk Management Platform Python SDK

这是一个用于与资产风险管理平台交互的Python SDK，提供了完整的API封装和数据模型。

主要功能：
- 组织架构管理
- 业务系统管理  
- 应用载体管理
- 软件成分管理
- 漏洞管理
- 安全问题管理
- 安全能力管理

使用示例：
    >>> from sarm_sdk import SARMClient
    >>> client = SARMClient(
    ...     base_url="https://api.platform.com",
    ...     token="your-bearer-token"
    ... )
    >>> organizations = client.organizations.create_batch([...])
"""

__version__ = "1.0.2"
__author__ = "Murphysec Team"
__email__ = "developer@murphysec.com"

from .client import SARMClient
from .exceptions import (
    SARMException,
    SARMAPIError,
    SARMValidationError,
    SARMNetworkError,
    SARMAuthenticationError,
    SARMAuthorizationError,
    SARMServerError,
)

# 导出主要类和异常
__all__ = [
    "SARMClient",
    "SARMException", 
    "SARMAPIError",
    "SARMValidationError",
    "SARMNetworkError",
    "SARMAuthenticationError",
    "SARMAuthorizationError",
    "SARMServerError",
] 