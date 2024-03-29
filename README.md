![Django CI](https://github.com/flkoch/training_planner/workflows/Django%20CI/badge.svg)
# Training Planner
Django app to track training registration and participation

## Current status
This project was developped for my local judo club in order to track registration and participation in times of COVID-19. In order to keep the requirements on the hardware as low as possible, all the configuration is done in source. The text is currently displayed in German and adheres to our requirements. All text fields are translatable and even the whole application can be served in multiple languages, though the user entered data cannot be translated. For customising the text you can directly edit the translation files or create translations for additional languages and set them as default in the `settings.py` file. For details see the django documentation for internationalisation.

## Requirements
The requirements are kept upto-date in the `requirements.txt` file. It is tested to run on Ubuntu-2004 but should work on any unix operating system with python3.

## Installation
In order to install and use the system for your own purposes, you should first clone the repository and adopt the static information as neccessary. A good starting point is the template files located in the app folders under templates and ending in `.html`. Further information is embedded directly from the views, models and forms, located in the respective files.

The local settings are loaded from environment variables. The following variables are loaded in `settings.py`and should be set to allow proper functionality. Their names should be self-explanatory, otherwise you can see where they are loaded in `settings.py`and search for the respective settings and allowed values.
```
PYTHON_DJANGO_DB_ENGINE
PYTHON_DJANGO_DB_NAME
PYTHON_DJANGO_DB_HOST
PYTHON_DJANGO_DB_USER
PYTHON_DJANGO_DB_PASSWORD
PYTHON_DJANGO_EMAIL_BACKEND
PYTHON_DJANGO_EMAIL_HOST
PYTHON_DJANGO_EMAIL_PORT
PYTHON_DJANGO_EMAIL_USE_SSL
PYTHON_DJANGO_EMAIL_USER
PYTHON_DJANGO_EMAIL_FROM
PYTHON_DJANGO_EMAIL_PASSWORD
PYTHON_DJANGO_SECRET_KEY
PYTHON_DJANGO_STATIC_ROOT
```
Once you have made the necessary adoptions, you are ready for deployment. You can follow for example the instruction on [DigitalOcean](https://www.digitalocean.com/community/tutorials/how-to-set-up-django-with-postgres-nginx-and-gunicorn-on-ubuntu-18-04), where instead of creating a new project you can clone your customised repository. When creating the `gunicorn.service` file, in the `[service]` section make sure to include `EnvironmentFile=` followed by the absolute path to a file containing your environment variables in the format `variable='value'` without any export directives. Only then gunicorn will be able to load the environment variables and start the server.

Once everything is working, you should finalise the deployment by switching the debug flag in `setting.py` to false and entering the allowed hostname in the same field. Make sure everything turns up when restarting the machine. As a last word of caution keep in mind that this is potentially a public-facing server which should be secured accordingly, including regular security upgrades, limiting ssh-access, proper firewall configuration and SSL-certificates for transmitting passwords upon registration.

## First Use
After setting up a new instance of this service you should log in with the superuser created from the commandline and supply as much additional information as you like. The following groups are created automatically.
```
Participant
Active Participant
Trainer
Active Trainer
Administrator
System
```
These groups  will partially be applied automatically. Trainer, Administrator and System groups have to be assigned manually through the admin interface. Only members of the Trainer group can create trainings, edit their own trainings, view member details and track participation. Members of the group Administrator can edit any training. The group System is applied to users which are non-regular users and should not be displayed on selection forms in the front-end.

You can also go about and add additional permissions to these groups to your liking. These permissions are only checked at the admin interface level. In order for the user to be able to reach this interface, they have to be marked as staff.
# Contribution
As currently many clubs might have similar difficulties of finding an easy tool for registration and participation tracking for their training sessions, I decided to make this tool available for everyone. I know that there is probably dozens of ways to improve the tool and am steadily working on improving existing funtionality and adding new function. If you notice any bugs or want to add any new features, make it easier for others to adopt, feel free to create an issue or a pull request.

When setting up your own VPS to host this application or other projects, you can give a try to [Vultr](https://www.vultr.com/?ref=8530062). I have been using them myself and have been satisfied with their services. By creating an account with the provided link you get free credit to try out and if you stay I will also get some credit.

If you want to support the project in any other way, feel free to contact me directly.
