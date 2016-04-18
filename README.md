# Assetnote

![logo](http://i.imgur.com/nY80uWj.png)

Assetnote notifies you of assets that have been found through scraping passive data stores. By using [Pushover's](https://pushover.net) push notification API, as soon as a new subdomain is found for an asset, a push notification is sent to your mobile phone (iOS/Android) with the data found.

For public release, I have included an example `manager` script for assetnote. This is Threatcrowd's public yet passive DNS data store. Assetnote can be extended very easily by writing scripts that interact with the `assetnote.db` SQLite database. The more scripts that have been made to scrape data sources, the more success one will have with this tool.

## Screenshots

Login:

![login](https://i.imgur.com/ZkwWrga.png)

Sent notifications:

![sent](https://i.imgur.com/R1ShMcG.png)

Adding assets:

![assets](https://i.imgur.com/xZWHiLB.png)

Push notification assets seen on the phone:

![notifications](https://i.imgur.com/71SzMB4.png)

## Concepts

Assetnote is simply a web interface around the SQLite database `assetnote.db`. This database contains two columns, one that stores the domains that you'd like to monitor and another that stores every found subdomain through managers.

The core concept is that when a script within the `managers` folder finds a new subdomain, it is inserted as a domain in the `sent_notifications` column of the SQLite database. This ensures that you don't receive notifications of subdomains you already know about.

## Installation

The installation process is annoying - if I get bugged about this enough, I'll work on making it easier.

This is a full installation guide for a Debian server hosted on Digital Ocean. This should cover most people, even those with very basic devops knowlege.

1. Run the following commands to get a MySQL server installed:

```
sudo apt-get update
sudo apt-get install mysql-server
sudo mysql_secure_installation
sudo mysql_install_db
```

You'll have to provide a password to set up the MySQL server.

When running `mysql_secure_installation`, use the following answers:

```
Change the root password? [Y/n] n
 ... skipping.

 Remove anonymous users? [Y/n] y
 ... Success!

 Disallow root login remotely? [Y/n] y
 ... Success!

 Remove test database and access to it? [Y/n] Y
 - Dropping test database...

 Reload privilege tables now? [Y/n] Y
 ... Success!
```

2. Create a database for Assetnote on your MySQL server:

```
$ mysql -uroot -p

# login with your mysql user set up in step 1

# create the assetnote database

mysql> CREATE DATABASE assetnote;
Query OK, 1 row affected (0.00 sec)

# exit

mysql> exit;
Bye
```

2. Clone this git repo:

`git clone https://github.com/infosec-au/assetnote`

3. Create a new pushover application:

Visit https://pushover.net/login and sign up:

![signup](https://cms-assets.tutsplus.com/uploads/users/317/posts/22264/image/signup.jpg)

![pushovernewapp](https://cms-assets.tutsplus.com/uploads/users/317/posts/22264/image/new-app.jpg)

4. Modify the following files:

- `config.py`

```
SECRET_KEY = 'CHANGEME'
SQLALCHEMY_DATABASE_URI = 'mysql://root:test@localhost:3389/assetnote'
SECURITY_PASSWORD_SALT = 'CHANGEME'
PUSHOVER_KEY = 'PUSHOVERKEY'
```

Change the above configuration to have random, hard to guess secret keys/salts. Change the database credentials as needed.

Put your pushover's application key in `PUSHOVER_KEY`.

- `assetnote.py`

Line 21: Modify this to use your database credentials instead

```
engine = sqlalchemy.create_engine('mysql://root:testing@localhost:3389/assetnote')
```

Line 59: Change the username and password that will be used to login to assetnote

```
user_datastore.create_user(email='shubs', password='testing')
```

5. Get pip:

`apt-get install python-pip`

6. Install the required headers for MySQL-python and install python-bcrypt:

`apt-get install python-dev libmysqlclient-dev`
`apt-get install python-bcrypt`

7. Install the required modules:

When your user is currently in the assetnote directory, run - `pip install -r requirements.txt`

8. Update your crontab to run your assetnote managers every 30 minutes:

`crontab -e`

`*/11 * * * * /usr/bin/timeout 30m python /home/deploy/assetnote/managers/threatcrowd.py > /home/deploy/tc_log.txt 2>&1`

This will run the script every 30 minutes and with a timeout of 30 minutes. Modify the path's as needed.

## Support / help

Contact me via Twitter if any help is needed [@infosec_au](https://twitter.com/infosec_au).

## Release details

![BSides Canberra](https://i.imgur.com/SDnAepz.png)

[bsidesau.com.au](http://bsidesau.com.au)

This was released at BSides Canberra by [@infosec_au](https://twitter.com/infosec_au) and [@nnwakelam](https://twitter.com/nnwakelam) for the talk "Scrutiny on the bug bounty".