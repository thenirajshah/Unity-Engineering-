/* Export the viewer's interleaved geometry as valid, self-contained glTF 2.0. */
const fs = require('node:fs');
const vm = require('node:vm');
const context = { window: {} };
vm.runInNewContext(fs.readFileSync('src/engine.js', 'utf8'), context);
const output = 'public/assets/models';
fs.mkdirSync(output, { recursive: true });

const models = ['reactor-limpet', 'exchanger', 'exchanger-cutaway', 'exchanger-exploded', 'pressure', 'anfd', 'ribbon', 'rmg'];
for (const kind of models) {
  const values = context.window.Unity3D.build(kind);
  const min = [Infinity, Infinity, Infinity];
  const max = [-Infinity, -Infinity, -Infinity];
  // Reverse triangles whose winding opposes the supplied outward normals.
  for (let i = 0; i < values.length; i += 27) {
    const a = [0, 1, 2].map((axis) => values[i + 9 + axis] - values[i + axis]);
    const b = [0, 1, 2].map((axis) => values[i + 18 + axis] - values[i + axis]);
    const cross = [a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0]];
    if (cross.reduce((dot, v, axis) => dot + v * values[i + 3 + axis], 0) < 0) {
      const second = values.slice(i + 9, i + 18);
      values.copyWithin(i + 9, i + 18, i + 27);
      values.set(second, i + 18);
    }
  }
  for (let i = 0; i < values.length; i += 9) {
    for (let axis = 0; axis < 3; axis += 1) {
      min[axis] = Math.min(min[axis], values[i + axis]);
      max[axis] = Math.max(max[axis], values[i + axis]);
    }
  }
  const vertices = [];
  const indices = [];
  const shared = new Map();
  for (let i = 0; i < values.length; i += 9) {
    const vertex = Array.from(values.slice(i, i + 9), value => Math.round(value * 1e6) / 1e6);
    const key = vertex.join(',');
    if (!shared.has(key)) {
      shared.set(key, vertices.length / 9);
      vertices.push(...vertex);
    }
    indices.push(shared.get(key));
  }
  const geometry = Buffer.from(Float32Array.from(vertices).buffer);
  const large = vertices.length / 9 > 65535;
  const index = Buffer.from((large ? Uint32Array.from(indices) : Uint16Array.from(indices)).buffer);
  const bytes = Buffer.concat([geometry, index, Buffer.alloc((4 - index.length % 4) % 4)]);
  const attribute = { bufferView: 0, componentType: 5126, count: vertices.length / 9, type: 'VEC3' };
  const gltf = {
    asset: {version: '2.0', generator: 'Unity Engineering equipment visualizer'},
    scene: 0,
    scenes: [{nodes:[0]}],
    nodes: [{mesh:0,name:kind}],
    meshes: [{primitives:[{attributes:{POSITION:0,NORMAL:1,COLOR_0:2},material:0,indices:3}]}],
    materials: [{name:'Fabricated metal',pbrMetallicRoughness:{metallicFactor:0.82,roughnessFactor:0.31}}],
    buffers: [{byteLength:bytes.length}],
    bufferViews: [{buffer:0,byteOffset:0,byteLength:geometry.length,byteStride:36,target:34962},{buffer:0,byteOffset:geometry.length,byteLength:index.length,target:34963}],
    accessors: [{...attribute,byteOffset:0,min,max},{...attribute,byteOffset:12},{...attribute,byteOffset:24},{bufferView:1,componentType:large?5125:5123,count:indices.length,type:'SCALAR'}]
  };
  const metadata = JSON.stringify(gltf);
  const json = Buffer.from(metadata.padEnd(Math.ceil(metadata.length / 4) * 4, ' '));
  const header = Buffer.alloc(20);
  header.write('glTF');
  header.writeUInt32LE(2,4);
  header.writeUInt32LE(28 + json.length + bytes.length,8);
  header.writeUInt32LE(json.length,12);
  header.write('JSON',16);
  const binary = Buffer.alloc(8);
  binary.writeUInt32LE(bytes.length);
  binary.write('BIN\0',4);
  fs.writeFileSync(`${output}/${kind}.glb`, Buffer.concat([header,json,binary,bytes]));
}
