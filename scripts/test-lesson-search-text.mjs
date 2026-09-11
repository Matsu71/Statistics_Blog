import assert from 'node:assert/strict';
import { lessonSearchText } from '../src/lib/lesson-search-text.mjs';
const cases = [
  ['0<x<1。連立方程式を解く。\n<section id="q">問題</section>', '連立方程式'],
  ['|s|<1。収束範囲を確認。<details><summary>証明</summary>根拠</details>', '収束範囲'],
  ['g(X)<g(Y)。単調性を確認。<p>説明</p>', '単調性'],
  ['<svg><title>和と差</title><text x="2" y="4">値域</text></svg>', '値域'],
  ['<p>第一節</p><p>次の節</p>', '第一節 次の節'],
  ['A < B > C', 'A < B > C']
];
for (const [input, expected] of cases) {
  const result = lessonSearchText(input);
  assert.ok(result.replace(/\s+/g,' ').includes(expected), `${input}: ${result}`);
}
assert.ok(!lessonSearchText('<section data-question="P05-Q1">解答</section>').includes('data-question'));
const inequality = '0<x<1。連立方程式を解く。\n<section>問題</section>';
assert.ok(!inequality.replace(/<[^>]*>/g,' ').includes('連立方程式'), 'Regression fixture must detect the old defect');
const source = [{ text: '</script><script>alert(1)</script>0<x<1' }];
const encoded = JSON.stringify(source).replace(/</g, '\\u003c');
assert.ok(!encoded.includes('<'));
assert.deepEqual(JSON.parse(encoded), source);
assert.throws(()=>lessonSearchText(null),TypeError);
console.log('Search text: 11 regression assertions passed; inequalities and Japanese prose preserved.');
