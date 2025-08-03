from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)
DB_NAME = 'keuangan.db'

def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS catatan (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tanggal TEXT NOT NULL,
                keterangan TEXT NOT NULL,
                jumlah REAL NOT NULL,
                tipe TEXT CHECK(tipe IN ('Pemasukan', 'Pengeluaran')) NOT NULL
            )
        ''')

@app.route('/')
def index():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT * FROM catatan ORDER BY tanggal DESC")
    catatan = cur.fetchall()
    conn.close()
    return render_template('index.html', catatan=catatan)

@app.route('/tambah', methods=['GET', 'POST'])
def tambah():
    if request.method == 'POST':
        data = (
            request.form['tanggal'],
            request.form['keterangan'],
            float(request.form['jumlah']),
            request.form['tipe']
        )
        conn = sqlite3.connect(DB_NAME)
        conn.execute("INSERT INTO catatan (tanggal, keterangan, jumlah, tipe) VALUES (?, ?, ?, ?)", data)
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    return render_template('form.html', action="Tambah", catatan=None)

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    if request.method == 'POST':
        data = (
            request.form['tanggal'],
            request.form['keterangan'],
            float(request.form['jumlah']),
            request.form['tipe'],
            id
        )
        conn.execute("UPDATE catatan SET tanggal=?, keterangan=?, jumlah=?, tipe=? WHERE id=?", data)
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    cur.execute("SELECT * FROM catatan WHERE id=?", (id,))
    catatan = cur.fetchone()
    conn.close()
    return render_template('form.html', action="Edit", catatan=catatan)

@app.route('/hapus/<int:id>')
def hapus(id):
    conn = sqlite3.connect(DB_NAME)
    conn.execute("DELETE FROM catatan WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

# Chartpage route
@app.route('/chart')
def chart():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    # Ambil total pemasukan & pengeluaran per bulan
    cur.execute('''
        SELECT 
            strftime('%Y-%m', tanggal) as bulan,
            SUM(CASE WHEN tipe = 'Pemasukan' THEN jumlah ELSE 0 END) as pemasukan,
            SUM(CASE WHEN tipe = 'Pengeluaran' THEN jumlah ELSE 0 END) as pengeluaran
        FROM catatan
        GROUP BY bulan
        ORDER BY bulan
    ''')
    data = cur.fetchall()
    conn.close()

    labels = [d[0] for d in data]
    pemasukan = [d[1] for d in data]
    pengeluaran = [d[2] for d in data]
    return render_template('chart.html', labels=labels, pemasukan=pemasukan, pengeluaran=pengeluaran)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
