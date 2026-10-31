/**
 * Implementação do Localizador sobre a Geolocation API do navegador.
 *
 * Usa alta precisão porque as leiras de um mesmo pátio ficam a poucos metros
 * uma da outra e a coordenada entra na trilha de auditoria (RNF01).
 */

import {
  ErroDeGeolocalizacao,
  type Coordenada,
  type Localizador,
} from '@/aplicacao/portas/localizador'

const TIMEOUT_MS = 20_000
/** Aceita uma leitura de até 30 s: o operador anda entre leiras próximas. */
const IDADE_MAXIMA_MS = 30_000

export class LocalizadorDoNavegador implements Localizador {
  capturar(): Promise<Coordenada> {
    if (!('geolocation' in navigator)) {
      return Promise.reject(
        new ErroDeGeolocalizacao(
          'sem_suporte',
          'Este aparelho não oferece GPS ao navegador.',
        ),
      )
    }

    return new Promise<Coordenada>((resolver, rejeitar) => {
      navigator.geolocation.getCurrentPosition(
        (posicao) =>
          resolver({
            latitude: posicao.coords.latitude,
            longitude: posicao.coords.longitude,
            precisaoMetros: Number.isFinite(posicao.coords.accuracy)
              ? Math.round(posicao.coords.accuracy)
              : null,
            capturadoEm: new Date(posicao.timestamp),
          }),
        (falha) => rejeitar(traduzirFalha(falha)),
        {
          enableHighAccuracy: true,
          timeout: TIMEOUT_MS,
          maximumAge: IDADE_MAXIMA_MS,
        },
      )
    })
  }
}

function traduzirFalha(falha: GeolocationPositionError): ErroDeGeolocalizacao {
  switch (falha.code) {
    case falha.PERMISSION_DENIED:
      return new ErroDeGeolocalizacao(
        'permissao_negada',
        'Permissão de localização negada. Libere o GPS para este site nas configurações do navegador.',
      )
    case falha.TIMEOUT:
      return new ErroDeGeolocalizacao(
        'tempo_esgotado',
        'O GPS demorou para responder. Saia de baixo de cobertura e tente novamente.',
      )
    default:
      return new ErroDeGeolocalizacao(
        'indisponivel',
        'GPS indisponível no momento. Ative a localização do aparelho e tente novamente.',
      )
  }
}
