#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SARM SDK 安全问题 API

提供安全问题相关的API操作。
"""

from typing import List, Dict, Any, Optional, TYPE_CHECKING
from ..models.response import BatchOperationResult
from ..exceptions import SARMValidationError

if TYPE_CHECKING:
    from ..client import SARMClient


class SecurityIssueAPI:
    """安全问题API类"""
    
    def __init__(self, client: 'SARMClient'):
        self.client = client
    
    def create_batch(
        self,
        issues: List[Dict[str, Any]],
        execute_release: bool = False
    ) -> BatchOperationResult:
        """
        批量创建安全问题
        
        Args:
            issues: 安全问题数据列表
            execute_release: 是否直接发布
            
        Returns:
            批量操作结果
        """
        if not issues:
            raise SARMValidationError("安全问题列表不能为空")
        
        if len(issues) > 1000:
            raise SARMValidationError("单次批量操作不能超过1000条记录")
        
        # 发送请求
        response = self.client.post(
            '/api/issue/',
            data=issues,
            execute_release=execute_release
        )
        
        # 处理批量操作结果
        if isinstance(response, dict) and 'code' in response and 'data' in response:
            from ..models.response import BatchOperationItem
            
            # 如果有详细的响应数据
            if isinstance(response.get('data'), list):
                items = [
                    BatchOperationItem(
                        unique_id=item.get('unique_id', ''),
                        name=item.get('title', ''),
                        success=item.get('success', False),
                        msg=item.get('msg', '')
                    )
                    for item in response['data']
                ]
            else:
                # 简单成功响应
                success = response.get('code') == 200
                items = [
                    BatchOperationItem(
                        unique_id=issue.get('issue_unique_id', f"issue_{i}"),
                        name=issue.get('issue_title', ''),
                        success=success,
                        msg="创建成功" if success else "创建失败"
                    )
                    for i, issue in enumerate(issues)
                ]
            
            return BatchOperationResult(
                data=items,
                code=response.get('code', 200)
            )
        
        return BatchOperationResult(**response)
    
    def create(self, issue: Dict[str, Any], execute_release: bool = False) -> BatchOperationResult:
        """创建单个安全问题"""
        return self.create_batch([issue], execute_release=execute_release)
    
    def update(self, issue_data: Dict[str, Any], execute_release: bool = False) -> Dict[str, Any]:
        """更新安全问题信息"""
        if 'issue_unique_id' not in issue_data:
            raise SARMValidationError("更新安全问题时必须提供 issue_unique_id")
        
        response = self.client.post(
            '/api/issue/update', 
            data=issue_data,
            execute_release=execute_release
        )
        return response
    
    def get_list(
        self,
        page: int = 1,
        limit: int = 50,
        status: Optional[str] = None,
        level: Optional[str] = None,
        **filters
    ) -> Dict[str, Any]:
        """
        获取安全问题列表
        
        Args:
            page: 页码
            limit: 每页条数
            status: 问题状态
            level: 问题级别
            **filters: 其他过滤条件
            
        Returns:
            安全问题列表
        """
        data = {
            "page": page,
            "limit": limit,
            **filters
        }
        if status:
            data["status"] = status
        if level:
            data["level"] = level
        
        response = self.client.post('/api/issue/', data=data)
        return response
    
    def get_component_vuln_list(self, issue_unique_id: str) -> Dict[str, Any]:
        """获取安全问题关联的成分和漏洞列表"""
        response = self.client.get(f'/api/issue/component_vuln_list/{issue_unique_id}')
        return response
    
    def update_component_vuln_list(
        self, 
        issue_unique_id: str, 
        component_ids: List[str], 
        vuln_ids: List[str]
    ) -> Dict[str, Any]:
        """更新安全问题关联的成分和漏洞列表"""
        data = {
            "component_unique_id": component_ids,
            "vuln_unique_id": vuln_ids
        }
        response = self.client.post(
            f'/api/issue/update_component_vuln_list/{issue_unique_id}',
            data=data
        )
        return response
    
    def update_component_list(
        self, 
        issue_unique_id: str, 
        component_ids: List[str]
    ) -> Dict[str, Any]:
        """更新安全问题关联的成分列表"""
        data = {"component_unique_id": component_ids}
        response = self.client.post(
            f'/api/issue/update_component_list/{issue_unique_id}',
            data=data
        )
        return response 