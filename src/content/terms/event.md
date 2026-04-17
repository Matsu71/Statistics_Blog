---
title: '事象'
slug: 'event'
exam_scope:
  - 'statistics_grade_2'
level: 'foundation'
status: published
category: 'probability'
short_definition: '標本空間の中で、確率を考えたい結果のまとまりです。'
definition: '事象は、標本空間の部分集合です。サイコロで偶数が出る事象なら、標本空間 {1,2,3,4,5,6} の中の {2,4,6} です。'
intuition:
  - '事象は、「この条件を満たしたら起きたと言う」と決める問いです。'
  - '標本空間が全体の箱なら、事象はその中で注目して色を付けた部分です。'
  - '1 つの結果だけでなく、複数の結果をまとめて 1 つの事象にできます。'
  - '確率は、事象がどれくらい起こりやすいかを表します。'
visual_explanation:
  - 'サイコロの標本空間 {1,2,3,4,5,6} のうち、偶数の事象は {2,4,6} です。'
  - '「3 以上が出る」は {3,4,5,6} で、別の事象です。'
  - '同じ標本空間の中で、目的に合わせて注目する部分を変えるのが事象です。'
where_it_appears:
  - '確率を分子と分母で計算する基本問題'
  - '和事象、積事象、補事象を考えるとき'
  - '条件付き確率や独立の前提を整理するとき'
practical_examples:
  - title: '偶数が出る事象'
    description: 'サイコロで偶数が出る事象は {2,4,6} です。標本空間のうち、条件を満たす結果だけを集めます。'
  - title: '補事象を見る'
    description: '「偶数が出る」の補事象は「偶数が出ない」、つまり {1,3,5} です。起きない側を見ると確率計算が楽になることがあります。'
exam_points:
  - '事象は標本空間の部分集合です。'
  - '和事象は「少なくともどちらか」、積事象は「両方」です。'
  - '補事象は、標本空間の中でその事象が起こらない部分です。'
  - '条件付き確率では、どの事象を条件としているかを確認します。'
formulas:
  - name: '事象'
    latex: 'A\subseteq\Omega'
    description: '事象 $A$ は標本空間 $\Omega$ の部分集合として表せます。'
    conditions:
      - '$A$ は事象です。'
      - '$\Omega$ は標本空間です。'
  - name: '補事象'
    latex: 'A^c=\Omega\setminus A'
    description: '事象 $A$ が起こらない結果全体を補事象と呼びます。'
    conditions:
      - '$A^c$ は $A$ の補事象です。'
rigorous_explanation:
  - '事象は集合として扱うため、和、積、補集合の考え方が使えます。'
  - '確率の計算では、どの結果がその事象に含まれるかを明確にすることが重要です。'
  - '条件付き確率では、条件となる事象の中に標本空間を狭めて考えます。'
common_mistakes:
  - '事象を 1 つの結果だけだと思うこと'
  - '標本空間を確認せずに事象だけを考えること'
  - '和事象と積事象を取り違えること'
  - '補事象を「反対の言葉」だけで考え、集合として確認しないこと'
related_terms:
  - 'probability'
  - 'conditional-probability'
references:
  - title: '統計検定2級 公式問題集'
    type: official
  - title: '統計学入門'
    type: textbook
updated_at: 2026-04-17
aliases: []
tags:
  - '確率'
  - '集合'
  - '事象'
sort_order: 220
---

`event` は `sample-space` の一部です。`probability` では、その事象が標本空間の中でどれくらい起こりやすいかを数で表します。`conditional-probability` では、ある事象が起きたという条件のもとで別の事象を見ます。
