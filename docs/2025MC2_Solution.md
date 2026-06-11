# Entry 名称：COOTEFOO 经济监督委员会偏见调查

**VAST Challenge 2025 · Mini-Challenge 2**

---

**团队成员：**

曾昭祥2312190219

张贤文 2312190210

钱易 2402100132

**使用的工具：** HTML、CSS、JavaScript、Vue 3、TypeScript、D3.js、Python、Pinia、Vite

**大约总共花了多少小时来完成这次提交？**

116小时

**在 2025 年 VAST Challenge 完成后，我们可以将您的提交内容发布在视觉分析基准存储库中吗？** 

是

---

## 问题与挑战

数十年来，Oceanus 一直享有相对简单、以渔业为基础的经济。近年来旅游业大幅扩张，带来显著变化。当地政府设立监督委员会——**Commission on Overseeing the Economic Future of Oceanus（COOTEFOO，海洋国经济未来监督委员会）**——监测当前经济并就为未来做准备提供建议。记者 Edwina Darling Moray 获得三份 COOTEFOO 委员会知识图谱数据集：**FILAH**（渔业方）、**TROUT**（旅游方）与 **journalist**（记者全量基准）。渔业方指控委员会偏袒旅游，旅游方指控委员会偏袒渔业。我们的任务是在视觉分析支持下，帮助 Moray 判断这些指控是否成立、委员会真实行为如何、子集与全量结论有何差异，并对具体委员做深度对比。

具体问题：

1. 基于 TROUT 与 FILAH 提供的数据集，用视觉分析判断各方指控是否被**其自身记录集**所支持。即：开发可视化，突出 TROUT 与 FILAH 数据集中的偏见（若存在）。在任一数据集中，COOTEFOO 成员行为是否有偏见证据？
2. 作为记者，Moray 希望更完整地了解 COOTEFOO 的行动与活动。她已将 TROUT、FILAH 的数据与补充记录合并为单一知识图谱。为该合并知识图谱设计视觉分析方法，查看 COOTEFOO 成员如何分配时间。**委员会整体是否偏袒？** 为结论提供视觉证据。
3. TROUT 与 FILAH 数据集不完整。用可视化对比：分别从 TROUT、FILAH 数据集得出的结论，与**全量数据集**中的行为相比如何？在全量背景下，TROUT 的指控是被加强、削弱还是不变？
4. 设计可视化，使 Moray 可选择一人，突出该人在不同数据集中行为的差异，聚焦各数据集讲述的故事对比。
   1. 至少选择一名被 TROUT 指控的 COOTEFOO 成员，说明使用更完整数据集后，对其活动的理解如何变化。
   2. 原 TROUT 数据中最影响判断变化的关键缺失证据是什么？
   3. 在全量数据背景下，FILAH 数据集的采样偏见对谁的行为影响最大？
   4. 在全量数据集背景下，展示 FILAH 数据的偏见。

---

## 分析指标说明（读图前提）

系统在 Python 后端将知识图谱预处理为前端指标，采用以下定义：

**偏差指数 bias_index**（基于委员 `participant` 边，仅统计 fishing / tourism 议题）：

```
bias_index = (旅游活动数 − 渔业活动数) ÷ (旅游活动数 + 渔业活动数)
```

| 取值 | 含义 |
|------|------|
| **+1** | 完全偏旅游 |
| **0** | 渔业/旅游均衡 |
| **−1** | 完全偏渔业 |

**活动覆盖率 coverage**：

```
coverage(成员, D) = 该成员在数据集 D 中的活动数 ÷ 该成员在记者数据集中的活动数
```

**情感均值 sentiment_mean**：取自 `participant` 边的 `sentiment` 字段，范围 [−1, 1]，在热图中以红蓝发散色阶呈现。

---

## 系统概况

<table width="100%" cellspacing="6" cellpadding="0" style="border:none; margin:0 auto;">
<tr>
<td colspan="3" style="border:none; padding:4px 0 2px; font-size:12px; color:#64748b; text-align:left;"><b>第一行 · 偏见全景</b></td>
</tr>
<tr>
<td width="50%" align="center" style="border:none; vertical-align:top;">
<img src="C:\Users\22965\AppData\Roaming\Typora\typora-user-images\image-20260611103833329.png" style="width:100%; max-width:520px; height:auto;" />
</td>
<td width="50%" align="center" style="border:none; vertical-align:top;">
<img src="C:\Users\22965\AppData\Roaming\Typora\typora-user-images\image-20260611103905739.png" style="width:100%; max-width:520px; height:auto;" />
</td>
</tr>
<tr>
<td colspan="3" style="border:none; padding:10px 0 2px; font-size:12px; color:#64748b; text-align:left;"><b>第二行 · 委员行为</b></td>
</tr>
<tr>
<td width="33%" align="center" style="border:none; vertical-align:top;">
<img src="C:\Users\22965\AppData\Roaming\Typora\typora-user-images\image-20260611103943994.png" style="width:100%; max-width:340px; height:auto;" />
</td>
<td width="34%" align="center" style="border:none; vertical-align:top;">
<img src="C:\Users\22965\AppData\Roaming\Typora\typora-user-images\image-20260611104020874.png" style="width:100%; max-width:340px; height:auto;" />
</td>
<td width="33%" align="center" style="border:none; vertical-align:top;">
<img src="C:\Users\22965\AppData\Roaming\Typora\typora-user-images\image-20260611104046107.png" style="width:100%; max-width:340px; height:auto;" />
</td>
</tr>
<tr>
<td colspan="3" style="border:none; padding:10px 0 2px; font-size:12px; color:#64748b; text-align:left;"><b>第三行 · 行程地图</b></td>
</tr>
<tr>
<td width="50%" align="center" style="border:none; vertical-align:top;">
<img src="C:\Users\22965\AppData\Roaming\Typora\typora-user-images\image-20260611104747615.png" style="width:100%; max-width:520px; height:auto;" />
</td>
<td width="50%" align="center" style="border:none; vertical-align:top;">
<img src="C:\Users\22965\AppData\Roaming\Typora\typora-user-images\image-20260611104825742.png" style="width:100%; max-width:520px; height:auto;" />
</td>
</tr>
</table>
我们的可视化应用程序采用**左侧导航 + 右侧主视图**布局，包含三个相互补充的分析模块，对应「宏观偏见 → 个体行为 → 时空证据」三层调查逻辑：

| 模块 | 核心图表 | 主要用途 |
|------|----------|----------|
| **偏见全景** | KPI 指标卡、采样偏见指数对比、数据集关键指标对比、话题行业构成、FILAH/TROUT 缺失节点分布 | 回答 Q1、Q3；展示数据集规模与结构性偏见 |
| **委员行为** | 委员偏见定位散点图、活动量平行坐标、活动覆盖率矩阵、情感倾向热图、跨数据集活动对比、关系网络（Ego） | 回答 Q2、Q4；支持点击成员联动下钻 |
| **行程地图** | Oceanus 官方地图、行程时间轴（含证据一致性图例）、行程区域分布、各成员行程数量 | 回答 Q1、Q2、Q3；提供时空与落点证据 |

**交互设计要点：**

- 委员行为页支持**点击成员行/散点/平行坐标线条**联动选中，右侧展开「跨数据集活动」与「关系网络」。
- 情感热图支持 FILAH / TROUT / 记者三标签切换，对比同一成员在不同材料中的「有值 / 缺失」。
- 行程地图支持三数据集筛选芯片、成员下拉筛选；记者模式下时间轴以绿点深浅标注**多方证实 / 单方验证 / 仅记者有**。
- 各图表标题旁集成 **TermExplanation** 术语悬浮说明，降低 Moray 等非图谱专家的理解门槛。

---

## MC2.1（Q1）：各方指控是否被其自身数据集支持？

基于 TROUT 与 FILAH 提供的数据集，用视觉分析判断各方指控是否被其自身记录集所支持；开发可视化突出两库偏见（若存在）。COOTEFOO 成员行为在任一数据集中是否有偏见证据？

![image-20260611110615858](C:\Users\22965\AppData\Roaming\Typora\typora-user-images\image-20260611110615858.png)

![image-20260611110709016](C:\Users\22965\AppData\Roaming\Typora\typora-user-images\image-20260611110709016.png)

![image-20260611110845739](C:\Users\22965\AppData\Roaming\Typora\typora-user-images\image-20260611110845739.png)

仅使用 FILAH 与 TROUT 时，**双方指控均只能得到有限支持，且两份数据集均存在严重结构性采样偏见**。

FILAH（渔业方，指控委员会偏旅游）：396 节点、189 条行程，但**仅覆盖 6 名委员中的 3 人**（Seal、Simone Kat、Carol Limpet），副主席 Ed Helpsford、财务 Teddy Goldstein、委员 Tante Titan 完全缺席。整体 `bias_index = +0.220`，participant 活动中渔游各 56 次，议题维度接近均衡，但行程落点高度集中在商业区与旅游区，**方向上部分支持**偏旅游叙事，却无法代表**委员会整体**。

TROUT（旅游方，指控委员会偏渔业）：人员 6/6 齐全，但行程仅 **18 条**（不足记者全量 5.3%），`bias_index = −0.046`，渔业议题 45、旅游 37，**仅有微弱支持**「偏渔业」；叙事高度依赖政府区会议，大量实地行为被省略。

**结论：** FILAH「漏人、堆行程」，TROUT「全员、极薄记录」——任一数据集都不能单独作为公正证据。

---

## MC2.2（Q2）：委员会整体是否偏袒？成员行为有何差异？

 为合并知识图谱设计视觉分析，查看 COOTEFOO 成员如何分配时间。委员会整体是否偏袒？请为结论提供视觉证据。

![image-20260611111319437](C:\Users\22965\AppData\Roaming\Typora\typora-user-images\image-20260611111319437.png)

![image-20260611111657411](C:\Users\22965\AppData\Roaming\Typora\typora-user-images\image-20260611111657411.png)

以记者全量（journalist）为基准，委员会在议题参与维度上整体 `bias_index = +0.297`（旅游 participant 120 次、渔业 81 次），呈**轻度偏旅游**，反映经济重心转移，不等同于集体蓄意偏袒。

**成员分化显著：** Simone Kat、Carol Limpet 旅游情感极高；Teddy Goldstein 相对亲渔业；主席 Seal 接近中立。平行坐标与覆盖率矩阵显示子集对个体画像扭曲极大（如 Kat 在 FILAH 覆盖率 100%、TROUT 仅 8%），**整体结论须以全量为准**。

行程时间轴与区域分布表明：全量行为以政府区落点最多，并向商业、旅游区域辐射；切换 FILAH/TROUT 后，不同成员行出现系统性空白。

**结论：** 委员会整体轻度偏旅游，但并非铁板一块，须分成员叙述。

---

## MC2.3（Q3）：子集结论在全量背景下如何变化？

对比 FILAH / TROUT 子集与全量行为。在全量背景下，TROUT 的指控是被加强、削弱还是不变？

![image-20260611114325738](C:\Users\22965\AppData\Roaming\Typora\typora-user-images\image-20260611114325738.png)

![image-20260611114200294](C:\Users\22965\AppData\Roaming\Typora\typora-user-images\image-20260611114200294.png)



![image-20260611114411902](C:\Users\22965\AppData\Roaming\Typora\typora-user-images\image-20260611114411902.png)

![image-20260611114425991](C:\Users\22965\AppData\Roaming\Typora\typora-user-images\image-20260611114425991.png)

![image-20260611114438575](C:\Users\22965\AppData\Roaming\Typora\typora-user-images\image-20260611114438575.png)

子集与全量落差悬殊：TROUT 行程 18 → 全量 342；FILAH 行程 189 但仅 3/6 成员有记录。会议数（12–13 vs 16）接近，**差距主要在行程与活动覆盖**。

覆盖率矩阵：Kat/Limpet 在 FILAH 为 100%、TROUT 为 3%–8%；Helpsford、Goldstein、Titan 在 FILAH 为 **0%**。

议题维度：仅 TROUT 时 bias **−0.046**，全量时 **+0.297**。TROUT 保留政府区会议、删除大量旅游实地 trip 与 participant 边。

**结论：** 在全量背景下，TROUT「委员会偏袒渔业」的指控被**显著削弱**（方向反转），而非加强。FILAH「偏旅游」与全量方向一致，但因漏掉 3 名委员全部活动，不能支撑对委员会整体的指控。

**需截取的系统截图：**

| 图号 | 截图内容 | 操作说明 |
|------|----------|----------|
| 图 10 | 数据集关键指标对比 + 采样偏见指数对比 | 「偏见全景」· 第二行两图（同 Q1 图 3）；可圈注行程柱差异 |
| 图 11 | 活动覆盖率矩阵 | 「委员行为」· 覆盖率表，六人百分比数字清晰 |
| 图 12 | 时间轴三数据集对比 | 「行程地图」· 仅 FILAH / 仅 TROUT / 三库全开各截一张或拼三联图 |
| 图 13 | TROUT 行程区域分布 | 「行程地图」· 仅选 TROUT · 左下区域分布图 |

---

## MC2.4（Q4）：个人深度分析

设计可视化，使 Moray 可选择一人，突出该人在不同数据集中的行为差异，聚焦各数据集讲述的故事对比。

### 4.a 至少选择一名被 TROUT 指控相关的委员：全量数据如何改变对其活动的理解？

以 **Tante Titan** 为例（TROUT 数据集中有记录、且在全量下画像反差极大）。

![image-20260611112810865](C:\Users\22965\AppData\Roaming\Typora\typora-user-images\image-20260611112810865.png)

![image-20260611112526847](C:\Users\22965\AppData\Roaming\Typora\typora-user-images\image-20260611112526847.png)

| 数据集 | 参与 | 行程 | 会议 | 话题 | 合计 |
|--------|------|------|------|------|------|
| FILAH | 0 | 0 | 0 | 0 | **0** |
| TROUT | 0 | 4 | 0 | 0 | **4** |
| 记者 | 54 | 49 | 11 | 32 | **103** |

TROUT 将其呈现为**边缘人物**（仅 4 条行程）；记者全量显示其为**高活跃委员**（103 条活动），`bias_index ≈ +0.72`，明显偏旅游。从「偶尔露面」变为「深度参与旅游议题与实地考察的核心成员」。

---

### 4.b 原 TROUT 数据中最影响判断变化的关键缺失证据是什么？

![image-20260611113129938](C:\Users\22965\AppData\Roaming\Typora\typora-user-images\image-20260611113129938.png)

![image-20260611113151747](C:\Users\22965\AppData\Roaming\Typora\typora-user-images\image-20260611113151747.png)

Titan 全量 103 条活动中，约 **96%** 未出现在 TROUT。最改变判断的不是单一数值，而是两类被系统性删除的证据：

1. **实地 trip 链**：全量 49 条行程在 TROUT 中几乎全灭，使 Moray 无法看到其考察码头扩建、遗产步行等旅游项目的实地行为。
2. **旅游议题 participant 边**：全量 54 条参与记录在 TROUT 中缺失，议题层面的「偏旅游」立场无法被还原。

![image-20260611113329183](C:\Users\22965\AppData\Roaming\Typora\typora-user-images\image-20260611113329183.png)

TROUT 仅保留少量政府区会议语境，足以维持「此人存在」，却不足以支撑对其真实角色与立场的任何判断。

---

### 4.c 在全量背景下，FILAH 采样偏见对谁的行为影响最大？

![image-20260611113546897](C:\Users\22965\AppData\Roaming\Typora\typora-user-images\image-20260611113546897.png)

活动覆盖率矩阵显示，**Ed Helpsford、Teddy Goldstein、Tante Titan** 三人在 FILAH 中覆盖率均为 **0%**——在渔业方叙事中「完全不存在」。

| 成员 | FILAH 覆盖率 | 记者全量活动数 | 说明 |
|------|-------------|---------------|------|
| Ed Helpsford | **0%** | 81 | 副主席，程序上最具代表性的成员之一 |
| Teddy Goldstein | **0%** | — | 全量相对亲渔业，纳入 FILAH 会削弱指控 |
| Tante Titan | **0%** | 103 | 全量最高活跃之一，反差最极端 |

![image-20260611113630196](C:\Users\22965\AppData\Roaming\Typora\typora-user-images\image-20260611113630196.png)

其中 **Titan** 全量 103 条 vs FILAH 零记录，数值反差最大；**Helpsford** 身份最关键（副主席零记录对「委员会整体」叙事破坏力最强）。

---

### 4.d 在全量数据集背景下，展示 FILAH 数据的偏见

![image-20260611113721440](C:\Users\22965\AppData\Roaming\Typora\typora-user-images\image-20260611113721440.png)

FILAH 相对记者全量缺失 **344** 个节点。「偏见全景 · FILAH 缺失节点分布」显示：旅游类议题节点缺失（43）多于渔业类（16），并非均匀随机缺失。与此同时，FILAH 对 Simone Kat、Carol Limpet 保持 **100%** 覆盖率并堆砌高行程，对 Helpsford 等三人零覆盖——存在**漏人 + 堆行程 + 选择性保留亲己方证人**嫌疑，而非完整委员会记录。

![image-20260611113942085](C:\Users\22965\AppData\Roaming\Typora\typora-user-images\image-20260611113942085.png)

![image-20260611113954822](C:\Users\22965\AppData\Roaming\Typora\typora-user-images\image-20260611113954822.png)

![image-20260611114028122](C:\Users\22965\AppData\Roaming\Typora\typora-user-images\image-20260611114028122.png)

情感热图三标签对比（以 Simone Kat 为例）进一步显示：FILAH 保留其完整情感画像，而 TROUT 侧大量格子为「—」，说明双方均在按叙事裁剪边集。

---

## 综合结论

| 问题 | 结论 |
|------|-----------|
| **Q1** | FILAH 部分支持「偏旅游」，TROUT 弱支持「偏渔业」；双方材料均不能单独采信 |
| **Q2** | 全量整体轻度偏旅游，成员立场分化显著 |
| **Q3** | 全量削弱 TROUT「偏渔业」叙事；FILAH 漏人使「委员会全体」结论失效 |
| **Q4** | Titan、Helpsford 等在子集中被严重失真；FILAH 对三人零覆盖是最大采样问题 |

**给 Moray 的建议：**

1. 以 **journalist 全量**为唯一裁决基准，FILAH/TROUT 仅作利益方声称对照。  
2. 报道须标注：FILAH 缺 3 名委员全部记录；TROUT 缺 94% 以上行程证据。  
3. 分成员叙述，避免「委员会 = 某一极端委员」。  
