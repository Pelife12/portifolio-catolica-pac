/** Lista das leiras da usina — tela inicial do operador. */

import { Link, useNavigate } from 'react-router-dom'

import type { Leira } from '@/aplicacao/contratos/tipos'
import { usarLeiras } from '@/aplicacao/hooks/usar-leiras'
import { diasDesde, formatarData, formatarMassa, formatarNumero } from '@/dominio/formatacao'
import { ROTULO_STATUS_LEIRA } from '@/dominio/rotulos'
import { descreverErro } from '@/infraestrutura/http/erros'
import { AvisoDeCarregamento, ListaEsqueleto } from '@/ui/componentes/Carregando'
import { Cartao } from '@/ui/componentes/Cartao'
import { EstadoVazio } from '@/ui/componentes/EstadoVazio'
import { FaixaDeErro } from '@/ui/componentes/FaixaDeErro'
import { Botao } from '@/ui/componentes/Botao'
import { Selo, type TomDoSelo } from '@/ui/componentes/Selo'
import { CAMINHOS } from '@/ui/rotas/caminhos'

const TOM_POR_STATUS: Record<Leira['status'], TomDoSelo> = {
  em_montagem: 'neutro',
  ativa: 'ok',
  em_maturacao: 'acento',
  encerrada: 'neutro',
}

export function Leiras() {
  const navegar = useNavigate()
  const { data: leiras, isPending, isError, error, refetch } = usarLeiras()

  return (
    <section>
      <div className="pagina__cabecalho">
        <div>
          <h1>Leiras</h1>
          <p className="texto-secundario">Pátio em acompanhamento</p>
        </div>
        <Botao onClick={() => navegar(CAMINHOS.novaLeira)}>Nova leira</Botao>
      </div>

      {isPending ? (
        <>
          <AvisoDeCarregamento texto="Carregando as leiras…" />
          <ListaEsqueleto itens={3} />
        </>
      ) : null}

      {isError ? (
        <FaixaDeErro
          titulo="Não foi possível carregar as leiras"
          acoes={[{ texto: 'Tentar novamente', ao: () => void refetch() }]}
        >
          {descreverErro(error)}
        </FaixaDeErro>
      ) : null}

      {leiras && leiras.length === 0 ? (
        <EstadoVazio
          titulo="Nenhuma leira cadastrada"
          acao={
            <Link className="botao" to={CAMINHOS.novaLeira}>
              Cadastrar a primeira leira
            </Link>
          }
        >
          Cadastre a leira com a composição da mistura para o sistema calcular o
          traço e começar a acompanhar o ciclo.
        </EstadoVazio>
      ) : null}

      {leiras && leiras.length > 0 ? (
        <div className="lista-leiras">
          {leiras.map((leira) => (
            <ItemDeLeira key={leira.id} leira={leira} />
          ))}
        </div>
      ) : null}
    </section>
  )
}

function ItemDeLeira({ leira }: { leira: Leira }) {
  const dias = diasDesde(leira.data_montagem)

  return (
    <Cartao compacto>
      <div className="leira-item__topo">
        <span className="leira-item__codigo">{leira.codigo}</span>
        <Selo tom={TOM_POR_STATUS[leira.status]}>{ROTULO_STATUS_LEIRA[leira.status]}</Selo>
      </div>

      <div className="leira-item__dados">
        <span className="leira-item__dado">
          Montada em <strong>{formatarData(leira.data_montagem)}</strong> · dia{' '}
          <strong>{dias}</strong>
        </span>
        {leira.relacao_cn_inicial ? (
          <span className="leira-item__dado">
            C/N inicial <strong>{formatarNumero(leira.relacao_cn_inicial, 1)}</strong>
          </span>
        ) : null}
        {leira.massa_total_kg ? (
          <span className="leira-item__dado">
            Lote <strong>{formatarMassa(leira.massa_total_kg)}</strong>
          </span>
        ) : null}
      </div>
    </Cartao>
  )
}
