import fs from 'node:fs';
import vm from 'node:vm';

const html = fs.readFileSync('log.html', 'utf8');
const js = html.split('<script>')[1].split('</script>')[0];

const box = { html: '', innerHTML: '', insertAdjacentHTML(_, s) { this.html += s; } };
const sandbox = {
  console,
  performance,
  document: {
    getElementById: id => (id === 'scan' ? box : null),
    body: { scrollHeight: 0 },
  },
  window: { scrollTo() {} },
  matchMedia: () => ({ matches: true }),   // reduced motion -> render all at once
  addEventListener() {},
  requestAnimationFrame() {},
  setTimeout() {},
  Date, Number, String, Math, JSON, Object, Array,
};
sandbox.globalThis = sandbox;

try {
  vm.createContext(sandbox);
  vm.runInContext(js, sandbox, { timeout: 20000 });
} catch (e) {
  console.error('THREW:', e.message);
  process.exit(1);
}

const out = box.innerHTML || box.html;
const lines = out.split('\n');
const plain = lines.map(l => l.replace(/<[^>]*>/g, ''));
console.log('RENDER OK');
console.log('lines        :', lines.length);
console.log('chars        :', out.length);
console.log('max line len :', Math.max(...plain.map(l => l.length)));
console.log('empty lines  :', plain.filter(l => !l.trim()).length);
console.log('undefined?   :', out.includes('undefined'));
console.log('NaN?         :', out.includes('NaN'));
console.log('[object      :', out.includes('[object'));
console.log('\n--- first 34 rendered lines ---');
console.log(plain.slice(0, 34).join('\n'));
console.log('\n--- last 26 rendered lines ---');
console.log(plain.slice(-26).join('\n'));
