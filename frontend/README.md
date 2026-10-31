# Frontend — PWA de campo (Aferra)

Aplicação React que o operador usa no pátio para registrar aferições e o gestor
usa para acompanhar as leiras. Consome a API FastAPI deste mesmo repositório.

A conversão para PWA (manifest, Service Worker, IndexedDB e Background Sync) é a
Sprint 4; esta sprint entrega a aplicação React, a integração com a API e as
telas de operação.

## Como rodar

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

Com a API no ar (`docker compose up` na raiz do repositório), o app sobe em
<http://localhost:5173> e fala com <http://localhost:8000/api/v1>. O servidor de
desenvolvimento escuta na rede local (`host: true`) para dar para abrir no
celular e testar o GPS e os alvos de toque no aparelho de verdade.

> O GPS só é liberado pelos navegadores em `localhost` ou sob HTTPS. Para testar
> no celular pela rede local, use um túnel HTTPS ou a porta encaminhada do
> navegador — em HTTP puro a captura falha e a tela exibe o erro de GPS.

| Script | O que faz |
| --- | --- |
| `npm run dev` | Servidor de desenvolvimento com HMR |
| `npm run build` | Checagem de tipos e build de produção |
| `npm run teste` | Testes unitários do domínio (Vitest) |
| `npm run tipos` | Só a checagem de tipos |

## Arquitetura

As mesmas quatro camadas do backend, com as dependências apontando sempre para
dentro:

```
src/
  dominio/          Regras puras: faixas agronômicas, temperatura, umidade,
                    janela de 24h, formatação. Sem React e sem rede.
  aplicacao/        Casos de uso e orquestração.
    contratos/      Tipos espelhados dos DTOs Pydantic da API.
    portas/         Interfaces de infraestrutura (sessão, geolocalização).
    api/            Um objeto por recurso da API, sobre o cliente HTTP.
    hooks/          React Query: consultas, mutações e chaves de cache.
    sessao/         Guarda do token, fora da árvore React.
    dependencias.tsx  Composition root — equivalente ao api/deps.py.
  infraestrutura/   Implementações concretas: fetch, localStorage, Geolocation.
  ui/               Componentes, layout, páginas e rotas.
  estilos/          Tokens e CSS por camada (tokens, base, componentes, layout, páginas).
```

Regras que valem em todo o código:

- nenhuma tela chama `fetch`: tudo passa pelo `ClienteHttp`, que concentra token,
  timeout e tradução de erro;
- nenhum componente instancia infraestrutura: as dependências vêm do
  `ProvedorDeDependencias`, o que permite trocar GPS e armazenamento por dublês
  em teste;
- o `dominio/` não importa nada de `ui/` nem de `aplicacao/`.

## Decisões de campo (RNF03)

- **Alvos grandes:** 48px de mínimo, 72px nos botões `+`/`−` da temperatura.
- **Passo de 0,5 °C** com toque longo acelerando, porque subir de 42 °C a 58 °C
  dariam 32 toques com luva.
- **Contraste AA nos dois temas:** o cinza dos rótulos monoespaçados foi
  calibrado para 4,5:1 tanto no claro quanto no escuro.
- **Erro sempre no contexto**, nunca em toast que desaparece: o operador pode
  estar olhando o termômetro quando o aviso sobe.
- **Um acento e um raio de canto**, definidos em `estilos/tokens.css`.

## Relação com os requisitos

| Requisito | Onde aparece |
| --- | --- |
| RF01 | Cadastro de leira com traço em tempo real (`NovaLeira`) |
| RF02 | Checagem da janela de 24h antes de enviar e tratamento da recusa da API |
| RF03 | Painel de alertas e reavaliação da leira pelo motor |
| RNF01 | Timestamp local, geolocalização obrigatória e usuário do token na coleta |
| RNF03 | Biblioteca de componentes de campo |
