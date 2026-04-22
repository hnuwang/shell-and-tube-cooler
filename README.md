# 固定管板式管壳式煤油冷却器设计系统

这是一个面向课程设计的换热器辅助设计项目，使用 Python 完成固定管板式管壳式煤油冷却器的传热计算、结构计算和阻力计算，并提供桌面 GUI、FastAPI 后端和 React 前端仪表盘。

项目特点：
- 统一使用 SI 单位
- 核心计算过程可追踪、可测试
- 使用 `dataclass` 组织主要数据模型
- 物性数据通过 CSV 表和线性插值得到
- 同时提供命令行、桌面界面和 Web 展示界面

## 功能概览
- 传热计算：热负荷、冷却水流量、LMTD、修正系数、总传热系数、面积校核
- 结构计算：管长候选筛选、管数分配、壳径和挡板间距估算
- 阻力计算：管程 / 壳程流速、Re、压降与约束校核
- 结果整理：Markdown / Excel / Word 导出、课程设计说明书素材
- 前端展示：工程计算仪表盘风格结果页

## 项目结构

```text
shell_and_tube_cooler/
├─ backend/                  FastAPI 后端
├─ data/                     物性表和默认配置
├─ docs/                     课程设计说明书素材
├─ frontend/                 React + Vite 前端
├─ scripts/                  启动与导出脚本
├─ src/                      Python 核心计算模块
├─ tests/                    单元测试
├─ config.py                 配置与工程假设
├─ main.py                   命令行入口
├─ report_data.py            报表数据构建
└─ ui_app.py                 桌面 GUI 入口
```

## 环境要求
- Python 3.11+
- Node.js 18+
- npm

## 快速开始

### 1. 命令行运行

```bash
python main.py
```

### 2. 桌面 GUI

```bash
python ui_app.py
```

### 3. 后端服务

项目后端默认运行在 `8010` 端口：

```bash
python -m uvicorn backend.app:app --host 127.0.0.1 --port 8010
```

接口文档：
- `http://127.0.0.1:8010/docs`

### 4. 前端界面

前端目录：

```bash
cd frontend
npm install
npm run dev
```

默认开发地址：
- `http://127.0.0.1:5173`

前端通过 `/api` 代理到本地后端；默认代理目标为 `http://127.0.0.1:8010`。

## 测试

Python 测试：

```bash
python -m unittest discover -s tests -v
```

前端构建校验：

```bash
cd frontend
npm run build
```

## 设计假设
- 管内走水，壳程走煤油
- 默认采用 1 壳程、2 管程
- 物性参数由 `data/kerosene.csv` 和 `data/water.csv` 插值得到
- 总传热系数采用“两阶段策略”：
  - `U_assumed` 用于初选面积
  - `U_calculated` 用于热阻校核
- 壳程几何中间量统一由 `src/geometry.py` 提供

## 主要文档
- `docs/report_outline.md`：说明书目录建议
- `docs/report_tables.md`：结果表模板
- `docs/design_notes.md`：设计说明素材
- `docs/thermal_notes.md`：传热公式与说明
- `docs/hydraulic_notes.md`：阻力计算说明
- `docs/backend_api.md`：后端接口说明
- `docs/frontend_architecture.md`：前端结构说明

## 当前版本
- `v1.0`：完成课程设计版核心计算、测试、桌面 GUI、FastAPI 后端和 React 前端仪表盘
