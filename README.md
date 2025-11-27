# LightAIModelEval - 轻量级AI模型评测平台

基于OpenCompass进行二次开发，专注于通过API形式进行大模型评测，支持云侧和边侧模型的协同评测与对比分析。

## 🏗️ 技术架构

本系统采用五层分层架构设计：

1. **前端表现层**：基于Vue 3、Element Plus和ECharts构建的现代化Web界面
2. **后端服务层**：使用FastAPI构建的RESTful API服务
3. **API适配层**：统一的API调用接口，支持多种模型服务接入
4. **评测引擎层**：基于OpenCompass的评测引擎
5. **数据持久层**：使用MySQL和MinIO进行数据存储

## 🚀 快速开始

### 环境准备

1. 安装Python 3.8+
2. 安装Node.js 16+
3. 安装依赖：
   ```bash
   # 安装后端依赖
   pip install -r requirements.txt
   
   # 安装前端依赖
   cd eval-ui && npm install && cd ..
   ```

### 启动服务

#### 方法一：分别启动（推荐开发环境）

1. 启动后端服务：
   ```bash
   cd backend
   python main.py
   ```

2. 启动前端服务：
   ```bash
   cd eval-ui
   npm run dev
   ```

#### 方法二：一键启动（推荐测试环境）

```bash
python start_all.py
```

### 访问系统

- 前端界面：http://localhost:5173
- 后端API：http://localhost:8000
- API文档：http://localhost:8000/docs

## 📁 项目结构

```
LightAIModelEval/
├── backend/                 # 后端服务
│   ├── main.py             # 主应用入口
│   ├── database.py         # 数据库模型和访问层
│   ├── storage.py          # 对象存储集成
│   └── requirements.txt    # 后端依赖
├── eval-ui/                # 前端界面
│   ├── src/                # Vue源码
│   ├── package.json        # 前端依赖
│   └── vite.config.ts      # 构建配置
├── opencompass/            # 评测引擎
│   ├── models/             # 模型适配器
│   ├── configs/            # 配置文件
│   ├── evaluator/          # 评测器
│   └── requirements/       # 依赖配置
├── services/               # 业务服务
├── docs/                   # 文档
├── tests/                  # 测试代码
├── requirements.txt        # 项目依赖
├── start_all.py            # 一键启动脚本
└── integration_test.py     # 集成测试
```

## 🛠️ 核心功能

### 1. API配置管理
- 支持云侧API（如OpenAI）和边侧API配置
- 安全的密钥管理（AES加密存储）
- 多种协议适配（OpenAI、RESTful、JSON-RPC等）

### 2. 评测任务管理
- 创建和管理评测任务
- 支持多种数据集（GSM8K、MMLU等）
- 多维度指标评测（准确率、时延、吞吐量等）

### 3. 结果分析与可视化
- 云侧与边侧模型结果对比
- 多维度指标可视化展示
- 评测报告查看

## 🔧 开发指南

### 添加新的API适配器

在 `opencompass/models/unified_api.py` 中继承 `BaseAPIAdapter` 类并实现相应方法。

### 添加新的评测数据集

参考 `opencompass/datasets/` 目录中的实现方式。

### 扩展评测指标

在 `opencompass/evaluator/unified_evaluator.py` 中添加新的指标计算方法。

## 📊 API文档

系统提供完整的Swagger API文档，访问 http://localhost:8000/docs 查看详细接口说明。

## 🧪 测试

运行集成测试：
```bash
python integration_test.py
```


## 🤝 贡献

欢迎提交Issue和Pull Request来改进本项目。

## 📄 许可证

本项目基于MIT许可证开源。