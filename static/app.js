const clock=document.getElementById('clock');
function tick(){clock.textContent=new Date().toLocaleString();}
tick();setInterval(tick,1000);

function escapeHtml(s){return String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));}
function renderEvents(events){
  document.getElementById('eventRows').innerHTML=events.map(e=>`<tr>
  <td>${escapeHtml(e.time)}</td><td class="plate">${escapeHtml(e.plate)}</td>
  <td>${escapeHtml(e.vehicle)}</td><td>${escapeHtml(e.camera)}</td>
  <td><span class="pill ${e.status.toLowerCase()}">${escapeHtml(e.status)}</span></td></tr>`).join('');
  document.getElementById('eventCount').textContent=events.length;
}
async function refresh(){
  const r=await fetch('/api/state');const d=await r.json();renderEvents(d.events);
  document.querySelectorAll('.toggle').forEach(b=>{
    const z=d.zones.find(x=>x.id===Number(b.dataset.id));if(!z)return;
    b.textContent=z.enabled?'ENABLED':'DISABLED';b.classList.toggle('enabled',z.enabled);
  });
  document.getElementById('zoneCount').textContent=d.zones.filter(z=>z.enabled).length;
}
document.getElementById('eventForm').addEventListener('submit',async e=>{
  e.preventDefault();const data=Object.fromEntries(new FormData(e.target).entries());
  await fetch('/api/events',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)});
  e.target.reset();await refresh();
});
document.querySelectorAll('.toggle').forEach(b=>b.addEventListener('click',async()=>{
  await fetch(`/api/zones/${b.dataset.id}/toggle`,{method:'POST'});await refresh();
}));
setInterval(refresh,5000);
