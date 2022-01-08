# web-201-heroku-flask-template

## Disclaimer

The instructions and the commands below were run on an Ubuntu WSL inside Windows 10.
If you are a Windows user, I totally recommend going the WSL route, altough it can be a little messy to setup.
If you are running on a Mac or some different setup, some stuff might be slightly different!

## Prerequisits

- A Git account and a personal access token so you can commit stuff from the command line
- Git installed in your machine so you can execute git commands
- Python installed in your machine so you can execute Python commands and run Pyton scripts. Make sure you have version 3.6 or superior. You also need to use pip, can't remember if that needed to be installed separately.


## Initializing the Project

Start by creating a new directory for the Python Flask example app. You can do it by running these commands:

```
$ mkdir your-app-name
$ cd your-app-name
```

I will use 'web-201-heroku-flask-template' as my app name.

Create a Python virtual environment:

```
python3 -m venv venv
source venv/bin/activate
```

## Installing Dependencies

We want to get Flask latest version:

```
pip3 install Flask
pip3 install gunicorn
pip3 install psycopg2
pip3 install Flask-SQLAlchemy
pip3 install Geoalchemy2
pip3 install flask_cors
```

More info about installing Flask can be found on their installation guide: https://flask.palletsprojects.com/en/2.0.x/installation/

We need a way to tell Heroku what are our app dependencies so they get also installed there.
We will use a requirements.txt file for that:

Once we got all the dependencies in our local, we put them into our requirements file:
(we need to be on the root directory of our project so the file gets created there)

```
python3 -m pip freeze > requirements.txt
```

## Writing the initial Application Code

You can copy the code from this template into your project. Files to copy:

- app.py


## Running the app locally

We want to make sure your app works fine up to this point.
To run, execute this:

```
flask run
```

You should see something like this on the output of the console:
```
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: off
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
```

If you access ```http://127.0.0.1:5000/``` or ```http://localhost:5000/``` you should see:

PUT APP IMAGE

During development, you normally want to reload your application automatically whenever you make a change to it. You can do this by passing an environment variable, FLASK_ENV=development, to flask run:

```
FLASK_ENV=development flask run
```

Use Ctrl+C to quit / shut down the flask app.

## Sync your changes to Github

The best is to setup a git repo and start commiting changes there from the beginning. You will be able to go back to previous versions if needed, and also we will deploy to Heroku what is on the git repo at any given time.

To sync your app project with Github:

1. From the GitHub site / console, create a new empty repository. Note down / copy your repo URL, it will look like *https://github.com/your-username/your-repo-name.git*
2. From your command line, run:

(replace 'https://github.com/mduhagon/web-201-heroku-flask-template.git' with YOUR repo URL from 1.)

```
git init
echo venv > .gitignore
echo __pycache__ >> .gitignore
git add .gitignore app.py requirements.txt
git branch -M main
git remote add origin https://github.com/mduhagon/web-201-heroku-flask-template.git
git push -u origin main
```

## Deploying the Application to Heroku

Setup a Heroku account if you don't have one already.

The Heroku command-line interface (CLI) is a tool that allows you to create and manage Heroku applications from the terminal. It’s the quickest and the most convenient way to deploy your application. You can check the developer’s documentation for installation instructions for your operating system. On most Linux distributions, you can install the Heroku CLI by running the following command:

```
curl https://cli-assets.heroku.com/install.sh | sh
```

The previous command downloads the Heroku CLI installer and executes it. Next, you have to log in by running the following command:

(for me it only works by adding sudo)

```
sudo heroku login
```

This opens a website with a button to complete the login process. Click Log In to complete the authentication process and start using the Heroku CLI:

[image]

The first step is to create a file named Procfile in the project’s root directory. This file tells Heroku how to run the app. You can create it by running the following command:

```
echo "web: gunicorn app:app" > Procfile
```


```
heroku create mduhagon-web-201-heroku-flask
```

if it works, you will see an output like this:

```
Creating ⬢ mduhagon-web-201-heroku-flask... done
https://mduhagon-web-201-heroku-flask.herokuapp.com/ | https://git.heroku.com/mduhagon-web-201-heroku-flask.git
```

To push your changes to the Heroku git remote, run the following:

(again, for me it only works adding sudo, you might try without)
```
sudo git push heroku main
```

If git asks for username / password, make sure you rerun the command to login from the Heroku cli:

```
sudo heroku login
```

## Adding a PostGres Database to your Heroku app

```
sudo heroku addons:create heroku-postgresql:hobby-dev
```

You should see an output similar to this:

```
Creating heroku-postgresql:hobby-dev on ⬢ mduhagon-web-201-heroku-flask... free
Database has been created and is available
 ! This database is empty. If upgrading, you can transfer
 ! data from another database with pg:copy
Created postgresql-parallel-63698 as DATABASE_URL
Use heroku addons:docs heroku-postgresql to view documentation
```

```
export DATABASE_URL=`sudo heroku pg:credentials:url postgresql-parallel-63698 | sed -n 5p | sed -r 's/\s+//g'`
```


