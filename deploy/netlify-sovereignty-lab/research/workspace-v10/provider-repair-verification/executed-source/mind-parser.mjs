import {parseCompletion,sha256} from './core.mjs';

// Inspect delimiters without interpreting or changing any string/value.
function structure(source){
 const stack=[],rootKeys=[];let inString=false,escape=false,start=0,rootEnd=-1;
 for(let i=0;i<source.length;i++){
  const ch=source[i];
  if(inString){
   if(escape)escape=false;else if(ch==='\\')escape=true;else if(ch==='"'){
    inString=false;
    if(stack.length===1&&stack[0]==='{'&&/^\s*:/.test(source.slice(i+1)))rootKeys.push(JSON.parse(source.slice(start,i+1)));
   }
   continue;
  }
  if(ch==='"'){inString=true;start=i;}
  else if(ch==='{'||ch==='[')stack.push(ch);
  else if(ch==='}'||ch===']'){
   if(stack.pop()!==(ch==='}'?'{':'['))return {invalid:true};
   if(!stack.length&&rootEnd<0)rootEnd=i;
  }
 }
 return {stack,inString,escape,rootEnd,duplicateKeys:new Set(rootKeys).size!==rootKeys.length};
}

// Preserve exact provider bytes. Recover only an unambiguous object boundary,
// on a normal stop. Never infer values, close strings or repair truncation.
export function parseMindCompletion(completion,mode){
  try{return {parsed:parseCompletion(completion.text,mode),repair:null};}catch(original){
    const source=String(completion.text||'').trim();
    if(completion.finish_reason!=='stop'||!source.endsWith('}'))throw original;
    // The provider sometimes closes the root early, then continues its fields:
    // {"reply":"..."},"cognitive_mode":"...",...}. Remove that one delimiter.
    // Candidate JSON must then parse, and duplicate root keys are prohibited.
    {let depth=0,inString=false,escape=false;
    for(let i=0;i<source.length;i++){
      const ch=source[i];
      if(inString){if(escape)escape=false;else if(ch==='\\')escape=true;else if(ch==='"')inString=false;continue;}
      if(ch==='"'){inString=true;continue;}
      if(ch==='{'||ch==='[')depth++;
      else if(ch==='}'||ch===']')depth--;
      if(depth===0&&ch==='}'){
        if(/^\s*,\s*"[a-z_]+"\s*:/.test(source.slice(i+1))){
          const candidate=source.slice(0,i)+source.slice(i+1),shape=structure(candidate);
          if(!shape.invalid&&!shape.inString&&!shape.stack.length&&!shape.duplicateKeys){
            try{return {parsed:parseCompletion(candidate,mode),repair:{kind:'remove_premature_root_close',removed_at:i,raw_sha256:sha256(completion.text),derived_sha256:sha256(candidate)}};}catch{}
          }
        }
        break;
      }
    }
    }
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
