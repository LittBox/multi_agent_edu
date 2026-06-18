# 项目学习用户数据变量说明

本文档用于说明项目中前端展示的核心学习用户数据，重点包括：

- BKT：判断学生现在会不会某个知识点
- SM-2：判断这个知识点什么时候该复习
- 用户画像雷达图五个维度

---

## 1. 总体说明

项目中的学习用户数据主要分为两类：

| 模型               | 解决的问题               | 典型字段                                                                                                                     |
| ------------------ | ------------------------ | ---------------------------------------------------------------------------------------------------------------------------- |
| BKT 贝叶斯知识追踪 | 学生现在会不会某个知识点 | `mastery`, `attempts`, `correct_attempts`, `streak`, `confidence`, `status`                                      |
| SM-2 间隔重复算法  | 这个知识点什么时候该复习 | `ef`, `quality`, `interval_days`, `repetition`, `next_review_at`, `last_review_at`, `is_due`, `overdue_days` |

简单理解：

```txt
BKT：判断学生现在会不会
SM-2：判断知识点什么时候该复习
```

---

## 2. BKT：学生现在会不会

BKT 用来估计某个学生对某个知识点的当前掌握概率。它不是简单地看学生答对还是答错，而是综合考虑猜对、失误和练习后的学习转移。

核心思想：

- 学生答对了，不一定真的会，可能是猜对。
- 学生答错了，也不一定真的不会，可能是失误。
- 每次做题后，不管对错，都有可能学到一点东西。

---

## 2.1 mastery：单个知识点掌握概率

### 含义

`mastery` 表示系统认为这个学生当前掌握某个知识点的概率。

取值范围：

```txt
0 ~ 1
```

初始值：

```txt
mastery = 0.1
```

也就是说，一个新知识点默认从 10% 掌握概率开始。

示例：

```txt
mastery = 0.1   表示约 10% 掌握
mastery = 0.6   表示约 60% 掌握
mastery = 0.9   表示约 90% 掌握
```

---

## 2.2 BKT 四个核心参数

| 参数          | 含义                 | 默认值   |
| ------------- | -------------------- | -------- |
| `p_init`    | 初始掌握概率         | `0.1`  |
| `p_transit` | 每次练习后学会的概率 | `0.15` |
| `p_guess`   | 不会但猜对的概率     | `0.2`  |
| `p_slip`    | 会了但失误的概率     | `0.1`  |

---

## 2.3 mastery 答对时的计算公式

如果学生答对：

$$
P(L \mid correct)
=
\frac{
P(L) \times (1 - P(S))
}{
P(L) \times (1 - P(S)) + (1 - P(L)) \times P(G)
}
$$

然后加入学习转移：

$$
new\_mastery
=
P(L \mid correct) + \left(1 - P(L \mid correct)\right) \times P(T)
$$

其中：

| 符号               | 含义                                       |
| ------------------ | ------------------------------------------ |
| `P(L)`           | 当前 mastery，即学生已经掌握该知识点的概率 |
| `P(S)`           | slip，会了但失误的概率                     |
| `P(G)`           | guess，不会但猜对的概率                    |
| `P(T)`           | transit，每次练习后学会的概率              |
| `P(L \| correct)` | 在观察到学生答对后，系统重新估计的掌握概率 |
| `P(L \| wrong)`   | 在观察到学生答错后，系统重新估计的掌握概率 |

说明：

```txt
P(L) 中的 P 是 Probability。
P(L) 表示 Probability of Learned，也就是“已经掌握的概率”。
```

---

## 2.4 mastery 答错时的计算公式

如果学生答错：

$$
P(L \mid wrong)
=
\frac{
P(L) \times P(S)
}{
P(L) \times P(S) + (1 - P(L)) \times (1 - P(G))
}
$$

然后加入学习转移：

$$
new\_mastery
=
P(L \mid wrong) + \left(1 - P(L \mid wrong)\right) \times P(T)
$$

注意：

```txt
即使答错，mastery 也可能略微上升。
```

原因是模型认为学生虽然答错了，但做题过程本身也可能带来学习收益。

---

## 2.5 mastery 的作用

`mastery` 是项目中最核心的长期学习状态。

它会用于：

- 判断知识点是否薄弱
- 判断知识点是否已掌握
- 计算学科平均掌握度
- 生成用户画像雷达图
- 展示掌握度看板
- 决定学习报告里的掌握情况

---

## 2.6 attempts：累计尝试次数

### 含义

`attempts` 表示这个学生在这个知识点上总共提交过多少次答案。

注意：

```txt
它是按知识点统计，不是按某一道题统计。
```

初始值：

```txt
attempts = 0
```

每次调用 `update_mastery()` 后都会：

```txt
state.attempts += 1
```

### 作用

1. 判断这个知识点是不是已经开始学习：

$$
learning\_status =
\begin{cases}
 attempts = 0,  &未开始\\
 attempts > 0,&已练习过 
\end{cases}
$$

2. 配合 `correct_attempts` 计算正确率：

$$
accuracy = \frac{correct\_attempts}{attempts}
$$

3. 体现数据量。

一个知识点只练过 1 次和练过 20 次，可信度是不一样的。

---

## 2.7 correct_attempts：答对次数

### 含义

前端接口里叫：

```txt
correct_attempts
```

BKT 模型代码里叫：

```txt
correct_count
```

它表示这个学生在这个知识点上累计答对了多少次。

### 作用

1. 用来算传统正确率：

$$
accuracy = \frac{correct\_attempts}{attempts}
$$

示例：

```txt
attempts = 10
correct_attempts = 7
accuracy = 70%
```

2. 用来展示学习表现。

例如练习页掌握度看板里：

```txt
累计尝试：10
答对次数：7
```

3. 它是 BKT 的辅助统计。

注意：

```txt
correct_attempts / attempts 不等于 mastery。
```

正确率只是历史表现，`mastery` 是模型对真实掌握状态的估计。

---

## 2.8 streak：连续正确次数

### 含义

`streak` 表示这个学生在当前知识点上最近连续答对了多少次。

更新规则：

$$
\begin{cases}
 streak += 1,  &答对\\
 streak = 0,   &答错 
\end{cases}
$$

### 作用

用于辅助判断学习稳定性。

示例：

```txt
mastery = 0.75，streak = 1
```

说明学生掌握度还不错，但最近连续正确次数不多。

```txt
mastery = 0.75，streak = 5
```

说明学生最近在这个知识点上表现比较稳定。

---

## 2.9 confidence：置信度

### 含义

`confidence` 表示系统对当前 `mastery` 判断有多确信。

它不是学生掌握程度，而是模型对自己判断的把握程度。

### 计算公式

置信度公式：

$$
total = \alpha + \beta
$$

$$
confidence = \min\left(1, \frac{\alpha + \beta}{20}\right)
$$

每提交一次答案，`alpha` 和 `beta` 的更新规则为：

$$
(\alpha, \beta) =
\begin{cases}
(\alpha + 1, \beta), & \text{答对} \\
(\alpha, \beta + 1), & \text{答错}
\end{cases}
$$

其中：

| 符号           | 含义                                   |
| -------------- | -------------------------------------- |
| `alpha`      | 成功参数，可以理解为答对相关的累计证据 |
| `beta`       | 失败参数，可以理解为答错相关的累计证据 |
| `confidence` | 系统对当前 mastery 判断的确信程度      |

初始情况下：

$$
\alpha = 1,\quad \beta = 9
$$

### 作用

`confidence` 的意义是区分下面两种情况：

```txt
情况 A：
mastery = 0.8
attempts = 1
confidence 低

情况 B：
mastery = 0.8
attempts = 20
confidence 高
```

两者 `mastery` 都是 `0.8`，但含义不一样。

情况 A 说明：

```txt
学生可能掌握了，但数据太少，系统还不太确定。
```

情况 B 说明：

```txt
学生多次练习后仍保持较高掌握度，系统更确信他真的掌握了。
```

所以 `confidence` 可以用于：

- 控制推荐策略
- 决定是否继续出题验证
- 判断画像可信度
- 辅助老师理解数据是否充分

---

## 2.10 status：掌握状态

`status` 表示当前知识点的学习状态。

常见状态：

```txt
learning
mastered
```

一般理解：

```txt
learning：学习中
mastered：已掌握
```

---

## 3. SM-2：这个知识点什么时候该复习

SM-2 是间隔重复算法，用于决定某个知识点下次应该什么时候复习。

它主要回答：

```txt
这个知识点什么时候该复习？
```

---

## 3.1 ef / easiness_factor：难度因子

### 含义

`ef` 或 `easiness_factor` 表示这个知识点对当前学生来说有多容易记住。

值越大，说明越容易，之后复习间隔增长越快。

初始值：

```txt
easiness_factor = 2.5
```

范围限制：

```txt
1.3 <= EF <= 2.5
```

公式：

$$
EF_{n+1} = EF_n - 0.8 + 0.28q - 0.02q^2
$$

说明：

| 符号       | 含义                         |
| ---------- | ---------------------------- |
| `EF_{n+1}` | 更新前的难度因子             |
| `EF_n` | 更新后的难度因子             |
| `q`      | 本次回答质量，取值范围 0 ~ 5 |

---

## 3.2 quality：回答质量

`quality` 是回答质量，范围是：

```txt
0 ~ 5
```

含义：

| quality | 含义                     |
| ------- | ------------------------ |
| `5`   | 完美回答，毫不犹豫       |
| `4`   | 正确，但需要思考         |
| `3`   | 正确，但很困难           |
| `2`   | 错误，但看到答案觉得熟悉 |
| `1`   | 错误，看到答案才有印象   |
| `0`   | 完全不会                 |

---

## 3.3 interval_days：复习间隔天数

### 含义

`interval_days` 表示距离下一次复习间隔多少天。

示例：

```txt
interval_days = 1     明天复习
interval_days = 6     6 天后复习
interval_days = 15    15 天后复习
```

### 计算规则

第一次成功：

```txt
repetition == 0
interval_days = 1
```

第二次成功：

```txt
repetition == 1
interval_days = 6
```

第三次及以后，复习间隔计算公式为：

$$
interval\_days = previous\_interval\_days \times EF
$$

然后更新连续成功复习次数：

$$
repetition = repetition + 1
$$

如果中间某次质量低于 3：

```txt
repetition 清零
interval_days 回到 1
```

### 示例

假设每次质量都不错，EF 保持 `2.5`：

```txt
第 1 次成功：interval_days = 1
第 2 次成功：interval_days = 6
第 3 次成功：interval_days = 6 × 2.5 = 15
第 4 次成功：interval_days = 15 × 2.5 = 37.5
第 5 次成功：interval_days = 37.5 × 2.5 = 93.75
```

---

## 3.4 repetition：成功复习次数

### 含义

`repetition` 表示连续成功复习的次数。

注意：

```txt
它不是总复习次数。
```

更新规则：

$$
new\_repetition =
\begin{cases}
old\_repetition + 1, & quality \ge 3 \\
0, & quality < 3
\end{cases}
$$

---

## 3.5 next_review_at：下次复习时间

`next_review_at` 表示这个知识点下次应该复习的时间。

公式：

$$
next\_review\_at = current\_time + interval\_days
$$

---

## 3.6 last_review_at：上次复习时间

`last_review_at` 表示这个知识点上一次复习的时间。

每次调用 SM-2 review 时都会更新：

```ts
item.last_review = datetime.now()
```

作用：

- 展示上次复习时间
- 计算学习记录
- 判断复习历史
- 辅助生成学习报告

---

## 3.7 is_due：是否到期

`is_due` 表示当前是否已经到了该复习的时间。

前端复习排期会展示：

```txt
已到期 / 计划中
```

公式：

$$
is\_due =
\begin{cases}
 current\_time \ge next\_review\_at, & true\\
current\_time < next\_review\_at, &   false 
\end{cases}
$$

---

## 3.8 overdue_days：逾期天数

`overdue_days` 表示这个知识点已经逾期多少天。

公式：

$$
overdue\_days = \frac{current\_time - next\_review\_at}{86400}
$$

其中：

$$
86400 = 24 \times 60 \times 60
$$

`86400` 表示一天的秒数，用来把秒换算成天。

所以除以 `86400` 是为了把秒换算成天。

作用：

```txt
逾期越久，越优先复习。
```

---

## 4. 用户画像维度

用户画像维度分数都会被限制在 `0 - 100`，并且会四舍五入。

统一处理方式：

```txt
低于 0 变成 0
高于 100 变成 100
```

用户画像共有五个维度：

```txt
1. 知识掌握
2. 答题准确
3. 练习活跃
4. 学习稳定
5. 复习健康
```

---

## 4.1 知识掌握

### 含义

表示这个学生所有已跟踪知识点的平均掌握度。

作用：

```txt
回答这个学生整体知识掌握水平怎么样。
```

### 公式

$$
mastery\_score = avg\_mastery \times 100
$$

其中：

$$
avg\_mastery =
\frac{
\sum mastery
}{
tracked\_knowledge\_points
}
$$

---

## 4.2 答题准确

### 含义

表示这个学生历史答题正确率。

### 来源

```txt
answer_record.is_correct
```

### 计算逻辑

后端会根据 `user_id` 查询该用户所有 `AnswerRecord`。

```txt
total_answers = 当前用户所有答题记录数量
correct_answers = 当前用户答对的记录数量
```

### 公式

```txt
答题准确 score = 正确题数 / 总答题数 × 100
```

如果没有答题记录：

```txt
score = 0
```

### 示例

```txt
total_answers = 10
correct_answers = 7
```

那么：

```txt
答题准确 score = 7 / 10 × 100 = 70
```

---

## 4.3 练习活跃

### 含义

表示这个学生最近练得够不够多。

### 固定参数

```txt
window_days = 7
target_answers = 20
```

### 公式

```txt
练习活跃 score = 近 7 天答题数 / 20 × 100
```

上限为 `100`。

也就是说：

```txt
最近 7 天答够 20 题，就能拿满 100 分。
```

### 示例

最近 7 天答了 10 题：

```txt
score = 10 / 20 × 100 = 50
```

最近 7 天答了 30 题：

```txt
score = 30 / 20 × 100 = 150
clamp 后 = 100
```

---

## 4.4 学习稳定

### 含义

表示这个学生是不是持续稳定地学习。

### 公式

```txt
学习稳定 score = 近 7 天有答题记录的天数 / 7 × 100
```

也就是最近 7 天里，有多少天至少答过题。

### 示例

最近 7 天里，有 3 天答过题：

```txt
score = 3 / 7 × 100 ≈ 43
```

最近 7 天每天都有答题：

```txt
score = 7 / 7 × 100 = 100
```

注意：

```txt
学习稳定只看有没有持续学习，不看每天答了多少题。
```

例如：

```txt
学生 A：1 天答 20 题，其他 6 天不答
学生 B：7 天每天答 1 题
```

学习稳定分：

```txt
学生 A = 1 / 7 × 100 ≈ 14
学生 B = 7 / 7 × 100 = 100
```

---

## 4.5 复习健康

### 含义

表示这个学生有没有按时复习。

### 公式

```txt
复习健康 score = 100 - 逾期复习数 × 20 - 今日到期复习数 × 10
```

如果没有复习计划：

```txt
review_score = 0
```

说明：

```txt
没有复习计划时不是 100，而是 0。
这代表“暂无可评价的复习健康数据”，但前端会显示成 0 分。
```

### 示例

没有逾期，没有今日到期：

```txt
review_score = 100
```

1 个今日到期：

```txt
review_score = 100 - 1 × 10 = 90
```

2 个逾期，1 个今日到期：

```txt
review_score = 100 - 2 × 20 - 1 × 10 = 50
```

6 个逾期：

```txt
review_score = 100 - 6 × 20 = -20
clamp 后 = 0
```

---

## 5. 用户画像维度汇总表

| 维度     | key             | 来源                               | 公式                                  | 含义           |
| -------- | --------------- | ---------------------------------- | ------------------------------------- | -------------- |
| 知识掌握 | `mastery`     | `learner_state.mastery`          | 所有 mastery 平均值 × 100            | 整体掌握水平   |
| 答题准确 | `accuracy`    | `answer_record.is_correct`       | 正确题数 / 总答题数 × 100            | 历史答题正确率 |
| 练习活跃 | `activity`    | `answer_record.submitted_at`     | 近 7 天答题数 / 20 × 100             | 最近练习量     |
| 学习稳定 | `consistency` | `answer_record.submitted_at`     | 近 7 天有答题记录天数 / 7 × 100      | 学习连续性     |
| 复习健康 | `review`      | `review_schedule.next_review_at` | 100 - 逾期数 × 20 - 今日到期数 × 10 | 是否按时复习   |

---

## 6. 核心区别总结

### 6.1 正确率不等于掌握度

```txt
正确率 = correct_attempts / attempts
mastery = BKT 模型估计的掌握概率
```

正确率只表示历史做题表现。

`mastery` 表示系统估计学生是否真正掌握。

---

### 6.2 attempts 和 confidence 的区别

```txt
attempts = 练习次数
confidence = 系统对 mastery 判断的确信程度
```

练得越多，模型一般越有把握。

---

### 6.3 BKT 和 SM-2 的区别

```txt
BKT：学生现在会不会
SM-2：什么时候再复习
```

BKT 负责学习状态判断。

SM-2 负责复习节奏安排。

---

## 7. 一句话总结

项目中的学习数据可以这样理解：

```txt
学生每次答题都会留下 AnswerRecord。
BKT 根据答题结果更新 LearnerState，判断学生现在会不会。
SM-2 根据复习质量更新 ReviewSchedule，判断什么时候再复习。
ReportService 把这些数据聚合成学习报告。
前端个人中心只负责展示这些后端计算好的结果。
```
