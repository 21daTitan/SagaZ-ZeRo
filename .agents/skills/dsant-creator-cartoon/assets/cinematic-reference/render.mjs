import {bundle} from '@remotion/bundler';
import {selectComposition,renderMedia,renderStill} from '@remotion/renderer';
import chromium from '@sparticuz/chromium';
const executable=await chromium.executablePath();
const serveUrl=await bundle({entryPoint:'src/index.tsx'});
const opts={serveUrl,id:'APVS',browserExecutable:executable,chromiumOptions:{gl:'swangle'}};
const composition=await selectComposition(opts);
if(process.argv[2]==='still'){for(const frame of (process.argv.slice(3).length?process.argv.slice(3).map(Number):[20,180,300,520,800,1120])){await renderStill({...opts,composition,frame,output:`../revisao/frame-${frame}.png`});console.log('STILL',frame)}}else{let last=-1;await renderMedia({...opts,composition,codec:'h264',outputLocation:'../finais/vitor-apvs-cinema-raw.mp4',concurrency:2,crf:19,onProgress:({progress})=>{const n=Math.floor(progress*10);if(n>last){last=n;console.log(n*10)}}})}
