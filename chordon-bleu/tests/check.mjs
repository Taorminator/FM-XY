// Zero-dependency smoke checks for the standalone CHORDON BLEU browser artifact.
// These are static/syntax checks only. Real browser audio must still be tested in Chromium/Safari.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
const source=fs.readFileSync(new URL('../browser/index.html',import.meta.url),'utf8');
const script=source.match(/<script>\s*([\s\S]*?)<\/script>/);
assert.ok(script,'inline script exists');
new vm.Script(script[1],{filename:'chordon-bleu.js'});
const controls=['play','mutate','keep','wonder','steps','root','quality','newloop','undo','rec','pads','saved','heatname'];
for (const id of controls) assert.ok(source.includes('id="'+id+'"'),'Missing control: '+id);
assert.match(source,/CHORDON.*?BLEU/);
for(const label of ['FLIP','SPICE','SAVE','MIDDLE AGE ENGINEERING'])assert.ok(source.includes(label),'Missing label: '+label);
assert.match(source,/function chordHeat\(/);
assert.match(source,/function harmonicVariation\(/);
assert.match(source,/function sessionLoad\(/);
assert.match(source,/function ensureAudio\(/);
assert.match(source,/manualRoot/);
assert.match(source,/manualQuality/);
assert.ok(!source.includes('<script src="'),'Browser must work as one independent HTML file');
console.log('PASS: CHORDON BLEU static and JavaScript syntax smoke checks');
