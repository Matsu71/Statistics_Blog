---
title: '累積分布関数'
slug: 'cumulative-distribution-function'
exam_scope:
  - 'statistics_grade_2'
level: 'advanced'
status: published
category: 'probability_distribution'
short_definition: '確率変数がある値以下になる確率を積み上げて表す関数です。'
definition: '累積分布関数は、$F(x)=P(X\le x)$ で定義される関数です。値 $x$ までにどれくらいの確率が積み上がっているかを表します。'
intuition:
  - '累積分布関数は、左から順に確率を足し上げたものです。'
  - '$x$ が大きくなるほど、$X\le x$ に含まれる範囲が広がるため、値は小さくなりません。'
  - '最終的には全体の確率 1 に近づきます。'
  - '正規分布表で読む累積確率は、累積分布関数の考え方です。'
visual_explanation:
  - '密度曲線なら、左端から $x$ までの面積を塗ったものが $F(x)$ です。'
  - '離散型なら、$x$ 以下の値に対応する棒の高さを足します。'
  - '上側確率を求めるときは、$1-F(x)$ を使います。'
where_it_appears:
  - '正規分布表で $P(Z\le z)$ を読むとき'
  - '分布の下側確率や上側確率を求めるとき'
  - '離散型と連続型を共通の形で扱うとき'
practical_examples:
  - title: 'テスト点の下側割合'
    description: '$F(70)=0.8$ なら、70 点以下の人が全体の 80% いると読めます。'
  - title: '上側確率に直す'
    description: '$P(X>70)$ を求めたいときは、連続型ならおおむね $1-F(70)$ と考えます。'
exam_points:
  - '累積分布関数は $F(x)=P(X\le x)$ です。'
  - '$F(x)$ は 0 から 1 の範囲にあります。'
  - '$x$ が大きくなると、$F(x)$ は小さくなりません。'
  - '上側確率や区間確率を求めるときに使います。'
formulas:
  - name: '累積分布関数'
    latex: 'F(x)=P(X\le x)'
    description: '確率変数 $X$ が $x$ 以下になる確率を表します。'
    conditions:
      - '$F(x)$ は累積分布関数です。'
  - name: '連続型での表現'
    latex: 'F(x)=\int_{-\infty}^{x} f(t)\,dt'
    description: '密度関数を左から $x$ まで積分すると累積確率になります。'
    conditions:
      - '$f(t)$ は確率密度関数です。'
rigorous_explanation:
  - '累積分布関数は、離散型にも連続型にも使える分布の表現です。'
  - '連続型では密度の面積を左から積み上げたものとして読めます。'
  - '区間確率は、累積分布関数の差 $F(b)-F(a)$ として求められます。'
common_mistakes:
  - '$F(x)$ を $P(X=x)$ だと思うこと'
  - '上側確率と下側確率を取り違えること'
  - '累積なので単調に増える性質を忘れること'
  - '正規分布表が累積確率か上側確率か確認しないこと'
related_terms:
  - 'probability-mass-function'
  - 'probability-density-function'
references:
  - title: '統計検定2級 公式問題集'
    type: official
  - title: '統計学入門'
    type: textbook
updated_at: 2026-04-17
aliases:
  - 'CDF'
tags:
  - '確率分布'
  - '累積分布関数'
  - '分布'
sort_order: 330
---

`cumulative-distribution-function` は分布を累積して読む見方です。`probability-mass-function` や `probability-density-function` が値や密度を表すのに対し、累積分布関数は「ここまでの確率」を表します。
