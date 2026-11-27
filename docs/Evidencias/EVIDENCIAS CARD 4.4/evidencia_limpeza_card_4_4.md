vidência — Card 4.4: saneamento de registros de teste em public.triagens

Responsável (banco): Maria Eduarda · Revisor: Lucas Maciel Projeto Supabase: Triagem para Todos (produção) · Execução: 22/11/2026, 19:58 UTC

Antes

2026-11-22 19:56:59 UTC — 223 linhas, 0 protocolos nulos, 0 duplicados, última triagem em 14/11/2026 14:22:43 UTC.

Exclusão controlada (somente os 2 protocolos citados no guia)
sql
DELETE FROM public.triagens
WHERE protocolo IN ('TRG-2026-f0d90ce1', 'TRG-2026-705f2198')
RETURNING id_triagem, protocolo, data_triagem, usuario_id, servico, periodo, solicitacao_dados;
protocolo	data_triagem (UTC)	paciente	serviço / período
TRG-2026-f0d90ce1	12/11/2026 20:17:14	Teste Mobile Testonio	tratamento_geral / vespertino
TRG-2026-705f2198	14/11/2026 14:22:43	Teste Silva	tratamento_geral / vespertino

Os dados completos das duas linhas ficaram no retorno do DELETE (id_triagem, usuario_id e solicitacao_dados), caso seja preciso restaurar.

Depois

2026-11-22 19:58:45 UTC

Verificação	Resultado
Linhas na tabela	221
Protocolos nulos	0
Protocolos duplicados	0
Protocolos citados no guia ainda presentes	0
Triagens órfãs (sem usuário)	0
Última triagem	09/10/2026 17:08:18 UTC
Índice	CREATE UNIQUE INDEX idx_triagem_protocolo ON public.triagens USING btree (protocolo)
Coluna protocolo	NOT NULL
Situação final da tabela (conferida em 23/11/2026 pelo revisor e em 25/11/2026)

Depois da exclusão acima, ficaram na tabela 219 registros da massa sintética do Card 1.3 (contas @example.com) e 2 registros de testes manuais de abril:

TRG-2026-02d34b08 ("Teste Mobile", 30/04);
TRG-2026-e1775456 ("bananovski", 30/04).

Esses 2 registros de abril foram removidos depois. A base final tem 219 linhas, todas da massa sintética, com 0 nulos, 0 duplicados, 0 órfãs, protocolo NOT NULL e o índice único idx_triagem_protocolo ativo. As contas fecham: 221 (depois da exclusão acima) − 2 (testes de abril) = 219.

A massa sintética de 219 registros pode ser apagada depois, com confirmação do grupo, se for necessário entregar a base zerada.
