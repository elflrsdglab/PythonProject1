from flask import Flask, render_template, request, redirect, url_for, session, flash, abort
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from data import UNIS, TUBITAK_UNITS
app = Flask(__name__)
app.secret_key = "change-me-in-prod"

users = {}

def login_required(view):
    @wraps(view)
    def wrapped(*a, **kw):
        if "user" not in session:
            flash("Please log in first.")
            return redirect(url_for("login", next=request.path))
        return view(*a, **kw)
    return wrapped

def find_uni(uid):
    for u in UNIS:
        if int(u["id"]) == int(uid):
            return u
    return None

def find_unit(slug_or_id):
    for u in TUBITAK_UNITS:
        if str(u["id"]) == str(slug_or_id) or u["slug"] == slug_or_id:
            return u
    return None

@app.route("/")
def index():
    return redirect(url_for("home") if "user" in session else url_for("login"))

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        if not username or not password:
            flash("Please fill all fields.")
            return redirect(url_for("signup"))
        if username in users:
            flash("Username already exists.")
            return redirect(url_for("signup"))
        users[username] = generate_password_hash(password)
        session["user"] = username
        flash("Account created!")
        return redirect(url_for("home"))
    return render_template("signup.html", title="Sign up")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        hash_ = users.get(username)
        if hash_ and check_password_hash(hash_, password):
            session["user"] = username
            flash("Logged in.")
            return redirect(request.args.get("next") or url_for("home"))
        flash("Wrong username or password.")
        return redirect(url_for("login"))
    return render_template("login.html", title="Login")

@app.route("/logout")
def logout():
    session.pop("user", None)
    flash("Logged out.")
    return redirect(url_for("login"))

# ----- Üniversiteler -----
@app.route("/home")
@login_required
def home():
    q = (request.args.get("q") or "").lower().strip()
    if q:
        unis = [u for u in UNIS if q in u["name"].lower() or q in u.get("address", "").lower()]
    else:
        unis = UNIS
    return render_template("home.html", title="Ankara Universities", unis=unis, q=q)

@app.route("/uni/<int:uid>")
@login_required
def uni_details(uid):
    uni = find_uni(uid)
    if not uni:
        abort(404)
    return render_template("details.html", title=uni["name"], uni=uni)

# ----- TÜBİTAK alt birimleri -----
@app.route("/tubitak")
@login_required
def tubitak_list():
    # DOSYA ADI: templates/tubitaklist.html
    return render_template("tubitaklist.html", title="TÜBİTAK Units", units=TUBITAK_UNITS)

@app.route("/tubitak/<slug>")
@login_required
def tubitak_details(slug):
    unit = find_unit(slug)
    if not unit:
        abort(404)

    return render_template("tubitakdetail.html", title=unit["name"], unit=unit)

if __name__ == "__main__":
    app.run(debug=True)
@app.route("/", methods=["GET"])
def home():
    names = sorted(UNIS.keys())
    error = request.args.get("error")
    return render_template("home.html", names=names, error=error)

@app.route("/select", methods=["POST"])
def select_university():
    name = request.form.get("uni")
    if not name or name not in UNIS:
        return redirect(url_for("home", error="Lütfen bir üniversite seçin."))
    info = UNIS[name]
    return render_template("details.html", name=name, info=info)

@app.route("/add", methods=["POST"])
def select_university():
    name = request.form.get("uni")
    if not name or name not in UNIS:
        # UNIS.add(name)
        return redirect(url_for("home", error="Lütfen bir üniversite seçin."))
    info = UNIS[name]
    return render_template("home.html", name=name, info=info)


if __name__ == "__main__":
    app.run(debug=True)
