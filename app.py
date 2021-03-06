from flask import Flask, render_template, request, redirect
from flask.helpers import url_for
from flask_sqlalchemy import SQLAlchemy

db_user = "root"
db_pass = "root"
db_name = "my_notes"

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://{}:{}@localhost/{}".format(db_user, db_pass, db_name)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)


@app.route("/")
def index():
    notes_sql = "Select * from notes where deleted_at is null"
    notes = db.session.execute(notes_sql)
    # print(type(notes))
    # for note in notes:
    #     print(note)
    return render_template('index.html', notes = notes)

@app.route("/create", methods=['GET', 'POST'])
def create():

    if request.method == 'GET':
        folders_sql = "Select * from folder"
        folders = db.session.execute(folders_sql)
        return render_template('create.html', folders = folders)
    elif request.method == 'POST':

        form = request.form
        params = {
            "title" : form['title'],
            "content" : form.get('content', ''),
            "folder_id" : form.get('folder_id', ''),
        }
        if not params['folder_id']:
            params['folder_id'] = None
        
        sql = f"insert into notes (`title`, `content`, `folder_id`) values(:title, :content, :folder_id)"
        
        db.session.execute(sql, params)
        db.session.commit()
        return redirect(url_for('index'))

@app.route("/update/<int:id>", methods=['GET', 'POST'])
def update(id):

    if request.method == 'GET':

        folders_sql = "Select * from folder"
        folders = db.session.execute(folders_sql)
        note_sql = "Select * from notes where id= :id and deleted_at is null"
        note = db.session.execute(note_sql, {"id":id}).fetchone()

        if not note:
            return redirect(url_for('error', code=404))
        
        return render_template('update.html', folders = folders, note = note)
    elif request.method == 'POST':

        form = request.form
        params = {
            "title" : form['title'],
            "content" : form.get('content', ''),
            "folder_id" : form.get('folder_id', ''),
            "id": id,
        }
        if not params['folder_id']:
            params['folder_id'] = None
        
        sql = f"update notes set title=:title, content=:content, folder_id=:folder_id where id=:id"
        
        res = db.session.execute(sql, params)
        db.session.commit()
        return redirect(url_for('index'))

@app.route("/delete", methods=['POST'])
def delete():

    if request.method == 'POST':
        try:
            id = request.form.get('id', None)
            if not id:
                return redirect('error', code=404)
            sql = f"update notes set deleted_at = now() where id=:id"
            db.session.execute(sql, {"id": id})
            db.session.commit()
        except (Exception):
            return redirect(url_for('error', code=404))
        return redirect(url_for('index'))

@app.route('/thrash')
def thrash():
    pass

@app.route("/error/<code>")
def error(code):
    codes = {
        "404": "404 Not Found",
    }
    return render_template("error.html", message = codes.get(code, "Invalid Request"))


if __name__ == "__main__":
    app.run(debug=True)