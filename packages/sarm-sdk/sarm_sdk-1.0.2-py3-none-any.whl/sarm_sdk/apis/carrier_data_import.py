#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SARM SDK 载体数据录入 API

提供载体维度的多数据录入功能，一次性录入载体、安全问题、组件和漏洞数据。
"""

from typing import List, Dict, Any, Optional, TYPE_CHECKING
from ..models.response import BatchOperationResult
from ..exceptions import SARMValidationError

if TYPE_CHECKING:
    from ..client import SARMClient


class CarrierDataImportAPI:
    """载体数据录入API类"""
    
    def __init__(self, client: 'SARMClient'):
        self.client = client
    
    def import_carrier_data(
        self,
        carrier_data_list: List[Dict[str, Any]],
        execute_release: bool = False
    ) -> BatchOperationResult:
        """
        载体维度多数据录入
        
        一次性录入载体、安全问题、组件和漏洞数据。
        
        Args:
            carrier_data_list: 载体数据列表，每个元素包含：
                - carrier: 载体信息
                - source_type: 数据来源类型 (automatic/manual)
                - issue_list: 安全问题列表（可选）
                - component_list: 组件列表（可选）  
                - vuln_list: 漏洞列表（可选）
            execute_release: 是否直接发布
            
        Returns:
            批量操作结果
            
        Raises:
            SARMValidationError: 数据验证错误
        """
        if not carrier_data_list:
            raise SARMValidationError("载体数据列表不能为空")
        
        if len(carrier_data_list) > 50:
            raise SARMValidationError("单次批量操作不能超过50条载体记录")
        
        # 发送请求
        response = self.client.post(
            '/api/insert/insert_carrier_issue',
            data=carrier_data_list,
            execute_release=execute_release
        )
        
        # 处理简单的成功响应
        if isinstance(response, dict) and 'code' in response:
            success = response.get('code') == 200
            # 创建批量操作结果
            from ..models.response import BatchOperationItem
            items = [
                BatchOperationItem(
                    unique_id=data.get('carrier', {}).get('carrier_unique_id', f"carrier_{i}"),
                    name=data.get('carrier', {}).get('name', ''),  # 原始API使用 "name" 字段
                    success=success,
                    msg="录入成功" if success else "录入失败"
                )
                for i, data in enumerate(carrier_data_list)
            ]
            
            return BatchOperationResult(
                data=items,
                code=response.get('code', 200)
            )
        
        return BatchOperationResult(**response)
    
    def create_carrier_data_structure(
        self,
        carrier_info: Dict[str, Any],
        source_type: str = "automatic",
        issue_list: Optional[List[Dict[str, Any]]] = None,
        component_list: Optional[List[Dict[str, Any]]] = None,
        vuln_list: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        创建标准的载体数据结构
        
        Args:
            carrier_info: 载体基础信息
            source_type: 数据来源类型，automatic或manual
            issue_list: 安全问题列表
            component_list: 组件列表
            vuln_list: 漏洞列表
            
        Returns:
            标准的载体数据结构
        """
        data = {
            "carrier": carrier_info,
            "source_type": source_type
        }
        
        if issue_list:
            data["issue_list"] = issue_list
        if component_list:
            data["component_list"] = component_list
        if vuln_list:
            data["vuln_list"] = vuln_list
            
        return data 