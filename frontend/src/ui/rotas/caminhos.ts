/** Caminhos em um só lugar: nenhuma tela escreve URL literal. */

export const CAMINHOS = {
  login: '/entrar',
  leiras: '/leiras',
  novaLeira: '/leiras/nova',
  leira: (leiraId = ':leiraId') => `/leiras/${leiraId}`,
  novaAfericao: (leiraId = ':leiraId') => `/leiras/${leiraId}/afericao`,
  afericaoRegistrada: (leiraId = ':leiraId') => `/leiras/${leiraId}/afericao/registrada`,
  painel: '/painel',
  alertas: '/alertas',
} as const
