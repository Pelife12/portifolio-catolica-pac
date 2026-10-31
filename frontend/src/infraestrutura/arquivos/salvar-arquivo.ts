/** Entrega um arquivo gerado (o laudo em PDF) para o usuário salvar ou abrir. */

export function salvarArquivo(arquivo: Blob, nomeDoArquivo: string): void {
  const url = URL.createObjectURL(arquivo)
  const ancora = document.createElement('a')
  ancora.href = url
  ancora.download = nomeDoArquivo
  ancora.rel = 'noopener'
  document.body.appendChild(ancora)
  ancora.click()
  ancora.remove()
  // Dá tempo ao navegador de iniciar o download antes de liberar a memória.
  setTimeout(() => URL.revokeObjectURL(url), 30_000)
}
