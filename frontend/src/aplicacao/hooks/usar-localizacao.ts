/**
 * Captura de geolocalização para a coleta (RNF01).
 *
 * A captura começa assim que a tela abre, porque o primeiro fix de GPS em pátio
 * aberto leva alguns segundos — esperar o operador apertar "registrar" para
 * pedir a posição faria a tela travar na hora errada.
 */

import { useCallback, useEffect, useRef, useState } from 'react'

import { usarDependencias } from '@/aplicacao/dependencias'
import {
  ErroDeGeolocalizacao,
  type Coordenada,
} from '@/aplicacao/portas/localizador'

export type EstadoDaLocalizacao = 'inicial' | 'capturando' | 'capturada' | 'falhou'

export interface Localizacao {
  estado: EstadoDaLocalizacao
  coordenada: Coordenada | null
  erro: ErroDeGeolocalizacao | null
  capturar: () => void
}

export function usarLocalizacao({ automatico = true } = {}): Localizacao {
  const { localizador } = usarDependencias()
  const [estado, definirEstado] = useState<EstadoDaLocalizacao>('inicial')
  const [coordenada, definirCoordenada] = useState<Coordenada | null>(null)
  const [erro, definirErro] = useState<ErroDeGeolocalizacao | null>(null)
  // Evita aplicar o resultado de uma captura numa tela já desmontada.
  const montado = useRef(true)

  useEffect(() => {
    montado.current = true
    return () => {
      montado.current = false
    }
  }, [])

  const capturar = useCallback(() => {
    definirEstado('capturando')
    definirErro(null)
    void localizador
      .capturar()
      .then((posicao) => {
        if (!montado.current) return
        definirCoordenada(posicao)
        definirEstado('capturada')
      })
      .catch((falha: unknown) => {
        if (!montado.current) return
        definirErro(
          falha instanceof ErroDeGeolocalizacao
            ? falha
            : new ErroDeGeolocalizacao('indisponivel', 'GPS indisponível no momento.'),
        )
        definirEstado('falhou')
      })
  }, [localizador])

  useEffect(() => {
    if (automatico) capturar()
  }, [automatico, capturar])

  return { estado, coordenada, erro, capturar }
}
