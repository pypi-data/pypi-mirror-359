## Modals for Flask

Use forms in Bootstrap modals with Flask.

### Description

Plain forms can be boring. Using them in modals is possible, but requires
JavaScript. Normal form submission in modals is problematic.

This Flask extension eases the process of using forms in Bootstrap modals.
Bootstrap versions 4 and 5 are supported. No JavaScript coding is required on 
your part. You can code in pure Python - flashing messages and rendering
templates.

This extension is a minor variantion of flask-modals to work with Flask>2.3.
The _app_ctx_stack variable was removed from Flask in version 2.3 so we replaced 
it by a call to the _get_current_object() method of current_app object

### Installation

```Shell
pip install Flask-Modals2
```

### Setup

1. Import the `Modal` class and instantiate it in your `app.py` file.

    ```Python
    from flask_modals2 import Modal

    app = Flask(__name__)
    modal = Modal(app)
    ```
    You will also need a secret key in the app config (not shown).
    <br>
2. Alternatively if you are using the application factory pattern:

    ```Python
    from flask_modals2 import Modal

    modal = Modal()

    def create_app():
        app = Flask(__name__)
        modal.init_app(app)
    ```
    <br>
3. Include the following in the head tag of your base template.

    ```html
    {{ modals() }}
    ```
    <br>
4. Include the following in the modal body.

    ```html
    <div class="modal-body">
    {{ modal_messages() }}
    <form method="post">
    ...
    ```

### Basic usage

You only need to import the function `render_template_modal` in your `routes.py`
file. Use it instead of `render_template` in the route handler for the page with
the modal form. It takes an extra argument - `modal` (the modal `id` with a default
of `modal-form`).
<br>
The extension works by submitting the modal form twice - first via
ajax and then, if all validations pass, normally. When submiited via ajax, it 
passes a field '_ajax' with the form, which can be used as shown below.

Example route handler:

```Python
from flask_modals import render_template_modal

@app.route('/', methods=['GET', 'POST'])
def index():

    ajax = '_ajax' in request.form  # Add this line
    form = LoginForm()
    if form.validate_on_submit():
        if form.username.data != 'test' or form.password.data != 'pass':
            flash('Invalid username or password', 'danger')
            return redirect(url_for('index'))

        if ajax:        # Add these
            return ''   # two lines
        login_user(user, remember=form.remember_me.data)

        flash('You have logged in!', 'success')
        return redirect(url_for('home'))

    # Add this line
    return render_template_modal('index.html', form=form)
```

### Other usage

If you want to render a template and not redirect:

```Python
@app.route('/', methods=['GET', 'POST'])
def index():

    ajax = '_ajax' in request.form
    form = LoginForm()
    if form.validate_on_submit():
        if form.username.data != 'test' or form.password.data != 'pass':
            flash('Invalid username or password', 'danger')
            return render_template_modal('index.html', form=form)

        if ajax:
            return ''
        login_user(user, remember=form.remember_me.data)

        flash('You have logged in!', 'success')
        return render_template_modal('index.html', form=form)

    return render_template_modal('index.html', form=form)
```
If the above looks verbose, you can use the `response` decorator and
return a context dictionary, like so:

```Python
from flask_modals import response

@app.route('/', methods=['GET', 'POST'])
@response('index.html')
def index():
    ...
    ...
    return {'form': form}
```
<br>

### Note

1. See the examples folder in the repo for more details.

2. The extension loads the NProgress js library to display a progress bar during
form submission.  
