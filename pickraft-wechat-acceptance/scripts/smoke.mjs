import fs from 'node:fs/promises'
import {resolve,dirname} from 'node:path'
import {fileURLToPath} from 'node:url'
import {createRequire} from 'node:module'
import assert from 'node:assert/strict'
const root=resolve(dirname(fileURLToPath(import.meta.url)),'../../../..')
const automator=createRequire(resolve(root,'tests/wechat/package.json'))('miniprogram-automator')
const endpoint=process.env.WECHAT_AUTOMATOR_WS||'ws://127.0.0.1:9420'
if(!['127.0.0.1','localhost','[::1]'].includes(new URL(endpoint).hostname))throw Error('Only loopback automator endpoints allowed')
const out=resolve(root,'.local/wechat-acceptance/smoke-'+Date.now())
await fs.mkdir(out,{recursive:true})
const results=[],m=await automator.connect({wsEndpoint:endpoint})
const scrollTop=async()=>Number(await (await m.currentPage()).scrollTop())
const wait=async fn=>{for(let i=0;i<40;i++){if(await fn())return;await new Promise(r=>setTimeout(r,500))}throw Error('UI condition timed out')}
try{
 const p=await m.reLaunch('/pages/index/index')
 // Cached cards can render before the first response installs its pagination cursor.
 await wait(async()=>(await p.$$('.template-card')).length>=24&&(await (await p.$('.feed-status'))?.text())==='加载更多')
 const before=await p.$$('.template-card');results.push({case:'DISC-01',scope:'initial feed renders',count:before.length,status:'passed'})
 await m.pageScrollTo(100000)
 await wait(async()=>(await p.$$('.template-card')).length>before.length)
 const cards=await p.$$('.template-card'),titles=await Promise.all(cards.map(c=>c.text()))
 await m.pageScrollTo(900)
 const scroll=await scrollTop()
 const first=await cards[0].$('.image-button');assert.ok(first)
 await first.tap();await wait(async()=>(await m.currentPage())?.path==='pages/template/index')
 await m.navigateBack();await wait(async()=>(await m.currentPage())?.path==='pages/index/index')
 assert.deepEqual(await Promise.all((await p.$$('.template-card')).map(c=>c.text())),titles)
 await wait(async()=>Math.abs((await scrollTop())-scroll)<=5)
 results.push({case:'DISC-02',scope:'append and detail return',count:cards.length,status:'passed'})
 const nav=await p.$$('.bottom-nav .taroify-button');assert.equal(nav.length,4)
 await nav[3].tap();await wait(async()=>!!await p.$('.personal-page'))
 await nav[0].tap();await wait(async()=>(await p.$$('.template-card')).length===cards.length)
 assert.deepEqual(await Promise.all((await p.$$('.template-card')).map(c=>c.text())),titles)
 await wait(async()=>Math.abs((await scrollTop())-scroll)<=5)
 results.push({case:'DISC-03',scope:'tab return',status:'passed'})
 await m.screenshot({path:resolve(out,'feed.png')})
 const payments=await m.navigateTo('/pages/payments/index')
 await wait(async()=>!!await payments.$('.recharge-packages'))
 await wait(async()=>!(await payments.$('.loading')))
 assert.equal((await payments.$$('.recharge-package')).length,3)
 const buttons=await payments.$$('.taroify-button')
 const purchase=[];for(const b of buttons)if(/^(购买暂未开放|请先登录|立即购买 · ¥)/.test(await b.text()))purchase.push(b)
 assert.equal(purchase.length,1)
 const purchaseLabel=await purchase[0].text()
 if(purchaseLabel==='购买暂未开放'||purchaseLabel==='请先登录')assert.equal(String(await (await purchase[0].$('button')).property('disabled')),'true')
 await m.screenshot({path:resolve(out,'payments.png')})
 results.push({case:'ACCOUNT-06',scope:'package cards and purchase entry render; no order submitted',purchaseLabel,status:'passed'})
 await m.navigateBack()
}catch(e){results.push({status:'failed',reason:e.message});process.exitCode=1}
finally{await fs.writeFile(resolve(out,'result.json'),JSON.stringify({mode:'devtools-real',modelSubmissions:0,results},null,2)+'\n');await m.disconnect()}
console.log(JSON.stringify({output:out,results}))
