/** Mapa de rotas da aplicação. */

import { Navigate, Route, Routes } from 'react-router-dom'

import { CascaDoApp } from '@/ui/layout/CascaDoApp'
import { Leiras } from '@/ui/paginas/Leiras'
import { Login } from '@/ui/paginas/Login'

import { CAMINHOS } from './caminhos'
import { RotaProtegida } from './RotaProtegida'

export function Rotas() {
  return (
    <Routes>
      <Route path={CAMINHOS.login} element={<Login />} />

      <Route element={<RotaProtegida />}>
        <Route element={<CascaDoApp />}>
          <Route path={CAMINHOS.leiras} element={<Leiras />} />
        </Route>
      </Route>

      {/* A lista de leiras é a casa do operador. */}
      <Route path="*" element={<Navigate to={CAMINHOS.leiras} replace />} />
    </Routes>
  )
}
