"""
sync_full_inkers.py
===================
Compara a estrutura do banco Firebird de DESENVOLVIMENTO com o de PRODUÇÃO:
  - Tabelas (novas e removidas)
  - Colunas: novas, removidas e com tipos diferentes
  - Índices (simples, UNIQUE, FK)
  - Stored Procedures e Functions
  - Triggers

Após a comparação, gera um arquivo SQL e APLICA as mudanças no banco de PRODUÇÃO.

Uso:
  python sync_full_inkers.py          <- modo interativo (pergunta antes de aplicar)
  python sync_full_inkers.py --auto   <- aplica automaticamente (para uso em scripts)
"""

import firebird.driver as fdb
import sys
import traceback
import os
from datetime import datetime

# ─── CONFIGURAÇÕES DE CONEXÃO ────────────────────────────────────────────────
DEV_HOST  = "127.0.0.1"
DEV_PATH  = "base_dev"
DEV_USER  = "SYSDBA"
DEV_PASS  = "masterkey"

PROD_HOST = "100.72.176.93"
PROD_PATH = "base"
PROD_USER = "SYSDBA"
PROD_PASS = "masterkey"

SQL_OUTPUT = "update_full_structure.sql"
# ─────────────────────────────────────────────────────────────────────────────


# Mapas em memória para decodificar Charset e Collation ID (serão populados na main)
CHARSETS = {}
COLLATIONS = {}

def load_charsets_and_collations(cur):
    """Carrega mapas de ID -> Nome para Charsets e Collations."""
    global CHARSETS, COLLATIONS
    cur.execute("SELECT rdb$character_set_id, TRIM(rdb$character_set_name) FROM rdb$character_sets")
    CHARSETS = {r[0]: r[1] for r in cur.fetchall()}
    cur.execute("SELECT rdb$collation_id, rdb$character_set_id, TRIM(rdb$collation_name) FROM rdb$collations")
    # Collation ID não é global, é por Charset
    COLLATIONS = {(r[0], r[1]): r[2] for r in cur.fetchall()}

def _charset_collate(charset_id, collate_id):
    """Gera sufixo CHARACTER SET ... COLLATE ... para texto se houver."""
    suffix = ""
    if charset_id is not None:
        cset = CHARSETS.get(charset_id)
        if cset and cset != "NONE":
            suffix += f" CHARACTER SET {cset}"
            if collate_id is not None:
                coll = COLLATIONS.get((collate_id, charset_id))
                # Só coloca COLLATE explícito se for diferente do default do charset
                if coll and coll != cset:
                    suffix += f" COLLATE {coll}"
    return suffix

def fb_type_str(field_type, char_len, field_sub_type, field_precision, field_scale, charset_id=None, collate_id=None):
    """Converte os metadados numéricos de tipo Firebird em string legível."""
    ft = field_type
    if ft == 7:
        if field_scale and field_scale < 0:
            return f"NUMERIC({field_precision or 5},{abs(field_scale)})"
        return "SMALLINT"
    if ft == 8:
        if field_scale and field_scale < 0:
            return f"NUMERIC({field_precision or 10},{abs(field_scale)})"
        return "INTEGER"
    if ft == 10:
        return "FLOAT"
    if ft == 12:
        return "DATE"
    if ft == 13:
        return "TIME"
    if ft == 14:
        return f"CHAR({char_len or 1}){_charset_collate(charset_id, collate_id)}"
    if ft == 16:
        if field_scale and field_scale < 0:
            return f"NUMERIC({field_precision or 18},{abs(field_scale)})"
        return "BIGINT"
    if ft == 27:
        return "DOUBLE PRECISION"
    if ft == 35:
        return "TIMESTAMP"
    if ft == 37:
        return f"VARCHAR({char_len or 255}){_charset_collate(charset_id, collate_id)}"
    if ft == 261:
        sub = field_sub_type or 0
        return f"BLOB SUB_TYPE {sub}"
    return f"UNKNOWN_TYPE_{ft}"


def decode_trigger_type(t_type):
    """Decodifica o tipo de trigger Firebird em string legível."""
    phase = "AFTER" if (t_type & 1) else "BEFORE"
    ops = []
    if t_type in (2, 3, 1, 17, 25, 49) or (t_type & 2):
        ops.append("INSERT")
    if t_type in (4, 5, 3, 18, 26, 50) or (t_type & 4):
        ops.append("UPDATE")
    if t_type in (6, 7, 5, 25, 33, 49) or (t_type & 8):
        ops.append("DELETE")
    # fallback
    if not ops:
        ops.append("INSERT")
    return f"{phase} {' OR '.join(ops)}"


# ─── QUERIES DE METADADOS ─────────────────────────────────────────────────────

QUERY_TABLES = """
    SELECT TRIM(r.rdb$relation_name)
    FROM rdb$relations r
    WHERE r.rdb$system_flag = 0
      AND r.rdb$view_blr IS NULL
    ORDER BY 1
"""

QUERY_COLUMNS = """
    SELECT
        TRIM(r.rdb$relation_name)                          AS tabela,
        TRIM(rf.rdb$field_name)                            AS coluna,
        f.rdb$field_type,
        COALESCE(f.rdb$character_length, 0)                AS char_len,
        COALESCE(f.rdb$field_sub_type, 0)                  AS sub_type,
        COALESCE(f.rdb$field_precision, 0)                 AS fld_precision,
        COALESCE(f.rdb$field_scale, 0)                     AS scale,
        f.rdb$character_set_id                             AS charset_id,
        f.rdb$collation_id                                 AS collate_id,
        COALESCE(rf.rdb$null_flag, 0)                      AS not_null,
        rf.rdb$default_source                              AS default_src,
        rf.rdb$field_position                              AS pos
    FROM rdb$relation_fields rf
    JOIN rdb$relations r   ON rf.rdb$relation_name = r.rdb$relation_name
    JOIN rdb$fields f      ON rf.rdb$field_source  = f.rdb$field_name
    WHERE r.rdb$system_flag = 0
      AND r.rdb$view_blr IS NULL
    ORDER BY 1, rf.rdb$field_position
"""

QUERY_INDEXES = """
    SELECT
        TRIM(i.rdb$index_name)       AS idx_name,
        TRIM(i.rdb$relation_name)    AS tabela,
        COALESCE(i.rdb$unique_flag, 0) AS is_unique,
        TRIM(s.rdb$field_name)       AS coluna,
        COALESCE(s.rdb$field_position, 0) AS pos,
        COALESCE(i.rdb$index_inactive, 0) AS inactive
    FROM rdb$indices i
    JOIN rdb$index_segments s ON i.rdb$index_name = s.rdb$index_name
    JOIN rdb$relations r      ON i.rdb$relation_name = r.rdb$relation_name
    WHERE r.rdb$system_flag = 0
      AND (i.rdb$system_flag IS NULL OR i.rdb$system_flag = 0)
    ORDER BY 1, 5
"""

QUERY_CONSTRAINTS = """
    SELECT
        TRIM(rc.rdb$constraint_name)  AS nome,
        TRIM(rc.rdb$relation_name)    AS tabela,
        TRIM(rc.rdb$constraint_type)  AS tipo,
        TRIM(rc.rdb$index_name)       AS idx
    FROM rdb$relation_constraints rc
    JOIN rdb$relations r ON rc.rdb$relation_name = r.rdb$relation_name
    WHERE r.rdb$system_flag = 0
    ORDER BY 1
"""

QUERY_FK_DETAIL = """
    SELECT
        TRIM(rc.rdb$constraint_name),
        TRIM(rc.rdb$relation_name),
        TRIM(rc.rdb$index_name),
        TRIM(ref.rdb$const_name_uq),
        COALESCE(ref.rdb$update_rule, 'RESTRICT'),
        COALESCE(ref.rdb$delete_rule, 'RESTRICT')
    FROM rdb$relation_constraints rc
    JOIN rdb$ref_constraints ref ON rc.rdb$constraint_name = ref.rdb$constraint_name
    WHERE rc.rdb$constraint_type = 'FOREIGN KEY'
"""

QUERY_PROCEDURES = """
    SELECT
        TRIM(p.rdb$procedure_name)    AS nome,
        TRIM(p.rdb$procedure_source)  AS source,
        p.rdb$procedure_type
    FROM rdb$procedures p
    WHERE (p.rdb$system_flag IS NULL OR p.rdb$system_flag = 0)
    ORDER BY 1
"""

QUERY_PROCS_PARAMS = """
    SELECT
        TRIM(pp.rdb$procedure_name),
        TRIM(pp.rdb$parameter_name),
        pp.rdb$parameter_type,
        f.rdb$field_type,
        COALESCE(f.rdb$character_length, 0),
        COALESCE(f.rdb$field_sub_type, 0),
        COALESCE(f.rdb$field_precision, 0),
        COALESCE(f.rdb$field_scale, 0),
        pp.rdb$parameter_number
    FROM rdb$procedure_parameters pp
    JOIN rdb$fields f ON pp.rdb$field_source = f.rdb$field_name
    ORDER BY pp.rdb$procedure_name, pp.rdb$parameter_type, pp.rdb$parameter_number
"""

QUERY_TRIGGERS = """
    SELECT
        TRIM(t.rdb$trigger_name)       AS nome,
        TRIM(t.rdb$relation_name)      AS tabela,
        t.rdb$trigger_sequence         AS seq,
        t.rdb$trigger_type             AS tipo,
        t.rdb$trigger_source           AS source,
        COALESCE(t.rdb$trigger_inactive, 0) AS inactive
    FROM rdb$triggers t
    WHERE (t.rdb$system_flag IS NULL OR t.rdb$system_flag = 0)
    ORDER BY 1
"""


# ─── FUNÇÕES DE COLETA ───────────────────────────────────────────────────────

def fetch_tables(cur):
    cur.execute(QUERY_TABLES)
    return {r[0] for r in cur.fetchall()}


def fetch_columns(cur):
    """Retorna dict: (tabela, coluna) -> dict com informações completas."""
    cur.execute(QUERY_COLUMNS)
    result = {}
    for row in cur.fetchall():
        tabela, coluna, ft, cl, st, prec, scale, cset_id, coll_id, nn, dflt, pos = row
        type_str = fb_type_str(ft, cl, st, prec, scale, cset_id, coll_id)
        result[(tabela, coluna)] = {
            "type_str": type_str,
            "not_null": nn,
            "default_src": dflt,
            "pos": pos,
            "raw": (ft, cl, st, prec, scale, cset_id, coll_id),
        }
    return result


def fetch_indexes(cur):
    """Retorna dict: idx_name -> {tabela, unique, cols: [...], inactive}."""
    cur.execute(QUERY_INDEXES)
    idxs = {}
    for idx_name, tabela, is_unique, coluna, pos, inactive in cur.fetchall():
        if idx_name not in idxs:
            idxs[idx_name] = {"tabela": tabela, "unique": bool(is_unique),
                               "cols": [], "inactive": bool(inactive)}
        idxs[idx_name]["cols"].append(coluna)
    return idxs


def fetch_constraints(cur):
    """Retorna dict: nome_constraint -> {tabela, tipo, idx}."""
    cur.execute(QUERY_CONSTRAINTS)
    return {r[0]: {"tabela": r[1], "tipo": r[2], "idx": r[3]} for r in cur.fetchall()}


def fetch_fk_details(cur):
    """Retorna dict: fk_name -> {tabela, idx, ref_const, on_update, on_delete}."""
    cur.execute(QUERY_FK_DETAIL)
    return {r[0]: {"tabela": r[1], "idx": r[2], "ref_const": r[3],
                   "on_update": r[4], "on_delete": r[5]} for r in cur.fetchall()}


def fetch_procedures(cur):
    """Retorna dict: proc_name -> {source, type}."""
    cur.execute(QUERY_PROCEDURES)
    procs = {}
    for nome, source, p_type in cur.fetchall():
        procs[nome] = {"source": (source or "").strip(), "type": p_type}
    return procs


def fetch_proc_params(cur):
    """Retorna dict: proc_name -> {input: [...], output: [...]}."""
    cur.execute(QUERY_PROCS_PARAMS)
    params = {}
    for proc, param, p_type, ft, cl, st, prec, scale, num in cur.fetchall():
        if proc not in params:
            params[proc] = {"input": [], "output": []}
        key = "input" if p_type == 0 else "output"
        params[proc][key].append((param, fb_type_str(ft, cl, st, prec, scale)))
    return params


def fetch_triggers(cur):
    """Retorna dict: trig_name -> {tabela, seq, tipo, source, inactive}."""
    cur.execute(QUERY_TRIGGERS)
    trigs = {}
    for nome, tabela, seq, t_type, source, inactive in cur.fetchall():
        trigs[nome] = {
            "tabela": tabela,
            "seq": seq,
            "tipo": t_type,
            "source": (source or "").strip(),
            "inactive": bool(inactive),
        }
    return trigs


def get_idx_cols(cur, idx_name):
    cur.execute(
        "SELECT TRIM(rdb$field_name) FROM rdb$index_segments "
        "WHERE rdb$index_name = ? ORDER BY rdb$field_position",
        [idx_name]
    )
    return [r[0] for r in cur.fetchall()]


# ─── GERAÇÃO DE SQL ──────────────────────────────────────────────────────────

def compare_and_generate(dev_conn, prod_conn, sql_file, report):
    cur_dev  = dev_conn.cursor()
    cur_prod = prod_conn.cursor()

    def log(msg):
        print(msg)
        report.append(msg)

    sql_statements = []

    def emit(sql):
        sql_statements.append(sql)
        sql_file.write(sql + " ^\n\n")

    # ─── TABELAS ─────────────────────────────────────────────────────────────
    log("\n══ TABELAS ══")
    dev_tables  = fetch_tables(cur_dev)
    prod_tables = fetch_tables(cur_prod)

    new_tables     = dev_tables - prod_tables
    removed_tables = prod_tables - dev_tables

    for t in sorted(new_tables):
        log(f"  [+] Tabela nova: {t}")
    for t in sorted(removed_tables):
        log(f"  [-] Tabela removida em DEV (não aplicado): {t}")

    # ─── COLUNAS ─────────────────────────────────────────────────────────────
    log("\n══ COLUNAS ══")
    dev_cols  = fetch_columns(cur_dev)
    prod_cols = fetch_columns(cur_prod)

    new_cols     = set(dev_cols.keys()) - set(prod_cols.keys())
    removed_cols = set(prod_cols.keys()) - set(dev_cols.keys())
    common_cols  = set(dev_cols.keys()) & set(prod_cols.keys())

    # Colunas novas → ADD
    for (tab, col) in sorted(new_cols):
        info   = dev_cols[(tab, col)]
        dtype  = info["type_str"]
        nn     = " NOT NULL" if info["not_null"] else ""
        dflt   = f" {info['default_src']}" if info["default_src"] else ""
        log(f"  [+] {tab}.{col}  ({dtype}{nn}{dflt})")
        emit(f"ALTER TABLE {tab} ADD {col} {dtype}{dflt}{nn}")

    # Colunas removidas → apenas aviso (não remove automaticamente por segurança)
    for (tab, col) in sorted(removed_cols):
        if tab in dev_tables:  # tabela existe em DEV mas coluna sumiu
            log(f"  [-] {tab}.{col} existe em PROD mas não em DEV (não removido — manual)")

    # Colunas com tipos diferentes → ALTER COLUMN
    # Famílias compatíveis para ALTER COLUMN TYPE no Firebird
    _NUMERIC_FAMILY = {"SMALLINT", "INTEGER", "BIGINT"}
    _FLOAT_FAMILY   = {"FLOAT", "DOUBLE PRECISION"}

    def _compatible_alter(dev_t, prod_t):
        """Retorna True se Firebird suporta ALTER COLUMN TYPE entre esses tipos."""
        # Mesma família numérica inteira ou float: ok
        if dev_t in _NUMERIC_FAMILY and prod_t in _NUMERIC_FAMILY:
            return True
        if dev_t in _FLOAT_FAMILY and prod_t in _FLOAT_FAMILY:
            return True
        # VARCHAR ↔ VARCHAR (mesmo tipo base, só muda tamanho): ok
        if dev_t.startswith("VARCHAR") and prod_t.startswith("VARCHAR"):
            return True
        if dev_t.startswith("CHAR") and prod_t.startswith("CHAR"):
            return True
        # NUMERIC(p,s) permanece na família NUMERIC: ok
        if dev_t.startswith("NUMERIC") and prod_t.startswith("NUMERIC"):
            return True
        # Mesmos tipos exatos
        if dev_t == prod_t:
            return True
        return False

    for (tab, col) in sorted(common_cols):
        dev_type  = dev_cols[(tab, col)]["type_str"]
        prod_type = prod_cols[(tab, col)]["type_str"]
        if dev_type != prod_type:
            if _compatible_alter(dev_type, prod_type):
                log(f"  [≠] {tab}.{col}: DEV={dev_type}  PROD={prod_type}  → alterando")
                emit(f"ALTER TABLE {tab} ALTER COLUMN {col} TYPE {dev_type}")
            else:
                log(f"  [!] {tab}.{col}: DEV={dev_type}  PROD={prod_type}  → INCOMPATÍVEL (manual)")
                sql_file.write(
                    f"-- !! ATENÇÃO: {tab}.{col} mudou de {prod_type} para {dev_type}\n"
                    f"-- Conversão direta não suportada pelo Firebird.\n"
                    f"-- Procedimento manual:\n"
                    f"--   1. ALTER TABLE {tab} ADD {col}_NEW {dev_type} ^\n"
                    f"--   2. UPDATE {tab} SET {col}_NEW = {col} ^\n"
                    f"--   3. ALTER TABLE {tab} DROP {col} ^\n"
                    f"--   4. ALTER TABLE {tab} ALTER {col}_NEW TO {col} ^\n\n"
                )

    # ─── CONSTRAINTS (UNIQUE & FK) ────────────────────────────────────────────
    log("\n══ CONSTRAINTS ══")
    dev_const  = fetch_constraints(cur_dev)
    prod_const = fetch_constraints(cur_prod)
    dev_fk     = fetch_fk_details(cur_dev)

    for name, info in sorted(dev_const.items()):
        if name in prod_const:
            continue
        tipo   = info["tipo"]
        tabela = info["tabela"]
        idx    = info["idx"]

        if tipo == "UNIQUE":
            cols = get_idx_cols(cur_dev, idx)
            log(f"  [+] UNIQUE {name} em {tabela} ({', '.join(cols)})")
            emit(f"ALTER TABLE {tabela} ADD CONSTRAINT {name} UNIQUE ({', '.join(cols)})")

        elif tipo == "PRIMARY KEY":
            cols = get_idx_cols(cur_dev, idx)
            log(f"  [+] PRIMARY KEY {name} em {tabela} ({', '.join(cols)})")
            emit(f"ALTER TABLE {tabela} ADD CONSTRAINT {name} PRIMARY KEY ({', '.join(cols)})")

        elif tipo == "FOREIGN KEY":
            fk = dev_fk.get(name)
            if fk:
                cols = get_idx_cols(cur_dev, idx)
                # Descobrir tabela referenciada
                # Descobrir tabela referenciada e o índice usado na constraint correspondente
                cur_dev.execute(
                    "SELECT TRIM(rdb$relation_name), TRIM(rdb$index_name) FROM rdb$relation_constraints "
                    "WHERE rdb$constraint_name = ?", [fk["ref_const"]]
                )
                ref_res = cur_dev.fetchone()
                if ref_res:
                    ref_table = ref_res[0]
                    ref_idx = ref_res[1]
                    ref_cols = get_idx_cols(cur_dev, ref_idx)
                    
                    # strip() corrige espaços extras retornados pelo Firebird nos metadados
                    on_del = (fk["on_delete"] or "").strip()
                    on_upd = (fk["on_update"] or "").strip()
                    # Firebird não aceita RESTRICT como keyword DDL (equivale ao NO ACTION)
                    _skip = {"RESTRICT", "NO ACTION", ""}
                    cascade_del = f" ON DELETE {on_del}" if on_del not in _skip else ""
                    cascade_upd = f" ON UPDATE {on_upd}" if on_upd not in _skip else ""
                    log(f"  [+] FK {name}: {tabela} ({', '.join(cols)}) → {ref_table} ({', '.join(ref_cols)})")
                    
                    emit(
                        f"ALTER TABLE {tabela} ADD CONSTRAINT {name} "
                        f"FOREIGN KEY ({', '.join(cols)}) REFERENCES {ref_table} ({', '.join(ref_cols)})"
                        f"{cascade_del}{cascade_upd}"
                    )

    # ─── ÍNDICES SIMPLES ─────────────────────────────────────────────────────
    log("\n══ ÍNDICES ══")
    dev_idxs  = fetch_indexes(cur_dev)
    prod_idxs = fetch_indexes(cur_prod)

    # Excluir índices que são PK/FK/UNIQUE (gerenciados como constraints)
    constraint_idx_dev  = {v["idx"] for v in dev_const.values() if v["idx"]}
    constraint_idx_prod = {v["idx"] for v in prod_const.values() if v["idx"]}

    for idx_name, info in sorted(dev_idxs.items()):
        if idx_name in constraint_idx_dev:
            continue  # já tratado como constraint
        if idx_name not in prod_idxs:
            cols    = ", ".join(info["cols"])
            unique  = "UNIQUE " if info["unique"] else ""
            tabela  = info["tabela"]
            if info["unique"]:
                log(f"  [+] INDEX UNIQUE {idx_name} em {tabela} ({cols})  ⚠ exige dados sem duplicatas!")
            else:
                log(f"  [+] INDEX {idx_name} em {tabela} ({cols})")
            emit(f"CREATE {unique}INDEX {idx_name} ON {tabela} ({cols})")
        else:
            # Verifica se colunas ou unique mudaram
            pi = prod_idxs[idx_name]
            if info["cols"] != pi["cols"] or info["unique"] != pi["unique"]:
                log(f"  [≠] INDEX {idx_name} mudou — recriando")
                emit(f"DROP INDEX {idx_name}")
                unique = "UNIQUE " if info["unique"] else ""
                emit(f"CREATE {unique}INDEX {idx_name} ON {info['tabela']} ({', '.join(info['cols'])})")

    # ─── STORED PROCEDURES ───────────────────────────────────────────────────
    log("\n══ STORED PROCEDURES / FUNCTIONS ══")
    dev_procs  = fetch_procedures(cur_dev)
    prod_procs = fetch_procedures(cur_prod)
    dev_params = fetch_proc_params(cur_dev)

    for proc_name, pinfo in sorted(dev_procs.items()):
        params    = dev_params.get(proc_name, {"input": [], "output": []})
        in_params = ", ".join(f"{n} {t}" for n, t in params["input"])
        out_params = ", ".join(f"{n} {t}" for n, t in params["output"])
        source    = pinfo["source"]

        out_clause = f"\nRETURNS ({out_params})" if out_params else ""

        if proc_name not in prod_procs:
            log(f"  [+] PROCEDURE nova: {proc_name}")
        else:
            prod_src = prod_procs[proc_name]["source"]
            # Normaliza espaços para comparação
            if source.replace("\r\n", "\n").strip() == prod_src.replace("\r\n", "\n").strip():
                continue
            log(f"  [≠] PROCEDURE alterada: {proc_name}")

        emit(
            f"CREATE OR ALTER PROCEDURE {proc_name} ({in_params}){out_clause}\n"
            f"AS\n{source}"
        )

    # ─── TRIGGERS ────────────────────────────────────────────────────────────
    log("\n══ TRIGGERS ══")
    dev_trigs  = fetch_triggers(cur_dev)
    prod_trigs = fetch_triggers(cur_prod)

    for trig_name, tinfo in sorted(dev_trigs.items()):
        source  = tinfo["source"]
        tabela  = tinfo["tabela"]
        seq     = tinfo["seq"]
        t_type  = tinfo["tipo"]
        status  = "INACTIVE" if tinfo["inactive"] else "ACTIVE"
        t_str   = decode_trigger_type(t_type)

        if trig_name not in prod_trigs:
            log(f"  [+] TRIGGER nova: {trig_name} em {tabela}")
        else:
            pt = prod_trigs[trig_name]
            prod_src = pt["source"]
            # Compara source e configurações
            if (source.replace("\r\n", "\n").strip() == prod_src.replace("\r\n", "\n").strip()
                    and tinfo["seq"] == pt["seq"] and tinfo["tipo"] == pt["tipo"]
                    and tinfo["inactive"] == pt["inactive"]):
                continue
            log(f"  [≠] TRIGGER alterada: {trig_name}")

        emit(
            f"CREATE OR ALTER TRIGGER {trig_name} FOR {tabela}\n"
            f"{status} {t_str} POSITION {seq}\nAS\n{source}"
        )

    return sql_statements


def apply_to_production(prod_conn, sql_statements, report):
    """Aplica cada statement no banco de produção."""
    log_fn = lambda m: (print(m), report.append(m))
    log_fn("\n══ APLICANDO NO BANCO DE PRODUÇÃO ══")

    if not sql_statements:
        log_fn("  Nenhuma alteração para aplicar.")
        return

    cur = prod_conn.cursor()
    errors = []

    for i, stmt in enumerate(sql_statements, 1):
        preview = stmt.strip()[:80].replace("\n", " ")
        try:
            cur.execute(stmt)
            prod_conn.commit()
            print(f"  [{i}/{len(sql_statements)}] OK → {preview}...")
        except Exception as e:
            prod_conn.rollback()
            msg = f"  [{i}/{len(sql_statements)}] ERRO → {preview}...\n    Detalhe: {e}"
            print(msg)
            report.append(msg)
            errors.append((stmt, str(e)))

    if errors:
        log_fn(f"\n  ⚠️  {len(errors)} erro(s) encontrado(s) durante aplicação.")
    else:
        log_fn(f"\n  ✅ Todos os {len(sql_statements)} statement(s) aplicados com sucesso!")


# ─── MAIN ────────────────────────────────────────────────────────────────────

def main():
    # --auto: aplica sem perguntar (para uso em shell scripts)
    auto_apply = "--auto" in sys.argv

    dev  = None
    prod = None
    report = []

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n{'='*60}")
    print(f"  SYNC FIREBIRD — DEV → PROD")
    print(f"  {timestamp}")
    print(f"  DEV : {DEV_HOST}/{DEV_PATH}")
    print(f"  PROD: {PROD_HOST}/{PROD_PATH}")
    print(f"{'='*60}\n")

    # firebird.driver aceita DSN no formato "host:database_path"
    dev_dsn  = f"{DEV_HOST}:{DEV_PATH}"
    prod_dsn = f"{PROD_HOST}:{PROD_PATH}"

    try:
        print("Conectando ao banco de DESENVOLVIMENTO...")
        dev = fdb.connect(dev_dsn, user=DEV_USER, password=DEV_PASS)
        print("Conectando ao banco de PRODUÇÃO...")
        prod = fdb.connect(prod_dsn, user=PROD_USER, password=PROD_PASS)
        print("Conexões estabelecidas com sucesso.\n")

        # Carrega os mapas de charset e collation de DEV para gerar SQL correto
        load_charsets_and_collations(dev.cursor())
    except Exception as e:
        print(f"ERRO DE CONEXÃO: {e}")
        traceback.print_exc()
        sys.exit(1)

    try:
        with open(SQL_OUTPUT, "w", encoding="utf-8") as sql_file:
            sql_file.write(f"-- Gerado em: {timestamp}\n")
            sql_file.write(f"-- DEV:  {DEV_HOST}/{DEV_PATH}\n")
            sql_file.write(f"-- PROD: {PROD_HOST}/{PROD_PATH}\n\n")
            sql_file.write("SET TERM ^ ;\n\n")

            sql_statements = compare_and_generate(dev, prod, sql_file, report)

            sql_file.write("COMMIT ^\n")
            sql_file.write("SET TERM ; ^\n")

        print(f"\n  Arquivo SQL gerado: '{SQL_OUTPUT}' ({len(sql_statements)} alterações)")

        if sql_statements:
            if auto_apply:
                print("\n  Modo automático (--auto): aplicando alterações no banco de PRODUÇÃO...")
                apply_to_production(prod, sql_statements, report)
            else:
                print("\n  Deseja aplicar as alterações no banco de PRODUÇÃO? [s/N]: ", end="", flush=True)
                resp = input().strip().lower()
                if resp == "s":
                    apply_to_production(prod, sql_statements, report)
                else:
                    print("  Aplicação cancelada. O arquivo SQL foi gerado para revisão manual.")
        else:
            print("  ✅ Bancos já estão sincronizados — nenhuma diferença encontrada!")

        # Salva relatório em arquivo de texto
        report_file = SQL_OUTPUT.replace(".sql", "_report.txt")
        with open(report_file, "w", encoding="utf-8") as rf:
            rf.write(f"Relatório de Sincronização — {timestamp}\n")
            rf.write("=" * 60 + "\n")
            rf.write("\n".join(report))
        print(f"\n  Relatório salvo em: '{report_file}'")

    except Exception as e:
        print(f"\nERRO CRÍTICO: {e}")
        traceback.print_exc()
        sys.exit(1)
    finally:
        if dev:
            dev.close()
        if prod:
            prod.close()
        print("\nConexões encerradas.\n")


if __name__ == "__main__":
    main()