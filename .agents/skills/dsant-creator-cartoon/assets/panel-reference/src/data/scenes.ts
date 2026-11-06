import approved from './approved.json';
import {SCENE_FRAMES,VO_KEYS,voLocal,wordLocal,FPS,type VoKey} from '../utils/timing';
import {evaluateTrack,orbit} from '../utils/animation';
export type Vec3 = [number,number,number];
export type EaseName = "linear" | "inOut" | "out" | "in" | "soft";

export type VideoConfig = {width:number;height:number;fps:number;durationInFrames:number;theme:string;language:string};
export type CameraKey = {at:number;position:Vec3;target:Vec3;zoom?:number;easing?:EaseName};
export type CameraPlan = {projection:"perspective"|"orthographic";movement:"dolly-in"|"dolly-out"|"vertical"|"orbit"|"tracking"|"split"|"hold";keys:CameraKey[]};
export type SceneObject = {id:string;type:string;visible:boolean;state?:{start:string;end:string}};
export type TrackAnimation = {type:"interpolate"|"spring";target:string;startFrame:number;endFrame:number;from?:number;to?:number;easing?:EaseName;damping?:number;unit?:"u3d"|"px"|"deg"|"rad"|"0-1"};
export type SceneBadge = {text:string;variant:"positive"|"negative"|"info"|"warning";appearAt:number;disappearAt?:number;subtitle?:string;slot?:"center"|"left"|"right";icon?:"?";size?:"normal"|"large"};
export type CaptionBlock={text:string;from:number;to:number};
export type AudioCue={kind:"narration"|"sfx";src:string;at:number;volume:number;status:"planned"|"ready"};
export type ScenePlan={id:string;startFrame:number;durationInFrames:number;voKey:VoKey;narration:string;camera:CameraPlan;objects:SceneObject[];animations:TrackAnimation[];badges:SceneBadge[];highlights:string[];captions:CaptionBlock[];audioCues:AudioCue[]};


export const VIDEO:VideoConfig={width:1080,height:1920,fps:30,durationInFrames:1200,theme:'RR Painel por dentro',language:'pt-BR'};
// Poses recalibradas para o painel 3D de 4,6 unidades. A narrativa aprovada não muda.
const poses=[
 orbit([0,-.12,0],26,-13,14),
 orbit([0,.1,0],25,-6,13),
 orbit([0,.65,.3],30,22,13),
 orbit([0,.6,.3],28,13,9),
 orbit([0,.12,.4],25,2,8),
 orbit([0,.05,.4],27,-9,14),
 orbit([0,.1,.5],29,-15,15),
 orbit([0,.1,.5],30,-10,14),
];
export const scenes:ScenePlan[]=(approved as unknown as ScenePlan[]).map((sc,i)=>{
 const times=SCENE_FRAMES[i];const ratio=times.durationInFrames/sc.durationInFrames;
 const animations=sc.animations.map(a=>({...a,startFrame:Math.round(a.startFrame*ratio),endFrame:Math.min(times.durationInFrames,Math.round(a.endFrame*ratio))}));
 if(i===1){const t=wordLocal('s2',6);animations.find(a=>a.target==='panel.explode')!.startFrame=Math.max(0,t-24);animations.find(a=>a.target==='panel.explode')!.endFrame=t+30;}
 if(i===3){const a=animations.find(a=>a.target==='panel.demo')!;a.startFrame=Math.max(25,wordLocal('s4',3)-15);a.endFrame=wordLocal('s4',3);}
 const voKey=VO_KEYS[i];
 return {...sc,startFrame:times.from,durationInFrames:times.durationInFrames,voKey,
 camera:{...sc.camera,keys:[{at:0,...poses[i]},...(i===2?[{at:Math.round(times.durationInFrames*.52),...orbit([0,.8,.4],25,28,12),easing:'soft' as const}]:[]),{at:times.durationInFrames-1,...poses[i+1],easing:'soft'}]},
 animations,audioCues:[{kind:'narration',src:`audio/vo/${voKey}.wav`,at:voLocal(voKey),volume:1,status:'ready'}],
 badges:sc.badges.map(b=>({...b,appearAt:0,disappearAt:times.durationInFrames})),
 captions:[],
 };
});
export const track=(target:string,frame:number,fallback=0)=>evaluateTrack(scenes,target,frame,FPS,fallback);
export const sceneAt=(frame:number)=>scenes.find(sc=>frame>=sc.startFrame&&frame<sc.startFrame+sc.durationInFrames)??scenes[scenes.length-1];
export const isVisible=(id:string,frame:number)=>sceneAt(frame).objects.some(o=>o.id===id&&o.visible);
let cursor=0;for(const sc of scenes){if(sc.startFrame!==cursor)throw new Error('Timeline descontínua');cursor+=sc.durationInFrames;for(const a of sc.animations){if(a.startFrame<0||a.endFrame>sc.durationInFrames||a.endFrame<=a.startFrame)throw new Error('Trilha fora da cena: '+a.target);}}
if(cursor!==VIDEO.durationInFrames)throw new Error('Soma de frames incorreta');
