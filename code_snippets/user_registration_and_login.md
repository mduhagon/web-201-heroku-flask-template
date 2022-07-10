### Whats the goal?

to implement user registration and login functionalities for our app! As a prerequisite, 
you have your app running at least locally. If it runs on Heroku even better, that's the ideal, 
but if you got stuck there somehow you can still get started with this part.

### High level overview of what we want to do

If we are going to have users in our app, we need to store them somewhere. 
We are using our Postgres Database (DB) instance to store our map locations, and we can also store our users there. 
We need to create a **model class that will represent the user**, this is: 

will hold all data attributes that a user should have:

- name
- email (We use this one usually because it is unique, names can repeat so they aren't unique)
- password (to log in)
- address? (let's not ask for user data if we do not need it later for something in our app)
- other attributes that make sense for your app use case! (you can add these to the user class structure provided)

the user class might also have some logic: methods that perform some task that
makes sense to be done by the user class. For example: 

- validations
- storing the user to the DB, etc.

Once we have a User model class, we will implement two forms:

- Registration (it allows to create new users in the DB)
- Login (it allows to start a session for an existing usre in the DB)

Finally, we will make the 'New location' functionality that comes in the template be only possible for logged-in users,
and when a new location is created we will 'link it' or relate it to the user that created it. 
So we can say each location now 'belongs' to a user of the site.

For all this, we will use a Flask extension called [flask_login](https://flask-login.readthedocs.io/en/latest/). 
It will take care of some of the heavy lifting involved with maintaining a user session on our app 

### Step 1 - Install new flask_login dependency

remember to do this within your venv / while your venv is activated:

```
pip3 install flask_login
pip3 install email_validator
```

Update your requirements.txt file (you can use pip freeze or add this dependency by hand):

**Mac / Linux**
```
python3 -m pip freeze > requirements.txt
```

**Windows**
```
pip freeze > requirements.txt
```

In the end the lines added to requirements.txt should be:

```
Flask-Login==0.6.1
dnspython==2.2.1
email-validator==1.2.1
idna==3.3
```
(actual version numbers might change over time)

### Step 2 - Create the User class

The class is added to your ``models.py`` file:

```
class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(200), nullable=False) # i.e Hanna Barbera
    display_name = db.Column(db.String(20), unique=True, nullable=False) # i.e hanna_25
    email = db.Column(db.String(120), unique=True, nullable=False) # i.e hanna@hanna-barbera.com
    password = db.Column(db.String(32), nullable=False) 
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    @classmethod
    def get_by_id(cls, user_id):
        return cls.query.filter_by(id=user_id).first()
        
    def __repr__(self):
        return f"User({self.id}, '{self.display_name}', '{self.email}')"      

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def update(self):
        db.session.commit()   
```

To make some references work you need to add the following to the imports ection on the top of the file:

```
from flask_login import UserMixin
from datetime import datetime
```

At this point you need to start your app locally, and force a re-creation of your DB. You do that by un-commenting 
the method ```db_drop_and_create_all()``` that is in app.py 

Then start your app (in any form you are doing it by now / ie. by command line / with VSCode run, etc):

```
flask run
```

At this point it can be a good idea to take a look at your database with DBeaver or a similar editor, or the SQL command line client, 
and verify a new table was created. (TODO: make a step-by-step guide for this)

Once the Flask app started and the DB is recreated you can comment back the method ```db_drop_and_create_all()```.
If you do more changes later, for example add some attribute for the User class, modify the SampleLocation class, etc. 
You need to do this procedure of executing ```db_drop_and_create_all()``` again, otherwise the changes will not be 'impacted into' or executed in the DB.

### Step 3 - Create a registration Form and page

Content for the Registration form class (you add it to ``forms.py``):

```
class RegistrationForm(FlaskForm):
    fullname = StringField(
        'Full Name', 
        validators=
            [DataRequired(), 
            Length(min=2, max=200)
        ]
    )

    username = StringField(
        'Username / Display Name', 
        validators=
            [DataRequired(), 
            Length(min=2, max=20)
        ]
    )

    email = StringField(
        'Email',
        validators=[
            DataRequired(), 
            Email()
        ]
    )

    password = PasswordField(
        'Password',
        validators=[
            DataRequired()
        ]
    )

    confirm_password = PasswordField(
        'Confirm Password',
        validators=[
            DataRequired(),
            EqualTo('password')
        ]
    )

    submit = SubmitField('Sign up')  

```

You need to modify existing import lines to add a few more imports:
```
from wtforms import StringField, SubmitField, HiddenField, PasswordField
from wtforms.validators import DataRequired, Length, Email, EqualTo
```

You need a new template file, called ``registration.html``:
```
class RegistrationForm(FlaskForm):
    fullname = StringField(
        'Full Name', 
        validators=
            [DataRequired(), 
            Length(min=2, max=200)
        ]
    )

    username = StringField(
        'Username / Display Name', 
        validators=
            [DataRequired(), 
            Length(min=2, max=20)
        ]
    )

    email = StringField(
        'Email',
        validators=[
            DataRequired(), 
            Email()
        ]
    )

    password = PasswordField(
        'Password',
        validators=[
            DataRequired()
        ]
    )

    confirm_password = PasswordField(
        'Confirm Password',
        validators=[
            DataRequired(),
            EqualTo('password')
        ]
    )

    submit = SubmitField('Sign up')  
```

You need to modify / add some imports at the top of the page:
```
from wtforms import StringField, SubmitField, HiddenField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo
```

You need to add the code to handle this new registration page / route in your ``app.py``:
```
   @app.route("/register", methods=['GET', 'POST'])
    def register():
        # Sanity check: if the user is already authenticated then go back to home page
        # if current_user.is_authenticated:
        #     return redirect(url_for('home'))

        # Otherwise process the RegistrationForm from request (if it came)
        form = RegistrationForm()
        if form.validate_on_submit():
            # hash user password, create user and store it in database
            hashed_password = hashlib.md5(form.password.data.encode()).hexdigest()
            user = User(
                full_name=form.fullname.data,
                display_name=form.username.data, 
                email=form.email.data, 
                password=hashed_password)

            try:
                user.insert()
                flash(f'Account created for: {form.username.data}!', 'success')
                return redirect(url_for('home'))
            except IntegrityError as e:
                flash(f'Could not register! The entered username or email might be already taken', 'danger')
                print('IntegrityError when trying to store new user')
                # db.session.rollback()
            
        return render_template('registration.html', form=form)   
```

With these bits you can hit /register on your browser against your running app and try out the registration page.
We do not have a link to register from the site yet, but we will add it later, maybe to the navigation bar in the home page.

Try out your form, what happens if you do not fill all fields? Can you register a user when entering all correct values?

### Step 4 - Create a login Form and page

Content for the Login form class (you add it to ``forms.py``):

```
class LoginForm(FlaskForm):
    username = StringField(
        'Username / Display Name',
        validators=[
            DataRequired()
        ]
    )

    password = PasswordField(
        'Password',
        validators=[
            DataRequired()
        ]
    )

    remember = BooleanField('Remember me')

    submit = SubmitField('Login')    
```

You need a new template file, called ``login.html``:
```
{% extends "layout.html" %}
{% block body %}
<div id="container">
    <div class="content-section">
        <form method="POST" action="">
            {{ form.hidden_tag() }}
            <fieldset class="form-group">
                <legend class="border-bottom mb-4">Login</legend>
                <div class="form-group">
                    {{ form.username.label(class="form-control-label") }}    
                    {% if form.username.errors %}
                    {{ form.username(class="form-control form-control-lg is-invalid") }}
                        <div class="invalid-feedback">
                            {% for error in form.username.errors %}
                                <span>{{ error }}</span>
                            {% endfor %}
                        </div>  
                    {% else %}    
                        {{ form.username(class="form-control form-control-lg") }}
                    {% endif %} 
                </div>  
                <div class="form-group">
                    {{ form.password.label(class="form-control-label") }}      
                    {% if form.password.errors %}
                        {{ form.password(class="form-control form-control-lg is-invalid") }} 
                        <div class="invalid-feedback">
                            {% for error in form.password.errors %}
                                <span>{{ error }}</span>
                            {% endfor %}
                        </div>  
                    {% else %}    
                        {{ form.password(class="form-control form-control-lg") }} 
                    {% endif %}
                </div>      
                <div class="form-check">
                    {{ form.remember(class="form-check-input") }}
                    {{ form.remember.label(class="form-check-label") }}
                </div>       
                <small class="text-muted ml-2">
                    <a href="#">Forgot password?</a>
                </small>
            </fieldset>
            <div class="form-group">
                {{ form.submit(class='btn btn-outline-info')}}    
            </div>
        </form>
    </div>
    <div class="border-top pt-3">
        <small class="text-muted">
            You do not have an account? <a class="ml-2" href="{{ url_for('register')}}">Register</a>
        </small>
    </div>
</div>    
{% endblock body %}
```

You need to add the code to handle the login, and also the loading of an user and logout routes in your ``app.py``:
(In the previous step we had created a stub method for login, replace that now with the actual implementation)
```
    @login_manager.user_loader
    def load_user(user_id):
        return User.get_by_id(user_id)           

    @app.route("/login", methods=['GET', 'POST'])
    def login():
        # Sanity check: if the user is already authenticated then go back to home page
        # if current_user.is_authenticated:
        #    return redirect(url_for('home'))

        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(display_name=form.username.data).first()
            hashed_input_password = hashlib.md5(form.password.data.encode()).hexdigest()
            if user and user.password == hashed_input_password:
                login_user(user, remember=form.remember.data)
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('home'))
            else:
                flash('Login Unsuccessful. Please check user name and password', 'danger')
        return render_template('login.html', title='Login', form=form) 

    @app.route("/logout")
    @login_required
    def logout():
        logout_user()
        flash(f'You have logged out!', 'success')
        return redirect(url_for('home'))   
```

Again, there is some additional classes to import at the top of the file:
```
from forms import NewLocationForm, RegistrationForm, LoginForm
from models import User
from sqlalchemy.exc import IntegrityError
from flask_login import login_user, logout_user, login_required, current_user, login_manager, LoginManager
```

Also, because we are using flask_login, we need to initialize a LoginManager at the app level. 
This will help us start a session for the user when they login correctly, and allow us to have a current_user 
in our app (if requests are being made by a logged in user)

In ``app.py`` inside the ``create_app()`` method, before you start defining routes, add the following lines:

```
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
```

### Step 5 - Use the current_user to display conditionally some content (login link / new location)

Now that we can login users, we can make new location page only accesible to logged in users. If you are not logged in to the site you should not be able to do that.
Also, if the user is not logged in we will show the login / register links in nav bar, but if the user is already logged, we will instead show a logout.

Modify the NavBar in ``map.html`` template so it looks like this:

```
{% extends "layout.html" %}
{% block head %}
  <link rel="stylesheet" href="https://js.arcgis.com/4.24/esri/themes/light/main.css"> 
  <script src="https://js.arcgis.com/4.24/"></script>
  <script src="{{ url_for('static', filename='map.js') }}"></script>
  <script>
    require(["esri/config","esri/Map", "esri/views/MapView", "esri/Graphic",
    "esri/layers/GraphicsLayer", "esri/core/reactiveUtils", "esri/geometry/Circle", "esri/rest/locator"], function (esriConfig,Map, MapView, Graphic, GraphicsLayer, reactiveUtils, Circle, locator) {
      esriConfig.apiKey = "{{map_key}}";
      initMap(esriConfig,Map, MapView, Graphic, GraphicsLayer, reactiveUtils, Circle, locator);
    });
  </script>
{% endblock %}
{% block body %}
  <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
    <span class="navbar-brand mb-0 h1">Navbar</span>
    <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarSupportedContent" aria-controls="navbarSupportedContent" aria-expanded="false" aria-label="Toggle navigation">
      <span class="navbar-toggler-icon"></span>
    </button>    
    <div class="collapse navbar-collapse" id="navbarSupportedContent">
      {% if current_user.is_authenticated %}
      <ul class="navbar-nav mr-auto">
        <li class="nav-item">
          <span class="nav-link text-reset">Hi {{ current_user.display_name }}!</span>
        </li>
        <li class="nav-item">
          <a class="nav-link" href="{{ url_for('new_location') }}">New Location</a>
        </li>
        <li class="nav-item">
          <a class="nav-link" href="{{ url_for('logout') }}">Logout</a>
        </li>      
      </ul>    
      {% else %}
      <ul class="navbar-nav mr-auto">
        <li class="nav-item">
          <a class="nav-link" href="{{ url_for('login') }}">Login</a>
        </li>
        <li class="nav-item">
          <a class="nav-link" href="{{ url_for('register') }}">New User Registration</a>
        </li>
      </ul>     
      {% endif %}
      <form method="GET" action="" onsubmit="return searchAddressSubmit()" class="form-inline my-2 my-lg-0">
        <input class="form-control mr-sm-2" id="search_address" type="search" placeholder="Search near..." aria-label="Search near">
        <button class="btn btn-info my-2 my-sm-0" type="submit">Search</button>
      </form>   
    </div>
  </nav>
  <div id="viewDiv"></div>
{% endblock %}
```

There are also a small additional style (this goes in ``styles.css``):
```
.navbar li.nav-item {
  color: #fff;    
}
```

Add the @login_required annotation to the new_location route (the line in the middle):

```
    @app.route("/new-location", methods=['GET', 'POST'])
    @login_required
    def new_location():
```

### Step 6 - Optional: make locations be related to user that created them

You can do this step if the relation makes sense for your app use case. For example: if you were developing an app where users
create entries for lost pets, and then you want to show on the site the details of each pet, along with the user that created the entry 
(because the owner of the lost pet will want to contact them for more details).

Otherwise, you might take a look at these changes to understand how to create a type of [relationship](https://docs.sqlalchemy.org/en/14/orm/basic_relationships.html) 
between the models in your app.

First, Add a reference to the User from the ``SampleLocation`` model (I mark with <<< the lines that change or were added):
```
class SampleLocation(db.Model):
    __tablename__ = 'sample_locations'

    id = Column(Integer, primary_key=True)
    description = Column(String(80))
    geom = Column(Geometry(geometry_type='POINT', srid=SpatialConstants.SRID))  
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False) # <<<

    # many to one side of the relationship of SampleLocation with User <<<
    user = db.relationship("User", back_populates="created_locations") # <<<

    ...
```

Then the reference from User to SampleLocation:
```
class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(200), nullable=False) # i.e Hanna Barbera
    display_name = db.Column(db.String(20), unique=True, nullable=False) # i.e hanna_25
    email = db.Column(db.String(120), unique=True, nullable=False) # i.e hanna@hanna-barbera.com
    password = db.Column(db.String(32), nullable=False) 
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    created_locations = db.relationship('SampleLocation', back_populates='user', order_by="SampleLocation.description", lazy=True) # <<<
    
    ....

```

Because we have changed the SampleLocation and defined the ``user_id`` as a required data now, we need to a) change the code that
creates the initial DB data and b) re-execute the initial creation of the db by un-commenting the method ``db_drop_and_create_all()`` in ``app.py`` 
(you can do this at the end after all bellow code changes are done)

Ok, so, this is the modified code to create the initial DB data (goes in ``models.py``):
```
def insert_sample_locations():
    # We need to start with an user to be able to relate initial locations to them
    admin_user = User(
        full_name="Administrator",
        display_name="admin",
        email="admin@dummy.mail",
        password=hashlib.md5("admin".encode()).hexdigest()
    )
    admin_user.insert()

    loc1 = SampleLocation(
        description='Brandenburger Tor',
        geom=SampleLocation.point_representation(
            latitude=52.516247, 
            longitude=13.377711
        )
    )
    loc1.user = admin_user # <<<
    loc1.insert()

    loc2 = SampleLocation(
        description='Schloss Charlottenburg',
        geom=SampleLocation.point_representation(
            latitude=52.520608, 
            longitude=13.295581
        )
    )
    loc2.user = admin_user # <<<
    loc2.insert()

    loc3 = SampleLocation(
        description='Tempelhofer Feld',
        geom=SampleLocation.point_representation(
            latitude=52.473580, 
            longitude=13.405252
        )
    )
    loc3.user = admin_user # <<<
    loc3.insert()
```

You also need this new import at the top of the ``models.py``:
```
import hashlib
```

The code to create a new location in the db needs to change slightly to add the relation between location and current logged in user:
```
    @app.route("/new-location", methods=['GET', 'POST'])
    @login_required
    def new_location():
        form = NewLocationForm()

        if form.validate_on_submit():            
            latitude = float(form.coord_latitude.data)
            longitude = float(form.coord_longitude.data)
            description = form.description.data

            location = SampleLocation(
                description=description,
                geom=SampleLocation.point_representation(latitude=latitude, longitude=longitude)
            )   
            location.user_id = current_user.id # <<<< added
            location.insert()
         ....   
```

There is a second method to insert locations passing all params as GET params (this could be used by an admin for example to insert more data)
We need to update that too so it keeps working:

```

    @app.route("/api/store_item")
    def store_item():
        try:
            latitude = float(request.args.get('lat'))
            longitude = float(request.args.get('lng'))
            description = request.args.get('description')
            user_id = int(request.args.get('user_id')) # <<<< added

            location = SampleLocation(
                description=description,
                geom=SampleLocation.point_representation(latitude=latitude, longitude=longitude),
                user_id=user_id # <<<< added
            )   
            
            ....
```

So you see how the relationship could be used in the views, we will show who created each location on the detail view.
This is the changed version of ``detail.html``:
```
{% extends "layout.html" %}
{% block body %}
    Sample location description: {{item.description}}<br/>
    Created by: {{item.user.display_name}}
{% endblock %}
```

``ìtem`` is an object of type SampleLocation, so it now has an attribute called user, that contains the whole user details that are related to it. 
So we not only can show the user_id for this location, but the user display_name, which is more useful for the end customer (that knows nothing about our internal ids)
