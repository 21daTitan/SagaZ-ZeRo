'use strict';
const $ = selector => document.querySelector(selector);
let sources = [], currentProject = null, busy = false;
const labels = {console:'Console',research:'Pesquisa',skills:'Skills',projects:'Projetos',settings:'Conexão'};
async function api(path, body) {
  const response = await fetch(path, body === undefined ? {} : {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
  const data = await response.json();
  if (!response.ok) throw Error(data.error || 'Não foi possível concluir.');
  return data;
}
function view(name) {
  if (!labels[name]) return;
  document.querySelectorAll('.view').forEach(el => { el.hidden = el.id !== name; });
  document.querySelectorAll('[data-view]').forEach(el => el.classList.toggle('active',el.dataset.view === name));
  $('#viewname').textContent = labels[name];
  if (name === 'projects') loadProjects();
}
function message(role, text, project) {
  $('#conversation .welcome')?.remove(); $('#conversation .boot')?.remove();
  const item = document.createElement('div'); item.className = 'message ' + role;
  const tag = document.createElement('div'); tag.className = 'role'; tag.textContent = role === 'user' ? 'VOCÊ' : 'SAGAZ';
  const content = document.createElement('div'); content.className = 'body'; content.textContent = text;
  item.append(tag,content);
  if (project) {
    const a = document.createElement('a'); a.className = 'tasklink'; a.href = '/api/context/' + project;
    a.textContent = 'Exportar contexto ↗'; a.target = '_blank'; a.rel = 'noopener'; item.append(a);
  }
  $('#conversation').append(item); $('#conversation').scrollTop = $('#conversation').scrollHeight;
}
function setProject(id) {
  currentProject = id; $('#niche').disabled = Boolean(id);
  $('#conversationstate').textContent = id ? 'Conversa ' + id.slice(0,8) : 'Nova conversa';
}
document.querySelectorAll('[data-view]').forEach(el => el.addEventListener('click', () => view(el.dataset.view)));
document.querySelectorAll('[data-prompt]').forEach(el => el.addEventListener('click', () => { $('#brief').value = el.dataset.prompt; $('#brief').focus(); }));
$('#newtask').addEventListener('click', () => {
  if (busy) return;
  setProject(null); $('#conversation').replaceChildren(); $('#brief').value = ''; view('console');
  $('#chatstatus').textContent = 'Nova conversa. As anteriores continuam em Projetos.'; $('#brief').focus();
});
$('#usemodel').addEventListener('change', () => {
  $('#send').textContent = $('#usemodel').checked ? 'Enviar ao modelo ↗' : 'Preparar tarefa ↗';
  $('#modehint').textContent = $('#usemodel').checked ? 'Modelo configurado' : 'Preparação local';
});
$('#chat').addEventListener('submit', async event => {
  event.preventDefault(); if (busy) return;
  const brief = $('#brief').value.trim(); if (!brief) return;
  busy = true; $('#send').disabled = true; $('#newtask').disabled = true;
  $('#chatstatus').textContent = $('#usemodel').checked ? 'Gerando resposta…' : 'Preparando contexto…';
  try {
    const data = await api('/api/chat',{brief,niche:$('#niche').value,method:$('#method').value,use_model:$('#usemodel').checked,parent_id:currentProject});
    message('user',brief); message('assistant',data.answer,data.id); setProject(data.id); $('#brief').value = '';
    $('#chatstatus').textContent = data.mode === 'configured_model' ? 'Resposta salva. Revise o conteúdo antes de publicar.' : 'Contexto e histórico salvos. Nenhum modelo foi chamado.';
  } catch (error) { $('#chatstatus').textContent = error.message; }
  finally { busy = false; $('#send').disabled = false; $('#newtask').disabled = false; }
});
function renderSources() {
  const query = $('#search').value.toLocaleLowerCase('pt-BR'), scope = $('#sourcescope').value, list = $('#sources'); list.replaceChildren();
  const rows = sources.filter(e => (scope === 'all' || e.scope === scope) && ((e.title || '')+' '+e.tags.join(' ')).toLocaleLowerCase('pt-BR').includes(query));
  if (!rows.length) list.textContent = 'Nenhuma referência neste filtro.';
  for (const entry of rows) {
    const row = document.createElement('div'); row.className = 'row'; const info = document.createElement('div');
    const title = document.createElement('strong'); title.textContent = entry.title || entry.user_label || entry.id;
    const detail = document.createElement('small'); detail.textContent = entry.tags.join(' · ') + ' / ' + entry.evidence;
    const link = document.createElement('a'); link.href = entry.url; link.target = '_blank'; link.rel = 'noopener noreferrer'; link.textContent = 'Abrir fonte ↗';
    info.append(title,detail); row.append(info,link); list.append(row);
  }
}
async function loadSources() { try { sources = (await api('/api/sources')).entries; renderSources(); } catch (e) { $('#sources').textContent = e.message; } }
$('#search').addEventListener('input',renderSources); $('#sourcescope').addEventListener('change',renderSources); $('#reloadsources').addEventListener('click',loadSources);
async function resume(id) {
  if (busy) return;
  try {
    const data = await api('/api/conversation/'+id); $('#conversation').replaceChildren();
    for (const item of data.messages) message(item.role,item.content);
    $('#niche').value = data.niche; $('#method').value = data.method; setProject(id); view('console');
    $('#chatstatus').textContent = 'Conversa restaurada. O próximo envio inclui o histórico recente.';
  } catch (e) { $('#projectlist').textContent = e.message; }
}
async function loadProjects() {
  const list = $('#projectlist'); list.textContent = 'Carregando…';
  try {
    const rows = await api('/api/projects'); list.replaceChildren();
    if (!rows.length) list.textContent = 'Seus projetos vão aparecer aqui.';
    rows.sort((a,b) => b.created_at.localeCompare(a.created_at));
    for (const p of rows) {
      const row = document.createElement('div'); row.className = 'row'; const info = document.createElement('div');
      const title = document.createElement('strong'); title.textContent = p.brief;
      const detail = document.createElement('small'); detail.textContent = p.niche + ' · ' + new Date(p.created_at).toLocaleString('pt-BR'); info.append(title,detail);
      const actions = document.createElement('div'); actions.className = 'actions';
      if (p.conversation) { const open = document.createElement('button'); open.textContent = 'Retomar'; open.addEventListener('click',()=>resume(p.id)); actions.append(open); }
      const link = document.createElement('a'); link.href = '/api/context/'+p.id; link.target = '_blank'; link.rel = 'noopener'; link.textContent = 'Contexto ↗';
      actions.append(link); row.append(info,actions); list.append(row);
    }
  } catch (e) { list.textContent = e.message; }
}
$('#reloadprojects').addEventListener('click',loadProjects);
$('#researchform').addEventListener('submit',async event => {
  event.preventDefault(); $('#collect').disabled = true; $('#researchresult').textContent = 'Coletando. Esta etapa pode levar até dois minutos…';
  try { $('#researchresult').textContent = JSON.stringify(await api('/api/research',{url:$('#videourl').value.trim()}),null,2); }
  catch(e) { $('#researchresult').textContent = e.message; } finally { $('#collect').disabled = false; }
});
async function start() {
  try {
    const status = await api('/api/status'); $('#version').textContent = 'v'+status.version;
    $('#connection').textContent = status.model_configured ? 'Endpoint configurado' : 'Modo local disponível';
    $('#usemodel').disabled = !status.model_configured;
    if ($('#bootlog')) $('#bootlog').textContent = '[core] SagaZ '+status.version+' inicializado\n[sources] '+status.sources+' referências no catálogo\n[model] '+(status.model_configured?'endpoint configurado / acesso não testado':'preparação local / nenhuma API chamada')+'\n[storage] projetos e conversas locais\n[shell] comandos do sistema desabilitados no chat';
    const config = await api('/api/connection'); $('#modelname').textContent = config.model || 'Não configurado';
    $('#keystate').textContent = config.key_present ? 'Presente no ambiente (oculta)' : 'Ausente; endpoints locais podem dispensar chave';
    $('#modelstate').textContent = config.configured ? 'Configuração detectada. Acesso ainda não testado.' : 'Modo local ativo. Configure um endpoint para gerar pelo SagaZ.';
    try {
      const [audit, cost] = await Promise.all([api('/gateway/audit/verify'), api('/gateway/cost')]);
      $('#gatewaystatus').textContent = 'AUDIT: '+(audit.valid ? 'OK' : 'ERRO')+' | registros: '+audit.records+'\nREQUESTS: '+cost.count+' | USD conhecido: '+cost.total_known_usd+' | sem preço: '+cost.unpriced_requests;
    } catch(e) { $('#gatewaystatus').textContent = 'Gateway: '+e.message; }

  } catch(e) { $('#connection').textContent = 'Servidor indisponível'; $('#chatstatus').textContent = e.message; }
  loadSources();
  try {
    const data = await api('/api/skills');
    if ($('#bootlog')) $('#bootlog').textContent += '\n[skills] '+data.count+' módulos de skills disponíveis\n[ready] /help exibe o mapa de comandos';
    for (const skill of data.entries) {
      const card = document.createElement('article'); card.className = 'card';
      const title = document.createElement('h2'); title.textContent = skill.id;
      const description = document.createElement('p'); description.textContent = skill.description;
      const state = document.createElement('small'); state.textContent = 'ARQUIVOS DISPONÍVEIS / DEPENDÊNCIAS SOB DEMANDA';
      card.append(title,description,state); $('#skilllist').append(card);
    }
  } catch(e) { $('#skilllist').textContent = e.message; }
  try {
    for (const entry of (await api('/api/integrations')).entries) {
      const p = document.createElement('p'); p.textContent = entry.role+' · '+entry.status+' — '+entry.decision; $('#integrationlist').append(p);
    }
  } catch(e) { $('#integrationlist').textContent = e.message; }
}
start();
const canvas = $('#rain'), ctx = canvas.getContext('2d');
if (ctx && !matchMedia('(prefers-reduced-motion: reduce)').matches) {
  let drops = [], last = 0;
  function size() { canvas.width = innerWidth; canvas.height = innerHeight; drops = Array(Math.ceil(innerWidth/24)).fill(0).map(()=>Math.random()*-80); }
  size(); addEventListener('resize',size);
  function frame(time) {
    if(time-last>110 && !document.hidden) {
      ctx.fillStyle='rgba(3,7,17,.13)'; ctx.fillRect(0,0,canvas.width,canvas.height); ctx.fillStyle='#00d9ff'; ctx.font='12px monospace';
      drops.forEach((y,i)=>{ctx.fillText(Math.random()>.5?'1':'0',i*24,y*20);drops[i]=y*20>canvas.height&&Math.random()>.98?0:y+.4;}); last=time;
    }
    requestAnimationFrame(frame);
  }
  requestAnimationFrame(frame);
}

$('#commandbar').addEventListener('submit', event => {
  event.preventDefault(); if (busy) return;
  const text = $('#command').value.trim(); if (!text) return;
  const commands = {'/skills':'skills','/projects':'projects','/research':'research','/connect':'settings','/console':'console'};
  if (text === '/help' || text === '/modules') {
    message('assistant', '/help · mapa de comandos\n/skills · catálogo de skills\n/cti <termo> · consulta CTI offline\n/research · referências e YouTube\n/projects · conversas e contextos\n/connect · configuração do modelo\n/new · nova conversa\n/clear · limpar somente a tela\n/status · estado do servidor\n\nUm texto sem / prepara um briefing. Comandos shell não são executados.');
  } else if (commands[text]) view(commands[text]);
  else if (text === '/new') $('#newtask').click();
  else if (text === '/clear') { $('#conversation').replaceChildren(); $('#chatstatus').textContent = 'Tela limpa. Histórico e conversa ativa preservados.'; }
  else if (text.startsWith('/cti ')) {
    const q = text.slice(5).trim();
    api('/api/cti/search?q='+encodeURIComponent(q)).then(d=>message('assistant',JSON.stringify(d,null,2))).catch(e=>message('assistant',e.message));
  }
  else if (text === '/cti') api('/api/cti/summary').then(d=>message('assistant',JSON.stringify(d,null,2))).catch(e=>message('assistant',e.message));
  else if (text === '/status') api('/api/status').then(d=>message('assistant',JSON.stringify(d,null,2))).catch(e=>message('assistant',e.message));
  else if (text.startsWith('/')) message('assistant','Comando desconhecido. Use /help.');
  else { $('#brief').value = text; $('#chat').requestSubmit(); }
  $('#command').value = '';
});
