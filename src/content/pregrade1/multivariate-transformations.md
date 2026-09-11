---
lesson_id: P05
slug: multivariate-transformations
title: 多変量の変数変換とヤコビアン
description: 二変数を和と差に変えると、長方形だった範囲がひし形になります。密度の式だけでなく、変換後の値域と面積の倍率を一緒に求めます。
status: published
goals:
  - 二変数の逆変換と、取り得る組の範囲を求める。
  - ヤコビアンの絶対値で密度を変換する。
  - 変換後の密度の積への分解と値域から、独立性を確かめる。
prerequisites: [G08, G10, P02]
reading_minutes: 13
practice_minutes: 10
practice_count: 4
review_status: self_checked
updated_at: 2026-09-11
---

## 何を新しい座標として見るか

XとYが独立に0〜1の一様分布に従う仮想モデルを考えます。元の(x,y)は単位正方形の中にあり、同時密度は1です。新たにS=X+Y、D=X−Yを作り、和と差の同時分布を求めます。

SとDの範囲を別々に見ると、0<S<2、−1<D<1です。しかし、その長方形の中のすべての組が可能なわけではありません。Sが小さいのにDだけ大きいと、元のXかYが負になります。密度の式を作る前に、取り得る組の範囲を考えます。

## 逆変換を解き、元の条件へ代入する

和と差の連立方程式を解くと、x=(s+d)/2、y=(s−d)/2です。0<x<1と0<y<1へ代入して整理すると、

$$
0<s<2,\qquad \max(-s,s-2)<d<\min(s,2-s).
$$

s=0.5なら−0.5<d<0.5、s=1なら−1<d<1、s=1.5なら−0.5<d<0.5です。範囲は(s,d)平面のひし形になります。境界はこの連続分布の確率0なので、密度の値を境界でどう置くかは区間確率を変えません。

<figure><svg viewBox="0 0 450 345" role="img" aria-labelledby="p05-figure-title p05-figure-desc"><title id="p05-figure-title">和と差が取る値の組</title><desc id="p05-figure-desc">横軸S、縦軸D。可能な範囲は頂点0,0、1,1、2,0、1,-1のひし形。Sが0.5の縦断面ではDは-0.5から0.5。</desc><path d="M70 305V35M55 170H410" fill="none" stroke="currentColor" stroke-width="2"/><path d="M70 170L220 60L370 170L220 280Z" fill="#d6eaee" stroke="#144a56" stroke-width="3"/><path d="M145 115V225" stroke="#8b4224" stroke-width="4"/><g fill="currentColor" font-size="18"><text x="52" y="192">0</text><text x="213" y="194">1</text><text x="365" y="194">2</text><text x="34" y="66">1</text><text x="24" y="286">−1</text><text x="408" y="194">S</text><text x="47" y="31">D</text><text x="96" y="328">S=0.5で切った範囲</text></g></svg><figcaption>SとDが取る値を別々に並べただけでは、この同時の制約を表せません。縦の線はS=0.5の断面です。</figcaption></figure>

## 面積の倍率を密度へ掛ける

二変数の滑らかな一対一変換で、逆変換のヤコビ行列が正則な領域では、新しい密度は元の密度に逆変換の行列式の絶対値を掛けます。[1]

$$
J=\left|\det\begin{pmatrix}
\partial x/\partial s&\partial x/\partial d\\
\partial y/\partial s&\partial y/\partial d
\end{pmatrix}\right|
=\left|\det\begin{pmatrix}1/2&1/2\\1/2&-1/2\end{pmatrix}\right|=\frac12.
$$

この例では、ひし形の内部でf_{S,D}(s,d)=1/2、それ以外で0です。新しい座標での小さな面積に対し、元の面積が1/2になるため、その倍率を掛けて確率を保ちます。行列式が負でも密度を負にしないよう、絶対値を取ります。

逆変換を使う向きを忘れ、順方向の行列式の絶対値2をそのまま密度に掛けると、確率の和が1になりません。ひし形の面積2×密度1/2=1という検算ができます。

## 和の密度は、断面の幅を積分して求める

Sだけの密度は、可能なdについて同時密度を積分します。0<s<1なら断面の幅が2sなのでf_S(s)=sです。1≤s<2なら幅2(2−s)なのでf_S(s)=2−sです。それ以外は0です。

$$
P(S\le0.5)=\int_0^{0.5}s\,ds=0.125.
$$

密度の高さが一定の二変量分布でも、その断面の幅が場所によって変わるので、周辺分布は一様とは限りません。平均E[S]=1、分散Var(S)=1/6も、元の独立な一様変数の和として検算できます。

## 無相関でも、取り得る範囲が結び付く

共分散Cov(S,D)=Var(X)−Var(Y)=0です。しかしSとDは独立ではありません。例えばS≤0.5のとき、D>0.75は起こりません。それぞれの事象は無条件には正の確率を持つのに、積事象は確率0になるからです。

「密度が1/2という定数だから独立」とも言えません。密度が0になる範囲まで含めて積に分解できる必要があります。ひし形という値域の制約が、和と差を関連付けています。

## 比と合計で、独立になる別の例

別のモデルとしてX,Yが独立に率2の指数分布とし、S=X+Y、R=X/(X+Y)とします。今度の逆変換はx=sr、y=s(1−r)、範囲はs>0、0<r<1です。逆変換のヤコビアンの絶対値はsです。

元の密度4e^{-2x-2y}へ代入すると、$f_{S,R}(s,r)=4se^{-2s}$ です。これはs>0上で積分1になる密度と、0<r<1上の密度1の積なので、SとRは独立です。Rは一様分布となりP(R≤0.25)=0.25です。

合計と差を使った前のモデルと、結果が異なります。見た目が似た変換だから同じ分布になるのではなく、元の同時分布・逆変換・範囲を一組として確認します。

## 確認問題

<section class="practice-question" data-question="P05-Q1" id="p05-q1">

### 問1：逆変換と係数

S=X+Y、D=X−Yの逆変換と、密度に掛ける係数を求めてください。

<details id="p05-q1-answer"><summary>解答と理由</summary>

X=(S+D)/2、Y=(S−D)/2、係数は逆変換の行列式の絶対値1/2です。負の行列式をそのまま掛けたり、順方向の2を掛けたりしません。

</details>
</section>

<section class="practice-question" data-question="P05-Q2" id="p05-q2">

### 問2：値域を確認する

一様分布のモデルで、S=0.5とした断面のDの範囲は何ですか。点(S,D)=(0.5,0.8)は可能ですか。

<details id="p05-q2-answer"><summary>解答と理由</summary>

−0.5<D<0.5です。(0.5,0.8)ではY=(0.5−0.8)/2=−0.15となり、元の範囲に入りません。別々の周辺範囲だけでは判断を誤ります。

</details>
</section>

<section class="practice-question" data-question="P05-Q3" id="p05-q3">

### 問3：周辺確率

一様分布のモデルでP(S≤0.5)を求めてください。

<details id="p05-q3-answer"><summary>解答と理由</summary>

0.125です。0<s<1での密度sを0から0.5まで積分します。密度の値0.5や、0〜2の一様と誤認した0.25ではありません。

</details>
</section>

<section class="practice-question" data-question="P05-Q4" id="p05-q4">

### 問4：指数分布の比

独立な率2の指数変数でR=X/(X+Y)とします。P(R≤0.25)と、RがS=X+Yと独立になる根拠を説明してください。

<details id="p05-q4-answer"><summary>解答と理由</summary>

確率は0.25です。同時密度が4se^{-2s}×1に分解し、範囲もs>0と0<r<1の直積だからです。共分散が0という条件だけで判断したのではありません。

</details>
</section>

## 詳しく確かめる

<details id="p05-change-of-variables-proof"><summary>密度の変換式を、確率を保つ積分から導く</summary>

元の変数から新しい変数への写像をg、滑らかな逆写像をhとします。両方が微分可能で行列式が0にならない領域を考えます。新しい変数の集合Aに入る確率は、元の領域h(A)の密度積分です。多変数の積分の変数変換定理から、

$$
P(g(X,Y)\in A)
=\iint_{h(A)}f_{X,Y}(x,y)\,dx\,dy
=\iint_A f_{X,Y}(h(s,d))|\det Dh(s,d)|\,ds\,dd.
$$

すべての適切な集合Aに対してこの積分が確率を表すため、被積分関数が新しい密度です。本文の線形写像ではDhが一定で1/2となり、面積の倍率も一定です。この説明は積分の変数変換定理を用いた導出であり、その解析学の定理自体をここで証明したものではありません。

一対一でない変換では、一つの新しい点へ移る複数の元の領域の寄与を足す必要があります。境界や特異点を無視してよいかも、確率0であるなどの根拠を確認します。式だけでなく領域を残すことが重要です。

</details>

## まとめと次の一歩

逆変換、取り得る組、面積の係数を順に求め、積分が1になるかを確かめます。次は、標本数を増やすと何がどの意味で近づくのかを整理します。

## 出典・関連資料

[1] [Penn State STAT 414, Lesson 23](https://online.stat.psu.edu/stat414/Lesson23)の変数変換定理と、[Statlect, Functions of random vectors](https://www.statlect.com/fundamentals-of-probability/functions-of-random-vectors)を参照しました。[準1級公式案内](https://www.toukei-kentei.jp/grade/grade_pre-1)の変数変換に対応します。確認日2026-09-11。図・基本例・問題・途中式は本コース用の独自制作です。
