import psycopg2

DATABASE_URL = 'postgres://postgres.buhdppagggxwwxsqcuhv:5NEWjL98UyxNpEBA@aws-0-us-west-1.pooler.supabase.com:5432/postgres'

def test_database_connection():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        print("Connected successfully!")
        conn.close()
    except psycopg2.OperationalError as e:
        print("Connection failed:", e)

if __name__ == "__main__":
    test_database_connection()
