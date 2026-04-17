---
title: 'ベイズの定理'
slug: 'bayes-theorem'
exam_scope:
  - 'statistics_grade_2'
level: 'advanced'
status: published
category: 'probability'
short_definition: '条件付き確率の向きを入れ替えて考えるための公式です。'
definition: 'ベイズの定理は、$P(A\mid B)$ と $P(B\mid A)$ を結びつける公式です。ある結果 $B$ が分かったあとで、その原因や仮説 $A$ の確率を更新して考えるときに使います。'
intuition:
  - 'ベイズの定理は、「原因から結果」だけでなく「結果から原因」を考える道具です。'
  - '検査で陽性だったとき、実際に病気である確率を考えるような場面で使います。'
  - '条件を逆にすると分母が変わるため、直感だけでは間違えやすいところを式で整理します。'
  - '事前にどれくらい起こりやすいかと、観測結果がどれくらい起こりやすいかを合わせて考えます。'
visual_explanation:
  - '全体を原因 $A$ と $A^c$ に分け、それぞれから結果 $B$ が起こる枝を考えます。'
  - '$B$ が起きた後は、$B$ に到達した枝だけを集めて、その中で $A$ から来た割合を見ます。'
  - '樹形図で分母と分子を整理すると、条件の向きの違いが見えやすくなります。'
where_it_appears:
  - '検査の陽性・陰性のように、結果から原因を考える問題'
  - '条件付き確率の向きを入れ替える問題'
  - '事前確率と事後確率を区別したい場面'
practical_examples:
  - title: '検査結果の読み取り'
    description: '病気の人が少ない集団では、検査が陽性でも実際に病気である確率は直感より小さくなることがあります。ベイズの定理は分母に陽性全体を置いて整理します。'
  - title: '原因を逆向きに考える'
    description: '雨の日に傘を持つ人が多いとしても、傘を持っている人が必ず雨を経験したとは限りません。条件の向きを入れ替えると意味が変わります。'
exam_points:
  - '$P(A\mid B)$ と $P(B\mid A)$ を取り違えないことが重要です。'
  - '分母は、結果 $B$ が起こる全体の確率です。'
  - '樹形図で枝の確率をかけ、同じ結果に到達する経路を足すと整理しやすいです。'
  - '事前確率、尤度、事後確率の役割を区別します。'
formulas:
  - name: 'ベイズの定理'
    latex: 'P(A\mid B)=\frac{P(B\mid A)P(A)}{P(B)}'
    description: '結果 $B$ が起きたもとで、原因や仮説 $A$ が成り立つ確率を表します。'
    conditions:
      - '$P(B)>0$ が必要です。'
      - '$P(A)$ は事前の起こりやすさです。'
  - name: '分母の分解'
    latex: 'P(B)=P(B\mid A)P(A)+P(B\mid A^c)P(A^c)'
    description: '事象 $A$ とその補事象で場合分けして、$B$ が起こる全体の確率を求めます。'
    conditions:
      - '$A^c$ は $A$ の補事象です。'
rigorous_explanation:
  - 'ベイズの定理は、条件付き確率の定義 $P(A\mid B)=P(A\cap B)/P(B)$ と $P(B\mid A)=P(A\cap B)/P(A)$ から導けます。'
  - '分母 $P(B)$ は、観測された結果が起こる全ての経路を足したものです。'
  - '条件の向きを入れ替えると、分母が変わるため値も一般には変わります。'
common_mistakes:
  - '$P(A\mid B)$ と $P(B\mid A)$ を同じだと思うこと'
  - '分母に $P(A)$ を置いてしまうこと'
  - '事前確率を無視して検査の精度だけで判断すること'
  - '補事象から $B$ が起こる経路を足し忘れること'
related_terms:
  - 'conditional-probability'
  - 'probability'
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
  - 'ベイズ'
sort_order: 260
---

`bayes-theorem` は `conditional-probability` の応用です。`probability` と `event` の基本に戻って、分母が何を表しているかを確認しながら読むと混乱しにくくなります。
