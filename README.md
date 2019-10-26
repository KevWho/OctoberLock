# August OAuth and REST Example #

### What is this repository for? ###

This example uses basic Python `requests` to get an OAuth access token from August Home.
Then it uses more `requests` to get a list of all your August Smart Locks and (optionally) lists the details of a specific lock.

### How do I get set up? ###

* Contact August Home and establish a relationship to develop your application.
* Prepare a list of HTTPS URLs that can be used for the OAuth webhooks. You will need to register these with August Home. Suggestion: for development, include at least one localhost callback. You can use HTTP for development, but you **must** use HTTPS for production.
* [optional] Install Docker. This makes it simple to run this app.

### Build and Run ###

You can build and run this with:

```
#!bash

docker build -t augustoauth .
docker run -d --name myauthtest --env-file <full path to environment file> -p 5000:5000 augustoauth
```

**Note** that if you're running Docker in a VM (as with `docker-machine` on a Mac or PC), you'll need to set up Port Forwarding for port 5000 out to the host machine (so on the host it might not be 5000). The port exposed on your host machine must match the port you listed in a webhook you registered with August.

#### Get debugging logs ####


```
#!bash

docker logs myauthtest
docker exec myauthtest cat augustdebug.txt
```

If you're using Docker, the `env-file` should look like this (variable names required, values come from you and August). Otherwise, if you're running this natively, just set these as environment variables.

```
#!bash

CLIENTID=12345678-9012-3456-7890-123456789012
APIKEY=a1b2c3d4-e5a1-b2c3-d4e5-a1b2c3d4e5a1
APISEC=thisISaBigSecretStringThatYouShouldProtect0=
AUTHCALL=http://localhost:30368/callback
```

**Note** that `AUTHCALL` must match one of the callbacks you gave to August when you requested API keys.
`CLIENTID, APIKEY, and APISEC` all come from August when you set up your development relationship.

## Source Code Notes ##

`request` vs `requests`:

* `request` is a global object available from the Flask package. Accessing it gives you information about the incoming request, including headers, query parameters, and any posted body.
* `requests` (note the **s**) is Python package which simplifies making HTTP requests.

So, _request_ parses **incoming** information, and _request**s**_ makes **outgoing** HTTP calls and encapsulates the responses.

## Origins of Code ##

This example started as sample code for [`requests-oauthlib`](https://requests-oauthlib.readthedocs.org/en/latest/examples/real_world_example.html) (which itself came from [this gist](https://gist.github.com/ib-lundgren/6507798)) but then I removed all the oauthlib code so that I could show the oauth requests explicitly.