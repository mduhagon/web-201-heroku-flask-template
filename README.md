# web-201-heroku-flask-template

## What is this template for?

As part of our course, we want to build a location-based web application. We know we will need a database to store some data, and that we want special support for geospatial data (latitude and longitude storage, searches based on distance, etc). Eventually we want to deploy our app somewhere!

This template aims to be a starting point for you to follow when creating your own application.
It will ensure a couple good things:
- You setup a GitHub repo for your project right from the start. If you need to share your code, fellow students and mentors can see it on GitHub or fork it and run it too!
- You setup a Heroku account and can deploy your project there, also from the start.
- By using a database provided / hosted by Heroku, you do not need to install a DB engine or plugins locally on your machine.
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
- A local installation of Postgres: The instructions given here will allow you to connect to the DB hosted in Heroku, even when you are running locally. Regardless, there are a few steps that may not work if you have no local Postgres installed. These are: 
  - the install of dependency `psycopg2` (you can workaround this one by installing `psycopg2-binary` instead)
  - Connecting to the Heroku db by using `heroku pg:psql`. To ensure this step will work fine, try executing the command `psql` from your command line. If the command is found, even when you see some error in connection to server or similar, you are OK. Only if the command is not found / recognized, then you might need to add this to your PATH. 

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

```
pip3 install Flask
pip3 install gunicorn
pip3 install psycopg2
pip3 install Flask-SQLAlchemy
pip3 install Geoalchemy2
pip3 install shapely
pip3 install flask_cors
pip3 install flask_wtf
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

## Setting up the Heroku cli and creating a Heroku app with a Posgres DB

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

Now we will create a new app inside your Heroku account. For that you need a unique name. I chose 'mduhagon-web-201-heroku-flask' for mine. Wherever you see this name in my commands, replace it with **your app name**.

To create the app, run:

```
heroku create mduhagon-web-201-heroku-flask
```

if it works, you will see an output like this:

```
Creating ⬢ mduhagon-web-201-heroku-flask... done
https://mduhagon-web-201-heroku-flask.herokuapp.com/ | https://git.heroku.com/mduhagon-web-201-heroku-flask.git
```

Now, we want to add a PostGres database to our app (hobby-dev is the free version):

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

As the last step in setting up our database, we want to install PostGis, the extendion library to deal with geolocated data.
To be able to do this we need our database name, in my example that is 'postgresql-parallel-63698' (notice that is mentioned on the output when we created the db, otherwise you can see the db name from the Heroku web console)

```
sudo heroku pg:psql postgresql-parallel-63698
```

This will open a command line for you to run commands on your database. Run the following:

```
CREATE EXTENSION postgis;
```

You should see the following output if the install went fine:

```
CREATE EXTENSION
```

Use 'exit' to get out of the db command line.

## Running the app locally

First, you want to get the app running locally, because if something did not work, it is easier to see what the issue is on your own machine than it is to do many Heroku deploys for each problem.

To run the sample code you copied from this template, two environment variables need to be set:

- DATABASE_URL: this is the connection string for the PostGres database. Because the DB is hosted by Heroku, it also defines the user / password / etc for us. And these are 'ephemeral' credentials that heroku will rotate periodically to make your db more secure. We don't know how often the credentials change, but we should assume they will, so no hardcoding these anywhere. To get the proper value you can use the heroku cli, and below you get a bit of command line magic to directly put that into a local env variable.
- GOOGLE_MAPS_API_KEY: You need to get this for yourself. It will be sent to the Google Maps API to render the map on the initial page of the sample app.

So, before running the flask app locally, set the two environment variables like this:
#### These commands will work on Ubuntu, and maybe also on Mac:

The first export requires you are authenticated with the heroku cli, so if you have not done that resently, run ```sudo heroku login``` first. Then run:
Also! replace 'postgresql-parallel-63698' with the name of your database! You have looked for that in the step above

```
export DATABASE_URL=`sudo heroku pg:credentials:url postgresql-parallel-63698 | sed -n 5p | sed -r 's/\s+//g'`
export GOOGLE_MAPS_API_KEY=ssdfsdfsAAqfdfsuincswdfgcxhmmjzdfgsevfh
```

#### For Windows or in case you do not have sed installed

The command for exporting the DATABASE_URL above is using some additional utility (sed) to get the value directly from the output from the heroku client query. This is useful, but maybe you do not have sed, or you are running these commands on Windows.

In that case you can do a little bit more manual work to get the same result: 

First call Heroku to get the db URL: 

```
sudo heroku pg:credentials:url postgresql-parallel-63698
```

OR:

```
sudo heroku pg:credentials:url postgresql-parallel-63698 -a mduhagon-web-201-heroku-flask
```
Again, you need to replace 'postgresql-parallel-63698' with the name of your own database. Also, if Heroku complains about `Error: Missing required flag: -a, --app APP  app to run command against ` then add the flag -a` like above but using your own app name.

This will output something like this:

```
$ sudo heroku pg:credentials:url postgresql-parallel-63698
Connection information for default credential.
Connection info string:
   "dbname=xxxxxxxxxxxxxx host=ec2-XXX-XXX-XXX-XXX.compute-X.amazonaws.com port=XXXX user=XXXXXXX password=XXXXXXXXXXXXXX sslmode=XXXXXX"
Connection URL:
   postgres://XXXXXXX:YYYYYYYYYYYYYYYYYYYYYYY@ec2-XXX-XXX-XXX-XXX.compute-X.amazonaws.com:XXXX/XXXXXXXXXXXXXXX
```

What we want to set as `DATABASE_URL` is the value shown as Connection URL, that starts with 'postgres://'
You can copy that value from the output and use it to set the variable. 

In Windows, that would look like this:

```
SET DATABASE_URL=postgres://XXXXXXX:YYYYYYYYYYYYYYYYYYYYYYY@ec2-XXX-XXX-XXX-XXX.compute-X.amazonaws.com:XXXX/XXXXXXXXXXXXXXX
SET GOOGLE_MAPS_API_KEY=ssdfsdfsAAqfdfsuincswdfgcxhmmjzdfgsevfh
```

The value for GOOGLE_MAPS_API_KEY is just a dummy value, you need to get the real api key value from your Google Apps console and use that value instead.
Remember never to commit this API key to your repo because that is public and the key could get exploited / used by other people. Use of Google Maps API costs money after some limits, so be careful.

It will help to have these commands handy, you will need to rerun them every time you start working on your app locally on a new instance of your command line.

If you want to verify the values of the env variables, use:

on Linux / Mac:
```
echo $DATABASE_URL
echo $GOOGLE_MAPS_API_KEY
```

on Windows:
```
echo %DATABASE_URL%
echo %GOOGLE_MAPS_API_KEY%
```

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

```
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
