from sqlalchemy import text
from app.core.db import engine

def upgrade():
    with engine.begin() as conn:
        conn.execute(text("ALTER TABLE events ADD COLUMN classification VARCHAR(50) DEFAULT 'Public' NOT NULL;"))
        print("Migration applied successfully.")

if __name__ == '__main__':
    upgrade()
