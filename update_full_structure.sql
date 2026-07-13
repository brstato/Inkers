-- Gerado em: 2026-07-02 18:19:28
-- DEV:  127.0.0.1/base_dev
-- PROD: 100.72.176.93/base

SET TERM ^ ;

-- !! ATENÇÃO: DESPESAS.VALOR mudou de FLOAT para NUMERIC(15,2)
-- Conversão direta não suportada pelo Firebird.
-- Procedimento manual:
--   1. ALTER TABLE "DESPESAS" ADD "VALOR_NEW" NUMERIC(15,2) ^
--   2. UPDATE "DESPESAS" SET "VALOR_NEW" = "VALOR" ^
--   3. ALTER TABLE "DESPESAS" DROP "VALOR" ^
--   4. ALTER TABLE "DESPESAS" ALTER "VALOR_NEW" TO "VALOR" ^

ALTER TABLE "VENDA" ADD CONSTRAINT "VENDA_CAIXA_FK" FOREIGN KEY ("ID_CAIXA") REFERENCES "CAIXA" ("ID") ^

CREATE OR ALTER PROCEDURE SP_BUSCA_DADOS_CLIENTE (P_TELEFONE VARCHAR(30))
RETURNS (CLIENTE_ID INTEGER, CLIENTE_NOME VARCHAR(100), PROFISSIONAL_ID INTEGER, PROFISSIONAL_NOME VARCHAR(100), LOJA_UUID VARCHAR(38), CONFIG_HORARIO BLOB SUB_TYPE 0, AGENDA_ID INTEGER, AGENDA_DATA TIMESTAMP, AGENDA_HORA_INI VARCHAR(30), AGENDA_HORA_FIM VARCHAR(30))
AS
BEGIN
    FOR
        SELECT 
            C.ID,
            C.NOME,
            P.ID,
            P.NOME,
            P.ID_LOJA_EX,
            L.CONFIG_HORARIO,
            A.ID,
            A.DATA2,
            A.HORA_INI,
            A.HORA_FIM
        FROM CLIENTES C
        -- 1. O índice CLIENTES_TELEFONE_IDX garante um acesso inicial imediato.
        -- 2. O índice CLIENTES_PROFISSIONAIS_FK liga rapidamente ao profissional.
        LEFT JOIN PROFISSIONAIS P ON C.PROFISSIONAL = P.ID
        -- 3. O índice UNQ1_LOJA na tabela LOJA faz a junção instantânea.
        LEFT JOIN LOJA L ON P.ID_LOJA_EX = L.UUID
        -- 4. Junção com a Agenda otimizada para usar o índice IDX_DATA2:
        LEFT JOIN AGENDA A ON P.ID = A.COD_FUNC 
                          -- Compara o TIMESTAMP puro com o limite de dias sem usar CAST
                          AND A.DATA2 >= CURRENT_DATE 
                          AND A.DATA2 < DATEADD(31 DAY TO CURRENT_DATE)
                          -- Evita o COALESCE() que também pode prejudicar índices:
                          AND (A.FLAG <> 'D' OR A.FLAG IS NULL)
        WHERE C.TELEFONE = :P_TELEFONE
        INTO 
            :CLIENTE_ID,
            :CLIENTE_NOME,
            :PROFISSIONAL_ID,
            :PROFISSIONAL_NOME,
            :LOJA_UUID,
            :CONFIG_HORARIO,
            :AGENDA_ID,
            :AGENDA_DATA,
            :AGENDA_HORA_INI,
            :AGENDA_HORA_FIM
    DO
    BEGIN
        SUSPEND;
    END
END ^

CREATE OR ALTER PROCEDURE SP_DESPESAS (P_DESCRICAO VARCHAR(30), P_STATUS VARCHAR(30), P_VALOR_PARCELA NUMERIC(15,2), P_QTD_PARCELAS INTEGER, P_FORMA_PAGAMENTO VARCHAR(30), P_DATA_PRIMEIRO_VENCIMENTO TIMESTAMP, P_ID_LOJA_EX VARCHAR(38))
AS
DECLARE VARIABLE I INTEGER;
DECLARE VARIABLE V_DATA_VENCIMENTO TIMESTAMP;
DECLARE VARIABLE V_DESCRICAO_PARCELA VARCHAR(30);
BEGIN
    -- Proteção contra loop infinito ou 0
    IF (:P_QTD_PARCELAS <= 0) THEN P_QTD_PARCELAS = 1;

    I = 1;

    WHILE (I <= :P_QTD_PARCELAS) DO
    BEGIN
        -- Calcula a data: Data Inicial + (I - 1) meses
        -- Ex: Mês 1 soma 0 meses. Mês 2 soma 1 mês, etc.
        V_DATA_VENCIMENTO = DATEADD(MONTH, I - 1, :P_DATA_PRIMEIRO_VENCIMENTO);

        -- Formata o texto "1 de 12", "2 de 12"
        V_DESCRICAO_PARCELA = CAST(I AS VARCHAR(5)) || ' de ' || CAST(:P_QTD_PARCELAS AS VARCHAR(5));

        INSERT INTO DESPESAS (
            DESCRICAO,
            PARCELA,
            VALOR,           -- Insere o valor cheio passado por parâmetro
            FORMA_PAGAMENTO,
            STATUS,
            DATA_VENCIMENTO,
            ID_LOJA_EX
        ) VALUES (
            :P_DESCRICAO,
            :V_DESCRICAO_PARCELA,
            :P_VALOR_PARCELA,
            :P_FORMA_PAGAMENTO,
            :P_STATUS,
            :V_DATA_VENCIMENTO,
            :P_ID_LOJA_EX
        );

        I = I + 1;
    END
END ^

CREATE OR ALTER PROCEDURE SP_LISTAR_DESPESAS_MES (P_ID_LOJA VARCHAR(38), P_DATA_INI DATE, P_DATA_FIM DATE)
RETURNS (R_ID INTEGER, R_DESCRICAO VARCHAR(30), R_VALOR NUMERIC(15,2), R_DATA_VENCIMENTO TIMESTAMP, R_STATUS VARCHAR(30), R_PARCELA VARCHAR(30), R_TOTAL_GERAL NUMERIC(15,2), R_ORIGEM VARCHAR(20))
AS
BEGIN
    -- O 'FOR SELECT' itera sobre os resultados linha a linha
    FOR 
        SELECT 
            ID, 
            DESCRICAO, 
            VALOR, 
            DATA_VENCIMENTO, 
            STATUS, 
            PARCELA,
            
            -- Window Function: Calcula a soma de TUDO que foi filtrado abaixo
            SUM(VALOR) OVER() AS TOTAL_GERAL,
            
            -- Define a origem (Resíduo ou Mês Atual)
            IIF(DATA_VENCIMENTO < :P_DATA_INI, 'RESIDUO', 'MES_ATUAL') AS ORIGEM
            
        FROM DESPESAS
        WHERE 
            ID_LOJA_EX = :P_ID_LOJA
            AND (
                -- Caso 1: Pertence ao período solicitado (P_DATA_INI até P_DATA_FIM)
                (DATA_VENCIMENTO >= :P_DATA_INI AND DATA_VENCIMENTO < :P_DATA_FIM AND STATUS <> 'PAGO')
                
                OR
                
                -- Caso 2: É antigo (menor que P_DATA_INI) mas está ABERTO (Resíduo)
				(
                    STATUS = 'ABERTO' 
                    AND DATA_VENCIMENTO < :P_DATA_INI 
                    AND (CURRENT_DATE >= :P_DATA_INI AND CURRENT_DATE < :P_DATA_FIM)
                )
            )
        ORDER BY 
            DATA_VENCIMENTO ASC
            
        INTO 
            :R_ID, 
            :R_DESCRICAO, 
            :R_VALOR, 
            :R_DATA_VENCIMENTO, 
            :R_STATUS, 
            :R_PARCELA, 
            :R_TOTAL_GERAL, 
            :R_ORIGEM
    DO
    BEGIN
        -- Devolve a linha processada para a aplicação
        SUSPEND;
    END
END ^

CREATE OR ALTER PROCEDURE SP_RESUMO_FINANCEIRO (P_ID_LOJA VARCHAR(38))
RETURNS (R_ANO INTEGER, R_MES INTEGER, R_TOTAL_PAGO NUMERIC(15,2), R_TOTAL_A_PAGAR NUMERIC(15,2), R_TOTAL_GERAL NUMERIC(15,2))
AS
BEGIN
  -- O comando FOR executa o SELECT e joga os valores nas variáveis de saída (R_...)
  FOR 
    SELECT 
        EXTRACT(YEAR FROM DATA_VENCIMENTO),
        EXTRACT(MONTH FROM DATA_VENCIMENTO),
        
        -- Soma Condicional (IIF é nativo no FB 3.0+)
        COALESCE(SUM(IIF(STATUS = 'PAGO', VALOR, 0)), 0),
        COALESCE(SUM(IIF(STATUS = 'ABERTO', VALOR, 0)), 0),
        COALESCE(SUM(VALOR), 0)
        
    FROM DESPESAS
    WHERE 
        ID_LOJA_EX = :P_ID_LOJA
        
        -- Lógica da Janela de Datas (-12 meses e +12 meses)
        AND DATA_VENCIMENTO >= DATEADD(MONTH, -6, DATEADD(DAY, 1 - EXTRACT(DAY FROM CURRENT_DATE), CURRENT_DATE))
        AND DATA_VENCIMENTO < DATEADD(MONTH, 7, DATEADD(DAY, 1 - EXTRACT(DAY FROM CURRENT_DATE), CURRENT_DATE))
        AND STATUS <> 'PAGO'
        
    GROUP BY 
        EXTRACT(YEAR FROM DATA_VENCIMENTO), 
        EXTRACT(MONTH FROM DATA_VENCIMENTO)
    ORDER BY 
        1 ASC, 2 ASC
        
    INTO 
        :R_ANO, 
        :R_MES, 
        :R_TOTAL_PAGO, 
        :R_TOTAL_A_PAGAR, 
        :R_TOTAL_GERAL
  DO
  BEGIN
    -- SUSPEND "devolve" a linha atual para o Lazarus e continua o loop
    SUSPEND;
  END
END ^

COMMIT ^
SET TERM ; ^
