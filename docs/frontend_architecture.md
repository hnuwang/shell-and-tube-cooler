# 前端页面架构设计

## 页面定位

该前端页面定位为“工程计算仪表盘 + 答辩展示页”的混合风格系统。页面在桌面端优先突出：

- 方案结论
- 核心 KPI 结果
- 参数录入与文件导入导出
- 适合老师快速查看的答辩摘要

## 页面结构

### 1. 顶部 Header

- 主标题：固定管板式管壳式煤油冷却器
- 副标题：课程设计计算与答辩展示系统
- 当前模式
- 接口连接状态
- 最近计算时间
- 数据来源

### 2. 状态横幅

根据设计结果的 `design_status` 展示三种状态：

- `success`
- `warning`
- `error`

### 3. 主体双栏布局

#### 左栏

- 文件与接口卡片
- 输入参数分组 Accordion
- 结果导出卡片
- 底部固定操作栏

#### 右栏

- KPI 卡片区
- 流程步骤条
- 双列结果卡片
- Tabs 详细区

## 推荐目录结构

```text
frontend/
├─ src/
│  ├─ components/
│  │  ├─ PageHeader.tsx
│  │  ├─ StatusBanner.tsx
│  │  ├─ FileActionsCard.tsx
│  │  ├─ ApiHealthCard.tsx
│  │  ├─ InputSections.tsx
│  │  ├─ ExportActionsCard.tsx
│  │  ├─ StickyActionBar.tsx
│  │  ├─ KpiCards.tsx
│  │  ├─ ProcessStepper.tsx
│  │  ├─ ScenarioCard.tsx
│  │  ├─ StructureCard.tsx
│  │  ├─ HydraulicCard.tsx
│  │  ├─ ValidationCard.tsx
│  │  ├─ DefenseSummaryCard.tsx
│  │  └─ DetailTabs.tsx
│  ├─ hooks/
│  │  ├─ useDesignCalculation.ts
│  │  └─ useExportActions.ts
│  ├─ mappers/
│  │  └─ designMappers.ts
│  ├─ services/
│  │  └─ designApi.ts
│  ├─ types/
│  │  └─ design.ts
│  ├─ mock/
│  │  └─ mockDesignData.ts
│  └─ pages/
│     └─ CoolerDesignDashboardPage.tsx
```

## 数据流

1. 页面加载时调用 `GET /api/health`
2. 然后请求默认参数或使用 fallback mock 参数
3. 用户修改参数后点击“开始计算”
4. 调用 `POST /api/design/calculate`
5. 后端 DTO 先经过 mapper 转成 ViewModel
6. 右侧结果仪表盘统一消费 ViewModel

## 技术约定

- 组件不直接使用后端原始 DTO
- 所有格式化逻辑集中在 `mappers/`
- 所有接口请求集中在 `services/`
- 所有状态管理放到 `hooks/`
- 页面组件只负责布局与交互编排
