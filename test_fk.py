import firebird.driver as fdb

def get_col_type(dsn, table, col):
    try:
        conn = fdb.connect(dsn, user='SYSDBA', password='masterkey')
        cur = conn.cursor()
        cur.execute(f"""
            select 
                f.rdb$field_type, 
                f.rdb$character_length,
                f.rdb$character_set_id,
                f.rdb$collation_id
            from rdb$relation_fields rf
            join rdb$fields f on rf.rdb$field_source = f.rdb$field_name
            where trim(rf.rdb$relation_name) = '{table}' and trim(rf.rdb$field_name) = '{col}'
        """)
        res = cur.fetchone()
        conn.close()
        return res
    except Exception as e:
        return str(e)

print("DEV:")
print("LOJA.ID_LOJA_EX:", get_col_type("127.0.0.1:base_dev", "LOJA", "ID_LOJA_EX"))
print("DESPESAS.ID_LOJA_EX:", get_col_type("127.0.0.1:base_dev", "DESPESAS", "ID_LOJA_EX"))

print("\nPROD:")
print("LOJA.ID_LOJA_EX:", get_col_type("100.72.176.93:base", "LOJA", "ID_LOJA_EX"))
print("DESPESAS.ID_LOJA_EX:", get_col_type("100.72.176.93:base", "DESPESAS", "ID_LOJA_EX"))
