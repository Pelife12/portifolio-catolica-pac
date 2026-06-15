# 🍃 Sistema Especialista para Rastreabilidade de Compostagem Orgânica

[![Status](https://img.shields.io/badge/Status-Planejamento_e_Arquitetura-blue)]()
[![Stack](https://img.shields.io/badge/Stack_Planejado-React_|_Python_|_PostgreSQL-success)]()

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

---
*Este projeto foi desenvolvido como requisito de avaliação (N3) acadêmica, focado na etapa de Engenharia de Requisitos e Planejamento Arquitetural de Software.*
