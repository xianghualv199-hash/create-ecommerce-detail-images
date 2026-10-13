# create-ecommerce-detail-images

一个面向中文电商视觉生产的 Codex Skill。它把商品照片和资料转化为一套可验证、可发布的主图、场景图、详情页分屏和营销延展，并把商品一致性、文字准确性与合规边界放在生成速度之前。

## 核心能力

- 建立“商品真相表”，区分图片可见信息、包装信息、用户资料与检测/资质证据。
- 完成产品定位、用户画像、核心卖点、视觉方向与当前竞品扫描。
- 按“看得清 + 看得懂 + 想要买”的 3 秒法则规划正方形主图。
- 先规划商品区、标题区、证据区和安全边距，再生成留白底图并完成中文排版。
- 将详情页拆成独立分屏逐张制作，避免长图一次生成造成文字错误和商品变形。
- 对商品外观、中文、数值、遮挡、裁切、页面差异和事实依据进行交付质检。

## 安装

将仓库克隆到 Codex Skills 目录：

```bash
git clone https://github.com/xianghualv199-hash/create-ecommerce-detail-images.git ~/.codex/skills/create-ecommerce-detail-images
```

重新打开 Codex，或开始一个新会话，使 Skill 被重新发现。

## 使用

在对话中上传有权使用的商品照片与资料，然后输入：

```text
使用 $create-ecommerce-detail-images，根据我上传的商品照片制作一套正方形电商主图和详情页。先完成商品分析与竞品扫描，再按 3 秒法则规划主图。
```

建议提供：

- 商品名称、品类与目标平台
- 正面、侧面、背面和细节照片（若有）
- 已确认的材质、规格、成分、使用方式与包装信息
- 可追溯的检测、认证或活动规则（若要使用相关主张）
- 品牌调性、参考风格和禁用表达

## 推荐工作流

1. 商品事实与证据分级
2. 商业分析与品类视觉路由
3. 当前竞品扫描与差异化方向
4. 主视觉系统与文字排版地图
5. 一张代表性样图确认
6. 3 秒主图、场景图与详情分屏
7. 缩略总览和逐张质检
8. 按文件清单交付

## 安全边界

- 不编造功效、认证、参数、材质、销量、排名、价格、优惠或售后承诺。
- 只有一张正面照片时，不虚构商品背面、隐藏结构或测试场景。
- 竞品扫描只用于发现同质化与差异化机会，不复制品牌资产、版式或文案。
- 准确中文和数值优先采用可控排版，不依赖生成模型直接绘制复杂文字。

## 目录结构

```text
.
├── SKILL.md
├── agents/openai.yaml
├── references/
│   ├── category-routing.md
│   ├── main-image-conversion.md
│   ├── main-plan-schema.md
│   ├── platform-specs.md
│   ├── prompt-templates.md
│   ├── qa-checklist.md
│   └── typography-layout.md
└── scripts/validate_main_plan.py
```

## 许可证

本项目采用 [MIT License](LICENSE)。
