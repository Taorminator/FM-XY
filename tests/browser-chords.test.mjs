import { readFileSync } from 'node:fs';
import vm from 'node:vm';
import assert from 'node:assert/strict';
const html = readFileSync(process.argv[2] || 'docs/try/index.html', 'utf8');
const js = html.match(/<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/)?.[1];
assert.ok(js);
function part(start,end) {
 const a=js.indexOf(start),b=js.indexOf(end,a+start.length);
 assert.ok(a>=0&&b>a,'missing code region '+start);
 return js.slice(a,b);
}
const script=[
 part('const NOTE_NAMES=','const CHORD_TYPES='),
 part('const SCALES=','// Global performance solo'),
 part('function chordLabel(','const midiToHz='),
 part('const midiToHz=','const makeEmptyPatterns='),
 part('function getWhiteMidiKeys(','function isSafeProject('),
 part('function previewChordOnKeyboard(','buildKeys();'),
 part('async function pressKey(','function releaseKey(')
].join('\n');
const state={page:'CHORD',selectedTrack:0,pattern:0,selectedStep:0,
 chord:{root:5,type:'m7',voicing:'OPEN',style:'BLOCK'},
 key:0,scale:'minor',octave:0,playing:false,recording:false,
 tracks:[{preset:'E-PIANO'},{},{},{}],arpMode:'OFF'};
const notes=[],chords=[],recorded=[],releases=[];
const audio={now:0,releaseTrackVoices:t=>releases.push(t),
 playNote:(n,t)=>notes.push([n,t]),playChord:c=>chords.push(c),playArpChord:c=>chords.push(c)};
const keysByMidi=new Map();
for(let midi=53;midi<=79;midi++){
 const white=![1,3,6,8,10].includes(midi%12),classes=new Set(white?['white']:['black']);
 const el={dataset:{},title:'',textContent:'',
  classList:{contains:k=>classes.has(k),add:k=>classes.add(k),remove:k=>classes.delete(k),toggle:(k,v)=>v?classes.add(k):classes.delete(k)},
  setAttribute(n,v){this[n]=v}};
 if(white)el.dataset.whiteIndex=String([...keysByMidi.values()].filter(x=>x.classList.contains('white')).length);
 keysByMidi.set(midi,el);
}
const context=vm.createContext({s:state,audio,keysByMidi,domKeyTimers:new Map(),chordHintEnabled:true,
 updateUI(){},toast(){},setTimeout(){return 1},clearTimeout(){},
 async enableSound(){return true},recordNote:(s,t,step,ev)=>recorded.push(ev),nextRecordStep:()=>7,
 TRACK_NAMES:['CHORD','BASS','LEAD','DRUM'],DRUM_LANES:['KICK','SNARE','CHH','OHH']});
vm.runInContext(script,context,{timeout:1000});
const run=s=>vm.runInContext(s,context,{timeout:1000});
assert.deepEqual([53,54,55].map(n=>run('chordKeyboardNote(s,'+n+')')),[65,66,67]);
for(let root=0;root<12;root++)for(let oct=-2;oct<=2;oct++){
 state.chord.root=root;state.octave=oct;
 const values=Array.from({length:27},(_,i)=>run('chordKeyboardNote(s,'+(53+i)+')'));
 assert.equal(new Set(values).size,27);
 assert.equal(values[0]%12,root);
 assert.ok(values.every(v=>v>=24&&v<=108));
}
state.chord.root=5;state.octave=0;
run('previewChordOnKeyboard(suggestNextChords(s)[0].chord)');
const highlighted=[...keysByMidi].filter(([,el])=>el.classList.contains('suggested'));
assert.ok(highlighted.length>0);
for(const [m]of highlighted) assert.ok(run('chordNotes(suggestNextChords(s)[0].chord).some(n=>n%12===chordKeyboardNote(s,'+m+')%12)'));
assert.equal(keysByMidi.get(53).textContent,'F');
const before=JSON.stringify(state.chord);
await run('(async()=>{await pressKey(53,false,0);await pressKey(55,false,1);await pressKey(54,true,0)})()');
assert.deepEqual(notes.map(([n])=>n),[65,67,66]);
assert.equal(chords.length,0);
assert.equal(releases.length,0);
assert.equal(JSON.stringify(state.chord),before);
state.playing=true;state.recording=true;
await run('pressKey(57,false,2)');
assert.equal(recorded[0].kind,'note');
assert.equal(recorded[0].note,69);
state.page='KEY';
await run('pressKey(53,false,0)');
assert.equal(chords.length,1);
assert.equal(JSON.stringify(state.chord),before);
console.log('PASS: distinct pitches, 60 root/octave maps, '+highlighted.length+' highlighted keys, recording and KEY mode');
