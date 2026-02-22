# 在Google Cloud 上使用LangGraph、EDA 和生成式AI 构建 ...

**URL**:
https://codelabs.developers.google.com/aidemy-multi-agent/instructions?hl=zh-cn

## 元数据
- 发布日期: 2025-12-22T00:00:00+00:00

## 完整内容
---
Aidemy：在 Google Cloud 上使用LangGraph、EDA 和生成式AI 构建多代理系统| Google Codelabs[跳至主要内容] 
[![Google Codelabs]] 
/
* English
* Deutsch
* Español
* Español –América Latina
* Français
* Indonesia
* Italiano
* Polski
* Português –Brasil
* Tiếng Việt
* Türkçe
* Русский* עברית* العربيّة* فارسی* हिंदी* বাংলা* ภาษาไทย* 中文–简体* 中文–繁體* 日本語* 한국어登录# Aidemy：在 Google Cloud 上使用LangGraph、EDA 和生成式AI 构建多代理系统## 1. 简介您好！您对智能体的概念很感兴趣，对吧？智能体是一种小助手，无需您动手即可帮您处理各种事务。太棒了！但实际上，一个代理并不总是能满足需求，尤其是在处理更大、更复杂的项目时。您可能需要一整个团队的他们！这时，多智能体系统就能派上用场了。与旧式的硬编码相比，由LLM 提供支持的代理可为您提供出色的灵活性。不过，总会有一些问题，这些模型也面临着一系列棘手的挑战。这正是我们将在本次研讨会中深入探讨的内容！![title] 
以下是您将学到的内容，可帮助您提升代理技能：**使用 LangGraph 构建您的第一个代理**：我们将使用热门框架 LangGraph 亲手构建您自己的代理。您将学习如何创建可连接到数据库的工具，如何利用最新的Gemini 2 API 进行一些互联网搜索，以及如何优化提示和回答，以便您的代理不仅可以与LLM 互动，还可以与现有服务互动。我们还将向您展示函数调用的运作方式。**以您的方式编排智能体**：我们将探索编排智能体的不同方式，从简单的直线路径到更复杂的多路径场景。您可以将其视为指导代理团队的运作。
**多智能体系统**：您将了解如何设置一个智能体可以协作并共同完成任务的系统，而这一切都归功于事件驱动型架构。
**LLM 自由**：选择最适合的 LLM：我们不必只使用一个 LLM！您将了解如何使用多个 LLM，为它们分配不同的角色，从而利用出色的“思维模型”来提升问题解决能力。
**什么是动态内容？没问题！**：想象一下，您的代理可以实时创建专门为每位用户量身定制的动态内容。我们将向您展示如何操作！
**使用 Google Cloud 将数据分析提升到新高度**：不要再局限于在笔记本中进行简单的数据分析。我们将向您展示如何在 Google Cloud 上设计和部署多代理系统，以便该系统能够投入实际应用！此项目将很好地展示如何使用我们讨论的所有技巧。## 2. 架构当老师或从事教育工作非常有意义，但我们必须承认，工作量（尤其是所有准备工作）可能非常具有挑战性！此外，学校往往没有足够的员工，辅导费用可能很高。因此，我们建议使用AI 赋能的教学助理。此工具可减轻教育工作者的负担，并帮助弥合因人员短缺和缺乏经济实惠的辅导而造成的差距。我们的AI 教学助理可以快速生成详细的课程计划、有趣的测验、易于理解的音频总结和个性化的作业。这样一来，教师就可以专注于自己最擅长的事情：与学生建立联系，帮助他们爱上学习。该系统包含两个网站：一个供教师创建未来几周的课程计划，![规划本] 
另一个供学生访问测验、音频总结和作业。![门户] 
好的，我们来了解一下为Aidemy 教学助理提供支持的架构。如您所见，我们已将其分解为几个关键组件，这些组件协同工作以实现此目的。![架构] 
**关键架构元素和技术**：
**Google Cloud Platform (GCP)**：整个系统的核心：
* Vertex AI：访问 Google 的Gemini LLM。
* Cloud Run：用于部署容器化代理和函数的无服务器平台。
* Cloud SQL：用于存储课程数据的 PostgreSQL 数据库。* Pub/Sub 和Eventarc：事件驱动型架构的基础，可实现组件之间的异步通信。
* Cloud Storage：存储音频总结和作业文件。
* Secret Manager：安全地管理数据库凭据。
* Artifact Registry：存储代理的 Docker 映像。* Compute Engine：部署自托管 LLM，而不是依赖于供应商解决方案
**LLM**：系统的“大脑”：
* Google 的Gemini 模型：（Gemini x Pro、Gemini x Flash、Gemini x Flash Thinking）用于课程规划、内容生成、动态 HTML 创建、测验解释和作业合并。* DeepSeek：用于生成自学作业的专业任务
**LangChain 和LangGraph**：用于 LLM 应用开发的框架* 有助于创建复杂的多智能体工作流。* 支持对工具（API 调用、数据库查询、网页搜索）进行智能编排。* 实现事件驱动型架构，以提高系统可伸缩性和灵活性。从本质上讲，我们的架构将LLM 的强大功能与结构化数据和事件驱动型通信相结合，所有这些都在Google Cloud 上运行。这使我们能够构建可扩缩、可靠且有效的教学助理。## 3. 准备工作**对于 Google Cloud 赠金**：为帮助您入门，请使用此[链接] 兑换免费 Google Cloud 赠金。您可以按照[此处的说明] 激活抵扣金额并创建新项目，也可以按照以下说明操作。
在[Google Cloud 控制台] 的项目选择器页面上，选择或创建一个 Google Cloud[项目] 。确保您的 Cloud 项目已启用结算功能。[了解如何检查项目是否已启用结算功能] 。
**在 Cloud Shell IDE 中启用Gemini Code Assist**
👉在Google Cloud 控制台中，前往Gemini Code Assist 工具，同意相关条款及条件，即可免费启用Gemini Code Assist。
![01-04-code-assist-enable.png] 
忽略权限设置，离开此页面。**在 Cloud Shell 编辑器中工作**
👉点击Google Cloud 控制台顶部的**激活 Cloud Shell**（这是 Cloud Shell 窗格顶部的终端形状图标），然后点击“打开**编辑器**”按钮（看起来像一个带有铅笔的打开的文件夹）。此操作会在窗口中打开 Cloud Shell 代码编辑器。您会在左侧看到文件资源管理器。![Cloud Shell] 
👉如图所示，点击底部状态栏中的**Cloud Code 登录**按钮。按照说明对插件进行授权。如果您在状态栏中看到**Cloud Code - no project**，请选择该选项，然后在下拉菜单中选择“Select a Google Cloud Project”（选择 Google Cloud 项目），然后从您创建的项目列表中选择特定的Google Cloud 项目。![登录项目] 
👉在云IDE 中打开终端，![新终端] 或![新终端] 
👉在终端中，使用以下命令验证您是否已通过身份验证，以及项目是否已设置为您的项目ID：
```
`gcloudauthlist`
```
👉并运行，确保将*&lt;&lt;YOUR\_PROJECT\_ID\>*替换为您的项目 ID：
```
`echo&lt;YOUR\_PROJECT\_ID&gt; &gt;\~/project\_id.txtgcloudconfigsetproject$(cat\~/project\_id.txt)`
```
👉运行以下命令以启用必要的Google Cloud API：
```
`gcloudservicesenablecompute.googleapis.com\\storage.googleapis.com\\run.googleapis.com\\artifactregistry.googleapis.com\\aiplatform.googleapis.com\\eventarc.googleapis.com\\sqladmin.googleapis.com\\secretmanager.googleapis.com\\cloudbuild.googleapis.com\\cloudresourcemanager.googleapis.com\\cloudfunctions.googleapis.com\\cloudaicompanion.googleapis.com`
```
这可能需要几分钟的时间。**设置权限**
👉设置服务账号权限。在终端中，运行以下命令：```
`gcloudconfigsetproject$(cat\~/project\_id.txt)exportPROJECT\_ID=$(gcloudconfiggetproject)exportSERVICE\_ACCOUNT\_NAME=$(gcloudcomputeproject-infodescribe--format="value(defaultServiceAccount)")echo"Here's your SERVICE\_ACCOUNT\_NAME $SERVICE\_ACCOUNT\_NAME"`
```
👉授予权限。在终端中，运行以下命令：```
`#Cloud Storage (Read/Write):gcloudprojectsadd-iam-policy-binding$PROJECT\_ID\\--member="serviceAccount:$SERVICE\_ACCOUNT\_NAME"\\--role="roles/storage.objectAdmin"#Pub/Sub (Publish/Receive):gcloudprojectsadd-iam-policy-binding$PROJECT\_ID\\--member="serviceAccount:$SERVICE\_ACCOUNT\_NAME"\\--role="roles/pubsub.publisher"gcloudprojectsadd-iam-policy-binding$PROJECT\_ID\\--member="serviceAccount:$SERVICE\_ACCOUNT\_NAME"\\--role="roles/pubsub.subscriber"#Cloud SQL (Read/Write):gcloudprojectsadd-iam-policy-binding$PROJECT\_ID\\--member="serviceAccount:$SERVICE\_ACCOUNT\_NAME"\\--role="roles/cloudsql.editor"#Eventarc (Receive Events):gcloudprojectsadd-iam-policy-binding$PROJECT\_ID\\--member="serviceAccount:$SERVICE\_ACCOUNT\_NAME"\\--role="roles/iam.serviceAccountTokenCreator"gcloudprojectsadd-iam-policy-binding$PROJECT\_ID\\--member="serviceAccount:$SERVICE\_ACCOUNT\_NAME"\\--role="roles/eventarc.eventReceiver"#Vertex AI (User):gcloudprojectsadd-iam-policy-binding$PROJECT\_ID\\--member="serviceAccount:$SERVICE\_ACCOUNT\_NAME"\\--role="roles/aiplatform.user"#Secret Manager (Read):gcloudprojectsadd-iam-policy-binding$PROJECT\_ID\\--member="serviceAccount:$SERVICE\_ACCOUNT\_NAME"\\--role="roles/secretmanager.secretAccessor"`
```
👉在[IAM 控制台] 中验证结果![IAM 控制台] 
👉在终端中运行以下命令，以创建名为**aidemy**的 Cloud SQL 实例。我们稍后会用到此功能，但由于此过程可能需要一些时间，因此我们现在就来完成。```
`gcloudsqlinstancescreateaidemy\\--database-version=POSTGRES\_14\\--cpu=2\\--memory=4GB\\--region=us-central1\\--root-password=1234qwer\\--storage-size=10GB\\--storage-auto-increase`
```
预配实例需要一段时间，请让此命令运行，然后继续执行下一步。## 4. 构建第一个代理在深入探讨复杂的多智能体系统之前，我们需要先建立一个基本构建块：单个功能性智能体。在本部分中，我们将迈出第一步，创建一个简单的“图书提供商”代理。图书提供商代理会接受一个类别作为输入，并使用Gemini LLM 生成该类别中的图书的JSON 表示形式。然后，它会以REST API 端点的形式提供这些图书推荐。![图书提供商]<image_link>
👉在另一个浏览器标签页中，在网络浏览器中打开[Google Cloud 控制台]<web_link>。在导航菜单 (☰) 中，前往“Cloud Run”。点击“+ ... 编写函数”按钮。![创建函数]<image_link>
👉接下来，我们将配置Cloud Run 函数的基本设置：* 服务名称：`book-provider`
* 区域：`us-central1`
* 运行时：`Python 3.12`
* 身份验证：从`Allow unauthenticated invocations`更改为“已启用”。
将“允许未经身份验证的调用”设置为启用后，外部流量无需身份验证即可访问该函数。👉将其他设置保留为默认值，然后点击**创建**。系统会将您转到源代码编辑器。
您会看到预先填充的`main.py`和`requirements.txt`文件。
`main.py`将包含函数的业务逻辑，`requirements.txt`将包含所需的软件包。
👉现在，我们准备好编写一些代码了！不过，在深入了解之前，我们先看看**Gemini Code Assist**能否帮助我们抢占先机。**返回到 Cloud Shell 编辑器**，点击顶部的 Gemini Code Assist 图标，系统应会打开Gemini Code Assist 对话。![Gemini Code Assist]<image_link>
您可能会看到一个弹出式窗口，其中包含类似“您缺少有效的Gemini Code Assist 许可，因此可能无法再访问该服务。请与您的结算管理员联系，购买或分配许可。”请忽略此消息。👉将以下请求粘贴到提示框中：```
`Usethefunctions\_frameworklibrarytobedeployableasanHTTPfunction.Acceptarequestwithcategoryandnumber\_of\_bookparameters(eitherinJSONbodyorquerystring).Uselangchainandgeminitogeneratethedataforbookwithfieldsbookname,author,publisher,publishing\_date.UsepydantictodefineaBookmodelwiththefields:bookname(string,description:"Name of the book"),author(string,description:"Name of the author"),publisher(string,description:"Name of the publisher"),andpublishing\_date(string,description:"Date of publishing").Uselangchainandgeminimodeltogeneratebookdata.theoutputshouldfollowtheformatdefinedinBookmodel.ThelogicshoulduseJsonOutputParserfromlangchaintoenforceoutputformatdefinedinBookModel.Haveafunctionget\_recommended\_books(category)thatinternallyuseslangchainandgeminitoreturnasinglebookobject.Themainfunction,exposedastheCloudFunction,shouldcallget\_recommended\_books()multipletimes(basedonnumber\_of\_book)andreturnaJSONlistofthegeneratedbookobjects.Handlethecasewherecategoryornumber\_of\_bookaremissingbyreturninganerrorJSONresponsewitha400statuscode.returnaJSONstringrepresentingtherecommendedbooks.useoslibrarytoretrieveGOOGLE\_CLOUD\_PROJECTenvvar.UseChatVertexAIfromlangchainfortheLLMcall`
```
然后，Code Assist 会生成一个潜在的解决方案，同时提供源代码和requirements.txt 依赖项文件。（请勿使用此代码）建议您将Code Assist 生成的代码与下面提供的经过测试的正确解决方案进行比较。这样，您就可以评估该工具的效果并发现任何潜在的差异。虽然绝不应盲目信任LLM，但 Code Assist 是一款出色的工具，可用于快速原型设计和生成初始代码结构，应使用它来获得良好的开端。由于这是一个研讨会，我们将继续使用下方提供的已验证代码。不过，您可以自行尝试使用Code Assist 生成的代码，以便更深入地了解其功能和局限性。👉返回到Cloud Run 函数的源代码编辑器（在另一个浏览器标签页中）。请仔细将`main.py`的现有内容替换为以下代码：
```
`importfunctions\_frameworkimportjsonfromflaskimportFlask,jsonify,requestfromlangchain\_google\_vertexaiimportChatVertexAIfromlangchain\_core.output\_parsersimportJsonOutputParserfromlangchain\_core.promptsimportPromptTemplatefrompydanticimportBaseModel,FieldimportosclassBook(BaseModel):bookname:str=Field(description="Name of the book")author:str=Field(description="Name of the author")publisher:str=Field(description="Name of the publisher")publishing\_date:str=Field(description="Date of publishing")project\_id=os.environ.get("GOOGLE\_CLOUD\_PROJECT")llm=ChatVertexAI(model\_name="gemini-2.0-flash-lite-001")defget\_recommended\_books(category):"""A simple book recommendation function.Args:category (str): categoryReturns:str: A JSON string representing the recommended books."""parser=JsonOutputParser(pydantic\_object=Book)question=f"Generate a random made up book on{category}with bookname, author and publisher and publishing\_date"prompt=PromptTemplate(template="Answer the user query.\\n{format\_instructions}\\n{query}\\n",input\_variables=["query"],partial\_variables={"format\_instructions":parser.get\_format\_instructions()},)chain=prompt|llm|parserresponse=chain.invoke({"query":question})returnjson.dumps(response)@functions\_framework.httpdefrecommended(request):request\_json=request.get\_json(silent=True)# Get JSON dataifrequest\_jsonand'category'inrequest\_jsonand'number\_of\_book'inrequest\_json:category=request\_json['category']number\_of\_book=int(request\_json['number\_of\_book'])elifrequest.argsand'category'inrequest.argsand'number\_of\_book'inrequest.args:category=request.args.get('category')number\_of\_book=int(request.args.get('number\_of\_book'))else:returnjsonify({'error':'Missing category or number\_of\_book parameters'}),400recommendations\_list=[]foriinrange(number\_of\_book)


---
*数据来源: Exa搜索 | 获取时间: 2026-02-22 20:38:45*