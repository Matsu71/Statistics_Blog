---
title: 'ベルヌーイ分布'
slug: 'bernoulli-distribution'
exam_scope:
  - 'statistics_grade_2'
level: 'standard'
status: published
category: 'probability_distribution'
short_definition: '成功か失敗かの 1 回の試行を表す、最も基本的な離散分布です。'
definition: 'ベルヌーイ分布は、成功を 1、失敗を 0 とする 1 回の試行を表す分布です。成功確率を $p$ とすると、$P(X=1)=p$、$P(X=0)=1-p$ です。'
intuition:
  - 'ベルヌーイ分布は、はい/いいえ、成功/失敗を 1 回だけ見る分布です。'
  - '表が出たら 1、裏が出たら 0 のように、結果を 0 と 1 にします。'
  - '二項分布は、このベルヌーイ試行を何回も独立に繰り返した成功回数の分布です。'
  - '確率 $p$ が大きいほど、1 が出やすくなります。'
visual_explanation:
  - '横軸に 0 と 1 だけを置き、それぞれに $1-p$ と $p$ の棒を立てます。'
  - '$p=0.5$ なら 0 と 1 の棒は同じ高さです。'
  - '$p$ が 1 に近づくほど、1 の棒が高くなります。'
where_it_appears:
  - '成功/失敗の 1 回の試行をモデル化するとき'
  - '二項分布の前提として'
  - '0/1 データの期待値や分散を考えるとき'
practical_examples:
  - title: '硬貨の表を成功とする'
    description: '硬貨で表が出たら $X=1$、裏なら $X=0$ とすれば、成功確率 $p=1/2$ のベルヌーイ分布です。'
  - title: '合否データ'
    description: 'ある問題に正解したら 1、不正解なら 0 とすれば、1 回分の結果をベルヌーイ分布として扱えます。'
exam_points:
  - '取りうる値は 0 と 1 です。'
  - '成功確率を $p$、失敗確率を $1-p$ とします。'
  - '二項分布はベルヌーイ試行の繰り返しとして理解します。'
  - '期待値は $p$、分散は $p(1-p)$ です。'
formulas:
  - name: 'ベルヌーイ分布'
    latex: 'P(X=x)=p^x(1-p)^{1-x}\quad (x=0,1)'
    description: '成功なら $x=1$、失敗なら $x=0$ として確率をまとめて表します。'
    conditions:
      - '$0\le p\le 1$ です。'
  - name: '期待値と分散'
    latex: 'E[X]=p,\quad \mathrm{Var}(X)=p(1-p)'
    description: '0/1 の値を取るため、成功確率 $p$ がそのまま期待値になります。'
    conditions:
      - '$X$ はベルヌーイ分布に従います。'
rigorous_explanation:
  - 'ベルヌーイ分布は、0 と 1 の 2 値だけを取る離散分布です。'
  - '期待値は $0\cdot(1-p)+1\cdot p=p$ です。'
  - '独立なベルヌーイ試行を複数回足し合わせると、成功回数は二項分布に従います。'
common_mistakes:
  - 'ベルヌーイ分布と二項分布を同じものだと思うこと'
  - '成功確率と失敗確率を足して 1 になることを忘れること'
  - '0/1 以外の値をそのままベルヌーイ分布として扱うこと'
  - '独立な繰り返しの前提を確認しないこと'
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
  - 'ベルヌーイ分布'
sort_order: 340
---

`bernoulli-distribution` は `binomial-distribution` の土台です。1 回の成功/失敗をベルヌーイ分布で表し、それを独立に繰り返した成功回数を二項分布で扱います。
