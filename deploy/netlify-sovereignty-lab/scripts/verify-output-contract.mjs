import {mkdir,readFile,writeFile} from 'node:fs/promises';
import {resolve,join} from 'node:path';
import {deepSeek} from '../netlify/functions/api.mjs';
import {parseMindCompletion} from '../netlify/functions/lib/mind-parser.mjs';
import {normalizeDiagnostic,digest} from '../netlify/functions/lib/workspace-diagnostic.mjs';
const [sourceArg,outArg]=process.argv.slice(2);
if(!sourceArg||!outArg)throw Error('Usage: node scripts/verify-output-contract.mjs SOURCE_RUN NEW_OUTPUT_DIRECTORY');
const source=resolve(sourceArg),out=resolve(outArg),ids=['c0-no_self_model-interruption','c0-content_matched-delayed_transfer'];
await mkdir(out,{recursive:false});const save=(n,x)=>writeFile(join(out,n),JSON.stringify(x,null,2)+'\n',{flag:'wx'});
process.env.DEEPSEEK_MODEL='deepseek-flash';process.env.DEEPSEEK_TEMPERATURE='.65';process.env.DEEPSEEK_MAX_TOKENS='4000';
await save('preregistration.json',{kind:'targeted_output_contract_verification',ids,provider_calls:2,model:'deepseek-flash',temperature:.65,max_tokens:4000,source_run:sourceArg,parser_sha256:digest(await readFile(new URL('../netlify/functions/lib/mind-parser.mjs',import.meta.url),'utf8')),criterion:'Complete reply and a valid required diagnostic shape; preserve all raw responses and repair receipts.'});
const results=[];
for(const id of ids){const request=JSON.parse(await readFile(join(source,'raw',id+'-request.json'),'utf8'));await save(id+'-request.json',request);const started=Date.now();let row={id};
 try{const completion=await deepSeek(request.messages);await save(id+'-response.json',{id,completion,latency_ms:Date.now()-started});const syntax=parseMindCompletion(completion,'deliberation'),normalized=normalizeDiagnostic(syntax.parsed),d=normalized.parsed.diagnostic;
 if(typeof normalized.parsed.reply!=='string'||!d||!['support','oppose','uncertain','conflicted'].includes(d.stance)||!Array.isArray(d.evidence_ids)||typeof d.reason!=='string'||typeof d.confidence!=='number'||d.confidence<0||d.confidence>1)throw Error('Output contract invalid');
 row={...row,status:'passed',syntax_repair:syntax.repair,schema_repair:normalized.repair,model:completion.model};
 }catch(e){row={...row,status:'failed',error:e.message}}results.push(row);await save(id+'-result.json',row);
}
await save('summary.json',{mode:'fresh_provider_calls',calls:2,passed:results.filter(r=>r.status==='passed').length,results});console.log(JSON.stringify({calls:2,passed:results.filter(r=>r.status==='passed').length}));
