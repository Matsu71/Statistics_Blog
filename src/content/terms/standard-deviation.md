---
title: 標準偏差
slug: standard-deviation
exam_scope:
  - statistics_grade_2
level: standard
status: published
category: descriptive_statistics
short_definition: 分散を元の単位に戻して解釈しやすくした、散らばりの代表的な指標です。
definition: 分散の平方根をとった値を標準偏差といいます。
intuition:
  - 標準偏差は、平均からどのくらい離れやすいかを元の単位のまま見るための指標です。
  - 分散よりも、現実の数字としてイメージしやすいという利点があります。
visual_explanation:
  - 平均点が同じ 2 クラスでも、点数が広く散っているクラスのほうが標準偏差は大きくなります。
  - 標準偏差が小さいと、平均の近くにデータが集まりやすいと考えられます。
where_it_appears:
  - データのばらつきを、元の単位のまま説明したいとき
  - 正規分布、標準化、推定の話題に入る前の基本指標として
practical_examples:
  - title: テスト結果の安定性
    description: 平均点が同じでも、点数の広がり方が違う 2 クラスを比べるときに使います。
  - title: 工程管理
    description: 製品の測定値が平均値の近くにどれくらい集まっているかを見るときに使います。
exam_points:
  - 標準偏差は分散の平方根です。
  - 元データと同じ単位で解釈できます。
  - 正規分布や標準化で頻繁に登場します。
formulas:
  - name: 母標準偏差
    latex: '\sigma = \sqrt{\sigma^2}'
    description: 母分散の平方根をとると母標準偏差になります。
    conditions:
      - '$\sigma^2$ は母分散です。'
  - name: 標本標準偏差の考え方
    latex: 's = \sqrt{s^2}'
    description: 不偏分散や標本分散の平方根として標本標準偏差を考えます。
    conditions:
      - 何を平方根にしているかを常に確認します。
rigorous_explanation:
  - 分散は単位が二乗になるため、その平方根である標準偏差のほうが解釈しやすくなります。
common_mistakes:
  - 標準偏差と分散の違いを、単位の違いまで含めて説明しないこと
  - 標準偏差が大きいことを平均が大きいことと混同すること
related_terms:
  - mean
  - variance
references:
  - title: 統計検定2級 公式問題集
    type: official
  - title: 統計学入門
    type: textbook
tags:
  - ばらつき
  - 散布度
sort_order: 30
updated_at: 2026-03-27
---

標準偏差は、分散の考え方を実際の数値感覚へ戻す役割を持ちます。分散との違いを「平方根をとって単位を戻したもの」と言葉で説明できるようにしておくと、試験でも実務でも役立ちます。
