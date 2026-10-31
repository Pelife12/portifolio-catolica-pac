/**
 * Central de alertas (RF03).
 *
 * Os alertas são gerados pelo motor no servidor; aqui o gestor triagem: vê o
 * que abriu, reconhece (assume que está ciente, e o backend grava quem) e
 * resolve quando a leira voltou ao normal.
 */

import { useState } from 'react'
import { Link } from 'react-router-dom'

import type { Alerta, StatusAlerta } from '@/aplicacao/contratos/tipos'
import { usarAlertas, usarReconhecerAlerta, usarResolverAlerta } from '@/aplicacao/hooks/usar-alertas'
import { usarLeiras } from '@/aplicacao/hooks/usar-leiras'
import { formatarDataHora } from '@/dominio/formatacao'
import {
  ROTULO_SEVERIDADE,
  ROTULO_STATUS_ALERTA,
  ROTULO_TIPO_ALERTA,
} from '@/dominio/rotulos'
import { descreverErro } from '@/infraestrutura/http/erros'
import { Botao } from '@/ui/componentes/Botao'
import { Cartao } from '@/ui/componentes/Cartao'
import { ListaEsqueleto } from '@/ui/componentes/Carregando'
import { EstadoVazio } from '@/ui/componentes/EstadoVazio'
import { FaixaDeErro } from '@/ui/componentes/FaixaDeErro'
import { Selo, type TomDoSelo } from '@/ui/componentes/Selo'
import { CAMINHOS } from '@/ui/rotas/caminhos'

type Filtro = StatusAlerta | 'todos'

const FILTROS: { valor: Filtro; texto: string }[] = [
  { valor: 'aberto', texto: 'Abertos' },
  { valor: 'reconhecido', texto: 'Reconhecidos' },
  { valor: 'resolvido', texto: 'Resolvidos' },
  { valor: 'todos', texto: 'Todos' },
]

const TOM_POR_SEVERIDADE: Record<Alerta['severidade'], TomDoSelo> = {
  informativo: 'acento',
  atencao: 'atencao',
  critico: 'perigo',
}

export function Alertas() {
  const [filtro, definirFiltro] = useState<Filtro>('aberto')
  const consulta = usarAlertas(filtro === 'todos' ? {} : { status: filtro })
  const leiras = usarLeiras()

  const codigoDaLeira = new Map((leiras.data ?? []).map((leira) => [leira.id, leira.codigo]))

  return (
    <section>
      <div className="pagina__cabecalho">
        <div>
          <h1>Central de alertas</h1>
          <p className="texto-secundario">Detectados pelo motor de inferência</p>
        </div>
      </div>

      <div className="filtros" role="group" aria-label="Filtrar alertas por situação">
        {FILTROS.map((opcao) => (
          <button
            key={opcao.valor}
            type="button"
            className="filtro"
            aria-pressed={filtro === opcao.valor}
            onClick={() => definirFiltro(opcao.valor)}
          >
            {opcao.texto}
          </button>
        ))}
      </div>

      {consulta.isPending ? <ListaEsqueleto itens={3} altura={120} /> : null}

      {consulta.isError ? (
        <FaixaDeErro
          titulo="Não foi possível carregar os alertas"
          acoes={[{ texto: 'Tentar novamente', ao: () => void consulta.refetch() }]}
        >
          {descreverErro(consulta.error)}
        </FaixaDeErro>
      ) : null}

      {consulta.data && consulta.data.length === 0 ? (
        <EstadoVazio
          icone="confirmado"
          titulo={filtro === 'aberto' ? 'Nenhum alerta aberto' : 'Nenhum alerta nesta situação'}
        >
          {filtro === 'aberto'
            ? 'Todas as leiras acompanhadas estão dentro das regras do ciclo termofílico.'
            : 'Troque o filtro para ver os alertas em outra situação.'}
        </EstadoVazio>
      ) : null}

      {consulta.data && consulta.data.length > 0 ? (
        <div className="pilha">
          {consulta.data.map((alerta) => (
            <ItemDeAlerta
              key={alerta.id}
              alerta={alerta}
              codigoDaLeira={codigoDaLeira.get(alerta.leira_id)}
            />
          ))}
        </div>
      ) : null}
    </section>
  )
}

function ItemDeAlerta({
  alerta,
  codigoDaLeira,
}: {
  alerta: Alerta
  codigoDaLeira: string | undefined
}) {
  const reconhecer = usarReconhecerAlerta()
  const resolver = usarResolverAlerta()
  const ocupado = reconhecer.isPending || resolver.isPending

  return (
    <Cartao compacto tom={alerta.severidade === 'critico' ? 'critico' : 'normal'}>
      <div className="alerta-item__topo">
        <div>
          <strong>{ROTULO_TIPO_ALERTA[alerta.tipo]}</strong>
          <p className="texto-secundario">
            <Link to={CAMINHOS.leira(alerta.leira_id)}>{codigoDaLeira ?? 'Leira'}</Link> ·{' '}
            {formatarDataHora(alerta.detectado_em)}
          </p>
        </div>
        <div className="pilha pilha--curta" style={{ alignItems: 'flex-end' }}>
          <Selo tom={TOM_POR_SEVERIDADE[alerta.severidade]}>
            {ROTULO_SEVERIDADE[alerta.severidade]}
          </Selo>
          <Selo tom={alerta.status === 'resolvido' ? 'ok' : 'neutro'}>
            {ROTULO_STATUS_ALERTA[alerta.status]}
          </Selo>
        </div>
      </div>

      <p className="alerta-item__mensagem">{alerta.mensagem}</p>

      {reconhecer.isError || resolver.isError ? (
        <p className="campo__auxiliar campo__auxiliar--erro" role="alert">
          {descreverErro(reconhecer.error ?? resolver.error)}
        </p>
      ) : null}

      {alerta.status !== 'resolvido' ? (
        <div className="alerta-item__acoes">
          {alerta.status === 'aberto' ? (
            <Botao
              variante="secundario"
              disabled={ocupado}
              onClick={() => reconhecer.mutate(alerta.id)}
            >
              Reconhecer
            </Botao>
          ) : null}
          <Botao disabled={ocupado} onClick={() => resolver.mutate(alerta.id)}>
            Marcar como resolvido
          </Botao>
        </div>
      ) : (
        <p className="texto-secundario" style={{ marginTop: 'var(--esp-3)' }}>
          Resolvido
          {alerta.reconhecido_em ? ` · reconhecido em ${formatarDataHora(alerta.reconhecido_em)}` : ''}
        </p>
      )}
    </Cartao>
  )
}
