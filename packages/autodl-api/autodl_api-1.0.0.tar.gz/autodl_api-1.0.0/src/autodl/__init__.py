"""
AutoDL弹性部署API封装包
支持所有AutoDL弹性部署相关功能
"""

__version__ = "1.0.0"
__author__ = "AutoDL API Wrapper"
__email__ = "support@autodl.com"

from .autodl_elastic_deployment import AutoDLElasticDeployment, AutoDLConstants

__all__ = [
    "AutoDLElasticDeployment",  # 弹性部署API
    "AutoDLConstants",  # 常量定义
    "ImageInfo",  # 镜像信息
    "DeploymentInfo",  # 部署信息
    "ContainerInfo",  # 容器信息
    "GPUStockInfo",  # GPU库存信息
    "DDPInfo"  # 时长包信息
] 