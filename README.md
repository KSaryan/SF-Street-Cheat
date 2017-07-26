# SF StreetCheat
SF StreetCheat is a 4 week project that I completed during my time as an software engineering fellow at Hackbright Academy. SF StreetCheat helps San Francisco residents avoid expensive parking tickets. With street cleaning happenign at different time on different sides, different bloacks, and evendifferent sides oft he same black, it can be difficult to remember when you need 
to move your car. Even if you do check the sign, you cna get distract and forget to move it in time. SF StreetCheat uses the data provided by DataSF through the Soda API, along with the Goggle Maps, SendGrid,  and Twilio APIs to not only show users how long they have until street clenaing, but also to send them texts or emails reminding them to move thir car before street 
cleaning time. This way they can go about their day or week knowing they won't come back to their car only to face a hefty ticket. SF StreetCheat also helps users find nearby streets that have street cleaning times that better fit their needs.

## Contents
* [Technologies](#technologies)
* [Database Model](#database model)
* [Features](#features)
* [Installation](#install)

## <a name="technologies"></a>Technologies
<b>Backend:</b> Python, Flask, PostgreSQL, SQLAlchemy<br/>
<b>Frontend:</b> JavaScript, jQuery, AJAX, Jinja2, Bootstrap, HTML5, CSS3<br/>
<b>APIs:</b> SODA, SendGrid, Twilio, Google Maps<br/>

## <a name="database model"></a>Database Model
![alt text](screenshots/database diagram dark version.png "database model")

## <a name="features"></a>Features
users can choose to log in or begin using the site
![alt text](screenshots/RecruiterHome.png "Recruiter Home")

Their currently location in autofilled and they confirm or fill in another
![alt text](screenshots/Recruiter_Studies.png "All Studies")

The sides of the street that match their location are filled into the dropdown for them to choose from
![alt text](screenshots/Recruiter_NewStudy.png "New Study")

They get information about street cleaning and towing
![alt text](screenshots/Recruiter_Screener.png "Screener")

They can search for other information about other street clenaing locations in their neighborhood
![alt text](screenshots/Recruiter_Screener.png "Screener")

And filter those locations to match their needs
![alt text](screenshots/Recruiter_Screener.png "Screener")

Once they log in
![alt text](screenshots/Recruiter_Search.png "Search Potential Participants")

They can receive text reminders
![alt text](screenshots/Recruiter_Email.png "Email")

Or check on favorite or recent locations
![alt text](screenshots/Recruiter_Screener.png "Screener")


## <a name="features"></a>Installation
To run Recruiter:

Install PostgreSQL (Mac OSX)

Clone or fork this repo:

```
https://github.com/KSaryan/SF-Street-Cheat
```

Create and activate a virtual environment inside your Recruiter directory:

```
virtualenv env
source env/bin/activate
```

Install the dependencies:

```
pip install -r requirements.txt
```
Sign up to use the SendGrid API (https---
Sign up to use the Twilio API (https---

Save your API key in a file called <kbd>secrets.sh</kbd> using this format:
```
export TWILIO_ACCOUNT_SID="YOUR_ACCOUNT_SID_GOES_HERE"
export TWILIO_AUTH_TOKEN="YOUR_AUTH_TOKEN_GOES_HERE"
export TWILIO_NUMBER="YOUR_NUMBER_GOES_HERE"
export SENDGRID_API_KEY="YOUR_API_KEY_GOES_HERE"
```

Source your keys from your secrets.sh file into your virtual environment:

```
source secrets.sh
```

Set up the database:

```
python model.py
```
```
python seed.py
``` 

Run the app:

```
python server.py
```

You can now navigate to 'localhost:5000/' to access SF StreetCheat.
