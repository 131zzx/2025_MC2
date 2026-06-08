"""
全局配置：数据路径与议题产业分类表
"""
from pathlib import Path

# ── 路径配置 ──────────────────────────────────────────────
ROOT = Path(__file__).parent.parent
DATA_DIR = ROOT / "data"
OUTPUT_DIR = ROOT / "frontend" / "public" / "data"

DATA_FILES = {
    "filah":      DATA_DIR / "FILAH.json",
    "trout":      DATA_DIR / "TROUT.json",
    "journalist": DATA_DIR / "journalist.json",
}

# ── 议题产业分类表 ─────────────────────────────────────────
# bias_score: +1=旅游, -1=渔业, 0=混合/中性
TOPIC_INDUSTRY: dict[str, dict] = {
    # 渔业
    "deep_fishing_dock":    {"industry": "fishing",  "bias_score": -1, "label": "Himark 商业渔港维护"},
    "new_crane_lomark":     {"industry": "fishing",  "bias_score": -1, "label": "Lomark 新起重机"},
    "fish_vacuum":          {"industry": "fishing",  "bias_score": -1, "label": "鱼类真空采集设备"},
    "low_volume_crane":     {"industry": "fishing",  "bias_score": -1, "label": "Haacklee 低容量卸货 crane"},
    "name_inspection_office": {"industry": "fishing", "bias_score": -1, "label": "Lomark 检验办公室命名"},
    # 旅游
    "expanding_tourist_wharf": {"industry": "tourism", "bias_score": +1, "label": "Haacklee 旅游码头扩建"},
    "marine_life_deck":     {"industry": "tourism",  "bias_score": +1, "label": "Centralia 海洋生物观测台"},
    "heritage_walking_tour":{"industry": "tourism",  "bias_score": +1, "label": "Haacklee 遗产步行游"},
    "waterfront_market":    {"industry": "tourism",  "bias_score": +1, "label": "Haacklee 滨水市场"},
    "concert":              {"industry": "tourism",  "bias_score": +1, "label": "音乐会计划"},
    "name_harbor_area":     {"industry": "tourism",  "bias_score": +1, "label": "Port Grove 港湾命名"},
    "statue_john_smoth":    {"industry": "tourism",  "bias_score": +1, "label": "Port Grove 雕像"},
    # 混合 / 中性
    "affordable_housing":   {"industry": "mixed",    "bias_score":  0, "label": "渔工住房 vs 短租冲突"},
    "seafood_festival":     {"industry": "mixed",    "bias_score":  0, "label": "Paackland 海鲜节"},
    "renaming_park_himark": {"industry": "neutral",  "bias_score":  0, "label": "Himark 公园更名"},
}

# 所有 6 名委员会成员
COMMITTEE_MEMBERS = [
    "Seal",
    "Ed Helpsford",
    "Teddy Goldstein",
    "Simone Kat",
    "Tante Titan",
    "Carol Limpet",
]

# place.zone 映射为数值（用于地理偏见分析）
ZONE_SCORE: dict[str, int] = {
    "tourism":     +1,
    "commercial":   0,
    "residential":  0,
    "government":   0,
    "industrial":  -1,
}

# 数据集简称 → 中文标签
DATASET_LABELS = {
    "filah":      "FILAH",
    "trout":      "TROUT",
    "journalist": "全量",
}
