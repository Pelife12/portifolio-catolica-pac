/** Chaves do React Query em um só lugar, para invalidação consistente. */

export const chaves = {
  usuarioAtual: ['usuario-atual'] as const,
  leiras: (usinaId?: string) => ['leiras', usinaId ?? 'todas'] as const,
  leira: (leiraId: string) => ['leira', leiraId] as const,
  composicao: (leiraId: string) => ['leira', leiraId, 'composicao'] as const,
  residuos: ['residuos'] as const,
  afericoes: (leiraId?: string) => ['afericoes', leiraId ?? 'todas'] as const,
  alertas: (leiraId?: string, status?: string) =>
    ['alertas', leiraId ?? 'todas', status ?? 'todos'] as const,
}
