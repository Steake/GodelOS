import {authorised,createHandler} from './api.mjs';

// One durable round per delivery. Duplicate deliveries are fenced by the CAS lease.
export default async function handler(request){
 if(!authorised(request))return new Response('Unauthorized',{status:401});
 const payload=await request.json();
 if(typeof payload.run_id!=='string'||!Number.isInteger(payload.expected_round))return new Response('Invalid round reservation',{status:422});
 return createHandler()(new Request('https://development.invalid/api/development/advance',{
  method:'POST',headers:{Authorization:request.headers.get('Authorization'),'Content-Type':'application/json'},body:JSON.stringify(payload)}));
}
export const config={background:true};
