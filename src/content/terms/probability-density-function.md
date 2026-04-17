---
title: '確率密度関数'
slug: 'probability-density-function'
exam_scope:
  - 'statistics_grade_2'
level: 'advanced'
status: published
category: 'probability_distribution'
short_definition: '連続型確率変数の確率を、曲線下の面積として表す関数です。'
definition: '確率密度関数は、連続型確率変数の分布を表す関数です。1 点ちょうどの確率ではなく、区間に対する確率を曲線の下の面積として求めます。'
intuition:
  - '確率密度関数は、連続型分布の形を描く曲線です。'
  - '曲線が高いところは、その近くの値が出やすいと読む手がかりになります。'
  - 'ただし、曲線の高さそのものが確率ではありません。'
  - '確率は、区間を決めて曲線の下の面積として読みます。'
visual_explanation:
  - '横軸に値、縦軸に密度を置いた滑らかな曲線を考えます。'
  - '$a$ から $b$ までの範囲に色を塗ると、その面積が $P(a\le X\le b)$ です。'
  - '正規分布の釣鐘型の曲線は、確率密度関数の代表例です。'
where_it_appears:
  - '正規分布の曲線を読むとき'
  - '連続型確率変数の確率を区間で求めるとき'
  - '累積分布関数との関係を学ぶとき'
practical_examples:
  - title: '身長の分布'
    description: '身長のような連続的な値では、170 cm ちょうどの確率ではなく、169.5 cm から 170.5 cm のような区間の確率を考えます。'
  - title: '正規分布の面積'
    description: '平均付近の区間では曲線の下の面積が大きくなりやすく、端の区間では面積が小さくなりやすいです。'
exam_points:
  - '確率密度関数は連続型に使います。'
  - '1 点の高さを確率と読まないようにします。'
  - '区間の確率は積分、つまり面積で求めます。'
  - '全体の面積は 1 です。'
formulas:
  - name: '区間確率'
    latex: 'P(a\le X\le b)=\int_a^b f(x)\,dx'
    description: '連続型では、区間に対応する密度の面積が確率です。'
    conditions:
      - '$f(x)$ は確率密度関数です。'
  - name: '全体の面積'
    latex: '\int_{-\infty}^{\infty}f(x)\,dx=1'
    description: '密度関数全体の面積は 1 になります。'
    conditions:
      - '$f(x)\ge 0$ です。'
rigorous_explanation:
  - '確率密度関数は、連続型確率変数の分布を面積で表すための関数です。'
  - '連続型では、通常 $P(X=x)=0$ であり、区間の確率を考えます。'
  - '累積分布関数は、密度を左から積み上げた関数として理解できます。'
common_mistakes:
  - '密度の高さをそのまま確率だと思うこと'
  - '連続型で 1 点ちょうどの確率を大きな値として読んでしまうこと'
  - '面積が 1 になる条件を忘れること'
  - '確率質量関数と同じ感覚で点ごとの確率を読むこと'
related_terms:
  - 'cumulative-distribution-function'
  - 'normal-distribution'
references:
  - title: '統計検定2級 公式問題集'
    type: official
  - title: '統計学入門'
    type: textbook
updated_at: 2026-04-17
aliases:
  - 'PDF'
tags:
  - '確率分布'
  - '連続型'
  - '確率密度関数'
sort_order: 320
---

`probability-density-function` は連続型分布の曲線です。`normal-distribution` の曲線を読むときも、曲線の高さではなく面積を確率として読む点が重要です。
