import { usarTema } from '@/ui/hooks/usar-tema'

import { Icone } from './Icone'

export function AlternadorDeTema() {
  const { tema, alternar } = usarTema()
  const proximo = tema === 'claro' ? 'escuro' : 'claro'

  return (
    <button
      type="button"
      className="botao botao--secundario"
      style={{ width: 44, minHeight: 44, padding: 0, borderRadius: 'var(--raio-interno)' }}
      onClick={alternar}
      aria-label={`Mudar para o tema ${proximo}`}
      title={`Tema ${proximo}`}
    >
      <Icone nome={tema === 'claro' ? 'lua' : 'sol'} tamanho={18} />
    </button>
  )
}
