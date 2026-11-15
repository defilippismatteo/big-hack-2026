import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {scenes} from '../src/motion/scenes.js';
const evidence=JSON.parse(readFileSync(new URL('../public/motion/case.json',import.meta.url)));
test('animation percentages are the recorded joint outcome sums, not forecast CTR',()=>{
 const d=evidence.decision;
 const total=Object.values(d.actions).reduce((a,b)=>a+b,0);
 const click=Object.entries(d.probabilities).filter(([k])=>k.startsWith('click__')).reduce((s,[,v])=>s+v,0);
 assert(Math.abs(total-1)<1e-9);assert(Math.abs(click-d.actions.click)<1e-9);
 assert.equal(d.calibratedToHumanCtr,false);assert.equal(evidence.persona.persona_id,'abbigliamento-P001');
 for(const v of Object.values(d.actions))assert(scenes[1].svg.includes((100*v).toFixed(1).replace('.',',')+'%'));
});
test('motion assets are self-contained vectors with accessible text and reduced-motion fallback',()=>{
 assert.equal(scenes.length,3);
 for(const scene of scenes){
  assert(scene.svg.includes('<title'));assert(scene.svg.includes('<desc'));assert(scene.svg.includes('prefers-reduced-motion'));
  assert(!/<image\b|<script\b|<foreignObject\b/.test(scene.svg));assert(!scene.svg.includes('data:image/'));
  assert(!/(?:href|src)="https?:/.test(scene.svg));assert.equal(scene.duration,8);
  assert.equal(readFileSync(new URL('../public/motion/'+scene.download,import.meta.url),'utf8'),scene.svg);
 }
});
test('interview excerpts are literal and Decision outputs are not shown to the interviewee',()=>{
 const i=evidence.interview;
 assert.equal(i.decisionOutputsVisible,false);assert.equal(i.receipt.status,'completed');
 assert(i.answers.positive.includes(i.literalExcerpts.positive));assert(i.answers.negative.includes(i.literalExcerpts.negative));
 assert(scenes[2].svg.includes('Nessuna probabilità'));
});
