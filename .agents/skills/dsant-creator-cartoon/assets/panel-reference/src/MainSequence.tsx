import React from 'react';
import {ThreeCanvas} from '@remotion/three';
import {AbsoluteFill,Audio,staticFile,useCurrentFrame,spring} from 'remotion';
import {World} from './components/World';
import {CameraController,cameraPoseAt,projectPoint} from './components/CameraController';
import {AnimatedCaptions} from './components/AnimatedCaptions';
import {scenes,sceneAt,track} from './data/scenes';
import {progress} from './utils/animation';
import {wordLocal} from './utils/timing';
import {FONT} from './theme';

const titles=[['PAINEL','PERDIDO?'],['OLHE','POR DENTRO.'],['TESTAR.','DEPOIS DECIDIR.'],['NÃO É SÓ','UM DISPLAY.'],['PODE TER','REPARO.'],['RR ELETRÔNICA','AUTOMOTIVA.'],['ANTES DE TROCAR,','CHAMA A RR.']];
const kickers=['ANTES DE DESCARTAR','UMA PEÇA. VÁRIAS CAMADAS.','SINTOMA NÃO É DIAGNÓSTICO','INFORMAÇÃO NO SEU CAMINHO','A AVALIAÇÃO DEFINE','RR • CARROS E MOTOS','FOTO + RELATO DO DEFEITO'];
function Annotation(){
 const f=useCurrentFrame(),sc=sceneAt(f),i=scenes.indexOf(sc),lf=f-sc.startFrame;
 if(i!==1&&i!==2&&i!==3)return null;
 let text='',point:[number,number,number]=[0,0,0];
 const ex=track('panel.explode',f);
 if(i===1){if(ex<.4)return null;text='POR DENTRO';point=[1.3,-.18*ex,.9];}
 if(i===2){const n=lf<wordLocal('s3',5)?0:lf<wordLocal('s3',10)?1:2;text=['01 / CONECTOR','02 / PLACA','03 / DISPLAY'][n];point=[[.6,-1.2,.8],[.4,-.2,.8],[.8,.65*ex,1.2]][n] as [number,number,number];}
 if(i===3){if(lf<wordLocal('s4',3))return null;const n=lf<wordLocal('s4',4)?0:lf<wordLocal('s4',6)?1:2;text=['VELOCIDADE','COMBUSTÍVEL','ALERTAS'][n];point=[n===1?1:0,n===2?-.5:.2,1];if(lf>wordLocal('s4',7)+12)return null;}
 const pt=projectPoint(cameraPoseAt(f),point);const opacity=progress(lf,0,12)*(1-progress(lf,sc.durationInFrames-12,sc.durationInFrames));
 return <div style={{position:'absolute',inset:0,opacity}}><svg width="1080" height="1920" style={{position:'absolute',inset:0}}><path d={`M ${pt.x} ${pt.y} L ${pt.x-35} ${pt.y+40} L 125 1245`} fill="none" stroke="#d4d9ce" strokeWidth="2" opacity=".65"/><circle cx={pt.x} cy={pt.y} r="7" fill="#e6d38b"/></svg><div style={{position:'absolute',top:1260,left:100,fontSize:28,fontWeight:700,letterSpacing:4,color:'#e1e5db'}}>{text}</div></div>;
}
function Overlay(){
 const f=useCurrentFrame(),sc=sceneAt(f),i=scenes.indexOf(sc),lf=f-sc.startFrame;
 const enter=spring({frame:lf+10,fps:30,config:{damping:22,stiffness:155}});
 const leave=1-progress(lf,sc.durationInFrames-6,sc.durationInFrames);
 const contact=progress(lf,18,48);
 return <AbsoluteFill style={{fontFamily:FONT,color:'#f5f3e9'}}>
  <div style={{position:'absolute',top:208,left:90,right:90,display:'flex',justifyContent:'space-between',alignItems:'center'}}><div style={{fontSize:33,fontWeight:700,letterSpacing:-1}}>RR<span style={{fontSize:21,fontWeight:500,letterSpacing:3,marginLeft:16,color:'#aab6ba'}}>PAINEL POR DENTRO</span></div><div style={{fontSize:21,letterSpacing:3,color:'#9caeb2'}}>01</div></div>
  <div style={{position:'absolute',left:90,top:290,right:90,opacity:leave,transform:`translateY(${(1-enter)*22}px)`}}>
   <div style={{fontSize:22,letterSpacing:4,color:'#c9c9b3',fontWeight:500,marginBottom:21}}>{kickers[i]}</div>
   <div style={{fontWeight:700,fontSize:i===6?77:i===2?80:i===5?79:100,letterSpacing:-4,lineHeight:1.02}}>{titles[i][0]}<br/><span style={{color:i===0?'#e6d38b':i===4?'#bad498':'#f5f3e9'}}>{titles[i][1]}</span></div>
  </div>
  <Annotation/>
  {i===0&&<div style={{position:'absolute',top:1237,left:90,fontSize:28,color:'#c9cfc8',letterSpacing:2,opacity:progress(lf,15,25)}}>TROCAR OU REPARAR?</div>}
  {i===4&&<div style={{position:'absolute',top:1210,left:90,right:90,opacity:progress(lf,15,38)}}><div style={{fontSize:22,letterSpacing:4,color:'#a6b5b5',marginBottom:19}}>DEPOIS DO DIAGNÓSTICO</div><div style={{display:'flex',alignItems:'center',gap:30}}><div style={{fontSize:36,fontWeight:700,color:'#bad498',paddingBottom:12,borderBottom:'3px solid #bad498'}}>REPARAR</div><span style={{fontSize:21,color:'#7e939a'}}>OU</span><div style={{fontSize:36,fontWeight:700,color:'#e2e3dc',paddingBottom:12,borderBottom:'3px solid #596b72'}}>SUBSTITUIR</div></div></div>}
  {i===5&&<div style={{position:'absolute',top:1233,left:90,right:90,opacity:progress(lf,12,28),fontSize:29,lineHeight:1.5,fontWeight:500}}>Alcântara · São Gonçalo · RJ<br/><span style={{color:'#cbd7b7'}}>Atendimento em todo o Brasil</span></div>}
  {i===6&&<div style={{position:'absolute',left:90,right:90,top:1204,opacity:contact,transform:`translateY(${(1-contact)*20}px)`}}><div style={{fontSize:22,color:'#b7c8af',letterSpacing:4,marginBottom:14}}>WHATSAPP • RR ELETRÔNICA</div><div style={{fontSize:82,fontWeight:700,letterSpacing:-2,whiteSpace:'nowrap'}}>(21) 96752-9104</div><div style={{fontSize:25,color:'#bac7c6',marginTop:12,opacity:progress(f,1090,1120)}}>Mande uma foto e conte o defeito.</div></div>}
  <div style={{position:'absolute',left:90,right:90,top:1538,height:2,background:'#334047'}}><div style={{height:'100%',width:`${f/1199*100}%`,background:'#d5d8c4'}}/></div>
  <div style={{position:'absolute',top:1564,left:90,right:90,display:'flex',justifyContent:'space-between',fontSize:17,color:'#7f929a',letterSpacing:2}}><span>DEMONSTRAÇÃO 3D</span><span>RR ELETRÔNICA AUTOMOTIVA</span></div>
 </AbsoluteFill>
}
export const MainSequence:React.FC=()=>{
 return <AbsoluteFill style={{background:'#101a20'}}>
  <style>{`@font-face{font-family:'RR Sans';src:url('${staticFile('fonts/bold.woff2')}');font-weight:700 900}@font-face{font-family:'RR Sans';src:url('${staticFile('fonts/medium.woff2')}');font-weight:400 600}`}</style>
  <AbsoluteFill style={{background:'radial-gradient(ellipse at 52% 47%,#32434c 0%,#17242c 44%,#0b131a 85%)'}}/>
  <ThreeCanvas width={1080} height={1920} dpr={1} shadows gl={{antialias:true,alpha:true,powerPreference:'high-performance'}} camera={{fov:24,near:.1,far:200,position:[0,4,27]}}><CameraController/><World/></ThreeCanvas>
  <AbsoluteFill style={{pointerEvents:'none',background:'linear-gradient(0deg,rgba(9,17,23,.98) 4%,rgba(9,17,23,.95) 25%,transparent 37%,transparent 66%,rgba(9,17,23,.6) 83%,rgba(9,17,23,.95) 100%)'}}/>
  <Overlay/><AnimatedCaptions/>
  <Audio src={staticFile('audio/mix.wav')} volume={1}/>
 </AbsoluteFill>
};
