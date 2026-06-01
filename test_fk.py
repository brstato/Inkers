import firebird.driver as fdb
import os
from dotenv import load_dotenv
load_dotenv()

def get_col_type(dsn, table, col):
    try:
        user = os.getenv('DEV_USER', 'SYSDBA')
        password = os.getenv('DEV_PASS', 'masterkey')
        conn = fdb.connect(dsn, user=user, password=password)
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

dev_host = os.getenv('DEV_HOST', '127.0.0.1')
dev_path = os.getenv('DEV_PATH', 'base_dev')
prod_host = os.getenv('PROD_HOST', '100.72.176.93')
prod_path = os.getenv('PROD_PATH', 'base')

print("DEV:")
print("LOJA.ID_LOJA_EX:", get_col_type(f"{dev_host}:{dev_path}", "LOJA", "ID_LOJA_EX"))
print("DESPESAS.ID_LOJA_EX:", get_col_type(f"{dev_host}:{dev_path}", "DESPESAS", "ID_LOJA_EX"))

print("\nPROD:")
print("LOJA.ID_LOJA_EX:", get_col_type(f"{prod_host}:{prod_path}", "LOJA", "ID_LOJA_EX"))
print("DESPESAS.ID_LOJA_EX:", get_col_type(f"{prod_host}:{prod_path}", "DESPESAS", "ID_LOJA_EX"))
