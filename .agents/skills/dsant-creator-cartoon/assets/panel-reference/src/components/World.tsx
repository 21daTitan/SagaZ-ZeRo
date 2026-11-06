import React,{useMemo} from 'react';
import * as THREE from 'three';
import {useCurrentFrame} from 'remotion';
import {track,scenes,sceneAt} from '../data/scenes';
import {progress,lerp,type Vec3} from '../utils/animation';
import {wordLocal} from '../utils/timing';

const outline=[[-2.2,.65],[-1.6,1.22],[1.6,1.22],[2.2,.65],[1.95,-.95],[1.35,-1.25],[-1.35,-1.25],[-1.95,-.95]];
function shape(scale=1){const s=new THREE.Shape();outline.forEach(([x,y],i)=>i?s.lineTo(x*scale,y*scale):s.moveTo(x*scale,y*scale));s.closePath();return s;}
const bodyGeo=new THREE.ExtrudeGeometry(shape(),{depth:.42,bevelEnabled:true,bevelSegments:3,steps:1,bevelSize:.09,bevelThickness:.075,curveSegments:10});
const boardGeo=new THREE.ExtrudeGeometry(shape(.9),{depth:.07,bevelEnabled:true,bevelSegments:1,bevelSize:.02,bevelThickness:.02,steps:1});
const frameShape=shape(.98);
const hole=new THREE.Path();hole.moveTo(-1.68,.74);hole.lineTo(-1.68,-.65);hole.lineTo(1.68,-.65);hole.lineTo(1.68,.74);hole.closePath();frameShape.holes.push(hole);
const bezelGeo=new THREE.ExtrudeGeometry(frameShape,{depth:.15,bevelEnabled:true,bevelSegments:3,bevelThickness:.04,bevelSize:.045,steps:1});
function Box({p,size,color,metal=.15,rough=.5,emissive,opacity=1}:{p:Vec3;size:Vec3;color:string;metal?:number;rough?:number;emissive?:string;opacity?:number}){return <mesh position={p} castShadow receiveShadow><boxGeometry args={size}/><meshStandardMaterial color={color} metalness={metal} roughness={rough} emissive={emissive??'#000000'} emissiveIntensity={emissive?.5:0} transparent={opacity<1} opacity={opacity}/></mesh>}
const Screw:React.FC<{x:number;y:number;z:number;turn?:number}>=({x,y,z,turn=0})=><group position={[x,y,z]} rotation={[0,0,turn]}><mesh rotation={[Math.PI/2,0,0]} castShadow><cylinderGeometry args={[.105,.105,.065,12]}/><meshStandardMaterial color="#a7acac" metalness={.8} roughness={.3}/></mesh><Box p={[0,0,.036]} size={[.12,.022,.006]} color="#20272a"/></group>;
const digitMap:Record<number,number[]>={0:[0,1,2,3,4,5],1:[1,2],2:[0,1,6,4,3],3:[0,1,6,2,3],4:[5,6,1,2],5:[0,5,6,2,3],6:[0,5,6,4,2,3],7:[0,1,2],8:[0,1,2,3,4,5,6],9:[0,1,2,3,5,6]};
const segments:Vec3[]=[[0,.4,0],[.2,.2,0],[.2,-.2,0],[0,-.4,0],[-.2,-.2,0],[-.2,.2,0],[0,0,0]];
function Digit({x,n,on}:{x:number;n:number;on:number}){return <group position={[x,.14,.054]}>{segments.map((p,i)=><Box key={i} p={p} size={i===0||i===3||i===6?[.32,.067,.015]:[.067,.29,.015]} color={digitMap[n].includes(i)&&on>.1?'#d8efbe':'#25372d'} emissive={digitMap[n].includes(i)&&on>.1?'#92c47b':undefined}/>)}</group>}
function Display({on,focus}:{on:number;focus:number}){return <group><Box p={[0,0,0]} size={[3.38,1.45,.08]} color={on>.1?'#314d39':'#1a2423'} rough={.3}/><Digit x={-.64} n={0} on={on}/><Digit x={0} n={0} on={on}/><Box p={[.82,.45,.06]} size={[.55,.025,.012]} color={on>.1?'#c6dba9':'#26322e'}/>{Array.from({length:6},(_,i)=><Box key={i} p={[.63+i*.12,-.08+i*.017,.06]} size={[.065,.13+i*.04,.012]} color={on>.1?'#b5cf95':'#26322e'}/>)}{Array.from({length:3},(_,i)=><mesh key={i} position={[-.7+i*.52,-.56,.06]}><circleGeometry args={[.055,12]}/><meshBasicMaterial color={on>.1?['#d7b969','#e27d66','#a3c58c'][i]:'#29322e'}/></mesh>)}{focus>0&&<mesh position={[focus===1?-.3:focus===2?.94:0,focus===3?-.55:.04,.08]}><ringGeometry args={[focus===3?.13:.45,focus===3?.15:.47,48]}/><meshBasicMaterial color="#e6d38b" transparent opacity={.6} depthWrite={false}/></mesh>}</group>}
function PCB({scan}:{scan:number}){
 const pins=Array.from({length:10},(_,i)=><React.Fragment key={i}><Box p={[-.55+i*.12,.44,.14]} size={[.045,.2,.035]} color="#c9bfa0" metal={.7}/><Box p={[-.55+i*.12,-.44,.14]} size={[.045,.2,.035]} color="#c9bfa0" metal={.7}/></React.Fragment>);
 return <group><mesh geometry={boardGeo} castShadow receiveShadow><meshStandardMaterial color="#205448" roughness={.75}/></mesh>
 {Array.from({length:12},(_,i)=>{const y=-.8+i*.14;const len=.6+(i%4)*.18;return <React.Fragment key={i}><Box p={[-1.32,y,.084]} size={[len,.018,.008]} color="#77907a" metal={.45}/><Box p={[1.2,y,.084]} size={[len,.018,.008]} color="#77907a" metal={.45}/><Box p={[-1.05+(i%3)*.09,y+.04,.084]} size={[.018,.1,.008]} color="#77907a"/></React.Fragment>})}
 <Box p={[0,0,.15]} size={[1.22,.7,.12]} color="#1b2225" rough={.65}/>{pins}
 {Array.from({length:6},(_,i)=><group key={i} position={[-1.35+(i%3)*1.28,i<3?.76:-.68,.1]}><Box p={[0,0,.09]} size={[.24,.14,.12]} color="#aa9677"/><Box p={[-.14,0,.09]} size={[.05,.15,.13]} color="#c4c5b7"/><Box p={[.14,0,.09]} size={[.05,.15,.13]} color="#c4c5b7"/></group>)}
 <group position={[1.4,.25,.12]}><mesh rotation={[Math.PI/2,0,0]}><cylinderGeometry args={[.18,.18,.32,16]}/><meshStandardMaterial color="#b8c2c4" metalness={.8} roughness={.3}/></mesh><Box p={[0,0,.17]} size={[.2,.024,.015]} color="#354044"/></group>
 <Box p={[0,-1.13,.11]} size={[1.3,.36,.35]} color="#ded3af" rough={.65}/>{Array.from({length:8},(_,i)=><Box key={i} p={[-.48+i*.138,-1.25,.31]} size={[.045,.16,.03]} color="#be9a52" metal={.7}/>)}
 {scan>0&&<mesh position={[-1.8+scan*3.6,0,.35]}><planeGeometry args={[.032,2.05]}/><meshBasicMaterial color="#e6d38b" transparent opacity={.8} depthWrite={false}/></mesh>}
 </group>
}
function Glove({amount}:{amount:number}){return <group position={[-2.65+amount*1.55,-1.35,.75]} rotation={[0,0,-.15]}><Box p={[-1.6,-.15,-.1]} size={[2.5,.75,.65]} color="#313b40" rough={.85}/><mesh position={[-.2,0,0]} scale={[.75,.47,.35]} castShadow><sphereGeometry args={[1,16,12]}/><meshStandardMaterial color="#17252d" roughness={.88}/></mesh>{Array.from({length:4},(_,i)=><mesh key={i} position={[.32,-.29+i*.16,.16]} rotation={[0,0,-.1]} castShadow><capsuleGeometry args={[.105,.65,4,8]}/><meshStandardMaterial color="#203440" roughness={.8}/></mesh>)}<mesh position={[.08,.47,.06]} rotation={[0,0,-.8]} castShadow><capsuleGeometry args={[.14,.47,4,8]}/><meshStandardMaterial color="#203440" roughness={.8}/></mesh></group>}
function Phone({amount}:{amount:number}){return <group position={[1.45,-2.1+amount*.75,2.8]} rotation={[-.13,-.35,-.16]} scale={.72}><Box p={[0,0,0]} size={[1.6,2.9,.18]} color="#0c1217" metal={.5}/><Box p={[0,.04,.105]} size={[1.43,2.62,.012]} color="#364b43" emissive="#263b32"/><Box p={[0,.2,.14]} size={[1.1,.67,.02]} color="#101e21"/><Box p={[0,.2,.16]} size={[.75,.3,.01]} color="#6b7e72"/><mesh position={[0,-.96,.15]}><circleGeometry args={[.18,32]}/><meshBasicMaterial color="#eeeade"/></mesh><mesh position={[0,1.23,.15]}><circleGeometry args={[.046,16]}/><meshBasicMaterial color="#101719"/></mesh></group>}

export const World:React.FC=()=>{
 const f=useCurrentFrame();const sc=sceneAt(f);const i=scenes.indexOf(sc);const lf=f-sc.startFrame;
 const ex=track('panel.explode',f);const demo=track('panel.demo',f);
 const stop=1-progress(f,0,14);const y=i===0?.18+stop*.55:0;
 const tilt=lerp(-.12,-.035,progress(f,0,60));
 const inspect=track('inspection.opacity',f);const scan=track('inspection.progress',f);
 const expand=ex;
 const focus=i===3?(lf<wordLocal('s4',4)?1:lf<wordLocal('s4',6)?2:3):0;
 const hideHand=1-progress(f,scenes[1].startFrame,scenes[1].startFrame+24);
 const phone=track('contact.opacity',f);
 const shellMat=useMemo(()=>new THREE.MeshStandardMaterial({color:'#222c32',roughness:.48,metalness:.3}),[]);
 return <>
  <ambientLight intensity={.7}/><hemisphereLight args={['#d5e8ed','#263034',1.2]}/>
  <directionalLight position={[-5,10,12]} intensity={3.5} color="#fff3dd" castShadow shadow-mapSize={[1024,1024]} shadow-camera-left={-8} shadow-camera-right={8} shadow-camera-top={8} shadow-camera-bottom={-8} shadow-bias={-.001}/>
  <directionalLight position={[8,3,-5]} intensity={4.5} color="#b4c5cd"/>
  <directionalLight position={[-6,0,4]} intensity={.7} color="#c4dbc4"/>
  <mesh position={[0,-2.45,0]} receiveShadow><boxGeometry args={[12,.26,7]}/><meshStandardMaterial color="#222e34" roughness={.8} metalness={.25}/></mesh>
  <Box p={[0,-2.6,2.9]} size={[12,.04,.03]} color="#607277" metal={.6}/>

  <group position={[0,y,.25]} rotation={[tilt,.04,Math.sin(f/160)*.018]}>
   <group position={[0,-expand*.7,-expand*.7]}>
    <mesh geometry={bodyGeo} castShadow receiveShadow material={shellMat}/>
    {[-1.4,1.4].map((x,j)=><group key={j}><Box p={[x,-1.26,.1]} size={[.3,.48,.32]} color="#1a242b"/><Screw x={x} y={-1.42} z={.3}/></group>)}
    <Box p={[0,-1.39,-.03]} size={[1.5,.37,.4]} color="#1c252b"/>
   </group>
   <group position={[0,-expand*.18,.46]} scale={[1,1,.65]}><PCB scan={inspect>0?scan:0}/></group>
   <group position={[0,expand*.65,.65+expand*.6]}><Display on={demo} focus={demo>.1?focus:0}/></group>
   <group position={[0,expand*1.75,.76+expand*1.15]}>
    <mesh geometry={bezelGeo} castShadow material={shellMat}/>
    <Box p={[0,.96,.21]} size={[1,.023,.01]} color="#b4b8ac"/>
    {[-1.88,1.88].map(x=>[.51,-.77].map(y=><Screw key={`${x}-${y}`} x={x} y={y} z={.24+expand*.16} turn={expand*2}/>))}
    <Box p={[0,-.96,.22]} size={[.5,.065,.03]} color="#a8aeaa"/>
   </group>
  </group>
  {hideHand>.01&&<group position={[-(1-hideHand)*5,0,0]}><Glove amount={progress(f,0,12)}/></group>}
  {i===0&&<group position={[0,-2.0,.2]} scale={[1,1-progress(f,sc.durationInFrames-24,sc.durationInFrames)*.6,1]}><Box p={[-2,-.6,0]} size={[.1,1.5,2.2]} color="#151e23"/><Box p={[2,-.6,0]} size={[.1,1.5,2.2]} color="#151e23"/><Box p={[0,-.6,-1.05]} size={[4,1.5,.1]} color="#151e23"/><Box p={[0,-.55,1.05]} size={[4,1.5,.1]} color="#344148"/>{Array.from({length:14},(_,k)=><Box key={k} p={[-1.8+k*.277,-.5,1.11]} size={[.04,1.2,.01]} color="#4e5a5c"/>)}</group>}
  {i===6&&<Phone amount={phone}/>}
 </>
};
