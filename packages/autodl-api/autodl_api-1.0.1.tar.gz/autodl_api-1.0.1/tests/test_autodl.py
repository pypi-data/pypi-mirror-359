"""
AutoDL弹性部署API测试
测试各种API功能是否正常工作
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from autodl import AutoDLElasticDeployment, AutoDLConstants
    IMPORT_SUCCESS = True
except ImportError as e:
    print(f"❌ 模块导入失败: {e}")
    IMPORT_SUCCESS = False


class TestAutoDLConstants(unittest.TestCase):
    """测试AutoDL常量定义"""
    
    def test_regions(self):
        """测试地区标识常量"""
        self.assertIn("西北企业区(推荐)", AutoDLConstants.REGIONS)
        self.assertEqual(AutoDLConstants.REGIONS["西北企业区(推荐)"], "westDC2")
    
    def test_base_images(self):
        """测试基础镜像常量"""
        self.assertIn("PyTorch 2.0.0 (CUDA 11.8)", AutoDLConstants.BASE_IMAGES)
        self.assertIsInstance(AutoDLConstants.BASE_IMAGES["PyTorch 2.0.0 (CUDA 11.8)"], str)
    
    def test_cuda_versions(self):
        """测试CUDA版本映射"""
        self.assertEqual(AutoDLConstants.CUDA_VERSIONS["11.8"], 118)
        self.assertEqual(AutoDLConstants.CUDA_VERSIONS["12.0"], 120)


class TestAutoDLElasticDeployment(unittest.TestCase):
    """测试AutoDL弹性部署API类"""
    
    def setUp(self):
        """设置测试环境"""
        self.token = "test_token"
        self.client = AutoDLElasticDeployment(self.token)
    
    def test_init(self):
        """测试客户端初始化"""
        self.assertEqual(self.client.token, self.token)
        self.assertEqual(self.client.base_url, "https://api.autodl.com")
        self.assertIn("Authorization", self.client.headers)
        self.assertIn("Content-Type", self.client.headers)
    
    @patch('requests.post')
    def test_get_images(self, mock_post):
        """测试获取镜像列表"""
        # 模拟API响应
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "code": "Success",
            "data": {
                "list": [
                    {
                        "id": 1,
                        "image_name": "test_image",
                        "image_uuid": "image-123",
                        "created_at": "2023-01-01T00:00:00Z",
                        "updated_at": "2023-01-01T00:00:00Z",
                        "status": "active"
                    }
                ]
            }
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        # 执行测试
        images = self.client.get_images()
        
        # 验证结果
        self.assertEqual(len(images), 1)
        self.assertEqual(images[0]['image_name'], "test_image")
        self.assertEqual(images[0]['image_uuid'], "image-123")
    
    @patch('requests.get')
    def test_get_deployments(self, mock_get):
        """测试获取部署列表"""
        # 模拟API响应
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "code": "Success",
            "data": {
                "list": [
                    {
                        "uuid": "deployment-123",
                        "name": "test_deployment",
                        "status": "running",
                        "created_at": "2023-01-01T00:00:00Z"
                    }
                ]
            }
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # 执行测试
        deployments = self.client.get_deployments()
        
        # 验证结果
        self.assertEqual(len(deployments), 1)
        self.assertEqual(deployments[0]['uuid'], "deployment-123")
        self.assertEqual(deployments[0]['name'], "test_deployment")
    
    @patch('requests.post')
    def test_get_gpu_stock(self, mock_post):
        """测试获取GPU库存"""
        # 模拟API响应
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "code": "Success",
            "data": [
                {
                    "RTX 4090": {
                        "total_gpu_num": 100,
                        "idle_gpu_num": 50,
                        "chip_corp": "nvidia",
                        "cpu_arch": "x86"
                    }
                }
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        # 执行测试
        stock = self.client.get_gpu_stock("westDC2", 118)
        
        # 验证结果
        self.assertEqual(len(stock), 1)
        self.assertEqual(stock[0]['gpu_type'], "RTX 4090")
        self.assertEqual(stock[0]['total_gpu_num'], 100)
        self.assertEqual(stock[0]['idle_gpu_num'], 50)
    
    @patch('requests.post')
    def test_create_replicaset_deployment(self, mock_post):
        """测试创建ReplicaSet部署"""
        # 模拟API响应
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "code": "Success",
            "data": {
                "deployment_uuid": "deployment-123"
            }
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        # 执行测试
        deployment_uuid = self.client.create_replicaset_deployment(
            name="test_deployment",
            image_uuid="image-123",
            replica_num=2,
            gpu_name_set=["RTX 4090"],
            gpu_num=1
        )
        
        # 验证结果
        self.assertEqual(deployment_uuid, "deployment-123")
    
    @patch('requests.put')
    def test_stop_deployment(self, mock_put):
        """测试停止部署"""
        # 模拟API响应
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "code": "Success"
        }
        mock_response.raise_for_status.return_value = None
        mock_put.return_value = mock_response
        
        # 执行测试
        result = self.client.stop_deployment("deployment-123")
        
        # 验证结果
        self.assertTrue(result)
    
    @patch('requests.delete')
    def test_delete_deployment(self, mock_delete):
        """测试删除部署"""
        # 模拟API响应
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "code": "Success"
        }
        mock_response.raise_for_status.return_value = None
        mock_delete.return_value = mock_response
        
        # 执行测试
        result = self.client.delete_deployment("deployment-123")
        
        # 验证结果
        self.assertTrue(result)
    
    @patch('requests.put')
    def test_set_replicas(self, mock_put):
        """测试设置副本数量"""
        # 模拟API响应
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "code": "Success"
        }
        mock_response.raise_for_status.return_value = None
        mock_put.return_value = mock_response
        
        # 执行测试
        result = self.client.set_replicas("deployment-123", 3)
        
        # 验证结果
        self.assertTrue(result)
    
    @patch('requests.post')
    def test_query_container_events(self, mock_post):
        """测试查询容器事件"""
        # 模拟API响应
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "code": "Success",
            "data": {
                "list": [
                    {
                        "deployment_container_uuid": "container-123",
                        "status": "starting",
                        "created_at": "2023-01-01T00:00:00Z"
                    }
                ]
            }
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        # 执行测试
        events = self.client.query_container_events("deployment-123")
        
        # 验证结果
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]['deployment_container_uuid'], "container-123")
    
    @patch('requests.post')
    def test_query_containers(self, mock_post):
        """测试查询容器"""
        # 模拟API响应
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "code": "Success",
            "data": [
                {
                    "container_uuid": "container-123",
                    "deployment_uuid": "deployment-123",
                    "status": "running",
                    "ip": "192.168.1.1",
                    "port": 8888,
                    "created_at": "2023-01-01T00:00:00Z"
                }
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        # 执行测试
        containers = self.client.query_containers("deployment-123")
        
        # 验证结果
        self.assertEqual(len(containers), 1)
        self.assertEqual(containers[0]['container_uuid'], "container-123")
        self.assertEqual(containers[0]['status'], "running")


def run_basic_tests():
    """运行基本功能测试"""
    print("=== AutoDL弹性部署API类测试 ===\n")
    
    # 测试模块导入
    print("测试: 模块导入")
    if IMPORT_SUCCESS:
        print("✅ 模块导入成功")
    else:
        print("❌ 模块导入失败")
        return
    
    # 测试常量定义
    print("\n测试: 常量定义")
    try:
        regions = AutoDLConstants.REGIONS
        base_images = AutoDLConstants.BASE_IMAGES
        cuda_versions = AutoDLConstants.CUDA_VERSIONS
        print("✅ 常量定义正常")
    except Exception as e:
        print(f"❌ 常量测试失败: {e}")
        return
    
    # 测试客户端创建
    print("\n测试: 客户端创建")
    try:
        client = AutoDLElasticDeployment("test_token")
        print("✅ 客户端创建成功")
    except Exception as e:
        print(f"❌ 客户端创建失败: {e}")
        return
    
    # 测试Token文件
    print("\n测试: Token文件")
    if os.path.exists(".autodl_token"):
        print("✅ 找到.autodl_token文件")
    else:
        print("⚠️  未找到.autodl_token文件")
    
    print("\n测试结果: 基本功能正常")
    print("✅ 所有基础测试通过")


if __name__ == "__main__":
    # 运行基本测试
    run_basic_tests()
    
    # 如果要运行完整的单元测试，取消注释以下代码
    # unittest.main(verbosity=2) 