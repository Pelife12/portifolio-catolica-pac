/** Chamadas de autenticação. */

import type { Token, Usuario } from '@/aplicacao/contratos/tipos'
import type { ClienteHttp } from '@/infraestrutura/http/cliente-http'

export class AutenticacaoApi {
  constructor(private readonly http: ClienteHttp) {}

  /** O backend usa OAuth2PasswordRequestForm: e-mail vai no campo `username`. */
  entrar(email: string, senha: string): Promise<Token> {
    return this.http.requisitar<Token>('/auth/login', {
      metodo: 'POST',
      publico: true,
      formulario: { username: email, password: senha },
    })
  }

  eu(): Promise<Usuario> {
    return this.http.requisitar<Usuario>('/auth/eu')
  }
}
