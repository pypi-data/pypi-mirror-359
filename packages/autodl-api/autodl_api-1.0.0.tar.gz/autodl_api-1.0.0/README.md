# AutoDL API封装包

[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

这是一个完整的AutoDL API封装包，支持所有弹性部署相关功能。

## 📦 安装

### PyPI安装

```bash
pip install autodl-api
```

### 从源码安装

```bash
git clone https://github.com/Rookie-Package/autodl.git
cd autodl
pip install -e .
```

### 依赖安装

```bash
pip install requests
```

## 🚀 快速开始

```python
from autodl import AutoDLElasticDeployment

# 创建客户端
client = AutoDLElasticDeployment("your_api_token")

# 获取镜像列表
images = client.get_images()

# 获取部署列表
deployments = client.get_deployments()

# 获取GPU库存
stock = client.get_gpu_stock("westDC2", 118)
```

## 📚 文档

- [使用示例](examples/autodl_example.ipynb)
- [官网API文档](https://www.autodl.com/docs/esd_api_doc/)
- [弹性部署](https://www.autodl.com/docs/elastic_deploy/)
- [弹性部署最佳实践](https://www.autodl.com/docs/elastic_deploy_practice/)
## 🧪 测试

```bash
# 运行基本测试
python tests/test_autodl.py

# 运行单元测试
python -m pytest tests/test_autodl.py -v

```

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📞 支持

如有问题，请查看[文档](docs/)或提交Issue。

## 🆕 最新更新

### v1.0.0
- ✅ 完整的AutoDL弹性部署API支持
- ✅ 支持ReplicaSet、Job、Container三种部署类型
- ✅ 容器管理和监控功能
- ✅ GPU库存查询和时长包管理
- ✅ 完整的错误处理和类型提示
- ✅ 详细的文档和示例 