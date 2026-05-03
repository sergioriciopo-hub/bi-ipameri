// ═══════════════════════════════════════════════════════════════════════════
// ÁGUAS DE IPAMERI – Power BI | Queries M (Advanced Editor)
// Cole cada bloco no Advanced Editor da respectiva tabela no Power Query
// Caminho dos arquivos: ajuste BASE_PATH conforme sua máquina
// ═══════════════════════════════════════════════════════════════════════════

// ── PARÂMETRO BASE_PATH ──────────────────────────────────────────────────────
// Criar em: Gerenciar Parâmetros → Novo Parâmetro
// Nome: BASE_PATH
// Tipo: Texto
// Valor padrão: C:\Users\SérgioRiciopo\AGUAS DE IPAMERI\03 COMERCIAL - Documentos\01 - Projetos e Propostas\Claude\BI_Ipameri\data\


// ═══════════════════════════════════════════════════════════════════════════
// TABELA: Faturamento
// ═══════════════════════════════════════════════════════════════════════════
let
    Source = Parquet.Document(File.Contents(BASE_PATH & "faturamento.parquet")),
    #"Tipo corrigido" = Table.TransformColumnTypes(Source, {
        {"dt_ref", type datetime},
        {"vl_agua", type number}, {"vl_esgoto", type number},
        {"vl_lixo", type number}, {"vl_servico", type number},
        {"vl_total_faturado", type number}, {"volume_m3", type number},
        {"qt_fatura", Int64.Type}, {"nr_economia", Int64.Type}
    }),
    #"Ano" = Table.AddColumn(#"Tipo corrigido", "Ano", each Date.Year([dt_ref]), Int64.Type),
    #"Mês Num" = Table.AddColumn(#"Ano", "Mês Num", each Date.Month([dt_ref]), Int64.Type),
    #"Mês Nome" = Table.AddColumn(#"Mês Num", "Mês Nome", each Date.ToText([dt_ref], "MMM/yy", "pt-BR")),
    #"Trimestre" = Table.AddColumn(#"Mês Nome", "Trimestre", each "T" & Text.From(Number.RoundUp(Date.Month([dt_ref]) / 3))),
    #"Semestre" = Table.AddColumn(#"Trimestre", "Semestre", each if Date.Month([dt_ref]) <= 6 then "S1" else "S2")
in
    #"Semestre"


// ═══════════════════════════════════════════════════════════════════════════
// TABELA: Arrecadacao
// ═══════════════════════════════════════════════════════════════════════════
let
    Source = Parquet.Document(File.Contents(BASE_PATH & "arrecadacao.parquet")),
    #"Tipo corrigido" = Table.TransformColumnTypes(Source, {
        {"dt_ref", type datetime},
        {"vl_agua", type number}, {"vl_esgoto", type number},
        {"vl_lixo", type number}, {"vl_servico", type number},
        {"vl_total_arrecadado", type number}
    }),
    #"Ano" = Table.AddColumn(#"Tipo corrigido", "Ano", each Date.Year([dt_ref]), Int64.Type),
    #"Mês Num" = Table.AddColumn(#"Ano", "Mês Num", each Date.Month([dt_ref]), Int64.Type)
in
    #"Mês Num"


// ═══════════════════════════════════════════════════════════════════════════
// TABELA: PainelArrecadacao
// ═══════════════════════════════════════════════════════════════════════════
let
    Source = Parquet.Document(File.Contents(BASE_PATH & "painel_arrecadacao.parquet")),
    #"Tipo corrigido" = Table.TransformColumnTypes(Source, {
        {"dt_pagamento", type datetime}, {"dt_ref", type datetime},
        {"vl_pagamento", type number}, {"vl_tarifa", type number},
        {"qt_documentos", Int64.Type}, {"qt_pagamentos", Int64.Type}
    }),
    #"Data Pagamento" = Table.AddColumn(#"Tipo corrigido", "Data", each DateTime.Date([dt_pagamento]), type date),
    #"Ano" = Table.AddColumn(#"Data Pagamento", "Ano", each Date.Year([dt_pagamento]), Int64.Type),
    #"Mês" = Table.AddColumn(#"Ano", "Mês Num", each Date.Month([dt_pagamento]), Int64.Type)
in
    #"Mês"


// ═══════════════════════════════════════════════════════════════════════════
// TABELA: Inadimplencia
// ═══════════════════════════════════════════════════════════════════════════
let
    Source = Parquet.Document(File.Contents(BASE_PATH & "pendencia_atual.parquet")),
    #"Tipo corrigido" = Table.TransformColumnTypes(Source, {
        {"dt_ref_documento", type datetime}, {"dt_vencimento", type datetime},
        {"vl_divida", type number}, {"nr_dias_atraso", Int64.Type}
    }),
    #"Corte Pendente Texto" = Table.AddColumn(#"Tipo corrigido", "Corte Pendente",
        each if [fl_corte_pendente] = true then "Sim" else "Não"),
    #"Aviso Vencido Texto" = Table.AddColumn(#"Corte Pendente Texto", "Aviso Vencido",
        each if [fl_aviso_vencido] = true then "Sim" else "Não")
in
    #"Aviso Vencido Texto"


// ═══════════════════════════════════════════════════════════════════════════
// TABELA: Cortes
// ═══════════════════════════════════════════════════════════════════════════
let
    Source = Parquet.Document(File.Contents(BASE_PATH & "cortes.parquet")),
    #"Tipo corrigido" = Table.TransformColumnTypes(Source, {
        {"dt_solicitacao", type datetime}, {"dt_limite_execucao", type datetime},
        {"dt_fim_execucao", type datetime}, {"dt_vencimento_aviso", type datetime},
        {"vl_pendencia_atual", type number}, {"vl_total_aviso_debito", type number},
        {"qt_servico", Int64.Type}, {"qt_tempo_execucao", Int64.Type}
    }),
    #"Fora Prazo Texto" = Table.AddColumn(#"Tipo corrigido", "Fora Prazo",
        each if [fl_fora_prazo] = true then "Sim" else "Não"),
    #"Tempo Horas" = Table.AddColumn(#"Fora Prazo Texto", "Tempo Execução (h)",
        each if [qt_tempo_execucao] <> null then Number.Round([qt_tempo_execucao] / 60, 1) else null, type number)
in
    #"Tempo Horas"


// ═══════════════════════════════════════════════════════════════════════════
// TABELA: Religacoes
// ═══════════════════════════════════════════════════════════════════════════
let
    Source = Parquet.Document(File.Contents(BASE_PATH & "religacoes.parquet")),
    #"Tipo corrigido" = Table.TransformColumnTypes(Source, {
        {"dt_corte", type datetime}, {"dt_reliagacao", type datetime},
        {"dias_corte_religacao", Int64.Type}
    })
in
    #"Tipo corrigido"


// ═══════════════════════════════════════════════════════════════════════════
// TABELA: Servicos
// ═══════════════════════════════════════════════════════════════════════════
let
    Source = Parquet.Document(File.Contents(BASE_PATH & "servicos.parquet")),
    #"Tipo corrigido" = Table.TransformColumnTypes(Source, {
        {"dt_solicitacao", type datetime}, {"dt_limite_execucao", type datetime},
        {"dt_fim_execucao", type datetime}, {"dt_cancelamento", type datetime},
        {"qt_servico", Int64.Type}, {"qt_tempo_execucao", Int64.Type},
        {"qt_tempo_deslocamento", Int64.Type}
    }),
    #"Fora Prazo" = Table.AddColumn(#"Tipo corrigido", "Status SLA",
        each if [fl_fora_prazo] = true then "Fora do Prazo" else "No Prazo"),
    #"Tempo Horas" = Table.AddColumn(#"Fora Prazo", "Tempo Execução (h)",
        each if [qt_tempo_execucao] <> null then Number.Round([qt_tempo_execucao] / 60, 1) else null, type number)
in
    #"Tempo Horas"


// ═══════════════════════════════════════════════════════════════════════════
// TABELA: Leituras
// ═══════════════════════════════════════════════════════════════════════════
let
    Source = Parquet.Document(File.Contents(BASE_PATH & "leituras.parquet")),
    #"Tipo corrigido" = Table.TransformColumnTypes(Source, {
        {"dt_ref", type datetime},
        {"qt_leitura", Int64.Type}, {"qt_volume_lido", Int64.Type},
        {"qt_volume_faturado", Int64.Type}
    }),
    #"Crítica Texto" = Table.AddColumn(#"Tipo corrigido", "Leitura Crítica",
        each if [fl_critica] = true then "Sim" else "Não"),
    #"Erro Texto" = Table.AddColumn(#"Crítica Texto", "Erro Leitura",
        each if [fl_erro_leitura] = 1 then "Sim" else "Não")
in
    #"Erro Texto"


// ═══════════════════════════════════════════════════════════════════════════
// TABELA: Backlog
// ═══════════════════════════════════════════════════════════════════════════
let
    Source = Parquet.Document(File.Contents(BASE_PATH & "backlog_servicos.parquet")),
    #"Tipo corrigido" = Table.TransformColumnTypes(Source, {
        {"dt_ref", type datetime}, {"dt_solicitacao", type datetime},
        {"qt_solicitado", Int64.Type}, {"qt_executado", Int64.Type},
        {"qt_cancelado", Int64.Type}, {"qt_pendente", Int64.Type}
    })
in
    #"Tipo corrigido"


// ═══════════════════════════════════════════════════════════════════════════
// TABELA CALENDÁRIO (criar como nova consulta em branco)
// ═══════════════════════════════════════════════════════════════════════════
let
    DataInicio = #date(2023, 1, 1),
    DataFim    = Date.From(DateTime.LocalNow()),
    QtdDias    = Duration.Days(DataFim - DataInicio) + 1,
    ListaDatas = List.Dates(DataInicio, QtdDias, #duration(1, 0, 0, 0)),
    Tabela     = Table.FromList(ListaDatas, Splitter.SplitByNothing(), {"Data"}),
    #"Tipo Data" = Table.TransformColumnTypes(Tabela, {{"Data", type date}}),
    #"Ano"      = Table.AddColumn(#"Tipo Data",    "Ano",         each Date.Year([Data]),                          Int64.Type),
    #"Mês Num"  = Table.AddColumn(#"Ano",          "Mês Num",     each Date.Month([Data]),                         Int64.Type),
    #"Mês Nome" = Table.AddColumn(#"Mês Num",      "Mês",         each Date.ToText([Data], "MMMM", "pt-BR")),
    #"Mês Abrev"= Table.AddColumn(#"Mês Nome",     "Mês Abrev",   each Date.ToText([Data], "MMM", "pt-BR")),
    #"Trimestre"= Table.AddColumn(#"Mês Abrev",    "Trimestre",   each "T" & Text.From(Number.RoundUp(Date.Month([Data]) / 3))),
    #"Semestre" = Table.AddColumn(#"Trimestre",    "Semestre",    each if Date.Month([Data]) <= 6 then "1º Semestre" else "2º Semestre"),
    #"AnoMês"   = Table.AddColumn(#"Semestre",     "AnoMês",      each Text.From(Date.Year([Data])) & "-" & Text.PadStart(Text.From(Date.Month([Data])), 2, "0")),
    #"AnoMêsNm" = Table.AddColumn(#"AnoMês",       "AnoMês Nome", each Text.PadStart(Text.From(Date.Month([Data])), 2, "0") & "/" & Text.From(Date.Year([Data]))),
    #"DiaSemana"= Table.AddColumn(#"AnoMêsNm",     "Dia Semana",  each Date.DayOfWeekName([Data], "pt-BR")),
    #"Dia"      = Table.AddColumn(#"DiaSemana",    "Dia",         each Date.Day([Data]),                           Int64.Type),
    #"É Hoje"   = Table.AddColumn(#"Dia",          "É Hoje",      each [Data] = Date.From(DateTime.LocalNow()),    type logical)
in
    #"É Hoje"
