# 🍃 Sistema Especialista para Rastreabilidade de Compostagem Orgânica

[![Status](https://img.shields.io/badge/Status-Planejamento_e_Arquitetura-blue)]()
[![Stack](https://img.shields.io/badge/Stack_Planejado-React_|_Python_|_PostgreSQL-success)]()

> **Projeto de Portfólio (Engenharia de Software/Ciência da Computação)** <br>
> **Autor:** Felipe Bogo <br>
> **Instituição:** Centro Universitário Católica de Santa Catarina

## 📖 Sobre o Projeto

Este repositório documenta a especificação, modelagem de requisitos e arquitetura de um software de apoio à decisão (estruturado como um **Sistema Especialista**) voltado para a gestão e certificação de usinas de compostagem de resíduos orgânicos. 

O objetivo principal do projeto é garantir o cumprimento ininterrupto da fase termofílica das leiras (temperaturas acima de 55°C) para eliminação de patógenos, automatizando as validações exigidas pelo Ministério da Agricultura e Pecuária (MAPA) no Brasil.

## ⚠️ O Problema e a Necessidade de Mercado

Atualmente, o monitoramento de pátios de compostagem sofre com uma polarização tecnológica:
1. **O Status Quo (Planilhas e Papel):** Sujeito a graves erros humanos, perdas de dados e fraudes temporais, impossibilitando uma rastreabilidade real.
2. **Soluções de Mercado (Telemetria IoT):** Dependem de hardwares importados caros (sensores de temperatura) e exigem conectividade de internet contínua (Wi-Fi/4G), algo raro em áreas agrícolas e pátios abertos.

## 💡 A Inovação e a Solução Proposta

O sistema projetado inova ao atuar como um **meio-termo inteligente e resiliente**:

- **Arquitetura PWA (Offline-First):** O frontend é planejado em React como um Progressive Web App. O operador insere a temperatura manualmente no meio do pátio, **totalmente offline**. O sistema armazena no cache do dispositivo e sincroniza os dados assim que uma rede é detectada.
- **Motor de Regras Agronômicas:** O backend planejado em Python cruza os dados coletados com a legislação do MAPA (Base de Conhecimento). Ele bloqueia datas retroativas, emite alertas se a temperatura cair abruptamente e calcula a relação Carbono/Nitrogênio ideal automaticamente.

## ⚙️ Principais Requisitos Especificados

- **RF01:** Cálculo automático de traço biológico (Balanço C:N e Umidade).
- **RF02:** Trava de inserção temporal (bloqueio contra dados retroativos).
- **RF03:** Disparo algorítmico de alertas de quebra de ciclo termofílico.
- **RNF01:** Trilha de auditoria (Log) imutável com carimbo de tempo para certificação.

## 📄 Arquivos do Repositório

Artigo científico completo formatado no padrão SBC contendo a fundamentação teórica, análise de trabalhos correlatos, detalhamento da arquitetura PWA e conclusões.


---
*Este projeto foi desenvolvido como requisito de avaliação (N3) acadêmica, focado na etapa de Engenharia de Requisitos e Planejamento Arquitetural de Software.*
