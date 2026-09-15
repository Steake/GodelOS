import {readFile,writeFile} from 'node:fs/promises';
import assert from 'node:assert/strict';
import {parseMindCompletion} from '../netlify/functions/lib/mind-parser.mjs';
import {normalizeDiagnostic,digest} from '../netlify/functions/lib/workspace-diagnostic.mjs';
const cases=['c0-content_matched-interruption','c0-no_state-interruption','c0-full-delayed_transfer','nested-imagination-close','redundant-trailing-close','literal-string-control'],results=[];
for(const id of cases){
 const raw=JSON.parse(await readFile(new URL('../tests/fixtures/'+id+'.json',import.meta.url),'utf8'));
 const before=digest(raw),syntax=parseMindCompletion(raw.completion,'deliberation'),schema=normalizeDiagnostic(syntax.parsed);
 assert.equal(digest(raw),before);assert.ok(schema.parsed.reply);assert.ok(schema.parsed.diagnostic);
 results.push({case:id,raw_id:raw.id,raw_unchanged:true,syntax_repair:syntax.repair,schema_repair:schema.repair,reply_characters:schema.parsed.reply.length,diagnostic:schema.parsed.diagnostic});
}
const output={mode:'offline_exact_response_replay',provider_calls:0,passed:results.length,results};
if(process.argv[2])await writeFile(process.argv[2],JSON.stringify(output,null,2)+'\n');
console.log(JSON.stringify({passed:results.length,provider_calls:0}));
