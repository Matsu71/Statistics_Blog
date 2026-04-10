import katex from 'katex';

const katexOptions = {
  output: 'htmlAndMathml' as const,
  throwOnError: false,
  strict: 'warn' as const
};

function escapeHtml(value: string) {
  return value
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#39;');
}

export function renderDisplayMath(latex: string) {
  return katex.renderToString(latex, {
    ...katexOptions,
    displayMode: true
  });
}

export function renderInlineMath(latex: string) {
  return katex.renderToString(latex, {
    ...katexOptions,
    displayMode: false
  });
}

export function renderInlineMathText(text: string) {
  const chunks: string[] = [];
  const pattern = /(?<!\\)\$([^$\n]+?)(?<!\\)\$/g;
  let cursor = 0;
  let match: RegExpExecArray | null;

  while ((match = pattern.exec(text)) !== null) {
    chunks.push(escapeHtml(text.slice(cursor, match.index)).replaceAll('\\$', '$'));
    chunks.push(renderInlineMath(match[1].trim()));
    cursor = match.index + match[0].length;
  }

  chunks.push(escapeHtml(text.slice(cursor)).replaceAll('\\$', '$'));
  return chunks.join('');
}
