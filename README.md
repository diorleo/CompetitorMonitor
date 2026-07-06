# MOZA Competitor Price Monitor

赛车模拟和飞行模拟产品价格对比可视化工具 — 对比 MOZA 与主要竞争对手的产品价格。

## 功能特性

- 📊 **多维度价格对比** — Wheel Base / Steering Wheel / Pedals / Bundle / Flight Sim 全品类
- 🏆 **竞争力洞察** — 自动计算 $/Nm 价值比、价格区间、品牌定位
- 📥 **导出 CSV** — 一键导出所有产品数据
- 🔄 **每月自动更新** — GitHub Actions 定时运行价格更新脚本

## 项目结构

```
CompeteMonitor/
├── index.html           # 主页面（深色主题，Chart.js 可视化）
├── data/
│   └── prices.js      # 价格数据文件（由 GitHub Actions 自动更新）
├── scripts/
│   └── update_prices.py  # 价格更新脚本
├── .github/
│   └── workflows/
│       └── update-prices.yml  # 每月定时任务
└── README.md
```

## 本地运行

```bash
# 启动本地服务器
python3 -m http.server 8080
# 访问 http://localhost:8080
```

## 价格数据来源

所有价格均来自各品牌官方网站（USD）：
- MOZA: us.mozaracing.com
- Fanatec: fanatec.com
- Simagic: simagic-usa.myshopify.com
- Logitech: logitechg.com
- Thrustmaster: eshop.thrustmaster.com
- PXN: us.e-pxn.com
- Thermaltake: thermaltakeusa.com
- Honeycomb: flyhoneycomb.com

## 自动更新

GitHub Actions 每月 1 日自动运行 `scripts/update_prices.py`：
- 脚本运行后如有价格变更，自动提交并推送
- 可手动触发：**Actions** → **Monthly Price Update** → **Run workflow**

## 部署

项目部署在 [Render](https://render.com/)（免费静态网站托管）：
1. Fork/Clone 此仓库
2. 在 Render 创建 Static Site
3. 连接 GitHub 仓库
4. 每次 push 自动部署

## 许可

MIT License
