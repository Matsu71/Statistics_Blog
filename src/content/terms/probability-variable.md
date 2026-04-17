---
title: '確率変数'
slug: 'probability-variable'
exam_scope:
  - 'statistics_grade_2'
level: 'foundation'
status: published
category: 'probability'
short_definition: '偶然の結果に応じて値が決まる変数です。'
definition: '確率変数は、試行の結果を数値に対応させる変数です。サイコロの出目を $X$ と置くと、$X$ は 1 から 6 の値を取る確率変数として扱えます。'
intuition:
  - '確率変数は、偶然の結果を計算しやすい数に変えるラベルです。'
  - '結果そのものではなく、結果に対応して決まる数値を見ます。'
  - '確率変数を使うと、平均や分散のような量を確率の世界でも扱えます。'
  - '値ごとの起こりやすさをまとめたものが確率分布です。'
visual_explanation:
  - '標本空間の各結果から、数値の箱へ矢印を引くイメージです。'
  - '硬貨で表なら 1、裏なら 0 と対応させれば、成功を数で扱えます。'
  - '同じ標本空間でも、何を数値化するかで確率変数は変わります。'
where_it_appears:
  - '期待値や分散を確率の文脈で定義するとき'
  - '二項分布や正規分布など、分布を扱うとき'
  - '標本平均や推定量を確率的に考えるとき'
practical_examples:
  - title: 'サイコロの出目'
    description: 'サイコロを振って出た目を $X$ とすれば、$X$ は 1 から 6 の値を取る確率変数です。'
  - title: '成功回数を数える'
    description: '10 回の試行で成功した回数を $X$ と置くと、$X$ は 0 から 10 の値を取る確率変数です。'
exam_points:
  - '確率変数は、結果を数値に対応させるものです。'
  - '確率変数そのものと、確率そのものを混同しないようにします。'
  - '確率変数の取りうる値と確率の対応が確率分布です。'
  - '離散型と連続型で、確率の読み方が変わります。'
formulas:
  - name: '確率変数'
    latex: 'X:\Omega\to\mathbb{R}'
    description: '標本空間の結果を実数に対応させる関数として確率変数を表せます。'
    conditions:
      - '$\Omega$ は標本空間です。'
      - '$X$ は確率変数です。'
rigorous_explanation:
  - '確率変数は、標本空間の結果そのものではなく、それに対応する数値を扱います。'
  - '確率変数を導入すると、値ごとの確率を分布としてまとめられます。'
  - '期待値は、確率変数の値を確率で重み付けした中心として定義されます。'
common_mistakes:
  - '確率変数を確率そのものだと思うこと'
  - '結果と、その結果に対応する数値を区別しないこと'
  - '確率変数は必ず 0 から 1 の値を取ると思うこと'
  - '確率分布と確率変数を同じものとして扱うこと'
related_terms:
  - 'probability-distribution'
  - 'expected-value'
references:
  - title: '統計検定2級 公式問題集'
    type: official
  - title: '統計学入門'
    type: textbook
updated_at: 2026-04-17
aliases:
  - '確率変量'
tags:
  - '確率'
  - '確率変数'
  - '分布'
sort_order: 270
---

`probability-variable` は `probability-distribution` と `expected-value` の土台です。まず結果を数値に変え、その値がどれくらい出やすいかを分布として整理します。
