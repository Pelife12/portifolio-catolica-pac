/** Tela de entrada no pátio. */

import { useState } from 'react'
import { Navigate, useLocation } from 'react-router-dom'

import { usarAutenticado, usarEntrar } from '@/aplicacao/hooks/usar-sessao'
import { descreverErro } from '@/infraestrutura/http/erros'
import { Botao } from '@/ui/componentes/Botao'
import { CampoDeTexto } from '@/ui/componentes/CampoDeTexto'
import { Cartao } from '@/ui/componentes/Cartao'
import { FaixaDeErro } from '@/ui/componentes/FaixaDeErro'
import { AlternadorDeTema } from '@/ui/componentes/AlternadorDeTema'
import { CAMINHOS } from '@/ui/rotas/caminhos'

export function Login() {
  const autenticado = usarAutenticado()
  const localizacao = useLocation()
  const entrar = usarEntrar()

  const [email, definirEmail] = useState('')
  const [senha, definirSenha] = useState('')

  const destino = (localizacao.state as { de?: string } | null)?.de ?? CAMINHOS.leiras
  if (autenticado) return <Navigate to={destino} replace />

  const podeEnviar = email.trim().length > 0 && senha.length > 0

  return (
    <div className="casca-auth">
      <div className="casca-auth__caixa pilha">
        <div className="linha linha--entre">
          <div className="linha">
            <div className="casca__marca" aria-hidden="true">
              A
            </div>
            <div>
              <h1>Entrar no pátio</h1>
              <p className="casca__subtitulo">Rastreabilidade de compostagem</p>
            </div>
          </div>
          <AlternadorDeTema />
        </div>

        <Cartao>
          <form
            className="pilha"
            onSubmit={(evento) => {
              evento.preventDefault()
              if (podeEnviar) entrar.mutate({ email: email.trim(), senha })
            }}
          >
            <CampoDeTexto
              rotulo="E-mail"
              type="email"
              inputMode="email"
              autoComplete="username"
              autoCapitalize="none"
              spellCheck={false}
              required
              value={email}
              onChange={(evento) => definirEmail(evento.target.value)}
            />
            <CampoDeTexto
              rotulo="Senha"
              type="password"
              autoComplete="current-password"
              required
              value={senha}
              onChange={(evento) => definirSenha(evento.target.value)}
            />

            {entrar.isError ? (
              <FaixaDeErro titulo="Não foi possível entrar">
                {descreverErro(entrar.error)}
              </FaixaDeErro>
            ) : null}

            <Botao
              type="submit"
              grande
              bloco
              disabled={!podeEnviar}
              carregando={entrar.isPending}
            >
              Entrar
            </Botao>
          </form>
        </Cartao>

        <p className="texto-secundario" style={{ textAlign: 'center' }}>
          A sessão dura a jornada de trabalho e continua valendo se o aparelho
          ficar sem rede no pátio.
        </p>
      </div>
    </div>
  )
}
