# Hermes · Outbound assistido no LinkedIn

Kit **limpo e compartilhável** para pesquisar contas, qualificar decisores, preparar abordagens, revisar uma fila e registrar resultados. **Não é um bot de disparo.** O envio e o login no LinkedIn são manuais; não há coleta de cookies, scraping de páginas privadas nem automação de convites/mensagens.

**[Abrir a página visual do kit](https://eduardovaladares37.github.io/hermes-linkedin-outbound-kit/)** · [Guia do Hermes](https://hermes-agent.nousresearch.com/docs/) · [Acordo de Usuário do LinkedIn](https://www.linkedin.com/legal/user-agreement)

## Comece em 5 minutos

1. Instale o [Hermes Agent](https://hermes-agent.nousresearch.com/docs/) pelo procedimento oficial e configure **seu próprio** provedor/modelo com `hermes setup`. Nunca copie `~/.hermes/.env`, `auth.json` ou perfis de navegador de outra pessoa.
2. Clone o repositório e copie a skill local: `mkdir -p ~/.hermes/skills/linkedin-outbound-assist && cp skills/linkedin-outbound-assist/SKILL.md ~/.hermes/skills/linkedin-outbound-assist/SKILL.md`. Reinicie a sessão para descoberta da skill; confirme com `hermes skills list`.
3. Crie seu espaço privado de trabalho **fora deste repo público**: `mkdir -p ~/linkedin-outbound-private && cp templates/candidates.csv templates/ledger.csv templates/exclusions.csv ~/linkedin-outbound-private/`.
4. Substitua as linhas **fictícias** de `candidates.csv` por contas e pessoas verificadas em fontes públicas. Ajuste `exclusions.csv` e rode `python3 scripts/queue.py prepare --workdir ~/linkedin-outbound-private`.
5. Abra `review_queue.csv`, revise a pertinência e a identidade de cada pessoa, e faça os contatos **manualmente** no LinkedIn com sua conta autorizada. Após confirmar visualmente o envio, registre: `python3 scripts/queue.py record --workdir ~/linkedin-outbound-private --url 'https://www.linkedin.com/in/exemplo/' --status connection_sent`.

> Dica: nunca execute `record` antecipadamente. Um convite pendente ou mensagem enviada deve ser confirmado na interface antes de ser marcado como enviado.

## Stack selecionada da infraestrutura Hermes

| Camada | Papel | Necessária? |
| --- | --- | --- |
| Hermes Agent + provedor configurado pelo destinatário | Pesquisa, síntese e rascunhos com supervisão | Sim |
| `web_search`, `web_extract` | Encontrar sites oficiais, notícias e fontes públicas | Sim (ou pesquisa manual se indisponível) |
| `read_file`, `write_file`, `search_files`, `terminal` | Manter CRM local e executar `queue.py` | Sim |
| `browser_exec` / Playwright | Verificar **sites públicos de empresas** ou testar esta página; não controlar LinkedIn | Opcional |
| Skill `linkedin-outbound-assist` (neste repo) | Processo de ICP → evidência → revisão → contato manual → registro | Recomendada |
| CSV local + `queue.py` | Exclusões, deduplicação por URL e fila de revisão | Recomendado |
| `computer_use`, Cloakbrowser, Browser Harness | Não são exigidos para este kit; isolamento de navegação não é autorização para automatizar LinkedIn | Não |
| MCPs de CRM, agendamento ou email | Integrações adicionais, com credenciais e permissões próprias | Não |

Esta é uma **adaptação original e mínima**, não uma exportação da instalação de Eduardo: nenhuma skill privada, histórico de campanha, lead real, credencial, script de envio, perfil do navegador ou configuração pessoal foi copiado. O kit funciona com Python 3 (biblioteca padrão) mesmo sem Hermes; Hermes acrescenta pesquisa e revisão assistidas.

## Processo operacional

1. **ICP e exclusões:** território, setor, porte, cargo decisor, sinal de necessidade, clientes e contatos proibidos.
2. **Pesquisa:** começar pela empresa e seu site oficial; buscar o decisor em fonte pública, confirmar cargo atual e registrar a URL de evidência. Não inferir uma URL de perfil apenas pelo nome.
3. **Qualificação:** score 1–5, motivo e contexto verificável; não preencher a lista com contatos fracos para bater meta.
4. **Preparação:** `queue.py prepare` elimina duplicatas/contatos prévios, exige URL de perfil válida e score ≥ 3, e mantém no máximo uma pessoa por domínio da empresa na fila padrão.
5. **Revisão humana:** conferir perfil/empresa, revisar qualquer texto gerado e optar por enviar ou descartar. Não automatizar ações na conta LinkedIn.
6. **Registro e acompanhamento:** só depois da confirmação manual, registrar `connection_sent`/`message_sent`, resposta, reunião ou `do_not_contact`. Parar imediatamente se houver recusa, aviso, limitação ou desafio da plataforma.

### Prompt inicial sugerido

```text
Use a skill linkedin-outbound-assist. Meu ICP é [setor, porte, território, cargos, sinais];
minhas exclusões são [lista]. Pesquise empresas e decisores em fontes públicas,
registre evidência e confiança, deduplique contra meu ledger local e entregue apenas
uma fila de revisão. Não acesse dados privados do LinkedIn, não envie convites ou
mensagens e não invente URLs de perfis.
```

## Formato dos dados e comandos

- `candidates.csv`: `company,domain,name,title,linkedin_url,source_url,fit_score,fit_reason,personalization_hook`
- `ledger.csv`: `linkedin_url,status,last_action_at,notes` — contatos registrados manualmente.
- `exclusions.csv`: `type,value,reason` — tipos `domain` ou `linkedin_url`.
- `review_queue.csv`: gerado pelo comando `prepare`; **não** contém dados pessoais nesta cópia pública.

```bash
python3 scripts/queue.py prepare --workdir ~/linkedin-outbound-private
python3 scripts/queue.py record --workdir ~/linkedin-outbound-private --url 'https://www.linkedin.com/in/exemplo/' --status do_not_contact --notes 'solicitou não receber contato'
python3 -m unittest discover -s tests -v
```

`record` aceita `connection_sent`, `message_sent`, `replied_positive`, `replied_negative`, `meeting_booked`, `do_not_contact`, `skipped`. Repetir o mesmo par URL+status não cria duplicata. A fila exclui qualquer URL já registrada no ledger (inclusive `skipped`) e qualquer exclusão explícita; reengajamento é deliberado e manual.

## Privacidade e limites

- **Não publique** seu diretório de trabalho privado, CSVs reais, prints, logs, cookies, tokens, senhas, sessões ou identificadores de clientes neste repo.
- Use somente informação profissional publicamente disponível ou fornecida com autorização; minimize dados pessoais e respeite pedidos de não contato.
- O [Acordo de Usuário do LinkedIn](https://www.linkedin.com/legal/user-agreement) restringe scraping e métodos automatizados não autorizados para acesso, contatos, mensagens e engajamento. Este kit deliberadamente não fornece automação dessas ações. Pacing/delays ou navegador isolado não tornam uma automação proibida permitida.
- Revise obrigações legais aplicáveis e regras da plataforma antes de usar dados e contatos. Nenhuma taxa horária ou diária garante conformidade ou segurança da conta.

## Estrutura

```text
index.html                         Página pública
skills/linkedin-outbound-assist/   Skill portátil e sem dados pessoais
templates/                         CSVs fictícios
scripts/queue.py                   Preparação e registro local, sem rede
tests/                             Testes com dados artificiais
```

Licença do conteúdo e código originais deste kit: MIT (`LICENSE`). Não inclui Hermes, LinkedIn, Browser Harness nem dados de terceiros; cada projeto mantém sua própria licença e termos.
