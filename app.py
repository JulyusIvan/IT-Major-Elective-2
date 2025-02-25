from flask import Flask, render_template, request, redirect, url_for, flash
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, Text, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

app = Flask(__name__)
bootstrap = Bootstrap5(app)

app.config["SECRET_KEY"] = "julyus"
app.config["SQLALCHEMY_DATABASE_URI"] = 'postgresql://postgres:julyus123@localhost:5432/myhobbies'
#app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:@localhost:3306/myhobbies"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base) 
db.init_app(app)

class Hobby(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, unique=True)
    name: Mapped[str] = mapped_column()
    hobby: Mapped[str] = mapped_column()
    posts = relationship("Post", back_populates="hobby", cascade="all, delete-orphan")

class Post(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, unique=True)
    hobby_id: Mapped[int] = mapped_column(ForeignKey('hobby.id'), nullable=False)
    details: Mapped[str] = mapped_column(Text)
    hobby = relationship('Hobby', back_populates='posts')

@app.route("/")
def home():
    hobbies = Hobby.query.all()
    return render_template('User/home.html', hobbies=hobbies)

@app.route("/read/<int:id>")
def read(id):
    myhobby = Hobby.query.get_or_404(id)
    posts = Post.query.filter_by(hobby_id=id).all()
    return render_template('User/read.html', myhobby=myhobby, posts=posts)

@app.route("/create", methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        name = request.form['name']
        hobby = request.form['hobby']
        new_hobby = Hobby(name=name, hobby=hobby)
        db.session.add(new_hobby)
        db.session.commit()
        flash("Hobby added successfully!")
        return redirect(url_for('home'))
    return render_template('User/create.html')

@app.route("/create_post/<int:hobby_id>", methods=['GET', 'POST'])
def create_post(hobby_id):
    if request.method == 'POST':
        details = request.form['details']
        new_post = Post(hobby_id=hobby_id, details=details)
        db.session.add(new_post)
        db.session.commit()
        flash("Post added successfully!")
        return redirect(url_for('read', id=hobby_id))
    return render_template('User/create_post.html', hobby_id=hobby_id)

@app.route("/update/<int:id>", methods=['GET', 'POST'])
def update(id):
    hobby = Hobby.query.get_or_404(id)
    if request.method == 'POST':
        hobby.name = request.form['name']
        hobby.hobby = request.form['hobby']
        db.session.commit()
        flash("Updated successfully!")
        return redirect(url_for('read', id=id))
    return render_template('User/update.html', hobby=hobby)

@app.route("/update_post/<int:id>", methods=['GET', 'POST'])
def update_post(id):
    post = Post.query.get_or_404(id)
    if request.method == 'POST':
        post.details = request.form['details']
        db.session.commit()
        flash("Post updated successfully!")
        return redirect(url_for('read', id=post.hobby_id))
    return render_template('User/update_post.html', post=post)

@app.route("/delete/<int:id>")
def delete(id):
    hobby = Hobby.query.get_or_404(id)
    db.session.delete(hobby)
    db.session.commit()
    flash("Deleted successfully!")
    return redirect(url_for('home'))

@app.route("/delete_post/<int:id>")
def delete_post(id):
    post = Post.query.get_or_404(id)
    hobby_id = post.hobby_id
    db.session.delete(post)
    db.session.commit()
    flash("Post deleted successfully!")
    return redirect(url_for('read', id=hobby_id))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
