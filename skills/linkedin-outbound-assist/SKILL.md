---
name: linkedin-outbound-assist
description: "Use when researching and preparing human-reviewed LinkedIn outbound with a local CSV ledger; no automated LinkedIn actions."
version: 1.0.0
license: MIT
---

# LinkedIn outbound assistido

## Escopo
Ajude o usuário a definir ICP, encontrar empresas/decisores em fontes públicas, qualificar, preparar uma fila de revisão e rascunhos, e manter um histórico local de contatos. O usuário faz login e envia convites/mensagens manualmente. Não execute automação de LinkedIn, raspagem de páginas privadas, endpoints ocultos, extração de cookies/tokens, contorno de desafios ou envio em massa. Não prometa que intervalos entre ações tornam automação permitida.

## Fluxo
1. Defina objetivo, ICP (segmento, porte, local, cargo, sinais), exclusões e limite voluntário de volume/qualidade.
2. Pesquise primeiro sites oficiais e fontes públicas; confirme cargo atual, domínio e evidência datada. Não fabrique URL de perfil. Uma fonte não acessível fica marcada como não verificada.
3. Registre candidatos em `candidates.csv`, com `fit_score` 1–5 e `fit_reason`; dados profissionais mínimos. Descarte scores inferiores a 3.
4. Consulte `ledger.csv` e `exclusions.csv`; rode `python3 scripts/queue.py prepare --workdir <pasta-privada>`. Resolva homônimos e links duvidosos na revisão, não no envio.
5. Apresente uma fila de revisão ao usuário com motivo da seleção e contexto verificável. Faça rascunhos curtos e verdadeiros apenas se pedidos; nenhum envio sem ato manual do usuário. Respeite pedido de não contato e resposta negativa.
6. Após o usuário confirmar o resultado real, atualize `ledger.csv` com `queue.py record`. Não marque convite/mensagem como enviado a partir de uma tentativa ou rascunho.
7. Relate contagem exata de candidatos, elegíveis, excluídos, em revisão e resultados; diferencie estado local de estado confirmado na plataforma.

## Segurança
- Nunca copie credenciais, sessões, histórico privado ou listas reais para repositório público.
- Não tente superar bloqueios, CAPTCHA, limitação, avisos ou restrições da plataforma.
- Sem sequência automática de follow-ups; cada contato depende de contexto e revisão humana.
- Se faltar confirmação de cargo, URL ou consentimento de uso dos dados, mantenha o candidato fora da fila de contato.
- Use ferramentas de navegador apenas para sites públicos externos e verificação desta página; navegação do próprio LinkedIn é manual pelo usuário.
