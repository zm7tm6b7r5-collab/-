const pptxgen = require("pptxgenjs");

const pres = new pptxgen();
pres.layout = "LAYOUT_16x9";
pres.author = "习概小组";
pres.title = "中国特色大国外交和推动构建人类命运共同体";

// ============================================================
// 党政风格配色
// ============================================================
const RED      = "C41E3A";   // 中国红
const DARK_RED = "8B1A2B";   // 深红
const GOLD     = "D4A843";   // 金色
const LIGHT_GOLD = "FFF3D4"; // 浅金底色
const WHITE    = "FFFFFF";
const OFF_WHITE = "FFF8F0";  // 暖白
const DARK     = "2D2D2D";   // 深色文字
const GRAY     = "666666";   // 灰色文字
const CREAM    = "FFF5E6";   // 奶油底色

// ============================================================
// 辅助函数
// ============================================================
function addRedBanner(slide, title, subtitle) {
  // 顶部红色横幅
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 10, h: 1.35,
    fill: { color: RED }
  });
  // 金色装饰线
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 1.35, w: 10, h: 0.04,
    fill: { color: GOLD }
  });
  // 标题
  slide.addText(title, {
    x: 0.8, y: 0.2, w: 8.4, h: 0.7,
    fontSize: 30, fontFace: "Microsoft YaHei",
    color: WHITE, bold: true, margin: 0
  });
  if (subtitle) {
    slide.addText(subtitle, {
      x: 0.8, y: 0.8, w: 8.4, h: 0.4,
      fontSize: 14, fontFace: "Microsoft YaHei",
      color: GOLD, margin: 0
    });
  }
  // 底部红色细线
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 5.35, w: 10, h: 0.03,
    fill: { color: RED }
  });
  // 底部页码区
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 5.38, w: 10, h: 0.245,
    fill: { color: RED }
  });
}

function addPageNumber(slide, num) {
  slide.addText(String(num), {
    x: 8.8, y: 5.38, w: 1, h: 0.245,
    fontSize: 10, fontFace: "Microsoft YaHei",
    color: WHITE, align: "right", margin: 0
  });
}

function addFooterText(slide, text) {
  slide.addText(text, {
    x: 0.5, y: 5.38, w: 5, h: 0.245,
    fontSize: 9, fontFace: "Microsoft YaHei",
    color: OFF_WHITE, margin: 0
  });
}

// 金边内容卡片
function addCard(slide, x, y, w, h) {
  slide.addShape(pres.shapes.RECTANGLE, {
    x, y, w, h,
    fill: { color: WHITE },
    shadow: { type: "outer", blur: 4, offset: 2, angle: 135, color: "000000", opacity: 0.1 }
  });
  // 左侧金色竖线
  slide.addShape(pres.shapes.RECTANGLE, {
    x, y, w: 0.06, h,
    fill: { color: GOLD }
  });
}

// 红色全屏背景（标题页、分隔页用）
function redSlide(slide) {
  slide.background = { color: RED };
}

// ============================================================
// 第1页：封面
// ============================================================
const s1 = pres.addSlide();
redSlide(s1);

// 顶部金色装饰带
s1.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 0, w: 10, h: 0.08,
  fill: { color: GOLD }
});
// 底部金色装饰带
s1.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 5.545, w: 10, h: 0.08,
  fill: { color: GOLD }
});

// 中心主标题区
s1.addShape(pres.shapes.RECTANGLE, {
  x: 1.2, y: 1.0, w: 7.6, h: 3.6,
  fill: { color: DARK_RED },
  shadow: { type: "outer", blur: 8, offset: 3, angle: 135, color: "000000", opacity: 0.25 }
});

// 金色细框
s1.addShape(pres.shapes.RECTANGLE, {
  x: 1.35, y: 1.15, w: 7.3, h: 3.3,
  fill: { color: "000000", transparency: 100 },
  line: { color: GOLD, width: 1.5 }
});

// 主标题
s1.addText("中国特色大国外交\n和推动构建人类命运共同体", {
  x: 1.6, y: 1.5, w: 6.8, h: 1.8,
  fontSize: 32, fontFace: "SimHei",
  color: GOLD, bold: true, align: "center", valign: "middle",
  lineSpacingMultiple: 1.5
});

// 副标题
s1.addText("—— 习近平新时代中国特色社会主义思想概论 · 第十六章", {
  x: 1.6, y: 3.2, w: 6.8, h: 0.5,
  fontSize: 16, fontFace: "Microsoft YaHei",
  color: OFF_WHITE, align: "center", margin: 0
});

// 底部信息
s1.addText("习概课程小组汇报", {
  x: 1.6, y: 4.0, w: 6.8, h: 0.35,
  fontSize: 13, fontFace: "Microsoft YaHei",
  color: GOLD, align: "center", margin: 0
});

// ============================================================
// 第2页：新闻引入
// ============================================================
const s2 = pres.addSlide();
s2.background = { color: CREAM };
addRedBanner(s2, "📰 新闻引入", '中孟宣布构建“新时代中孟命运共同体”');
addPageNumber(s2, 2);
addFooterText(s2, "习概第16章 · 中国特色大国外交");

// 新闻卡片
addCard(s2, 0.6, 1.7, 4.2, 3.2);

s2.addText("新闻事实", {
  x: 0.9, y: 1.85, w: 3.6, h: 0.4,
  fontSize: 18, fontFace: "Microsoft YaHei",
  color: RED, bold: true, margin: 0
});

s2.addText([
  { text: "2026年6月26日", options: { bold: true, breakLine: true, fontSize: 14, color: DARK } },
  { text: "", options: { breakLine: true, fontSize: 8 } },
  { text: "国家主席习近平在北京人民大会堂会见来华正式访问的孟加拉国总理塔里克。", options: { breakLine: true, fontSize: 13, color: DARK } },
  { text: "", options: { breakLine: true, fontSize: 8 } },
  { text: "两国领导人共同宣布：构建\"新时代中孟命运共同体\"。", options: { bold: true, fontSize: 13, color: RED } },
  { text: "", options: { breakLine: true, fontSize: 8 } },
  { text: "——来源：新华社", options: { fontSize: 10, color: GRAY, italic: true } }
], {
  x: 0.9, y: 2.3, w: 3.6, h: 2.4,
  fontFace: "Microsoft YaHei", valign: "top", margin: 0
});

// 右侧：插入新闻照片
s2.addImage({
  path: "C:/Users/AUSU/Desktop/习近平会见孟加拉国总理塔里克_01.jpg",
  x: 5.25, y: 1.7, w: 4.2, h: 3.2,
  sizing: { type: "contain", w: 4.2, h: 3.2 }
});
// 金色细边框
s2.addShape(pres.shapes.RECTANGLE, {
  x: 5.25, y: 1.7, w: 4.2, h: 3.2,
  fill: { color: "000000", transparency: 100 },
  line: { color: GOLD, width: 2 }
});
// 照片说明
s2.addText("新华社记者 李响 摄", {
  x: 5.25, y: 4.82, w: 4.2, h: 0.2,
  fontSize: 9, fontFace: "Microsoft YaHei",
  color: GRAY, align: "center", margin: 0
});

// ============================================================
// 第3页：新闻解读
// ============================================================
const s3 = pres.addSlide();
s3.background = { color: CREAM };
addRedBanner(s3, "🔍 新闻解读", "这个事件释放了什么信号？");
addPageNumber(s3, 3);
addFooterText(s3, "习概第16章 · 中国特色大国外交");

// 四个要点卡片 2x2
const cards3 = [
  { t: "01", h: "朋友圈持续扩大", d: "中国外交从大国关系到全球南方齐头并进，南亚成为命运共同体建设的新热点" },
  { t: "02", h: "合作不断升级", d: "从\"一带一路\"经贸合作升级为\"命运共同体\"，体现合作深度与战略互信的质变" },
  { t: "03", h: "全球南方崛起", d: "孟加拉国等发展中国家在国际秩序中争取更多话语权，中国坚定站在全球南方一边" },
  { t: "04", h: "大国担当彰显", d: "中国以构建人类命运共同体为目标，为世界提供中国方案、贡献中国智慧" }
];

cards3.forEach((c, i) => {
  const col = i % 2;
  const row = Math.floor(i / 2);
  const cx = 0.6 + col * 4.6;
  const cy = 1.7 + row * 1.75;

  addCard(s3, cx, cy, 4.2, 1.45);

  // 编号圆圈
  s3.addShape(pres.shapes.OVAL, {
    x: cx + 0.25, y: cy + 0.25, w: 0.5, h: 0.5,
    fill: { color: RED }
  });
  s3.addText(c.t, {
    x: cx + 0.25, y: cy + 0.25, w: 0.5, h: 0.5,
    fontSize: 16, fontFace: "Microsoft YaHei",
    color: WHITE, bold: true, align: "center", valign: "middle", margin: 0
  });

  s3.addText(c.h, {
    x: cx + 0.95, y: cy + 0.15, w: 3.0, h: 0.45,
    fontSize: 16, fontFace: "Microsoft YaHei",
    color: RED, bold: true, margin: 0
  });
  s3.addText(c.d, {
    x: cx + 0.95, y: cy + 0.6, w: 3.0, h: 0.7,
    fontSize: 11, fontFace: "Microsoft YaHei",
    color: DARK, margin: 0
  });
});

// ============================================================
// 第4页：第16章整体框架
// ============================================================
const s4 = pres.addSlide();
redSlide(s4);

s4.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 0, w: 10, h: 0.06,
  fill: { color: GOLD }
});
s4.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 5.565, w: 10, h: 0.06,
  fill: { color: GOLD }
});

s4.addText("第十六章 · 内容框架", {
  x: 0.8, y: 0.4, w: 8.4, h: 0.7,
  fontSize: 28, fontFace: "SimHei",
  color: GOLD, bold: true, align: "center", margin: 0
});

// 三节卡片横向排列
const sections4 = [
  { num: "第一节", title: "新时代中国外交\n在大变局中开创新局", items: "百年未有之大变局\n中国特色大国外交\n国际影响力显著提升" },
  { num: "第二节", title: "全面推进\n中国特色大国外交", items: "和平发展道路\n新型国际关系\n维护国家利益 · 外交为民" },
  { num: "第三节", title: "推动构建\n人类命运共同体", items: "人类命运共同体内涵\n全球治理体系改革\n高质量共建一带一路" }
];

sections4.forEach((sec, i) => {
  const sx = 0.5 + i * 3.15;

  s4.addShape(pres.shapes.RECTANGLE, {
    x: sx, y: 1.5, w: 2.85, h: 3.6,
    fill: { color: DARK_RED }
  });
  s4.addShape(pres.shapes.RECTANGLE, {
    x: sx + 0.08, y: 1.58, w: 2.69, h: 3.44,
    fill: { color: "000000", transparency: 100 },
    line: { color: GOLD, width: 1 }
  });

  s4.addText(sec.num, {
    x: sx, y: 1.6, w: 2.85, h: 0.45,
    fontSize: 14, fontFace: "Microsoft YaHei",
    color: GOLD, align: "center", margin: 0
  });
  s4.addText(sec.title, {
    x: sx + 0.25, y: 2.1, w: 2.35, h: 1.0,
    fontSize: 16, fontFace: "SimHei",
    color: WHITE, bold: true, align: "center", valign: "middle",
    lineSpacingMultiple: 1.3, margin: 0
  });
  s4.addShape(pres.shapes.RECTANGLE, {
    x: sx + 0.6, y: 3.15, w: 1.65, h: 0.02,
    fill: { color: GOLD }
  });
  s4.addText(sec.items, {
    x: sx + 0.25, y: 3.3, w: 2.35, h: 1.6,
    fontSize: 12, fontFace: "Microsoft YaHei",
    color: OFF_WHITE, align: "center", valign: "middle",
    lineSpacingMultiple: 1.5, margin: 0
  });
});

// 底部引导问题
s4.addText("核心问题：中国需要什么样的外交？中国能为世界做什么？", {
  x: 0.8, y: 5.25, w: 8.4, h: 0.3,
  fontSize: 11, fontFace: "Microsoft YaHei",
  color: LIGHT_GOLD, align: "center", italic: true, margin: 0
});

// ============================================================
// 第5页：第一节
// ============================================================
const s5 = pres.addSlide();
s5.background = { color: CREAM };
addRedBanner(s5, "第一节 · 新时代中国外交在大变局中开创新局", "当今世界正经历百年未有之大变局");
addPageNumber(s5, 5);
addFooterText(s5, "习概第16章 · 中国特色大国外交");

// 三列要点
const points5 = [
  {
    icon: "🌍",
    title: "百年未有之大变局",
    body: "国际力量对比深刻调整，新兴市场国家和发展中国家群体性崛起。全球治理体系面临深刻变革，和平与发展仍是时代主题。"
  },
  {
    icon: "🇨🇳",
    title: "中国特色大国外交",
    body: "坚持独立自主的和平外交政策，不走\"国强必霸\"的老路。在对外交往中坚持正确义利观，讲信义、重情义、扬正义、树道义。"
  },
  {
    icon: "📈",
    title: "影响力显著提升",
    body: "从\"韬光养晦\"到\"积极作为\"，我国国际影响力、感召力、塑造力显著提升。为世界和平与发展作出更大贡献。"
  }
];

points5.forEach((p, i) => {
  const px = 0.5 + i * 3.15;

  addCard(s5, px, 1.7, 2.85, 2.35);

  s5.addText(p.icon, {
    x: px, y: 1.8, w: 2.85, h: 0.45,
    fontSize: 28, align: "center", margin: 0
  });
  s5.addText(p.title, {
    x: px + 0.3, y: 2.25, w: 2.25, h: 0.4,
    fontSize: 15, fontFace: "SimHei",
    color: RED, bold: true, align: "center", margin: 0
  });
  s5.addShape(pres.shapes.RECTANGLE, {
    x: px + 0.8, y: 2.65, w: 1.25, h: 0.02,
    fill: { color: GOLD }
  });
  s5.addText(p.body, {
    x: px + 0.3, y: 2.75, w: 2.25, h: 1.15,
    fontSize: 10.5, fontFace: "Microsoft YaHei",
    color: DARK, lineSpacingMultiple: 1.4, valign: "top", margin: 0
  });
});

// 底部图片占位区 — G20峰会照片
s5.addShape(pres.shapes.RECTANGLE, {
  x: 0.5, y: 4.2, w: 9.0, h: 0.95,
  fill: { color: OFF_WHITE },
  line: { color: GOLD, width: 1.5, dashType: "dash" }
});
s5.addText("📷 点击此处插入图片  |  推荐：G20峰会、联合国会议等国际场合照片（新华社）", {
  x: 0.7, y: 4.2, w: 8.6, h: 0.95,
  fontSize: 11, fontFace: "Microsoft YaHei",
  color: GRAY, align: "center", valign: "middle", margin: 0
});

// ============================================================
// 第6页：第二节①
// ============================================================
const s6 = pres.addSlide();
s6.background = { color: CREAM };
addRedBanner(s6, "第二节 · 全面推进中国特色大国外交（上）", "坚持走和平发展道路 · 推动构建新型国际关系");
addPageNumber(s6, 6);
addFooterText(s6, "习概第16章 · 中国特色大国外交");

// 左卡片
addCard(s6, 0.5, 1.7, 4.35, 3.3);
s6.addText("🕊️", {
  x: 0.5, y: 1.85, w: 4.35, h: 0.5,
  fontSize: 28, align: "center", margin: 0
});
s6.addText("坚持走和平发展道路", {
  x: 0.8, y: 2.35, w: 3.75, h: 0.45,
  fontSize: 18, fontFace: "SimHei", color: RED, bold: true, align: "center", margin: 0
});
s6.addShape(pres.shapes.RECTANGLE, {
  x: 1.5, y: 2.8, w: 2.35, h: 0.02,
  fill: { color: GOLD }
});
s6.addText([
  { text: "• 和平发展是中国特色社会主义的必然选择", options: { bullet: true, breakLine: true, fontSize: 12 } },
  { text: "• 不走\"国强必霸\"的老路，不搞扩张、不搞霸权", options: { bullet: true, breakLine: true, fontSize: 12 } },
  { text: "• 以和平方式解决国际争端", options: { bullet: true, breakLine: true, fontSize: 12 } },
  { text: "• 在追求本国利益时兼顾他国合理关切", options: { bullet: true, fontSize: 12 } }
], {
  x: 0.8, y: 2.95, w: 3.75, h: 1.85,
  fontFace: "Microsoft YaHei", color: DARK, valign: "top",
  paraSpaceAfter: 8, margin: 0
});

// 右卡片
addCard(s6, 5.15, 1.7, 4.35, 3.3);
s6.addText("🤝", {
  x: 5.15, y: 1.85, w: 4.35, h: 0.5,
  fontSize: 28, align: "center", margin: 0
});
s6.addText("推动构建新型国际关系", {
  x: 5.45, y: 2.35, w: 3.75, h: 0.45,
  fontSize: 18, fontFace: "SimHei", color: RED, bold: true, align: "center", margin: 0
});
s6.addShape(pres.shapes.RECTANGLE, {
  x: 6.15, y: 2.8, w: 2.35, h: 0.02,
  fill: { color: GOLD }
});

// 三原则
const principles6 = [
  { t: "相互尊重", d: "尊重各国自主选择的社会制度和发展道路" },
  { t: "公平正义", d: "反对霸权主义和强权政治，坚持国家不分大小一律平等" },
  { t: "合作共赢", d: "对话而不对抗、结伴而不结盟，实现共同发展" }
];

principles6.forEach((pr, i) => {
  const py = 2.9 + i * 0.7;
  s6.addShape(pres.shapes.OVAL, {
    x: 5.55, y: py, w: 0.22, h: 0.22,
    fill: { color: RED }
  });
  s6.addText(pr.t, {
    x: 5.9, y: py - 0.05, w: 3.3, h: 0.25,
    fontSize: 12, fontFace: "Microsoft YaHei",
    color: RED, bold: true, margin: 0
  });
  s6.addText(pr.d, {
    x: 5.9, y: py + 0.22, w: 3.3, h: 0.35,
    fontSize: 10, fontFace: "Microsoft YaHei",
    color: GRAY, margin: 0
  });
});

// ============================================================
// 第7页：第二节②
// ============================================================
const s7 = pres.addSlide();
s7.background = { color: CREAM };
addRedBanner(s7, "第二节 · 全面推进中国特色大国外交（下）", "坚决维护国家利益 · 坚持外交为民");
addPageNumber(s7, 7);
addFooterText(s7, "习概第16章 · 中国特色大国外交");

// 左侧：维护国家利益
addCard(s7, 0.5, 1.7, 4.35, 3.3);

s7.addShape(pres.shapes.RECTANGLE, {
  x: 0.5, y: 1.7, w: 4.35, h: 0.55,
  fill: { color: RED }
});
s7.addText("坚决维护国家主权、安全、发展利益", {
  x: 0.8, y: 1.7, w: 3.75, h: 0.55,
  fontSize: 16, fontFace: "SimHei", color: WHITE, bold: true, valign: "middle", margin: 0
});

s7.addText([
  { text: "核心立场", options: { bold: true, breakLine: true, fontSize: 13, color: RED } },
  { text: "在国家核心利益问题上决不妥协、决不退让。", options: { breakLine: true, fontSize: 11, color: DARK } },
  { text: "", options: { breakLine: true, fontSize: 6 } },
  { text: "重点领域", options: { bold: true, breakLine: true, fontSize: 13, color: RED } },
  { text: "• 台湾问题：坚持一个中国原则", options: { bullet: true, breakLine: true, fontSize: 11 } },
  { text: "• 南海问题：维护领土主权和海洋权益", options: { bullet: true, breakLine: true, fontSize: 11 } },
  { text: "• 涉疆涉藏：反对外部势力干涉内政", options: { bullet: true, breakLine: true, fontSize: 11 } },
  { text: "• 经济安全：维护产业链供应链稳定", options: { bullet: true, fontSize: 11 } }
], {
  x: 0.8, y: 2.4, w: 3.75, h: 2.4,
  fontFace: "Microsoft YaHei", valign: "top",
  paraSpaceAfter: 2, margin: 0
});

// 右侧：外交为民
addCard(s7, 5.15, 1.7, 4.35, 3.3);

s7.addShape(pres.shapes.RECTANGLE, {
  x: 5.15, y: 1.7, w: 4.35, h: 0.55,
  fill: { color: RED }
});
s7.addText("坚持外交为民", {
  x: 5.45, y: 1.7, w: 3.75, h: 0.55,
  fontSize: 16, fontFace: "SimHei", color: WHITE, bold: true, valign: "middle", margin: 0
});

s7.addText([
  { text: "理念", options: { bold: true, breakLine: true, fontSize: 13, color: RED } },
  { text: "外交工作要服务人民，增强海外中国公民的安全感和获得感。", options: { breakLine: true, fontSize: 11, color: DARK } },
  { text: "", options: { breakLine: true, fontSize: 6 } },
  { text: "举措", options: { bold: true, breakLine: true, fontSize: 13, color: RED } },
  { text: "• 领事保护：24小时全球领事保护热线12308", options: { bullet: true, breakLine: true, fontSize: 11 } },
  { text: "• 海外撤侨：多次成功组织大规模撤侨行动", options: { bullet: true, breakLine: true, fontSize: 11 } },
  { text: "• \"中国领事\"APP：指尖办理领事业务", options: { bullet: true, breakLine: true, fontSize: 11 } },
  { text: "• 疫情互助：为海外同胞提供\"健康包\"等援助", options: { bullet: true, fontSize: 11 } }
], {
  x: 5.45, y: 2.4, w: 3.75, h: 2.4,
  fontFace: "Microsoft YaHei", valign: "top",
  paraSpaceAfter: 2, margin: 0
});

// ============================================================
// 第8页：第三节① —— 红底分隔页风格
// ============================================================
const s8 = pres.addSlide();
redSlide(s8);

s8.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 0, w: 10, h: 0.06,
  fill: { color: GOLD }
});
s8.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 5.565, w: 10, h: 0.06,
  fill: { color: GOLD }
});

s8.addText("第三节", {
  x: 0.8, y: 0.4, w: 8.4, h: 0.5,
  fontSize: 18, fontFace: "Microsoft YaHei",
  color: GOLD, align: "center", margin: 0
});

s8.addText("推动构建人类命运共同体", {
  x: 0.8, y: 0.9, w: 8.4, h: 0.8,
  fontSize: 32, fontFace: "SimHei",
  color: WHITE, bold: true, align: "center", margin: 0
});

// 五个世界的理念（缩小高度，为下方图片留空间）
s8.addShape(pres.shapes.RECTANGLE, {
  x: 0.8, y: 2.0, w: 8.4, h: 2.05,
  fill: { color: DARK_RED }
});
s8.addShape(pres.shapes.RECTANGLE, {
  x: 0.95, y: 2.12, w: 8.1, h: 1.8,
  fill: { color: "000000", transparency: 100 },
  line: { color: GOLD, width: 1.5 }
});

s8.addText("构建人类命运共同体，建设一个：", {
  x: 1.2, y: 2.18, w: 7.6, h: 0.35,
  fontSize: 15, fontFace: "Microsoft YaHei",
  color: GOLD, align: "center", margin: 0
});

const fiveWorlds = [
  "持久和平的世界",
  "普遍安全的世界",
  "共同繁荣的世界",
  "开放包容的世界",
  "清洁美丽的世界"
];

fiveWorlds.forEach((w, i) => {
  const wx = 1.6 + i * 1.4;
  s8.addShape(pres.shapes.OVAL, {
    x: wx, y: 2.7, w: 1.2, h: 0.35,
    fill: { color: RED }
  });
  s8.addText(w, {
    x: wx, y: 2.7, w: 1.2, h: 0.35,
    fontSize: 10, fontFace: "Microsoft YaHei",
    color: WHITE, bold: true, align: "center", valign: "middle", margin: 0
  });
});

s8.addText("三大倡议：全球发展倡议 · 全球安全倡议 · 全球文明倡议", {
  x: 1.2, y: 3.25, w: 7.6, h: 0.3,
  fontSize: 11, fontFace: "Microsoft YaHei",
  color: OFF_WHITE, align: "center", margin: 0
});

s8.addText("全人类共同价值：和平 · 发展 · 公平 · 正义 · 民主 · 自由", {
  x: 1.2, y: 3.55, w: 7.6, h: 0.3,
  fontSize: 11, fontFace: "Microsoft YaHei",
  color: LIGHT_GOLD, align: "center", margin: 0
});

// 海报图片占位区
s8.addShape(pres.shapes.RECTANGLE, {
  x: 1.5, y: 4.2, w: 7.0, h: 1.15,
  fill: { color: DARK_RED },
  line: { color: GOLD, width: 1.5, dashType: "dash" }
});
s8.addText("📷 点击此处插入海报  |  推荐：人类命运共同体宣传海报（新华社 / 一带一路官网）", {
  x: 1.7, y: 4.2, w: 6.6, h: 1.15,
  fontSize: 11, fontFace: "Microsoft YaHei",
  color: GOLD, align: "center", valign: "middle", margin: 0
});

// ============================================================
// 第9页：第三节② —— 全球治理 + 一带一路
// ============================================================
const s9 = pres.addSlide();
s9.background = { color: CREAM };
addRedBanner(s9, "第三节 · 全球治理体系改革与高质量共建\"一带一路\"", "积极参与全球治理 · 推动共同发展");
addPageNumber(s9, 9);
addFooterText(s9, "习概第16章 · 中国特色大国外交");

// 左侧卡片：全球治理（缩小高度）
addCard(s9, 0.5, 1.65, 4.35, 2.5);
s9.addText("🌐 积极参与全球治理体系改革", {
  x: 0.8, y: 1.78, w: 3.75, h: 0.35,
  fontSize: 14, fontFace: "SimHei", color: RED, bold: true, margin: 0
});
s9.addText([
  { text: "• 维护以联合国为核心的国际体系", options: { bullet: true, breakLine: true, fontSize: 10.5 } },
  { text: "• 推动IMF、世界银行等国际机构改革", options: { bullet: true, breakLine: true, fontSize: 10.5 } },
  { text: "• 积极参与气候变化、维和、公共卫生等全球行动", options: { bullet: true, breakLine: true, fontSize: 10.5 } },
  { text: "• 提出全球发展倡议、全球安全倡议、全球文明倡议", options: { bullet: true, breakLine: true, fontSize: 10.5 } },
  { text: "• 加入RCEP，推进加入CPTPP进程", options: { bullet: true, fontSize: 10.5 } }
], {
  x: 0.8, y: 2.2, w: 3.75, h: 1.7,
  fontFace: "Microsoft YaHei", color: DARK, valign: "top",
  paraSpaceAfter: 3, margin: 0
});

// 右侧卡片：一带一路（缩小高度 + 数据单行排列）
addCard(s9, 5.15, 1.65, 4.35, 2.5);
s9.addText("🚂 高质量共建\"一带一路\"", {
  x: 5.45, y: 1.78, w: 3.75, h: 0.35,
  fontSize: 14, fontFace: "SimHei", color: RED, bold: true, margin: 0
});

// 数据亮点 — 横向一行排列
const data9 = [
  { n: "23.6万亿", l: "对共建国家进出口" },
  { n: "51.9%", l: "共建伙伴占外贸比重" },
  { n: "12万+列", l: "中欧班列累计开行" },
  { n: "22国", l: "签署自贸协定" }
];

data9.forEach((d, i) => {
  const dx = 5.3 + i * 1.05;
  s9.addText(d.n, {
    x: dx, y: 2.3, w: 0.95, h: 0.35,
    fontSize: 15, fontFace: "Microsoft YaHei",
    color: RED, bold: true, align: "center", margin: 0
  });
  s9.addText(d.l, {
    x: dx, y: 2.65, w: 0.95, h: 0.3,
    fontSize: 7.5, fontFace: "Microsoft YaHei",
    color: GRAY, align: "center", margin: 0
  });
});

s9.addText("（2025年数据，来源：人民网、央视网）", {
  x: 5.45, y: 3.5, w: 3.75, h: 0.2,
  fontSize: 8, fontFace: "Microsoft YaHei",
  color: GRAY, italic: true, margin: 0
});

// 底部图片占位区 — 中欧班列航拍照片
s9.addShape(pres.shapes.RECTANGLE, {
  x: 0.5, y: 4.3, w: 9.0, h: 0.85,
  fill: { color: OFF_WHITE },
  line: { color: GOLD, width: 1.5, dashType: "dash" }
});
s9.addText("📷 点击此处插入图片  |  推荐：中欧班列无人机航拍照片（新华社）", {
  x: 0.7, y: 4.3, w: 8.6, h: 0.85,
  fontSize: 11, fontFace: "Microsoft YaHei",
  color: GRAY, align: "center", valign: "middle", margin: 0
});

// ============================================================
// 第10页：新闻回扣理论
// ============================================================
const s10 = pres.addSlide();
redSlide(s10);

s10.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 0, w: 10, h: 0.06,
  fill: { color: GOLD }
});
s10.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 5.565, w: 10, h: 0.06,
  fill: { color: GOLD }
});

s10.addText("新闻回扣理论", {
  x: 0.8, y: 0.25, w: 8.4, h: 0.55,
  fontSize: 26, fontFace: "SimHei",
  color: GOLD, bold: true, align: "center", margin: 0
});
s10.addText("中孟命运共同体如何体现第十六章核心内容？", {
  x: 0.8, y: 0.75, w: 8.4, h: 0.35,
  fontSize: 13, fontFace: "Microsoft YaHei",
  color: OFF_WHITE, align: "center", margin: 0
});

// 对照表
const rows10 = [
  { theory: "新型国际关系", news: "相互尊重、平等互利的双边关系" },
  { theory: "一带一路高质量发展", news: "港口、水利、基建项目合作，中缅孟经济走廊" },
  { theory: "人类命运共同体", news: "正式宣布构建\"新时代中孟命运共同体\"" },
  { theory: "全球南方合作", news: "在联合国协调立场，维护发展中国家利益" },
  { theory: "和平发展道路", news: "对话协商解决分歧，不干涉内政" }
];

const tableY = 1.4;
const col1X = 0.8, col1W = 2.8;
const col2X = 3.8, col2W = 5.4;

// 表头
s10.addShape(pres.shapes.RECTANGLE, {
  x: col1X, y: tableY, w: col1W, h: 0.45,
  fill: { color: DARK_RED }
});
s10.addText("第十六章理论要点", {
  x: col1X, y: tableY, w: col1W, h: 0.45,
  fontSize: 13, fontFace: "SimHei", color: GOLD, bold: true, align: "center", valign: "middle", margin: 0
});
s10.addShape(pres.shapes.RECTANGLE, {
  x: col2X, y: tableY, w: col2W, h: 0.45,
  fill: { color: DARK_RED }
});
s10.addText("中孟案例对应体现", {
  x: col2X, y: tableY, w: col2W, h: 0.45,
  fontSize: 13, fontFace: "SimHei", color: GOLD, bold: true, align: "center", valign: "middle", margin: 0
});

rows10.forEach((r, i) => {
  const ry = tableY + 0.45 + i * 0.65;
  const bgColor = i % 2 === 0 ? DARK_RED : RED;

  s10.addShape(pres.shapes.RECTANGLE, {
    x: col1X, y: ry, w: col1W, h: 0.65,
    fill: { color: bgColor }
  });
  s10.addText(r.theory, {
    x: col1X + 0.2, y: ry, w: col1W - 0.4, h: 0.65,
    fontSize: 12, fontFace: "Microsoft YaHei", color: WHITE, bold: true, valign: "middle", margin: 0
  });
  s10.addShape(pres.shapes.RECTANGLE, {
    x: col2X, y: ry, w: col2W, h: 0.65,
    fill: { color: bgColor }
  });
  s10.addText("→  " + r.news, {
    x: col2X + 0.2, y: ry, w: col2W - 0.4, h: 0.65,
    fontSize: 11, fontFace: "Microsoft YaHei", color: OFF_WHITE, valign: "middle", margin: 0
  });
});

// ============================================================
// 第11页：个人思考与启发①
// ============================================================
const s11 = pres.addSlide();
s11.background = { color: CREAM };
addRedBanner(s11, "💡 个人思考与启发（一）", "从\"旁观者\"到\"参与者\"");
addPageNumber(s11, 11);
addFooterText(s11, "习概第16章 · 中国特色大国外交");

addCard(s11, 0.5, 1.7, 4.35, 3.3);
s11.addText("以前的认知", {
  x: 0.8, y: 1.85, w: 3.75, h: 0.4,
  fontSize: 16, fontFace: "SimHei", color: RED, bold: true, margin: 0
});
s11.addText([
  { text: "觉得外交离自己很远，是大国之间的博弈，", options: { breakLine: true, fontSize: 12 } },
  { text: "是国家领导人的事，跟普通人没什么关系。", options: { breakLine: true, fontSize: 12 } },
  { text: "", options: { breakLine: true, fontSize: 8 } },
  { text: "→ 把\"外交\"等同于\"新闻联播里的会见\"", options: { italic: true, breakLine: true, fontSize: 11, color: GRAY } }
], {
  x: 0.8, y: 2.35, w: 3.75, h: 1.3,
  fontFace: "Microsoft YaHei", color: DARK, valign: "top",
  lineSpacingMultiple: 1.3, margin: 0
});

// 箭头
s11.addText("→", {
  x: 0.8, y: 3.65, w: 3.75, h: 0.4,
  fontSize: 24, fontFace: "Microsoft YaHei",
  color: RED, align: "center", margin: 0
});

s11.addText("现在的理解", {
  x: 0.8, y: 3.95, w: 3.75, h: 0.35,
  fontSize: 16, fontFace: "SimHei", color: RED, bold: true, margin: 0
});
s11.addText("一带一路带来的进口商品、留学生交流、中国企业在海外的项目，实际上都影响着我们的日常生活。全球化时代，每个人都是国家外交的\"受益者\"和\"名片\"。", {
  x: 0.8, y: 4.3, w: 3.75, h: 1.0,
  fontSize: 11, fontFace: "Microsoft YaHei",
  color: DARK, lineSpacingMultiple: 1.4, valign: "top", margin: 0
});

// 右侧总结卡片
addCard(s11, 5.15, 1.7, 4.35, 3.3);
s11.addText("核心感悟", {
  x: 5.45, y: 1.85, w: 3.75, h: 0.4,
  fontSize: 18, fontFace: "SimHei", color: RED, bold: true, align: "center", margin: 0
});
s11.addShape(pres.shapes.RECTANGLE, {
  x: 6.15, y: 2.25, w: 2.35, h: 0.02,
  fill: { color: GOLD }
});

const thoughts11 = [
  "外交不是虚无缥缈的宏大叙事，而是由一个个具体的合作项目、一次次真实的文明交流构成的。",
  "作为新时代大学生，我们既是国家发展的受益者，也是国家形象的塑造者。",
  "理解中国外交，就是理解中国与世界的关系——这关乎每个人的未来。"
];

thoughts11.forEach((t, i) => {
  const ty = 2.45 + i * 0.95;
  s11.addShape(pres.shapes.OVAL, {
    x: 5.55, y: ty + 0.05, w: 0.18, h: 0.18,
    fill: { color: GOLD }
  });
  s11.addText(t, {
    x: 5.85, y: ty, w: 3.35, h: 0.85,
    fontSize: 11, fontFace: "Microsoft YaHei",
    color: DARK, valign: "top", lineSpacingMultiple: 1.3, margin: 0
  });
});

// ============================================================
// 第12页：个人思考与启发②
// ============================================================
const s12 = pres.addSlide();
redSlide(s12);

s12.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 0, w: 10, h: 0.06,
  fill: { color: GOLD }
});
s12.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 5.565, w: 10, h: 0.06,
  fill: { color: GOLD }
});

s12.addText("💡 个人思考与启发（二）", {
  x: 0.8, y: 0.3, w: 8.4, h: 0.55,
  fontSize: 24, fontFace: "SimHei",
  color: GOLD, bold: true, align: "center", margin: 0
});
s12.addText("大国担当与青年责任", {
  x: 0.8, y: 0.8, w: 8.4, h: 0.35,
  fontSize: 16, fontFace: "Microsoft YaHei",
  color: OFF_WHITE, align: "center", margin: 0
});

// 两个卡片
const cards12 = [
  {
    title: "什么是大国担当？",
    items: [
      "不只是经济体量大，更是为世界提供公共产品",
      "在气候变化、公共卫生、维和等领域承担责任",
      "以人类命运共同体理念引领全球治理",
      "让发展成果惠及更多国家和人民"
    ]
  },
  {
    title: "青年能做什么？",
    items: [
      "培养国际视野：关注全球议题，理解中国立场",
      "讲好中国故事：用世界听得懂的语言传播中国文化",
      "参与跨文化交流：留学、志愿服务、国际组织实习",
      "夯实专业能力：以专业本领服务国家战略需求"
    ]
  }
];

cards12.forEach((c, i) => {
  const cx = 0.5 + i * 4.7;

  s12.addShape(pres.shapes.RECTANGLE, {
    x: cx, y: 1.45, w: 4.3, h: 3.7,
    fill: { color: DARK_RED }
  });

  s12.addText(c.title, {
    x: cx + 0.3, y: 1.55, w: 3.7, h: 0.45,
    fontSize: 18, fontFace: "SimHei", color: GOLD, bold: true, align: "center", margin: 0
  });
  s12.addShape(pres.shapes.RECTANGLE, {
    x: cx + 1.2, y: 2.0, w: 1.9, h: 0.02,
    fill: { color: GOLD }
  });

  c.items.forEach((item, j) => {
    s12.addText("✦  " + item, {
      x: cx + 0.3, y: 2.2 + j * 0.7, w: 3.7, h: 0.6,
      fontSize: 12, fontFace: "Microsoft YaHei",
      color: WHITE, valign: "top", lineSpacingMultiple: 1.2, margin: 0
    });
  });
});

// 底部金句
s12.addText("「 各美其美，美人之美，美美与共，天下大同 」 —— 费孝通", {
  x: 0.8, y: 5.2, w: 8.4, h: 0.3,
  fontSize: 11, fontFace: "Microsoft YaHei",
  color: LIGHT_GOLD, align: "center", italic: true, margin: 0
});

// ============================================================
// 第13页：小组总结
// ============================================================
const s13 = pres.addSlide();
s13.background = { color: CREAM };
addRedBanner(s13, "📋 小组总结", "核心观点回顾");
addPageNumber(s13, 13);
addFooterText(s13, "习概第16章 · 中国特色大国外交");

const summary13 = [
  { num: "1", text: "世界正经历百年未有之大变局，中国特色大国外交应运而生，开创了外交工作新局面。" },
  { num: "2", text: "坚持和平发展道路、构建新型国际关系、维护国家利益、践行外交为民，构成中国外交的四大支柱。" },
  { num: "3", text: "构建人类命运共同体是新时代中国外交的总目标，\"一带一路\"是重要实践平台。" },
  { num: "4", text: "中孟命运共同体的最新实践表明，中国理念正在转化为具体的国际合作成果。" },
  { num: "5", text: "作为新时代大学生，理解中国外交、培养国际视野，是我们的责任与担当。" }
];

summary13.forEach((s, i) => {
  const sy = 1.55 + i * 0.58;

  s13.addShape(pres.shapes.RECTANGLE, {
    x: 0.6, y: sy, w: 8.8, h: 0.52,
    fill: { color: i % 2 === 0 ? OFF_WHITE : WHITE }
  });

  s13.addShape(pres.shapes.OVAL, {
    x: 0.8, y: sy + 0.06, w: 0.4, h: 0.4,
    fill: { color: RED }
  });
  s13.addText(s.num, {
    x: 0.8, y: sy + 0.06, w: 0.4, h: 0.4,
    fontSize: 14, fontFace: "Microsoft YaHei",
    color: WHITE, bold: true, align: "center", valign: "middle", margin: 0
  });

  s13.addText(s.text, {
    x: 1.4, y: sy, w: 7.8, h: 0.52,
    fontSize: 12, fontFace: "Microsoft YaHei",
    color: DARK, valign: "middle", margin: 0
  });
});

// 底部致谢
s13.addShape(pres.shapes.RECTANGLE, {
  x: 2.5, y: 4.7, w: 5, h: 0.35,
  fill: { color: RED }
});
s13.addText("感谢聆听 · 欢迎批评指正", {
  x: 2.5, y: 4.7, w: 5, h: 0.35,
  fontSize: 12, fontFace: "Microsoft YaHei",
  color: WHITE, align: "center", valign: "middle", margin: 0
});

// ============================================================
// 第14页：参考资料
// ============================================================
const s14 = pres.addSlide();
s14.background = { color: CREAM };
addRedBanner(s14, "📚 参考资料", "");
addPageNumber(s14, 14);
addFooterText(s14, "习概第16章 · 中国特色大国外交");

addCard(s14, 0.5, 1.6, 9.0, 3.4);

const refs = [
  { label: "教材", text: "本书编写组.《习近平新时代中国特色社会主义思想概论》. 高等教育出版社、人民出版社，2023年8月." },
  { label: "新闻", text: "《习近平会见孟加拉国总理塔里克》. 新华社，2026年6月26日." },
  { label: "新闻", text: "《高质量共建\"一带一路\" 不断拓展共赢发展新空间》. 人民网/央视网，2026年1月27日." },
  { label: "新闻", text: "《主场外交盛况空前，中国尽显\"全球战略稳定器\"本色》. 中国青年报，2026年6月10日." },
  { label: "新闻", text: "China, Bangladesh Announce to Build Community with Shared Future in New Era. Xinhua News, June 26, 2026." },
  { label: "数据", text: "走进外交部网站 (fmprc.gov.cn) —— 外交政策、发言人谈话、领事服务等." }
];

refs.forEach((r, i) => {
  const ry = 1.75 + i * 0.52;

  s14.addShape(pres.shapes.RECTANGLE, {
    x: 0.8, y: ry + 0.05, w: 0.7, h: 0.25,
    fill: { color: RED }
  });
  s14.addText(r.label, {
    x: 0.8, y: ry + 0.05, w: 0.7, h: 0.25,
    fontSize: 9, fontFace: "Microsoft YaHei",
    color: WHITE, bold: true, align: "center", valign: "middle", margin: 0
  });
  s14.addText(r.text, {
    x: 1.65, y: ry, w: 7.6, h: 0.4,
    fontSize: 10.5, fontFace: "Microsoft YaHei",
    color: DARK, valign: "middle", margin: 0
  });
});

// ============================================================
// 第15页：结束页
// ============================================================
const s15 = pres.addSlide();
redSlide(s15);

s15.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 0, w: 10, h: 0.08,
  fill: { color: GOLD }
});
s15.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 5.545, w: 10, h: 0.08,
  fill: { color: GOLD }
});

// 中央装饰框
s15.addShape(pres.shapes.RECTANGLE, {
  x: 1.5, y: 1.2, w: 7.0, h: 3.2,
  fill: { color: DARK_RED },
  shadow: { type: "outer", blur: 8, offset: 3, angle: 135, color: "000000", opacity: 0.25 }
});
s15.addShape(pres.shapes.RECTANGLE, {
  x: 1.65, y: 1.35, w: 6.7, h: 2.9,
  fill: { color: "000000", transparency: 100 },
  line: { color: GOLD, width: 2 }
});

s15.addText("谢谢观看", {
  x: 1.65, y: 1.7, w: 6.7, h: 1.2,
  fontSize: 48, fontFace: "SimHei",
  color: GOLD, bold: true, align: "center", valign: "middle", margin: 0
});

s15.addShape(pres.shapes.RECTANGLE, {
  x: 3.5, y: 3.0, w: 3.0, h: 0.03,
  fill: { color: GOLD }
});

s15.addText("中国特色大国外交和推动构建人类命运共同体", {
  x: 1.65, y: 3.2, w: 6.7, h: 0.5,
  fontSize: 16, fontFace: "Microsoft YaHei",
  color: OFF_WHITE, align: "center", margin: 0
});

s15.addText("恳请各位老师同学批评指正", {
  x: 1.65, y: 3.7, w: 6.7, h: 0.4,
  fontSize: 13, fontFace: "Microsoft YaHei",
  color: LIGHT_GOLD, align: "center", margin: 0
});

// ============================================================
// 保存
// ============================================================
pres.writeFile({ fileName: "c:/Users/AUSU/Documents/trae_projects/cc/tmp/习概第16章_学习汇报.pptx" })
  .then(() => console.log("PPTX generated successfully!"))
  .catch(err => console.error("Error:", err));
