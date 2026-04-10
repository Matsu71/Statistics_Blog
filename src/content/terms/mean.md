---
title: 平均
slug: mean
exam_scope:
  - statistics_grade_2
level: foundation
status: published
category: descriptive_statistics
short_definition: データ全体の中心を手早くつかむための、もっとも基本的な代表値です。
definition: 複数の値を合計して個数で割った値であり、データ全体を均したときの1つ分を表します。
intuition:
  - 平均は、ばらばらの値をならして1つの代表値にしたものです。
  - シーソーがつり合う位置を思い浮かべると、中心の感覚をつかみやすくなります。
visual_explanation:
  - 点数が 40 点、50 点、60 点なら、真ん中あたりの 50 点に全体の中心があると考えられます。
  - 値の重さを並べたときに、平均は左右がつり合う位置としてイメージできます。
where_it_appears:
  - クラスの平均点を見て、全体の学力水準をざっくり把握するとき
  - 月ごとの平均気温や平均売上のように、全体傾向を1つの数字にまとめたいとき
practical_examples:
  - title: クラスの平均点
    description: テスト結果をひとまとめにして、クラス全体がどのくらい取れているかを見るときに使います。
  - title: 平均売上
    description: 日ごとの売上をならして、通常時の水準を把握するときに使います。
exam_points:
  - 平均は代表値だが、外れ値の影響を受けやすいです。
  - 平均だけではデータのばらつきは分かりません。
  - 分散や標準偏差と組み合わせて見ることが多いです。
formulas:
  - name: 標本平均
    latex: '\bar{x} = \frac{1}{n}\sum_{i=1}^{n} x_i'
    description: 観測値の合計をデータ数で割ると標本平均になります。
    conditions:
      - '$x_i$ は i 番目の観測値です。'
      - '$n$ はデータ数です。'
rigorous_explanation:
  - 平均からの偏差をすべて足すと 0 になるため、平均はデータ全体のつり合いの点として理解できます。
proof:
  summary: 平均の定義を偏差の和に代入すると、偏差の総和が 0 になることを確認できます。
  outline_steps:
    - '$\sum_{i=1}^{n}(x_i-\bar{x})$ を書き下します。'
    - '$\bar{x} = \frac{1}{n}\sum_{i=1}^{n}x_i$ を代入します。'
    - 合計を整理すると 0 になります。
common_mistakes:
  - 平均だけでデータ全体の特徴を説明できたと思い込むこと
  - 中央値と平均を同じものとして扱うこと
related_terms:
  - variance
  - standard-deviation
references:
  - title: 統計検定2級 公式問題集
    type: official
  - title: 統計学入門
    type: textbook
updated_at: 2026-03-27
aliases:
  - 算術平均
tags:
  - 代表値
  - 中心
sort_order: 10
---

平均は、値を1つに要約する入口の概念です。平均を見たあとは、その周りにどれくらい散らばっているかを分散や標準偏差で見る流れが自然です。
