---
title: 'ポアソン分布'
slug: 'poisson-distribution'
exam_scope:
  - 'statistics_grade_2'
level: 'standard'
status: published
category: 'probability_distribution'
short_definition: '一定の時間や範囲で起こる回数を表す離散分布です。'
definition: 'ポアソン分布は、一定の時間や空間の中で、まれな出来事が何回起こるかを表す離散分布です。平均発生回数を $\lambda$ として表します。'
intuition:
  - 'ポアソン分布は、「一定の範囲で何回起きるか」を数える分布です。'
  - '1 時間あたりの電話件数、1 ページあたりの誤字数のような回数データで使われます。'
  - '平均回数 $\lambda$ が分布の中心と広がりを決めます。'
  - '二項分布で試行回数が多く、成功確率が小さい場面の近似として出ることもあります。'
visual_explanation:
  - '横軸に 0 回、1 回、2 回と発生回数を並べ、各回数の確率を棒で表します。'
  - '$\lambda$ が小さいと 0 回や 1 回に確率が集まりやすくなります。'
  - '$\lambda$ が大きくなると、山は右へ移動します。'
where_it_appears:
  - '一定時間内の到着件数や発生回数を考えるとき'
  - '二項分布の近似として'
  - '平均と分散が同じ分布の例として'
practical_examples:
  - title: '電話の件数'
    description: 'コールセンターに 1 分あたり平均 3 件の電話が来るなら、1 分間に何件来るかをポアソン分布で近似できることがあります。'
  - title: '誤字の数'
    description: '1 ページあたりの誤字数のように、一定範囲での発生回数を見るときに使われます。'
exam_points:
  - 'ポアソン分布は回数を表す離散分布です。'
  - 'パラメータ $\lambda$ は平均発生回数です。'
  - '期待値と分散はどちらも $\lambda$ です。'
  - '二項分布との関係が問われることがあります。'
formulas:
  - name: 'ポアソン分布の確率'
    latex: 'P(X=k)=\frac{e^{-\lambda}\lambda^k}{k!}'
    description: '一定範囲で $k$ 回起こる確率を表します。'
    conditions:
      - '$\lambda>0$ は平均発生回数です。'
      - '$k=0,1,2,\ldots$ です。'
  - name: '期待値と分散'
    latex: 'E[X]=\lambda,\quad \mathrm{Var}(X)=\lambda'
    description: 'ポアソン分布では平均と分散が同じ値になります。'
    conditions:
      - '$X$ はポアソン分布に従います。'
rigorous_explanation:
  - 'ポアソン分布は、非負整数を取る離散分布です。'
  - '平均発生回数 $\lambda$ が大きいほど、分布の山は大きな回数側へ動きます。'
  - '二項分布で $n$ が大きく $p$ が小さく、$np$ が一定程度のときの近似として使われることがあります。'
common_mistakes:
  - '割合や連続量にそのままポアソン分布を使うこと'
  - '$\lambda$ を確率だと思うこと'
  - '平均と分散が同じという性質を忘れること'
  - '発生回数ではなく発生時刻そのものの分布だと考えること'
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
  - 'ポアソン分布'
sort_order: 360
---

`poisson-distribution` は回数データを扱う分布です。`binomial-distribution` と同じく離散型ですが、固定回数の試行中の成功回数ではなく、一定範囲での発生回数を見ます。
