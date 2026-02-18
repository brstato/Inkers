import firebird.driver as fdb
import sys
import traceback

def decode_trigger_type(t_type):
    phase = "AFTER" if (t_type & 1) else "BEFORE"
    ops = []
    if (t_type & 2) or t_type in [1, 2, 17, 18, 25, 26, 49, 50]: ops.append("INSERT")
    if (t_type & 4) or t_type in [3, 4, 17, 18, 33, 34, 49, 50]: ops.append("UPDATE")
    if (t_type & 8) or t_type in [5, 6, 25, 26, 33, 34, 49, 50]: ops.append("DELETE")
    return f"{phase} {' OR '.join(ops)}"

def get_sync_sql():
    dev = None
    prod = None
    try:
        try:
            print("Conectando aos bancos...")
            # Ajuste os IPs conforme necessário
            dev = fdb.connect('localhost:base_dev', user='SYSDBA', password='masterkey')
            prod = fdb.connect('100.72.176.93:base', user='SYSDBA', password='masterkey')
        except Exception as e:
            print(f"/* Erro de conexão: {e} */")
            traceback.print_exc()
            sys.exit(1)

        with open("update_full_structure.sql", "w") as sql_file:
            # Importante: SET TERM para evitar erros de terminador
            sql_file.write("SET TERM ^ ;\n\n")
            cur_dev = dev.cursor()
            cur_prod = prod.cursor()

            # --- 1. MAPEAMENTO DE TIPOS INTELIGENTE ---
            print("Analisando estrutura e tipos de dados...")
            sys.stdout.flush()
            
            # Esta query busca o tipo REAL do campo no banco de desenvolvimento
            query_meta = """
                select 
                    trim(r.rdb$relation_name), 
                    trim(rf.rdb$field_name),
                    CASE f.rdb$field_type
                        WHEN 7 THEN 'SMALLINT'
                        WHEN 8 THEN 'INTEGER'
                        WHEN 10 THEN 'FLOAT'
                        WHEN 12 THEN 'DATE'
                        WHEN 13 THEN 'TIME'
                        WHEN 14 THEN 'CHAR(' || f.rdb$character_length || ')'
                        WHEN 16 THEN 'BIGINT'
                        WHEN 27 THEN 'DOUBLE PRECISION'
                        WHEN 35 THEN 'TIMESTAMP'
                        WHEN 37 THEN 'VARCHAR(' || f.rdb$character_length || ')'
                        WHEN 261 THEN 'BLOB SUB_TYPE ' || f.rdb$field_sub_type
                        ELSE 'VARCHAR(255)'
                    END as field_def
                from rdb$relation_fields rf
                join rdb$relations r on rf.rdb$relation_name = r.rdb$relation_name
                join rdb$fields f on rf.rdb$field_source = f.rdb$field_name
                where r.rdb$system_flag = 0 and r.rdb$view_blr is null
            """
            
            # Pega estrutura do DEV
            cur_dev.execute(query_meta)
            # Mapa: (Tabela, Coluna) -> "TIPO DE DADO" (Ex: INTEGER, BLOB SUB_TYPE 1, etc)
            dev_struct = {(r[0], r[1]): r[2] for r in cur_dev.fetchall()}
            
            # Pega estrutura do PROD (apenas para saber o que existe)
            cur_prod.execute(query_meta)
            prod_existing = {(r[0], r[1]) for r in cur_prod.fetchall()}

            # --- GERAÇÃO DOS ALTER TABLE (COLUNAS) ---
            for (tab, col), dtype in dev_struct.items():
                if (tab, col) not in prod_existing:
                    print(f"   -> Criando {tab}.{col} como {dtype}")
                    # Agora ele usa o DTYPE real (ex: BLOB ou INTEGER)
                    sql_file.write(f"ALTER TABLE {tab} ADD {col} {dtype} ^\n")

            # --- 2. UNIQUE CONSTRAINTS ---
            print("Sincronizando Unique Constraints...")
            query_const = """
                select trim(rc.rdb$constraint_name), trim(rc.rdb$relation_name), trim(rc.rdb$index_name)
                from rdb$relation_constraints rc
                join rdb$relations r on rc.rdb$relation_name = r.rdb$relation_name
                where rc.rdb$constraint_type = 'UNIQUE' and r.rdb$system_flag = 0
            """
            cur_dev.execute(query_const)
            const_dev = cur_dev.fetchall()
            cur_prod.execute(query_const)
            const_prod = {r[0] for r in cur_prod.fetchall()}

            for name, table, idx in const_dev:
                if name not in const_prod:
                    cur_dev.execute(f"select trim(rdb$field_name) from rdb$index_segments where rdb$index_name = '{idx}'")
                    cols = [r[0] for r in cur_dev.fetchall()]
                    sql_file.write(f"ALTER TABLE {table} ADD CONSTRAINT {name} UNIQUE ({', '.join(cols)}) ^\n")

            # --- 3. FOREIGN KEYS ---
            print("Sincronizando Foreign Keys...")
            # Nota: Agora as FKs vão funcionar porque os tipos das colunas (criadas acima) estarão corretos
            query_fk = """
                select trim(rc.rdb$constraint_name), trim(rc.rdb$relation_name), 
                       trim(rc.rdb$index_name), trim(ref.rdb$const_name_uq)
                from rdb$relation_constraints rc
                join rdb$ref_constraints ref on rc.rdb$constraint_name = ref.rdb$constraint_name
                where rc.rdb$constraint_type = 'FOREIGN KEY'
            """
            cur_dev.execute(query_fk)
            fks_dev = cur_dev.fetchall()
            cur_prod.execute(query_fk)
            fks_prod = {r[0] for r in cur_prod.fetchall()}

            for name, table, idx, ref_const in fks_dev:
                if name not in fks_prod:
                    try:
                        cur_dev.execute(f"select trim(rdb$field_name) from rdb$index_segments where rdb$index_name = '{idx}'")
                        cols = [r[0] for r in cur_dev.fetchall()]
                        
                        cur_dev.execute(f"select trim(rdb$relation_name) from rdb$relation_constraints where rdb$constraint_name = '{ref_const}'")
                        res_ref = cur_dev.fetchone()
                        if res_ref:
                            ref_table = res_ref[0]
                            sql_file.write(f"ALTER TABLE {table} ADD CONSTRAINT {name} FOREIGN KEY ({', '.join(cols)}) REFERENCES {ref_table} ^\n")
                    except Exception as e:
                        print(f"Erro FK {name}: {e}")

            # --- 4. TRIGGERS ---
            print("Sincronizando Triggers...")
            query_trig = "select trim(rdb$trigger_name), trim(rdb$relation_name), rdb$trigger_sequence, rdb$trigger_type, rdb$trigger_source, rdb$trigger_inactive from rdb$triggers where rdb$system_flag = 0"
            cur_dev.execute(query_trig)
            for name, table, seq, t_type, source, inactive in cur_dev.fetchall():
                status = "INACTIVE" if inactive == 1 else "ACTIVE"
                # Usa CREATE OR ALTER para garantir atualização
                sql_file.write(f"CREATE OR ALTER TRIGGER {name} FOR {table}\n{status} {decode_trigger_type(t_type)} POSITION {seq}\nAS\n{source}^\n\n")

            # Finalização correta
            sql_file.write("COMMIT ^\n")
            sql_file.write("SET TERM ; ^\n")

        print("Sucesso: 'update_full_structure.sql' gerado com tipos corretos.")

    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        traceback.print_exc()
        sys.exit(1)
    finally:
        if dev: dev.close()
        if prod: prod.close()

if __name__ == "__main__":
    get_sync_sql()