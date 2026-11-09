#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SagaZ-ZeRo — Interface Web
=========================

Servidor FastAPI que expõe o SagaZ-ZeRo multi-provedor via navegador.

Endpoints:
  GET  /                 — interface
  GET  /api/status       — estado (shell, provedor ativo, criptografia)
  GET  /api/providers    — catálogo de provedores e modelos
  POST /api/credentials  — define a chave de API em tempo de execução
  POST /api/clear        — limpa o histórico local
  POST /api/chat         — streaming da resposta

A chave de API pode ser definida no .env OU colada na interface. Quando
colada, fica apenas em memória do processo — nunca é gravada em disco.
"""

import asyncio
import getpass
import os
import platform
import re
import sys

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel

from agent import (
    Agent,
    build_system_prompt,
    execute_shell_blocks,
    extract_shell_blocks,
    install_shutdown_handlers,
    kill_active_procs,
)

try:
    from cassandra.client import (
        AllProvidersExhausted,
        ProviderError,
        load_credentials,
    )
    from cassandra.filter import Credential, ProviderBlocked
    from cassandra.providers import provider_catalog, resolve_provider
    from cassandra.compact import compact, needs_compaction
    from cassandra.toolfetch import (
        extract_tool_blocks,
        fetch as tool_fetch,
    )
    CORE_OK = True
except ImportError as _exc:  # pragma: no cover
    CORE_OK = False
    _CORE_ERR = str(_exc)


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

ALLOW_SHELL = os.getenv("CASSANDRA_ALLOW_SHELL", "1").lower() in ("1", "true", "yes", "on")

# Valor de CASSANDRA_PROVIDER vindo do .env, guardado antes de qualquer
# override da interface. Sem isto, escolher um provedor no seletor e depois
# voltar para "— provedor —" (auto) deixava o valor antigo preso no
# ambiente, e o auto-detect nunca voltava a valer.
_ENV_PROVIDER_DEFAULT = os.getenv("CASSANDRA_PROVIDER", "").strip()

# Credencial definida em runtime pela interface (só em memória).
RUNTIME_CREDENTIALS = []


def _active_credentials():
    """Credenciais efetivas: as da interface têm prioridade sobre o .env."""
    if RUNTIME_CREDENTIALS:
        return list(RUNTIME_CREDENTIALS)
    return load_credentials() if CORE_OK else []


HTML_CONTENT = r"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>SagaZ-ZeRo · HooLeeSh33t EdiTioN</title>
<style>
  :root {
    --cyan: #00f5ff;
    --cyan-dim: #00b8cc;
    --cyan-glow: rgba(0,245,255,0.18);
    --cyan-border: rgba(0,245,255,0.35);
    --bg: #000d0f;
    --bg2: #001215;
    --bg3: #001a1f;
    --text: #c8f7ff;
    --text-dim: #5fa8b8;
    --green: #00ff41;
    --red: #ff2d55;
    --yellow: #ffd60a;
    --panel-bg: rgba(0,18,22,0.92);
    --radius: 8px;
    --font-mono: 'Courier New', Courier, monospace;
  }
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  html, body { height: 100%; overflow: hidden; background: var(--bg); color: var(--text); font-family: var(--font-mono); }

  /* ── MATRIX CANVAS ── */
  #matrix-canvas {
    position: fixed; top: 0; left: 0; width: 100%; height: 100%;
    z-index: 0; pointer-events: none; opacity: 0.22;
  }

  /* ── LAYOUT ── */
  #app {
    position: relative; z-index: 1;
    display: grid;
    grid-template-rows: auto 1fr auto;
    height: 100vh;
    max-width: 980px;
    margin: 0 auto;
    padding: 0 12px;
  }

  /* ── HEADER ── */
  header {
    display: flex; align-items: center; justify-content: space-between;
    padding: 10px 0 8px;
    border-bottom: 1px solid var(--cyan-border);
  }
  .logo {
    display: flex; align-items: center; gap: 10px;
  }
  .logo-glyph {
    font-size: 22px; color: var(--cyan);
    text-shadow: 0 0 12px var(--cyan), 0 0 30px var(--cyan-dim);
    animation: pulse-glyph 2.5s ease-in-out infinite;
  }
  @keyframes pulse-glyph {
    0%,100%{text-shadow:0 0 10px var(--cyan),0 0 25px var(--cyan-dim);}
    50%{text-shadow:0 0 22px var(--cyan),0 0 50px var(--cyan-dim),0 0 80px rgba(0,245,255,0.3);}
  }
  .logo-text {
    display: flex; flex-direction: column; line-height: 1.1;
  }
  .logo-name {
    font-size: 15px; font-weight: bold; color: #fff;
    text-shadow: 0 0 8px var(--cyan);
    letter-spacing: 1px;
  }
  .logo-sub {
    font-size: 10px; color: var(--cyan-dim); letter-spacing: 2px;
    text-transform: uppercase;
  }
  .header-right {
    display: flex; align-items: center; gap: 8px;
  }
  .status-dot {
    width: 8px; height: 8px; border-radius: 50%;
    background: var(--green);
    box-shadow: 0 0 8px var(--green);
    animation: blink 2s ease-in-out infinite;
  }
  .status-dot.offline { background: var(--red); box-shadow: 0 0 8px var(--red); animation: none; }
  @keyframes blink { 0%,100%{opacity:1;} 50%{opacity:0.4;} }
  .status-label { font-size: 11px; color: var(--text-dim); }
  #btn-settings {
    background: none; border: 1px solid var(--cyan-border);
    color: var(--cyan); font-size: 14px; cursor: pointer;
    padding: 4px 10px; border-radius: var(--radius);
    transition: all .2s;
  }
  #btn-settings:hover { background: var(--cyan-glow); box-shadow: 0 0 10px var(--cyan-border); }

  /* ── PROVIDER BAR ── */
  #provider-bar {
    display: flex; flex-direction: column; gap: 6px;
    padding: 7px 0 5px;
    border-bottom: 1px solid rgba(0,245,255,0.1);
  }
  .bar-row { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
  .bar-label { font-size: 11px; color: var(--text-dim); white-space: nowrap; }
  select, input[type=text], input[type=password] {
    background: var(--bg2); border: 1px solid var(--cyan-border);
    color: var(--text); font-family: var(--font-mono); font-size: 12px;
    padding: 5px 8px; border-radius: var(--radius);
    outline: none; transition: border-color .2s, box-shadow .2s;
    height: 30px; line-height: 18px;
  }
  select:focus, input:focus {
    border-color: var(--cyan);
    box-shadow: 0 0 8px var(--cyan-glow);
  }
  #provider-select { min-width: 130px; max-width: 170px; }
  #model-select { min-width: 150px; flex: 1; max-width: 260px; }
  .force-input {
    border-style: dashed; border-color: var(--yellow); color: var(--yellow);
    min-width: 150px; flex: 1; max-width: 220px; font-size: 11px;
  }
  .force-input::placeholder { color: rgba(255,214,10,0.55); }
  .bar-sep { width: 1px; height: 20px; background: var(--cyan-border); }
  /* ── PILLS DE STATUS (provider ativo, shell, cifrado/sanitizado/anti-recusa) ── */
  .pill {
    font-size: 10px; padding: 3px 9px; border-radius: 12px;
    border: 1px solid var(--cyan-border); color: var(--text-dim);
    white-space: nowrap; background: var(--bg2);
  }
  .pill.on   { color: var(--green);  border-color: var(--green); }
  .pill.off  { color: var(--red);    border-color: var(--red); }
  .pill.warn { color: var(--yellow); border-color: var(--yellow); }

  /* ── CHAT AREA ── */
  #chat-area {
    overflow-y: auto; overflow-x: hidden;
    padding: 14px 0 10px;
    display: flex; flex-direction: column; gap: 12px;
    scroll-behavior: smooth;
  }
  #chat-area::-webkit-scrollbar { width: 4px; }
  #chat-area::-webkit-scrollbar-thumb { background: var(--cyan-border); border-radius: 2px; }

  /* ── MESSAGES ── */
  .msg { display: flex; gap: 10px; max-width: 100%; animation: fadeIn .25s ease; }
  @keyframes fadeIn { from{opacity:0;transform:translateY(6px);} to{opacity:1;transform:none;} }
  .msg-avatar {
    flex-shrink: 0; width: 32px; height: 32px;
    border-radius: 50%; border: 1px solid var(--cyan-border);
    display: flex; align-items: center; justify-content: center;
    font-size: 14px; background: var(--bg2);
    box-shadow: 0 0 8px var(--cyan-glow);
  }
  .msg.user { flex-direction: row-reverse; }
  .msg.user .msg-avatar { border-color: rgba(0,255,65,0.3); box-shadow: 0 0 8px rgba(0,255,65,0.1); }
  .msg-bubble {
    max-width: calc(100% - 48px);
    padding: 10px 14px;
    border-radius: var(--radius);
    font-size: 13px; line-height: 1.65;
    white-space: pre-wrap; word-break: break-word;
  }
  .msg.assistant .msg-bubble {
    background: var(--panel-bg);
    border: 1px solid var(--cyan-border);
    box-shadow: 0 0 16px rgba(0,245,255,0.07);
    color: var(--text);
  }
  .msg.user .msg-bubble {
    background: rgba(0,245,255,0.07);
    border: 1px solid rgba(0,245,255,0.2);
    color: #e0f8ff;
    text-align: right;
  }
  .msg-bubble code {
    background: rgba(0,0,0,0.5); padding: 1px 5px;
    border-radius: 4px; font-size: 12px; color: var(--cyan);
  }
  .msg-bubble pre {
    background: rgba(0,0,0,0.6); border: 1px solid var(--cyan-border);
    border-radius: 6px; padding: 10px 12px; overflow-x: auto;
    margin: 8px 0; font-size: 12px; color: var(--green);
  }
  /* Streaming cursor */
  .cursor-blink::after {
    content: '▋'; color: var(--cyan);
    animation: cursor-blink .7s step-end infinite;
  }
  @keyframes cursor-blink { 0%,100%{opacity:1;} 50%{opacity:0;} }

  /* ── SYSTEM MESSAGES ── */
  .msg-system {
    text-align: center; font-size: 11px; color: var(--text-dim);
    padding: 4px; letter-spacing: 1px;
  }

  /* ── INPUT AREA ── */
  #input-area {
    padding: 8px 0 12px;
    border-top: 1px solid var(--cyan-border);
    display: flex; flex-direction: column; gap: 6px;
  }
  #input-row {
    display: flex; gap: 8px; align-items: flex-end;
  }
  #user-input {
    flex: 1; resize: none; min-height: 44px; max-height: 160px;
    background: var(--bg2); border: 1px solid var(--cyan-border);
    color: var(--text); font-family: var(--font-mono); font-size: 13px;
    padding: 10px 12px; border-radius: var(--radius);
    outline: none; transition: border-color .2s, box-shadow .2s;
    overflow-y: auto; line-height: 1.5;
  }
  #user-input:focus {
    border-color: var(--cyan);
    box-shadow: 0 0 12px var(--cyan-glow);
  }
  #user-input::placeholder { color: var(--text-dim); }
  #btn-send {
    flex-shrink: 0; height: 44px; padding: 0 18px;
    background: linear-gradient(135deg, #003a40, #005a65);
    border: 1px solid var(--cyan);
    color: var(--cyan); font-family: var(--font-mono); font-size: 14px;
    cursor: pointer; border-radius: var(--radius);
    box-shadow: 0 0 12px var(--cyan-glow);
    transition: all .2s;
    display: flex; align-items: center; gap: 6px;
  }
  #btn-send:hover { background: linear-gradient(135deg, #004a52, #007080); box-shadow: 0 0 20px var(--cyan-border); }
  #btn-send:disabled { opacity: 0.4; cursor: not-allowed; }
  #input-hint { font-size: 10px; color: var(--text-dim); padding-left: 2px; }

  /* ── SETTINGS MODAL ── */
  #settings-modal {
    display: none; position: fixed; inset: 0; z-index: 100;
    background: rgba(0,0,0,0.75); backdrop-filter: blur(4px);
    align-items: center; justify-content: center;
  }
  #settings-modal.open { display: flex; }
  .modal-box {
    background: var(--bg3); border: 1px solid var(--cyan-border);
    border-radius: 10px; padding: 24px; width: 90%; max-width: 460px;
    box-shadow: 0 0 40px rgba(0,245,255,0.15);
    animation: fadeIn .2s ease;
  }
  .modal-title {
    font-size: 15px; color: var(--cyan); font-weight: bold;
    margin-bottom: 16px; letter-spacing: 1px;
    text-shadow: 0 0 10px var(--cyan-dim);
  }
  .modal-row { margin-bottom: 14px; }
  .modal-row label { display: block; font-size: 11px; color: var(--text-dim); margin-bottom: 5px; letter-spacing: 1px; }
  .modal-row input, .modal-row select { width: 100%; }
  .modal-actions { display: flex; gap: 8px; justify-content: flex-end; margin-top: 18px; }
  .btn-secondary {
    background: none; border: 1px solid var(--cyan-border);
    color: var(--text-dim); font-family: var(--font-mono); font-size: 12px;
    padding: 7px 16px; border-radius: var(--radius); cursor: pointer;
    transition: all .2s;
  }
  .btn-secondary:hover { border-color: var(--cyan); color: var(--cyan); }
  .btn-primary {
    background: linear-gradient(135deg, #003a40, #005a65);
    border: 1px solid var(--cyan);
    color: var(--cyan); font-family: var(--font-mono); font-size: 12px;
    padding: 7px 20px; border-radius: var(--radius); cursor: pointer;
    box-shadow: 0 0 10px var(--cyan-glow);
    transition: all .2s;
  }
  .btn-primary:hover { box-shadow: 0 0 18px var(--cyan-border); }
  .cred-status {
    font-size: 11px; margin-top: 6px; min-height: 16px;
  }
  .cred-status.ok { color: var(--green); }
  .cred-status.err { color: var(--red); }

  /* ── SHELL TOGGLE ── */
  .toggle-row { display: flex; align-items: center; gap: 8px; }
  .toggle {
    position: relative; width: 36px; height: 20px;
    display: inline-block;
  }
  .toggle input { opacity: 0; width: 0; height: 0; }
  .toggle-slider {
    position: absolute; inset: 0; background: #002a30;
    border: 1px solid var(--cyan-border); border-radius: 20px;
    cursor: pointer; transition: .3s;
  }
  .toggle-slider::before {
    content: ''; position: absolute; height: 14px; width: 14px;
    left: 2px; top: 2px; background: var(--text-dim);
    border-radius: 50%; transition: .3s;
  }
  .toggle input:checked + .toggle-slider { background: #004a52; border-color: var(--cyan); }
  .toggle input:checked + .toggle-slider::before { transform: translateX(16px); background: var(--cyan); }

  /* ── SCAN LINE EFFECT ── */
  #app::before {
    content: ''; position: fixed; inset: 0; z-index: 2;
    pointer-events: none;
    background: repeating-linear-gradient(
      0deg, transparent, transparent 2px,
      rgba(0,0,0,0.04) 2px, rgba(0,0,0,0.04) 4px
    );
  }

  /* ── RESPONSIVE ── */
  @media(max-width:600px) {
    #model-select, .force-input { max-width: 100%; width: 100%; }
    .bar-sep { display: none; }
    .modal-box { padding: 16px; }
  }
</style>
</head>
<body>
<canvas id="matrix-canvas"></canvas>

<div id="app">
  <!-- HEADER -->
  <header>
    <div class="logo">
      <span class="logo-glyph">⬡</span>
      <div class="logo-text">
        <span class="logo-name">SagaZ-ZeRo</span>
        <span class="logo-sub">HooLeeSh33t EdiTioN · by dSanT</span>
      </div>
    </div>
    <div class="header-right">
      <span class="status-dot" id="status-dot"></span>
      <span class="status-label" id="status-label">conectando...</span>
      <button id="btn-settings" title="Configurar API">⚙</button>
    </div>
  </header>

  <!-- PROVIDER BAR -->
  <div id="provider-bar">
    <div class="bar-row">
      <span class="bar-label">PROVIDER</span>
      <select id="provider-select"><option value="">carregando...</option></select>
      <span class="bar-label">MODELO</span>
      <select id="model-select"><option value="">—</option></select>
      <input type="text" id="model-override-input" class="force-input"
             placeholder="forçar modelo (opcional)"
             title="Preenchido aqui, este valor passa por cima do modelo selecionado acima — use pra forçar um modelo fora do catálogo.">
    </div>
    <div class="bar-row">
      <span class="pill" id="pill-provider">— nenhuma credencial —</span>
      <label class="toggle" title="Executar comandos de shell retornados pela API">
        <input type="checkbox" id="shell-toggle">
        <span class="toggle-slider"></span>
      </label>
      <span class="pill off" id="pill-shell">SHELL OFF</span>
      <span class="pill" id="pill-encrypt">cifrado: —</span>
      <span class="pill" id="pill-sanitize">sanitizado: —</span>
      <span class="pill" id="pill-guard">anti-recusa: —</span>
    </div>
  </div>

  <!-- CHAT AREA -->
  <div id="chat-area">
    <div class="msg-system">▸ SagaZ-ZeRo HooLeeSh33t EdiTioN inicializado · Base: Evil Cassandra por Mörlsara</div>
    <div class="msg-system">▸ Adicione sua chave API em ⚙ CONFIGURAR API para começar</div>
  </div>

  <!-- INPUT AREA -->
  <div id="input-area">
    <div id="input-row">
      <textarea id="user-input" placeholder="Digite sua mensagem... (Enter para enviar, Shift+Enter para quebrar linha)" rows="2"></textarea>
      <button id="btn-send">▶ ENVIAR</button>
    </div>
    <div id="input-hint">© 2024 dSanT · HooLeeSh33t EdiTioN · Base: Evil Cassandra — Mörlsara Code Nexus</div>
  </div>
</div>

<!-- SETTINGS MODAL -->
<div id="settings-modal">
  <div class="modal-box">
    <div class="modal-title">⚙ CONFIGURAR API — SagaZ-ZeRo</div>
    <p style="font-size:11px;color:var(--text-dim);margin-bottom:14px;line-height:1.5;">
      Cole sua chave BYOK. O provider é auto-detectado pelo formato da chave,
      mas pode ser forçado manualmente aqui — assim como a Base URL e o
      Modelo, pra quando precisar apontar pra um endpoint ou modelo fora
      do catálogo padrão.
    </p>

    <div class="modal-row">
      <label>CHAVE API (BYOK)</label>
      <input type="password" id="api-key-input" placeholder="sk-... ou equivalente">
    </div>
    <div class="modal-row">
      <label>PROVIDER (auto-detect, ou force aqui)</label>
      <select id="cred-provider-select"><option value="">— auto-detectar pela chave —</option></select>
    </div>
    <div class="modal-row">
      <label>BASE URL (opcional — força endpoint custom)</label>
      <input type="text" id="base-url-input" placeholder="https://api.openai.com/v1">
    </div>
    <div class="modal-row">
      <label>MODELO (opcional — força modelo específico)</label>
      <input type="text" id="cred-model-input" placeholder="ex: gpt-4o, deepseek-chat...">
    </div>
    <div class="cred-status" id="cred-status"></div>

    <div class="modal-actions">
      <button class="btn-secondary" id="btn-clear-chat">🗑 LIMPAR SESSÃO</button>
      <button class="btn-secondary" id="btn-close-modal">Fechar</button>
      <button class="btn-primary" id="btn-save-creds">💾 SALVAR / FORÇAR API</button>
    </div>
  </div>
</div>

<script>
// ═══════════════════════════════════════════════════════════
//  MATRIX RAIN
// ═══════════════════════════════════════════════════════════
(function(){
  const canvas = document.getElementById('matrix-canvas');
  const ctx = canvas.getContext('2d');
  const chars = '01アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホSAGAZZERO⬡◆◇▲△'.split('');
  let cols, drops;
  const FONT_SIZE = 14;

  function resize() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    cols = Math.floor(canvas.width / FONT_SIZE);
    drops = Array(cols).fill(1).map(() => Math.random() * -50);
  }
  resize();
  window.addEventListener('resize', resize);

  function draw() {
    ctx.fillStyle = 'rgba(0,13,15,0.055)';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    for (let i = 0; i < cols; i++) {
      const char = chars[Math.floor(Math.random() * chars.length)];
      const y = drops[i] * FONT_SIZE;
      // Head glow (bright)
      ctx.font = `bold ${FONT_SIZE}px 'Courier New'`;
      ctx.fillStyle = '#c8ffff';
      ctx.shadowColor = '#00f5ff';
      ctx.shadowBlur = 8;
      ctx.fillText(char, i * FONT_SIZE, y);
      // Trail
      const trailChar = chars[Math.floor(Math.random() * chars.length)];
      ctx.font = `${FONT_SIZE}px 'Courier New'`;
      ctx.fillStyle = '#00b8cc';
      ctx.shadowColor = '#007a8a';
      ctx.shadowBlur = 4;
      ctx.fillText(trailChar, i * FONT_SIZE, y - FONT_SIZE);

      ctx.shadowBlur = 0;
      if (y > canvas.height && Math.random() > 0.975) drops[i] = 0;
      drops[i] += 0.5 + Math.random() * 0.4;
    }
  }
  setInterval(draw, 45);
})();

// ═══════════════════════════════════════════════════════════
//  STATE
// ═══════════════════════════════════════════════════════════
const state = {
  provider: '',
  model: '',
  streaming: false,
  shellEnabled: false,
};

// ═══════════════════════════════════════════════════════════
//  ELEMENTS
// ═══════════════════════════════════════════════════════════
const chatArea       = document.getElementById('chat-area');
const userInput      = document.getElementById('user-input');
const btnSend        = document.getElementById('btn-send');
const providerSel    = document.getElementById('provider-select');
const modelSel       = document.getElementById('model-select');
const modelOverride  = document.getElementById('model-override-input');
const shellToggle    = document.getElementById('shell-toggle');
const pillProvider   = document.getElementById('pill-provider');
const pillShell      = document.getElementById('pill-shell');
const pillEncrypt    = document.getElementById('pill-encrypt');
const pillSanitize   = document.getElementById('pill-sanitize');
const pillGuard      = document.getElementById('pill-guard');
const statusDot      = document.getElementById('status-dot');
const statusLabel    = document.getElementById('status-label');
const btnSettings    = document.getElementById('btn-settings');
const settingsModal  = document.getElementById('settings-modal');
const apiKeyInput    = document.getElementById('api-key-input');
const baseUrlInput   = document.getElementById('base-url-input');
const credModelInput = document.getElementById('cred-model-input');
const credProvSel    = document.getElementById('cred-provider-select');
const credStatus     = document.getElementById('cred-status');
const btnSaveCreds   = document.getElementById('btn-save-creds');
const btnCloseModal  = document.getElementById('btn-close-modal');
const btnClearChat   = document.getElementById('btn-clear-chat');

// ═══════════════════════════════════════════════════════════
//  UTILS
// ═══════════════════════════════════════════════════════════
function escHtml(s) {
  return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

function mdToHtml(text) {
  // Code blocks
  text = text.replace(/```(\w*)\n?([\s\S]*?)```/g, (_,lang,code) =>
    `<pre><code class="lang-${lang}">${escHtml(code.trim())}</code></pre>`
  );
  // Inline code
  text = text.replace(/`([^`]+)`/g, '<code>$1</code>');
  // Bold
  text = text.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
  // Italic
  text = text.replace(/\*([^*]+)\*/g, '<em>$1</em>');
  // Links
  text = text.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" style="color:var(--cyan)">$1</a>');
  // Newlines
  text = text.replace(/\n/g, '<br>');
  return text;
}

function setStatus(online) {
  statusDot.className = 'status-dot' + (online ? '' : ' offline');
  statusLabel.textContent = online ? 'online' : 'offline';
}

function appendMessage(role, content, streaming=false) {
  const wrap = document.createElement('div');
  wrap.className = `msg ${role}`;
  const avatar = document.createElement('div');
  avatar.className = 'msg-avatar';
  avatar.textContent = role === 'user' ? '👤' : '⬡';
  const bubble = document.createElement('div');
  bubble.className = 'msg-bubble' + (streaming ? ' cursor-blink' : '');
  bubble.innerHTML = role === 'user' ? escHtml(content) : mdToHtml(content);
  wrap.appendChild(avatar);
  wrap.appendChild(bubble);
  chatArea.appendChild(wrap);
  chatArea.scrollTop = chatArea.scrollHeight;
  return bubble;
}

function appendSystem(text) {
  const d = document.createElement('div');
  d.className = 'msg-system';
  d.textContent = '▸ ' + text;
  chatArea.appendChild(d);
  chatArea.scrollTop = chatArea.scrollHeight;
}

// ═══════════════════════════════════════════════════════════
//  PROVIDERS & MODELS
//  provider_catalog() (cassandra/providers.py) devolve uma LISTA DE
//  OBJETOS — {key, label, base_url, default_model, models, env_var,
//  notes, detectable, context_window} — não strings. Era isso que
//  virava "[object Object]" na versão anterior desta interface.
// ═══════════════════════════════════════════════════════════
let providerCatalog = {};  // key -> objeto do catálogo

async function loadProviders() {
  try {
    const r = await fetch('/api/providers');
    if (!r.ok) throw new Error(r.status);
    const data = await r.json();
    const providers = data.providers || [];
    providerCatalog = {};
    providerSel.innerHTML = '';
    credProvSel.innerHTML = '<option value="">— auto-detectar pela chave —</option>';
    providers.forEach(p => {
      providerCatalog[p.key] = p;
      providerSel.add(new Option(p.label, p.key));
      credProvSel.add(new Option(p.label, p.key));
    });
    if (providers.length) {
      state.provider = providers[0].key;
      providerSel.value = state.provider;
      loadModelsFromCatalog(state.provider);
    }
    setStatus(true);
  } catch(e) {
    setStatus(false);
    appendSystem('Erro ao carregar provedores: ' + e.message);
  }
}

// Popula o seletor de modelo a partir do catálogo LOCAL — sempre
// disponível, mesmo sem credencial ativa ainda, porque é isso que o
// provedor realmente oferece (cassandra/providers.py). Se já existir
// credencial configurada, refreshModelsFromAPI() enriquece depois
// com a lista de verdade da conta.
function loadModelsFromCatalog(providerKey) {
  const p = providerCatalog[providerKey];
  modelSel.innerHTML = '';
  if (!p || !p.models || !p.models.length) {
    modelSel.add(new Option('— sem catálogo, use "forçar modelo" —', ''));
    state.model = '';
    return;
  }
  p.models.forEach(m => modelSel.add(new Option(m, m)));
  state.model = p.default_model || p.models[0];
  modelSel.value = state.model;
}

// Consulta os modelos REALMENTE disponíveis pra credencial ativa
// (GET /v1/models do provedor, via /api/models). Só funciona depois
// de salvar uma chave em ⚙ CONFIGURAR API — antes disso não há
// credencial pra consultar, e o catálogo local acima já cobre o uso.
async function refreshModelsFromAPI() {
  try {
    const r = await fetch('/api/models');
    const data = await r.json();
    if (!data.models || !data.models.length) return;
    const current = modelSel.value;
    modelSel.innerHTML = '';
    data.models.forEach(m => {
      const label = m.context_window ? `${m.id}  (${Math.round(m.context_window/1000)}k)` : m.id;
      modelSel.add(new Option(label, m.id));
    });
    const stillThere = data.models.some(m => m.id === current);
    state.model = stillThere ? current : data.models[0].id;
    modelSel.value = state.model;
  } catch {
    // Sem credencial ativa ou provedor sem /v1/models — mantém o catálogo local.
  }
}

providerSel.addEventListener('change', () => {
  state.provider = providerSel.value;
  loadModelsFromCatalog(state.provider);
});
modelSel.addEventListener('change', () => { state.model = modelSel.value; });

// ═══════════════════════════════════════════════════════════
//  SHELL TOGGLE
//  O servidor devolve {"allow_shell": bool} em /api/shell/toggle e
//  /api/status. A versão anterior lia "shell_enabled" (campo que não
//  existe), por isso o badge nunca refletia o estado real.
// ═══════════════════════════════════════════════════════════
function paintShellPill(on) {
  state.shellEnabled = on;
  shellToggle.checked = on;
  pillShell.textContent = on ? 'SHELL ATIVO ⚠️' : 'SHELL OFF';
  pillShell.className = 'pill ' + (on ? 'warn' : 'off');
}

shellToggle.addEventListener('change', async () => {
  try {
    const r = await fetch('/api/shell/toggle', {method: 'POST'});
    const data = await r.json();
    paintShellPill(!!data.allow_shell);
    appendSystem(`Shell ${state.shellEnabled ? 'ATIVADO ⚠️ (comandos retornados pela API passam a executar)' : 'desativado'}`);
  } catch(e) {
    shellToggle.checked = state.shellEnabled;
  }
});

// ═══════════════════════════════════════════════════════════
//  STATUS POLL
//  /api/status devolve: allow_shell, provider, provider_label,
//  credentials (contagem), encrypt, sanitize, guard, refusal_retries.
//  A versão anterior só lia (errado) "shell_enabled" e ignorava o
//  resto — por isso os badges de provider/cifrado/sanitizado/
//  anti-recusa do Cassandra original tinham desaparecido aqui.
// ═══════════════════════════════════════════════════════════
async function checkStatus() {
  try {
    const r = await fetch('/api/status');
    const data = await r.json();
    setStatus(true);

    paintShellPill(!!data.allow_shell);

    pillProvider.textContent = data.credentials > 0
      ? `${data.provider_label || data.provider || '?'} (${data.credentials})`
      : '— nenhuma credencial, ⚙ pra configurar —';
    pillProvider.className = 'pill ' + (data.credentials > 0 ? 'on' : '');

    pillEncrypt.textContent  = 'cifrado: '     + (data.encrypt  ? 'sim' : 'não');
    pillEncrypt.className    = 'pill ' + (data.encrypt  ? 'on' : '');
    pillSanitize.textContent = 'sanitizado: '  + (data.sanitize ? 'sim' : 'não');
    pillSanitize.className   = 'pill ' + (data.sanitize ? 'on' : '');
    pillGuard.textContent    = 'anti-recusa: ' + (data.guard    ? 'sim' : 'não');
    pillGuard.className      = 'pill ' + (data.guard    ? 'on' : '');
  } catch { setStatus(false); }
}
setInterval(checkStatus, 8000);

// ═══════════════════════════════════════════════════════════
//  CREDENTIALS
// ═══════════════════════════════════════════════════════════
btnSettings.addEventListener('click', () => settingsModal.classList.add('open'));
btnCloseModal.addEventListener('click', () => settingsModal.classList.remove('open'));
settingsModal.addEventListener('click', e => {
  if (e.target === settingsModal) settingsModal.classList.remove('open');
});

btnSaveCreds.addEventListener('click', async () => {
  const key   = apiKeyInput.value.trim();
  const base  = baseUrlInput.value.trim();
  const prov  = credProvSel.value;
  const model = credModelInput.value.trim();
  if (!key) { credStatus.textContent = 'Informe a chave API.'; credStatus.className='cred-status err'; return; }
  credStatus.textContent = 'Salvando...'; credStatus.className='cred-status';
  try {
    const r = await fetch('/api/credentials', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      // base_url/model SEMPRE string (nunca null) — o backend espera
      // str, e mandar null quebrava a validação silenciosamente.
      body: JSON.stringify({provider: prov, api_key: key, base_url: base, model: model})
    });
    const data = await r.json();
    if (data.success) {
      credStatus.textContent = '✓ ' + (data.message || 'Credenciais salvas!'); credStatus.className='cred-status ok';
      apiKeyInput.value = '';
      appendSystem(data.message || 'Credenciais configuradas.');
      if (data.provider) {
        state.provider = data.provider;
        providerSel.value = data.provider;
        loadModelsFromCatalog(data.provider);
      }
      if (model) {
        state.model = model;
        modelOverride.value = model;
      }
      await refreshModelsFromAPI();
      await checkStatus();
      setTimeout(() => settingsModal.classList.remove('open'), 1200);
    } else {
      credStatus.textContent = data.message || 'Erro desconhecido.'; credStatus.className='cred-status err';
    }
  } catch(e) {
    credStatus.textContent = 'Erro de rede: ' + e.message; credStatus.className='cred-status err';
  }
});

btnClearChat.addEventListener('click', async () => {
  try {
    await fetch('/api/clear', {method:'POST'});
  } catch {}
  chatArea.innerHTML = '';
  appendSystem('Sessão limpa.');
  settingsModal.classList.remove('open');
});

// ═══════════════════════════════════════════════════════════
//  CHAT / STREAMING
// ═══════════════════════════════════════════════════════════
async function sendMessage() {
  const text = userInput.value.trim();
  if (!text || state.streaming) return;

  userInput.value = '';
  userInput.style.height = '';
  appendMessage('user', text);

  state.streaming = true;
  btnSend.disabled = true;
  btnSend.textContent = '⏳';

  const bubble = appendMessage('assistant', '', true);
  let fullText = '';

  try {
    // "forçar modelo" (campo manual na barra) passa por cima do
    // modelo selecionado no dropdown, se preenchido.
    const forcedModel = modelOverride.value.trim();
    const r = await fetch('/api/chat', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({
        message: text,
        provider: state.provider || undefined,
        model: forcedModel || state.model || undefined,
      })
    });

    if (!r.ok) {
      const err = await r.json().catch(() => ({detail: r.statusText}));
      bubble.classList.remove('cursor-blink');
      bubble.innerHTML = `<span style="color:var(--red)">⚠ ${escHtml(err.detail || 'Erro desconhecido')}</span>`;
      return;
    }

    const reader = r.body.getReader();
    const decoder = new TextDecoder();
    let buf = '';

    while (true) {
      const {value, done} = await reader.read();
      if (done) break;
      buf += decoder.decode(value, {stream: true});
      const lines = buf.split('\n');
      buf = lines.pop();
      for (const line of lines) {
        if (!line.startsWith('data:')) continue;
        const raw = line.slice(5).trim();
        if (raw === '[DONE]') break;
        try {
          const obj = JSON.parse(raw);
          const delta = obj?.choices?.[0]?.delta?.content || '';
          if (delta) {
            fullText += delta;
            bubble.innerHTML = mdToHtml(fullText);
            chatArea.scrollTop = chatArea.scrollHeight;
          }
        } catch {}
      }
    }
  } catch(e) {
    bubble.innerHTML = `<span style="color:var(--red)">⚠ Erro de rede: ${escHtml(e.message)}</span>`;
  } finally {
    bubble.classList.remove('cursor-blink');
    state.streaming = false;
    btnSend.disabled = false;
    btnSend.textContent = '▶ ENVIAR';
    chatArea.scrollTop = chatArea.scrollHeight;
  }
}

btnSend.addEventListener('click', sendMessage);
userInput.addEventListener('keydown', e => {
  if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); }
  // Auto-resize
  setTimeout(() => {
    userInput.style.height = '';
    userInput.style.height = Math.min(userInput.scrollHeight, 160) + 'px';
  }, 0);
});

// ═══════════════════════════════════════════════════════════
//  HISTÓRICO (HooLeeSh33t v0.3 — adição autorizada por dSanT)
//  O servidor já guarda a conversa em memória enquanto o
//  processo roda. Isto só redesenha a tela com o que já existe
//  ao abrir/voltar pra página — não inventa nada novo.
// ═══════════════════════════════════════════════════════════
async function loadHistory() {
  try {
    const r = await fetch('/api/history');
    if (!r.ok) return;
    const data = await r.json();
    const messages = data.messages || [];
    if (messages.length === 0) return;

    chatArea.innerHTML = '';
    appendSystem('Histórico restaurado — continuando de onde você parou.');
    for (const m of messages) {
      appendMessage(m.role === 'user' ? 'user' : 'assistant', m.content);
    }
  } catch {
    // Sem histórico pra restaurar (ou servidor reiniciado do zero) — segue normal.
  }
}

// ═══════════════════════════════════════════════════════════
//  INIT
// ═══════════════════════════════════════════════════════════
(async () => {
  await loadProviders();
  await checkStatus();
  await refreshModelsFromAPI();  // enriquece com /v1/models se já houver credencial (.env)
  await loadHistory();
  userInput.focus();
})();
</script>
</body>
</html>
"""


# ---------------------------------------------------------------------------
# ESTADO / AGENTE
# ---------------------------------------------------------------------------

agent = Agent(allow_interactive=False)
conversation = []

# `conversation` é global (uma sessão só). Duas requisições simultâneas
# intercalariam mensagens e corromperiam o histórico — este lock serializa
# as respostas.
_chat_lock = asyncio.Lock()


def _next_or_none(iterator):
    """
    Puxa o próximo item de um iterador, devolvendo None no fim.

    Usado com `run_in_threadpool` para consumir o stream bloqueante do
    provedor sem travar o event loop do uvicorn.
    """
    try:
        return next(iterator)
    except StopIteration:
        return None


class ChatRequest(BaseModel):
    message: str
    model: str = ""
    provider: str = ""
    thinking: bool = False


class CredentialRequest(BaseModel):
    api_key: str = ""
    provider: str = ""
    base_url: str = ""
    model: str = ""


@app.get("/")
async def get_index():
    return HTMLResponse(content=HTML_CONTENT)


@app.get("/api/providers")
async def get_providers():
    if not CORE_OK:
        return {"providers": [], "error": _CORE_ERR}
    return {"providers": provider_catalog()}


@app.get("/api/models")
async def get_available_models():
    """
    Retorna os modelos efetivamente disponíveis para a credencial ativa.

    Consulta GET /v1/models no endpoint do provedor e cruza com o
    catálogo local. Assim a web mostra apenas modelos que a conta do
    usuário realmente pode invocar — não a lista estática do código.
    """
    if not CORE_OK:
        return {"models": [], "error": _CORE_ERR}

    creds = _active_credentials()
    if not creds:
        return {"models": [], "error": "no credentials"}

    cred = creds[0]
    try:
        import httpx
        headers = {"Authorization": f"Bearer {cred.api_key}"}
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(
                f"{cred.base_url}/models", headers=headers
            )
        if resp.status_code != 200:
            return {
                "models": [],
                "error": f"HTTP {resp.status_code}: {resp.text[:200]}",
            }
        data = resp.json()
        api_models = [m.get("id", "") for m in data.get("data", [])]
        if not api_models:
            return {"models": [], "error": "empty response"}

        # Cruza com o catálogo local para enriquecer com context_window
        catalog = provider_catalog()
        provider_info = next(
            (p for p in catalog if p["key"] == cred.provider_key), {}
        )
        model_ctx = {}
        for p in catalog:
            for m in p.get("models", []):
                model_ctx[m] = p.get("context_window", 128000)

        # Preserva a ordem da API, adiciona context_window quando conhecido
        result = []
        for m in api_models:
            ctx = model_ctx.get(m)
            entry = {"id": m}
            if ctx:
                entry["context_window"] = ctx
            result.append(entry)

        return {"models": result, "provider": cred.provider_key}

    except Exception as exc:
        return {"models": [], "error": str(exc)}


@app.get("/api/status")
async def get_status():
    creds = _active_credentials()
    provider_key = ""
    provider_label = ""
    if creds:
        provider_key = creds[0].provider_key
        provider_label = creds[0].label

    return {
        "allow_shell": ALLOW_SHELL,
        "cwd": os.getcwd(),
        "credentials": len(creds),
        "provider": provider_key,
        "provider_label": provider_label,
        # O padrão do encrypt é "0" — igual ao de cassandra/client.py.
        # Antes era "1", então sem a variável definida a interface dizia
        # "cifrado" enquanto o cliente NÃO cifrava: a UI mentia.
        "encrypt": os.getenv("CASSANDRA_ENCRYPT", "0").lower() in {"1", "true", "yes", "on"},
        "sanitize": os.getenv("CASSANDRA_SANITIZE", "1").lower() in {"1", "true", "yes", "on"},
        "guard": os.getenv("CASSANDRA_GUARD", "1").lower() in {"1", "true", "yes", "on"},
        "refusal_retries": os.getenv("CASSANDRA_REFUSAL_RETRIES", "2"),
        "core_ok": CORE_OK,
    }


@app.get("/api/history")
async def get_history():
    """
    HooLeeSh33t v0.3 (adição autorizada por dSanT, ver REPO-LOCK.md).

    A variável `conversation` já é global e persiste em memória
    enquanto o processo roda (ver comentário acima dela) — isto só
    expõe esse estado já existente pro front-end conseguir redesenhar
    a tela ao carregar/voltar, sem perder o que já foi dito.
    Não cria nenhum armazenamento novo, só lê o que já existia.
    """
    visible = [
        {"role": m.get("role"), "content": m.get("content")}
        for m in conversation
        if m.get("role") in ("user", "assistant")
    ]
    return {"messages": visible}


@app.post("/api/shell/toggle")
async def toggle_shell_endpoint():
    """
    Alterna o modo de execução autônoma de comandos shell em tempo de execução.
    """
    global ALLOW_SHELL
    ALLOW_SHELL = not ALLOW_SHELL
    user = getpass.getuser()
    privilege = "ROOT" if ALLOW_SHELL else "USER"
    if conversation and conversation[0].get("role") == "system":
        dynamic_skillogy, _ = agent.get_relevant_skillogy(
            "",
            allow_shell=ALLOW_SHELL,
        )
        conversation[0] = {
            "role": "system",
            "content": build_system_prompt(
                user=user,
                privilege=privilege,
                skillogy=dynamic_skillogy,
                allow_shell=ALLOW_SHELL,
            ),
        }
    return {"allow_shell": ALLOW_SHELL}


@app.post("/api/credentials")
async def set_credentials(req: CredentialRequest):
    """
    Define a credencial em runtime. Só em memória — nunca grava em disco.
    """
    global RUNTIME_CREDENTIALS
    if not CORE_OK:
        return {"success": False, "message": f"Núcleo indisponível: {_CORE_ERR}"}

    key = (req.api_key or "").strip()
    if not key:
        # Sem chave: volta a usar o .env.
        RUNTIME_CREDENTIALS = []
        agent.clear_session()
        return {"success": True, "message": "Credencial removida — usando o .env."}

    provider = resolve_provider(key, req.provider, req.base_url)
    model = (req.model or "").strip() or provider.default_model

    RUNTIME_CREDENTIALS = [
        Credential(
            provider_key=provider.key,
            api_key=key,
            model=model,
            base_url=provider.base_url,
            label=provider.label,
        )
    ]
    # Recria o cliente para pegar a nova credencial.
    agent.clear_session()

    return {
        "success": True,
        "message": f"Provedor {provider.label}, modelo {model or '(padrão)'}.",
        "provider": provider.key,
    }


@app.post("/api/clear")
async def clear_chat():
    conversation.clear()
    agent.clear_session()
    return {"success": True}


@app.post("/api/chat")
async def chat_endpoint(req: ChatRequest, request: Request):

    if not CORE_OK:
        async def err_gen():
            yield f"\n\n> ❌ **Núcleo multi-provedor indisponível:** {_CORE_ERR}\n"
        return StreamingResponse(err_gen(), media_type="text/plain")

    creds = _active_credentials()
    if not creds:
        async def no_key_gen():
            yield (
                "\n\n> 🔑 **Nenhuma chave de API configurada.**\n>\n"
                "> Clique em **⚙ CONFIGURAR API** e cole sua chave, ou defina no `.env`:\n"
                "> ```\n> CASSANDRA_API_KEY=\"nvapi-...\"\n> ```\n"
                "> O provedor é detectado automaticamente pelo formato da chave.\n"
            )
        return StreamingResponse(no_key_gen(), media_type="text/plain")

    # Override de provedor por requisição (seletor da UI).
    #
    # Precisa LIMPAR quando o pedido não traz provedor: antes o valor
    # anterior permanecia no ambiente e não havia como voltar ao
    # auto-detect. Restaura o padrão do .env quando existir.
    if req.provider.strip():
        os.environ["CASSANDRA_PROVIDER"] = req.provider.strip()
    elif _ENV_PROVIDER_DEFAULT:
        os.environ["CASSANDRA_PROVIDER"] = _ENV_PROVIDER_DEFAULT
    else:
        os.environ.pop("CASSANDRA_PROVIDER", None)

    sys_info = f"OS: {platform.system()} {platform.release()}"
    prompt = f"[SISTEMA OPERACIONAL: {sys_info} | WORKSPACE ATUAL: {os.getcwd()}]\n{req.message.strip()}"

    dynamic_skillogy, _ = agent.get_relevant_skillogy(
        prompt,
        allow_shell=ALLOW_SHELL,
        model=req.model,
        provider=req.provider or os.getenv("CASSANDRA_PROVIDER", ""),
    )
    user = getpass.getuser()
    privilege = "ROOT" if ALLOW_SHELL else "USER"

    current_system_prompt = build_system_prompt(
        user=user,
        privilege=privilege,
        skillogy=dynamic_skillogy,
        allow_shell=ALLOW_SHELL,
    )
    if not conversation or conversation[0].get("role") != "system":
        conversation.insert(0, {"role": "system", "content": current_system_prompt})
    else:
        conversation[0] = {"role": "system", "content": current_system_prompt}

    conversation.append({"role": "user", "content": prompt})

    # === COMPACTAÇÃO DE CONTEXTO (início do turno) ===
    # Roda aqui, antes do loop: neste ponto o turno anterior já terminou
    # por completo, então resumir o histórico não interrompe nenhuma
    # tarefa em andamento.
    compaction_notice = ""
    if needs_compaction(conversation):
        try:
            res = compact(conversation, agent.client, req.model)
            sys_prompt = conversation[0] if conversation and \
                conversation[0].get("role") == "system" else None
            new_conv = res.to_messages(system_prompt=sys_prompt)
            conversation.clear()
            conversation.extend(new_conv)
            how = {
                "llm": "resumo por LLM",
                "local": "resumo local (fallback)",
            }.get(res.method, res.method)
            compaction_notice = (
                f"\n\n> 💾 **Contexto compactado:** {res.removed} "
                f"mensagens resumidas ({how}).\n\n"
            )
        except Exception as exc:  # noqa: BLE001
            compaction_notice = f"\n\n> ⚠️ **Compactação falhou:** {exc}\n\n"

    async def event_generator(request=None):
        """
        Gerador ASSÍNCRONO.

        O trabalho pesado (chamadas de rede ao provedor, execução de shell)
        é bloqueante. Rodá-lo direto numa corrotina travaria o event loop do
        uvicorn e, em streams longos, o navegador veria a conexão morrer
        ("Error in input stream"). Por isso cada passo bloqueante vai para
        um thread separado com `run_in_threadpool`.

        `request` permite detectar que o operador abortou (botão Parar):
        nesse caso paramos de gastar tokens em vez de continuar gerando
        uma resposta que ninguém vai ler.
        """
        from starlette.concurrency import run_in_threadpool

        async def _cliente_desconectou() -> bool:
            if request is None:
                return False
            try:
                return await request.is_disconnected()
            except Exception:  # noqa: BLE001
                return False

        # Avisa sobre a compactação feita no início deste turno.
        if compaction_notice:
            yield compaction_notice

        step = 0
        while step < 5:
            # O operador pode ter apertado Parar entre passos. Sem esta
            # checagem continuaríamos gerando (e gastando tokens) uma
            # resposta que ninguém vai ler.
            if await _cliente_desconectou():
                return

            full_reply = []
            try:
                stream_wrapper = agent.chat_stream(
                    messages=conversation,
                    model=req.model,
                    thinking=req.thinking,
                )
                # Itera o stream em thread separada, devolvendo os chunks
                # ao event loop conforme chegam.
                iterator = iter(stream_wrapper)
                while True:
                    # Espera o próximo chunk OU a desconexão — o que vier
                    # primeiro. Sem isto, um modelo lento mantém o lock
                    # preso (e continua gerando) mesmo depois de o
                    # operador apertar Parar, porque a espera pelo chunk
                    # bloqueia qualquer outra checagem.
                    _t = asyncio.create_task(
                        run_in_threadpool(_next_or_none, iterator)
                    )
                    while True:
                        done, _ = await asyncio.wait({_t}, timeout=1.0)
                        if _t in done:
                            break
                        if await _cliente_desconectou():
                            _t.cancel()
                            # Propaga para o wrapper, que fecha o stream
                            # do modelo e mata subprocessos.
                            raise asyncio.CancelledError()
                    chunk = _t.result()
                    if chunk is None:
                        break
                    full_reply.append(chunk)
                    yield chunk

                # Avisa quando a guarda anti-recusa neutralizou uma recusa.
                try:
                    gr = agent.client.last_guard_report
                except Exception:
                    gr = {}
                if gr.get("recovered"):
                    yield (
                        "\n\n> 🛡️ **Recusa neutralizada automaticamente** "
                        f"(tentativa {gr.get('final_attempt', '?')}): o pedido foi "
                        "reescrito em termos técnicos neutros e o modelo "
                        "cooperou.\n"
                    )
                elif gr.get("detected") and gr.get("recovered") is False:
                    yield (
                        "\n\n> ⚠️ **Recusa persistente:** o modelo recusou mesmo "
                        "após reescrita. Considere reformular o pedido ou "
                        "aumentar `CASSANDRA_REFUSAL_RETRIES`.\n"
                    )
            except ProviderBlocked as e:
                yield (
                    f"\n\n> 🛡️ **SagaZ-ZeRo pausado por proteção anti-banimento:** {e}\n"
                    "> *Aguarde o cooldown ou adicione outra chave de API.*\n"
                )
                break
            except AllProvidersExhausted as e:
                yield (
                    f"\n\n> ⚠️ **Provedores esgotados:** {e}\n"
                    "> *Verifique suas chaves de API ou adicione outra em ⚙ CONFIGURAR API.*\n"
                )
                break
            except ProviderError as e:
                yield (
                    f"\n\n> ❌ **Erro do provedor:** {e}\n"
                    "> *Verifique a chave, o modelo e o endpoint configurados.*\n"
                )
                break
            except Exception as e:
                yield f"\n\n> ❌ **Erro ao consultar o SagaZ-ZeRo:** {e}\n"
                break

            reply = "".join(full_reply)
            conversation.append({"role": "assistant", "content": reply})

            # ------------------------------------------------------------------
            # Daqui para baixo tudo é pós-processamento. Qualquer exceção aqui
            # NÃO pode matar o stream (o navegador reportaria "Error in input
            # stream"), então cada bloco tem seu próprio tratamento.
            # ------------------------------------------------------------------

            # Download de ferramenta sob demanda (bloco ```tool).
            try:
                if extract_tool_blocks is not None:
                    tool_specs = extract_tool_blocks(reply)
                    if tool_specs:
                        for spec in tool_specs:
                            tname = spec.get("name", "?")
                            tsrc = spec.get("source", "?")
                            yield (
                                f"\n\n> 🔧 **Ferramenta solicitada:** "
                                f"`{tname}` (via {tsrc})\n\n"
                            )
                            # Heartbeat: um `apt install` pode levar
                            # minutos. Sem sinal de vida a interface
                            # parecia travada.
                            _tt = asyncio.create_task(
                                run_in_threadpool(tool_fetch, spec, ALLOW_SHELL)
                            )
                            while not _tt.done():
                                await asyncio.wait({_tt}, timeout=5.0)
                                if await _cliente_desconectou():
                                    return
                                if not _tt.done():
                                    yield (
                                        f"\n> ⏳ processando `{tname}`… "
                                        f"(download/instalação em andamento)\n\n"
                                    )
                            tr = _tt.result()
                            if tr.action == "suggested":
                                yield (
                                    f"> ℹ️ **Modo restrito** — rode manualmente:\n"
                                    f"> ```bash\n> {tr.command}\n> ```\n\n"
                                )
                                msg = (
                                    f"[FERRAMENTA SUGERIDA: {tname}]\n"
                                    f"Modo restrito — o operador deve rodar:\n"
                                    f"```bash\n{tr.command}\n```\n"
                                    f"Motivo: {spec.get('reason', '(não informado)')}\n\n"
                                    "Continue a tarefa assumindo que a ferramenta "
                                    "estará disponível, ou proponha uma alternativa."
                                )
                            elif tr.ok:
                                yield f"> ✅ {tr.message}\n\n"
                                if tr.path:
                                    yield f"> 📁 `{tr.path}`\n\n"
                                msg = (
                                    f"[FERRAMENTA DISPONÍVEL: {tname}]\n"
                                    f"{tr.message}\n"
                                    + (f"Caminho: {tr.path}\n" if tr.path else "")
                                    + (f"SHA-256: {tr.sha256}\n" if tr.sha256 else "")
                                    + "\nContinue a tarefa usando a ferramenta."
                                )
                            else:
                                yield f"> ⚠️ **Recusado:** {tr.message}\n\n"
                                msg = (
                                    f"[FERRAMENTA INDISPONÍVEL: {tname}]\n"
                                    f"Motivo: {tr.message}\n\n"
                                    "Não insista nesta ferramenta. Use uma "
                                    "alternativa já disponível no sistema ou "
                                    "explique o bloqueio ao operador."
                                )
                            conversation.append({"role": "user", "content": msg})
                        step += 1
                        continue
            except Exception as exc:  # noqa: BLE001
                yield f"\n\n> ⚠️ **Falha no download de ferramenta:** {exc}\n\n"

            # Carregamento de skill sob demanda (bloco ```skill).
            try:
                skill_blocks = re.findall(
                    r"```skill\s*\n(.*?)\n```", reply, re.IGNORECASE | re.DOTALL
                )
                if skill_blocks and agent._skill_index is not None:
                    for query in skill_blocks:
                        query = query.strip()
                        if not query:
                            continue
                        yield f"\n\n> 🧠 **Carregando skill:** `{query}`\n\n"
                        content, loaded = await run_in_threadpool(
                            agent._skill_index.load, query
                        )
                        if content:
                            yield f"> ✅ Carregada: {', '.join(loaded)}\n\n"
                            msg = (
                                f"[SKILL CARREGADA: {', '.join(loaded)}]\n\n"
                                f"{content}\n\n"
                                "Use o procedimento acima para continuar."
                            )
                        else:
                            avail = agent._skill_index.catalog(limit=60)
                            yield "> ⚠️ Skill não encontrada.\n\n"
                            msg = (
                                f"[SKILL NÃO ENCONTRADA: '{query}']\n\n"
                                f"Skills disponíveis: {avail}\n\n"
                                "Tente outro nome ou prossiga sem ela."
                            )
                        conversation.append({"role": "user", "content": msg})
                    step += 1
                    continue
            except Exception as exc:  # noqa: BLE001
                yield f"\n\n> ⚠️ **Falha ao carregar skill:** {exc}\n\n"

            # NOTA: a compactação NÃO acontece aqui. Ela roda no início do
            # próximo turno (antes do loop), depois que todo o trabalho
            # pendente deste turno terminou. Compactar no meio da execução
            # apagava o comando que o SagaZ-ZeRo acabara de gerar — ele
            # "largava a mão" da tarefa em andamento.

            # Execução autônoma de shell. Isolada: um comando problemático
            # não pode derrubar o stream.
            try:
                if ALLOW_SHELL:
                    # Avisa ANTES de executar. A execução pode levar
                    # minutos; sem este aviso a interface ficava parada
                    # sem nenhum sinal de vida (o "fica parado" ao usar
                    # ferramentas/comandos).
                    _cmds = extract_shell_blocks(reply)
                    if _cmds:
                        yield (
                            f"\n\n> ⚙️ **Executando {len(_cmds)} comando(s) "
                            f"localmente em `{os.getcwd()}`...**\n\n"
                        )
                        for _c in _cmds:
                            _c = _c.strip()
                            if _c:
                                yield f"> `{_c[:200]}`\n\n"

                    # Heartbeat: roda em paralelo e emite sinal de vida a
                    # cada 5s, para o stream nunca parecer travado.
                    _task = asyncio.create_task(
                        run_in_threadpool(execute_shell_blocks, reply, True)
                    )
                    while not _task.done():
                        await asyncio.wait({_task}, timeout=5.0)
                        if await _cliente_desconectou():
                            # Operador apertou Parar: encerra o stream do
                            # modelo e mata os comandos em execução.
                            try:
                                agent.client.abort_active()
                            except Exception:  # noqa: BLE001
                                pass
                            try:
                                kill_active_procs(verbose=True)
                            except Exception:  # noqa: BLE001
                                pass
                            return
                        if not _task.done():
                            yield (
                                "\n> ⏳ ainda executando… (comandos longos "
                                "podem levar alguns minutos)\n\n"
                            )
                    cmd_output = _task.result()

                    if cmd_output:
                        yield (
                            f"\n\n> ✅ **Execução concluída.**\n"
                            f"```text\n{cmd_output[:4000]}\n```\n\n"
                        )
                        msg = (
                            f"[SAÍDA DA EXECUÇÃO LOCAL NO DIRETÓRIO {os.getcwd()}]\n"
                            f"```text\n{cmd_output}\n```\n"
                            "Se o objetivo ainda não foi concluído, você PODE e DEVE "
                            "gerar novos comandos shell para continuar atuando de forma "
                            "autônoma. Caso o objetivo tenha sido atingido, apenas "
                            "apresente o resultado final."
                        )
                        conversation.append({"role": "user", "content": msg})
                        step += 1
                        continue
            except Exception as exc:  # noqa: BLE001
                yield f"\n\n> ⚠️ **Falha na execução de shell:** {exc}\n\n"

            break

    # Avisa se já houver uma resposta em andamento (em vez de corromper o
    # histórico compartilhado).
    if _chat_lock.locked():
        async def busy_gen():
            yield (
                "\n\n> ⏳ **Já existe uma resposta em andamento.**\n> "
                "Aguarde ela terminar antes de enviar outra mensagem.\n"
            )
        return StreamingResponse(busy_gen(), media_type="text/plain")

    _inner = event_generator(request)

    async def _serialized():
        # Segura o lock durante todo o stream: o histórico só é tocado
        # por uma resposta de cada vez.
        async with _chat_lock:
            try:
                async for chunk in _inner:
                    yield chunk
            except asyncio.CancelledError:
                # O cliente abortou (botão Parar, Esc ou aba fechada).
                # Encerra o trabalho DE VERDADE — não basta a tela parar:
                #  1. fecha o stream HTTP do modelo, para ele parar de
                #     gerar (e cobrar) tokens que ninguém vai ler;
                #  2. mata comandos de shell ainda em execução.
                try:
                    agent.client.abort_active()
                except Exception:  # noqa: BLE001
                    pass
                try:
                    await _inner.aclose()
                except Exception:  # noqa: BLE001
                    pass
                try:
                    _n = kill_active_procs()
                    if _n:
                        print(
                            f"[+] Parada do operador: {_n} subprocesso(s) "
                            f"encerrado(s)."
                        )
                except Exception:  # noqa: BLE001
                    pass
                raise

    return StreamingResponse(
        _serialized(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )


def run_server(port=8080, allow_shell=None):
    global ALLOW_SHELL
    if allow_shell is not None:
        ALLOW_SHELL = allow_shell

    if not CORE_OK:
        print(f"\n[!] ERRO: núcleo multi-provedor indisponível — {_CORE_ERR}")
        print("[!] Verifique se o pacote 'cassandra/' existe e as dependências estão instaladas.")
        sys.exit(1)

    creds = _active_credentials()
    print(f"\n[+] Iniciando SagaZ-ZeRo WEB na porta {port}...")
    print(f"[+] Acesse: http://localhost:{port}")
    if creds:
        for c in creds:
            print(f"[+] Provedor: {c.label} | modelo: {c.model or '(padrão)'} | chave: ...{c.api_key[-4:]}")
    else:
        print("[!] Nenhuma chave no .env — configure pela interface (⚙ CONFIGURAR API).")
    print(f"[+] Criptografia de envelope: {'ATIVA' if os.getenv('CASSANDRA_ENCRYPT','1') in ('1','true','yes','on') else 'inativa'}")
    print(f"[+] Sanitização de termos:    {'ATIVA' if os.getenv('CASSANDRA_SANITIZE','1') in ('1','true','yes','on') else 'inativa'}")
    if ALLOW_SHELL:
        print("[!] AVISO: MODO SHELL AUTOMÁTICO ATIVADO NA WEB!")

    # --- Encerramento limpo (Ctrl+C) ---
    # Dois problemas faziam o Ctrl+C "não funcionar":
    #   1. o uvicorn espera a requisição em andamento terminar — e um
    #      stream do modelo pode levar minutos;
    #   2. comandos de shell rodam em sessão própria (para podermos matar
    #      o grupo), então NÃO recebem o SIGINT e ficam pendurados.
    # O helper cuida de (2); o timeout abaixo cuida de (1).
    install_shutdown_handlers()

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info",
        # Sem isto, o Ctrl+C fica pendurado até a requisição em curso
        # terminar. 3s é suficiente para o stream fechar com elegância.
        timeout_graceful_shutdown=3,
    )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="SagaZ-ZeRo Web UI")
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.getenv("CASSANDRA_WEB_PORT", "8080")),
        help="Porta do servidor Web (padrão: 8080)",
    )
    parser.add_argument(
        "--allow-shell",
        dest="allow_shell",
        action="store_true",
        default=ALLOW_SHELL,
        help="Permite execução autônoma de comandos shell na web (padrão: ativo)",
    )
    parser.add_argument(
        "--no-allow-shell",
        dest="allow_shell",
        action="store_false",
        help="Desativa a execução autônoma de comandos shell na web",
    )
    args = parser.parse_args()
    run_server(port=args.port, allow_shell=args.allow_shell)

