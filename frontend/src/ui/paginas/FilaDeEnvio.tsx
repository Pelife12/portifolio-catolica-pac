/**
 * Fila de envio: as coletas que ainda estão só no aparelho.
 *
 * É o "indicador visual do status de sincronização" do operador: mostra o que
 * falta subir e por quê, e permite forçar o envio quando a rede voltar.
 */

import type { ItemDaFila } from '@/aplicacao/portas/fila-de-afericoes'
import { usarFila, usarSincronizarFila } from '@/aplicacao/hooks/usar-fila'
import { formatarDataHora } from '@/dominio/formatacao'
import { formatarTemperatura } from '@/dominio/temperatura'
import { descreverErro } from '@/infraestrutura/http/erros'
import { Botao } from '@/ui/componentes/Botao'
import { Cartao } from '@/ui/componentes/Cartao'
import { ListaEsqueleto } from '@/ui/componentes/Carregando'
import { EstadoVazio } from '@/ui/componentes/EstadoVazio'
import { FaixaDeErro } from '@/ui/componentes/FaixaDeErro'
import { Selo } from '@/ui/componentes/Selo'
import { usarStatusDeRede } from '@/ui/hooks/usar-status-de-rede'

export function FilaDeEnvio() {
  const online = usarStatusDeRede()
  const { data: itens, isPending, isError, error } = usarFila()
  const sincronizar = usarSincronizarFila()

  const pendentes = (itens ?? []).filter((item) => item.estado === 'pendente')

  return (
    <section>
      <div className="pagina__cabecalho">
        <div>
          <h1>Fila de envio</h1>
          <p className="casca__subtitulo">
            {online ? 'Online' : 'Offline · aguardando rede'}
            {' · '}
            {pendentes.length} {pendentes.length === 1 ? 'coleta pendente' : 'coletas pendentes'}
          </p>
        </div>
      </div>

      <div className="pilha">
        {isPending ? <ListaEsqueleto itens={2} altura={72} /> : null}

        {isError ? (
          <FaixaDeErro titulo="Não foi possível ler a fila do aparelho">
            {descreverErro(error)}
          </FaixaDeErro>
        ) : null}

        {itens && itens.length === 0 ? (
          <EstadoVazio icone="confirmado" titulo="Tudo enviado">
            Nenhuma coleta aguardando: tudo o que foi registrado neste aparelho já está no
            servidor.
          </EstadoVazio>
        ) : null}

        {(itens ?? []).map((item) => (
          <ItemDaFilaDeEnvio key={item.idCliente} item={item} />
        ))}

        {sincronizar.data ? <ResumoDaRodada resultado={sincronizar.data} /> : null}

        {pendentes.length > 0 ? (
          <Botao
            grande
            bloco
            carregando={sincronizar.isPending}
            onClick={() => sincronizar.mutate()}
          >
            Sincronizar agora
          </Botao>
        ) : null}
      </div>
    </section>
  )
}

function ItemDaFilaDeEnvio({ item }: { item: ItemDaFila }) {
  return (
    <Cartao compacto>
      <div className="linha linha--entre">
        <div>
          <strong>
            {item.rotuloDaLeira} · {formatarTemperatura(item.dados.temperatura_celsius)} °C
          </strong>
          <p className="texto-secundario">
            Coleta de {formatarDataHora(item.dados.registrado_em)} · salva no aparelho
          </p>
        </div>
        <Selo tom="atencao">na fila</Selo>
      </div>
      {item.ultimoErro ? (
        <p className="campo__auxiliar" style={{ marginTop: 'var(--esp-2)' }}>
          Última tentativa: {item.ultimoErro.mensagem}
        </p>
      ) : null}
    </Cartao>
  )
}

function ResumoDaRodada({
  resultado,
}: {
  resultado: { enviadas: number; pendentes: number; interrompidaPor: 'rede' | 'sessao' | null }
}) {
  if (resultado.interrompidaPor === 'rede') {
    return (
      <FaixaDeErro titulo="Sem conexão com o servidor" tom="atencao">
        {resultado.enviadas > 0 ? `${resultado.enviadas} enviadas antes da queda. ` : ''}
        As demais continuam guardadas e sobem quando a rede voltar.
      </FaixaDeErro>
    )
  }
  if (resultado.interrompidaPor === 'sessao') {
    return (
      <FaixaDeErro titulo="Sessão expirada" tom="atencao">
        Entre novamente para enviar as coletas. Nada foi perdido: a fila continua no aparelho.
      </FaixaDeErro>
    )
  }
  return (
    <p role="status" className="texto-secundario" style={{ textAlign: 'center' }}>
      {resultado.enviadas} {resultado.enviadas === 1 ? 'coleta enviada' : 'coletas enviadas'}.
    </p>
  )
}
