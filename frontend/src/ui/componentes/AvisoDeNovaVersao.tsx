import { useEffect, useState } from 'react'

import { aoSurgirNovaVersao, ativarNovaVersao } from '@/infraestrutura/pwa/service-worker'

/**
 * Faixa de "nova versão disponível". A troca só acontece quando o operador
 * toca em Atualizar: recarregar sozinho poderia apagar uma coleta em digitação.
 */
export function AvisoDeNovaVersao() {
  const [registro, definirRegistro] = useState<ServiceWorkerRegistration | null>(null)

  useEffect(() => aoSurgirNovaVersao(definirRegistro), [])

  if (!registro) return null

  return (
    <div className="faixa-versao" role="status">
      <span>Nova versão do Aferra disponível.</span>
      <button type="button" className="botao botao--texto" onClick={() => ativarNovaVersao(registro)}>
        Atualizar
      </button>
    </div>
  )
}
