---
lesson_id: G40
slug: grade2-integrated-practice
title: 2級の総合演習と準1級への接続
description: 記述・調査・確率・推測・回帰を横断し、公式を選ぶ条件から解釈まで確かめます。誤答した理由に応じて必要な講座へ戻れます。
status: published
goals:
  - 初見の数値と場面に対して、対象・条件・方法を自分で選ぶ。
  - 計算結果を別の式や表と照合し、誤りの種類を説明する。
  - 苦手な前提を復習し、準1級へ向けた次の学習範囲を整理する。
prerequisites: [G04, G05, G09, G18, G24, G26, G30, G32, G34, G36, G37, G38, G39]
reading_minutes: 8
practice_minutes: 60
practice_count: 16
review_status: self_checked
updated_at: 2026-09-11
---

## この演習の使い方

本ページは本コースのために作成した独自の16問です。公式過去問の転載・記憶再現ではなく、公式試験の出題数や形式を完全に模した模擬試験でもありません。ここでの正答数から、合格確率を保証するものではありません。

解答を開く前に、推定したい量、与えられた条件、使う式、数値、結論を短く書いてください。計算だけ合っても、条件や解釈が違えば復習対象です。一度見た答えを覚えるだけでなく、数値や方向が変わったときにも理由を説明できるかを確かめます。

所要時間は編集上の目安です。時間を測るより、分からなかった箇所を記録し、対応する教材へ戻ることを優先して構いません。初回は分布表や電卓を使ってもよいですが、どの表のどの裾を使ったかを残します。

## 確認問題

<section class="practice-question" data-question="G40-Q1" id="g40-q1">

### 問1：総和と二乗の順番

データは1、3、5です。平均、二乗の和、和の二乗、不偏分散を求めてください。

<details id="g40-q1-answer"><summary>解答と理由・復習先</summary>

平均3、二乗の和35、和の二乗81、不偏分散4です。平均からの二乗偏差の和は4+0+4=8で、n−1=2で割ります。Σx²と(Σx)²は別です。

復習：[記号と総和](../parameters-statistics-and-notation/)／[標本分散](../sampling-mean-proportion-variance/)。

</details>
</section>

<section class="practice-question" data-question="G40-Q2" id="g40-q2">

### 問2：不均等と単位変換

非負の値0、0、10、10について、G03の有限データの定義でジニ係数を求めてください。全値を100倍にすると変わりますか。

<details id="g40-q2-answer"><summary>解答と理由・復習先</summary>

ジニ係数は0.5です。順序付き全組の絶対差の和80を、2×4×合計20=160で割ります。正の倍率では分子・分母が同じ倍率になるため変わりません。全値に定数を加える場合とは違います。

復習：[ローレンツ曲線とジニ係数](../lorenz-and-gini/)。

</details>
</section>

<section class="practice-question" data-question="G40-Q3" id="g40-q3">

### 問3：二期間の平均成長率

値が100から150、次に120となりました。一期間あたり一定の率で同じ最終値に到達するとした平均成長率を求めてください。

<details id="g40-q3-answer"><summary>解答と理由・復習先</summary>

倍率1.5と0.8の積は1.2です。幾何平均の倍率√1.2から1を引き、約9.5445%です。増減率50%と−20%の算術平均15%では、二期間で同じ最終値になりません。

復習：[幾何平均と指数](../growth-indices-autocorrelation/)。

</details>
</section>

<section class="practice-question" data-question="G40-Q4" id="g40-q4">

### 問4：非復元標本の平均

母集団の大きさN=50、母集団内の分母N−1で定義した分散が20です。10個を単純無作為・非復元で選ぶとき、標本平均の分散と標準誤差を求めてください。

<details id="g40-q4-answer"><summary>解答と理由・復習先</summary>

分散は(1−10/50)×20/10=1.6、標準誤差は√1.6です。与えられた母集団分散の分母がN−1なので、この形の有限母集団補正を使います。独立復元抽出の式と混ぜません。

復習：[抽出法と有限母集団補正](../sampling-and-finite-populations/)。

</details>
</section>

<section class="practice-question" data-question="G40-Q5" id="g40-q5">

### 問5：警告後の不良確率

不良確率0.2、不良の警告確率0.8、良品の警告確率0.1というモデルです。警告確率と、警告が出た条件での不良確率を求めてください。

<details id="g40-q5-answer"><summary>解答と理由・復習先</summary>

警告確率は0.2×0.8+0.8×0.1=0.24です。警告かつ不良は0.16なので、警告後の不良確率は0.16/0.24=2/3です。0.8をそのまま条件を逆にした確率にしません。

復習：[条件付き確率とベイズ](../conditional-probability-and-bayes/)。

</details>
</section>

<section class="practice-question" data-question="G40-Q6" id="g40-q6">

### 問6：共分散を残す

X,Yが0か1を取り、P(0,0)=0.3、P(0,1)=0.2、P(1,0)=0.1、P(1,1)=0.4です。Cov(X,Y)とV(X−Y)を求めてください。

<details id="g40-q6-answer"><summary>解答と理由・復習先</summary>

E[X]=0.5、E[Y]=0.6、E[XY]=0.4なので共分散0.1です。分散は0.25と0.24なので、差の分散は0.25+0.24−0.2=0.29です。独立を勝手に仮定しません。

復習：[同時分布](../joint-marginal-independent/)／[和と差の分散](../expectation-variance-covariance/)。

</details>
</section>

<section class="practice-question" data-question="G40-Q7" id="g40-q7">

### 問7：二項か超幾何か

8個中3個が対象品です。2個を非復元で等確率に選び、両方が対象品となる確率を求めてください。

<details id="g40-q7-answer"><summary>解答と理由・復習先</summary>

超幾何分布で、3個から2個を選ぶ3通りを、8個から2個の28通りで割り、3/28です。順番付きなら(3/8)(2/7)でも同じです。(3/8)²は独立な復元抽出の別モデルです。

復習：[二項分布と超幾何分布](../binomial-hypergeometric/)。

</details>
</section>

<section class="practice-question" data-question="G40-Q8" id="g40-q8">

### 問8：成功までの試行数

成功確率0.25の独立試行を最初の成功まで続けます。4回目に初めて成功する確率と、成功を含む平均試行数を求めてください。

<details id="g40-q8-answer"><summary>解答と理由・復習先</summary>

確率は0.75³×0.25=27/256≈0.10547、平均試行数は1/0.25=4です。平均失敗数なら3です。固定した4試行で成功1回という二項の問題とは違います。

復習：[幾何分布と負の二項分布](../geometric-negative-binomial/)。

</details>
</section>

<section class="practice-question" data-question="G40-Q9" id="g40-q9">

### 問9：一観測と標本平均

母平均20、母標準偏差4の正規母集団から独立に16件を取ります。標本平均の分布と、平均が21.96以上となる確率を求めてください。

<details id="g40-q9-answer"><summary>解答と理由・復習先</summary>

標本平均はN(20,1)で、第2引数は分散です。標準誤差1なので、P(Z≥1.96)≈0.025です。元の一観測の標準偏差4は変わらず、平均の標準誤差と取り替えません。

復習：[正規分布](../normal-and-bivariate-normal/)／[標本平均](../sampling-mean-proportion-variance/)。

</details>
</section>

<section class="practice-question" data-question="G40-Q10" id="g40-q10">

### 問10：zとtの区間

n=36、平均10です。母標準偏差3が既知の場合の95%区間を1.96で求めてください。3が今回の標本標準偏差だった場合には、何を変えますか。正規標本でt₀.₉₇₅,₃₅≈2.03011を使ってください。

<details id="g40-q10-answer"><summary>解答と理由・復習先</summary>

既知σなら標準誤差0.5、区間9.02〜10.98です。未知σでs=3なら、自由度35のt分位点を使い、約8.98495〜11.01505です。標本標準偏差を既知母標準偏差と呼び替えません。

復習：[母平均の区間推定](../mean-confidence-intervals/)。

</details>
</section>

<section class="practice-question" data-question="G40-Q11" id="g40-q11">

### 問11：不偏なら常に有利か

ある母数のもとで推定量Aは不偏で分散2、Bは偏り0.5で分散1です。この母数での平均二乗誤差を比べてください。

<details id="g40-q11-answer"><summary>解答と理由・復習先</summary>

AのMSEは2、Bは1+0.5²=1.25です。この条件ではBの方が小さくなります。不偏性とMSEの大小は同じ判定ではありません。他の母数でも同じ優越性があるとは、この情報だけでは分かりません。

復習：[不偏性・一致性・MSE](../unbiased-consistent-mse/)。

</details>
</section>

<section class="practice-question" data-question="G40-Q12" id="g40-q12">

### 問12：対応した平均差

独立な4組の前−後の差が1、2、3、4でした。差の母平均0を検定するt値と自由度を求めてください。差が正規というモデルを仮定します。

<details id="g40-q12-answer"><summary>解答と理由・復習先</summary>

平均差2.5、差の不偏分散5/3、標準誤差√(5/12)です。t=2.5/√(5/12)=√15≈3.87298、自由度3です。前後を合わせた8個を独立標本として扱いません。

復習：[平均差の検定](../two-mean-and-paired-tests/)。

</details>
</section>

<section class="practice-question" data-question="G40-Q13" id="g40-q13">

### 問13：度数の適合度

三分類の観測度数が12、18、30、帰無仮説は各分類の確率1/3です。期待度数、Pearson統計量、自由度を求めてください。同じ標本から追加の母数は推定していません。

<details id="g40-q13-answer"><summary>解答と理由・復習先</summary>

期待各20、X²=(64+4+100)/20=8.4、自由度2です。カイ二乗2の右側p値はe⁻⁴·²≈0.01500です。カテゴリ数3をそのまま自由度にせず、合計度数の制約を考えます。

復習：[適合度検定](../goodness-of-fit/)／[独立性検定との違い](../contingency-table-independence/)。

</details>
</section>

<section class="practice-question" data-question="G40-Q14" id="g40-q14">

### 問14：単回帰を元データから作る

x=0、1、2、3、y=1、2、2、5です。切片付き最小二乗の傾き、切片、残差平方和を求めてください。

<details id="g40-q14-answer"><summary>解答と理由・復習先</summary>

x̄=1.5、ȳ=2.5、Sxx=5、Sxy=6なので、傾き1.2、切片0.7です。予測0.7、1.9、3.1、4.3に対する残差は0.3、0.1、−1.1、0.7で、平方和1.8です。n−2=2で割る誤差分散の推定値は0.9です。

復習：[単回帰の推定と標準誤差](../regression-estimation-standard-errors/)／[予測区間](../regression-tests-and-prediction/)。

</details>
</section>

<section class="practice-question" data-question="G40-Q15" id="g40-q15">

### 問15：分散分析の全体検定

独立な三群で各3件、群間平方和24、群内平方和6です。正規・等分散モデルのF値と自由度を求めてください。棄却したら全組の差が証明されますか。

<details id="g40-q15-answer"><summary>解答と理由・復習先</summary>

F=(24/2)/(6/6)=12、自由度2,6、右側p値0.008です。棄却は全平均が同じではないという結論で、すべての組が違うことの証明ではありません。必要な比較を、多重性を考慮して行います。

復習：[一元配置分散分析](../one-way-anova/)／[解析出力](../reading-analysis-output/)。

</details>
</section>

<section class="practice-question" data-question="G40-Q16" id="g40-q16">

### 問16：計算の再現と結論の妥当性

公開データで非常に小さいp値が得られました。別の配布元の同名データでは少し違う値になりました。「どちらも同じ研究名なので版の確認は不要」「小さいp値だから因果と一般化も保証される」という二つの説明を評価してください。

<details id="g40-q16-answer"><summary>解答と理由・復習先</summary>

どちらも不適切です。配布元、選択ファイル、取得日、列・単位、前処理、対象行、ハッシュ、コードとライブラリの版を照合します。同名でも修正や欠測処理が異なる場合があります。

p値は指定したモデルと標本のもとでの結果です。代表性、独立性、因果の条件、測定の妥当性を保証しません。計算が再現できることと、研究の結論が目的に適切なことを分けます。

復習：[データから分析を再現する](../reproducible-case-study/)／[実験計画](../randomization-replication-blocking/)。

</details>
</section>

## 誤答した理由で復習先を選ぶ

計算手順を思い出せなかったのか、使う分布を間違えたのか、分母・単位・自由度を取り違えたのか、解釈が違ったのかを分けて記録します。同じ不正答でも必要な復習が異なります。

|つまずいた内容|主な復習先|
|---|---|
|記号・分母・二乗の順番|G01、G02、G09、G15|
|抽出・対応・独立の判断|G05、G06、G08、G21、G28|
|分布とパラメータの選択|G10〜G18|
|推定と検定、裾と自由度|G19〜G32|
|係数・診断・解析結果|G33〜G39|

正解を開いた直後に同じ問題へ答えられたことだけを、十分に理解したと認定しません。数値を変えたり、差の方向を逆にしたり、仮定を一つ外したりしても説明できるかを確かめてください。

## 詳しく確かめる

<details id="g40-independent-check"><summary>答えを別の経路で検算する：問14の例</summary>

問14ではSyy=9、Sxy=6、Sxx=5なので、最小二乗の残差平方和はSyy−Sxy²/Sxx=9−36/5=1.8です。一行ずつ予測と残差を求めて二乗した値とも一致します。

さらに残差の和は0、xを掛けた残差の和も0になります。これらは切片付き最小二乗の正規方程式に対応します。同じ数を同じ手順で繰り返すだけでなく、別の恒等式へ戻ると、足し算・分母・符号の誤りを発見しやすくなります。

検算が一致しても、モデルの前提やデータの代表性までは証明できません。算術、モデル、解釈の三つを別々に確認することが、次の高度な手法を学ぶ土台になります。

</details>

## まとめと次の一歩

2級コースでは、記述と調査設計から確率・標本分布を経て、推定・検定・回帰へ進みました。公式を使う前提を明記し、計算を追い、結果から言える範囲を限定することが共通の軸です。

準1級へ進む際は、行列・微分積分・推定理論を必要に応じて補い、多変量解析、時系列、一般化線形モデル、ベイズ、計算統計、因果推論などへ範囲を広げます。すべての補助数学を先に完走するのではなく、手法の前提と結び付けて学びます。

準1級のコース本文がすでに全件公開されているという意味ではありません。受験予定日に対応する公式範囲を確認し、実際に公開済みの教材と準備中の内容を区別して案内します。まずこの演習の復習記録を使い、2級の前提に戻る必要がある箇所を整理してください。

## 出典・関連資料

[統計検定2級・公式出題範囲](https://www.toukei-kentei.jp/hubfs/files/grade_range/grade2_hani_20181214.pdf)、[統計検定準1級・公式案内](https://www.toukei-kentei.jp/grade/grade_pre-1)、[OpenIntro Statistics](https://www.openintro.org/book/os/)。本ページの問題・数値例・解答・復習構成は独自制作です。公式問題の転載や本試験の出題保証ではありません。
