# SagaZ-ZeRo · HooLeeSh33t Edition _by dSant_ 🧢⚡

**What's up!** Your AI, **your way** — multi-model, your own key (BYOK), running on
your machine, your VPS, even Termux. You call the shots, it does the work. 😎

> Derivative edition of the masterpiece **Cassandra** by **Mörlsara**
> (_Morlsara Code Nexus_). We honor the origin and add our own flavor on top.
> Original credit always rides along. 🙏 _(Versão em português: [`README.md`](README.md))_

---

## What it does 🚀

- 🔑 **BYOK** — plug in **your** key (OpenAI-compatible: OpenAI, Claude, Gemini, local Ollama, your endpoint…). No account to create.
- 🧠 **Multi-model** — swap models on the fly.
- 🖥️ **Two faces, one soul:** **HooLeeSh33t Matrix** (web) and the **Operator Console** (terminal/TUI).
- 🧩 **Skills** — consented read-only Discord memory, CTI, dSant creative… and you can plug in more.
- 🔒 **Responsible by default** — key stored `0600`, destructive actions **always** confirm, nothing exposed to the internet unless you say so.

---

## Run it (3 steps) ▶️

```bash
python3 dsant.py doctor                 # 1) health check
python3 -m sagaz operator               # 2) operator console → /conectar, /testar, then just chat
python3 -m sagaz --web --port 8080      # 3) or the HooLeeSh33t Matrix web UI
#    On a VPS, use an SSH tunnel — never expose the raw port.
```

Connect a provider and **the web chat talks to the real model automatically**.
No provider? The Core still prepares your briefing locally.

---

## Update without losing your edits 🔄

Cassandra evolves upstream; we pull improvements **without wiping your work**.
Step-by-step in **[`docs/UPSTREAM.md`](docs/UPSTREAM.md)** (reviewed selective port,
no reckless merges). Full edition doctrine in
**[`docs/MASTER-PROMPT-SAGAZ.md`](docs/MASTER-PROMPT-SAGAZ.md)**.

---

## Boundaries ✋

This edition does **not** bundle filter-evasion / anti-censorship / offensive
exploitation tooling — our choice, see [`NOTICE.md`](NOTICE.md). SagaZ-ZeRo is for
building, automating and creating, responsibly.

---

## Credits 🫡

- **Edition:** SagaZ-ZeRo · HooLeeSh33t Edition — **by dSant** (`@21daTitan`, _Systemia Solutions_)
- **Original work:** **Cassandra** by **Mörlsara** — _Morlsara Code Nexus_
- **Upstream:** https://github.com/DarkyHArry/cassandra-agent
