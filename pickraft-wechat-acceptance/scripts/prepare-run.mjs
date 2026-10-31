import fs from 'node:fs/promises'
import {resolve,dirname} from 'node:path'
import {fileURLToPath} from 'node:url'
import {createHash} from 'node:crypto'
import {execFileSync} from 'node:child_process'
const skill=resolve(dirname(fileURLToPath(import.meta.url)),'..'),root=resolve(skill,'../../..')
const out=resolve(root,'.local/wechat-acceptance',new Date().toISOString().replace(/[:.]/g,'-'))
const {cases}=JSON.parse(await fs.readFile(resolve(skill,'references/cases.json')))
const manifest=JSON.parse(await fs.readFile(resolve(skill,'assets/manifest.json')))
for(const item of manifest.files){
 const b=await fs.readFile(resolve(skill,'assets',item.file))
 if(createHash('sha256').update(b).digest('hex')!==item.sha256)throw Error('Fixture checksum failed: '+item.file)
}
if(new Set(cases.map(c=>c.id)).size!==cases.length)throw Error('Duplicate case IDs')
for(const c of cases){
 if(!c.steps.length||!c.expected.length)throw Error('Incomplete case: '+c.id)
 if(c.history?.evidence)await fs.access(resolve(root,c.history.evidence))
 for(const asset of c.assets||[])if(asset!=='boundary')await fs.access(resolve(skill,'assets',asset))
}
await fs.mkdir(out,{recursive:true})
const report={date:new Date().toISOString(),commit:execFileSync('git',['rev-parse','HEAD'],{cwd:root,encoding:'utf8'}).trim(),clientVersion:null,apiVersion:null,mode:null,modelSubmissions:0,costCny:null,cases:cases.map(c=>({id:c.id,title:c.title,status:'not-run',mode:c.mode,observed:'',evidence:[],reason:''}))}
await fs.writeFile(resolve(out,'run.json'),JSON.stringify(report,null,2)+'\n')
console.log(JSON.stringify({cases:cases.length,verifiedAssets:manifest.files.length,report:resolve(out,'run.json')}))
