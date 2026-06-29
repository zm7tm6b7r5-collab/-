# -*- coding: utf-8 -*-
"""
PetStore 数据库 E-R 图 — 网格化精确布局版本
布局：
  y=8.0:   [商品分类]          [用户]
  y=5.0:   [商品]    [购物车]  [订单]
  y=1.5:                       [订单明细]
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Polygon
import matplotlib.patches as mpatches

plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei']
plt.rcParams['axes.unicode_minus'] = False

fig, ax = plt.subplots(1, 1, figsize=(16, 10))
ax.set_xlim(0, 16)
ax.set_ylim(0, 10)
ax.set_aspect('equal')
ax.axis('off')

# ===== 颜色 =====
C_HEAD  = '#2F5496'   # 深蓝（实体头部）
C_BODY  = '#FFFFFF'   # 白（实体主体）
C_EDGE  = '#2F5496'   # 实体边框
C_DIAM  = '#ED7D31'   # 橙（联系菱形）
C_LINE  = '#555555'   # 连线
C_PK    = '#FFF2CC'   # 主键高亮

# ===== 实体定义 (x, y, w, h, 实体名, [属性列表]) =====
# 属性: (名称, 标记) 或 名称
ENTITIES = [
    # x    y     w     h    名称      属性
    (0.8, 6.5, 2.3, 1.1, '商品分类', [('分类编号','PK'), '分类名称']),
    (0.8, 3.3, 2.3, 2.4, '商品',     [('商品编号','PK'), '商品名', '商品介绍',
                                        '市场价格', '当前价格', '数量', ('分类编号','FK')]),
    (6.5, 6.5, 2.3, 2.1, '用户',     [('用户号','PK'), '用户名', '密码',
                                        '性别', '邮箱', '电话']),
    (6.5, 3.3, 2.3, 1.5, '购物车',   [('购物车编号','PK'), ('用户号','FK'),
                                        ('商品编号','FK'), '数量']),
    (11.8, 6.0, 2.3, 1.9, '订单',    [('订单号','PK'), ('用户号','FK'),
                                        '订单日期', '订单总价', '是否已处理']),
    (11.8, 1.5, 2.3, 2.1, '订单明细', [('明细编号','PK'), ('订单号','FK'),
                                        ('商品编号','FK'), '商品名', '单价', '数量']),
]


def draw_entity_box(ax, x, y, w, h, title, attrs):
    """绘制实体"""
    head_h = 0.42
    # 头部
    head = FancyBboxPatch((x, y+h-head_h), w, head_h,
                          boxstyle="round,pad=0.01",
                          facecolor=C_HEAD, edgecolor=C_EDGE, linewidth=1.0)
    ax.add_patch(head)
    ax.text(x+w/2, y+h-head_h/2, title, ha='center', va='center',
            fontsize=9, fontweight='bold', color='white')

    # 主体
    body = FancyBboxPatch((x, y), w, h-head_h,
                          boxstyle="round,pad=0.01",
                          facecolor=C_BODY, edgecolor=C_EDGE, linewidth=1.0)
    ax.add_patch(body)

    # 属性
    n = len(attrs)
    row_h = (h - head_h) / max(n, 1)
    for i, attr in enumerate(attrs):
        if isinstance(attr, tuple):
            name, tag = attr
        else:
            name, tag = attr, ''
        ty = y + h - head_h - (i + 0.5) * row_h

        if 'PK' in str(tag):
            ax.text(x + 0.12, ty, name, ha='left', va='center', fontsize=7,
                    fontweight='bold', color=C_HEAD)
        else:
            ax.text(x + 0.12, ty, name, ha='left', va='center', fontsize=7,
                    color='#333333')
        if tag:
            ax.text(x + w - 0.1, ty, tag, ha='right', va='center', fontsize=5.5,
                    color='#999999', style='italic')

    # 分割线
    ax.plot([x+0.03, x+w-0.03], [y+h-head_h, y+h-head_h], color=C_EDGE, lw=0.8)
    return (x + w/2, y + h/2)  # 中心点


# ===== 绘制所有实体 =====
centers = {}
for ent in ENTITIES:
    x, y, w, h, name, attrs = ent
    cx, cy = draw_entity_box(ax, x, y, w, h, name, attrs)
    centers[name] = (x, y, w, h, cx, cy)


def diamond(ax, cx, cy, text, size=0.32):
    """绘制联系菱形"""
    d = Polygon([
        (cx, cy+size), (cx+size*1.4, cy),
        (cx, cy-size), (cx-size*1.4, cy)
    ], facecolor=C_DIAM, edgecolor='#B04A0E', linewidth=0.8, zorder=5)
    ax.add_patch(d)
    ax.text(cx, cy, text, ha='center', va='center', fontsize=7.5,
            fontweight='bold', color='white', zorder=6)


def line_between(ax, x1, y1, x2, y2, card='', lw=1.0):
    """画连线，card标注在线中间"""
    ax.plot([x1, x2], [y1, y2], color=C_LINE, linewidth=lw, zorder=2)
    if card:
        mx, my = (x1+x2)/2, (y1+y2)/2
        dx, dy = x2-x1, y2-y1
        nx, ny = -dy, dx
        dist = (nx**2 + ny**2)**0.5 or 1
        nx, ny = nx/dist * 0.28, ny/dist * 0.28
        ax.text(mx+nx, my+ny, card, fontsize=8, ha='center', va='center',
                color='#C55A11', fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.12', fc='white', ec='none', alpha=0.85))


# ===== 联系菱形位置 =====
# 商品分类(底) → 商品(顶)
d1_x, d1_y = 1.95, 4.8
diamond(ax, d1_x, d1_y, '包含')

# 用户(底) → 购物车(顶)
d2_x, d2_y = 7.65, 5.3
diamond(ax, d2_x, d2_y, '添加')

# 商品(右) → 购物车(左)
d3_x, d3_y = 5.1, 4.1
diamond(ax, d3_x, d3_y, '被加入')

# 用户(右) → 订单(左)
d4_x, d4_y = 9.8, 7.0
diamond(ax, d4_x, d4_y, '下达')

# 订单(底) → 订单明细(顶)
d5_x, d5_y = 12.95, 4.0
diamond(ax, d5_x, d5_y, '拥有')

# 商品(右) → 订单明细(左)
d6_x, d6_y = 5.5, 2.5
diamond(ax, d6_x, d6_y, '对应')


# ===== 连线（精确起终点） =====
# 1. 商品分类底 → 商品顶
line_between(ax, 1.95, 6.5, 1.95, 5.7, '1')
line_between(ax, 1.95, 4.5, 1.95, 3.3+2.4, 'N')

# 2. 用户底 → 购物车顶
line_between(ax, 7.65, 6.5, 7.65, 5.55, '1')
line_between(ax, 7.65, 5.05, 7.65, 4.8, 'N')

# 3. 商品右 → 购物车左
line_between(ax, 3.1, 4.0, 4.75, 4.1, '1')
line_between(ax, 5.45, 4.1, 6.5, 4.05, 'N')

# 4. 用户右 → 订单左
line_between(ax, 8.8, 7.0, 9.45, 7.0, '1')
line_between(ax, 10.15, 7.0, 11.8, 7.0, 'N')

# 5. 订单底 → 订单明细顶
line_between(ax, 12.95, 6.0, 12.95, 4.3, '1')
line_between(ax, 12.95, 3.7, 12.95, 3.6, 'N')

# 6. 商品右下 → 订单明细左
# 商品右边界中心: (3.1, 3.3+1.2=4.5) → 订单明细左边界: (11.8, 1.5+1.05=2.55)
line_between(ax, 3.1, 3.8, 5.15, 2.5, '1')
line_between(ax, 5.85, 2.5, 11.8, 2.55, 'N')


# ===== 标题 =====
ax.text(8, 9.5, 'PetStore 数据库 E-R 图', ha='center', fontsize=15, fontweight='bold', color='#1a1a1a')
ax.text(8, 9.05, '宠物商店电子商务系统 — 概念结构设计', ha='center', fontsize=9, color='#888888')

# ===== 图例 =====
lx, ly = 0.8, 9.2
ax.text(lx, ly, '图例', fontsize=8, fontweight='bold', color='#555')
# 实体
legend_ent = FancyBboxPatch((lx, ly-0.35), 0.7, 0.25,
                             boxstyle="round,pad=0.02", fc='white', ec=C_EDGE, lw=0.8)
ax.add_patch(legend_ent)
ax.text(lx+0.35, ly-0.23, '实体', ha='center', fontsize=6.5, color='#555')
# 联系
diamond(ax, lx+1.2, ly-0.23, '联系', size=0.15)
# 基数
ax.text(lx+2.0, ly-0.23, '1 : N  一对多', fontsize=7, color='#C55A11', fontweight='bold')

plt.tight_layout(pad=0.3)
out_path = r'c:\Users\AUSU\Documents\trae_projects\cc\tmp\petstore_er.png'
plt.savefig(out_path, dpi=250, bbox_inches='tight', facecolor='white')
print(f'ER图已保存: {out_path}')
plt.close()
