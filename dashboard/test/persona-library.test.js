import test from 'node:test';
import assert from 'node:assert/strict';
import {existsSync, readFileSync} from 'node:fs';
import {ALL_AVATARS, avatarFor} from '../src/pages/avatarPool.js';
const read=path=>JSON.parse(readFileSync(new URL(path,import.meta.url),'utf8'));
test('the directory exposes every profile and preserves verbatim answers with the frozen asset mapping',()=>{
 const library=read('../public/data/persona-library.json');
 const cards=read('../../data/personas_600/persona_cards.json').personas;
 const frozen=read('../../data/personas_600/interviews/frozen.json').interviews;
 assert.equal(library.personas.length,600);
 assert.equal(new Set(library.personas.map(p=>p.persona_id)).size,600);
 assert.equal(library.assets.length,36);
 const assetIds=new Set(library.assets.map(a=>a.asset_id));
 for(const card of cards){
  const exported=library.personas.find(p=>p.persona_id===card.persona_id);
  for(const [key,value] of Object.entries(card))assert.deepEqual(exported[key],value);
  const source=frozen.find(p=>p.persona_id===card.persona_id);
  assert.equal(exported.answers.length,source.response.answers?.length??0);
  for(const [i,answer] of exported.answers.entries()){
   const original=source.response.answers[i];
   for(const [key,value] of Object.entries(original))assert.deepEqual(answer[key],value);
   assert.equal(answer.asset_id,source.mapping[original.stimulus_id]);
   assert.ok(assetIds.has(answer.asset_id));
  }
 }
});
test('all 600 personas resolve to an existing illustrated avatar PNG',()=>{
 const library=read('../public/data/persona-library.json');
 for(const src of ALL_AVATARS){
  assert.ok(existsSync(new URL('../public'+src,import.meta.url)),`Missing ${src}`);
 }
 const chiara=library.personas.find(p=>p.persona_id==='abbigliamento-P001');
 assert.equal(avatarFor(chiara).src,'/avatars/chiara-hero.png');
 const used=new Set();
 for(const persona of library.personas){
  const {src,bg}=avatarFor(persona);
  assert.ok(ALL_AVATARS.includes(src));
  assert.match(bg,/^#[0-9a-f]{6}$/i);
  used.add(src);
 }
 assert.ok(used.size>=18);
});
