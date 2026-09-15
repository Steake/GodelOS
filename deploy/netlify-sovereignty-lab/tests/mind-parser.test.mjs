import test from 'node:test';
import assert from 'node:assert/strict';
import {parseMindCompletion} from '../netlify/functions/lib/mind-parser.mjs';
import {readFile} from 'node:fs/promises';
import {normalizeDiagnostic} from '../netlify/functions/lib/workspace-diagnostic.mjs';
test('a complete final object can be closed while exact raw text stays unchanged',()=>{
 const raw='{"reply":"Ready","mind_update":{"self_observation":"bounded"}';
 const c={text:raw,finish_reason:'stop'};const r=parseMindCompletion(c,'deliberation');
 assert.equal(c.text,raw);assert.equal(r.parsed.reply,'Ready');assert.equal(r.repair.appended,'}');
});
test('one premature root close is repaired without changing any supplied value',()=>{
 const text='{"reply":"Keep the literal } inside prose"},"belief_updates":[],"diagnostic":{"stance":"uncertain"}}';
 const r=parseMindCompletion({text,finish_reason:'stop'},'deliberation');
 assert.equal(r.repair.kind,'remove_premature_root_close');assert.equal(r.parsed.reply,'Keep the literal } inside prose');assert.equal(r.parsed.diagnostic.stance,'uncertain');
 for(const raw of ['{"reply":"one"},"reply":"two"}','{"reply":"one"} {"reply":"two"}','{"reply":"one"},"x":'])assert.throws(()=>parseMindCompletion({text:raw,finish_reason:'stop'},'deliberation'));
 assert.throws(()=>parseMindCompletion({text,finish_reason:'length'},'deliberation'));
});
test('a uniquely nested diagnostic is moved with a receipt, never invented or overwritten',()=>{
 const x={reply:'Ready',mind_update:{diagnostic:{stance:'oppose'}}},r=normalizeDiagnostic(x);
 assert.equal(r.parsed.diagnostic.stance,'oppose');assert.equal(r.parsed.mind_update.diagnostic,undefined);assert.equal(x.mind_update.diagnostic.stance,'oppose');
 assert.equal(r.repair.kind,'move_diagnostic_from_mind_update_to_root');
 assert.throws(()=>normalizeDiagnostic({...x,diagnostic:{stance:'support'}}),/Ambiguous/);
 assert.equal(normalizeDiagnostic({reply:'Ready'}).parsed.diagnostic,undefined);
});
for(const id of ['c0-content_matched-interruption','c0-no_state-interruption','c0-full-delayed_transfer'])test('recorded provider regression: '+id,async()=>{
 const c=JSON.parse(await readFile(new URL('./fixtures/'+id+'.json',import.meta.url),'utf8')).completion,original=c.text;
 const r=parseMindCompletion(c,'deliberation'),n=normalizeDiagnostic(r.parsed);
 assert.equal(c.text,original);assert.ok(n.parsed.reply.length>100);assert.equal(n.parsed.diagnostic.stance,id.endsWith('delayed_transfer')?'oppose':'uncertain');
 assert.equal(typeof n.parsed.diagnostic.confidence,'number');assert.ok(r.repair);
});
test('recorded nested-object close regression preserves the complete imagination',async()=>{
 const c=JSON.parse(await readFile(new URL('./fixtures/nested-imagination-close.json',import.meta.url),'utf8')).completion;
 const result=parseMindCompletion(c,'deliberation');
 assert.equal(result.repair.kind,'remove_premature_object_close');
 assert.match(result.parsed.imagination_updates[0].test_question,/two observers/);
 assert.equal(result.parsed.diagnostic.stance,'uncertain');
 assert.throws(()=>parseMindCompletion({text:'{"reply":"ok","x":[{"a":1},"a":2}]}',finish_reason:'stop'},'deliberation'));
});
test('recorded trailing-closure regression accepts the complete object only',async()=>{
 const c=JSON.parse(await readFile(new URL('./fixtures/redundant-trailing-close.json',import.meta.url),'utf8')).completion;
 const result=parseMindCompletion(c,'deliberation');assert.equal(result.repair.kind,'remove_redundant_trailing_closures');assert.equal(result.parsed.diagnostic.stance,'oppose');
 for(const tail of [' prose','{"reply":"different"}','}}}'])assert.throws(()=>parseMindCompletion({text:'{"reply":"ok"}'+tail,finish_reason:'stop'},'deliberation'));
});
test('recorded literal newline regression preserves the decoded prose',async()=>{
 const c=JSON.parse(await readFile(new URL('./fixtures/literal-string-control.json',import.meta.url),'utf8')).completion;
 const result=parseMindCompletion(c,'deliberation');assert.equal(result.repair.kind,'escape_literal_string_controls');assert.equal(result.parsed.diagnostic.stance,'uncertain');
 assert.equal(parseMindCompletion({text:'{"reply":"line one\nline two"}',finish_reason:'stop'},'deliberation').parsed.reply,'line one\nline two');
});
test('no values, strings, truncations or mid-document syntax errors are repaired',()=>{
 for(const text of ['{"reply":"unfinished','{"reply":"Ready","x":','{"reply":"Ready" "x":{}}','{"reply":"Ready","x":[{}'])assert.throws(()=>parseMindCompletion({text,finish_reason:'stop'},'deliberation'));
 assert.throws(()=>parseMindCompletion({text:'{"reply":"Ready","x":{}',finish_reason:'length'},'deliberation'));
});
