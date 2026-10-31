/** Rota inexistente: diz o que aconteceu em vez de redirecionar em silêncio. */

import { Link } from 'react-router-dom'

import { EstadoVazio } from '@/ui/componentes/EstadoVazio'
import { CAMINHOS } from '@/ui/rotas/caminhos'

export function NaoEncontrada() {
  return (
    <EstadoVazio
      icone="alerta"
      titulo="Página não encontrada"
      acao={
        <Link className="botao" to={CAMINHOS.leiras}>
          Voltar às leiras
        </Link>
      }
    >
      O endereço pode ter mudado ou a leira pode ter sido removida.
    </EstadoVazio>
  )
}
