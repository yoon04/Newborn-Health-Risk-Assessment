const assert = require('node:assert/strict');
const fs = require('node:fs');
const source = fs.readFileSync('templates/form.html', 'utf8');
const fields = ['appearance','pulse','grimace','activity','respiration'];
const elements = {};
for (const minute of [10,15,20]) {
  elements['repeatRow'+minute] = {hidden:true};
  for (const field of fields) elements['apgar_'+minute+'_'+field] = {value:'',focus(){}};
}
elements.repeatObservations = {hidden:true};
elements.repeatSuggestion = {textContent:''};
elements.addRepeatObservation = {hidden:true,dataset:{}};
const document = {getElementById(id){return elements[id];}};
let apgarVals = {};
function updateTimedObservations(){updateRepeatControls();}
eval(source.slice(source.indexOf('function updateRepeatControls(){'), source.indexOf('function updateTimedObservations(){')));
// Inline handlers can resolve element IDs in the form's named-property scope.
// Exercise the actual markup handler with that scope, instead of calling a function directly.
const clickHandler = source.match(/id="addRepeatObservation"[^>]*onclick="([^"]+)"/)[1];
function clickRepeatButton(){
  const formScope={addRepeatObservation:elements.addRepeatObservation};
  with(formScope){eval(clickHandler);}
}
function setFive(scores){apgarVals=Object.fromEntries(fields.map((f,i)=>[f,scores[i]]));updateRepeatControls();}
function setRepeat(minute,scores){fields.forEach((f,i)=>elements['apgar_'+minute+'_'+f].value=String(scores[i]));updateRepeatControls();}
updateRepeatControls();
assert.equal(elements.addRepeatObservation.hidden,true);
setFive([1,2,1,1,2]); // Exactly 7 does not suggest repeat scoring.
assert.equal(elements.addRepeatObservation.hidden,true);
setFive([1,1,1,1,2]);
assert.equal(elements.addRepeatObservation.hidden,false);
assert.equal(elements.repeatRow10.hidden,true); // Staff opens each row explicitly.
clickRepeatButton();
assert.equal(elements.repeatRow10.hidden,false);
assert.equal(elements.repeatRow15.hidden,true);
assert.equal(elements.addRepeatObservation.hidden,true); // Complete 10 min first.
setRepeat(10,[1,1,1,1,2]);
assert.equal(elements.addRepeatObservation.dataset.minute,'15');
clickRepeatButton();
assert.equal(elements.repeatRow15.hidden,false);
assert.equal(elements.repeatRow20.hidden,true);
setRepeat(15,[1,2,2,2,2]); // Improved repeat ends prompts, preserving records.
assert.match(elements.repeatSuggestion.textContent,/no further repeat-scoring prompt/);
assert.equal(elements.addRepeatObservation.hidden,true);
assert.equal(elements.repeatRow10.hidden,false);
setRepeat(15,[1,1,1,1,2]);
assert.equal(elements.addRepeatObservation.dataset.minute,'20');
clickRepeatButton();
setRepeat(20,[1,1,1,1,2]);
assert.equal(elements.addRepeatObservation.hidden,true);
setFive([2,2,2,2,2]);
assert.equal(elements.repeatRow10.hidden,false);
// Restore a submitted 15-minute record after server-side validation errors.
updateRepeatControls.added = new Set();
fields.forEach(f=>elements['apgar_10_'+f].value='');
updateRepeatControls();
assert.equal(elements.repeatRow10.hidden,false);
assert.equal(elements.repeatRow15.hidden,false);
console.log('Repeat observation controls: passed');
