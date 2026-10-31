import fs from 'node:fs/promises'
import {fileURLToPath} from 'node:url'
import {resolve,dirname} from 'node:path'
import assert from 'node:assert/strict'
if(!process.argv[2])throw Error('Usage: summarize.mjs <run.json>')
const report=JSON.parse(await fs.readFile(process.argv[2]))
const plan=JSON.parse(await fs.readFile(resolve(dirname(fileURLToPath(import.meta.url)),'../references/cases.json')))
const ids=new Set(),counts={'not-run':0,passed:0,failed:0,blocked:0}
for(const c of report.cases){
 assert.ok(plan.cases.some(p=>p.id===c.id),'Unknown case '+c.id)
 assert.ok(!ids.has(c.id),'Duplicate case '+c.id);ids.add(c.id)
 assert.ok(Object.hasOwn(counts,c.status),'Invalid status '+c.id);counts[c.status]++
 if(c.status==='passed')assert.ok(c.observed?.trim()&&c.evidence?.length&&c.mode,'Passed without evidence '+c.id)
 if(['failed','blocked'].includes(c.status))assert.ok(c.reason?.trim(),'Missing reason '+c.id)
}
assert.equal(ids.size,plan.cases.length,'Missing cases; leave unexecuted ones as not-run')
console.log(JSON.stringify({counts,allPassed:counts.passed===ids.size,modelSubmissions:report.modelSubmissions,costCny:report.costCny},null,2))
