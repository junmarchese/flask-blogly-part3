"""Blogly application."""

from flask import Flask, redirect, render_template, request, url_for
from models import db, connect_db, User, Post, Tag, PostTag
from datetime import datetime

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///blogly'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ECHO'] = True

    connect_db(app)

    with app.app_context():
        db.create_all()

    return app

app = create_app()

# call this only if/when testing app
# app = create_app(test_config=True)

if __name__ == '__main__':
    app.run(debug=True)


@app.route('/')
def homepage():
    """Show recent list of posts."""
    posts = Post.query.all()
    return render_template('homepage.html', posts=posts)

@app.errorhandler(404)
def page_not_found(e):
    """Show 404 NOT FOUND page."""
    return render_template('404.html'), 404


####### User route #######

@app.route('/users')
def list_users():
    """List all users."""
    users = User.query.all()
    return render_template('users_list.html', users=users)

@app.route('/users/new', methods=["GET", "POST"])
def add_user():
    """Add a new user."""
    if request.method == "POST":
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        image_url = request.form['image_url']

        new_user = User(first_name=first_name, last_name=last_name, image_url=image_url)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('list_users'))
    
    return render_template('new_user.html')

@app.route('/users/<int:user_id>')
def show_user(user_id):
    """Show information about the given user."""
    user = User.query.get_or_404(user_id)
    return render_template('user_detail.html', user=user)

@app.route('/users/<int:user_id>/edit', methods=["GET", "POST"])
def edit_user(user_id):
    """Show edit page for a user and allow existing user to make edits."""
    user = User.query.get_or_404(user_id)

    if request.method == "POST":
        user.first_name = request.form['first_name']
        user.last_name = request.form['last_name']
        user.image_url = request.form['image_url']

        db.session.add(user)
        db.session.commit()
        return redirect(url_for('list_users', user_id=user.id))
    
    return render_template('edit_user.html', user=user)

@app.route('/users/<int:user_id>/delete', methods=["POST"])
def delete_user(user_id):
    """Delete the user."""
    user = User.query.get_or_404(user_id)

    # Post.query.filter_by(user_id=user.id).delete()

    # posts = Post.query.filter_by(user_id=user.id).all()
    # for post in posts:
    #     post.user_id = None

    db.session.delete(user)
    db.session.commit()

    return redirect(url_for('list_users'))


####### Posts route ########

@app.route('/users/<int:user_id>/posts/new', methods=["GET", "POST"])
def add_post(user_id):
    """Show form to add a post for that user and handle form submission."""
    user = User.query.get_or_404(user_id)
    # tags = Tag.query.all()
    tags = Tag.query.all()
    tag_ids = [int(num) for num in request.form.getlist('tags')]

    if request.method == "POST":
        title = request.form.get('title')
        content = request.form.get('content')
        tag_ids = [int(num) for num in request.form.getlist('tags')]
        tags = Tag.query.filter(Tag.id.in_(tag_ids)).all()
        # tags = Tag.query.filter(Tag.id.in_(tag_ids)).all()
        new_post = Post(title=title, content=content, user_id = user.id)
        new_post.tags = tags
        db.session.add(new_post)
        db.session.commit()

        # for tag_id in tag_ids:
        #     tag = Tag.query.get(tag_id)
        #     if tag:
        #         new_post.tags.append(tag)

        db.session.commit()
        return redirect(url_for('show_user', user_id=user.id))
    
    return render_template('new_post.html', user=user, tags=tags)


@app.route('/posts/<int:post_id>')
def show_post(post_id):
    """Show a single post."""
    post = Post.query.get_or_404(post_id)
    return render_template('post_detail.html', post=post)

@app.route('/posts/<int:post_id>/edit', methods=["GET", "POST"])
def edit_post(post_id):
    """Show form to edit a post, cancel back to user page, and handle edit submission"""
    post = Post.query.get_or_404(post_id)
    tags = Tag.query.all()

    if request.method == "POST":
        post.title = request.form['title']
        post.content = request.form['content']
        
        tag_ids = [int(num) for num in request.form.getlist('tags')]
        # post.tags = Tag.query.filter(Tag.id.in_(tag_ids)).all()

        post.tags = [Tag.query.get(tag_id) for tag_id in tag_ids if Tag.query.get(tag_id)]
        # for tag_id in tag_ids:
        #     tag = Tag.query.get(tag_id)
        #     post.tags.append(tag)

        # db.session.add(post)
        db.session.commit()
        return redirect(url_for('show_post', post_id=post.id))
    
    return render_template('edit_post.html', post=post, tags=tags)

@app.route('/posts/<int:post_id>/delete', methods=["POST"])
def delete_post(post_id):
    """Delete a post."""
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('show_user', post_id=post.user_id))



####### Tags route #######

@app.route('/tags')
def list_tags():
    """List all tags."""
    tags = Tag.query.all()
    return render_template('tags_list.html', tags=tags)

@app.route('/tags/new', methods=["GET", "POST"])
def add_tag():
    """Add a new tag."""
    tags = Tag.query.all()

    if request.method == "POST":
        name = request.form.get('name')
        post_ids = []
        if 'posts' in request.form:
            post_ids = [int(num) for num in request.form.getlist('posts')]

        new_tag = Tag(name=name)
        db.session.add(new_tag)
        db.session.commit()

        if post_ids:
            posts = Post.query.filter(Post.id.in_(post_ids)).all()

            for post in posts:
                post.tags.append(new_tag)

        return redirect (url_for('list_tags'))
    
    return render_template('new_tag.html', tags=tags)
        # new_tag = Tag(name=name, posts=posts)
        # new_tag.posts = posts
        # db.session.add(new_tag)
        # db.session.commit()

        # for post_id in post_ids:
        #     post = Post.query.get(post_id)
        #     if post:
        #         new_tag.posts.append(post)

    #     db.session.commit()
    #     return redirect(url_for('list_tags'))
    
    # return render_template('new_tag.html', posts=posts)

@app.route('/tags/<int:tag_id>')
def showDetail_tag(tag_id):
    """Show detail about a tag."""
    tag = Tag.query.get_or_404(tag_id)
    return render_template('tag_detail.html', tag=tag)

@app.route('/tags/<int:tag_id>/edit', methods=["GET", "POST"])
def edit_tag(tag_id):
    """Edit a tag."""
    tag = Tag.query.get_or_404(tag_id)
    posts = Post.query.all()

    if request.method == "POST":
        tag.name = request.form['name']
        post_ids = [int(num) for num in request.form.getlist('posts')]

        tag.posts = Post.query.filter(Post.id.in_(post_ids)).all()
        db.session.add(tag)
        db.session.commit()
        return redirect(url_for('list_tags'))
    
    return render_template('edit_tag.html', tag=tag, posts=posts)

@app.route('/tags/<int:tag_id>/delete', methods=["POST"])
def delete_tag(tag_id):
    """Delete a tag."""
    tag = Tag.query.get_or_404(tag_id)
    db.session.delete(tag)
    db.session.commit()
    return redirect(url_for('list_tags'))



