(() => {
  'use strict';
  const $ = (s) => document.querySelector(s);
  const $$ = (s) => [...document.querySelectorAll(s)];
  const views = ['chat', 'connections', 'commands', 'files', 'studies'];
  const labels = {chat:'Conversa',connections:'Conexões',commands:'Comandos',files:'Arquivos',studies:'Estudos'};
  const attachments = [];
  let connected = false;
  let authenticationRequired = false;
  const api = {status:'/api/v1/status',chat:'/api/v1/chat'};
  function setView(view){
    if(!views.includes(view)) return;
    $$('.nav[data-view]').forEach(b=>b.classList.toggle('active',b.dataset.view===view));
    $$('.view').forEach(v=>v.classList.toggle('active',v.id===`view-${view}`));
    $('#pageLabel').textContent=labels[view];$('#sidebar').classList.remove('open');
  }
  $$('.nav[data-view]').forEach(b=>b.addEventListener('click',()=>setView(b.dataset.view)));
  $('#openMenu').onclick=()=>$('#sidebar').classList.add('open');
  $('#closeMenu').onclick=()=>$('#sidebar').classList.remove('open');
  function bubble(sender,text){
    $('#hero')?.remove();const row=document.createElement('div');row.className=`message ${sender==='Você'?'from-user':'from-agent'}`;
    const name=document.createElement('span');name.className='sender';name.textContent=sender==='Você'?'EU':'SagaZ-ZeRo';
    const content=document.createElement('div');content.className='bubble';content.textContent=text;
    row.append(name,content);$('#chatFeed').append(row);$('#chatFeed').scrollTop=$('#chatFeed').scrollHeight;
  }
  function localCommand(input){
    const cmd=input.trim().toLowerCase();
    if(cmd==='/ajuda'||cmd==='/help')return 'Comandos locais: /ajuda, /status, /modelos, /limpar. Outros comandos exigem o SagaZ Core conectado.';
    if(cmd==='/status')return connected?'Core detectado; serviços avançados dependem de autorização.':'Modo prévia. Nenhum backend de IA ou executor remoto está conectado.';
    if(cmd==='/modelos')return 'Conecte o gateway BYOK no backend. A página não solicita nem armazena chaves de API.';
    if(cmd==='/limpar'){ $('#chatFeed').replaceChildren();return 'Conversa local limpa.'; }
    return null;
  }
  async function send(){
    const input=$('#prompt').value.trim();if(!input && !attachments.length)return;
    const names=attachments.map(f=>f.name).join(', ');
    bubble('Você',input+(names?`\n📎 Anexos: ${names}`:''));$('#prompt').value='';
    const command=localCommand(input);if(command){bubble('SagaZ',command);return;}
    if(authenticationRequired && !connected){$('#authOverlay').hidden=false;$('#loginPassword').focus();bubble('SagaZ','É necessário autenticar no Core para consultar a IA.');return;}
    if(!connected){bubble('SagaZ','Interface de prévia: esta solicitação ainda não foi enviada à IA. Para processamento real, integre o SagaZ Core ao contrato /api/v1/chat. Seus anexos permanecem somente neste navegador.');return;}
    if(attachments.length){bubble('SagaZ','Anexos exigem o endpoint seguro de uploads /api/v1/files, que não está habilitado nesta prévia. Nenhum arquivo foi enviado.');return;}
    try{
      const controller=new AbortController();const timeout=setTimeout(()=>controller.abort(),30000);
      let response;
      try { response=await fetch(api.chat,{method:'POST',credentials:'same-origin',headers:{'Content-Type':'application/json','X-SagaZ-Request':'1'},body:JSON.stringify({message:input}),signal:controller.signal}); }
      finally{clearTimeout(timeout);}
      if(!response.ok)throw new Error(`HTTP ${response.status}`);
      const data=await response.json();if(typeof data.reply!=='string')throw Error('Resposta inválida do backend');bubble('SagaZ',data.reply);
    }catch(e){bubble('SagaZ',`Falha ao consultar o Core (${e.message}). Confira o contrato e os logs do servidor.`);}
  }
  $('#chatForm').addEventListener('submit',e=>{e.preventDefault();send();});
  $('#prompt').addEventListener('keydown',e=>{if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();send();}});
  $$('.quick-prompts button').forEach(b=>b.onclick=()=>{$('#prompt').value=b.dataset.prompt;$('#prompt').focus();});
  $('#slashBtn').onclick=()=>{$('#prompt').value='/ajuda';$('#prompt').focus();};
  $('#newChat').onclick=()=>{$('#chatFeed').replaceChildren();attachments.length=0;renderAttachments();setView('chat');bubble('SagaZ','Nova conversa iniciada. /ajuda mostra os comandos disponíveis.');if(connected)fetch('/api/v1/chat/reset',{method:'POST',credentials:'same-origin',headers:{'X-SagaZ-Request':'1'}}).catch(()=>{});};
  const sources=[['GitHub','Código, branches e revisão'],['Notion','Estudos e documentação'],['Provedores de IA','BYOK através do gateway'],['VPS / SSH','Operações aprovadas'],['Memória','Contexto e decisões versionadas'],['Arquivos','Análise controlada no servidor']];
  sources.forEach(([name,desc])=>{const tile=document.createElement('article');tile.className='tile';const strong=document.createElement('strong');strong.textContent=name;const p=document.createElement('p');p.textContent=desc;const small=document.createElement('small');small.textContent='Aguardando integração';tile.append(strong,p,small);$('#connectionsGrid').append(tile);});
  const textExtensions=/\.(txt|md|json|js|ts|py|sh|html|css|csv|log)$/i;
  function renderAttachments(){
    $('#attachList').replaceChildren();$('#fileShelf').replaceChildren();
    if(!attachments.length){const empty=document.createElement('span');empty.className='muted';empty.textContent='Nenhum arquivo selecionado.';$('#fileShelf').append(empty);}
    attachments.forEach((file,i)=>{
      const pill=document.createElement('span');pill.className='attach-pill';pill.append(document.createTextNode(`📎 ${file.name} `));
      const remove=document.createElement('button');remove.setAttribute('aria-label',`Remover ${file.name}`);remove.textContent='×';remove.onclick=()=>{attachments.splice(i,1);renderAttachments();};pill.append(remove);$('#attachList').append(pill);
      const btn=document.createElement('button');btn.textContent=`${file.name} · ${(file.size/1024).toFixed(1)} KB`;btn.onclick=()=>previewFile(file);$('#fileShelf').append(btn);
    });
  }
  async function previewFile(file){
    if(!textExtensions.test(file.name)){ $('#filePreview').textContent='Arquivo reconhecido, mas este tipo exige o analisador do Core. Nenhum conteúdo foi enviado.';return; }
    if(file.size>1024*1024){$('#filePreview').textContent='Arquivo maior que 1 MB: processe no backend para evitar sobrecarga do navegador.';return;}
    try{const content=await file.text();$('#filePreview').textContent=content.slice(0,10000)+(content.length>10000?'\n… [prévia limitada]':'');}catch{$('#filePreview').textContent='Não foi possível ler o arquivo.';}
  }
  $('#fileInput').onchange=e=>{for(const f of e.target.files){if(attachments.length>=12)break;attachments.push(f);}renderAttachments();e.target.value='';};
  function formatCti(data,isSummary){
    if(isSummary)return `Base CTI: ${data.count} registros\nStatus: ${JSON.stringify(data.status_counts)}\n\n${data.records.map(item=>`${item.id} · ${item.title} [${item.status}]`).join('\n')}`;
    if(!data.results.length)return `Nenhum registro para: ${data.query}`;
    return `Busca: ${data.query} · ${data.count} resultado(s)\n\n${data.results.map(item=>`${item.id} · ${item.title} [${item.status}]`).join('\n')}`;
  }
  $('#commandPreview').onclick=async()=>{
    const cmd=$('#commandInput').value.trim();if(!cmd)return;$('#commandInput').value='';
    const match=cmd.match(/^\/cti(?:\s+(.+))?$/i);$('#terminalLog').textContent+=`\n$ ${cmd}\n`;
    if(!match){$('#terminalLog').textContent+='[PREVIEW] Não executado. O Core precisa validar sessão, permissões e aprovação.';return;}
    try{
      const query=match[1]?.trim();const url=query?`/api/cti/search?q=${encodeURIComponent(query)}`:'/api/cti/summary';
      const response=await fetch(url,{cache:'no-store',credentials:'same-origin'});const data=await response.json();
      if(!response.ok)throw new Error(data.error||`HTTP ${response.status}`);
      $('#terminalLog').textContent+=formatCti(data,!query);
    }catch(error){$('#terminalLog').textContent+=`CTI indisponível: ${error.message}`;}
  };
  try{const s=JSON.parse(localStorage.getItem('sagaz.study.v1')||'null');if(s){$('#studyTitle').value=s.title||'';$('#studyBody').value=s.body||'';}}catch{}
  $('#saveStudy').onclick=()=>{const s={title:$('#studyTitle').value,body:$('#studyBody').value,updatedAt:new Date().toISOString(),scope:'local-browser'};try{localStorage.setItem('sagaz.study.v1',JSON.stringify(s));$('#studyStatus').textContent='Salvo apenas neste navegador. Exporte para compartilhar.';}catch{$('#studyStatus').textContent='O navegador bloqueou o armazenamento local.';}};
  $('#exportStudy').onclick=()=>{const data={title:$('#studyTitle').value,body:$('#studyBody').value,exportedAt:new Date().toISOString()};const a=document.createElement('a');const url=URL.createObjectURL(new Blob([JSON.stringify(data,null,2)],{type:'application/json'}));a.href=url;a.download='sagaz-estudo.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);};
  async function checkCore(){
    connected=false;
    try{
      const controller=new AbortController();const timer=setTimeout(()=>controller.abort(),2400);
      let res;try{res=await fetch(api.status,{cache:'no-store',credentials:'same-origin',signal:controller.signal});}finally{clearTimeout(timer);}
      if(!res.ok)throw new Error('Status indisponível');
      const body=await res.json();
      authenticationRequired=Boolean(body?.service==='sagaz-zero'&&body?.auth_required);
      connected=Boolean(body?.service==='sagaz-zero'&&body?.chat&&body?.authenticated);
      $('#authOverlay').hidden=!(authenticationRequired&&!body?.authenticated);
      if(connected){
        $('#connectionDot').classList.add('online');
        $('#connectionStatus').textContent='Core autenticado · chat';
        $('#coreBadge').textContent='CHAT: CONECTADO';
        $('#modelLabel').textContent=body.model||'Core';
      }else{
        $('#connectionDot').classList.remove('online');
        $('#connectionStatus').textContent=authenticationRequired?'Autenticação necessária':'Prévia · sem gateway';
        $('#coreBadge').textContent=authenticationRequired?'LOGIN NECESSÁRIO':'CORE: PRÉVIA';
      }
    }catch{
      $('#coreBadge').textContent='CORE: INDISPONÍVEL';
    }
  }
  $('#loginForm').addEventListener('submit',async e=>{
    e.preventDefault();$('#loginError').textContent='';
    const password=$('#loginPassword').value;
    try{
      const res=await fetch('/api/v1/login',{method:'POST',credentials:'same-origin',headers:{'Content-Type':'application/json','X-SagaZ-Request':'1'},body:JSON.stringify({password})});
      $('#loginPassword').value='';
      if(!res.ok){$('#loginError').textContent=res.status===429?'Tentativas excedidas. Tente mais tarde.':'Senha incorreta ou servidor indisponível.';return;}
      await checkCore();
    }catch{$('#loginError').textContent='Falha de rede. Confira o servidor.';}
  });
  checkCore();
  const cvs=$('#matrix'),ctx=cvs.getContext('2d');let rain=[],raf=0,enabled=localStorage.getItem('sagaz.fx')!=='off'&&!matchMedia('(prefers-reduced-motion: reduce)').matches;
  function resize(){if(!ctx)return;const ratio=Math.min(devicePixelRatio||1,1.4);cvs.width=Math.floor(innerWidth*ratio);cvs.height=Math.floor(innerHeight*ratio);ctx.setTransform(ratio,0,0,ratio,0,0);const n=Math.max(8,Math.floor(innerWidth/27));rain=Array.from({length:n},()=>({x:Math.random()*innerWidth,y:Math.random()*innerHeight,velocity:0.45+Math.random()*1.2,size:10+Math.random()*5}));}
  function animate(){if(!enabled||!ctx)return;ctx.clearRect(0,0,innerWidth,innerHeight);ctx.font='12px monospace';rain.forEach(r=>{ctx.fillStyle=`rgba(50,${170+Math.floor(Math.random()*65)},255,.46)`;ctx.fillText('01SZ⌘<>/'[Math.floor(Math.random()*8)],r.x,r.y);r.y+=r.velocity*2;if(r.y>innerHeight+20){r.y=-20;r.x=Math.random()*innerWidth;}});raf=requestAnimationFrame(animate);}
  $('#fxToggle').onclick=()=>{enabled=!enabled;localStorage.setItem('sagaz.fx',enabled?'on':'off');cancelAnimationFrame(raf);ctx?.clearRect(0,0,innerWidth,innerHeight);if(enabled)animate();};
  addEventListener('resize',resize);resize();if(enabled)animate();
})();
