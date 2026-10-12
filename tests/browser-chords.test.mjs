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
 part('const MAX_VOICES=','/* --- display.mjs --- */'),
 part('function getWhiteMidiKeys(','function isSafeProject('),
 part('function previewChordOnKeyboard(','buildKeys();'),
 part('async function pressKey(','function releaseKey(')
].join('\n');
const state={page:'CHORD',selectedTrack:0,pattern:0,selectedStep:0,
 chord:{root:5,type:'m7',voicing:'OPEN',style:'BLOCK'},
 key:0,scale:'minor',octave:0,playing:false,recording:false,
 tracks:[{preset:'E-PIANO'},{},{},{}],arpMode:'OFF'};
const notes=[],chords=[],arpeggios=[],recorded=[],releases=[],playedPitches=[];
const audio={now:0,releaseTrackVoices:t=>releases.push(t),
 playNote:(n,t)=>notes.push([n,t]),
 playChord:(chord,track,at,duration,settings,octave)=>chords.push({chord,octave}),
 playArpChord:(chord,track,at,duration,settings,state,octave)=>arpeggios.push({chord,octave})};
const keysByMidi=new Map();
for(let midi=53;midi<=79;midi++){
 const white=![1,3,6,8,10].includes(midi%12),classes=new Set(white?['white']:['black']);
 const el={dataset:{},title:'',textContent:'',
  classList:{contains:k=>classes.has(k),add:k=>classes.add(k),remove:k=>classes.delete(k),toggle:(k,v)=>v?classes.add(k):classes.delete(k)},
  setAttribute(n,v){this[n]=v}};
 if(white)el.dataset.whiteIndex=String([...keysByMidi.values()].filter(x=>x.classList.contains('white')).length);
 keysByMidi.set(midi,el);
}
const context=vm.createContext({s:state,audio,keysByMidi,playedPitches,domKeyTimers:new Map(),chordHintEnabled:true,
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
assert.equal(notes.length,0,'CHORD keys must not play solitary notes');
assert.equal(chords.length,3,'each key must trigger a complete chord');
assert.deepEqual(chords.map(x=>x.chord.root),[5,7,6]);
assert.ok(chords.every(x=>x.chord.type==='m7'));
assert.deepEqual(chords.map(x=>x.octave),[0,0,0]);
assert.equal(releases.length,0,'simultaneous chords should not be force-cut');
assert.equal(JSON.stringify(state.chord),before,'ROOT and TYPE are never changed by playing');
// Exercise the real Web Audio voice scheduling method, not only the key router.
for(const x of chords) {
 context.testChord=x.chord;context.testOctave=x.octave;
 run('MiniAudio.prototype.playChord.call({playNote:(note)=>playedPitches.push(note)},testChord,0,0,.68,{},testOctave)');
}
assert.deepEqual(playedPitches.slice(0,4),[65,72,75,80],'F m7 OPEN pitches');
assert.deepEqual(playedPitches.slice(4,8),[67,74,77,82],'G m7 OPEN pitches');
assert.deepEqual(playedPitches.slice(8,12),[66,73,76,81],'F# m7 OPEN pitches');
state.playing=true;state.recording=true;
await run('pressKey(57,false,2)');
assert.equal(recorded[0].kind,'chord');
assert.equal(recorded[0].root,9);
assert.equal(recorded[0].type,'m7');
assert.equal(recorded[0].octave,0);
state.recording=false;state.arpMode='UP';
await run('pressKey(53,false,0)');
assert.equal(arpeggios.length,1);
assert.equal(arpeggios[0].chord.root,5);
assert.equal(arpeggios[0].octave,0);
state.arpMode='OFF';state.page='KEY';
await run('pressKey(53,false,0)');
assert.equal(chords.length,5,'KEY mode remains a chord player');
assert.equal(releases.length,1,'KEY mode keeps its legacy monophonic retrigger');
assert.equal(JSON.stringify(state.chord),before);
console.log('PASS: 27 chromatic roots, complete chord voicings and scheduling, visual hints, recording, ARP and KEY');
