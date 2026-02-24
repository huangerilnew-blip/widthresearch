概述 - LangChain 教程
===============
- [x] - [x] 

[跳到内容](https://github.langchain.ac.cn/langgraph/concepts/human_in_the_loop/#human-in-the-loop)

**LangGraph 平台文档已迁移！** 请在新的 [LangChain 文档](https://docs.langchain.org.cn/langgraph-platform)网站上查找 LangGraph 平台文档。

[![Image 1: logo](https://github.langchain.ac.cn/langgraph/static/wordmark_dark.svg)![Image 2: logo](https://github.langchain.ac.cn/langgraph/static/wordmark_light.svg)](https://github.langchain.ac.cn/langgraph/ "LangGraph")

LangGraph

概述

[](https://github.langchain.ac.cn/langgraph/concepts/human_in_the_loop/?q= "Share")

正在初始化搜索

[GitHub](https://github.com/langchain-ai/langgraph "Go to repository")

*   [开始使用](https://github.langchain.ac.cn/langgraph/)
*   [指南](https://github.langchain.ac.cn/langgraph/guides/)
*   [参考](https://github.langchain.ac.cn/langgraph/reference/)
*   [示例](https://github.langchain.ac.cn/langgraph/examples/)
*   [更多资源](https://github.langchain.ac.cn/langgraph/additional-resources/)

[![Image 3: logo](https://github.langchain.ac.cn/langgraph/static/wordmark_dark.svg)![Image 4: logo](https://github.langchain.ac.cn/langgraph/static/wordmark_light.svg)](https://github.langchain.ac.cn/langgraph/ "LangGraph") LangGraph 

[GitHub](https://github.com/langchain-ai/langgraph "Go to repository")

*   [开始使用](https://github.langchain.ac.cn/langgraph/)
*   - [x] [指南](https://github.langchain.ac.cn/langgraph/guides/)  指南 
    *   - [x]  智能体开发   智能体开发 
        *   [概述](https://github.langchain.ac.cn/langgraph/agents/overview/)
        *   [运行智能体](https://github.langchain.ac.cn/langgraph/agents/run_agents/)

    *   - [x]  LangGraph API   LangGraph API 
        *   [图 API](https://github.langchain.ac.cn/langgraph/concepts/low_level/)
        *   [函数式 API](https://github.langchain.ac.cn/langgraph/concepts/functional_api/)
        *   [运行时](https://github.langchain.ac.cn/langgraph/concepts/pregel/)

    *   - [x]  核心功能   核心功能 
        *   [流式处理](https://github.langchain.ac.cn/langgraph/concepts/streaming/)
        *   [持久化](https://github.langchain.ac.cn/langgraph/concepts/persistence/)
        *   [持久化执行](https://github.langchain.ac.cn/langgraph/concepts/durable_execution/)
        *   [内存](https://github.langchain.ac.cn/langgraph/concepts/memory/)
        *   [上下文](https://github.langchain.ac.cn/langgraph/agents/context/)
        *   [模型](https://github.langchain.ac.cn/langgraph/agents/models/)
        *   [工具](https://github.langchain.ac.cn/langgraph/concepts/tools/)
        *   - [x]  人工干预   人机协作 (Human-in-the-loop) 
            *   - [x]  概述  [概述](https://github.langchain.ac.cn/langgraph/concepts/human_in_the_loop/) 目录 
                *   [核心功能](https://github.langchain.ac.cn/langgraph/concepts/human_in_the_loop/#key-capabilities)
                *   [模式](https://github.langchain.ac.cn/langgraph/concepts/human_in_the_loop/#patterns)

            *   [添加人工干预](https://github.langchain.ac.cn/langgraph/how-tos/human_in_the_loop/add-human-in-the-loop/)

        *   [时间旅行](https://github.langchain.ac.cn/langgraph/concepts/time-travel/)
        *   [子图](https://github.langchain.ac.cn/langgraph/concepts/subgraphs/)
        *   [多智能体](https://github.langchain.ac.cn/langgraph/concepts/multi_agent/)
        *   [MCP](https://github.langchain.ac.cn/langgraph/concepts/mcp/)
        *   [追踪](https://github.langchain.ac.cn/langgraph/concepts/tracing/)

*   [参考](https://github.langchain.ac.cn/langgraph/reference/)
*   [示例](https://github.langchain.ac.cn/langgraph/examples/)
*   [额外资源](https://github.langchain.ac.cn/langgraph/additional-resources/)

 目录 
*   [核心功能](https://github.langchain.ac.cn/langgraph/concepts/human_in_the_loop/#key-capabilities)
*   [模式](https://github.langchain.ac.cn/langgraph/concepts/human_in_the_loop/#patterns)

hil human-in-the-loop overview[](https://github.com/langchain-ai/langgraph/edit/main/docs/docs/concepts/human_in_the_loop.md "Edit this page")
人机协作 (Human-in-the-loop)[¶](https://github.langchain.ac.cn/langgraph/concepts/human_in_the_loop/#human-in-the-loop "Permanent link")
====================================================================================================================================

要在代理或工作流中审查、编辑和批准工具调用，请[使用 LangGraph 的人机协同（human-in-the-loop）功能](https://github.langchain.ac.cn/langgraph/how-tos/human_in_the_loop/add-human-in-the-loop/)，以便在工作流的任何时刻进行人工干预。这在大型语言模型 (LLM) 驱动的应用中尤其有用，因为模型输出可能需要验证、修正或额外的上下文。

![Image 5: image](https://github.langchain.ac.cn/langgraph/concepts/img/human_in_the_loop/tool-call-review.png)

提示

有关如何使用人机协同的信息，请参阅[启用人工干预](https://github.langchain.ac.cn/langgraph/how-tos/human_in_the_loop/add-human-in-the-loop/)和[使用服务器 API 实现人机协同](https://github.langchain.ac.cn/langgraph/cloud/how-tos/add-human-in-the-loop/)。

核心功能[¶](https://github.langchain.ac.cn/langgraph/concepts/human_in_the_loop/#key-capabilities "Permanent link")
---------------------------------------------------------------------------------------------------------------

*   **持久化执行状态**：中断功能使用了 LangGraph 的[持久化](https://github.langchain.ac.cn/langgraph/concepts/persistence/)层，该层会保存图的状态，从而可以无限期地暂停图的执行，直到您恢复为止。这是因为 LangGraph 在每一步之后都会为图状态创建检查点，这使得系统能够持久化执行上下文并在之后从中断处继续恢复工作流。这支持了没有时间限制的异步人工审查或输入。

有两种暂停图的方法

    *   [动态中断](https://github.langchain.ac.cn/langgraph/how-tos/human_in_the_loop/add-human-in-the-loop/#pause-using-interrupt)：在特定节点内部，根据图的当前状态使用 `interrupt` 来暂停图。
    *   [静态中断](https://github.langchain.ac.cn/langgraph/how-tos/human_in_the_loop/add-human-in-the-loop/#debug-with-interrupts)：使用 `interrupt_before` 和 `interrupt_after` 在预定义的点暂停图，即在节点执行之前或之后。

![Image 6: image](https://github.langchain.ac.cn/langgraph/concepts/img/breakpoints.png)

一个由3个顺序步骤组成的示例图，在 step_3 之前设有一个断点。

*   **灵活的集成点**：人机协同逻辑可以引入到工作流的任何一点。这允许有针对性的人工参与，例如批准 API 调用、修正输出或引导对话。

模式[¶](https://github.langchain.ac.cn/langgraph/concepts/human_in_the_loop/#patterns "Permanent link")
-----------------------------------------------------------------------------------------------------

您可以使用 `interrupt` 和 `Command` 实现四种典型的设计模式

*   [批准或拒绝](https://github.langchain.ac.cn/langgraph/how-tos/human_in_the_loop/add-human-in-the-loop/#approve-or-reject)：在关键步骤（如 API 调用）之前暂停图，以审查和批准该操作。如果操作被拒绝，您可以阻止图执行该步骤，并可能采取替代操作。此模式通常涉及根据人工输入来路由图。
*   [审查和编辑状态](https://github.langchain.ac.cn/langgraph/how-tos/human_in_the_loop/add-human-in-the-loop/#review-and-edit-state)：暂停图以审查和编辑图状态。这对于纠正错误或用附加信息更新状态很有用。此模式通常涉及用人工输入来更新状态。
*   [审查工具调用](https://github.langchain.ac.cn/langgraph/how-tos/human_in_the_loop/add-human-in-the-loop/#review-tool-calls)：在工具执行之前，暂停图以审查和编辑 LLM 请求的工具调用。
*   [验证人工输入](https://github.langchain.ac.cn/langgraph/how-tos/human_in_the_loop/add-human-in-the-loop/#validate-human-input)：在进入下一步之前，暂停图以验证人工输入。

回到顶部[上一页 调用工具](https://github.langchain.ac.cn/langgraph/how-tos/tool-calling/)[下一页 添加人工干预](https://github.langchain.ac.cn/langgraph/how-tos/human_in_the_loop/add-human-in-the-loop/)

版权所有 © 2025 LangChain, Inc | [同意偏好](https://github.langchain.ac.cn/langgraph/concepts/human_in_the_loop/#__consent)

使用 [MkDocs Material](https://squidfunk.github.io/mkdocs-material/) 制作

[](https://github.langchain.ac.cn/langgraphjs/ "langchain-ai.github.io")[](https://github.com/langchain-ai/langgraph "github.com")[](https://twitter.com/LangChainAI "twitter.com")