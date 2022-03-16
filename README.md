# web-201-heroku-flask-template

## What is this template for?

As part of our course, we want to build a location-based web application. We know we will need a database to store some data, and that we want special support for geospatial data (latitude and longitude storage, searches based on distance, etc). Eventually we want to deploy our app somewhere!

This template aims to be a starting point for you to follow when creating your own application.
It will ensure a couple good things:
- You setup a GitHub repo for your project right from the start. If you need to share your code, fellow students and mentors can see it on GitHub or fork it and run it too!
- You setup a Heroku account and can deploy your project there, also from the start.
- ~~By using a database provided / hosted by Heroku, you do not need to install a DB engine or plugins locally on your machine.~~
- While Heroku does allow installing a MySql DB, neither of the checked options meet all requirements to run the geolocation logic we want. So this guide is relying on you using a remote DB that will be provided/hosted by the mentor
- The template includes sample code to show a Google Map and some markers in it
- The template also includes a sample model with some prestored locations, just to test out the map functionality and make sure PostGis extension works too.

The idea is you use this to get a first working version of these very basic functionalities, and then start changing things to build your own app.

## Disclaimer

The instructions and the commands below were run on an Ubuntu WSL inside Windows 10.
If you are a Windows user, I totally recommend going the WSL route, altough it can be a little messy to setup.
If you are running on a Mac or some different setup, some stuff might be slightly different!

## Prerequisites

- A GitHub account and a [personal access token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token) so you can commit stuff from the command line
- Git installed in your machine so you can execute git commands
- Python installed in your machine so you can execute Python commands and run Pyton scripts. Make sure you have version **3.6 or superior**. You also need to use pip, can't remember if that needed to be installed separately.
- A Google Maps API Key

## Initializing the Project

Start by creating a new directory for your new app. You can do it by running these commands:

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

We want to get a bunch of libraries to get us started:
(you may install these one by one in case some error / warning comes)

You may or may not need to install the MySql client first.
Take a closer look here if you try to install 

```
pip3 install Flask
pip3 install gunicorn
pip3 install Flask-SQLAlchemy
pip3 install shapely
pip3 install flask_cors
pip3 install flask-mysqldb
```

If something fail while installing flask-mysqldb
take a closer look at this [guide](https://pypi.org/project/Flask-MySQLdb/), you might need to install
the mysqlclient first.

Needed to install this in Ubuntu:

```
apt-get install libmysqlclient-dev python-dev
```

More info about installing Flask can be found on their installation guide: https://flask.palletsprojects.com/en/2.0.x/installation/

We need a way to tell Heroku what are our app dependencies so they get also installed there.
We will use a requirements.txt file for that:

Once we got all the dependencies in our local, we put them into our requirements file:
(we need to be on the root directory of our project so the file gets created there)

```
python3 -m pip freeze > requirements.txt
```

If later on you install more libraries on your local virtual env, remember to generate the requirements.txt file again and push that change so the next time you deploy to Heroku it gets installed there as well.

## Writing the initial Application Code

You can copy the code from this template into your project. Files and folders to copy:

- static/
- templates/
- app.py
- models.py

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
git add .gitignore app.py models.py requirements.txt
git add static
git add templates
git commit -m "first commit"
git branch -M main
git remote add origin https://github.com/mduhagon/web-201-heroku-flask-template.git <<< replace this
git push -u origin main
```

## Setting up the Heroku cli and creating a Heroku app ~~with a Posgres DB~~

[Setup a Heroku account](https://signup.heroku.com/) if you don't have one already.

The Heroku command-line interface (CLI) is a tool that allows you to create and manage Heroku applications from the terminal. It’s the quickest and the most convenient way to deploy your application. You can check the developer’s documentation for installation instructions for your operating system. On most Linux distributions, you can install the Heroku CLI by running the following command:

```
curl https://cli-assets.heroku.com/install.sh | sh
```

The previous command downloads the Heroku CLI installer and executes it. Next, you have to log in by running the following command:

(for me the 'heroku' command always needs to be run with sudo, otherwise it fails. You may not need sudo on your local env)

```
sudo heroku login
```

This opens a website with a button to complete the login process. Click Log In to complete the authentication process and start using the Heroku CLI:

![heroku login browser window](/_readme_assets/Heroku-login.png)

If you were not already logged in Heroku's website, then you will have to enter username and password instead to login now. Once you do either of these,
in your command line interface, the heroku cli should say something like:

```
Logging in... done
Logged in as mduhagon@gmail.com
```

but with your username of course. In order to run any command with the heroku cli to control your apps, deploy, etc, you first need to do the above login step. After a while the authentication expires, so if at some point you run a heroku client command and it starts asking for username / pass, rerun the login command and you should be back in business.

Now we will create a new app inside your Heroku account. For that you need a unique name. I chose 'mduhagon-web-201-flask-mysql' for mine. Wherever you see this name in my commands, replace it with **your app name**.

To create the app, run:

```
heroku create mduhagon-web-201-flask-mysql
```

if it works, you will see an output like this:

```
Creating ⬢ mduhagon-web-201-flask-mysql... done
https://mduhagon-web-201-flask-mysql.herokuapp.com/ | https://git.heroku.com/mduhagon-web-201-flask-mysql.git
```

Now, we want to add a MySql database to our app, but! 
There are a few limitations with the MySql DBs that we could install via Heroku:

- ClearDB will give you a MySQL database with version 5.6, this is rather old and the support for Geolocation functions is super poor
- JAWSDB was almost good! It gives you a MySQL db with version 8, has all the functions we need, but... they seem to have limited some stuff because they do not have SRIDs in the sys schema...

So, as a quick workaround, I can provide a remote DB
that will live in the AWS account I own, and you can use it.
You will have to ask me for the REAL connection string, and then use it in the following steps

## Running the app locally

First, you want to get the app running locally, because if something did not work, it is easier to see what the issue is on your own machine than it is to do many Heroku deploys for each problem.

To run the sample code you copied from this template, two environment variables need to be set:

- DATABASE_URL: this is the connection string for the database. In this setup it will not come from Heroku, we need to set it locally and also tell Heroku what is the proper value
- GOOGLE_MAPS_API_KEY: You need to get this for yourself. It will be sent to the Google Maps API to render the map on the initial page of the sample app.

So, before running the flask app locally, set the two environment variables like this:
#### For Ubuntu / Mac:

Ask mentor for the value you need to use in DATABASE_URL, and replace it
for the dummy value mysql://XXXXXXXXX.... in the bellow command

The second env variable you need to set is your Google maps key, 
so the map within the sample app can be loaded:

```
export DATABASE_URL=mysql://XXXXXXXXX:YYYYYYYYY@ZZZZZZZZZZZ.cbetxkdyhwsb.us-east-1.rds.amazonaws.com:3306/KKKKKKKKK
export GOOGLE_MAPS_API_KEY=ssdfsdfsAAqfdfsuincswdfgcxhmmjzdfgsevfh
```

If you did this step correctly, when you execute these commands,
You should see the values you set via export:

```
> echo $DATABASE_URL
mysql://XXXXXXXXX:YYYYYYYYY@ZZZZZZZZZZZ.cbetxkdyhwsb.us-east-1.rds.amazonaws.com:3306/KKKKKKKKK

> echo $GOOGLE_MAPS_API_KEY
ssdfsdfsAAqfdfsuincswdfgcxhmmjzdfgsevfh
```

#### For Windows

(to be done later)


Finally, to run the app:

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

![sample app](/_readme_assets/Sample-app.png)

Bonus: during development, you normally want to reload your application automatically whenever you make a change to it. You can do this by passing an environment variable, FLASK_ENV=development, to flask run:

```
FLASK_ENV=development flask run
```

Use Ctrl+C to quit / shut down the flask app.

## Deploying the app to Heroku

Now that you verified the app runs locally, you can deploy it to Heroku!

The first step is to create a file named Procfile in the project’s root directory. This file tells Heroku how to run the app. You can create it by running the following command:

```
echo "web: gunicorn app:app" > Procfile
```

Commit this file to your GitHub repo:

```
git add Procfile
git commit -m "Procfile for heroku"
git push
```

Now all your code is up-to-date with GitHub. This is important because you push to Heroku whatever is in the main branch of your repo. 

Before deploy, a small extra step. Remember we need 2 environment variables for the sample code to work. DATABASE_URL is by default provided by Heroku because we have a DB attached to our app. The second env variable is something we define, so we need to set it manually as a Heroku config variable:

(here again for DATABASE_URL you need to use the real value provided by the mentor)
```
sudo heroku config:set DATABASE_URL=mysql://XXXXXXXXX:YYYYYYYYY@ZZZZZZZZZZZ.cbetxkdyhwsb.us-east-1.rds.amazonaws.com:3306/KKKKKKKKK
sudo heroku config:set GOOGLE_MAPS_API_KEY=ssdfsdfsAAqfdfsuincswdfgcxhmmjzdfgsevfh
```

Now all is ready. To deploy that current state into your Heroku app, run:

```
sudo git push heroku main
```

This will output a lot of things as heroku installs all components. By the end if all is OK you will see the URL of your launched app:

```
remote: -----> Launching...
remote:        Released v5
remote:        https://mduhagon-web-201-heroku-delete.herokuapp.com/ deployed to Heroku
remote:
remote: Verifying deploy... done.
```

If all went well, your sample app is now running in Heroku as well! Check the provided URL to verify.

## What now?

The sample code has some useful functionality: it is taking the database connection string from the already set Heroku env variable, it is using another config variable for the Google Maps key so that is not hardcoded in your source code (because the Google API key cannot be commited to GitHub!). It is also storing some sample data with lat / long and querying for it when you zoom / reposition the map. You can take a closer look at all this, so you then decide how to extend it.

You will keep making changes to the app, adding the functionality of your project. Everything in the template is just a sample, you can change / remove things as you wish.
Each time you have some new functionality working commit it to GitHub, and then to Heroku, so you make sure it works there as well.

In a nutshell, this process will look like this:

1. Use git status to see all the files you added or changed:

```
git status
```

2. Use git add to stage all the above changes that should go to your repo (you may need to do this for multiple paths or you can also list many together)

```
git add xxxxx
```

3. Commit the changes and push to GitHub

```
git commit -m "a short description of your changes so others know what you did / is also a future reference for yourself"
git push
```

4. Deploy the changes to Heroku:

```
sudo heroku login
sudo git push heroku main
```
