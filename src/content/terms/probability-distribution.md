---
title: '確率分布'
slug: 'probability-distribution'
exam_scope:
  - 'statistics_grade_2'
level: 'foundation'
status: published
category: 'probability_distribution'
short_definition: '確率変数の値と、その起こりやすさの対応をまとめたものです。'
definition: '確率分布は、確率変数がどの値をどれくらいの確率で取るかを表すものです。離散型では値ごとの確率、連続型では密度や累積分布関数を使って表します。'
intuition:
  - '確率分布は、値の出やすさの地図です。'
  - 'どの値が起こりやすく、どの値が起こりにくいかをまとめます。'
  - 'サイコロなら 1 から 6 が同じ高さの棒になります。'
  - '正規分布のような連続型では、曲線の下の面積として確率を読みます。'
visual_explanation:
  - '離散型では、値ごとに確率の棒を立てると分布が見えます。'
  - '連続型では、滑らかな曲線の下の面積として区間の確率を見ます。'
  - '分布が分かると、期待値や分散を計算できます。'
where_it_appears:
  - '二項分布、正規分布など個別の分布を学ぶ入口'
  - '期待値や分散を確率変数に対して求めるとき'
  - '標本平均や検定統計量の分布を考えるとき'
practical_examples:
  - title: 'サイコロの分布'
    description: '公平なサイコロでは、1 から 6 の各値がそれぞれ $1/6$ の確率を持ちます。これが出目の確率分布です。'
  - title: '成功回数の分布'
    description: '10 回の試行で成功回数を数えると、0 回から 10 回までの値に確率が割り当てられます。この対応を分布として見ます。'
exam_points:
  - '確率分布は、確率変数の値と確率の対応です。'
  - '離散型では確率の合計が 1 になります。'
  - '連続型では密度の面積が 1 になります。'
  - '期待値や分散は分布に基づいて決まります。'
formulas:
  - name: '離散型の全確率'
    latex: '\sum_x p(x)=1'
    description: '離散型では、取りうる値すべての確率を足すと 1 になります。'
    conditions:
      - '$p(x)=P(X=x)$ です。'
  - name: '連続型の全確率'
    latex: '\int_{-\infty}^{\infty} f(x)\,dx=1'
    description: '連続型では、密度関数の全体の面積が 1 になります。'
    conditions:
      - '$f(x)$ は確率密度関数です。'
rigorous_explanation:
  - '確率分布は、確率変数に確率構造を与えるものです。'
  - '離散型では点ごとの確率を直接扱います。'
  - '連続型では 1 点の確率ではなく、区間の確率を面積として扱います。'
common_mistakes:
  - '値の一覧だけを確率分布だと思うこと'
  - '連続型で 1 点の確率を棒の高さとして読んでしまうこと'
  - '確率の合計や密度の面積が 1 になる条件を忘れること'
  - '確率変数と確率分布を同じものとして扱うこと'
related_terms:
  - 'probability-mass-function'
  - 'probability-density-function'
  - 'cumulative-distribution-function'
references:
  - title: '統計検定2級 公式問題集'
    type: official
  - title: '統計学入門'
    type: textbook
updated_at: 2026-04-17
aliases: []
tags:
  - '確率分布'
  - '確率変数'
  - '分布'
sort_order: 300
---

`probability-distribution` は個別の分布を学ぶ入口です。離散型は `probability-mass-function`、連続型は `probability-density-function`、累積した見方は `cumulative-distribution-function` で整理します。
