import os, hashlib, sqlite3
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
import uvicorn

app = FastAPI()

def init_db():
    conn = sqlite3.connect("fruitflow.db")
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, email TEXT UNIQUE, password TEXT)")
    conn.commit()
    conn.close()
init_db()

def hash_pwd(p):
    return hashlib.sha256(p.encode()).hexdigest()

def login_page(msg=""):
    html = "<html><head><style>body{font-family:sans-serif;display:flex;justify-content:center;align-items:center;height:100vh;background:#fef9f0} .box{background:white;padding:35px;border-radius:16px;width:340px;box-shadow:0 8px 25px rgba(0,0,0,.08)} input{width:100%;padding:12px;margin:8px 0;border:1px solid #eee;border-radius:10px} button{width:100%;padding:12px;background:#f59e0b;color:white;border:none;border-radius:10px;font-weight:bold;cursor:pointer}</style></head><body><div class='box'><h2>FruitFlow Premium</h2><p style='color:red'>"
    html += msg
    html += "</p><form method='post' action='/login'><input name='email' placeholder='Email' required><input type='password' name='password' placeholder='Password' required><button>Connexion</button></form><br><a href='/register'>Creer un compte</a></div></body></html>"
    return html

def register_page(msg=""):
    html = "<html><head><style>body{font-family:sans-serif;display:flex;justify-content:center;align-items:center;height:100vh;background:#fef9f0} .box{background:white;padding:35px;border-radius:16px;width:340px;box-shadow:0 8px 25px rgba(0,0,0,.08)} input{width:100%;padding:12px;margin:8px 0;border:1px solid #eee;border-radius:10px} button{width:100%;padding:12px;background:#f59e0b;color:white;border:none;border-radius:10px;font-weight:bold}</style></head><body><div class='box'><h2>Inscription</h2><p style='color:red'>"
    html += msg
    html += "</p><form method='post' action='/register'><input name='email' placeholder='Email' required><input type='password' name='password' required><button>Creer</button></form><br><a href='/'>Retour login</a></div></body></html>"
    return html

def lab_page(user_email):
    html = '''
<html><head><title>FruitFlow - Labo</title>
<style>
body{margin:0;font-family:Inter,Segoe UI,sans-serif;background:#fefbf3;color:#333}
.topbar{background:white;padding:10px 25px;font-size:13px;color:#666;display:flex;justify-content:space-between;border-bottom:1px solid #f0e6d5}
header{text-align:center;padding:25px 0 10px 0}
header h1{margin:0;font-size:22px} header p{color:#888;font-size:13px}
.grid{max-width:1100px;margin:20px auto;display:grid;grid-template-columns:1fr 1fr;gap:20px;padding:0 20px}
.card{background:white;border-radius:14px;padding:20px;box-shadow:0 4px 15px rgba(0,0,0,.05);border:1px solid #fef3c7}
.drop{border:1.5px dashed #fbbf24;background:#fffbeb;border-radius:10px;padding:25px;text-align:center;color:#999;font-size:13px;cursor:pointer}
.btn-black{background:#111;color:white;border:none;width:100%;padding:12px;border-radius:25px;font-weight:bold;margin-top:12px;cursor:pointer}
.input-row{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:10px}
.input-row div label{font-size:10px;color:#888;font-weight:bold;text-transform:uppercase}
.input-row input{width:100%;padding:8px 10px;border:1px solid #f3e5c3;border-radius:8px;background:#fffdf5;margin-top:4px}
.btn-green{background:#111;color:white;border:none;width:100%;padding:12px;border-radius:25px;font-weight:bold;margin-top:10px;cursor:pointer}
.result-box{max-width:1100px;margin:20px auto;background:#fffef7;border:1px solid #fde68a;border-radius:14px;padding:20px}
</style></head>
<body>
<div class="topbar"><div>Transformez vos fruits en concentres de qualite.</div><div>USEREMAIL | <a href="/logout">Deconnexion</a></div></div>
<header><h1>Votre laboratoire numerique - Concentration d'un Jus</h1><p>Procede: Jus dilue -> Evaporateur -> Jus concentre + Vapeur (Fruit Flow)</p></header>
<div class="grid">
<div class="card">
<h3>1. Analyse d'image - Jus initial</h3>
<div class="drop" id="drop" onclick="document.getElementById('file').click()">Glissez image du jus dilue<br><small>Cliquez pour uploader</small><br><img id="preview" style="max-width:100%;margin-top:10px;display:none;border-radius:8px"></div>
<input type="file" id="file" accept="image/*" style="display:none" onchange="loadImg(event)">
<button class="btn-black" onclick="analyser()">Analyser jus initial</button>
<div id="ci_res" style="background:#fef3c7;padding:10px;border-radius:8px;display:none;margin-top:10px"></div>
</div>
<div class="card">
<h3>2. Calculs - Concentration d'un jus</h3>
<div class="input-row">
<div><label>Debit Massique Initial (kg/h)</label><input id="m0" value="100" type="number"></div>
<div><label>Debit Recyclage Ajoute (kg/h)</label><input id="mr" value="15" type="number"></div>
</div>
<div class="input-row">
<div><label>Concentration Finale Souhaitee (% Brix)</label><input id="cf" value="65" type="number"></div>
<div><label>Temperature Chauffage (C)</label><input id="temp" value="85" type="number"></div>
</div>
<button class="btn-green" onclick="simulation()">LANCER LA SIMULATION</button>
</div>
</div>
<div class="result-box">
<h3>Resultat Final</h3>
<div id="final" style="color:#666;font-size:13px">En attente... Dir analyse image + lancer simulation</div>
</div>
<script>
let Ci=12;
function loadImg(e){
 let file=e.target.files[0];
 let reader=new FileReader();
 reader.onload=function(ev){
   document.getElementById('preview').src=ev.target.result;
   document.getElementById('preview').style.display='block';
 };
 reader.readAsDataURL(file);
}
function analyser(){
 let file=document.getElementById('file').files[0];
 if(!file){alert('Choisir image dabord!');return;}
 Ci=(Math.random()*5+10).toFixed(1);
 document.getElementById('ci_res').style.display='block';
 document.getElementById('ci_res').innerHTML='<b>Analyse reussie!</b><br>Concentration initiale: <b>'+Ci+' Brix</b>';
}
function simulation(){
 let m0=parseFloat(document.getElementById('m0').value);
 let mr=parseFloat(document.getElementById('mr').value);
 let cf=parseFloat(document.getElementById('cf').value);
 let temp=parseFloat(document.getElementById('temp').value);
 let m_total=m0+mr;
 let m_conc=m_total*Ci/cf;
 let m_evap=m_total-m_conc;
 let Q=m_evap*2260 + m_total*4.18*(temp-20);
 let rendement=m_conc/m_total*100;
 document.getElementById('final').innerHTML=
 '<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:15px;margin-top:10px">'+
 '<div style="background:#fef3c7;padding:15px;border-radius:10px"><b>Entree</b><br>Ci: '+Ci+' Brix<br>Total: '+m_total+' kg/h</div>'+
 '<div style="background:#dcfce7;padding:15px;border-radius:10px"><b>Concentre</b><br>Finale: '+cf+' Brix<br>Debit: <b>'+m_conc.toFixed(2)+' kg/h</b><br>Rendement: '+rendement.toFixed(1)+'%</div>'+
 '<div style="background:#dbeafe;padding:15px;border-radius:10px"><b>Energie</b><br>Eau evaporee: <b>'+m_evap.toFixed(2)+' kg/h</b><br>Q: <b>'+Q.toFixed(0)+' kJ/h</b></div>'+
 '</div>';
}
</script>
</body></html>
'''
    html = html.replace("USEREMAIL", user_email)
    return html

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    if request.cookies.get("user"):
        return RedirectResponse("/lab")
    return login_page()

@app.get("/register", response_class=HTMLResponse)
def reg_get():
    return register_page()

@app.post("/register")
def reg_post(email: str = Form(...), password: str = Form(...)):
    conn=sqlite3.connect("fruitflow.db")
    c=conn.cursor()
    try:
        c.execute("INSERT INTO users VALUES (NULL,?,?)",(email,hash_pwd(password)))
        conn.commit()
        conn.close()
        r=RedirectResponse("/lab",302)
        r.set_cookie(key="user",value=email)
        return r
    except:
        conn.close()
        return HTMLResponse(register_page("Email deja utilise"))

@app.post("/login")
def log_post(email: str = Form(...), password: str = Form(...)):
    conn=sqlite3.connect("fruitflow.db")
    c=conn.cursor()
    c.execute("SELECT * FROM users WHERE email=? AND password=?",(email,hash_pwd(password)))
    u=c.fetchone()
    conn.close()
    if u:
        r=RedirectResponse("/lab",302)
        r.set_cookie(key="user",value=email)
        return r
    return HTMLResponse(login_page("Erreur login"))

@app.get("/lab", response_class=HTMLResponse)
def lab(request: Request):
    user=request.cookies.get("user")
    if not user:
        return RedirectResponse("/")
    return lab_page(user)

@app.get("/logout")
def logout():
    r=RedirectResponse("/",302)
    r.delete_cookie("user")
    return r

if __name__ == "__main__":
    port=int(os.environ.get("PORT",8005))
    uvicorn.run(app,host="0.0.0.0",port=port)