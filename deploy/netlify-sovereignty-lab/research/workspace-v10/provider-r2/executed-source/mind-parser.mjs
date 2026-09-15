import {parseCompletion,sha256} from './core.mjs';

// Preserve exact provider bytes. The sole permitted syntax recovery closes at
// most two objects after a completed final object, only on a normal provider
// stop. Never infer missing values, close strings or repair truncated output.
export function parseMindCompletion(completion,mode){
  try{return {parsed:parseCompletion(completion.text,mode),repair:null};}catch(original){
    const source=String(completion.text||'').trim();
    if(completion.finish_reason!=='stop'||!source.endsWith('}'))throw original;
    const stack=[];let inString=false,escape=false;
    for(const char of source){
      if(inString){if(escape)escape=false;else if(char==='\\')escape=true;else if(char==='"')inString=false;continue;}
      if(char==='"')inString=true;
      else if(char==='{'||char==='[')stack.push(char);
      else if(char==='}'||char===']'){if(stack.pop()!==(char==='}'?'{':'['))throw original;}
    }
    if(inString||escape||stack.length<1||stack.length>2||stack.some(c=>c!=='{'))throw original;
    const appended='}'.repeat(stack.length),candidate=source+appended;
    try{return {parsed:parseCompletion(candidate,mode),repair:{kind:'close_complete_objects_at_eof',appended,raw_sha256:sha256(completion.text),derived_sha256:sha256(candidate)}};}catch{throw original;}
  }
}

// Extract only a complete top-level reply string. Do not invent missing bytes.
export function recoverReply(completion){
  const source=String(completion.text||'').trim().replace(/^```(?:json)?\s*/i,'');
  if(!source.startsWith('{'))return null;
  let depth=0,inString=false,escaped=false;
  for(let i=0;i<source.length;i++){
    const ch=source[i];
    if(inString){if(escaped)escaped=false;else if(ch==='\\')escaped=true;else if(ch==='"')inString=false;continue;}
    if(ch==='{'||ch==='[')depth++;else if(ch==='}'||ch===']')depth--;
    if(ch==='"'){
      if(depth===1){const match=source.slice(i).match(/^"reply"\s*:\s*("(?:[^"\\]|\\.)*")/s);if(match){try{const reply=JSON.parse(match[1]);return reply.trim()?reply:null;}catch{return null;}}}
      inString=true;
    }
  }
  return null;
}
