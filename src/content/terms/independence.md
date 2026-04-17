---
title: '独立'
slug: 'independence'
exam_scope:
  - 'statistics_grade_2'
level: 'standard'
status: published
category: 'probability'
short_definition: '一方の事象が起きても、もう一方の起こりやすさが変わらない関係です。'
definition: '独立とは、事象 $B$ が起きたと分かっても、事象 $A$ の確率が変わらない関係です。式では $P(A\cap B)=P(A)P(B)$ と表せます。'
intuition:
  - '独立は、情報が増えても相手の起こりやすさが変わらない関係です。'
  - '硬貨を 2 回投げるとき、1 回目の結果は 2 回目の表の出やすさを変えません。'
  - '無関係そうに見えることと、統計的に独立であることは同じではありません。'
  - '条件付き確率で見ると、独立なら $P(A\mid B)=P(A)$ です。'
visual_explanation:
  - '独立なら、$B$ の中で $A$ が占める割合が、全体で $A$ が占める割合と同じになります。'
  - '事象の重なりが単なるかけ算 $P(A)P(B)$ で表せるとき、独立と判断できます。'
  - '重なりが多すぎたり少なすぎたりすれば、独立ではない可能性があります。'
where_it_appears:
  - '反復試行や二項分布の前提を確認するとき'
  - '条件付き確率の問題で、条件を付けても変わらないかを見るとき'
  - '確率の積の形で計算してよいか判断するとき'
practical_examples:
  - title: '硬貨を 2 回投げる'
    description: '1 回目が表だったことは、2 回目が表になる確率を変えません。このような反復試行では独立を仮定しやすいです。'
  - title: '独立でない例'
    description: '雨が降ることと傘を持っていることは関係がありそうです。一方を知ると他方の起こりやすさが変わるなら、独立とは言えません。'
exam_points:
  - '独立なら $P(A\cap B)=P(A)P(B)$ です。'
  - '独立なら $P(A\mid B)=P(A)$ です。'
  - '排反と独立は別の概念です。'
  - '「関係がなさそう」という直感だけで独立と判断しません。'
formulas:
  - name: '独立の条件'
    latex: 'P(A\cap B)=P(A)P(B)'
    description: '2 つの事象が独立なら、同時に起きる確率はそれぞれの確率の積になります。'
    conditions:
      - '$A$ と $B$ は事象です。'
  - name: '条件付き確率による表現'
    latex: 'P(A\mid B)=P(A)'
    description: '条件 $B$ を知っても $A$ の確率が変わらないことを表します。'
    conditions:
      - '$P(B)>0$ が必要です。'
rigorous_explanation:
  - '独立は、条件付き確率を使って「情報を得ても確率が変わらない」と定義できます。'
  - '排反は同時に起きない関係なので、独立とは意味が違います。'
  - '確率が 0 でない排反事象は、通常は独立ではありません。'
common_mistakes:
  - '排反と独立を同じ意味だと思うこと'
  - '現実的に関係が薄そうなら必ず独立だと考えること'
  - '独立の確認をせずに確率をかけ算すること'
  - '条件付き確率が変わるかどうかを見ないこと'
related_terms:
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
  - '独立'
  - '条件付き確率'
sort_order: 250
---

`independence` は `conditional-probability` とセットで理解すると安定します。条件を付けても確率が変わらないときに独立と読み、二項分布のような反復試行の前提にもなります。
