import firebird.driver as fdb
import sys

def decode_trigger_type(t_type):
    phase = "AFTER" if (t_type & 1) else "BEFORE"
    ops = []
    if (t_type & 2) or t_type in [1, 2, 17, 18, 25, 26, 49, 50]: ops.append("INSERT")
    if (t_type & 4) or t_type in [3, 4, 17, 18, 33, 34, 49, 50]: ops.append("UPDATE")
    if (t_type & 8) or t_type in [5, 6, 25, 26, 33, 34, 49, 50]: ops.append("DELETE")
    return f"{phase} {' OR '.join(ops)}"

def get_sync_sql():
    try:
        dev = fdb.connect('base_dev', user='SYSDBA', password='masterkey')
        prod = fdb.connect('base', user='SYSDBA', password='masterkey')
    except Exception as e:
        print(f"/* Erro de conexão: {e} */")
        sys.exit(1)

    with open("update_full_structure.sql", "w") as sql_file:
        sql_file.write("SET TERMINAL ^ ;\n\n")
        cur_dev = dev.cursor()
        cur_prod = prod.cursor()

        # --- 1. COLUNAS (Foco no EVENT_ID para Google Calendar) ---
        print("Sincronizando Colunas...")
        query_cols = """
            select trim(r.rdb$relation_name), trim(f.rdb$field_name)
            from rdb$relation_fields f
            join rdb$relations r on f.rdb$relation_name = r.rdb$relation_name
            where r.rdb$system_flag = 0 and r.rdb$view_blr is null
        """
        cur_dev.execute(query_cols)
        cols_dev = cur_dev.fetchall()
        cur_prod.execute(query_cols)
        cols_prod = set(cur_prod.fetchall())

        for tab, col in cols_dev:
            if (tab, col) not in cols_prod:
                dtype = "VARCHAR(1024)" if col == "EVENT_ID" else "VARCHAR(255)"
                sql_file.write(f"ALTER TABLE {tab} ADD {col} {dtype} ;\n")

        # --- 2. UNIQUE CONSTRAINTS ---
        print("Sincronizando Unique Constraints...")
        query_const = """
            select trim(rdb$constraint_name), trim(rdb$relation_name), trim(rdb$index_name)
            from rdb$relation_constraints 
            where rdb$constraint_type = 'UNIQUE' and rdb$system_flag = 0
        """
        cur_dev.execute(query_const)
        const_dev = cur_dev.fetchall()
        cur_prod.execute(query_const)
        const_prod = {r[0] for r in cur_prod.fetchall()}

        for name, table, idx in const_dev:
            if name not in const_prod:
                # Busca as colunas do índice da constraint
                cur_dev.execute(f"select trim(rdb$field_name) from rdb$index_segments where rdb$index_name = '{idx}'")
                cols = [r[0] for r in cur_dev.fetchall()]
                sql_file.write(f"ALTER TABLE {table} ADD CONSTRAINT {name} UNIQUE ({', '.join(cols)}) ;\n")

        # --- 3. FOREIGN KEYS ---
        print("Sincronizando Foreign Keys...")
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
                cur_dev.execute(f"select trim(rdb$field_name) from rdb$index_segments where rdb$index_name = '{idx}'")
                cols = [r[0] for r in cur_dev.fetchall()]
                cur_dev.execute(f"select trim(rdb$relation_name) from rdb$relation_constraints where rdb$constraint_name = '{ref_const}'")
                ref_table = cur_dev.fetchone()[0]
                sql_file.write(f"ALTER TABLE {table} ADD CONSTRAINT {name} FOREIGN KEY ({', '.join(cols)}) REFERENCES {ref_table} ;\n")

        # --- 4. TRIGGERS ---
        print("Sincronizando Triggers...")
        query_trig = "select trim(rdb$trigger_name), trim(rdb$relation_name), rdb$trigger_sequence, rdb$trigger_type, rdb$trigger_source, rdb$trigger_inactive from rdb$triggers where rdb$system_flag = 0"
        cur_dev.execute(query_trig)
        for name, table, seq, t_type, source, inactive in cur_dev.fetchall():
            status = "INACTIVE" if inactive == 1 else "ACTIVE"
            sql_file.write(f"CREATE OR ALTER TRIGGER {name} FOR {table}\n{status} {decode_trigger_type(t_type)} POSITION {seq}\nAS\n{source}^\n\n")

        sql_file.write("COMMIT ^\nSET TERMINAL ; ^\n")

    dev.close()
    prod.close()
    print("Sucesso: 'update_full_structure.sql' gerado.")

if __name__ == "__main__":
    get_sync_sql()