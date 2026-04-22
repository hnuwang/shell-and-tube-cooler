# 固定管板式管壳式煤油冷却器设计程序

本项目是一个面向课程设计的 Python 3.11+ 命令行程序，用于完成固定管板式管壳式煤油冷却器的传热计算、结构计算和阻力计算。程序采用统一 SI 单位、`dataclass` 数据模型和可追踪中间量输出，便于复核与撰写设计说明书。

## 项目简介

- 热侧介质：煤油，壳程流动
- 冷侧介质：冷却水，管内流动
- 设计任务：完成热负荷、LMTD/F 修正、面积初选、几何筛选、总传热系数校核与压降校核
- 深度定位：课程设计版，优先使用教材中常见、便于解释的简化关联式

## 运行方式

```bash
python main.py
```

若本机 `python` 命令不可用，可改用显式 Python 路径运行。

图形界面版本可通过以下命令启动：

```bash
python ui_app.py
```

界面支持导入 JSON 参数文件、回填表单、执行计算并导出结果摘要。

## Web 后端（第一阶段）

项目已新增 `FastAPI` 后端骨架，计算核心仍然复用现有 `run_design(config)`。

安装依赖后，可通过以下命令启动：

```bash
uvicorn backend.app:app --reload
```

启动后可访问：

- `GET /api/health`
- `GET /api/design/default-config`
- `POST /api/design/run`
- `POST /api/design/import/json`
- `POST /api/design/import/excel`
- `POST /api/design/export/excel`
- `POST /api/design/export/word`

接口详细说明见 [docs/backend_api.md](/C:/Users/wh/Desktop/分类文档/换热器程序设计/shell_and_tube_cooler/docs/backend_api.md)。

## 目录说明

```text
shell_and_tube_cooler/
├─ README.md
├─ requirements.txt
├─ main.py
├─ config.py
├─ report_data.py
├─ data/
├─ src/
├─ tests/
└─ docs/
```

## 假设说明

- 统一采用 SI 单位，输入温度接口使用 ℃，物性表存储温度为 K
- 管内走水、壳程走煤油
- 默认采用 1 壳程、2 管程
- 使用两阶段总传热系数策略：`U_assumed` 用于面积初选，`U_calculated` 用于热阻校核
- 壳程几何量统一由 `src/geometry.py` 定义，其他模块不得重复定义壳程当量直径或横流面积
- 若方案不满足面积、速度或压降约束，程序自动迭代候选；全部失败时抛出工程化异常

## 样例输出说明

默认配置下，程序会输出四组表格：

- `input`：题目工况输入
- `properties`：冷热侧代表物性
- `thermal`：热工计算结果
- `mechanical`：结构与几何候选结果
- `hydraulic`：流速、Re 和压降校核结果

若使用图形界面，左侧为参数文件导入与工程假设输入区，右侧按“传热计算、结构计算、阻力计算、综合结论、计算日志”分栏展示结果。
