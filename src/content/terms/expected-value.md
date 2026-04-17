---
title: '期待値'
slug: 'expected-value'
exam_scope:
  - 'statistics_grade_2'
level: 'standard'
status: published
category: 'probability'
short_definition: '確率に応じて重み付けした、確率変数の平均的な中心です。'
definition: '期待値は、確率変数の取りうる値を、その値が起こる確率で重み付けして合計したものです。長く繰り返したときの平均の目安として読めます。'
intuition:
  - '期待値は、確率の世界での平均です。'
  - '起こりやすい値ほど重く、起こりにくい値ほど軽く見ます。'
  - '1 回で必ず期待値そのものが出るわけではありません。'
  - '長く繰り返したとき、平均がどのあたりに落ち着きそうかを見る指標です。'
visual_explanation:
  - '値ごとの棒に確率という重みを付けて、全体のつり合いの位置を見るイメージです。'
  - 'サイコロなら 1 から 6 が同じ確率なので、中心は 3.5 になります。'
  - '確率が偏っていると、期待値も起こりやすい値の側へ寄ります。'
where_it_appears:
  - '確率分布の中心を表すとき'
  - '二項分布の平均を求めるとき'
  - '分散を定義する前に、中心を決めるとき'
practical_examples:
  - title: 'サイコロの期待値'
    description: '公平なサイコロの期待値は $(1+2+3+4+5+6)/6=3.5$ です。1 回で 3.5 が出るわけではなく、長期的な平均の目安です。'
  - title: 'くじの期待値'
    description: '100 円を 0.1 の確率で得て、0 円を 0.9 の確率で得るくじの期待値は 10 円です。金額に確率を掛けて合計します。'
exam_points:
  - '期待値は、値に確率を掛けて合計します。'
  - '期待値は 1 回の結果を予測する値ではありません。'
  - '離散型では和、連続型では積分で表します。'
  - '分散は、期待値からのずれを使って定義されます。'
formulas:
  - name: '離散型の期待値'
    latex: 'E[X]=\sum_x x p(x)'
    description: '取りうる値 $x$ に、その確率 $p(x)$ を掛けて合計します。'
    conditions:
      - '$p(x)=P(X=x)$ です。'
  - name: '線形性'
    latex: 'E[aX+b]=aE[X]+b'
    description: '期待値は定数倍と足し算に対して扱いやすい性質を持ちます。'
    conditions:
      - '$a,b$ は定数です。'
rigorous_explanation:
  - '期待値は、確率分布に基づいて定まる中心です。'
  - '離散型では全ての値について $x p(x)$ を足し合わせます。'
  - '期待値は実際に取りうる値とは限りません。サイコロの期待値 3.5 は出目としては存在しません。'
common_mistakes:
  - '期待値が 1 回ごとに必ず出る値だと思うこと'
  - '確率を掛けずに値だけを平均すること'
  - '期待値と最頻値を混同すること'
  - '期待値だけでリスクやばらつきまで分かると思うこと'
related_terms:
  - 'variance'
  - 'probability-distribution'
references:
  - title: '統計検定2級 公式問題集'
    type: official
  - title: '統計学入門'
    type: textbook
updated_at: 2026-04-17
aliases: []
tags:
  - '確率'
  - '期待値'
  - '平均'
sort_order: 280
---

`expected-value` は `mean` の考え方を確率分布に広げたものです。`variance` では、この期待値からのずれを使って散らばりを測ります。`probability-distribution` と一緒に読むと、値と確率の対応が見えやすくなります。
