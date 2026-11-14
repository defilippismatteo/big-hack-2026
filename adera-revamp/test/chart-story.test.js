import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import test from 'node:test';
import {chartDomain} from '../src/overview/chartModel.js';
const read=name=>JSON.parse(readFileSync(new URL('../public/data/'+name+'.json',import.meta.url)));
test('zoom and zero-based domains preserve and contain narrow, flat and missing series',()=>{
 for(const values of [[1.160212851,1.17538999],[1.17,1.17],[0,0],[null,NaN,undefined],[]]) {
  for(const zoom of [true,false]) {
   const d=chartDomain(values,zoom); assert(d.max>d.min);assert.equal(d.ticks.length,5);
   for(const v of values.filter(Number.isFinite)) assert(v>=d.min&&v<=d.max);
   if(!zoom)assert.equal(d.min,0);
  }
 }
 const values=[1.160212851,1.17538999];assert(chartDomain(values).max-chartDomain(values).min<.1);
});
test('acquired interview reports remain separate from quantitative forecast data and cover all 600 interviews and 36 assets',()=>{
 const story=read('product-story'), overview=read('overview');
 assert.equal(story.reportsKind,'synthetic_interviews');assert.equal(story.examplesKind,'synthetic');
 assert.match(story.examplesSource.sha256,/^[a-f0-9]{64}$/);
 assert.match(story.reportsSource.frozenSha256,/^[a-f0-9]{64}$/);
 assert.equal(story.reportsSource.nInterviews,600);
 assert.equal(story.reportsSource.nAssets,36);
 assert.equal(Object.keys(overview.simulatedDecision).length,36);
 for(const campaign of overview.campaigns) {
  const example=story.examples[campaign.vertical], report=story.reports[campaign.vertical];
  assert.equal(example.vertical,campaign.vertical);assert(example.persona_id&&example.model&&example.provider&&example.interview);
  assert.equal(report.n_interviews,200);
  assert.equal(report.positive.length,3);assert.equal(report.negative.length,3);
 }
 assert.equal(overview.forecast.length,699);assert(!('reports' in overview));
});
