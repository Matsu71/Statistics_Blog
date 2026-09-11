---
lesson_id: G39
slug: reproducible-case-study
title: データから分析と報告を再現する
description: 出所を確認したデータを読み、要約・平均差・モデル条件・報告を一つにつなげます。計算を再現できることと、母集団への一般化は区別します。
status: draft
goals:
  - データの出所・版・列・単位・対象件数を記録する。
  - 元のCSVから要約とWelchの平均差分析を再計算する。
  - 観察データの限界を残し、推定値・区間・p値を報告する。
prerequisites: [G05, G21, G28, G35, G36, G38]
reading_minutes: 14
practice_minutes: 15
practice_count: 4
review_status: self_checked
updated_at: 2026-09-11
---

## 合成例から、出所のある観測データへ

この講座はUCI Machine Learning Repositoryが配布するIrisデータを使います。前の講座の架空の数値例とは異なり、花の計測値を含む公開データです。ただし、公開されているデータを取得したことは、自分たちが無作為抽出や無作為割付を実施したことにはなりません。

UCIの配布物から`bezdekIris.data`を選び、元の行と数値を保ったCSVに変換します。複数の配布版を無言で混ぜず、選んだファイル名、取得元、ハッシュを記録します。数値例や解析結果は、この実際のCSVから計算して表示する構成です。取得や検算が完了していない下書きは公開しません。

データの四つの計測列は、がく片と花弁の長さ・幅で、単位はcmです。最後の列が分類名です。この例では花弁長`petal_length_cm`を一つの目的変数として選び、まず分類別の特徴を整理します。

[使用するCSV](../../../data/grade2-iris.csv)と、[取得・変換の記録](../../../data/grade2-iris-provenance.json)を確認してください。CC BY 4.0の条件と配布元への表示を保ちます。

## 読み込んだ時点で、形と範囲を点検する

一行を一つの計測記録として、行数、分類数、欠測、単位を確認します。この配布物では三分類が各50行、合計150行であることを検算します。空欄や別の単位の値を0として補う処理はしません。

同じ計測値を持つ複数行があっても、数値が一致することだけで同一対象の二重登録とは断定できません。この教材では配布された観測行を勝手に削除せず、行が一致する数も変換記録へ残します。重複や独立性の疑いがある場合は、原資料と取得経緯の確認が必要です。

分類ごとに人数が同じという構成は、自然界の各分類の割合が1/3という証拠ではありません。この標本の構成と、推測したい母集団の構成を区別します。

## 花弁長の要約を再計算する

標本平均と、分母n−1の標本標準偏差を求めます。以下の表はビルド時にCSVから計算した値です。途中で丸めず、表示時に丸めます。元データを確認せず既知の有名な数値を転載する方法ではありません。

<!-- IRIS_SUMMARY_START -->
取得・整合性確認と計算が完了した場合にのみ、この表を生成して公開します。
<!-- IRIS_SUMMARY_END -->

各群の平均の差だけでなく、散らばり、最小値と最大値、標本数も読みます。違う分類をまとめた全体の分布は、群の混合により複数の山を持つことがあります。全150行を同じ一つの正規母集団からの観測と決めつけません。

## 二群の平均差をモデルとして推定する

setosaとversicolorについて、差を「versicolor−setosa」と定めます。独立した組のない二群という作業上のモデルを置き、母分散を等しいと仮定しないWelch法で、花弁長の平均差・標準誤差・近似自由度・95%区間を計算します。

$$
\widehat\Delta=\bar x_{\mathrm{versicolor}}-\bar x_{\mathrm{setosa}},\qquad
SE=\sqrt{\frac{s_{\mathrm{versicolor}}^2}{n_{\mathrm{versicolor}}}+\frac{s_{\mathrm{setosa}}^2}{n_{\mathrm{setosa}}}}.
$$

この選択は、等分散の検定が非有意だったから確定した条件ではありません。Welchであっても独立性、標本の選び方、外れ値、モデルの適合の問題がなくなるわけではありません。歴史的な公開データに計算上のモデルを当てはめる教材として、その限界を明示します。

<!-- IRIS_WELCH_START -->
実際のCSVから平均差と推測値を計算し、別の式との一致を確認した後に表示します。
<!-- IRIS_WELCH_END -->

## 出力を一文の結論へ戻す

結果の報告には、使ったデータと列、二群の件数、差の方向と単位、方法、推定区間、p値、条件と限界を含めます。p値だけを示したり、計算機の表示が小さいことを確率0と書いたりしません。

<!-- IRIS_REPORT_START -->
検算済みの数値を含む報告例を、同じCSVから生成します。
<!-- IRIS_REPORT_END -->

分類と花弁長の関連が強くても、「分類を人為的に変えれば花弁がその差だけ伸びる」という介入の結論ではありません。収集対象が現在のあらゆる地域・季節の花を代表するという根拠も、この計算だけにはありません。小さいp値と、母集団への一般化・因果性を区別します。

## 自分で計算を再現する

CSVを保存した場所で、Pythonの標準ライブラリとNumPy・SciPyを使い、次のように再計算できます。ここでの列名と単位は、この講座が配布するCSVの仕様です。空欄を0へ置き換える前処理は含みません。

```python
import csv
from pathlib import Path
import numpy as np
from scipy import stats

path = Path("grade2-iris.csv")
if not path.is_file():
    raise FileNotFoundError("配布CSVを同じフォルダに保存してください。")
with path.open(encoding="utf-8", newline="") as handle:
    rows = list(csv.DictReader(handle))

def values(species: str) -> np.ndarray:
    result = np.array([
        float(row["petal_length_cm"])
        for row in rows
        if row["species"].lower().removeprefix("iris-") == species
    ])
    if result.size < 2 or not np.isfinite(result).all():
        raise ValueError("件数・分類名・欠測を確認してください。")
    return result

first = values("versicolor")
second = values("setosa")
difference = first.mean() - second.mean()
a = first.var(ddof=1) / first.size
b = second.var(ddof=1) / second.size
se = np.sqrt(a + b)
df = (a + b) ** 2 / (a ** 2 / (first.size - 1) + b ** 2 / (second.size - 1))
critical = stats.t.ppf(0.975, df)
interval = (difference - critical * se, difference + critical * se)
test = stats.ttest_ind(first, second, equal_var=False)
print("差と95%区間（cm）:", difference, interval)
print("t・自由度・両側p:", test.statistic, df, test.pvalue)
```

同じデータで計算が一致しても、モデルの前提や調査の代表性が実証されたわけではありません。再現性は、どの入力からどの処理で値を得たかを追えることです。データが真実を十分表しているか、推論が目的に合うかも、別に検討します。

## 確認問題

<section class="practice-question" data-question="G39-Q1">

### 問1：標準偏差と標準誤差

CSVのsetosaの花弁長について、平均、分母n−1の標準偏差、平均の推定標準誤差を求めてください。

<details id="g39-q1-answer"><summary>解答と理由</summary>

<!-- IRIS_Q1_START -->
この解答の数値は、取得したCSVからの検算後に生成します。
<!-- IRIS_Q1_END -->

</details>
</section>

<section class="practice-question" data-question="G39-Q2">

### 問2：差の方向と区間

差をversicolor−setosaとしたWelch法の平均差と95%区間を求めてください。差の順番を逆にすると何が変わりますか。

<details id="g39-q2-answer"><summary>解答と理由</summary>

<!-- IRIS_Q2_START -->
この解答の数値は、同じCSVとWelchの式で生成します。
<!-- IRIS_Q2_END -->

</details>
</section>

<section class="practice-question" data-question="G39-Q3">

### 問3：小さいp値と一般化

小さいp値が得られました。現在のあらゆる地域の花に同じ差があり、分類への介入による因果効果も証明したと言えますか。

<details id="g39-q3-answer"><summary>解答と理由</summary>

言えません。計算は、この配布データに明記したモデルを当てはめた結果です。収集対象の代表性や現在の母集団との関係、介入の定義・因果の条件は別に必要です。計算上の不確かさと、データ収集上の限界を分けて報告します。

</details>
</section>

<section class="practice-question" data-question="G39-Q4">

### 問4：再現に必要な情報

同じ名前のIrisデータを別の場所から取得すれば、必ず同じ結果になると考えてよいですか。保存すべき情報を挙げてください。

<details id="g39-q4-answer"><summary>解答と理由</summary>

名前だけでは同一版とは限りません。配布元、選んだファイル、取得日、元と変換後のハッシュ、列と単位、前処理、対象行、解析コード、ライブラリの版、利用条件を記録します。数値が一致しているかを実際に確認し、修正や除外を黙って加えません。

</details>
</section>

## 詳しく確かめる

<details id="g39-audit-method"><summary>同じ結果を二つの計算経路で確かめる</summary>

標本平均・不偏分散からWelchの統計量と近似自由度を直接計算し、SciPyの独立二群t検定を等分散なしで実行した統計量・p値と照合します。区間はtの分位点から作り、ライブラリが返す同じ手法の区間とも比較します。

三群の分散分析を補助的に計算する場合も、群間・群内の平方和からのF比と`f_oneway`を照合します。これは等分散のモデルを適切と認定する前提確認ではなく、実装と算術が一致するかの検算です。Welchの二群比較とは別の問いとして扱います。

CSVのハッシュを保存すると、後から入力が変わっていないかを確認できます。ただし、ハッシュ一致はデータが適切に測定されたことの証明ではありません。入力・計算・モデル・結論の各段階で、何を確かめたかを区別します。

</details>

## まとめと次の一歩

出所と版を固定し、元データから計算を再現し、推定と検定を条件付きで報告します。次は2級コース全体を横断する独自の総合演習です。

## 出典・関連資料

[UCI Machine Learning Repository: Iris](https://archive.ics.uci.edu/dataset/53/iris)、DOI: 10.24432/C56C76、データの作成者表示R. A. Fisher、元の研究1936年、配布ページの利用条件CC BY 4.0を参照します。選択した実ファイルと変換の記録は、本文の出所記録に保存します。[SciPy: independent-samples t-test](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.ttest_ind.html)、[SciPy: one-way ANOVA](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.f_oneway.html)。本文・演習・分析コードは独自制作で、データの利用条件と本文の作成主体を区別しています。
