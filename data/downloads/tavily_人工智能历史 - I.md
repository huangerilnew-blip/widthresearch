[Artificial Intelligence](https://www.ibm.com/cn-zh/think/artificial-intelligence)

# AI 的历史

## 作者

[Tim Mucci](https://www.ibm.com/think/author/tim-mucci.html) 

IBM Writer

人类自古以来就梦想着制造会思考的机器。民间故事中和历史上打造可编程设备的尝试反映了这种长期以来的雄心壮志，而虚构的故事充满了智能机器的可能性，设想着它们的优点和危险。也难怪当 OpenAI 发布第一个版本的 [GPT](https://www.ibm.com/cn-zh/think/topics/gpt)（Generative Pretrained Transformer，生成式预训练转换器）时，迅速获得了广泛关注，标志着向实现这一古老梦想迈出了重要一步。

GPT-3 是 [AI](https://www.ibm.com/cn-zh/topics/artificial-intelligence) 领域具有里程碑意义的时刻，因为它具有前所未有的规模，具有 1,750 亿个参数，这使其无需进行大量微调即可执行各种自然语言任务。该模型使用大数据进行训练，使其能够生成类似人类的文本并参与对话。它还能够进行小样本学习，显著提高了其泛用性，并在聊天机器人和虚拟助理等商业 AI 应用中表现出了实用性。

如今，AI 正逐渐融入日常生活的方方面面，从社交媒体到工作流程，随着技术的不断进步，其影响力也将持续增长。要了解这项技术的发展方向，首先要了解我们是如何走到今天的。以下是 AI 的主要发展历史：

## 20 世纪以前

Jonathan Swift 的奇幻小说《格列佛游记》提出了“引擎”的概念，这是一个大型机械装置，用于帮助学者产生新的想法、句子和书籍。

- Jonathan Swift 的《格列佛游记》(1726)

Swift 的讽刺作品预示了算法文本生成的概念，而现代 AI 已将这一概念变为现实。AI 模型可以根据底层算法将词语和想法组合在一起，从而生成连贯的文本，这与斯威夫特虚构的“引擎”所要做的事情类似。

### 1914 年

西班牙工程师 Leonardo Torres y Quevedo 在巴黎*世界博览会*上展示了第一台国际象棋机 *El Ajedrecista*。它使用电磁铁并且是完全自动化的。*El Ajedrecista* 自动下了一个简单的国际象棋残局，即王、车对王。机器一旦设置好就不需要人工干预，它会自主进行符合规则的国际象棋移动，如果人类对手下出了不合规则的招法，机器会发出信号指示错误。如果机器被置于获胜位置，它就能够可靠地将死人类对手。

一部名为《罗森的通用机器人》(R.U.R) 的戏剧在伦敦上演。这部由 Karel Čapek 创作的戏剧是英语中首次使用“机器人”一词。在捷克语中，“robota”一词与封建制度下农民从事的强制性或强迫性工作有关。该剧获得成功后，“机器人”一词迅速获得国际认可，并成为机械或人造人执行任务的标准术语。虽然 Čapek 笔下的机器人是有机的，但该词却与机械、人形机器联系在一起，被设计用来从事单调、无技能的劳动。

爱荷华州立大学物理和数学教授 John Vincent Atanasoff 和他的研究生 Clifford Berry 在爱荷华州立大学依靠 650 美元的资助，创造了 Atanasoff-Berry Computer (ABC)。ABC 计算机被认为是最早的数字电子计算机之一，也是美国计算机科学领域的里程碑。

虽然 ABC 从未充分运行或广泛使用，但它引入的几个关键概念将成为现代计算发展的基础。

与以前依赖十进制的计算设备不同，ABC 使用二进制（1 和 0）来表示数据，二进制成为此后计算机的标准。ABC 也是最早使用电子电路而不是机械或机电系统进行计算的计算机之一，因此计算得更快、更可靠。ABC 将数据存储（内存）与处理单元（逻辑运算）分开，现代计算机体系结构仍在遵循这一原则。它使用电容器存储数据，可处理多达 30 个联立方程。

ABC 采用大约 300 个真空电子管进行逻辑运行，使其比早期的机械计算器更快。尽管真空电子管体积庞大且容易出现故障，但它们是电子计算领域的一项关键发展。ABC 重量超过 700 磅，可以求解多达 29 个联立线性方程。

### 1943 年

Warren S. McCulloch 和 Walter Pitts 在 *Bulletin of Mathematical Biophysics* 上发表了《A Logical Calculus of the Ideas Immanent in Nervous Activity》。1这是神经科学和 AI 史上影响深远的著作之一。这篇论文奠定了大脑可以被理解为一个计算系统的思想基础，并引入了人工神经网络的概念，而人工神经网络现已成为现代 AI 的一项关键技术。这一思想启发了计算机系统，特别是通过[神经网络](https://www.ibm.com/cn-zh/topics/neural-networks)和[深度学习](https://www.ibm.com/cn-zh/topics/deep-learning)来模拟类似大脑的功能和过程。

### 1950

英国数学家 Alan Turing 的里程碑式论文《Computing Machinery and Intelligence》发表在 *Mind* 上。2这篇论文是 AI 领域的奠基性文章，探讨了“机器能思考吗？”这一问题。Turing 的方法为日后讨论会思考的机器的本质以及如何通过“模仿游戏”（即现在的图灵测试）来衡量其智能确立了基础。Turing 引入了一个思想实验，以避免直接回答“机器会思考吗？”；他是将这个问题重新表述为更具体、更可操作的形式：机器能否表现出与人类无异的智能行为？

图灵测试已成为 AI 的核心概念，这是通过评估机器令人信服地模仿人类对话和行为的能力来衡量机器智能的一种方法。

## 1950–1980

### 1951

Marvin Minsky 和 Dean Edmunds 构建了第一个人工神经网络。随机神经模拟强化计算器 (SNARC) 是模拟人脑学习过程的早期尝试，特别是通过[强化学习](https://www.ibm.com/cn-zh/topics/reinforcement-learning)。

SNARC 的设计目的是模拟老鼠在迷宫中的行为。其想法是让机器模仿动物通过奖惩进行学习的方式，即随时间推移根据反馈调整自己的行为。它是一台模拟计算机，使用 3,000 个真空电子管组成的网络和突触权重来模拟 40 个类似神经元的单元。

### 1952

数学家兼计算机科学家 Allen Newell 和政治学家 Herbert A. Simon 开发出了 Logic Theorist 和 General Problem Solve 等具有影响力的程序，这些程序是首批使用计算方法模拟人类解决问题能力的程序。

### 1955

“人工智能”一词最初出现在一份名为《A Proposal for the Dartmouth Summer Research Project on Artificial Intelligence》3的研讨会提案中，由达特茅斯学院的 John McCarthy、哈佛大学的 Marvin Minsky、IBM 的 Nathaniel Rochest 以及贝尔电话实验室的 Claude Shannon 共同提交。

一年后，即 1956 年 7 月和 8 月举行的这次研讨会被普遍认为是新兴 AI 领域的正式诞生之时。

### 1957 年

Frank Rosenblatt 是一位心理学家兼计算机科学家，他开发了 Perceptron，这是一种早期的人工神经网络，可以实现基于两层计算机学习网络的模式识别。Perceptron 引入了二元分类器的概念，二元分类器可通过学习[算法](https://www.ibm.com/cn-zh/topics/machine-learning-algorithms)调整其输入的权重，从而从数据中学习。虽然仅限于解决线性可分离问题，但它为未来神经网络和[机器学习](https://www.ibm.com/cn-zh/topics/machine-learning)的发展奠定了基础。

### 1958

John McCarthy 开发了编程语言 Lisp4，Lisp 是 LISt Processing 的缩写。Lisp 的诞生源于 McCarthy 在形式化算法和数理逻辑方面的工作，特别是受到他希望创建一种可以处理符号信息的编程语言的影响。Lisp 很快成为 AI 研究中最流行的编程语言。

### 1959

Arthur Samuel 率先提出了机器学习的概念，他开发了一个计算机程序，随着时间的推移，该程序在跳棋方面的性能不断提高。Samuel 证明，可以对计算机进行编程，使其遵循预定义的规则，并从经验中“学习”，最终比程序员下得更好。他的工作标志着向教机器通过经验不断进步的方向迈出了重要一步，并在此过程中创造了“机器学习”这一术语。

Oliver Selfridge 发表了他的论文“Pandemonium: A paradigm for learning”。5他的“魔都”模型提出了一种系统，在该系统中，各种“恶魔”（处理单元）共同识别模式。恶魔们竞相识别未经预编程的数据中的特征，模拟无监督学习。Selfridge 的模型是对模式识别的早期贡献，影响了机器视觉和 AI 的未来发展。

John McCarthy 在他的论文《具有常识的程序》中提出了"建议接受者"的概念。*6*该程序旨在通过处理形式逻辑中的句子来解决问题，为 AI 的推理奠定基础。McCarthy 设想的系统可以理解指令，利用常识性知识进行推理，并从经验中学习，其长远目标是开发出能像人类一样有效适应和学习的 AI。这一概念有助于形成早期的知识表示和自动推理研究。

### 1965

哲学家 Hubert Dreyfus 出版了*《*Alchemy and Artificial Intelligence》7，文章认为人类大脑的运作方式与计算机有着根本的不同。他预测，由于复制人类直觉和理解力方面的挑战，AI 的进步会受到限制。他的批评在引发关于 AI 的哲学和实践极限的辩论方面具有影响力。

I.J. Good 撰写了《Speculations Concerning the First Ultraintelligent Machine》8，其中有一个著名的断言：一旦创造了一台超智能机器，它就可以设计出更智能的系统，使自己成为人类的最后一项发明—只要它保持可控。他的想法预示着现代关于 AI 超级智能及其风险的讨论。

Joseph Weizenbaum 开发了 ELIZA9，这是一个通过响应自然语言输入来模仿人类对话的程序。尽管 Weizenbaum 打算展示人机交流的表面化，但他感到惊讶的是，有很多用户认为该程序有类似人类的情绪，这引发了有关 AI 和人类互动的伦理问题。

斯坦福大学的 Edward Feigenbaum、Bruce Buchanan、Joshua Lederberg 和 Carl Djerassi 开发了 DENDRAL。10这是第一个通过模拟假设生成来实现有机化学家决策过程自动化的专家系统。DENDRAL 的成功标志着 AI 的进步，展示了系统如何执行专业任务，甚至比人类专家更好。

### 1966

Shakey 于 20 世纪 60 年代末在 SRI 研发，是第一个能够对自己的行动进行推理的移动机器人，集感知、规划和解决问题于一身。11Marvin Minsky 在 1970 年《生活》杂志的一篇文章中预测，AI 将在三到八年内达到普通人的一般智能。Shakey 的成就标志着机器人和 AI 领域的一个里程碑，尽管 Minsky 雄心勃勃的时间表被证明过于乐观。

### 1969

Arthur Bryson 和 Yu-Chi Ho 介绍了一种优化多级动态系统的方法 - [反向传播](https://www.ibm.com/cn-zh/think/topics/backpropagation)。虽然该算法最初是为控制系统开发的，但在训练多层神经网络时却变得至关重要。。随着计算能力的进步，反向传播在 2000 和 2010 年代才开始崭露头角，从而促成了深度学习的兴起。

Marvin Minsky 和 Seymour Papert 出版了《*Perceptrons: An Introduction to Computational Geometry*》，*12*，该书批判性地分析了单层神经网络的局限性。他们的工作经常被指责为降低了人们对神经网络的兴趣。在 1988 年版中，他们认为，尽管到 20 世纪 60 年代中期，对感知机进行了大量实验，但由于缺乏理论理解，相关进展已经停滞。

### 1970

Terry Winograd 创建了 SHRDLU，这是一款开创性的自然语言理解程序。13SHRDLU 可以用简单的英语与用户交互，操作虚拟积木世界中的对象，这展示了计算机理解和响应复杂指令的潜力。这是[自然语言处理](https://www.ibm.com/cn-zh/topics/natural-language-processing)领域的一项早期成果，但其成功仅限于特定的高度结构化环境。SHRDLU 的功能凸显了实现更广泛的 AI 语言理解的前景和挑战。

### 1972 年

MYCIN 由斯坦福大学开发，是最早创建的专家系统之一，用于帮助医生诊断细菌感染和推荐抗生素治疗。14MYCIN 使用基于规则的方法模拟人类专家的决策过程，并为医疗 AI 系统的开发创建了一个平台。然而，由于伦理和法律问题，它从未在临床实践中实施。

### 1973

James Lighthill 向英国科学研究理事会提交了一份关于 AI 研究进展的关键报告，并得出 AI 未能兑现其早期承诺的结论。15 他认为，该领域尚未产生重大突破，导致英国政府大幅减少了对 AI 的资助。这份报告导致了第一个 AI 寒冬的爆发16，此时期人们对 AI 研究的兴趣和投资消减了。

## 1980–2000

### 1980

WABOT-217 是日本早稻田大学开发的仿人机器人，于 1980 年开始制造，1984 年左右完成。它是继 1973 年制造的 WABOT-1 之后的又一款机器人。WABOT-1 着重于基本的移动和交流，而 WABOT-2 则更为专业，专门设计为音乐家机器人。它可以用摄像"眼睛"阅读乐谱，与人类交谈，用电子风琴演奏音乐，甚至可以为人类歌手伴奏。该项目标志着仿人机器人和 AI 的发展迈出了有意义的一步，仿人机器人和 AI 能够执行复杂的、类似人类的任务，如艺术表达。

### 1982

日本启动了第五代计算机系统项目 (FGCS)，旨在开发能够进行逻辑推理和解决问题的计算机，推动 AI 研究的发展。这个雄心勃勃的项目旨在制造能够执行自然语言处理等任务的机器和专家系统。尽管该项目于 1992 年停止，但 FGCS 项目及其研究成果为并发逻辑编程领域的发展做出了巨大贡献。

### 1984 年

在人工智能发展协会 (AAAI) 年会上，Roger Schank 和 Marvin Minsky 对即将到来的“AI 之冬”发出警告。他们预测，对 AI 的过高期望很快就会导致投资和研究的崩溃，就像 20 世纪 70 年代中期资金减少一样。他们的预言在三年内变成现实，人们对 AI 的兴趣因未兑现承诺而减弱，导致资助减少，进展放缓。这一时期被称为第二次 AI 寒冬。

Schank 和 Minsky 的警告凸显了 AI 热潮的周期性质，当技术未能满足投资者和公众的预期时，迸发的乐观情绪之后是幻灭的寒冬。

### 1986

David Rumelhart、Geoffrey Hinton 和 Ronald Williams 发表了开创性的论文《Learning representations by back-propagating errors》，他们在论文中描述了反向传播算法。18这种方法允许神经网络通过“反向传播”误差来调整内部权重，提高了多层网络学习复杂模式的能力。反向传播算法成为现代深度学习的基础，重新激发了人们对神经网络的兴趣，并克服了早期 AI 研究中凸显的一些局限性。这一发现以 Arthur Bryson 和 Yu-Chi Ho 1969 年的研究成果为基础，将反向传播算法专门应用于神经网络，克服了以往多层网络训练中的一些局限性。

这一突破使人工神经网络的实际应用变得可行，并为 21 世纪前十年和 21 世纪 10 年代的深度学习革命打开了大门。

### 1987

在教育大会的主题演讲中，苹果公司 CEO John Sculley 展示了 Knowledge Navigator 视频，想象未来数字智能代理将帮助用户通过网络系统获取海量信息。19这个富有远见的概念描述了一位教授与一位知识渊博的声控助手互动的场景，这位助手可以检索数据、回答问题并显示我们现在所认识的互联网信息。这段视频预见了现代技术的许多要素，如 AI 助手、网络知识数据库和我们互联的数字世界。

### 1988

Judea Pearl 出版了《*Probabilistic Reasoning in Intelligent Systems*》，彻底改变了 AI 在不确定情况下处理信息的方式。*20*该工作引入了贝叶斯网络，一种表示复杂概率模型的形式主义，以及在其中执行推理的算法。Pearl 的方法使 AI 系统能够在不确定的环境中做出合理的决策，影响到 AI 以外的领域，包括工程和自然科学。他的贡献得到了 2011 年图灵奖的认可，该奖表彰了他在为 AI 中的现代概率推理创建“表示和计算基础”方面的作用。21

Rollo Carpenter 开发了 Jbberwacky22，这是一个早期的[聊天机器人](https://www.ibm.com/cn-zh/topics/chatbots)，旨在模拟像人类一般的有趣、娱乐性和有幽默感的对话。与基于规则的系统不同，Jbberwacky 从人类交互中学习以生成更自然的对话，为后来的会话式 AI 模型铺平了道路。该聊天机器人是创建通过从与用户的交互中不断学习来模仿自发的日常人类对话的首批 AI 尝试之一。

IBM T.J. Watson 研究中心的研究人员发表了《A Statistical Approach to Language Translation》，标志着机器翻译从基于规则的方法向概率方法的关键转变。23这种方法以 IBM 的 Candide 项目为例 24，使用了 220 万个英法句子对，主要来自加拿大议会的会议记录。这种新方法强调从数据中的统计模式中学习，而不是试图理解或“懂得”语言，这反映了依赖于分析已知示例的机器学习的更广泛趋势。这种概率模型为自然语言处理和机器翻译的许多未来进步铺平了道路。

Marvin Minsky 和 Seymour Papert 发布了他们 1969 年出版的《*Perceptrons*》一书的扩展版，这是对早期神经网络意义深远的批评。在题为“A View from 1988”的新序言中，他们反思了 AI 领域的缓慢进展，并指出由于不熟悉早期的挑战，许多研究人员继续重复过去的错误。12他们强调了对更深入理论理解的需求，这在早期的神经网络研究中是缺乏的。他们强调了最初的批评，同时认可了后来导致现代深度学习进步的新兴方法。

### 1989 年

Yann LeCun 和 AT&T 贝尔实验室的研究团队取得了突破性进展，成功地将反向传播算法应用于多层神经网络，以识别手写邮政编码图像。24这是利用[卷积神经网络](https://www.ibm.com/cn-zh/topics/convolutional-neural-networks)进行深度学习的首批实际应用之一。尽管当时的硬件条件有限，但神经网络的培训大约需要三天时间，与之前的尝试相比有了显著改进。该系统在手写数字识别（邮政服务自动化的一项关键任务）方面的成功，展示了神经网络在图像识别任务方面的潜力，并为深度学习在随后几十年的爆炸式增长奠定了基础。

### 1993

科幻小说作家兼数学家 Vernor Vinge 发表了题为《The Coming Technological Singularity》的文章，其中他预测超人的智慧将在未来30 年内诞生，从而从根本上改变人类文明。25Vinge 认为，技术进步，特别是 AI，将导致智能爆炸，机器将超越人类智能，并结束我们所知的人类时代。他的文章对于普及“技术奇点”这一概念发挥了重要作用，并引发了 AI、伦理和未来主义社区的讨论。

这一预测持续影响着有关 AI 和超级智能潜在影响的讨论，特别是创造远超人类能力的智能机器所带来的生存风险和伦理考量。

### 1995

Richard Wallace 在 Joseph Weizenbaum 的 ELIZA 计划基础上开发了聊天机器人 A.L.I.C.E.26（人工语言互联网计算机实体）。ELIZA 依靠脚本回复来模拟对话，与之不同的是，A.L.I.C.E. 利用新兴的万维网来收集和处理大量自然语言数据，使其能够进行更复杂、更流畅的对话。A.L.I.C.E. 使用一种名为 AIML（人工智能标记语言）的模式匹配技术来解析和生成回复，这使它比其前辈更具适应性和可扩展性。Wallace 的工作为会话式 AI 的进一步发展奠定了基础，对现代虚拟助手和聊天机器人产生了影响。

### 1997

Sepp Hochreiter 和 Jürgen Schmidhuber 推出了[长短期记忆](https://video.ibm.com/recorded/131507960) (LSTM)，这种[循环神经网络](https://www.ibm.com/cn-zh/topics/recurrent-neural-networks) (RNN) 旨在克服传统 RNN 的局限性，尤其是它们无法有效捕获数据中的长期依赖关系。LSTM 网络广泛用于手写识别、语音识别、自然语言处理和时间序列预测等应用。

IBM 的 Deep Blue 在六局制比赛中击败了卫冕的国际象棋世界冠军 Garry Kasparov，创造了历史。27这是计算机国际象棋程序首次在标准国际象棋比赛时间控制下击败世界冠军。Deep Blue 的胜利表明，计算机可以在高度战略性的游戏中胜过人类，长期以来，这被认为是人类智能的标志。这台机器每秒计算数百万步的能力，再加上博弈论和启发式的进步，使其能够战胜 Kasparov，巩固了 Deep Blue 在 AI 历史上的地位。

该事件还引发了关于人类认知与 AI 未来关系的讨论，影响了后续在自然语言处理、自主系统等其他领域的 AI 研究。

### 1998

Dave Hampton 和 Caleb Chung 创造了 Furby，这是第一款广受欢迎的家用机器人宠物。28Furby 可以响应触摸、声音和光，并随着时间的推移“学习”语言，从它的语言 Furbish 开始，但随着它与用户的互动，逐渐“说”更多的英语。它首次在消费产品中将机器人技术与娱乐相结合，而其模仿学习和与用户互动的能力使其成为更复杂的社交机器人的先驱。

Yann LeCun、Yoshua Bengio 和他们的合作者发表了关于神经网络在手写识别中应用的有影响力的论文。29他们的工作重点是使用卷积神经网络来优化反向传播算法，使其更有效地训练深度网络。通过改进反向传播过程并展示 CNN 在图像和模式识别方面的强大功能，LeCun 和 Bengio 的研究为当今广泛 AI 应用中使用的现代深度学习技术奠定了基础。

## 2000–2020

### 2000

麻省理工学院的 Cynthia Breazeal 开发了 Kismet，这是一款旨在通过情感和社交提示与人类互动的机器人。30Kismet 配备了摄像头、麦克风和富有表现力的面部特征，能够感知和响应人类的情绪，如快乐、悲伤和惊讶。这一发展标志着社交机器人技术的一大进步，探索了机器人如何更自然地与人类互动。

### 2006

Geoffrey Hinton 出版了《Learning Multiple Layers of Representation》一书，其中总结了深度学习的关键突破，并概述了如何更有效地训练多层神经网络。31Hinton 的工作重点是训练具有分级连接的网络，以生成感知数据，而不是简单地对其进行分类。这种方法代表从传统神经网络向我们现在所说的深度学习的转变，使机器能够学习数据的复杂分层表示。

### 2007

Fei-Fei Li 和她的团队在普林斯顿大学启动了 ImageNet 项目，创建了最大、最全面的注释图像数据库之一。32ImageNet 旨在通过提供涵盖数千个类别的数百万张标记图像来支持视觉对象识别软件的开发。该数据集的规模和质量推动了计算机视觉研究的进步，特别是在训练深度学习模型以识别和分类图像中的对象方面。

### 2009

Rajat Raina、Anand Madhavan 和 Andrew Ng 发表了"使用图形处理器的大规模深度无监督学习"一文，认为图形处理器 (GPU) 在深度学习任务中的性能远远超过传统的多核 CPU。33他们证明，GPU 的超强计算能力可以彻底改变深度无监督学习方法的适用性，使研究人员能够更高效地训练更广泛、更复杂的模型。这项工作对加速 GPU 在深度学习中的应用起到了重要作用，从而在 2010 年代取得了突破性进展，为计算机视觉和自然语言处理等领域的现代 AI 应用提供了动力。

西北大学智能信息实验室的计算机科学家开发了 Stats Monkey，该程序能在无需人工干预的情况下自动生成体育新闻报道。34利用比赛统计数据，Stats Monkey 可以制作关于棒球比赛的连贯叙述，包括回顾、球员表现和分析。

### 2011 年

IBM 的 Watson 是一款先进的自然语言问答计算机，因为参加游戏节目《Jeopardy！》，对阵该节目中最成功的两位冠军 Ken Jennings 和 Brad Rutter，并击败了他们成为头条新闻。35Watson 处理和解释自然语言的能力及其庞大的知识库使其能够快速准确地回答复杂的问题。这场胜利凸显了 AI 在复杂层面上理解人类语言和与人互动能力的进步。

Apple 推出集成到 iOS 操作系统中的虚拟助理 Siri。Siri 提供自然语言用户界面，允许用户通过语音命令与其设备交互。Siri 可以利用机器学习执行发送消息、设置提醒、提供建议和回答问题等任务，以适应每个用户的偏好和语音模式。这种个性化自适应的[语音识别](https://www.ibm.com/cn-zh/topics/speech-recognition)系统可为用户提供个性化体验，对于日常消费者来说，标志着人工智能驱动助手的可用性和可访问性方面实现了飞跃。

### 2012

Jeff Dean 和 Andrew Ng 利用大型神经网络以及源自 YouTube 视频的 1,000 万张未标记图像进行了一项实验。36在实验期间，神经网络在没有事先标记的情况下学习识别数据中的模式，其间“令我们感到有趣的是”，一个神经元变得对猫的图像特别敏感。这一发现是无监督学习的证明，展示了深度神经网络如何从海量数据中自主学习特征。

多伦多大学的研究人员在 Geoffrey Hinton 的带领下，设计了一种卷积神经网络，在 ImageNet 大规模视觉识别挑战赛中取得了突破性的结果。37他们的卷积神经网络（即 AlexNet）实现了 16% 的错误率，比前一年 25% 的最佳结果有了大幅提升。这一成果标志着计算机视觉领域深度学习的转折点，证明在大型数据集上进行训练时，卷积神经网络可以超越传统的图像分类方法。

### 2016 年

Google DeepMind 的 AlphaGo 击败了世界顶级围棋选手之一李世石。围棋是一种复杂的棋盘游戏，其可能的招法比宇宙中的原子还多；长期以来，围棋一直被认为是对 AI 的一个挑战。38AlphaGo 4–1 战胜李世石是 AI 领域的一个开创性时刻，展示了深度学习技术的强大，足以处理以前超出 AI 能力的高度复杂的战略任务。

Hanson Robotics 推出了一款非常先进的仿人机器人 -Sophia。39Sophia 可以通过图像识别和自然语言处理相结合的方式识别人脸、进行眼神交流并进行对话。

### 2017

Facebook 人工智能研究 (FAIR) 实验室的研究人员训练两个聊天机器人相互谈判。虽然聊天机器人被编程为用英语进行交流，但在它们的对话过程中，它们开始摆脱结构化的人类语言，创建了自己的速记语言，以便更有效地进行交流。40这种发展出乎意料，因为机器人可以在没有人工干预的情况下优化交流。为了让机器人使用人类能理解的语言，实验曾暂停，但这一事件凸显了 AI 系统自主和不可预测地演化的潜力。

### 2020

OpenAI 推出 GPT-3，这是一种拥有 1,750 亿个参数的语言模型，使其成为迄今为止最大、最复杂的 AI 模型之一。GPT-3 展示了生成类似人类撰写文本、进行对话、编写代码、翻译语言和基于自然语言提示进行创意写作的能力。作为[大型语言模型](https://www.ibm.com/cn-zh/topics/large-language-models) (LLM) 最早的范例之一，GPT 庞大的尺寸和规模使其能够执行各种语言任务，几乎不需要进行特定任务的训练。此示例展示了 AI 在理解和生成高度连贯语言方面的潜力。

DeepMind 的 AlphaFold 2 通过氨基酸序列准确预测了蛋白质的三维结构，在生物学领域取得了突破性进展。这一成果解决了困扰科学家数十年的难题，即了解蛋白质如何折叠成其独特的三维形状。AlphaFold 2 在蛋白质结构预测方面的高准确性对疾病研究和药物开发具有重要意义，为了解疾病背后的分子机制和更有效地设计新型疗法提供了新途径。

## 2021-至今

### 2021

MUM（多任务统一模型）是由 Google 开发的一种强大的 AI 模型，旨在通过理解和生成 75 种语言来改善搜索体验。MUM 可以执行多项任务，同时分析文本、图像和视频，从而处理更复杂、更细致的搜索查询。41与传统模型不同，MUM 可以处理多模态输入，并为涉及多个信息源的复杂问题提供全面、上下文丰富的答案。

Tesla 推出全自动驾驶 (FSD) Beta 版，这是一种旨在实现完全自动驾驶的高级驾驶辅助系统。FSD Beta 利用深度学习和神经网络实现复杂驾驶场景的导航，例如实时城市街道、高速公路和十字路口。它允许 Tesla 车辆在特定条件下自动转向、加速和制动，同时需要驾驶员的监督。Tesla 的 FSD Beta 版标志着该公司朝着全自动驾驶汽车的目标迈出了一步，尽管在实现自动驾驶技术广泛部署的路途上仍存在监管挑战和安全问题。

### 2021–2023

OpenAI 推出 DAL-E，随后推出 DAL-E 2 和 DAL-E 3，此系列[生成式 AI](https://www.ibm.com/cn-zh/topics/generative-ai) 模型能够从文本描述生成非常详细的图像。这些模型使用先进的深度学习和转换器架构，根据用户输入创建复杂、逼真和艺术化的图像。DAL-E 2 和 3 扩展了 AI 在视觉内容创建中的使用，允许用户在没有传统图形设计技能的情况下将想法转化为图像。

### 2024

2 月

Google 推出有限 beta 版的 Gemini 1.5，这是一种高级语言模型，能够处理长达 1 百万个词元的上下文长度。42该模型可以处理和理解单次提示中的大量信息，提高了在复杂对话和任务中针对较长文本维护上下文的能力。Gemini 1.5 针对长输入提供了增强的记忆功能和上下文理解，代表了自然语言处理领域的显著飞跃。

OpenAI 公开发布 Sora，这是一种文本转视频模型，能够根据文本描述生成长达一分钟的视频。43这项创新将 AI 生成内容的用途扩展到静态图像之外，使用户能够根据提示创建详细的动态视频片段。Sora 有望为视频内容创作开辟新的可能性。

StabilityAI 宣布推出最新的文本转图像模型 Stable Diffusion 3。与 Sora 一样，Stable Diffusion 3 使用类似的架构，从文本提示生成详细的创意内容。44

5 月

Google DeepMind 推出 AlphaFold 的新扩展，有助于识别癌症和遗传病，为遗传诊断和个性化医疗提供了强大的工具。45

IBM 推出 [Granite](https://www.ibm.com/cn-zh/granite) 系列生成式 AI 模型，作为其 [watsonx](https://www.ibm.com/cn-zh/watsonx) 平台的一部分。Granite 模型包含 30 亿至 340 亿个参数，专为代码生成、时间序列预测和文档处理等任务而设计。这些模型是开源的，可在 Apache 2.0 许可证下使用，属于轻量级模型，经济高效且可定制，是各种业务应用程序的理想选择。

6 月

Apple 宣布推出 Apple Intelligence，它可将 ChatGPT 整合至全新 iPhone 和 Siri。46这种整合使 Siri 能够执行更复杂的任务，进行更自然的对话，更好地理解和执行精细的命令。

9 月

NotebookLM 引入了 DeepDive，这是一种新型多模态 AI，能够将源资料转换为播客结构的引人入胜的音频演示。47DeepDive 能够分析和汇总来自不同格式（包括网页、文本、音频和视频）的信息，从而为跨各种平台创建个性化和自动化内容开辟了新的机会。此功能使其成为媒体制作和教育的全能工具。

[当前的 AI 趋势](https://www.ibm.com/cn-zh/think/insights/artificial-intelligence-trends)表明，生成式 AI 将会以更小、更高效的基础模型为基础，并会出现代理式 AI，其中特定 AI 模型协同工作以更快地完成用户请求。[更远的未来](https://www.ibm.com/cn-zh/think/insights/artificial-intelligence-future)，自动驾驶汽车将在高速公路上行驶，多模态 AI 将在单一平台上创建音频、视频、文本和图像，AI 助手将帮助用户规划个人生活和职业生涯。

1. [A logical calculus of the ideas immanent in nervous activity](https://link.springer.com/article/10.1007/BF02478259)，springer.com，1943 年 12 月
2. [Computing machinery and intelligence](https://academic.oup.com/mind/article/LIX/236/433/986238)，*Mind*，1950 年 10 月
3. [A proposal for the Dartmouth summer research project on artificial intelligence](https://www-formal.stanford.edu/jmc/history/dartmouth/dartmouth.html)，Stanford.edu，1955 年 8 月 31 日
4. [Lisp (progamming language)](https://en.wikipedia.org/wiki/Lisp_(programming_language))，wikipedia.org
5. [Pandemonium: a paradigm for learning](https://aitopics.org/download/classics:504E1BAC)，aitopics.org
6. [Programs with common sense](https://www-formal.stanford.edu/jmc/mcc59.pdf)，stanford.edu
7. [Alchemy and artifical intelligence](https://www.rand.org/content/dam/rand/pubs/papers/2006/P3244.pdf)，rand.org，1965 年 12 月
8. [Speculations concerning the first ultraintelligent machine](https://www.sciencedirect.com/science/article/abs/pii/S0065245808604180)，sciencedirect.com
9. [ELIZA](https://en.wikipedia.org/wiki/ELIZA)，wikipedia.org
10. [Dendral](https://en.wikipedia.org/wiki/Dendral)，wikipedia.org
11. [Shakey the robot](https://www.sri.com/hoi/shakey-the-robot/)，sri.com
12. [Perceptrons: an introduction to computational geometry](https://direct.mit.edu/books/monograph/3132/PerceptronsAn-Introduction-to-Computational)，MIT.edu
13. [SHRDLU](https://hci.stanford.edu/winograd/shrdlu/)，stanford.edu
14. [MYCIN: a knowledge-based program for infectious disease diagnosis](https://www.sciencedirect.com/science/article/abs/pii/S0020737378800492)，science.direct.com
15. [Artificial Intelligence: a general survey](https://www.chilton-computing.org.uk/inf/literature/reports/lighthill_report/p001.htm)，chilton-computing.org.uk，1972 年 7 月
16. [AI winter](https://en.wikipedia.org/wiki/AI_winter)，wikipedia.org
17. [WABOT](https://www.humanoid.waseda.ac.jp/booklet/kato_2.html)，humanoid.waseda.ac.jp
18. [Learning representations by back-propagating errors](https://www.nature.com/articles/323533a0)，nature.com，1986 年 10 月 9 日
19. [Knowledge navigator](https://www.youtube.com/watch?v=QRH8eimU_20)，youtube.com，2008 年 4 月 29 日
20. [Probabilistic reasoning in intelligent systems: networks of plausible inference](https://www.sciencedirect.com/book/9780080514895/probabilistic-reasoning-in-intelligent-systems)，sciencedirect.com，1988 年
21. [Judea Pearl Turing Award](https://amturing.acm.org/award_winners/pearl_2658896.cfm)，amturing.amc.org
22. [Jabberwacky](https://en.wikipedia.org/wiki/Jabberwacky)，wikipedia.org
23. [A statistical approach to language translation](https://dl.acm.org/doi/10.3115/991635.991651)，acm.org，1988 年 8 月 22 日
24. [Candide: a statistical machine translation system](https://aclanthology.org/H94-1100.pdf)，aclanthology.org
25. [The coming technological singularity: how to survive in the post-human era](https://edoras.sdsu.edu/~vinge/misc/singularity.html)，edoras.sdsu.edu，1993
26. [A.L.I.C.E. (Artificial Linguistic Internet Computer Entity)](https://en.wikipedia.org/wiki/Artificial_Linguistic_Internet_Computer_Entity)，wikipedia.org
27. [Deep blue (chess computer)](https://en.wikipedia.org/wiki/Deep_Blue_(chess_computer))，wikipedia.org
28. [Furby](https://en.wikipedia.org/wiki/Furby)，wikipedia.org
29. [Gradient-based learning applied to document recognition](http://vision.stanford.edu/cs598_spring07/papers/Lecun98.pdf)，Stanford.edu，1998 年 11 月
30. [Kismet](https://web.media.mit.edu/~cynthiab/research/robots/kismet/overview/overview.html)，mit.edu
31. [Learning multiple layers of representation](https://www.cs.toronto.edu/~hinton/absps/tics.pdf)，toronto.edu
32. [ImageNet](https://en.wikipedia.org/wiki/ImageNet)，wikipedia.org
33. [Large-scale deep unsupervised learning using graphic processors](https://robotics.stanford.edu/~ang/papers/icml09-LargeScaleUnsupervisedDeepLearningGPU.pdf)，stanford.edu
34. [The robots are coming! Oh, they're here](https://archive.nytimes.com/mediadecoder.blogs.nytimes.com/2009/10/19/the-robots-are-coming-oh-theyre-here/?_r=0)，nytimes.com，2009 年 10 月 19 日
35. [Watson IBM invitational](https://www.jeopardy.com/jbuzz/news-events/watson-ibm-invitational)，jeopardy.com，2015 年 6 月 22 日
36. [Using large-scale brain simulations for machine learning and A.I.，](https://blog.google/technology/ai/using-large-scale-brain-simulations-for/)blog.google，2012 年 6 月 26 日
37. [ImageNet large scale visual recognition challenge 2012](https://image-net.org/challenges/LSVRC/2012/)，image-net.org
38. [AlphaGo](https://en.wikipedia.org/wiki/AlphaGo)，wikipedia.org
39. [We talked to Sophia](https://www.youtube.com/watch?v=78-1MlkxyqI)，youtube.com，2017 年 12 月 28 日
40. [Facebook's artificial intelligence robots shut down after they start talking to each other in their own language](https://www.independent.co.uk/life-style/facebook-artificial-intelligence-ai-chatbot-new-language-research-openai-google-a7869706.html)，independent.co.uk，2017 年 7 月 31 日
41. [How will Google MUM affect your search ranking in 2024?](https://learn.g2.com/google-mum)，learn.g2.com，2023 年 8 月 7 日
42. [Our next-generation model: Gemini 1.5](https://blog.google/technology/ai/google-gemini-next-generation-model-february-2024/)，blog.google，2024 年 2 月 15 日
43. [Sora](https://openai.com/index/sora/)，openai.com
44. [Stable diffusion 3](https://stability.ai/news/stable-diffusion-3)，stability.ai，2024 年 2 月 22 日
45. [AlphaFold 3 predicts the structure and interactions of all of life’s molecules](https://blog.google/technology/ai/google-deepmind-isomorphic-alphafold-3-ai-model/)，blog.google，2024 年 5 月 8 日
46. [Apple intelligence](https://www.apple.com/newsroom/2024/06/introducing-apple-intelligence-for-iphone-ipad-and-mac/)，apple.com，2024 年 6 月 10 日
47. [NotebookLM now lets you listen to a conversation about your sources](https://blog.google/technology/ai/notebooklm-audio-overviews/)，blog.google，2024 年 9 月 11 日

[博客   AI 的未来：塑造未来 10 年的趋势 

深入了解 AI 的未来，到 2034 年，创新将如何重塑行业。深入了解 AI 在社会中不断演变的角色、其技术进步以及将影响其对决策和自动化的影响的道德考虑。](https://www.ibm.com/cn-zh/think/insights/artificial-intelligence-future)

## Think 时事通讯

来自 Think 的最新 AI 和技术洞察

 [立即注册](https://www.ibm.com/cn-zh/forms/news-mkt-52954)

相关解决方案    [watsonx.ai 中的基础模型 

深入了解 watsonx 组合中基础模型库，从容自信地为您的业务扩展生成式 AI

 深入了解 watsonx.ai](https://www.ibm.com/cn-zh/products/watsonx-ai/foundation-models)   [IBM Maximo Visual Inspection 

IBM Maximo Visual Inspection 是一个无代码计算机视觉平台，旨在实现视觉检查流程自动化。深入了解资源、自助演示、产品导览和解决方案简介。

 了解 IBM Maximo Visual Inspection](https://www.ibm.com/cn-zh/products/maximo/visual-inspection)   [人工智能 (AI) 咨询服务 

IBM® Consulting 正在与全球客户和合作伙伴展开合作，共同开创 AI 的未来。我们由 20,000 多名 AI 专家组成的多元化全球团队可帮助您在整个企业中快速、从容地设计并扩展尖端的 AI 解决方案和自动化功能。​

 深入了解 IBM AI 咨询服务](https://www.ibm.com/cn-zh/consulting/artificial-intelligence)

## 资源

  

IBM AI Academy

AI 教育

 

 


如何使用预处理来优化 Watson Visual Recognition 结果

 


AI 的未来是开放的

博客

使用面向 AI 构建器的新一代企业级开发平台 IBM watsonx.ai，可以训练、验证、调整和部署生成式 AI、基础模型和机器学习功能。使用一小部分数据，即可在很短的时间内构建 AI 应用程序。

    [深入了解 watsonx.ai](https://www.ibm.com/cn-zh/products/watsonx-ai)   [预约实时演示](https://www.ibm.com/cn-zh/forms/mkt-demo-dataaiwatsonxai)