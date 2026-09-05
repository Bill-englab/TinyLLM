/* TinyLLM 课程进度逻辑 —— 与 docs/dashboard.html 共享同一 localStorage 键 */
const KEY = 'tinyllm-course-v1';
function getS(){ try{ return JSON.parse(localStorage.getItem(KEY)||'{}'); }catch(e){ return {}; } }
function saveS(s){ localStorage.setItem(KEY, JSON.stringify(s)); }
function st(id){ return getS()[id] || {t:false, p:false}; }
function mark(id, field){
  const s = getS();
  s[id] = Object.assign({t:false, p:false}, s[id]);
  s[id][field] = !s[id][field];
  saveS(s);
  refreshMarks();
}
function refreshMarks(){
  document.querySelectorAll('[data-lesson]').forEach(box=>{
    const id = box.getAttribute('data-lesson');
    const s = st(id);
    const bt = box.querySelector('[data-f="t"]');
    const bp = box.querySelector('[data-f="p"]');
    if(bt){ bt.classList.toggle('on', s.t); bt.textContent = s.t ? '✓ 理论已完成' : '标记理论完成'; }
    if(bp){ bp.classList.toggle('on', s.p); bp.textContent = s.p ? '✓ 实践已完成' : '标记实践完成'; }
  });
}
document.addEventListener('DOMContentLoaded', refreshMarks);
