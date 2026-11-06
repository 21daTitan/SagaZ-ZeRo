import React,{useMemo} from 'react';
import {registerRoot,Composition,AbsoluteFill,useCurrentFrame,Sequence,Audio,staticFile,interpolate} from 'remotion';
import {ThreeCanvas} from '@remotion/three';
import {useThree} from '@react-three/fiber';
import * as THREE from 'three';
import data from './data.json';
const TOTAL=data.reduce((a,b)=>a+b.frames,0), PI=Math.PI;
const clamp=(n:number)=>Math.max(0,Math.min(1,n));
const lerp=(a:number,b:number,t:number)=>a+(b-a)*t;
function Ball({p=[0,0,0],s=[1,1,1],c='#fff',rough=.7,metal=0,...props}:any){return <mesh position={p} scale={s} castShadow receiveShadow {...props}><sphereGeometry args={[1,24,16]}/><meshStandardMaterial color={c} roughness={rough} metalness={metal}/></mesh>}
function Round({p=[0,0,0],s=[1,1,1],r=[0,0,0],c='#fff',radius=.1,metal=0,rough=.7,opacity=1,...props}:any){const geo=useMemo(()=>{const w=s[0],h=s[1],rr=Math.min(radius,w/3,h/3,s[2]/3);const sh=new THREE.Shape();sh.moveTo(-w/2+rr,-h/2);sh.lineTo(w/2-rr,-h/2);sh.quadraticCurveTo(w/2,-h/2,w/2,-h/2+rr);sh.lineTo(w/2,h/2-rr);sh.quadraticCurveTo(w/2,h/2,w/2-rr,h/2);sh.lineTo(-w/2+rr,h/2);sh.quadraticCurveTo(-w/2,h/2,-w/2,h/2-rr);sh.lineTo(-w/2,-h/2+rr);sh.quadraticCurveTo(-w/2,-h/2,-w/2+rr,-h/2);const g=new THREE.ExtrudeGeometry(sh,{depth:s[2]-rr*2,bevelEnabled:true,bevelThickness:rr,bevelSize:rr*.5,bevelSegments:3,steps:1,curveSegments:8});g.translate(0,0,-(s[2]-rr*2)/2);return g;},[...s,radius]);return <mesh position={p} rotation={r} geometry={geo} castShadow receiveShadow {...props}><meshStandardMaterial color={c} roughness={rough} metalness={metal} transparent={opacity<1} opacity={opacity}/></mesh>}
function Line({points,c='#27313a',width=.015}:any){const g=useMemo(()=>new THREE.TubeGeometry(new THREE.CatmullRomCurve3(points.map((p:any)=>new THREE.Vector3(...p))),12,width,7,false),[JSON.stringify(points),width]);return <mesh geometry={g}><meshStandardMaterial color={c}/></mesh>}
function Limb({a,b,c,width=.06}:any){const mid=a.map((x:number,i:number)=>(x+b[i])/2),v=new THREE.Vector3(...b).sub(new THREE.Vector3(...a));const q=new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(0,1,0),v.clone().normalize());return <mesh position={mid} quaternion={q} castShadow><capsuleGeometry args={[width,Math.max(.001,v.length()-2*width),6,12]}/><meshStandardMaterial color={c} roughness={.85}/></mesh>}
function Phone(){return <group><Round s={[.22,.4,.034]} c="#15232e" radius={.025} metal={.4}/><Round p={[0,0,.022]} s={[.18,.33,.009]} radius={.015} c="#67becd"/><Ball p={[0,-.16,.03]} s={[.012,.012,.005]} c="#d9f0ec"/></group>}
function Hero({mode='stand',f=0,p=[0,0,0],turn=0}:any){const walk=mode==='push'?Math.sin(f*.18):0;const phone=mode==='phone';const drive=mode==='drive';const push=mode==='push';const strain=push?Math.sin(f*.19)*.035:Math.sin(f*.035)*.012;const blink=f%123<5;const brow=push?.11:phone?-.06:0;
return <group position={p} rotation={[push?.24:0,turn,0]}>
<Round p={[0,.96,0]} s={[.46,.62,.26]} radius={.09} c="#204b64"/>
<Round p={[0,1.01,.142]} s={[.31,.48,.025]} c="#2b657c" radius={.02}/>
<Line points={[[0,.76,.16],[0,1.28,.16]]} c="#b9c5bf" width={.008}/>
{[-1,1].map(k=><group key={k}>
<Limb a={[k*.13,.69,0]} b={[k*.14,.38,push?walk*k*.13:drive?.3:0]} width={.085} c="#253343"/>
<Limb a={[k*.14,.38,push?walk*k*.13:drive?.3:0]} b={[k*.14,.12,push?-walk*k*.12:drive?.44:.02]} width={.07} c="#253343"/>
<Round p={[k*.14,.075,push?-walk*k*.12+.08:drive?.5:.1]} s={[.22,.14,.4]} radius={.055} c="#e1d4b9"/>
<Round p={[k*.14,.024,push?-walk*k*.12+.08:drive?.5:.1]} s={[.23,.035,.41]} radius={.012} c="#344448"/>
<Ball p={[k*.29,1.18,0]} s={[.14,.16,.15]} c="#245b73"/>
</group>)}
{[-1,1].map(k=>{let elbow=[k*.33,.91,.05],hand=[k*.33,.65,.09];if(push){elbow=[k*.31,1.2,.35];hand=[k*.28,1.12,.67]}if(drive){elbow=[k*.29,1.01,.25];hand=[k*.24,1.1,.47]}if(phone&&k===1){elbow=[.43,1.04,.19];hand=[.37,1.65,.24]}return <group key={k}><Limb a={[k*.26,1.2,0]} b={elbow} c="#efcda0" width={.062}/><Limb a={elbow} b={hand} c="#efcda0" width={.052}/><Ball p={hand} s={[.07,.09,.065]} c="#f5d7ad"/>{phone&&k===1&&<group position={[.4,1.67,.2]} rotation={[0,.7,-.12]}><Phone/></group>}</group>})}
<Ball p={[0,1.35,0]} s={[.1,.12,.1]} c="#e8bb8b"/>
<group position={[0,1.85+strain,0]} rotation={[phone?-.05:push?.06:0,Math.sin(f*.025)*.035,phone?-.06:0]}>
<Ball s={[.44,.48,.39]} c="#f4d8ae" rough={.8}/>
{[-1,1].map(k=><group key={k}><Ball p={[k*.432,-.025,0]} s={[.08,.115,.055]} c="#e8bc90"/><Ball p={[k*.153,.045,.362]} s={[.105,blink?.014:.13,.045]} c="#fff6df"/><Ball p={[k*.153,.04,.401]} s={[.045,blink?.008:.065,.018]} c="#293e47"/><Ball p={[k*.14,.065,.42]} s={[.014,blink?.004:.018,.008]} c="#fff"/><Line points={[[k*.23,.22+brow,.35],[k*.15,.24,.379],[k*.08,.21-brow,.36]]} width={.018} c="#53463b"/></group>)}
<Ball p={[0,-.06,.398]} s={[.07,.065,.07]} c="#e6b989"/>
<Line points={push?[[-.10,-.23,.33],[0,-.19,.376],[.10,-.23,.33]]:phone?[[-.12,-.20,.34],[0,-.24,.375],[.12,-.20,.34]]:[[-.1,-.21,.34],[0,-.235,.375],[.1,-.21,.34]]} width={.013} c="#865c45"/>
<Ball p={[0,.30,-.035]} s={[.46,.22,.39]} c="#1e6587" rough={.9}/>
<Round p={[0,.29,-.43]} s={[.42,.045,.34]} radius={.02} c="#144e6e"/>
<Line points={[[0,.51,0],[0,.43,.22],[0,.31,.36]]} width={.007} c="#4c91a8"/>
<Ball p={[0,.52,-.03]} s={[.035,.017,.035]} c="#467f91"/>
</group>
</group>}
function Car({f=0,drive=false,broken=false}:any){const wh=drive?-f*.09:0;
return <group>
<Round p={[0,.57,0]} s={[4.05,.67,1.6]} c="#246b88" metal={.45} rough={.3} radius={.17}/>
<Round p={[.92,.86,0]} s={[1.5,.19,1.52]} c="#2e7692" metal={.45} radius={.08}/>
<Round p={[-1.5,.86,0]} s={[.85,.19,1.5]} c="#24657f" metal={.45} radius={.06}/>
<Round p={[.55,1.18,0]} s={[1.3,.46,.02]} r={[0,PI/2,0]} c="#72a0aa" opacity={.3} radius={.02}/><Round p={[-.3,1.49,0]} s={[1.65,.12,1.43]} c="#276d88" metal={.4} radius={.05}/>
{[-1,1].map(z=><group key={z}>
<Round p={[-.3,1.18,z*.68]} s={[1.67,.56,.035]} c="#315f72" radius={.08}/>
<Round p={[.12,1.19,z*.706]} s={[.72,.43,.014]} c="#77a9b3" opacity={.24} rough={.23} metal={.3} radius={.045}/>
<Round p={[-.73,1.19,z*.706]} s={[.72,.43,.014]} c="#648d9e" rough={.25} metal={.3} radius={.045}/>
<Round p={[-.05,.78,z*.807]} s={[.2,.035,.025]} c="#c1cad0" metal={.8} radius={.01}/>
<Round p={[.6,1.04,z*.88]} s={[.19,.14,.22]} c="#21627d" radius={.045}/>
{[-1.22,1.22].map(x=><group key={x} position={[x,.40,z*.79]} rotation={[0,0,wh]}><mesh rotation={[PI/2,0,0]} castShadow><cylinderGeometry args={[.40,.40,.24,32]}/><meshStandardMaterial color="#182a31" roughness={.95}/></mesh><mesh position={[0,0,z*.13]} rotation={[PI/2,0,0]}><cylinderGeometry args={[.25,.25,.025,24]}/><meshStandardMaterial color="#a7adb1" metalness={.8} roughness={.3}/></mesh>{[0,1,2,3,4].map(k=><Round key={k} p={[0,0,z*.15]} s={[.035,.44,.02]} c="#52626a" radius={.006} r={[0,0,k*PI/5]}/>)}<Ball p={[0,0,z*.17]} s={[.075,.075,.025]} c="#e1e0cf" metal={.7}/></group>)}
<Round p={[1.96,.66,z*.52]} s={[.055,.22,.35]} c="#ffe0a2" radius={.02} rough={.2}/>
<Round p={[-2.02,.66,z*.58]} s={[.03,.2,.22]} c="#b84c3e" radius={.02}/>
</group>)}
<Round p={[2.04,.41,0]} s={[.07,.12,1.3]} c="#61747b" radius={.03} metal={.7}/>
<Round p={[2.06,.61,0]} s={[.07,.2,.46]} c="#142f3f" radius={.02}/>
{[-.10,0,.10].map(z=><Round key={z} p={[2.1,.62,z]} s={[.015,.11,.02]} c="#667e86" radius={.003}/>)}
<Round p={[-2.08,.43,0]} s={[.03,.16,.48]} c="#d7dbd1" radius={.01}/>
{drive&&<group position={[-.1,-.15,.05]} scale={.70} rotation={[0,PI/2,0]}><Hero mode="drive" f={f}/></group>}
{broken&&Array.from({length:9},(_,k)=>{const t=((f*.014+k/9)%1);return <Ball key={k} p={[1.05+Math.sin(k*2+t*3)*.2,1+t*1.9,-.15-t*.4]} s={[.12+t*.25,.13+t*.23,.11+t*.22]} c={k%2?'#9da7a6':'#bcc0b6'}/>})}
</group>}
function Environment({f,driving=false}:any){const offset=driving?(f*.10)%8:0;return <>
<color attach="background" args={['#83959d']}/><fog attach="fog" args={['#83959d',16,48]}/>
<hemisphereLight args={['#b7d6e8','#495249',1.4]}/><ambientLight intensity={.25}/>
<directionalLight position={[-7,8,-5]} color="#ffce8b" intensity={3.5} castShadow shadow-mapSize={[1024,1024]} shadow-camera-left={-10} shadow-camera-right={10} shadow-camera-top={10} shadow-camera-bottom={-10} shadow-bias={-.001}/>
<directionalLight position={[2,4,8]} color="#b9e7ff" intensity={1}/>
<mesh rotation={[-PI/2,0,0]} receiveShadow><planeGeometry args={[140,140]}/><meshStandardMaterial color="#58645a" roughness={1}/></mesh>
<Round p={[0,-.035,0]} s={[100,.08,7]} c="#414e53" radius={.01}/>
{Array.from({length:15},(_,k)=><group key={k} position={[k*8-48-offset,0,0]}>
<Round p={[0,.012,0]} s={[3.3,.009,.1]} c="#c6c7ab" radius={.003}/>
{[-1].map(z=><group key={z}>
<Round p={[0,.12,z*4.5]} s={[7.94,.25,1.6]} c="#a2a59a" radius={.03}/>
<Round p={[0,.05,z*3.62]} s={[7.97,.15,.16]} c="#c2c2af" radius={.02}/>
<Round p={[1.7,1.85,z*7]} s={[4.7,3.7+(k%3),3.1]} c={['#89968a','#a59982','#748c8d'][k%3]} radius={.06}/>
{[0,1,2].map(w=><group key={w}><Round p={[w*1.2+.5,2.4,z*5.43]} s={[.65,.9,.025]} c="#354e59" radius={.025}/><Round p={[w*1.2+.5,2.4,z*5.4]} s={[.022,.9,.025]} c="#b0b8ad" radius={.004}/></group>)}
<Round p={[-2,1.65,z*4.15]} s={[.065,3.3,.065]} c="#48585b" radius={.02}/>
<Limb a={[-2,3.2,z*4.15]} b={[-2,3.45,z*3.65]} c="#48585b" width={.035}/>
<Round p={[-2,3.44,z*3.55]} s={[.18,.07,.43]} c="#fff0bd" radius={.02}/>
<Ball p={[-.7,.55,z*5]} s={[.7,.55,.5]} c="#526d58"/>
</group>)}
</group>)}
{Array.from({length:60},(_,k)=><Round key={k} p={[((k*13)%97)-48,.012,((k*17)%65)/10-3.25]} s={[.08,.006,.025]} r={[0,k,0]} c="#788080" radius={.002}/>)}
</>}
function Camera({i,f,local}:any){const {camera}=useThree();let pos:number[],target:number[];const t=local/data[i].frames;
if(i===0){if(local<65){pos=[3.1,1.7,2.9];target=[.1,1.05,0]}else{pos=[lerp(6,5.5,t),2.8,9.5];target=[0,.85,0]}}
else if(i===1){pos=[lerp(-5.5,-5.0,t),3.1,11.5];target=[-.9,1,0]}
else if(i===2){pos=[lerp(4.3,4.0,t),2.7,lerp(7.5,7.0,t)];target=[2.5,1.25,1.4]}
else if(i===3){pos=[lerp(4.5,4.2,t),2.6,7.1];target=[2.5,1.3,1.5]}
else{pos=[5.8,2.7,7.5];target=[1.4,1.05,.6]}
camera.position.set(...pos as [number,number,number]);camera.lookAt(...target as [number,number,number]);return null}
function World({i,f,local}:any){return <><Environment f={local} driving={i===0}/><Camera i={i} f={f} local={local}/>
<group position={[0,i===0?Math.sin(f*.3)*.008:0,0]}><Car f={local} drive={i===0} broken={i===1&&local>24}/></group>
{i===1&&<Hero mode="push" f={local} p={[-2.67+Math.sin(local*.05)*.02,0,.1]} turn={PI/2}/>}
{i>=2&&<Hero mode={i===2?'phone':'stand'} f={local} p={[2.5,0,1.6]} turn={-.2}/>}
{i===0&&<Round p={[-.7,1.02,.3]} s={[.45,.45,.4]} c="#b98d5c" radius={.03}/>}
</>}
function Video(){const f=useCurrentFrame();let i=data.findIndex(s=>f>=s.start&&f<s.start+s.frames);if(i<0)i=4;const s=data[i],local=f-s.start;const fade=clamp(local/10);const final=i===4;
return <AbsoluteFill style={{background:'#12232a',fontFamily:'DejaVu Sans,sans-serif',color:'#fff7e8'}}>
<ThreeCanvas width={1080} height={1920} shadows dpr={1} gl={{antialias:true}} camera={{position:[5,2.7,7],fov:36}}><World i={i} f={f} local={local}/></ThreeCanvas>
<AbsoluteFill style={{background:'linear-gradient(180deg,rgba(12,27,35,.65) 0%,transparent 35%,transparent 54%,rgba(9,23,31,.95) 89%)'}}/>
<div style={{position:'absolute',top:210,left:76,right:76,opacity:fade}}><div style={{fontSize:23,letterSpacing:4,color:'#f1d2a1'}}>ANTES DO PRÓXIMO IMPREVISTO</div><div style={{fontSize:69,fontWeight:900,letterSpacing:-2,lineHeight:1.08,marginTop:22}}>{['FALTAVAM\n5 MINUTOS.','NÃO ERA HORA\nDE PARAR.','E AGORA?','PREPARAR COMEÇA\nCOM UMA CONVERSA.','CONTE COM\nORIENTAÇÃO.'][i].split('\n').map((t,k)=><div key={k}>{t}</div>)}</div></div>
{!final&&<div style={{position:'absolute',left:85,right:85,bottom:385,fontSize:37,lineHeight:1.4,textShadow:'0 2px 7px #000',opacity:fade}}>{s.text}</div>}
{final&&<div style={{position:'absolute',left:80,right:70,top:1200,opacity:fade}}><div style={{fontSize:45,fontWeight:900}}>VITOR DOS SANTOS</div><div style={{fontSize:30,color:'#c3d7da',marginTop:13}}>Consultor APVS Brasil</div><div style={{fontSize:24,letterSpacing:4,color:'#a9e2bd',marginTop:35}}>FALE COMIGO NO WHATSAPP</div><div style={{fontSize:76,fontWeight:900,letterSpacing:-2,marginTop:12,whiteSpace:'nowrap'}}>(21) 99879-3765</div><div style={{fontSize:29,marginTop:15}}>@21apvs</div></div>}
<div style={{position:'absolute',left:85,bottom:260,fontSize:17,letterSpacing:2,color:'#c5cecb'}}>HISTÓRIA FICTÍCIA · CONSULTORIA APVS BRASIL</div>
{data.map((s,k)=><Sequence key={k} from={s.start+8}><Audio src={staticFile(`vo${k}.mp3`)}/></Sequence>)}
<Audio src={staticFile('ambience.wav')} volume={1}/><Audio src={staticFile('music.wav')} volume={.10} loop/>
</AbsoluteFill>}
registerRoot(()=> <Composition id="APVS" component={Video} durationInFrames={TOTAL} fps={30} width={1080} height={1920}/>);
