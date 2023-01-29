from datetime import datetime
from flask import Flask, request, render_template, redirect, send_file, url_for
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os
from werkzeug.utils import secure_filename

app = Flask(__name__, template_folder='templates', static_folder='static')

# Configuration for the PostgreSQL database
DATABASE_URI = 'postgresql://postgres:chetan@127.0.0.1:5432/badges'

# Function to initialize the database and create the table


def init_db():
    conn = psycopg2.connect(DATABASE_URI)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS badges (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            description TEXT NOT NULL,
            badge_file VARCHAR(255) NOT NULL,
            eligible_students TEXT NOT NULL
        );
    """)
    cur.close()
    conn.close()

# Route to handle the form submission for uploading a badge


@app.route('/badge/upload', methods=['GET', 'POST'])
def upload_badge():
    if request.method == 'POST':
        badge_name = request.form['badge_name']
        badge_description = request.form['badge_description']
        eligible_students = request.form['eligible_students']
        badge_file = request.files['badge_file']
        filename = secure_filename(badge_file.filename)
        badge_file.save(os.path.join('static/badges', filename))
        conn = psycopg2.connect(DATABASE_URI)
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO badges (name, description, badge_file, eligible_students)
            VALUES (%s, %s, %s, %s);
        """, (badge_name, badge_description, filename, eligible_students))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('list_badges'))
    return render_template('index.html')

# Route to list all the badges


@app.route('/badge/list')
def list_badges():
    conn = psycopg2.connect(DATABASE_URI)
    cur = conn.cursor()
    cur.execute("SELECT * FROM badges;")
    badges = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('list_badges.html', badges=badges)

# Route to handle the API endpoint for verifying a badge


@app.route('/badge/verify')
def verify_badge():
    badge_name = request.args.get('name')
    email = request.args.getlist('email')
    email = email[0].split(",")[0]
    conn = psycopg2.connect(DATABASE_URI)
    cur = conn.cursor()
    cur.execute("""
        SELECT * FROM badges WHERE name=%s;
        """, (badge_name,))
    badge = cur.fetchone()
    cur.close()
    conn.close()
    if not badge:
        return 'Badge not found', 403
    if email not in badge[4].split(','):
        return 'Unauthorized', 403
    return send_file(os.path.join('static/badges', str(datetime.now())+badge[3]), mimetype='image/png')


# Route for the "edit_badge" function to display the badge details for editing
@app.route('/badge/edit/<int:badge_id>', methods=['GET', 'POST'])
def edit_badge(badge_id):
    if request.method == 'POST':
        badge_name = request.form['badge_name']
        badge_description = request.form['badge_description']
        eligible_students = request.form['eligible_students']
        badge_file = request.files.get('badge_file')
        if badge_file:
            filename = secure_filename(badge_file.filename)
            badge_file.save(os.path.join('static/badges',
                            str(datetime.now())+filename))
        else:
            conn = psycopg2.connect(DATABASE_URI)
            cur = conn.cursor()
            cur.execute(
                "SELECT badge_file FROM badges WHERE id=%s", (badge_id,))
            filename = cur.fetchone()[0]
            cur.close()
            conn.close()
        conn = psycopg2.connect(DATABASE_URI)
        cur = conn.cursor()
        cur.execute("""
            UPDATE badges
            SET name=%s, description=%s, badge_file=%s, eligible_students=%s
            WHERE id=%s;
        """, (badge_name, badge_description, filename, eligible_students, badge_id))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('list_badges'))
    conn = psycopg2.connect(DATABASE_URI)
    cur = conn.cursor()
    cur.execute("SELECT * FROM badges WHERE id=%s", (badge_id,))
    badge = cur.fetchone()
    cur.close()
    conn.close()
    return render_template('edit.html', badge=badge)

# Route to delete a badge


@app.route('/badge/delete/<int:badge_id>')
def delete_badge(badge_id):
    conn = psycopg2.connect(DATABASE_URI)
    cur = conn.cursor()
    cur.execute("""
        DELETE FROM badges WHERE id=%s;
    """, (badge_id,))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('list_badges'))


@app.route('/')
def index():
    return redirect(url_for('list_badges'))


if __name__ == '__main__':
    init_db()
    app.run(host='127.0.0.1', port=8082, debug=False)
