# perfetto_extras

[![PyPI version](https://img.shields.io/pypi/v/perfetto_extras.svg)](https://pypi.org/project/perfetto_extras/)  

基于 Perfetto 的 Python 工具包，提供 trace 事件生成与浏览器可视化能力。

## 特性

- **trace_events**：便捷生成符合 Perfetto 规范的 trace 事件，可自定义进程、线程、事件类型等。
- **批量事件接口**：支持批量添加 counter、instant、complete 等多种 trace 事件，适合大规模数据写入。
- **opentrace**：一键在浏览器中打开本地 trace 文件，自动本地 HTTP 服务并跳转至 [ui.perfetto.dev](https://ui.perfetto.dev)。
- **命令行工具**：安装后可直接使用 `opentrace` 命令，无需再写 python 脚本。

## 当前版本

**0.3.0**

## 安装

```bash
pip install perfetto_extras
```

或使用 poetry：

```bash
poetry add perfetto_extras
```

## 快速开始

### 1. 生成 Trace 事件

```python
from perfetto_extras import trace_events

# 创建 Trace 对象
t = trace_events.Trace()
# 创建进程轨迹
track = t.create_process_track("MyProcess", "category")
# 添加线程轨迹
thread = track.create_thread_track("MainThread", "category")
# 添加事件
thread.add_complete_event("event1", ts=0, duration_us=1000, args={"foo": 1})

# 导出为 JSON
with open("my_trace.json", "w") as f:
    f.write(t.dumps(indent=2, ensure_ascii=False))
```

### 2. 批量添加 Trace 事件（推荐）

```python
from perfetto_extras import trace_events

t = trace_events.Trace()

# 批量添加 counter 事件
t.add_batch_counter_events(
    process_name="CounterDemo",
    category="Counter",
    name_prefix="Counter",
    timestamps=[1000, 2000, 3000],
    values_list=[
        {"cat": 2, "dog": 4},
        {"cat": 3, "dog": 5},
        {"cat": 4, "dog": 6}
    ]
)

# 批量添加 instant 事件
t.add_batch_instant_events(
    process_name="InstantDemo",
    process_category="InstantCat",
    thread_name="Thread-1",
    thread_category="ThreadCat",
    timestamps=[1100, 2100, 3100],
    args_list=[
        {"event": "A"},
        {"event": "B"},
        {"event": "C"}
    ]
)

# 批量添加 complete 事件
t.add_batch_complete_events(
    process_name="CompleteDemo",
    process_category="CompleteCat",
    thread_name="Thread-2",
    thread_category="ThreadCat",
    timestamps=[1200, 2200, 3200],
    durations=[50, 60, 70],
    args_list=[
        {"task": "X"},
        {"task": "Y"},
        {"task": "Z"}
    ]
)

with open("batch_trace.json", "w") as f:
    f.write(t.dumps(indent=2, ensure_ascii=False))
```

### 3. 浏览器可视化 Trace 文件

#### 方式一：直接用命令行工具（推荐）

```bash
opentrace my_trace.json
```

#### 方式二：用 python -m 方式

```bash
python -m perfetto_extras.opentrace my_trace.json
```

命令会自动打开浏览器并加载本地 trace 文件到 Perfetto UI。

## 目录结构

```
perfetto_extras/
    trace_events.py   # Trace 事件生成核心模块
    opentrace.py      # 浏览器可视化工具
pyproject.toml        # 项目配置与依赖
README.md             # 使用说明
```

## 依赖

- Python >= 3.11
- protobuf == 5.29.3
- click >= 8.2.1, <9.0.0

## 贡献

欢迎提交 issue 和 PR！

1. Fork 本仓库
2. 新建分支
3. 提交修改
4. 发起 Pull Request

## License

MIT

---

**温馨提示：**  
- 如果你的包有更多功能、API 或命令行参数，请在 README 里详细补充示例和说明。
- 如果有徽章（如 PyPI 版本、CI 状态），可以加在最上面。

如需根据你的实际 API 或功能进一步定制，请把主要功能点或代码片段发给我，我可以帮你写得更详细！