import fs from 'node:fs/promises'
import {createRequire} from 'node:module'
import {fileURLToPath} from 'node:url'
import {resolve,dirname} from 'node:path'
import {createHash} from 'node:crypto'
const root=resolve(dirname(fileURLToPath(import.meta.url)),'../../../..')
const sharp=createRequire(resolve(root,'apps/api/package.json'))('sharp')
const out=process.argv.includes('--boundary')?resolve(root,'.local/wechat-acceptance/boundary'):resolve(root,'.agents/skills/pickraft-wechat-acceptance/assets')
await fs.mkdir(out,{recursive:true})
if(process.argv.includes('--boundary')){
 const bytes=Buffer.alloc(3200*2400*3);let x=42
 for(let i=0;i<bytes.length;i++){x^=x<<13;x^=x>>>17;x^=x<<5;bytes[i]=x&255}
 const source=sharp(bytes,{raw:{width:3200,height:2400,channels:3}})
 await source.clone().jpeg({quality:75,chromaSubsampling:'4:4:4'}).toFile(resolve(out,'high-resolution.jpg'))
 await source.clone().png().toFile(resolve(out,'over-limit.png'))
 await sharp({create:{width:3000,height:2000,channels:3,background:'#c75233'}}).withMetadata({orientation:6}).jpeg().toFile(resolve(out,'oriented.jpg'))
 console.log({boundaryDirectory:out});process.exit(0)
}
const shapes={portrait:'<circle cx="320" cy="220" r="110" fill="#e7b58d"/><path d="M150 640V490Q160 340 320 340Q480 340 490 490V640" fill="#526fa8"/><circle cx="282" cy="210" r="12"/><circle cx="358" cy="210" r="12"/><path d="M280 270Q320 300 360 270" fill="none" stroke="#6b4935" stroke-width="9"/>',face:'<ellipse cx="320" cy="310" rx="200" ry="160" fill="#edc395"/><circle cx="250" cy="290" r="16"/><circle cx="390" cy="290" r="16"/><path d="M260 360Q320 410 380 360" fill="none" stroke="#6b4935" stroke-width="10"/>',pose:'<circle cx="320" cy="120" r="60" fill="#bd7f69"/><path d="M320 180V380M320 240L120 160M320 240L520 180M320 380L180 580M320 380L470 570" fill="none" stroke="#526fa8" stroke-width="26"/>',product:'<rect x="210" y="180" width="220" height="330" rx="60" fill="#7fbaa4"/><rect x="250" y="110" width="140" height="90" rx="16" fill="#426757"/><circle cx="320" cy="330" r="65" fill="#f8f5ef"/>',landscape:'<circle cx="470" cy="150" r="70" fill="#e7b75a"/><path d="M0 500L190 200L360 480L500 320L640 500V640H0" fill="#619785"/>',portraitLong:'<circle cx="320" cy="230" r="130" fill="#d28f79"/><rect x="200" y="420" width="240" height="180" fill="#526fa8"/>'}
const manifest=[]
for(const [name,shape] of Object.entries(shapes)){
 const [w,h]=name==='landscape'?[960,640]:name==='portraitLong'?[640,1280]:[640,640]
 const svg=Buffer.from(`<svg xmlns="http://www.w3.org/2000/svg" width="${w}" height="${h}" viewBox="0 0 640 640"><rect width="640" height="640" fill="#f8f5ef"/>${shape}</svg>`)
 await sharp(svg).png().toFile(resolve(out,name+'.png'))
}
await sharp({create:{width:255,height:255,channels:3,background:'#789'}}).png().toFile(resolve(out,'tiny.png'))
await fs.writeFile(resolve(out,'corrupt.jpg'),'Intentionally invalid image fixture. No private data.\n')
await sharp({create:{width:300,height:300,channels:3,background:'#789'}}).gif().toFile(resolve(out,'unsupported.gif'))
for(const name of (await fs.readdir(out)).filter(n=>/\.(png|jpg|gif)$/.test(n)).sort()){
 const b=await fs.readFile(resolve(out,name));let size={};try{const m=await sharp(b).metadata();size={width:m.width,height:m.height}}catch{}
 manifest.push({file:name,sha256:createHash('sha256').update(b).digest('hex'),bytes:b.length,...size,purpose:name==='corrupt.jpg'?'invalid bytes':name==='tiny.png'?'short edge rejection':name==='unsupported.gif'?'unsupported format':'synthetic pipeline fixture'})
}
await fs.writeFile(resolve(out,'manifest.json'),JSON.stringify({origin:'Programmatically authored geometric fixtures; no real people or third-party images. Use freely with this repository.',files:manifest},null,2)+'\n')
console.log({files:manifest.length})
