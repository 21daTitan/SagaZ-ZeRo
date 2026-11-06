import {Composition} from 'remotion';
import {MainSequence} from './MainSequence';
export const RemotionRoot:React.FC=()=> <Composition id="RRPainel" component={MainSequence} durationInFrames={1200} fps={30} width={1080} height={1920}/>;
