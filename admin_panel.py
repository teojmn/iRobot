from flask import Flask, render_template_string, jsonify
import csv
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EMPRUNTS_CSV = os.path.join(BASE_DIR, "emprunts.csv")
CASIERS_CSV = os.path.join(BASE_DIR, "casiers.csv")

app = Flask(__name__)

def read_csv(path):
    if not os.path.exists(path):
        return []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)

@app.route("/")
def index():
    return render_template_string("""
    <html>
    <head>
      <title>Admin Panel</title>
      <style>
        body {
          font-family: Arial, sans-serif;
          background: #f4f6f8;
          margin: 0;
          padding: 20px;
        }
        h1 {
          color: #2c3e50;
          margin-bottom: 30px;
        }
        h2 {
          color: #34495e;
          margin-top: 40px;
        }
        table {
          border-collapse: collapse;
          width: 80%;
          margin-bottom: 30px;
          background: #fff;
          box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        }
        th, td {
          border: 1px solid #dfe6e9;
          padding: 10px 16px;
          text-align: left;
        }
        th {
          background: #2980b9;
          color: #fff;
        }
        tr:nth-child(even) {
          background: #f2f6fa;
        }
        .plein {
          background: #27ae60;
          color: #fff;
          font-weight: bold;
          text-align: center;
        }
        .vide {
          background: #c0392b;
          color: #fff;
          font-weight: bold;
          text-align: center;
        }
      </style>
      <script>
        function updateTables() {
          fetch('/data')
            .then(response => response.json())
            .then(data => {
              // Casiers
              let casiersRows = '';
              data.casiers.forEach(function(c) {
                let plein = ['true', '1', 'yes'].includes(c.statut.toLowerCase());
                casiersRows += `<tr>
                  <td>${c.id_casier}</td>
                  <td class="${plein ? 'plein' : 'vide'}">${plein ? 'Plein' : 'Vide'}</td>
                </tr>`;
              });
              document.getElementById('casiers_body').innerHTML = casiersRows;

              // Emprunts
              let empruntsRows = '';
              data.emprunts.forEach(function(e) {
                empruntsRows += `<tr>
                  <td>${e.id_emprunt || ''}</td>
                  <td>${e.mail || ''}</td>
                  <td>${e.id_casier || ''}</td>
                  <td>${e.date || ''}</td>
                  <td>${e.heure || ''}</td>
                  <td>${e.statut || ''}</td>
                </tr>`;
              });
              document.getElementById('emprunts_body').innerHTML = empruntsRows;
            });
        }
        setInterval(updateTables, 2000);
        window.onload = updateTables;
      </script>
    </head>
    <body>
    <h1>Admin Panel</h1>
    <h2>Casiers</h2>
    <table>
      <tr><th>ID Casier</th><th>Statut</th></tr>
      <tbody id="casiers_body"></tbody>
    </table>
    <h2>Emprunts</h2>
    <table>
      <tr>
        <th>ID Emprunt</th><th>Mail</th><th>ID Casier</th><th>Date</th><th>Heure</th><th>Statut</th>
      </tr>
      <tbody id="emprunts_body"></tbody>
    </table>
    </body>
    </html>
    """)

@app.route("/data")
def data():
    casiers = read_csv(CASIERS_CSV)
    emprunts = read_csv(EMPRUNTS_CSV)
    return jsonify({"casiers": casiers, "emprunts": emprunts})

if __name__ == "__main__":
    app.run(debug=True)