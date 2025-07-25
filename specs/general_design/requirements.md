# Agent Context Engineering Specification

## 1. KV-Cache 优化 (KV-Cache Optimization)

### 1.1. 原则
最大化 KV-Cache 命中率以降低延迟和成本。上下文历史应被设计为高度可缓存的。

### 1.2. 实现要求
- **1.2.1. 稳定的提示词前缀**: 系统提示词 (System Prompt) 及任何前置上下文必须保持静态。禁止在缓存前缀中包含时间戳、请求ID等动态变量。
- **1.2.2. 上下文只追加**: 交互历史必须是只追加（append-only）的。禁止修改或删除历史中的任何动作（Action）或观察（Observation）。
- **1.2.3. 确定性序列化**: 所有从结构化数据（如 JSON）到字符串的序列化过程必须是确定性的，特别是对象键（key）的顺序必须固定。
- **1.2.4. 显式缓存断点**: (如果框架支持) 在需要的地方（如系统提示词之后）显式插入缓存断点，以确保关键前缀被缓存。
- **1.2.5. 服务端配置**: 对于自托管模型，必须启用前缀缓存（prefix caching）功能，并使用会话ID等机制确保同一会话的请求被路由到可重用缓存的实例上。

## 2. 工具可用性管理 (Tool Availability Management)

### 2.1. 原则
通过 Logits Masking 管理工具的可用性，而不是在上下文中动态增删工具定义。

### 2.2. 实现要求
- **2.2.1. 静态工具定义**: 在一次完整的任务会话中，提供给模型的工具定义列表必须保持不变。
- **2.2.2. 使用 Logits Masking**: 必须通过 logits masking/bias 或其他解码期干预手段来限制或强制模型选择特定的工具，而非通过修改上下文中的工具 schema。
- **2.2.3. 引导式函数调用**: 利用响应预填充（Response Prefill）技术引导模型生成特定的函数调用格式，可用于实现“强制调用工具”或“强制调用特定工具子集”。
- **2.2.4. 工具名称规范**: 工具名称应采用统一的前缀（如 `file_`、`browser_`）进行分组，以便于通过前缀进行批量屏蔽。

## 3. 将文件系统作为上下文 (File System as Context)

### 3.1. 原则
将本地文件系统作为持久化、大容量的外部记忆体，以克服上下文窗口的限制。

### 3.2. 实现要求
- **3.2.1. 文件 I/O 工具**: Agent 必须被赋予读（`readFile`）、写（`writeFile`）、列出（`ls`）等文件系统操作工具。
- **3.2.2. 可恢复的压缩**: 上下文压缩策略必须是无损且可逆的。必须保留恢复完整信息的引用（如文件路径或URL）。
- **3.2.3. 内容外部化**: 大尺寸的观察结果（如网页HTML、文件内容）必须被写入文件，在上下文中只保留其文件路径作为引用。
- **3.2.4. 按需读取**: Agent 必须能够根据上下文中的文件路径引用，在需要时使用文件读取工具将内容加载回来。

## 4. 通过复述引导注意力 (Attention Manipulation via Recitation)

### 4.1. 原则
为防止在长任务中发生目标偏离，应周期性地将核心任务计划重新注入到上下文的末尾。

### 4.2. 实现要求
- **4.2.1. 维护计划文件**: Agent 必须在任务开始时创建并维护一个计划文件（如 `plan.md` 或 `todo.md`）。
- **4.2.2. 周期性更新与复述**: Agent 必须周期性地（例如，在每个关键步骤后）执行一个动作序列：读取计划文件，更新其状态（如标记已完成项），并将更新后的完整计划作为观察结果附加到当前上下文的末尾。

## 5. 错误信息保留 (Error Information Retention)

### 5.1. 原则
在上下文中完整保留失败动作和其产生的错误信息，以供模型学习和适应。

### 5.2. 实现要求
- **5.2.1. 禁止清理失败记录**: 失败的动作及其尝试不得从历史记录中移除。
- **5.2.2. 完整错误报告**: 失败动作产生的观察结果必须包含由环境返回的、未经修改的完整错误信息或堆栈跟踪（Stack Trace）。
- **5.2.3. 正常化错误处理流程**: Agent 的控制循环在遇到错误后应正常继续，将包含错误信息的上下文传递给模型，由模型决定下一步骤。

## 6. 上下文多样性 (Context Diversity)

### 6.1. 原则
通过引入受控的、结构化的变体来打破上下文的模式重复性，避免模型因过度模仿（few-shot mimicry）而导致行为僵化。

### 6.2. 实现要求
- **6.2.1. 序列化模板变化**: 在不影响语义的前提下，为动作和观察结果的序列化引入多种模板。
- **6.2.2. 措辞多样性**: 对相似的观察结果使用略微不同的自然语言措辞。
- **6.2.3. 避免过度模仿**: 避免在上下文中填充大量完全相同的成功示例，鼓励模型根据当前具体情况进行推理，而非模式匹配。