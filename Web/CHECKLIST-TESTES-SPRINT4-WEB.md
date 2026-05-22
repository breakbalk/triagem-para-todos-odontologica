# Checklist manual — Sprint 4 (Web COE)

Backend: `cd Web/backend` → `python app.py` (ou `COE_STORAGE=json`).

## RF08 / RF09 / RN15 — Confirmação

- [ ] Enviar triagem e abrir `/pages/confirmacao.html`
- [ ] Card roxo exibe **especialidade** e **turno** corretos (RN15)
- [ ] Resumo completo com protocolo, nome, telefone, status
- [ ] Nota sobre horário definido pela equipe

## RF10 / RN16 — Documentos

- [ ] Home: botão «Documentos necessários» abre modal pergaminho
- [ ] Confirmação: seção fixa lista RG/CPF, SUS, comprovante (legível no celular)
- [ ] Triagem: bloco «Antes de ir à clínica»

## Logout e segurança

- [ ] Home / Triagem / Confirmação / Admin: «Sair» pede confirmação
- [ ] Após sair: volta ao login; `sessionStorage` sem `coe_last_triagem`
- [ ] `localStorage` sem `usuario_logado` / `nivel_acesso`
- [ ] Admin sem login de cookie → redireciona para login (sem depender de localStorage)

## Performance (RNF04 / RNF06)

- [ ] Home: vídeo com `preload="none"`; decoração `loading="lazy"`
- [ ] Páginas usam `/css/style.min.css`
- [ ] Regenerar CSS: `python Web/tools/minify_css.py`
- [ ] Carregamento inicial da home aceitável em rede 3G simulada (DevTools)

## Compatibilidade

- [ ] Chrome mobile (ou responsivo 375px)
- [ ] Tablet ~768px — fundos e modal
- [ ] `prefers-reduced-motion`: vídeo da home oculto
