#!/usr/bin/env python3
"""
测试新的创建部署功能
"""

from autodl import AutoDLElasticDeployment, AutoDLConstants

def test_create_deployment():
    """测试创建部署功能"""
    
    # 从文件读取token
    try:
        with open(".autodl_token", "r") as f:
            token = f.read().strip()
    except FileNotFoundError:
        print("请创建.autodl_token文件并填入您的API token")
        return
    
    # 创建客户端
    client = AutoDLElasticDeployment(token)
    
    print("=== 测试创建部署功能 ===\n")
    
    # 获取可用的镜像
    try:
        images = client.get_images(page_index=1, page_size=5)
        if images:
            test_image_uuid = images[0].image_uuid
            print(f"使用镜像: {images[0].image_name} (UUID: {test_image_uuid})")
        else:
            # 使用公共基础镜像
            test_image_uuid = AutoDLConstants.BASE_IMAGES['PyTorch 2.0.0 (CUDA 11.8)']
            print(f"使用公共镜像: PyTorch 2.0.0 (CUDA 11.8) (UUID: {test_image_uuid})")
    except Exception as e:
        print(f"获取镜像失败: {e}")
        return
    
    print("\n1. 测试创建ReplicaSet部署:")
    try:
        deployment_uuid = client.create_replicaset_deployment(
            name="API测试ReplicaSet",
            image_uuid=test_image_uuid,
            replica_num=1,  # 只创建1个副本进行测试
            gpu_name_set=["RTX 4090"],
            gpu_num=1,
            cmd="sleep 60",  # 简单的测试命令
            price_from=10,
            price_to=9000
        )
        print(f"✅ ReplicaSet部署创建成功，UUID: {deployment_uuid}")
        
        # 等待一下，然后获取部署列表
        import time
        time.sleep(5)
        
        deployments = client.get_deployments()
        print(f"当前部署数量: {len(deployments)}")
        for dep in deployments:
            print(f"  - {dep.name} (UUID: {dep.deployment_uuid}) - 状态: {dep.status}")
        
        return deployment_uuid
        
    except Exception as e:
        print(f"❌ 创建ReplicaSet部署失败: {e}")
    
    print("\n2. 测试创建Job部署:")
    try:
        deployment_uuid = client.create_job_deployment(
            name="API测试Job",
            image_uuid=test_image_uuid,
            replica_num=1,
            parallelism_num=1,
            gpu_name_set=["RTX 4090"],
            gpu_num=1,
            cmd="sleep 30",  # 简单的测试命令
            price_from=10,
            price_to=9000
        )
        print(f"✅ Job部署创建成功，UUID: {deployment_uuid}")
        return deployment_uuid
        
    except Exception as e:
        print(f"❌ 创建Job部署失败: {e}")
    
    print("\n3. 测试创建Container部署:")
    try:
        deployment_uuid = client.create_container_deployment(
            name="API测试Container",
            image_uuid=test_image_uuid,
            gpu_name_set=["RTX 4090"],
            gpu_num=1,
            cuda_v=113,
            cmd="sleep 60",  # 简单的测试命令
            price_from=10,
            price_to=9000
        )
        print(f"✅ Container部署创建成功，UUID: {deployment_uuid}")
        return deployment_uuid
        
    except Exception as e:
        print(f"❌ 创建Container部署失败: {e}")
    
    return None

def cleanup_deployment(client, deployment_uuid):
    """清理部署"""
    if not deployment_uuid:
        return
    
    print(f"\n清理部署 {deployment_uuid}:")
    
    try:
        # 停止部署
        print("停止部署...")
        client.stop_deployment(deployment_uuid)
        
        # 等待一下
        import time
        time.sleep(5)
        
        # 删除部署
        print("删除部署...")
        client.delete_deployment(deployment_uuid)
        print("✅ 部署清理完成")
        
    except Exception as e:
        print(f"清理部署时出错: {e}")

def main():
    """主函数"""
    deployment_uuid = test_create_deployment()
    
    if deployment_uuid:
        print(f"\n🎉 部署创建测试成功！")
        print(f"部署UUID: {deployment_uuid}")
        
        # 询问是否清理部署
        response = input("\n是否清理测试部署？(y/n): ").strip().lower()
        if response in ['y', 'yes', '是']:
            try:
                with open(".autodl_token", "r") as f:
                    token = f.read().strip()
                client = AutoDLElasticDeployment(token)
                cleanup_deployment(client, deployment_uuid)
            except Exception as e:
                print(f"清理失败: {e}")
        else:
            print("请手动清理部署以避免产生额外费用")
    else:
        print("\n❌ 部署创建测试失败")

if __name__ == "__main__":
    main() 