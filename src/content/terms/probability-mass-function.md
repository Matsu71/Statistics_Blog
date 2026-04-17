---
title: '確率質量関数'
slug: 'probability-mass-function'
exam_scope:
  - 'statistics_grade_2'
level: 'advanced'
status: published
category: 'probability_distribution'
short_definition: '離散型確率変数が各値を取る確率を表す関数です。'
definition: '確率質量関数は、離散型確率変数 $X$ が値 $x$ を取る確率 $P(X=x)$ を表す関数です。値ごとの確率を直接並べて見るための道具です。'
intuition:
  - '確率質量関数は、離散型の分布を棒の高さで表すものです。'
  - 'サイコロの 1, 2, 3, 4, 5, 6 にそれぞれ確率を置くイメージです。'
  - '確率は各点に乗っていて、すべて足すと 1 になります。'
  - '連続型の確率密度関数とは、1 点の確率を直接扱うかどうかが違います。'
visual_explanation:
  - '横軸に値、縦軸にその値を取る確率を置く棒グラフを考えます。'
  - '棒の高さをすべて足すと 1 になります。'
  - '二項分布やベルヌーイ分布は、確率質量関数で表せます。'
where_it_appears:
  - '離散型確率分布を表すとき'
  - 'ベルヌーイ分布や二項分布を定義するとき'
  - '期待値を和で計算するとき'
practical_examples:
  - title: 'サイコロの確率質量関数'
    description: '公平なサイコロでは、$p(1)=p(2)=\cdots=p(6)=1/6$ です。値ごとの確率を関数としてまとめます。'
  - title: '成功回数の確率'
    description: '10 回中 3 回成功する確率のように、成功回数ごとの確率を並べると確率質量関数になります。'
exam_points:
  - '確率質量関数は離散型に使います。'
  - '$p(x)=P(X=x)$ と読みます。'
  - 'すべての $x$ について $p(x)$ を足すと 1 です。'
  - '確率密度関数と混同しないようにします。'
formulas:
  - name: '確率質量関数'
    latex: 'p(x)=P(X=x)'
    description: '離散型確率変数 $X$ が値 $x$ を取る確率を表します。'
    conditions:
      - '$p(x)\ge 0$ です。'
  - name: '全確率'
    latex: '\sum_x p(x)=1'
    description: '取りうる値すべての確率を合計すると 1 になります。'
    conditions:
      - '和は $X$ が取りうる全ての値について取ります。'
rigorous_explanation:
  - '確率質量関数は、離散型分布の確率を点ごとに与える関数です。'
  - '各値の確率は 0 以上で、全ての値について合計すると 1 になります。'
  - '期待値は $\sum_x x p(x)$ のように、確率質量関数を重みとして計算します。'
common_mistakes:
  - '確率質量関数を連続型にもそのまま使うこと'
  - '確率の合計が 1 になることを確認しないこと'
  - '値そのものと確率を混同すること'
  - '確率密度関数の高さと同じ読み方をすること'
related_terms:
  - 'probability-density-function'
  - 'bernoulli-distribution'
references:
  - title: '統計検定2級 公式問題集'
    type: official
  - title: '統計学入門'
    type: textbook
updated_at: 2026-04-17
aliases:
  - 'PMF'
tags:
  - '確率分布'
  - '離散型'
  - '確率質量関数'
sort_order: 310
---

`probability-mass-function` は離散型分布の表し方です。`probability-density-function` は連続型、`cumulative-distribution-function` は値以下になる確率を積み上げた見方です。
