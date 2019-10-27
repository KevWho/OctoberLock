# OctoberLock - Made @ Cal Hacks 6.0 #

Integrating August's smart locks and doorbell cams with Google's Vision API to verify the number of guests entering an Airbnb property throughout the renter's stay.

### What is this repository for? ###

The webapp notes the building's approximate population over time by counting the number of people that go in and out of the building. Whenever guests unlock the door to the home, the webapp begins accessing and analyzing outdoor footage from the doorbell camera using Google's vision API. The approximate flow of people over time is stored and made available graphically and numerically to the homeowner, making it easy and quick to determine when a threshold has been crossed.

### Running ###

You will need to have a Google Application Credentials plist file.

An instance of the backend is running at https://olock.kevin-hu.org. You can run the backend api with:

```
python app.py
```

You can run the webapp (Dashboard) with:

```
cd webapp
npm start
```
