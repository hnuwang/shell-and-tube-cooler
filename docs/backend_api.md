# FastAPI 后端接口说明

## 启动方式

安装依赖后，在项目根目录执行：

```bash
uvicorn backend.app:app --reload
```

默认本地地址通常为：

`http://127.0.0.1:8000`

交互式文档为：

- `http://127.0.0.1:8000/docs`
- `http://127.0.0.1:8000/redoc`

## 接口清单

### 1. 健康检查

- 方法：`GET`
- 路径：`/api/health`
- 用途：前端启动时检查后端是否在线

### 2. 获取默认配置

- 方法：`GET`
- 路径：`/api/design/default-config`
- 用途：前端表单初始化

### 3. 运行设计计算

- 方法：`POST`
- 路径：`/api/design/run`
- 请求体：JSON，字段与 `DesignConfig` 对应
- 返回：完整 `design` 结果对象

### 4. 导入 JSON 参数文件

- 方法：`POST`
- 路径：`/api/design/import/json`
- 类型：`multipart/form-data`
- 字段：`file`
- 返回：解析后的配置对象

### 5. 导入 Excel 参数表

- 方法：`POST`
- 路径：`/api/design/import/excel`
- 类型：`multipart/form-data`
- 字段：`file`
- 返回：解析后的配置对象

### 6. 导出 Excel 结果表

- 方法：`POST`
- 路径：`/api/design/export/excel`
- 请求体：JSON，字段与 `DesignConfig` 对应
- 返回：`.xlsx` 文件流

### 7. 导出 Word 结果表

- 方法：`POST`
- 路径：`/api/design/export/word`
- 请求体：JSON，字段与 `DesignConfig` 对应
- 返回：`.docx` 文件流

## 前端调用建议

前端建议统一通过 `fetch` 或 `axios` 调用这些接口：

1. 页面初始化时先请求 `/api/design/default-config`
2. 用户修改参数后调用 `/api/design/run`
3. 上传参数文件时调用 `/api/design/import/json` 或 `/api/design/import/excel`
4. 点击导出按钮时调用 `/api/design/export/excel` 或 `/api/design/export/word`

## 说明

- 后端目前属于第一阶段 API 化版本，重点是把现有 Python 计算核心稳定封装成 HTTP 服务。
- 现有命令行程序和 Tkinter 桌面版不受影响，可与后端并行保留。
