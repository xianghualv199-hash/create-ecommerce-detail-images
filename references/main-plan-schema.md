# 主图方案数据结构

正式生成前将主图方案保存为 UTF-8 JSON，使用 `scripts/validate_main_plan.py` 检查。

## 顶层字段

- `product_name`：商品名。
- `expected_count`：计划主图数量。
- `canvas`：`width`、`height`、`required_ratio`。比例仅允许 `1:1`、`3:4`、`4:5`、`9:16`、`16:9`。
- `promotion`：只在使用促销 claim 时提供，必须包含 `verified`、`offer`、`source_ref`、`start_date`、`end_date`、`scope`。日期格式为 `YYYY-MM-DD`。
- `main_images`：主图数组。

## 每张主图

- `index`：从 1 开始的唯一序号。
- `role`：`identity`、`usp`、`evidence`、`trust`、`scene`、`decision` 或 `promotion`。
- `focus`：该图唯一核心任务，全套不重复。
- `headline`：对象，含 `text` 和 `claim_id`。文字不超过 10 个可见字符。
- `copy`：副标或标签数组；每项同样含 `text` 和 `claim_id`。
- `claims`：该图使用的事实和主张。

## Claim

- `id`：项目内唯一 ID。
- `claim`：完整主张。
- `category`：`identity`、`attribute`、`specification`、`scene`、`performance`、`efficacy`、`certification`、`ranking` 或 `promotion`。
- `claim_status`：`visible`、`confirmed`、`pending` 或 `rejected`。
- `source_type`：`image-visible`、`packaging`、`user-material`、`test-report`、`certificate` 或 `promotion-terms`。
- `source_ref`：可追溯的图片、文件、页码或记录引用。
- `supported_copy`：该证据允许直接展示的精确短文案白名单。标题和副标必须与其中一项精确匹配；白名单文本必须能从 `claim` 原文中直接对应，不得借合规 claim ID 挂靠其他主张。

`performance`、`efficacy` 只允许已确认的 `test-report` / `certificate`。`certification` 需要 `certificate` 或可读包装引用。`ranking` 不用于展示文案。`promotion` 必须使用 `promotion-terms` 并与顶层活动对象一致。

## 最小示例

```json
{
  "product_name": "示例商品",
  "expected_count": 1,
  "canvas": {"width": 1200, "height": 1200, "required_ratio": "1:1"},
  "main_images": [
    {
      "index": 1,
      "role": "identity",
      "focus": "商品身份",
      "headline": {"text": "300ml玻璃杯", "claim_id": "c1"},
      "copy": [],
      "claims": [
        {
          "id": "c1",
          "claim": "300ml玻璃杯",
          "category": "identity",
          "claim_status": "confirmed",
          "source_type": "packaging",
          "source_ref": "front-package-image",
          "supported_copy": ["300ml玻璃杯"]
        }
      ]
    }
  ]
}
```
