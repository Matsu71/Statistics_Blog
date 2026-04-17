---
title: '条件付き確率'
slug: 'conditional-probability'
exam_scope:
  - 'statistics_grade_2'
level: 'standard'
status: published
category: 'probability'
short_definition: 'ある事象が起きたという条件のもとで、別の事象が起こる確率です。'
definition: '条件付き確率は、事象 $B$ が起きたと分かっている状況で、事象 $A$ が起こる確率です。標本空間を $B$ の中に狭めてから、$A$ がどれくらい含まれるかを見ます。'
intuition:
  - '条件付き確率は、見ている全体を条件の中に絞り込む考え方です。'
  - '「全員の中で」ではなく「条件を満たした人の中で」と母集団を狭めます。'
  - '条件を付けると、同じ事象でも確率が変わることがあります。'
  - '独立かどうかを調べるときにも、条件付き確率が基準になります。'
visual_explanation:
  - '標本空間全体のうち、まず事象 $B$ の領域だけを残します。'
  - 'その $B$ の中で、$A$ と重なっている部分がどれくらいあるかを見ます。'
  - '$A$ と $B$ の重なりが大きいほど、$P(A\mid B)$ は大きくなります。'
where_it_appears:
  - '「すでに分かっている条件」がある確率問題'
  - '独立の定義を確認するとき'
  - 'ベイズの定理で条件を入れ替えるとき'
practical_examples:
  - title: 'カードを引く例'
    description: '赤いカードを引いたと分かっているとき、そのカードがハートである確率を考えるなら、全カードではなく赤いカードの中だけで割合を見ます。'
  - title: '条件で全体が変わる'
    description: 'ある検査で陽性だった人の中で実際に病気である確率は、全員の中で病気である確率とは別です。条件によって見ている集団が変わります。'
exam_points:
  - '条件付き確率は、条件となる事象の中に標本空間を狭めて考えます。'
  - '$P(A\mid B)$ と $P(B\mid A)$ は一般には同じではありません。'
  - '分母は条件となる事象の確率です。'
  - '独立なら $P(A\mid B)=P(A)$ になります。'
formulas:
  - name: '条件付き確率'
    latex: 'P(A\mid B)=\frac{P(A\cap B)}{P(B)}'
    description: '事象 $B$ が起きたもとで、$A$ も起きる確率を表します。'
    conditions:
      - '$P(B)>0$ が必要です。'
      - '$A\cap B$ は $A$ と $B$ が同時に起きる事象です。'
rigorous_explanation:
  - '条件付き確率は、確率の基準となる全体を $B$ に取り替える操作です。'
  - '$P(A\mid B)$ は $A$ と $B$ の重なりを $B$ の大きさで割ったものです。'
  - '条件を逆にすると分母が変わるため、$P(A\mid B)$ と $P(B\mid A)$ を区別します。'
common_mistakes:
  - '$P(A\mid B)$ と $P(B\mid A)$ を同じだと思うこと'
  - '分母を $P(A)$ にしてしまうこと'
  - '条件を付けたのに標本空間全体で考え続けること'
  - '条件付き確率と積事象の確率を混同すること'
related_terms:
  - 'independence'
  - 'bayes-theorem'
references:
  - title: '統計検定2級 公式問題集'
    type: official
  - title: '統計学入門'
    type: textbook
updated_at: 2026-04-17
aliases: []
tags:
  - '確率'
  - '条件付き確率'
  - '事象'
sort_order: 240
---

`conditional-probability` は、条件が付いたときに確率の分母が変わることを学ぶページです。`independence` では、条件を付けても確率が変わらない場合を扱います。`bayes-theorem` は条件付き確率を組み替える公式です。
