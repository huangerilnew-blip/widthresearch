## 热搜

## 最近搜索[清空](javascript:void(0);)

![](/static/img/article/article-logo.png?v=1)
![](/static/img/article/article-desc.png)

# 使用LangGraph实现Map-Reduce：构建灵活的并行处理分支

在这篇文章中，我们将介绍 LangChain 的一篇文章，并实现之前讨论过的树形思维算法。我们将在 LangGraph 中使用 map-reduce 方法来进行实现。

Map-reduce操作是实现高效任务分解并进行并行处理的关键技术。这种方法涉及到将大型任务分解成更小的子任务，这些子任务并行处理完毕后，再将结果汇总起来。

![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC "使用LangGraph实现Map-Reduce：构建灵活的并行处理分支_")

![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC "使用LangGraph实现Map-Reduce：构建灵活的并行处理分支_")

然而，在实现这一点时存在两个主要挑战：一个是设计图时可能不清楚子任务的数量，另一个是每个子任务需要不同的输入状态。为解决这些问题，LangGraph 提供了一个使用 `Send` API 的解决方案。该 API 利用条件连接将不同的状态分发给多个节点实例。此外，它允许发送的状态与核心图的当前状态不同，从而实现灵活且动态的工作流程管理。

`Send`

这种方法能高效地执行复杂的并行处理任务，适用于大规模数据处理和复杂计算任务。LangGraph的`Send` API是一个创新解决方案，显著提升了MapReduce操作实施的灵活性和效率。

`Send`

我们将要介绍的代码实现使用LangGraph来实现Map-Reduce模式，以自动化生成、评估和分析改善发展中城市公共交通的解决方案。我们将解释关键部分，特别是如何使用Send：

总体流程：  
— 生成解决方案  
— 评估每个解决方案  
— 对每个评估进行深入分析  
— 最后排名

StateGraph 的用途：代码使用 StateGraph 来定义工作流。这管理着数据在各个步骤之间的流动。

`# 定义继续评估函数，参数为OverallState对象
def continue_to_evaluation(state: OverallState):
# 对每一个解决方案进行评估
return [Send("评估解决方案", {"解决方案": s}) for s in state["解决方案"]]`

备注：`OverallState` 和 `解决方案` 分别表示总体状态和解决方案列表。函数 `evaluate_solution` 的作用是评估每个解决方案的有效性。

`OverallState`
`解决方案`
`evaluate_solution`

此功能会为每个生成的解决方案调用“evaluate\_solution”节点。每个解决方案都会单独评估。

`def 继续深入思考(state: OverallState):
return [Send("深入思考", {"评论": r}) for r in state["reviews"]]`

这种方法让我们能够模仿复杂的思维过程，高效处理大量信息。通过使用 Send，我们可以实现整个过程中的动态和灵活的工作流管理。

 `import operator
from typing import Annotated, TypedDict
from langchain_core.pydantic_v1 import BaseModel
from langchain_anthropic import ChatAnthropic
from langgraph.constants import Send
from langgraph.graph import END, StateGraph, START
# 初始化AI模型
model = ChatAnthropic(model="claude-3-5-sonnet-20240620")
# 定义每个步骤的提示
step1_prompt = """步骤1：我有一个与{input}相关的问题。你能为我脑暴三个不同的解决方案吗？请考虑各种因素，例如{perfect_factors}"""
step2_prompt = """步骤2：对于每个提出的解决方案，进行评估。考虑其优缺点，所需初期努力，实施难度，潜在挑战和预期结果。根据这些因素为每个选项分配成功概率和信心水平。
解决方案：
{solutions}"""
step3_prompt = """步骤3：对每个解决方案进行深入思考。生成潜在场景，制定实施策略，确定必要的合作伙伴关系或资源，以及如何克服潜在障碍。同时考虑任何可能的意外后果及其处理方式。
评估：
{review}"""
step4_prompt = """步骤4：根据评估和场景对解决方案进行排名。根据潜力对解决方案进行排名。为每个排名提供理由，并提供每个解决方案的最终考虑。
详细分析：
{deepen_thought_process}"""
# 定义AI输出的数据结构
class Solutions(BaseModel):
solutions: list[str]
class Review(BaseModel):
review: str
class DeepThought(BaseModel):
deep_thought: str
class RankedSolutions(BaseModel):
ranked_solutions: str
# 定义整个过程的状态
class OverallState(TypedDict):
input: str
perfect_factors: str
solutions: Annotated[list[str], operator.add]
reviews: Annotated[list[str], operator.add]
deep_thoughts: Annotated[list[str], operator.add]
ranked_solutions: str
# 定义单个解决方案处理的状态
class SolutionState(TypedDict):
solution: str
# 图形组件函数
def generate_solutions(state: OverallState):
# 根据输入的问题和因素生成初始解决方案
prompt = step1_prompt.format(input=state["input"], perfect_factors=state["perfect_factors"])
response = model.with_structured_output(Solutions).invoke(prompt)
return {"solutions": response.solutions}
def evaluate_solution(state: SolutionState):
# 单独评估每个解决方案
prompt = step2_prompt.format(solutions=state["solution"])
response = model.with_structured_output(Review).invoke(prompt)
return {"reviews": [response.review]}
def deepen_thought(state: SolutionState):
# 对每个解决方案进行深入分析
prompt = step3_prompt.format(review=state["solution"])
response = model.with_structured_output(DeepThought).invoke(prompt)
return {"deep_thoughts": [response.deep_thought]}
def rank_solutions(state: OverallState):
# 根据深入分析对所有解决方案进行排名
deep_thoughts = "\n\n".join(state["deep_thoughts"])
prompt = step4_prompt.format(deepen_thought_process=deep_thoughts)
response = model.with_structured_output(RankedSolutions).invoke(prompt)
return {"ranked_solutions": response.ranked_solutions}
# 定义并行处理的映射逻辑
def enter_evaluation(state: OverallState):
# 为评估每个解决方案创建并行分支
return [Send("evaluate_solution", {"solution": s}) for s in state["solutions"]]
def deepen_thought_process(state: OverallState):
# 为每个评估的深入分析创建并行分支
return [Send("deepen_thought", {"solution": r}) for r in state["reviews"]]
# 构建图
graph = StateGraph(OverallState)
# 向图中添加节点
graph.add_node("generate_solutions", generate_solutions)
graph.add_node("evaluate_solution", evaluate_solution)
graph.add_node("deepen_thought", deepen_thought)
graph.add_node("rank_solutions", rank_solutions)
# 添加边以连接节点
graph.add_edge(START, "generate_solutions")
graph.add_conditional_edges("generate_solutions", enter_evaluation, ["evaluate_solution"])
graph.add_conditional_edges("evaluate_solution", deepen_thought_process, ["deepen_thought"])
graph.add_edge("deepen_thought", "rank_solutions")
graph.add_edge("rank_solutions", END)
# 编译图
app = graph.compile()
# 执行图
for s in app.stream({
"input": "改善一个正在增长的城市的公共交通",
"perfect_factors": "成本、效率、环境影响和用户体验"
}):
print(s)`

**执行情况**

`{
"generate_solutions": {
"solutions": ["实施快速公交系统（BRT）", "开发全面的共享单车计划", "引入集成智能卡支付系统"]
}
}
{
"evaluate_solution": {
"reviews": ["\n我将评估提出的解决方案：开发全面的共享单车计划\n\n优点:\n1. 环保的交通选择\n2. 减少交通拥堵并解决停车问题\n3. 促进体育活动和公共健康\n4. 提升城市交通可达性\n5. 有可能吸引游客并促进当地经济\n\n缺点:\n1. 初始基础设施和自行车的高投资\n2. 持续的维护费用\n3. 自行车可能遭受破坏或盗窃\n4. 依赖天气\n5. 可能会受到汽车主导社区的反对\n\n所需初始努力:\n1. 全面的城市规划和可行性研究\n2. 获得资金（公共、私人或混合）\n3. 与自行车制造商和技术提供商建立合作关系\n4. 创建用户友好的应用程序和支付系统\n5. 建立停车站和自行车道\n\n实施难度：中等到高\n- 需要多个利益相关者之间的协调（城市规划者、交通部门、私人合作伙伴）\n- 需要基础设施变化（自行车道、停车站）\n- 为自行车跟踪和用户管理集成技术\n\n潜在挑战:\n1. 在城市不同区域平衡自行车的可用性\n2. 在混合交通环境中确保骑行者安全\n3. 克服公众的反对或怀疑\n4. 适应不同季节和天气条件\n5. 与现有的交通选择竞争（例如，拼车服务）\n\n预期结果:\n1. 可持续交通的使用增加\n2. 减少个人车辆的碳排放\n3. 由于增加的体育活动改善公共健康\n4. 作为进步和环保的城市形象增强\n5. 有可能减少交通拥堵\n\n成功概率：70%\n如果仔细实施并有强大的社区参与，共享单车计划有很大的成功机会。世界上许多城市已成功采用类似的计划，证明了它们的可行性。\n\n信心水平：75%\n尽管存在挑战，但潜在的好处和支持可持续城市交通的全球趋势使人们对这一解决方案的成功潜力保持相当高的信心。\n"]
}
}
{
"evaluate_solution": {
"reviews": ["评估引入集成智能卡支付系统的提议，让我们考虑其潜力、优缺点、实施因素和预期结果:\n\n1. 潜力:\n集成智能卡支付系统具有重要意义，因为它可以简化交易，改善客户体验，可能增加收入。\n\n2. 优点:\n- 方便用户：一张卡适用于多种交通方式\n- 更快的交易：减少排队时间\n- 数据收集：提供有关旅行模式的宝贵见解\n- 减少现金处理：提高安全性和降低成本\n- 灵活的票价结构：易于实施折扣和忠诚计划\n\n3. 缺点:\n- 初始投资高：需要大量前期资金\n- 技术复杂性：需要强大的基础设施和软件\n- 隐私问题：处理个人和金融数据\n- 采用挑战：一些用户可能会抵制变化\n\n4. 初始所需努力:\n所需初始努力包括:\n- 系统设计和规划\n- 硬件采购和安装\n- 软件开发和集成\n- 员工培训\n- 公众教育和营销活动\n\n5. 实施难度:\n实施难度相对较高，因为:\n- 与现有系统的复杂集成\n- 需要多个交通机构之间的协调\n- 可能的技术挑战和兼容性问题\n- 需要广泛的测试和逐步推出\n\n6. 潜在挑战:\n- 初期部署中的技术故障\n- 某些用户群体的抵制（例如，老年人、低收入群体）\n- 确保系统的安全性和数据保护\n- 持续系统的可靠性和减少停机时间\n\n7. 预期结果:\n- 收费收集效率的提高\n- 更好的用户体验和满意度\n- 更好的数据用于交通规划和优化\n- 可能由于便利性增加乘车次数\n- 长期的收费收集和管理成本节省\n\n8. 成功概率:\n鉴于其他城市的类似系统记录和潜在好处，我将成功概率定为75%。\n\n9. 信心水平:\n基于可用信息和项目的复杂性，我将信心水平定为80%。\n\n总之，尽管引入集成智能卡支付系统存在重大挑战和需要大量的初始投资，但其潜在好处和长期优势使其成为改善交通系统的希望解决方案。相对较高的成功概率和信心水平表明，这一选项值得认真考虑，前提是实施计划周全并执行得当。"]
}
}
{
"evaluate_solution": {
"reviews": ["基于给定的任务，我将评估实施快速公交系统（BRT）作为解决城市交通问题的一种解决方案的潜力。我将考虑各种因素并分配成功概率和信心水平。\n\n评估快速公交（BRT）系统:\n\n优点:\n1. 与基于铁路的交通系统相比更具成本效益\n2. 实施时间比地铁或轻轨系统快\n3. 增加了乘客容量，比常规公交车更具优势\n4. 专用车道减少了旅行时间并提高了可靠性\n5. 灵活可扩展 - 可以根据需要进行扩展或修改\n6. 有可能减少交通拥堵和碳排放\n\n缺点:\n1. 可能需要重新分配道路空间，减少私人车辆的车道\n2. 初始抵抗来自受影响的车道改变的汽车用户和企业\n3. 重于重型铁路系统的容量较低\n4. 比铁路系统选择对乘客的吸引力较低\n\n所需初始努力:\n1. 全面的城市规划和交通研究\n2. 专用公交车道和车站的设计\n3. 采购专用BRT车辆\n4. 安装智能交通系统（ITS）进行实时跟踪和信号优先\n5. 公众宣传和教育活动\n\n实施难度：中等\n- 虽然比铁路系统更容易实施，但BRT仍然需要大量基础设施变化和各个城市部门之间的协调。\n\n潜在挑战:\n1. 获得资金和政治支持\n2. 克服来自汽车主导社区的反对\n3. 确保与现有交通系统的无缝整合\n4. 维护专用车道，防止未经授权使用\n5. 实现高质量服务标准以吸引乘客\n\n预期结果:\n1. 改善公共交通旅行时间和可靠性\n2. 增加公共交通乘车次数\n3. 在BRT走廊减少交通拥堵\n4. 改善空气质量并减少碳排放\n5. 增强城市交通可达性和便利性\n6. 沿BRT走廊可能实现交通导向型开发\n\n成功概率：75%\n相对较高的成功概率基于BRT系统在世界各地城市的证明记录、成本效益及其实施和操作的灵活性。\n\n信心水平：80%\n高信心水平基于全球实施BRT系统的大量数据，许多城市观察到的明确好处以及系统的适应性。然而，本地因素和潜在反对可能仍会影响项目的成功，因此不是更高的信心水平。\n\n总体而言，实施快速公交系统似乎是改善城市交通的希望解决方案。其成本效益、相对快速的实施时间和在其他城市证明的成功使其成为强有力的竞争者。但是，仔细规划、强大的政治意愿和有效的公众参与将是克服潜在挑战并确保成功的关键。"]
}
}
{
"deepen_thought": {
"deep_thoughts": ["\n要深入思考集成智能卡支付系统解决方案，让我们考虑潜在情景、实施策略、合作伙伴关系、资源、障碍管理和意外结果:\n\n1. 潜在情景:\n\na) 分阶段推出:\n- 情景: 以单个交通模式（例如公交车）为起点，逐步扩展到其他模式。\n- 策略: 在特定区域或路线开始试点计划，测试系统并收集反馈，然后再进行全实施。\n\nb) 多个城市合作:\n- 情景: 与邻近城市合作，创建一个区域智能卡系统。\n- 策略: 形成一个交通管理机构联盟，分享成本、专业知识和资源，以创建一个更全面和广泛采用的系统。\n\nc) 公共-私人合作伙伴关系:\n- 情景: 与技术公司合作，开发和维护系统。\n- 策略: 利用私营部门的专业知识，同时保持公共监管和控制票价政策。\n\n2. 实施策略:\n\na) 利益相关者参与:\n- 进行广泛的用户研究，并在设计过程中涉及各种利益相关者群体。\n- 创建一个由不同交通机构和部门代表组成的专用项目团队。\n\nb) 技术选择:\n- 评估多个技术提供商并选择一个提供灵活性和可扩展性的解决方案。\n- 确保所选技术可以与现有系统集成并适应未来创新。\n\nc) 渐进过渡:\n- 在新系统推出期间，保持现有支付方式。\n- 为早期智能卡系统用户提供激励措施（例如折扣、积分）。\n\n3. 必要的合作伙伴关系和资源:\n\na) 合作伙伴:\n- 技术公司提供硬件和软件解决方案\n- 金融机构处理支付\n- 地方企业进行潜在的交叉推广和智能卡的扩展使用\n- 社区组织协助宣传和教育\n\nb) 资源:\n- 资金: 获得政府拨款、交通局预算和可能的私人投资\n- 技术专业知识: 从智能卡技术、数据安全和系统集成方面的专家着手或承包\n- 培训资源: 为员工开发全面的培训计划和为公众提供教育材料\n\n4. 克服潜在障碍:\n\na) 技术问题:\n- 实施严格的测试协议并拥有一个专属的技术支持团队\n- 为系统故障制定应急计划，包括离线验证方法\n\nb) 用户采用:\n- 发起全面的营销和教育运动\n- 在主要交通枢纽提供帮助站和员工，帮助用户过渡\n- 为意外欠款或系统误用提供宽限期\n\nc) 隐私问题:\n- 实施强大的数据保护措施，并清楚地传达隐私政策\n- 为用户提供匿名卡选项\n\nd) 公平问题:\n- 确保无银行账户的人可以进行现金充值\n- 为低收入用户提供补贴或免费卡\n\n5. 潜在意外结果和管理:\n\na) 出乎意料的高采用率:\n- 结果: 系统过载或卡短缺\n- 管理: 具备可扩展的基础设施和卡的灵活供应链\n\nb) 不预期的安全漏洞:\n- 结果: 数据泄露或欺诈卡使用\n- 管理: 建立快速响应团队和协议；进行定期安全审计\n\nc) 与某些交通模式的集成挑战:\n- 结果: 全系统实施延迟\n- 管理: 为特定模式制定解决方案，并准备好延长时间表\n\nd) 旅行模式的变化:\n- 结果: 由于新系统而出现的交通使用变化\n- 管理: 利用数据分析快速识别趋势并进行相应调整\n\ne) 扩展使用到其他城市服务:\n- 结果: 城市服务或地方企业的卡使用增加\n- 管理: 开发扩展使用的合作伙伴关系和协议，同时确保主要交通功能的效率\n\n通过考虑这些情景、策略和潜在结果，交通机构可以为集成智能卡支付系统创建一个更稳健和适应性强的实施计划。这种深入分析有助于预测挑战、利用机会，最终增加新系统部署和采用的成功可能性。\n"]
}
}
{
"deepen_thought": {
"deep_thoughts": ["让我们深入探讨快速公交系统（BRT）的实施，考虑各种情景、策略、合作伙伴关系、资源和潜在障碍:\n\n1. 情景规划:\na) 最佳情景: BRT系统顺利实施，获得广泛公众支持。这显著减少了旅行时间，增加了乘车次数，并在走廊沿线引发了交通导向型开发。\nb) 中等情景: BRT系统面临初始反对，但逐渐获得认可。它改善了交通时间和服务的可靠性，但比预期时间更长才能达到乘车目标。\nc) 最糟情景: BRT系统面临强烈反对，实施过程中经历重大延迟，难以吸引乘客远离私人车辆。\n\n2. 实施策略:\na) 分阶段方法: 从试点走廊开始，展示效益并解决问题，然后再扩大网络。\nb) 全面重新设计: 将BRT系统作为更大的城市流动性计划的一部分实施，包括自行车道、人行道改善和交通导向型发展政策。\nc) 公共-私人合作伙伴关系: 与私营部门合作伙伴合作，为资金、运营和维护提供资金，以减少公共资源负担。\n\n3. 必要的合作伙伴关系和资源:\na) 政府机构: 交通部门、城市规划部门、环境机构、公共工程部门。\nb) 私营部门: 公交车制造商、智能交通系统提供商、建筑公司。\nc) 非营利组织和社区组织: 进行公共宣传和教育。\nd) 学术机构: 研究支持和影响研究。\ne) 国际组织: 技术支持和最佳实践（例如，ITDP、世界银行）。\n\n4. 克服障碍:\na) 公众抵抗: 实施全面的公众宣传活动，展示效益，通过虚拟现实模拟和访问成功BRT城市的实地考察。\nb) 资金挑战: 探索创新的融资机制，如价值捕获、碳信用，和公私合作。\nc) 技术问题: 建立一个由经验丰富的专业人员和国际顾问组成的专属项目管理办公室。\nd) 政治反对: 通过商业团体、环保组织和社区组织建立一个支持者联盟来倡导项目。\n\n5. 意外结果和缓解:\na) 沿BRT走廊的绅士化: 通过包容性规划政策和公共交通导向型开发中的经济适用房要求来缓解。\nb) 自动驾驶汽车的影响: 通过将BRT与新兴的移动出行技术整合，可能使用自动驾驶公交车或创建用于共享自动驾驶汽车的专用车道。\nc) 智能交通系统的网络安全威胁: 制定强大的安全协议和冗余系统，以保护免受潜在攻击或系统故障。\nd) 气候变化影响: 设计基础设施以抵御极端天气事件和温度升高。\n\n6. 长期可持续性:\na) 为持续维护和升级建立专门的资金流，可能通过车费收入的百分比或特别评估区。\nb) 建立持续改进计划，以适应城市需求和技术进步。\nc) 开展技能培训计划，确保系统操作和维护人员的稳定供应。\nd) 实施全面的数据收集和分析系统，以监测绩效并为未来改进提供信息。\n\n通过考虑这些更深层次的BRT实施方面，城市可以更好地准备挑战，利用机会，创建一个更有弹性和适应性的城市交通系统。这种方法增加了长期成功的可能性，并最大限度地提高了对城市流动性质量生活的积极影响。"]
}
}
{
"deepen_thought": {
"deep_thoughts": ["让我们深入探讨共享单车计划解决方案，考虑潜在情景、实施策略、合作伙伴关系、资源、障碍和意外结果:\n\n1. 潜在情景:\na) 快速采用: 计划迅速获得居民和游客认可，需要快速扩张和额外资金。\nb) 缓慢启动: 初始采用缓慢，需要增加营销努力和可能的价格或可访问性调整。\nc) 季节性波动: 在良好天气时使用量激增，在恶劣条件时下降，需要针对非高峰季节的适应策略。\nd) 技术整合成功: 该计划的应用成为智慧城市倡议的典范，与其他交通选择无缝衔接。\n\n2. 实施策略:\na) 分阶段推出: 从高流量地区开始试点项目，然后根据数据和反馈进行扩展。\nb) 公共-私人合作关系: 与有经验的共享单车运营商合作，利用他们的专业知识和科技。\nc) 社区参与: 在规划停车站位置时涉及当地社区，并持续收集反馈以进行改进。\nd) 与公共交通整合: 确保与其他现有公共交通无缝连接，实现最后一公里的可达性。\ne) 动态定价: 实施动态定价以鼓励平衡自行车分布和非高峰时段使用。\n\n3. 必要的合作伙伴关系和资源:\na) 地方政府: 为许可证、资金和与城市规划的整合。\nb) 自行车制造商: 供应和维护耐用、用户友好的自行车。\nc) 科技公司: 为开发和维护应用程序、支付系统和物联网整合。\nd) 城市规划师和交通工程师: 为安全自行车道和最佳停车站位置设计。\ne) 地方企业: 作为赞助商和潜在的停车站主机。\nf) 健康保险公司: 作为合作伙伴推广健康益处，提供用户激励。\n\n4. 克服潜在障碍:\na) 人为破坏/盗窃: 实施GPS跟踪，要求用户注册，设计防盗自行车和停车站。\nb) 安全顾虑: 提供免费的安全培训，分发头盔，并投资于保护自行车道。\nc) 分布不均: 使用激励措施（例如，将自行车归还到较少受欢迎的车站以获取信用）和雇用员工重新分配自行车。\nd) 天气问题: 设计防风雨的自行车，提供有遮盖的停车站，并在季节变化时提供折扣。\ne) 汽车用户反对: 发起关于效益的意识活动，逐步实施无车区以展示改善。\n\n5. 潜在意外结果和处理:\na) 过度饱和: 如果方案成功，可能导致自行车过剩。解决方案：实施严格的停车规定和动态卡数上限。\nb) 对当地自行车店的影响: 计划可能影响当地的自行车租赁业务。解决方案：与这些商店合作进行维护或提供角色。\nc) 数据隐私问题: 用户数据收集可能引发隐私问题。解决方案：实施强大的数据保护措施和透明政策。\nd) 微移动冲突: 增加的电动滑板车可能与计划竞争。解决方案：在同一个系统内整合多种微移动选项。\ne) 对公众的温和化担忧: 改善的自行车基础设施可能促进温和化。解决方案：确保站的公平分布和低成本选项。\n\n6. 长期可持续性策略:\na) 多样化: 扩展至包括电动自行车或与其他共享移动服务整合。\nb) 企业伙伴关系: 为员工福利计划开发B2B提供。\nc) 旅游合作: 为游客创建特殊通行证或游，与当地景点合作。\nd) 数据变现: 分析并出售匿名旅行模式数据给城市规划师和研究人员。\ne) 持续创新: 根据用户反馈和技术进步定期更新自行车设计和应用程序功能。\n\n通过考虑这些更深层次的方面，共享单车计划可以更好地为各种情景做好准备，增加长期成功和对城市流动性积极影响的可能性。\n"]
}
}
{
"rank_solutions": {
"ranked_solutions": [
{
"rank": 1,
"solution": "快速公交系统（BRT）",
"justification": "BRT系统提供了最全面和变革性的城市交通挑战解决方案。它有可能显著减少旅行时间，增加乘车次数，并激发交通导向型开发。详细的场景规划、实施策略和对长期可持续性的考虑使其成为一个稳健的解决方案。其与其他交通方式整合和适应未来技术的能力也使它具有优势。"
},
{
"rank": 2,
"solution": "集成智能卡支付系统",
"justification": "该解决方案解决了公共交通使用的效率和便利性方面的问题。它有可能简化各种交通方式的运营，改善用户体验，并为未来规划提供有价值的数据。分阶段实施方法和对潜在障碍的考虑使其成为一个实际且可行的解决方案。然而，它排名低于BRT系统，因为它没有直接解决容量和速度问题。"
},
{
"rank": 3,
"solution": "共享单车计划",
"justification": "虽然共享单车计划提供了环保和健康促进的替代方案，但可能在大规模通勤模式上影响有限，与其他解决方案相比。这是一个有价值的补充方案，但可能不适合所有用户或天气条件。详细的实施策略和合作伙伴关系考虑使它成为一个深思熟虑的解决方案，但其对城市拥堵的总体影响可能不如高排名选项那样显著。"
}
]
}
}`

AI 执行结果摘要

`输入： "改善大城市中的公共交通"
方面： "成本、效率、环境影响、用户体验"
1. 提出的解决方案：
a) 实施快速公交系统（BRT）
b) 发展全面的公共自行车计划
c) 引入一体化智能卡支付系统
2. 每个解决方案的评估：
a) 快速公交系统（BRT）
* 成功概率：75%
* 信心水平：80%
* 主要好处：成本效率、快速部署、高乘客容量、灵活性
* 主要挑战：道路空间重新分配、初始阻力、与铁路系统的吸引力
b) 公共自行车计划
* 成功概率：70%
* 信心水平：75%
* 主要好处：环保、减少拥堵、促进健康
* 主要挑战：高初始投资、维护成本、天气依赖性
c) 一体化智能卡支付系统
* 成功概率：75%
* 信心水平：80%
* 主要好处：改善便利性、加快交易、数据收集
* 主要挑战：高初始投资、技术复杂性、隐私担忧
3. 解决方案排名：
第一名：快速公交系统（BRT）
第二名：一体化智能卡支付系统
第三名：公共自行车计划
排名理由：快速公交系统被认为是最全面和最具变革性的解决方案，具有减少旅行时间、增加乘客人数和促进以公共交通为导向的发展的高潜力。`

**图表输出**

 `from IPython.display import Image # 显示图片对象 (display image object)
Image(app.get_graph().draw_mermaid_png()) # 获取并绘制mermaid图的PNG格式 (get and draw the mermaid diagram in PNG format)`

![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC "使用LangGraph实现Map-Reduce：构建灵活的并行处理分支_")

![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC "使用LangGraph实现Map-Reduce：构建灵活的并行处理分支_")

本文原创发布于慕课网 ，转载请注明出处，谢谢合作

若觉得本文不错，就分享一下吧！

共同学习，写下你的评论

评论加载中...

作者其他优质文章

![](https://img1.sycdn.imooc.com/545867790001599f02200220-100-100.jpg)

[摇曳的蔷薇](/u/6458227/articles "摇曳的蔷薇")

关注作者，订阅最新文章

### 阅读免费教程

![](https://img1.sycdn.imooc.com/wiki/5f0eb80e09807fcb00840084.jpg)

后端通用面试教程

41个小节
32784
370

![](https://img1.sycdn.imooc.com/wiki/60a75c5509e0659700840084.jpg)

网络编程入门教程

20个小节
13626
256

![](https://img1.sycdn.imooc.com/wiki/5ff3ca6e092c832100840084.jpg)

Pandas 入门教程

25个小节
20250
386

![]()
![]()

100积分直接送

付费专栏免费学

大额优惠券免费领

购课补贴  
联系客服咨询优惠详情

慕课网APP  
您的移动学习伙伴

扫描二维码  
关注慕课网微信公众号

举报