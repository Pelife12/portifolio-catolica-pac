/** Esqueletos no formato do conteúdo final, em vez de um spinner genérico. */

interface PropsDeEsqueleto {
  altura?: number
  largura?: string
}

export function Esqueleto({ altura = 16, largura = '100%' }: PropsDeEsqueleto) {
  return <div className="esqueleto" style={{ height: altura, width: largura }} />
}

export function ListaEsqueleto({ itens = 3, altura = 92 }: { itens?: number; altura?: number }) {
  return (
    <div className="esqueleto-lista" aria-hidden="true">
      {Array.from({ length: itens }, (_, indice) => (
        <Esqueleto key={indice} altura={altura} />
      ))}
    </div>
  )
}

/** Região anunciada por leitor de tela enquanto a lista carrega. */
export function AvisoDeCarregamento({ texto = 'Carregando…' }: { texto?: string }) {
  return (
    <p role="status" className="somente-leitores">
      {texto}
    </p>
  )
}
