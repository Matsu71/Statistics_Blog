// Shared, dependency-free calculations for the foundation teaching labs.
// Normal tails use direct integration, not 1 - CDF for small upper tails.
// Educational inputs are bounded in the UI; all exported functions validate inputs.
const SQRT_2PI = Math.sqrt(2 * Math.PI);
const finite = (x, name) => { if (!Number.isFinite(x)) throw new RangeError(`${name} must be finite`); };
export function normalDensity(z) { finite(z, 'z'); return Math.exp(-z * z / 2) / SQRT_2PI; }
function integrate(f, a, b, tolerance = 1e-12) {
  const mid = (a + b) / 2, fa = f(a), fm = f(mid), fb = f(b);
  const initial = (b - a) * (fa + 4 * fm + fb) / 6;
  function recurse(left, right, fl, fc, fr, estimate, eps, remaining) {
    const center = (left + right) / 2;
    const lm = (left + center) / 2, rm = (center + right) / 2;
    const f1 = f(lm), f2 = f(rm);
    const l = (center - left) * (fl + 4 * f1 + fc) / 6;
    const r = (right - center) * (fc + 4 * f2 + fr) / 6;
    const delta = l + r - estimate;
    if (Math.abs(delta) <= 15 * eps) return l + r + delta / 15;
    if (remaining === 0) throw new RangeError('Numerical integration did not converge');
    return recurse(left, center, fl, f1, fc, l, eps / 2, remaining - 1)
      + recurse(center, right, fc, f2, fr, r, eps / 2, remaining - 1);
  }
  return recurse(a, b, fa, fm, fb, initial, tolerance, 24);
}
export function normalSF(z) {
  finite(z, 'z');
  if (Math.abs(z) > 38) throw new RangeError('normalSF supports |z| <= 38');
  if (z === 0) return 0.5;
  if (z < 0) return 1 - normalSF(-z);
  // Substitute x=z+t: SF(z)=phi(z)*integral_0^infinity exp(-zt-t^2/2) dt.
  // Truncation at t=12 contributes < 2e-33 of absolute probability for z>=0.
  return normalDensity(z) * integrate((t) => Math.exp(-z * t - t * t / 2), 0, 12, 1e-12 / (z + 1));
}
export function normalCDF(z) { return normalSF(-z); }
export function normalInterval(a, b) {
  finite(a, 'a'); finite(b, 'b');
  if (a > b) throw new RangeError('a must not exceed b');
  if (a === b) return 0;
  if (a >= 0) return normalSF(a) - normalSF(b);
  if (b <= 0) return normalSF(-b) - normalSF(-a);
  return 1 - normalSF(-a) - normalSF(b);
}
export function describe(values) {
  if (!Array.isArray(values) || values.length === 0) throw new RangeError('A nonempty array is required');
  let mean = 0, sumSquares = 0, n = 0;
  for (const x of values) { finite(x, 'value'); n++; const d = x - mean; mean += d / n; sumSquares += d * (x - mean); }
  return { n, mean, sumSquares, variance: sumSquares / n, sd: Math.sqrt(sumSquares / n),
    unbiasedVariance: n > 1 ? sumSquares / (n - 1) : null,
    sampleSD: n > 1 ? Math.sqrt(sumSquares / (n - 1)) : null };
}
export function median(values) {
  if (!values.length) throw new RangeError('No median for an empty array');
  values.forEach((v) => finite(v, 'value'));
  const a = [...values].sort((x, y) => x - y), m = Math.floor(a.length / 2);
  return a.length % 2 ? a[m] : (a[m - 1] + a[m]) / 2;
}
export function quartiles(values) {
  if (values.length < 2) throw new RangeError('At least two observations are required');
  const a = [...values].sort((x, y) => x - y), m = Math.floor(a.length / 2);
  const q1 = median(a.slice(0, m)), q2 = median(a), q3 = median(a.slice(a.length % 2 ? m + 1 : m));
  return { q1, q2, q3, iqr: q3 - q1, lowerFence: q1 - 1.5 * (q3 - q1), upperFence: q3 + 1.5 * (q3 - q1) };
}
export function binomialPMF(k, n, p) {
  if (!Number.isInteger(n) || n < 0 || n > 10000 || !Number.isInteger(k)) throw new RangeError('Invalid count');
  finite(p, 'p'); if (p < 0 || p > 1) throw new RangeError('p must be in [0,1]');
  if (k < 0 || k > n) return 0;
  if (p === 0) return k === 0 ? 1 : 0;
  if (p === 1) return k === n ? 1 : 0;
  let logChoose = 0;
  for (let j = 1; j <= Math.min(k, n - k); j++) logChoose += Math.log(n - j + 1) - Math.log(j);
  return Math.exp(logChoose + k * Math.log(p) + (n - k) * Math.log1p(-p));
}
export function binomialRange(a, b, n, p) {
  if (!Number.isInteger(a) || !Number.isInteger(b) || a > b) throw new RangeError('Invalid integer interval');
  let sum = 0, correction = 0;
  for (let k = a; k <= b; k++) { const term = binomialPMF(k, n, p) - correction; const next = sum + term; correction = (next - sum) - term; sum = next; }
  return sum;
}
export function wilsonInterval(k, n, z = 1.959963984540054) {
  if (!Number.isInteger(n) || n < 1 || !Number.isInteger(k) || k < 0 || k > n) throw new RangeError('Invalid binomial counts');
  finite(z, 'z'); if (z <= 0) throw new RangeError('z must be positive');
  const q = k / n, denominator = 1 + z * z / n;
  const center = (q + z * z / (2 * n)) / denominator;
  const half = z * Math.sqrt(q * (1 - q) / n + z * z / (4 * n * n)) / denominator;
  // Endpoint correction only removes roundoff for mathematical endpoints, not a Wald clipping rule.
  return [k === 0 ? 0 : center - half, k === n ? 1 : center + half];
}
export function seededRandom(seed) {
  if (!Number.isInteger(seed) || seed < 1 || seed >= 2147483647) throw new RangeError('seed must be an integer in 1..2147483646');
  let state = seed;
  // Deterministic multiplicative generator for reproducible teaching demonstrations, not cryptography.
  return () => { state = (state * 16807) % 2147483647; return state / 2147483647; };
}
export function normalRandom(random) {
  const u = random(), v = random();
  if (!(u > 0 && u < 1 && v > 0 && v < 1)) throw new RangeError('Random values must be strictly between zero and one');
  return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v);
}
export const confidenceCritical = Object.freeze({ 90: 1.6448536269514722, 95: 1.959963984540054, 99: 2.5758293035489004 });
export function coverageSimulation({ mu, sigma, n, repetitions, level, seed }) {
  finite(mu, 'mu'); finite(sigma, 'sigma');
  if (sigma <= 0 || !Number.isInteger(n) || n < 1 || !Number.isInteger(repetitions) || repetitions < 1 || repetitions > 5000) throw new RangeError('Invalid simulation parameters');
  const critical = confidenceCritical[level]; if (!critical) throw new RangeError('Unsupported confidence level');
  const random = seededRandom(seed), se = sigma / Math.sqrt(n), half = critical * se;
  const intervals = Array.from({ length: repetitions }, (_, i) => {
    // Draw the sample mean directly from its exact normal sampling distribution.
    const mean = mu + se * normalRandom(random), lower = mean - half, upper = mean + half;
    return { index: i + 1, mean, lower, upper, covers: lower <= mu && mu <= upper };
  });
  return { se, half, intervals, covered: intervals.filter((x) => x.covers).length };
}
