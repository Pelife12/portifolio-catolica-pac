# 🍃 Sistema Especialista para Rastreabilidade de Compostagem Orgânica

[![Status](https://img.shields.io/badge/Status-Desenvolvimento_conclu%C3%ADdo-success)]()
[![Stack](https://img.shields.io/badge/Stack-React_PWA_|_FastAPI_|_PostgreSQL-blue)]()

> **Projeto de Portfólio (Engenharia de Software/Ciência da Computação)** <br>
> **Autor:** Felipe Bogo <br>
> **Instituição:** Centro Universitário Católica de Santa Catarina (Católica SC)

## 📖 Sobre o Projeto

Este repositório documenta a especificação, modelagem de requisitos e arquitetura de um software de apoio à decisão (estruturado como um **Sistema Especialista**) voltado para a gestão e certificação de usinas de compostagem de resíduos orgânicos. 

O objetivo principal do projeto é garantir o cumprimento ininterrupto da fase termofílica das leiras (temperaturas acima de 55°C) para eliminação de patógenos, automatizando as validações exigidas pelo Ministério da Agricultura e Pecuária (MAPA) no Brasil.

## ⚠️ O Problema e a Necessidade de Mercado

Atualmente, o monitoramento de pátios de compostagem sofre com uma polarização tecnológica:
1. **O Status Quo (Planilhas e Papel):** Sujeito a graves erros humanos, perdas de dados e fraudes temporais, impossibilitando uma rastreabilidade real.
2. **Soluções de Mercado (Telemetria IoT):** Dependem de hardwares importados caros (sensores de temperatura) e exigem conectividade de internet contínua (Wi-Fi/4G), algo que falha frequentemente em áreas agrícolas e pátios abertos ("sombras de sinal").

## 💡 A Inovação e a Solução Proposta

O sistema projetado inova ao atuar como um **meio-termo inteligente e resiliente**, centralizando todo o cálculo agronômico, coleta e emissão de laudos em uma única plataforma operável no campo:

- **Arquitetura PWA (Offline-First):** O operador insere a temperatura manualmente no meio do pátio com um smartphone, **totalmente offline**. O sistema armazena no cache do dispositivo e sincroniza os dados passivamente assim que uma rede Wi-Fi é detectada.
- **Motor de Regras Agronômicas:** O backend atua como o "cérebro" da operação, cruzando os dados coletados com a legislação do MAPA (Base de Conhecimento), bloqueando adulterações temporais e emitindo alertas preventivos.

## ⚙️ Especificação de Requisitos

A arquitetura foi mapeada com rigor técnico para o desenvolvimento futuro, destacando-se:

### Requisitos Funcionais (RF)
- **RF01:** Cálculo automático de traço biológico (Balanço Carbono/Nitrogênio e Umidade ideal).
- **RF02:** Trava lógica sistêmica impedindo a inserção de dados com datas retroativas a 24 horas.
- **RF03:** Disparo algorítmico de alertas ao gestor em caso de quebra de ciclo termofílico (queda de temperatura).
- **RF04:** Geração e exportação automática de laudos de auditoria em PDF.
- **RF05:** Sincronização assíncrona dos dados via *Service Workers* (PWA) ao detectar conectividade.

### Requisitos Não Funcionais e Restrições (RNF)
- **RNF01 (Auditoria):** Geração de Logs imutáveis com carimbo de tempo, geolocalização e usuário.
- **RNF03 (Usabilidade UX):** Interface adaptada com alto contraste e botões expandidos para uso de operadores com luvas no pátio.
- **Restrições Tecnológicas:** - **Frontend:** Desenvolvido obrigatoriamente em **React** (Ecossistema PWA).
  - **Backend:** Desenvolvido em **Python** (FastAPI/Django) para alta eficiência matemática no motor de inferência.
  - **Banco de Dados:** **PostgreSQL** para garantir persistência e relacionamento atômico (ACID) dos dados biológicos.

## 🚀 Roadmap de Desenvolvimento

O ciclo de desenvolvimento e implantação do software está dimensionado em 6 Sprints mensais:

- **Mês 1:** Infraestrutura, modelagem do Banco de Dados (PostgreSQL) e base da API RESTful.
- **Mês 2:** Codificação do Motor de Inferência (Python) e tradução das regras do MAPA.
- **Mês 3:** Desenvolvimento da interface UI/UX *mobile-first* (React).
- **Mês 4:** Conversão da aplicação para PWA, configurando IndexedDB para modo 100% offline.
- **Mês 5:** Integração Frontend/Backend e simulações de estresse de sincronização assíncrona.
- **Mês 6:** Homologação em usina parceira, ajustes práticos e *deploy* em produção.

## 📄 Arquivos do Repositório

Artigo científico completo formatado no padrão da Sociedade Brasileira de Computação (SBC), contendo a fundamentação teórica, análise de trabalhos correlatos, modelagem da arquitetura e conclusões do planejamento.
[PAC_COMPOSTAGEM_N3.pdf](https://github.com/user-attachments/files/28938844/PAC_COMPOSTAGEM_N3.pdf)

Design teste feito até o momento: https://claude.ai/code/artifact/75ba4c83-95e3-4581-8ee2-2067499bf65b

## 🛠️ Estado do desenvolvimento

Todas as entregas do cronograma (06/08 a 03/12) estão implementadas:

| Requisito | Onde está |
| --- | --- |
| RF01 · Traço C/N e umidade | `domain/services/calculo_de_traco.py` · tela Nova leira com cálculo em tempo real |
| RF02 · Trava de 24h | validação na API, gatilho no banco e checagem prévia no PWA |
| RF03 · Motor termofílico e alertas | `domain/services/motor_de_alertas.py` · central de alertas |
| RF04 · Laudo em PDF | `GET /api/v1/leiras/{id}/laudo` · botão "Laudo PDF" no histórico da leira |
| RF05 · Sincronização assíncrona | fila em IndexedDB, Background Sync e idempotência por `id_cliente` |
| RNF01 · Auditoria | timestamp com fuso, GPS obrigatório, usuário do token e `audit_log` imutável |
| RNF02 · Teto de 2 s | índices das consultas recorrentes e cabeçalho `Server-Timing` com aviso no log |
| RNF03 · Usabilidade de campo | alvos de 48–72 px, passo de 0,5 °C, contraste AA nos dois temas |

| Pasta | O que é |
| --- | --- |
| `backend/` | API FastAPI em Clean Architecture, PostgreSQL e migrations Alembic |
| `frontend/` | PWA em React, instalável e operável offline ([frontend/README.md](frontend/README.md)) |

### Desenvolvimento

```bash
docker compose up --build                       # PostgreSQL + API em http://localhost:8000
cd frontend && npm install && npm run dev        # PWA em http://localhost:5173
```

### Homologação

Build de produção do PWA (Service Worker ativo) servido por nginx, API sem reload e segredo do JWT obrigatório:

```bash
JWT_SEGREDO=$(openssl rand -hex 32) docker compose -f docker-compose.homologacao.yml up --build -d
```

PWA em <http://localhost:8080> · documentação da API em <http://localhost:8000/docs>.

### Demonstração ponta a ponta

```bash
docker compose -f docker-compose.homologacao.yml exec api python -m scripts.seed_demo
```

O script cria uma usina de demonstração com um gestor, um operador e três leiras — uma conforme, uma não conforme (com alerta do motor) e uma em andamento — e imprime os acessos de teste no terminal. Roteiro sugerido:

1. **Entrar** como operador no celular e instalar o app ("Adicionar à tela inicial").
2. **Coletar** na LR-103: ajustar a temperatura com `+`/`−` (toque longo acelera), aguardar o GPS e registrar.
3. **Cortar a rede** (modo avião) e registrar outra coleta: ela vai para a **Fila**, com o marcador na aba.
4. **Voltar a rede**: a fila sobe sozinha (Background Sync), sem duplicar — o `id_cliente` garante a idempotência.
5. **Testar a trava de 24h**: no campo "Momento da coleta", voltar a data dois dias; o app avisa antes de enviar e a API/banco recusam.
6. Entrar como **gestor** no desktop: Painel do pátio, **Central de alertas** (LR-102 não atingiu 55 °C em 72 h) e histórico com a curva de temperatura.
7. **Emitir o laudo** da LR-101 (conforme) e da LR-102 (não conforme) e conferir o hash de integridade no rodapé.

> Os dados históricos da demonstração são gravados com os gatilhos desligados **apenas dentro da transação do script**, porque aferições de dias atrás violam a trava de 24h. Nenhum caminho da API consegue fazer isso.

---
*Este projeto foi desenvolvido como requisito de avaliação (N3) acadêmica, focado na etapa de Engenharia de Requisitos e Planejamento Arquitetural de Software.*
