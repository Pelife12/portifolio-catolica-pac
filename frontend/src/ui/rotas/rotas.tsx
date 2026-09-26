/** Mapa de rotas da aplicação. */

import { Navigate, Route, Routes } from 'react-router-dom'

import { CascaDoApp } from '@/ui/layout/CascaDoApp'
import { Leiras } from '@/ui/paginas/Leiras'
import { Login } from '@/ui/paginas/Login'
import { AfericaoRegistrada } from '@/ui/paginas/AfericaoRegistrada'
import { NovaAfericao } from '@/ui/paginas/NovaAfericao'
import { NovaLeira } from '@/ui/paginas/NovaLeira'

import { CAMINHOS } from './caminhos'
import { RotaProtegida } from './RotaProtegida'

export function Rotas() {
  return (
    <Routes>
      <Route path={CAMINHOS.login} element={<Login />} />

      <Route element={<RotaProtegida />}>
        <Route element={<CascaDoApp />}>
          <Route path={CAMINHOS.leiras} element={<Leiras />} />
          <Route path={CAMINHOS.novaLeira} element={<NovaLeira />} />
          <Route path={CAMINHOS.novaAfericao()} element={<NovaAfericao />} />
          <Route path={CAMINHOS.afericaoRegistrada()} element={<AfericaoRegistrada />} />
        </Route>
      </Route>

      {/* A lista de leiras é a casa do operador. */}
      <Route path="*" element={<Navigate to={CAMINHOS.leiras} replace />} />
    </Routes>
  )
}
