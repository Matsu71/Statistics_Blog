---
title: '二項分布'
slug: 'binomial-distribution'
exam_scope:
  - 'statistics_grade_2'
level: 'standard'
status: published
category: 'probability_distribution'
short_definition: '独立な成功/失敗の試行を繰り返したときの、成功回数の分布です。'
definition: '二項分布は、成功確率 $p$ のベルヌーイ試行を独立に $n$ 回繰り返したとき、成功回数 $X$ が従う分布です。'
intuition:
  - '二項分布は、何回成功するかを数える分布です。'
  - '同じ条件の試行を、独立に何回も繰り返すことが前提です。'
  - 'コインを 10 回投げて表が何回出るか、のような問題で使います。'
  - '成功確率 $p$ と試行回数 $n$ が分布の形を決めます。'
visual_explanation:
  - '横軸に成功回数 0,1,2,...,n を並べ、それぞれの確率を棒で表します。'
  - '$p=0.5$ なら中央付近が高くなりやすく、$p$ が小さいと左側に山が寄ります。'
  - '$n$ が大きいと、条件によって正規分布に近い形に見えることがあります。'
where_it_appears:
  - '反復試行の成功回数を求める問題'
  - '正規近似や標本比率の入口として'
  - '期待値と分散の公式を使う確率分布の問題'
practical_examples:
  - title: '10 回のコイン投げ'
    description: '公平な硬貨を 10 回投げて表が 3 回出る確率は、二項分布で考えられます。成功を表、成功確率を $p=1/2$ とします。'
  - title: '合格回数を数える'
    description: '同じ条件の小テストを 5 回受け、それぞれ合格確率が同じで独立だと考えるなら、合格回数は二項分布でモデル化できます。'
exam_points:
  - '二項分布では、試行回数 $n$、成功確率 $p$、独立性を確認します。'
  - '確率は組合せ $\binom{n}{k}$ を使って求めます。'
  - '期待値は $np$、分散は $np(1-p)$ です。'
  - 'ベルヌーイ分布を繰り返した成功回数として理解します。'
formulas:
  - name: '二項分布の確率'
    latex: 'P(X=k)=\binom{n}{k}p^k(1-p)^{n-k}'
    description: '成功回数が $k$ 回になる確率を表します。'
    conditions:
      - '$n$ は試行回数です。'
      - '$p$ は成功確率です。'
      - '$k=0,1,\ldots,n$ です。'
  - name: '期待値と分散'
    latex: 'E[X]=np,\quad \mathrm{Var}(X)=np(1-p)'
    description: '二項分布の中心と散らばりを表す公式です。'
    conditions:
      - '$X\sim\mathrm{Bin}(n,p)$ です。'
rigorous_explanation:
  - '二項分布では、$k$ 回成功し $n-k$ 回失敗する確率は $p^k(1-p)^{n-k}$ です。'
  - '成功する位置の選び方が $\binom{n}{k}$ 通りあるため、この組合せを掛けます。'
  - '独立性と同じ成功確率という前提が崩れると、二項分布として扱えません。'
common_mistakes:
  - '独立でない試行にも二項分布を使うこと'
  - '成功確率が毎回同じか確認しないこと'
  - '$\binom{n}{k}$ を掛け忘れること'
  - '成功回数ではなく、成功する順番そのものを分布の値だと思うこと'
related_terms:
  - 'normal-distribution'
  - 'expected-value'
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
  - '二項分布'
sort_order: 350
---

`binomial-distribution` は `bernoulli-distribution` を複数回足し合わせた成功回数の分布です。`expected-value` とあわせて読むと、$np$ がなぜ中心になるのかを整理しやすくなります。
