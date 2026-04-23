# AI-Travel-Copilot

一个基于多 Agent 的旅行规划系统，支持从用户输入生成完整行程，并支持简单的多轮修改与重规划。

## 1. 项目说明

该项目实现了一个基础的旅行规划流程，主要能力包括：

* 根据用户需求生成旅行行程；

* 支持口语化输入（如“轻松一点”“多吃点美食”）；

* 支持简单的多轮修改（如天气变化、局部调整）；

* 支持 mock / real 工具切换。

***

## 2. 快速启动

### 2.1 安装依赖

```
pip install -r requirements.txt
```

### 2.2 启动服务

```
uvicorn main:app --reload
```

默认地址：

```
http://127.0.0.1:8000
```

***

## 3. 常用接口

### 3.1 生成行程（结构化输入）

```
curl -X POST http://127.0.0.1:8000/plan/generate \
-H "Content-Type: application/json" \
-d '{
  "origin": "上海",
  "destination": "杭州",
  "days": 2,
  "budget": 3000,
  "preferences": ["美食", "夜景"]
}'
```

### 3.2 口语输入生成

```
curl -X POST http://127.0.0.1:8000/plan/chat \
-H "Content-Type: application/json" \
-d '{
  "user_input": "想去杭州玩两天，别太赶，多吃点好吃的"
}'
```

***

## 4. 基本流程

系统整体流程可以表示为：

```
用户输入
→ 解析需求
→ 检索候选
→ 简单排序
→ 生成行程
```

如果是修改请求：

```
已有行程
→ 定位受影响部分
→ 局部更新
→ 返回新行程
```

***

## 5. 项目结构

&#x20;

```
api/         接口
agents/      核心逻辑
services/    流程编排
tools/       工具调用
memory/      简单会话数据
schemas/     数据结构
```

