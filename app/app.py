from flask import Flask, render_template, request
import pandas as pd
import mysql.connector
app = Flask(__name__)

@app.route('/')
def home():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT lrn, name FROM students")
    students = cursor.fetchall()

    total = len(students)

    cursor.close()
    conn.close()

    return render_template("index.html", students=students, total=total)

def get_metrics():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM students")
    total = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    return total


@app.route('/upload', methods=['POST'])
def upload():
    try:
        file = request.files['file']

        if not file:
            return "No file uploaded"

        
        df = pd.read_excel(file, header=None)

       
        df = df.rename(columns={
            0: 'LRN',     
            2: 'NAME',    
            3: 'SEX'      
        })

       
        df = df[['LRN', 'NAME', 'SEX']]

     
        df = df.dropna(subset=['LRN'])

       
        df = df[df['LRN'].astype(str).str.isnumeric()]

        print("\n===== CLEAN DATA =====")
        print(df.head(10))

       
        conn = get_db_connection()
        cursor = conn.cursor()

        inserted = 0

        
        for _, row in df.iterrows():
            lrn = str(row['LRN']).strip()
            name = str(row['NAME']).strip()
            gender = str(row['SEX']).strip().upper()

            
            if gender.startswith('M'):
                gender = 'MALE'
            elif gender.startswith('F'):
                gender = 'FEMALE'
            else:
                gender = 'UNKNOWN'

            print("INSERTING:", lrn, name, gender)

           
            cursor.execute("""
                INSERT IGNORE INTO students (lrn, name)
                VALUES (%s, %s)
            """, (lrn, name))

           
            cursor.execute("""
                INSERT INTO student_records (lrn, school_year, grade_level, gender, status)
                VALUES (%s, %s, %s, %s, %s)
            """, (lrn, "2025-2026", 10, gender, "ENROLLED"))

            inserted += 1

        conn.commit()
        cursor.close()
        conn.close()

        return f"{inserted} students imported successfully!"

    except Exception as e:
        print("\nERROR:", str(e))
        return f"Error occurred: {str(e)}"

def get_db_connection():
    return mysql.connector.connect(
        host="db",   
        user="root",
        password="root",
        database="mydb"
    )