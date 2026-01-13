# 尝尝咸淡 RAG (Cook RAG)

## 项目简介
这是一个基于 RAG (Retrieval-Augmented Generation) 的智能食谱问答系统。

## 环境准备

1. 确保已安装 Conda。
2. 激活环境 (如果已配置 VSCode settings.json，VSCode 会自动识别):
   ```bash
   conda activate cook-rag-1
   ```
3. 安装依赖:
   ```bash
   pip install fastapi uvicorn python-dotenv requests streamlit
   # 以及其他 rag_module 需要的依赖
   ```

## 运行项目

### 1. 启动后端服务
后端服务基于 FastAPI，提供 RAG 问答接口。

```bash
python server.py
```
服务默认运行在: http://127.0.0.1:9000

### 2. 启动前端界面
前端界面基于 Streamlit，提供聊天交互。

```bash
streamlit run web/app.py
```
启动后会自动在浏览器打开: http://localhost:8501

## 项目结构
- `app/routers/`: 路由定义 (rag_router.py)
- `data/`: 食谱数据
- `rag_module/`: RAG 核心逻辑
- `web/`: 前端界面代码
- `server.py`: 后端启动入口
