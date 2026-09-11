/**
 * Build searchable text without treating mathematical inequalities as HTML.
 * This is an index transformation, not an HTML sanitizer; render content with
 * the trusted-content pipeline and JSON-escape it separately.
 * @param {string} source
 * @returns {string}
 */
export function lessonSearchText(source) {
  if (typeof source !== 'string') throw new TypeError('Lesson source must be a string');
  return source
    .replace(/<!--[\s\S]*?-->/g, ' ')
    .replace(/<\/?(?:section|details|summary|figure|figcaption|svg|title|desc|g|path|text|p|div|span|ul|ol|li|table|thead|tbody|tr|th|td)(?:\s[^<>]*?)?\s*\/?>/gi, ' ');
}
