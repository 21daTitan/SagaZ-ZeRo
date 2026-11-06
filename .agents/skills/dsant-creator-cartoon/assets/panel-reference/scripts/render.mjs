import {bundle} from '@remotion/bundler';
import {openBrowser,selectComposition,renderStill,renderMedia} from '@remotion/renderer';
import fs from 'node:fs';
import path from 'node:path';
import chromium from '@sparticuz/chromium';
const serveUrl=await bundle({entryPoint:'src/index.ts',outDir:path.resolve('out/bundle')});
const chromiumOptions={gl:'swangle',disableWebSecurity:true};
const browserExecutable=process.env.CHROME_BINARY??await chromium.executablePath();
const browser=await openBrowser('chrome',{browserExecutable,chromiumOptions});
const comp=await selectComposition({serveUrl,id:'RRPainel',puppeteerInstance:browser,chromiumOptions});
const mode=process.argv[2]??'stills';
try{
 if(mode==='stills'){
 fs.mkdirSync('out/stills',{recursive:true});
 const frames=process.argv.slice(3).length?process.argv.slice(3).map(Number):[0,20,85,160,250,330,405,490,560,665,720,820,940,1020,1125,1190];
 for(const frame of frames){await renderStill({composition:comp,serveUrl,frame,output:`out/stills/f${String(frame).padStart(4,'0')}.png`,imageFormat:'png',scale:.5,puppeteerInstance:browser,chromiumOptions});console.log('STILL',frame)}
 }else{
 let last=-1;
 await renderMedia({composition:comp,serveUrl,codec:'h264',outputLocation:'out/rr-painel-raw.mp4',crf:18,concurrency:3,puppeteerInstance:browser,chromiumOptions,imageFormat:'jpeg',jpegQuality:95,onProgress:({progress,renderedFrames,encodedFrames})=>{const n=Math.floor(progress*20);if(n>last){last=n;console.log(`PROGRESS ${Math.round(progress*100)}% frames=${renderedFrames} encoded=${encodedFrames}`)}}});
 console.log('RENDER COMPLETE');
 }
}finally{await browser.close({silent:true})}
