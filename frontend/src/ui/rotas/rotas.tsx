/** Mapa de rotas da aplicação. */

import { Navigate, Route, Routes } from 'react-router-dom'

import { CascaDoApp } from '@/ui/layout/CascaDoApp'
import { AfericaoRegistrada } from '@/ui/paginas/AfericaoRegistrada'
import { FilaDeEnvio } from '@/ui/paginas/FilaDeEnvio'
import { Alertas } from '@/ui/paginas/Alertas'
import { HistoricoDaLeira } from '@/ui/paginas/HistoricoDaLeira'
import { Leiras } from '@/ui/paginas/Leiras'
import { Login } from '@/ui/paginas/Login'
import { NaoEncontrada } from '@/ui/paginas/NaoEncontrada'
import { NovaAfericao } from '@/ui/paginas/NovaAfericao'
import { NovaLeira } from '@/ui/paginas/NovaLeira'
import { Painel } from '@/ui/paginas/Painel'

import { CAMINHOS } from './caminhos'
import { RotaProtegida } from './RotaProtegida'

export function Rotas() {
  return (
    <Routes>
      <Route path={CAMINHOS.login} element={<Login />} />
      {/* A lista de leiras é a casa do operador. */}
      <Route path="/" element={<Navigate to={CAMINHOS.leiras} replace />} />

      <Route element={<RotaProtegida />}>
        <Route element={<CascaDoApp />}>
          <Route path={CAMINHOS.leiras} element={<Leiras />} />
          {/* Rota estática antes da dinâmica: /leiras/nova não é um id. */}
          <Route path={CAMINHOS.novaLeira} element={<NovaLeira />} />
          <Route path={CAMINHOS.leira()} element={<HistoricoDaLeira />} />
          <Route path={CAMINHOS.novaAfericao()} element={<NovaAfericao />} />
          <Route path={CAMINHOS.afericaoRegistrada()} element={<AfericaoRegistrada />} />
          <Route path={CAMINHOS.painel} element={<Painel />} />
          <Route path={CAMINHOS.alertas} element={<Alertas />} />
          <Route path={CAMINHOS.fila} element={<FilaDeEnvio />} />
          {/* Sem sessão, a RotaProtegida leva ao login antes de chegar aqui. */}
          <Route path="*" element={<NaoEncontrada />} />
        </Route>
      </Route>
    </Routes>
  )
}
