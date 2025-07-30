"""
AutoDL弹性部署API封装类
支持所有弹性部署相关功能
"""

import requests
from typing import Dict, List, Optional, Union
from dataclasses import dataclass
from datetime import datetime



class AutoDLConstants:
    """AutoDL常量定义"""
    
    # 地区标识
    REGIONS = {
        "西北企业区(推荐)": "westDC2",
        "西北B区": "westDC3", 
        "北京A区": "beijingDC1",
        "北京B区": "beijingDC2",
        "L20专区(原北京C区)": "beijingDC4",
        "V100专区(原华南A区)": "beijingDC3",
        "内蒙A区": "neimengDC1",
        "佛山区": "foshanDC1",
        "重庆A区": "chongqingDC1",
        "3090专区": "yangzhouDC1",
        "内蒙B区": "neimengDC3"
    }
    
    # 公共基础镜像UUID
    BASE_IMAGES = {
        "PyTorch 1.9.0 (CUDA 11.1)": "base-image-12be412037",
        "PyTorch 1.10.0 (CUDA 11.3)": "base-image-u9r24vthlk",
        "PyTorch 1.11.0 (CUDA 11.3)": "base-image-l374uiucui",
        "PyTorch 2.0.0 (CUDA 11.8)": "base-image-l2t43iu6uk",
        "TensorFlow 2.5.0 (CUDA 11.2)": "base-image-0gxqmciyth",
        "TensorFlow 2.9.0 (CUDA 11.2)": "base-image-uxeklgirir",
        "TensorFlow 1.15.5 (CUDA 11.4)": "base-image-4bpg0tt88l",
        "Miniconda (CUDA 11.6)": "base-image-mbr2n4urrc",
        "Miniconda (CUDA 10.2)": "base-image-qkkhitpik5",
        "Miniconda (CUDA 11.1)": "base-image-h041hn36yt",
        "Miniconda (CUDA 11.3)": "base-image-7bn8iqhkb5",
        "Miniconda (CUDA 9.0)": "base-image-k0vep6kyq8",
        "TensorRT 8.5.1 (CUDA 11.8)": "base-image-l2843iu23k"
    }
    
    # CUDA版本映射
    CUDA_VERSIONS = {
        "11.8": 118,
        "12.0": 120,
        "12.1": 121,
        "12.2": 122
    }
    
    # GPU类型
    GPU_TYPES = [
        "RTX 4090", "RTX 4080", "RTX 3090", "RTX 3080", "RTX 3070",
        "V100", "A100", "H100", "L20", "L40"
    ]


class AutoDLElasticDeployment:
    """AutoDL弹性部署API封装类"""
    
    def __init__(self, token: str):
        """
        初始化AutoDL弹性部署客户端
        
        Args:
            token: AutoDL API token，从控制台 -> 设置 -> 开发者Token获取
        """
        self.token = token
        self.base_url = "https://api.autodl.com"
        self.headers = {
            "Authorization": token,
            "Content-Type": "application/json"
        }
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, 
                     params: Optional[Dict] = None) -> Dict:
        """
        发送HTTP请求
        
        Args:
            method: HTTP方法 (GET, POST, DELETE)
            endpoint: API端点
            data: POST请求的数据
            params: GET请求的参数
            
        Returns:
            API响应数据
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=self.headers, params=params)
            elif method.upper() == "POST":
                response = requests.post(url, headers=self.headers, json=data)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=self.headers, json=data)
            elif method.upper() == "PUT":
                response = requests.put(url, headers=self.headers, json=data)
            else:
                raise ValueError(f"不支持的HTTP方法: {method}")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"API请求失败: {e}")
    
    def get_images(self, page_index: int = 1, page_size: int = 10, 
                   offset: Optional[int] = None) -> List[Dict]:
        """
        获取私有镜像列表
        
        Args:
            page_index: 页码
            page_size: 每页条目数
            offset: 查询的起始偏移量
            
        Returns:
            镜像信息列表
        """
        data = {
            "page_index": page_index,
            "page_size": page_size
        }
        if offset is not None:
            data["offset"] = offset
            
        response = self._make_request("POST", "/api/v1/dev/image/private/list", data=data)
        
        if response.get("code") != "Success":
            raise Exception(f"获取镜像失败: {response.get('msg', '未知错误')}")
        return response.get("data", {}).get("list", [])
    
    def create_deployment(self, name: str, image_uuid: str, deployment_type: str = "ReplicaSet",
                         replica_num: int = 1, parallelism_num: Optional[int] = None,
                         gpu_name_set: Optional[List[str]] = None, gpu_num: int = 1,
                         cuda_v_from: int = 113, cuda_v_to: int = 128,
                         cpu_num_from: int = 1, cpu_num_to: int = 100,
                         memory_size_from: int = 1, memory_size_to: int = 256,
                         dc_list: Optional[List[str]] = None, cmd: str = "sleep 100",
                         price_from: int = 10, price_to: int = 9000,
                         reuse_container: bool = True, env_vars: Optional[Dict[str, str]] = None) -> str:
        """
        创建弹性部署
        
        Args:
            name: 部署名称
            image_uuid: 镜像UUID
            deployment_type: 部署类型 ("ReplicaSet", "Job", "Container")
            replica_num: 副本数量
            parallelism_num: 并行数量（Job类型需要）
            gpu_name_set: GPU类型列表，如 ["RTX 4090"]
            gpu_num: GPU数量
            cuda_v_from: CUDA版本下限
            cuda_v_to: CUDA版本上限
            cpu_num_from: CPU数量下限
            cpu_num_to: CPU数量上限
            memory_size_from: 内存大小下限(GB)
            memory_size_to: 内存大小上限(GB)
            dc_list: 数据中心列表，如 ["westDC2", "westDC3"]
            cmd: 启动命令
            price_from: 价格下限
            price_to: 价格上限
            reuse_container: 是否复用容器
            env_vars: 环境变量
            
        Returns:
            部署UUID
        """
        if dc_list is None:
            dc_list = ["westDC2", "westDC3"]
        
        if gpu_name_set is None:
            gpu_name_set = ["RTX 4090"]
        
        # 构建基础请求数据
        data = {
            "name": name,
            "deployment_type": deployment_type,
            "replica_num": replica_num,
            "reuse_container": reuse_container,
            "container_template": {
                "dc_list": dc_list,
                "gpu_name_set": gpu_name_set,
                "gpu_num": gpu_num,
                "cuda_v_from": cuda_v_from,
                "cuda_v_to": cuda_v_to,
                "cpu_num_from": cpu_num_from,
                "cpu_num_to": cpu_num_to,
                "memory_size_from": memory_size_from,
                "memory_size_to": memory_size_to,
                "cmd": cmd,
                "price_from": price_from,
                "price_to": price_to,
                "image_uuid": image_uuid,
            }
        }
        
        # 根据部署类型添加特定参数
        if deployment_type == "Job" and parallelism_num is not None:
            data["parallelism_num"] = parallelism_num
        elif deployment_type == "Container":
            # Container类型使用cuda_v而不是cuda_v_from/cuda_v_to
            data["container_template"]["cuda_v"] = cuda_v_from
            # 移除cuda_v_from和cuda_v_to
            data["container_template"].pop("cuda_v_from", None)
            data["container_template"].pop("cuda_v_to", None)
        
        # 添加环境变量
        if env_vars:
            data["container_template"]["env_vars"] = env_vars
            
        response = self._make_request("POST", "/api/v1/dev/deployment", data=data)
        
        if response.get("code") != "Success":
            raise Exception(f"创建部署失败: {response.get('msg', '未知错误')}")
        
        deployment_uuid = response.get("data", {}).get("deployment_uuid")
        if not deployment_uuid:
            raise Exception("创建部署成功但未返回部署UUID")
        
        return deployment_uuid
    
    def create_replicaset_deployment(self, name: str, image_uuid: str, replica_num: int = 2,
                                   gpu_name_set: Optional[List[str]] = None, gpu_num: int = 1,
                                   cuda_v_from: int = 113, cuda_v_to: int = 128,
                                   cpu_num_from: int = 1, cpu_num_to: int = 100,
                                   memory_size_from: int = 1, memory_size_to: int = 256,
                                   dc_list: Optional[List[str]] = None, cmd: str = "sleep 100",
                                   price_from: int = 10, price_to: int = 9000,
                                   reuse_container: bool = True, env_vars: Optional[Dict[str, str]] = None) -> str:
        """
        创建ReplicaSet类型部署
        
        Args:
            name: 部署名称
            image_uuid: 镜像UUID
            replica_num: 副本数量
            gpu_name_set: GPU类型列表
            gpu_num: GPU数量
            cuda_v_from: CUDA版本下限
            cuda_v_to: CUDA版本上限
            cpu_num_from: CPU数量下限
            cpu_num_to: CPU数量上限
            memory_size_from: 内存大小下限(GB)
            memory_size_to: 内存大小上限(GB)
            dc_list: 数据中心列表
            cmd: 启动命令
            price_from: 价格下限
            price_to: 价格上限
            reuse_container: 是否复用容器
            env_vars: 环境变量
            
        Returns:
            部署UUID
        """
        return self.create_deployment(
            name=name,
            image_uuid=image_uuid,
            deployment_type="ReplicaSet",
            replica_num=replica_num,
            gpu_name_set=gpu_name_set,
            gpu_num=gpu_num,
            cuda_v_from=cuda_v_from,
            cuda_v_to=cuda_v_to,
            cpu_num_from=cpu_num_from,
            cpu_num_to=cpu_num_to,
            memory_size_from=memory_size_from,
            memory_size_to=memory_size_to,
            dc_list=dc_list,
            cmd=cmd,
            price_from=price_from,
            price_to=price_to,
            reuse_container=reuse_container,
            env_vars=env_vars
        )
    
    def create_job_deployment(self, name: str, image_uuid: str, replica_num: int = 4,
                            parallelism_num: int = 1, gpu_name_set: Optional[List[str]] = None,
                            gpu_num: int = 1, cuda_v_from: int = 113, cuda_v_to: int = 128,
                            cpu_num_from: int = 1, cpu_num_to: int = 100,
                            memory_size_from: int = 1, memory_size_to: int = 256,
                            dc_list: Optional[List[str]] = None, cmd: str = "sleep 10",
                            price_from: int = 10, price_to: int = 9000,
                            reuse_container: bool = True, env_vars: Optional[Dict[str, str]] = None) -> str:
        """
        创建Job类型部署
        
        Args:
            name: 部署名称
            image_uuid: 镜像UUID
            replica_num: 副本数量
            parallelism_num: 并行数量
            gpu_name_set: GPU类型列表
            gpu_num: GPU数量
            cuda_v_from: CUDA版本下限
            cuda_v_to: CUDA版本上限
            cpu_num_from: CPU数量下限
            cpu_num_to: CPU数量上限
            memory_size_from: 内存大小下限(GB)
            memory_size_to: 内存大小上限(GB)
            dc_list: 数据中心列表
            cmd: 启动命令
            price_from: 价格下限
            price_to: 价格上限
            reuse_container: 是否复用容器
            env_vars: 环境变量
            
        Returns:
            部署UUID
        """
        return self.create_deployment(
            name=name,
            image_uuid=image_uuid,
            deployment_type="Job",
            replica_num=replica_num,
            parallelism_num=parallelism_num,
            gpu_name_set=gpu_name_set,
            gpu_num=gpu_num,
            cuda_v_from=cuda_v_from,
            cuda_v_to=cuda_v_to,
            cpu_num_from=cpu_num_from,
            cpu_num_to=cpu_num_to,
            memory_size_from=memory_size_from,
            memory_size_to=memory_size_to,
            dc_list=dc_list,
            cmd=cmd,
            price_from=price_from,
            price_to=price_to,
            reuse_container=reuse_container,
            env_vars=env_vars
        )
    
    def create_container_deployment(self, name: str, image_uuid: str,
                                  gpu_name_set: Optional[List[str]] = None, gpu_num: int = 1,
                                  cuda_v: int = 113, cpu_num_from: int = 1, cpu_num_to: int = 100,
                                  memory_size_from: int = 1, memory_size_to: int = 256,
                                  dc_list: Optional[List[str]] = None, cmd: str = "sleep 100",
                                  price_from: int = 10, price_to: int = 9000,
                                  reuse_container: bool = True, env_vars: Optional[Dict[str, str]] = None) -> str:
        """
        创建Container类型部署
        
        Args:
            name: 部署名称
            image_uuid: 镜像UUID
            gpu_name_set: GPU类型列表
            gpu_num: GPU数量
            cuda_v: CUDA版本
            cpu_num_from: CPU数量下限
            cpu_num_to: CPU数量上限
            memory_size_from: 内存大小下限(GB)
            memory_size_to: 内存大小上限(GB)
            dc_list: 数据中心列表
            cmd: 启动命令
            price_from: 价格下限
            price_to: 价格上限
            reuse_container: 是否复用容器
            env_vars: 环境变量
            
        Returns:
            部署UUID
        """
        return self.create_deployment(
            name=name,
            image_uuid=image_uuid,
            deployment_type="Container",
            replica_num=1,  # Container类型固定为1
            gpu_name_set=gpu_name_set,
            gpu_num=gpu_num,
            cuda_v_from=cuda_v,  # 会被转换为cuda_v
            cuda_v_to=cuda_v,
            cpu_num_from=cpu_num_from,
            cpu_num_to=cpu_num_to,
            memory_size_from=memory_size_from,
            memory_size_to=memory_size_to,
            dc_list=dc_list,
            cmd=cmd,
            price_from=price_from,
            price_to=price_to,
            reuse_container=reuse_container,
            env_vars=env_vars
        )
    
    def get_deployments(self) -> List[Dict]:
        """
        获取部署列表
        
        Returns:
            部署信息列表
        """
        response = self._make_request("GET", "/api/v1/dev/deployment/list")
        
        if response.get("code") != "Success":
            raise Exception(f"获取部署列表失败: {response.get('msg', '未知错误')}")
    
        return response.get("data", {}).get("list", [])
    
    def query_container_events(
            self, deployment_uuid: str,
            deployment_container_uuid: str = "",
            page_index: int = 0,
            page_size: int = 10,
            ) -> List[Dict]:
        """
        查询容器事件
        
        Args:
            deployment_uuid: 部署UUID
            
        Returns:
            容器事件列表
        """
        body = {
            "deployment_uuid": deployment_uuid,
            "deployment_container_uuid": deployment_container_uuid,
            "page_index": page_index,
            "page_size": page_size,
        }
        response = self._make_request("POST", "/api/v1/dev/deployment/container/event/list", data=body)
        
        if response.get("code") != "Success":
            raise Exception(f"查询容器事件失败: {response.get('msg', '未知错误')}")

        return response.get("data", {}).get("list", [])
    
    def query_containers(
            self, 
            deployment_uuid: str,
            deployment_container_uuid: str = "", 
            page_index: int = 1, 
            page_size: int = 100,
            date_from: str = "",
            date_to: str = "",
            gpu_name: str = "",
            cpu_num_from: int = 0,
            cpu_num_to: int = 0,
            memory_size_from: int = 0,
            memory_size_to: int = 0,
            price_from: int = 0,
            price_to: int = 0,
            released: bool = False,
            status: List[str] = ["running"]
        ) -> List[Dict]:
        """
        查询容器
        
        Args:
            deployment_uuid: 部署UUID
            
        Returns:
            容器信息列表
        """
        body = {
            "deployment_uuid": deployment_uuid,
            "container_uuid": deployment_container_uuid,
            "date_from": date_from,
            "date_to": date_to,
            "gpu_name": gpu_name,
            "cpu_num_from": cpu_num_from,
            "cpu_num_to": cpu_num_to,
            "memory_size_from": memory_size_from,
            "memory_size_to": memory_size_to,
            "price_from": price_from,
            "price_to": price_to,
            "released": released,
            "status": status,
            "page_index": page_index,
            "page_size": page_size
        }
        response = self._make_request("POST", "/api/v1/dev/deployment/container/list", data=body)
        
        if response.get("code") != "Success":
            raise Exception(f"查询容器失败: {response.get('msg', '未知错误')}")
        
        return response.get("data", [])
    
    def stop_container(
            self, 
            deployment_container_uuid: str,
            decrease_one_replica_num: bool = False,
            no_cache: bool = False,
            cmd_before_shutdown: str = "sleep 5",
        ) -> bool:
        """
        停止某容器
        
        Args:
            deployment_container_uuid (str): 部署的容器uuid，必填。
            decrease_one_replica_num (bool, 可选): 对于ReplicaSet类型的部署，是否同时将副本数减少1个。默认为False。
            no_cache (bool, 可选): 停止容器后是否不要放入缓存池供复用容器（如果创建部署时未选择复用容器，则该字段无实际作用）。默认为False，即如果部署设置了复用容器，则此容器停止后会被复用。
            cmd_before_shutdown (str, 可选): 在停止容器前先执行的命令。注意命令执行超时时间为5秒，超时将直接停止容器。如果创建部署时也设置了cmd_before_shutdown字段，则此接口中的值将覆盖部署中的值然后执行（极小概率会出现两者都会执行）。
            
        Returns:
            是否成功
        """
        data = {
            "deployment_container_uuid": deployment_container_uuid,
            "decrease_one_replica_num": decrease_one_replica_num,
            "no_cache": no_cache,
            "cmd_before_shutdown": cmd_before_shutdown
        }
        response = self._make_request("POST", "/api/v1/dev/deployment/container/stop", data=data)
        
        if response.get("code") != "Success":
            raise Exception(f"停止容器失败: {response.get('msg', '未知错误')}")
        
        return True
    
    def set_replicas(self, deployment_uuid: str, replicas: int) -> bool:
        """
        设置副本数量
        
        Args:
            deployment_uuid: 部署UUID
            replicas: 副本数量
            
        Returns:
            是否成功
        """
        body = {
            "deployment_uuid": deployment_uuid,
            "replica_num": replicas
        }
        response = self._make_request("PUT", "/api/v1/dev/deployment/replica_num", data=body)
        
        if response.get("code") != "Success":
            raise Exception(f"设置副本数量失败: {response.get('msg', '未知错误')}")
        
        return True
    
    def stop_deployment(self, deployment_uuid: str) -> bool:
        """
        停止部署
        
        Args:
            deployment_uuid: 部署UUID
            
        Returns:
            是否成功
        """
        data = {
            "deployment_uuid": deployment_uuid, 
            "operate": "stop"
        }
        response = self._make_request("PUT", "/api/v1/dev/deployment/operate", data=data)
        
        if response.get("code") != "Success":
            raise Exception(f"停止部署失败: {response.get('msg', '未知错误')}")
        
        return True
    
    def delete_deployment(self, deployment_uuid: str) -> bool:
        """
        删除部署
        
        Args:
            deployment_uuid: 部署UUID
            
        Returns:
            是否成功
        """
        body = {
            "deployment_uuid": deployment_uuid,
        }
        response = self._make_request("DELETE", "/api/v1/dev/deployment", data=body)
        
        if response.get("code") != "Success":
            raise Exception(f"删除部署失败: {response.get('msg', '未知错误')}")
        
        return True
    
    def set_scheduling_blacklist(
            self, 
            deployment_uuid: str, 
            expire_in_minutes: int, 
            comment: str,
        ) -> bool:
        """
        设置调度黑名单
        
        Args:
            deployment_uuid: 部署UUID
            blacklist: 黑名单列表
            
        Returns:
            是否成功
        """
        body = {
            "deployment_uuid": deployment_uuid,
            "expire_in_minutes": expire_in_minutes,
            "comment": comment
        }
        response = self._make_request("POST", "/api/v1/dev/deployment/scheduling/blacklist", data=body)
        
        if response.get("code") != "Success":
            raise Exception(f"设置调度黑名单失败: {response.get('msg', '未知错误')}")
        
        return True
    
    def get_scheduling_blacklist(self, deployment_uuid: str) -> List[str]:
        """
        获取生效中的调度黑名单
        
        Args:
            deployment_uuid: 部署UUID
            
        Returns:
            黑名单列表
        """
        params = {}
        response = self._make_request("GET", "/api/v1/dev/deployment/scheduling/blacklist", params=params)
        
        if response.get("code") != "Success":
            raise Exception(f"获取调度黑名单失败: {response.get('msg', '未知错误')}")
        
        return response.get("data", [])
    
    def get_gpu_stock(
            self, 
            region_sign: str, 
            cuda_v_from: int = 117,
            cuda_v_to: int = 128, 
        ) -> List[Dict]:
        """
        获取弹性部署GPU库存
        
        Args:
            region_sign: 地区标识
            cuda_v: CUDA版本
            gpu_types: 指定GPU型号列表，为None时返回所有型号
            
        Returns:
            GPU库存信息列表
        """
        body = {
            "region_sign": region_sign,
            "cuda_v_to": cuda_v_to,
            "cuda_v_from": cuda_v_from,
        }
        response = self._make_request("POST", "/api/v1/dev/machine/region/gpu_stock", data=body)
        
        if response.get("code") != "Success":
            raise Exception(f"获取GPU库存失败: {response.get('msg', '未知错误')}")
        data = response.get("data", [])
        flat_list = []
        for item in data:
            if isinstance(item, dict):
                for gpu_type, info in item.items():
                    info_flat = info.copy()
                    info_flat = {"gpu_type": gpu_type, **info_flat}
                    flat_list.append(info_flat)
        return flat_list
    
    def get_ddp_overview(self, deployment_uuid: str) -> List[Dict]:
        """
        获取已购时长包数据
        
        Args:
            deployment_uuid: 部署UUID
            
        Returns:
            时长包信息列表
        """
        params = {"deployment_uuid": deployment_uuid}
        response = self._make_request("GET", "/api/v1/dev/deployment/ddp/overview", params=params)
        
        if response.get("code") != "Success":
            raise Exception(f"获取时长包数据失败: {response.get('msg', '未知错误')}")
        return response.get("data", [])


 