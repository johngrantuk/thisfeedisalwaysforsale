Start local blockchain:
$ npm run chain

cd thisartworkisalwaysonsale
truffle migrate
Note address of ERC721Full and ArtSteward

cd project
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser

python manage.py runserver
App will be available at: http://127.0.0.1:8000/

App will be available at: http://127.0.0.1:8000/admin
Art steward address:
Erc721 address:

Change MetaMask to Localhost 8545

http://127.0.0.1:8000/feed_admin/
Create Policy

Add text description, etc
Add Patron info and buy options
Helper to load db feed examples
Video


Tried a Heroku deployment but got the following:
2019-04-04T16:59:31.076241+00:00 heroku[web.1]: Process running mem=1212M(236.7%)
2019-04-04T16:59:31.076315+00:00 heroku[web.1]: Error R15 (Memory quota vastly exceeded)
2019-04-04T16:59:31.076474+00:00 heroku[web.1]: Stopping process with SIGKILL
2019-04-04T16:59:31.241084+00:00 heroku[web.1]: Process exited with status 137
