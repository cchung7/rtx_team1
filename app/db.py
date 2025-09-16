import os, pathlib, sys
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from dotenv import load_dotenv

ROOT = pathlib.Path(__file__).resolve().parents[1]
SQL_DIR = ROOT / "sql"

def get_db_url() -> str:
    load_dotenv()
    return os.getenv("DB_URL", "sqlite:///data/aqi.sqlite")

def get_engine() -> Engine:
    return create_engine(get_db_url(), pool_pre_ping=True, future=True)

def engine_flavor(engine: Engine) -> str:
    name = engine.url.get_backend_name()  
    return "mysql" if "mysql" in name else "sqlite"

def read_sql(path: pathlib.Path) -> str:
    return path.read_text(encoding="utf-8")

def apply_sql(engine: Engine, sql_text: str) -> None:
    stmts = [s.strip() for s in sql_text.split(";") if s.strip()]
    with engine.begin() as conn:
        for s in stmts:
            conn.exec_driver_sql(s)

def init():
    eng = get_engine()
    flavor = engine_flavor(eng)
    schema = SQL_DIR / ( "schema.mysql.sql" if flavor == "mysql" else "schema.sqlite.sql" )
    if not schema.exists():
        print(f"[init] missing schema: {schema}", file=sys.stderr)
        sys.exit(1)
    print(f"[init] Applying {flavor.upper()} schema -> {eng.url}")
    apply_sql(eng, read_sql(schema))
    print("[init] Done.")

if __name__ == "__main__":
    cmd = (sys.argv[1] if len(sys.argv) > 1 else "init").lower()
    if cmd == "init":
        init()
    else:
        print("Usage: python -m app.db init")
