---
lesson_id: G33
slug: regression-estimation-standard-errors
title: 単回帰の推定と標準誤差
description: 最小二乗直線を求めた後、その係数がどのくらい変動するかを考えます。残差の標準偏差と、傾きの標準誤差を分けます。
status: published
goals:
  - 元のデータから回帰係数・残差・残差平方和を再計算する。
  - 誤差分散と係数の標準誤差を、自由度と単位を含めて説明する。
  - 最小二乗の代数的な計算と、推測のためのモデル条件を区別する。
prerequisites: [F20, G09, G15, G17, G24]
reading_minutes: 13
practice_minutes: 11
practice_count: 4
review_status: self_checked
updated_at: 2026-09-11
---

## 一本の直線を、再計算できるデータから作る

説明用に、xが1、2、3、4、5、6、対応するyが2、4、5、4、6、9という6組を作ります。実在する人や施設の測定ではありません。yをxから予測する切片付きの直線を考えます。

|x|1|2|3|4|5|6|
|---|---:|---:|---:|---:|---:|---:|
|y|2|4|5|4|6|9|

平均はx̄=3.5、ȳ=5です。偏差の平方和と積和をSxx、Syy、Sxyと書くと、それぞれ17.5、28、20です。これらは分母で割る前の和であり、分散・共分散の数値とは区別します。

## 傾きと切片は最小二乗で選ぶ

残差平方和Σ(yᵢ−a−bxᵢ)²が最小になる係数は、Sxx>0のとき、b=Sxy/Sxx、a=ȳ−bx̄です。この例ではb=8/7、a=1なので、予測値は

$$
\hat y=1+\frac87x
$$

です。切片を含む最小二乗直線は、点(x̄,ȳ)を通ります。平均の場所での予測が5となることも検算できます。

最小二乗の係数を計算するだけなら、誤差が正規という仮定は不要です。一方、母回帰係数を推測し、標準誤差や検定を解釈するには、次に示すモデルの条件が必要です。

## 観測値から予測値を引く

残差eᵢ=yᵢ−ŷᵢを計算します。分数のまま残すと、丸め誤差を抑えて検算できます。

|x|観測y|予測ŷ|残差e|
|---:|---:|---:|---:|
|1|2|15/7|−1/7|
|2|4|23/7|5/7|
|3|5|31/7|4/7|
|4|4|39/7|−11/7|
|5|6|47/7|−5/7|
|6|9|55/7|8/7|

残差の和は0、残差平方和SSEは(1+25+16+121+25+64)/49=36/7です。各残差を、元の観測と対応するxの組から計算します。二列を別々に並べ替えてはいけません。

<figure>
<svg viewBox="0 0 420 295" role="img" aria-labelledby="g33-figure-title g33-figure-desc">
<title id="g33-figure-title">観測6点、最小二乗直線、x=4での縦方向の残差</title>
<desc id="g33-figure-desc">横軸はx、縦軸はy。直線は1足す8x割る7。x=4の観測4に対する予測は39割る7で、残差はマイナス11割る7。正確な数値は直前の表にもあります。</desc>
<path d="M55 35V250H385" fill="none" stroke="currentColor" stroke-width="2"/>
<path d="M105 207.142857L355 92.857143" fill="none" stroke="#144a56" stroke-width="3"/>
<path d="M255 138.571429V170" fill="none" stroke="#8b391d" stroke-width="3" stroke-dasharray="5 3"/>
<g fill="#17222f"><circle cx="105" cy="210" r="5"/><circle cx="155" cy="170" r="5"/><circle cx="205" cy="150" r="5"/><circle cx="255" cy="170" r="5"/><circle cx="305" cy="130" r="5"/><circle cx="355" cy="70" r="5"/></g>
<g fill="currentColor" font-size="14" text-anchor="middle"><text x="105" y="272">1</text><text x="155" y="272">2</text><text x="205" y="272">3</text><text x="255" y="272">4</text><text x="305" y="272">5</text><text x="355" y="272">6</text><text x="39" y="255">0</text><text x="39" y="215">2</text><text x="39" y="175">4</text><text x="39" y="135">6</text><text x="39" y="95">8</text><text x="39" y="55">10</text></g>
<text x="395" y="272" fill="currentColor" font-size="15">x</text><text x="38" y="23" fill="currentColor" font-size="15">y</text><text x="267" y="191" fill="currentColor" font-size="13">縦方向の残差</text>
</svg>
<figcaption>線までの最短距離ではなく、y方向の差を二乗して最小化しています。軸の数値と表を合わせて読んでください。</figcaption>
</figure>

## 推測のための線形モデル

各観測についてYᵢ=α+βxᵢ+εᵢとし、xは固定して考えます。誤差の期待値0、分散が共通σ²、異なる観測の誤差は無相関という条件を置くと、最小二乗係数は不偏で、通常の分散公式が使えます。正確なt・F推測には、さらに独立な正規誤差を仮定します。

確率的なxを扱う場合も、xに条件付けた平均・分散・独立性として条件を明記します。x自身が正規分布であることは、この固定xの回帰推測の必要条件ではありません。散布図が直線に見えるだけで、誤差の独立性まで確立したことにもなりません。

観測できないモデル誤差εと、推定した直線からの残差eも別です。残差は係数推定の制約を持つため、元の誤差が独立でも残差どうしは一般に独立ではありません。

## 残差の分散はn−2で割る

切片と傾きの二係数を推定するので、残差の自由度はn−2です。モデルの共通誤差分散の推定値はs²=SSE/(n−2)です。この例では(36/7)/4=9/7、残差標準偏差は3/√7です。

傾きと切片の推定標準誤差は、それぞれ

$$
\operatorname{SE}(b)=\frac{s}{\sqrt{S_{xx}}},\qquad
\operatorname{SE}(a)=s\sqrt{\frac1n+\frac{\bar x^2}{S_{xx}}}
$$

です。傾きでは√(18/245)、切片では√(39/35)になります。残差標準偏差はyの単位、傾きの標準誤差はy/xの単位です。同じ「ばらつき」という説明だけで、違う量を取り替えません。

同じ残差分散なら、xの観測範囲が広くSxxが大きいほど、傾きの精度は高くなります。ただし観測範囲を広げても直線モデルが妥当かは別に確認します。

## 確認問題

<section class="practice-question" data-question="G33-Q1" id="g33-q1">

### 問1：回帰係数

Sxx=17.5、Sxy=20、x̄=3.5、ȳ=5です。傾きと切片を求めてください。

<details id="g33-q1-answer"><summary>解答と理由</summary>

傾き8/7、切片1です。切片は5−(8/7)×3.5です。相関係数の値と、単位を持つ傾きは一般には一致しません。

</details>
</section>

<section class="practice-question" data-question="G33-Q2" id="g33-q2">

### 問2：誤差分散と傾きの標準誤差

n=6、SSE=36/7です。誤差分散の推定値と、傾きの標準誤差を求めてください。

<details id="g33-q2-answer"><summary>解答と理由</summary>

s²=(36/7)/(6−2)=9/7、SE(b)=√{(9/7)/(35/2)}=√(18/245)です。分母をnやn−1にしません。係数の標準誤差と残差標準偏差も違います。

</details>
</section>

<section class="practice-question" data-question="G33-Q3" id="g33-q3">

### 問3：一つの残差

x=4、観測y=4について、予測値と残差を求めてください。

<details id="g33-q3-answer"><summary>解答と理由</summary>

予測39/7、残差4−39/7=−11/7です。観測点が直線より下なので負です。引く順番は観測−予測です。

</details>
</section>

<section class="practice-question" data-question="G33-Q4" id="g33-q4">

### 問4：xが全件同じ

xの値がすべて3でした。同じ式で切片と傾きを別々に一意に推定できますか。

<details id="g33-q4-answer"><summary>解答と理由</summary>

できません。Sxx=0で、傾きの式の分母が0になります。α+3βという組合せは考えられても、二つの係数を分離する情報がありません。

</details>
</section>

## 詳しく確かめる

<details id="g33-slope-variance"><summary>傾きの分散を、線形結合として導く</summary>

b=Σ(xᵢ−x̄)Yᵢ/Sxxです。係数wᵢ=(xᵢ−x̄)/SxxはΣwᵢ=0、Σwᵢxᵢ=1を満たすため、モデルの期待値からE[b]=βです。

誤差が無相関で共通分散σ²なら、V(b)=σ²Σwᵢ²=σ²/Sxxです。σ²をs²で推定して平方根を取ると、本文の標準誤差になります。異分散や相関した誤差では、一般に同じ分散公式は使えません。

誤差分散の推定でn−2を用いるのは、切片と傾きの二次元への当てはめを除いた残差空間がn−2次元になるためです。この説明と、正規誤差を用いる残差二乗和のカイ二乗性は区別し、次講でt・F推測につなげます。

</details>

## まとめと次の一歩

直線、残差、誤差分散、係数の標準誤差を別々に計算します。次はその標準誤差を使って検定・信頼区間・予測区間を作ります。

## 出典・関連資料

[OpenIntro: Linear regression with a single predictor](https://openintro-ims.netlify.app/model-slr)、[SciPy: linregress](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.linregress.html)、[統計検定2級・公式範囲](https://www.toukei-kentei.jp/hubfs/files/grade_range/grade2_hani_20181214.pdf)。データ・表・図・問題と導出記述は独自制作です。
