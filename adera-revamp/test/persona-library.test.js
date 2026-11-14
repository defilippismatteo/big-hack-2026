import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const read=path=>JSON.parse(readFileSync(new URL(path,import.meta.url),'utf8'));
test('the directory exposes every profile and preserves verbatim answers with the frozen asset mapping',()=>{
 const library=read('../public/data/persona-library.json');
 const cards=read('../../artifacts/personas_t3_600/persona_cards.json').personas;
 const frozen=read('../../artifacts/personas_t3_600/interviews/frozen.json').interviews;
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
