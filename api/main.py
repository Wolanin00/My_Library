from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import math

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///mybooks.db"
app.config['SECRET_KEY'] = 'my_secret_key'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)



class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    author = db.Column(db.String(250), nullable=False)
    rating = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"<Book {self.title}>"


with app.app_context():
    db.create_all()


@app.route('/')
def home():
    all_books = db.session.query(Book).order_by(Book.rating.desc()).all()
    return render_template('index.html', book_stack=all_books)


@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        b_name = request.form["book"]
        b_author = request.form["author"]
        b_rating = request.form["rating"]
        try:
            float_rating = float(b_rating)
        except ValueError:
            flash('Rating should be float')
            return render_template('add.html', name=b_name, author=b_author)
        else:
            if float_rating < 0 or float_rating > 10:
                flash('Rating should be in range 0-10')
                return render_template('add.html', name=b_name, author=b_author)
        b_rating = math.floor(float_rating * 10) / 10
        new_book = Book(title=b_name, author=b_author, rating=b_rating)
        db.session.add(new_book)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('add.html', name='', author='')


@app.route("/edit", methods=["GET", "POST"])
def edit():
    book_id = request.args.get('id')
    book_selected = Book.query.get(book_id)
    if request.method == "POST":
        book_id = request.form["id"]
        book_to_update = Book.query.get(book_id)
        new_rating = request.form["rating"]
        try:
            float_rating = float(new_rating)
        except ValueError:
            flash('Rating should be float')
            return render_template("edit.html", book=book_to_update)
        else:
            if float_rating < 0 or float_rating > 10:
                flash('Rating should be in range 0-10')
                return render_template("edit.html", book=book_to_update)
        book_to_update.rating = math.floor(float_rating * 10) / 10
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("edit.html", book=book_selected)


@app.route("/delete")
def delete():
    book_id = request.args.get('id')
    # DELETE A RECORD BY ID
    book_to_delete = Book.query.get(book_id)
    db.session.delete(book_to_delete)
    db.session.commit()
    return redirect(url_for('home'))


if __name__ == "__main__":
    app.run(debug=True)
