import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# 设置中文字体（尝试多种常用中文字体）
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Arial Unicode MS', 'sans-serif'] 
plt.rcParams['axes.unicode_minus'] = False

DATA_DIR = Path("../frontend/public/data")
OUT_DIR = Path("charts")
OUT_DIR.mkdir(exist_ok=True)

def load_json(name):
    with open(DATA_DIR / f"{name}.json", 'r', encoding='utf-8') as f:
        return json.load(f)

# 颜色配置（保持与前端一致）
COLORS = {'filah': '#ff9c6e', 'trout': '#69c0ff', 'journalist': '#95de64'}

def gen_q1_bias_chart():
    """生成 Q1 偏见指数对比图"""
    data = load_json("bias_index")
    # 仅展示 ALL 级别的对比
    df = pd.DataFrame(data)
    df = df[df['member'] == 'ALL']
    
    plt.figure(figsize=(10, 4))
    sns.barplot(x='bias_index', y='dataset', data=df, palette=COLORS)
    plt.axvline(0, color='gray', linestyle='--')
    plt.title("采样偏见指数对比 (Bias Index)")
    plt.xlabel("偏见指数 (+: 偏旅游, -: 偏渔业)")
    plt.savefig(OUT_DIR / "Q1_bias_index.png", dpi=300, bbox_inches='tight')
    print("Generated: Q1_bias_index.png")

def gen_q2_sentiment_heatmap():
    """生成 Q2 情感倾向热图"""
    data = load_json("sentiment_agg")
    df = pd.DataFrame(data)
    # 仅取全量数据集作为基准
    df = df[df['dataset'] == 'journalist']
    pivot = df.pivot(index='member', columns='industry', values='sentiment_mean')
    
    plt.figure(figsize=(10, 6))
    sns.heatmap(pivot, annot=True, cmap="RdBu", center=0, vmin=-1, vmax=1)
    plt.title("委员会全员情感倾向热图 (记者数据集)")
    plt.savefig(OUT_DIR / "Q2_sentiment_heatmap.png", dpi=300, bbox_inches='tight')
    print("Generated: Q2_sentiment_heatmap.png")

def gen_q3_indicator_compare():
    """生成 Q3 数据集指标规模对比"""
    data = load_json("overview")
    df = pd.DataFrame(data)
    
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    metrics = [('node_count', '节点总数'), ('edge_count', '边总数'), 
               ('trip_count', '行程总数'), ('member_count', '覆盖成员数')]
    
    for i, (col, title) in enumerate(metrics):
        ax = axes[i//2, i%2]
        sns.barplot(x='dataset', y=col, data=df, palette=COLORS, ax=ax)
        ax.set_title(title)
        ax.set_ylabel("")
        
    plt.tight_layout()
    plt.savefig(OUT_DIR / "Q3_indicator_compare.png", dpi=300, bbox_inches='tight')
    print("Generated: Q3_indicator_compare.png")

def gen_q4_coverage_matrix():
    """生成 Q4 成员活动覆盖率矩阵"""
    data = load_json("coverage")
    df = pd.DataFrame(data)
    pivot = df.pivot(index='member', columns='dataset', values='coverage')
    
    plt.figure(figsize=(8, 6))
    sns.heatmap(pivot, annot=True, fmt=".1%", cmap="YlGn")
    plt.title("成员活动覆盖率矩阵 (对比全量数据)")
    plt.savefig(OUT_DIR / "Q4_member_coverage.png", dpi=300, bbox_inches='tight')
    print("Generated: Q4_member_coverage.png")

if __name__ == "__main__":
    gen_q1_bias_chart()
    gen_q2_sentiment_heatmap()
    gen_q3_indicator_compare()
    gen_q4_coverage_matrix()
    print("\n所有图表已生成在 submission_materials/charts 目录下！")
