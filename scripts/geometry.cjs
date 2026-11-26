const fs = require('node:fs');
const vm = require('node:vm');
const context = { window: {} };
vm.runInNewContext(fs.readFileSync('src/engine.js', 'utf8'), context);
fs.mkdirSync('/tmp/unity-geometry', { recursive: true });
for (const { kind } of require('../src/products.json')) {
  const geometry = context.window.Unity3D.build(kind);
  fs.writeFileSync('/tmp/unity-geometry/' + kind, Buffer.from(geometry.buffer));
}
