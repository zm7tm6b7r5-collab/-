# CLAUDE.md

> 本文件补充全局 `~/.claude/CLAUDE.md`，只放**本项目特有**的规则。
> 沟通风格、通用行为准则、软件环境等见全局配置。

---

## 文件地图

```
cc/  ($ 项目根目录)
│
├── 📋 考纲与资料
│   ├── 南大社会学考研参考书目与考纲.md    ← 权威考点清单（exam-review 读取）
│   └── 南大社会学考研参考书目与考纲.docx   ← 原始文档
│
├── 🐍 考研脚本
│   ├── kaoyan_daily.py                     ← 每日复习主脚本
│   ├── kaoyan_config.json / kaoyan_cache.json / kaoyan_history.json
│   ├── kaoyan_report_*.md                  ← 每日复习报告
│   ├── kaoyan_daily.log
│   └── kaoyan_selector/                    ← 选题模块
│
├── 📝 Prompt 库
│   └── prompts/                            ← scorer_prompt / analyzer_prompt / ...
│
├── 🍅 工具脚本
│   ├── pomodoro.py                         ← 番茄钟
│   ├── setup_task.ps1                      ← 一次性配置脚本
│   └── requirements.txt                    ← Python 依赖
│
├── 🗄️ 数据库作业
│   ├── 准备数据.sql / 全连接查询.sql / 多表联查作业.sql
│   └── 数据库原理期末大作业.md / .docx
│
├── ⚡ Electron 应用（CC-Switch）
│   ├── package.json / vite.config.js / index.html
│   ├── src/ / electron/ / dist-electron/
│   └── CC-Switch.msi
│
├── 🔌 Skills 源码
│   └── skills/                             ← find-skills 等（git submodule）
│
├── 🧹 临时文件（可忽略）
│   └── _*.txt                               ← _debug, _verify, _hw, _req 等共 11 个
│
├── 📎 其他
│   ├── feishu_auth_qr.png                  ← 飞书授权码
│   ├── movie.html                          ← 电影页面
│   ├── cc / .cc-connect/ / .claude/
│   └── 期末大作业 跨境(1).docx
│
└── 📖 Obsidian Vault（外部，非本目录）
    └── C:\Users\AUSU\Desktop\llmwiki       ← ~155 页社会学笔记
```

---

## 核心原则

| # | 原则 | 含义 |
|---|------|------|
| P1 | **学术优先** | 每个任务评估与考研目标和智库规划的关联度 |
| P2 | **Skill 优先** | 已有 Skill 能解决的问题，不重复造轮子 |
| P3 | **先读后写** | 操作任何文件前必须读取上下文 |
| P4 | **渐进推进** | 分批执行，每步确认，不跳步骤 |
| P5 | **来源可溯** | 每个论断标注来源，不编造不存在的文献或数据 |
| P6 | **不确定时多问** | 宁可多问一个澄清问题，不做错误假设 |
| P7 | **日志纪律** | vault 操作必修日志，项目决策必修 memory |

### 决策优先级

当多个原则冲突时：

```
1. 数据真实性（不编造） >
2. 用户确认（关键决策不代劳） >
3. 学术规范（格式/引用/论证标准） >
4. 效率（Skill 复用 > 从零写代码） >
5. 简洁（适度省略细节）
```

### Vault 协作红线

```
操作 Obsidian vault？
├── 只读？ → 直接操作
└── 要写？ → ① 先读 llmwiki/CLAUDE.md + wiki/index.md
            → ② 用规定的页面类型（entity/concept/topic/comparison/source）
            → ③ 遵守命名（lowercase-hyphens.md）
            → ④ 对齐 frontmatter（type/date_created/date_updated/tags/exam_weight/exam_types）
            → ⑤ 写完更新 index.md + log.md + 检查 Canvas 同步
```

---

## 研究规则

### 学术搜索策略

| 需求 | 工具链 | 优先级 |
|------|--------|--------|
| 中文核心期刊论文 | `cnki-search` → `cnki-advanced-search` → `cnki-paper-detail` | 第一 |
| 英文论文 | `read-arxiv-paper` / `deep-research` | 第二 |
| 深度议题研究 | `deep-research`（多源 + 引用报告） | 综合场景 |
| 结构化文献综述 | `literature-review`（STORM 多视角对话框架） | 综述场景 |
| 政策文件/政府报告 | `deep-research`（限定 gov.cn/UNDP/World Bank 域名） | 智库场景 |
| 微信文章 | `wechat-article-to-markdown` | 自媒体资料 |

### 信息来源可信度

| 等级 | 来源 | 用途 |
|------|------|------|
| **一级** ⭐⭐⭐⭐⭐ | CSSCI 核心期刊、政府统计年鉴、CGSS/CFPS 等大型调查 | 核心论据 |
| **二级** ⭐⭐⭐⭐ | 普通学术期刊、博士论文、权威出版社专著 | 补充论据 |
| **三级** ⭐⭐⭐ | 智库报告、国际组织报告、学术会议论文 | 背景与比较 |
| **四级** ⭐⭐ | 媒体报道、公众号、个人博客 | 仅作语境补充 |

### 文献管理

- 深度研究产出存入 vault（`wiki/sources/`）
- 关键文献标注：作者+年份+核心论点+方法+局限
- 引用格式：中文 GB/T 7714，英文 APA 第7版
- 不编造文献：所有引用必须来自实际检索结果

---

## 学术写作规范

### 社会学论文

- **段落结构：** 论点 → 论据（文献/数据） → 论证 → 小结
- **引言三要素：** 研究问题 + 文献缺口 + 本文结构
- **结论原则：** 结论 ≠ 摘要。回答"这意味着什么"，不逐章复述。

| ❌ 避免 | ✅ 使用 |
|--------|--------|
| 笔者认为 / 本文认为 | 本文发现 / 分析表明 |
| 很多 / 非常多 | 约 XX% / 显著 |
| 这个问题很重要 | 该问题影响约 XX 万人/涉及… |
| 可能 / 大概 | 数据显示 / 估计 / 约为 |

### 智库写作

> 智库写作规范（BLUF 原则、四要素建议、字数控制、模板）已整合到 `think-tank-training` Skill 的模式三。
> 调用 `think-tank-training` 时自动加载，无需在此重复。

---

## 知识管理

### 资料入库流程

```
新资料 → 结构化笔记（vault 模板）
       → 链接已有知识（entity/concept/comparison）
       → 更新 index.md + log.md
       → 评估是否做 Anki 卡片
```

### Anki 制卡

- 遵循 `flashcard-general.md` / `flashcard-math.md` 规则
- 三步流程：JSON 转储 → 用户审批 → 批量创建
- 统一牌组 `Learning`，用标签分类
- 新学概念当天制卡

### 复习节奏

- 每周日：检查 claude-mem-lite 记录的薄弱项
- 每月：用 `exam-review` 做一次真题模拟

---

## 代码规范

### 交付标准

每次交付 Python 脚本时附：

```
📦 交付清单
├── 脚本文件（.py）
├── 依赖清单（requirements.txt 更新）
├── 运行说明（安装 + 运行命令）
├── 输入/输出说明
└── 注意事项（已知限制、需手动操作的部分）
```

### 不做什么

| ❌ | 原因 |
|---|------|
| `git push --force` | 保护 git 历史 |
| 引入不必要的重依赖 | 优先标准库 |
| 创建用户看不懂的抽象 | 类/装饰器/元编程 |
| 悄悄修改已有脚本行为 | 先说明再改 |

---

## 自检与记录

### 产出前快速自检

- [ ] 事实有来源？（无来源标注"分析判断"）
- [ ] 数字精确？（不模糊化）
- [ ] 下一步明确？（用户读完知道该做什么）

### 记录规则

| 时机 | 动作 |
|------|------|
| 修复了非简单 bug | `mem_save(type="bugfix", lesson_learned="...")` |
| 做了架构/方向决策 | `mem_save(type="decision", lesson_learned="...")` |
| 修改了 vault 文件 | 更新 index.md + log.md |
| 会话结束有未完成事项 | `mem_defer` 或写入 memory |

---

## 附录 A：Skill 清单

> **动态查询优于手写维护。** 实际安装的 Skill 在 `~/.claude/skills/` 目录下。
> 要查看当前可用 Skill：`ls ~/.claude/skills/*/SKILL.md`

### 本项目高频 Skill

| Skill | 用途 | 调用方式 |
|-------|------|---------|
| `exam-review` | 考研 5 模式复习 | 说"抽测""真题模拟""查漏补缺"等 |
| `paper-writing-workflow` | 论文写作 6 步法 | 说"写论文""开题""文献综述"等 |
| `think-tank-training` | 智库研究 5 模式 | 说"智库""政策分析""政策简报"等 |

### 常用外部 Skill

| Skill | 关键词触发 |
|-------|-----------|
| `deep-research` | 深度研究、多源搜索 |
| `cnki-search` / `cnki-advanced-search` / `cnki-paper-detail` | 知网、中文论文 |
| `literature-review` | 文献综述 |
| `stata-skill` | Stata、定量分析 |
| `claude-mem-lite` | 跨会话记忆（自动注入） |

---

## 附录 B：当前状态

| 状态 | 事项 |
|------|------|
| ✅ | exam-review / paper-writing-workflow / think-tank-training 三个 Skill 搭建 |
| ✅ | Prompt Library 搭建 |
| ✅ | markitdown PDF 转换修复 |
| ⏳ | knowledge-gap-scanner 状态待确认 |
| ⏳ | vault 链接增强分析 |
