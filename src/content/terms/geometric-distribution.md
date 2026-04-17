---
title: '幾何分布'
slug: 'geometric-distribution'
exam_scope:
  - 'statistics_grade_2'
level: 'advanced'
status: published
category: 'probability_distribution'
short_definition: '初めて成功するまでに必要な試行回数を表す離散分布です。'
definition: '幾何分布は、成功確率 $p$ の独立な試行を繰り返し、初めて成功するまでの試行回数を表す分布です。'
intuition:
  - '幾何分布は、「成功するまで何回かかるか」を見る分布です。'
  - '1 回目で成功することもあれば、何回も失敗してから成功することもあります。'
  - '成功確率 $p$ が大きいほど、少ない回数で成功しやすくなります。'
  - '二項分布が固定回数内の成功回数を見るのに対し、幾何分布は初成功までの待ち時間を見ます。'
visual_explanation:
  - '1 回目成功、2 回目成功、3 回目成功という回数ごとに確率の棒を立てます。'
  - '回数が増えるほど、そこまで失敗し続ける必要があるため確率は小さくなります。'
  - '$p$ が大きいと左側の棒が高くなります。'
where_it_appears:
  - '初めて成功するまでの回数を考えるとき'
  - '反復試行の待ち時間をモデル化するとき'
  - '二項分布との違いを整理するとき'
practical_examples:
  - title: '初めて表が出るまで'
    description: '公平な硬貨を投げ続け、初めて表が出るまでの回数は幾何分布で考えられます。'
  - title: '初成功までの試行回数'
    description: '成功確率が一定で独立な挑戦を繰り返すとき、何回目で初めて成功するかを表します。'
exam_points:
  - '幾何分布は初めて成功するまでの試行回数を表します。'
  - '各試行は独立で、成功確率 $p$ が一定であることを確認します。'
  - '二項分布は成功回数、幾何分布は初成功までの回数です。'
  - '取りうる値は 1,2,3,... と続きます。'
formulas:
  - name: '幾何分布の確率'
    latex: 'P(X=k)=(1-p)^{k-1}p'
    description: '$k-1$ 回失敗してから、$k$ 回目で初めて成功する確率です。'
    conditions:
      - '$0<p\le 1$ です。'
      - '$k=1,2,3,\ldots$ です。'
  - name: '期待値'
    latex: 'E[X]=\frac{1}{p}'
    description: '成功確率 $p$ が大きいほど、初成功までの平均回数は小さくなります。'
    conditions:
      - '$X$ は初成功までの試行回数です。'
rigorous_explanation:
  - '幾何分布では、$k$ 回目に初めて成功するには、最初の $k-1$ 回が失敗し、最後に成功する必要があります。'
  - '独立性により、確率は $(1-p)^{k-1}p$ と掛け算で表せます。'
  - '成功確率が一定でない場合や試行が独立でない場合は、この形をそのまま使えません。'
common_mistakes:
  - '二項分布と同じく固定回数内の成功回数だと思うこと'
  - '$k$ 回目までに成功する確率と、$k$ 回目に初めて成功する確率を混同すること'
  - '失敗回数が $k-1$ 回であることを忘れること'
  - '独立性や成功確率一定の前提を確認しないこと'
related_terms:
  - 'binomial-distribution'
references:
  - title: '統計検定2級 公式問題集'
    type: official
  - title: '統計学入門'
    type: textbook
updated_at: 2026-04-17
aliases: []
tags:
  - '確率分布'
  - '離散型'
  - '幾何分布'
sort_order: 370
---

`geometric-distribution` は `binomial-distribution` と同じく成功/失敗の試行を扱います。ただし、二項分布は固定回数内の成功回数、幾何分布は初成功までの試行回数を見る点が違います。
