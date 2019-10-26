FROM python:2-onbuild
RUN apt-get update; apt-get install -yq nano
CMD python /usr/src/app/augustoauth.py

# This Dockerfile is simple because it makes heavy use of ONBUILD commands in the base image.
# https://github.com/docker-library/python/blob/master/2.7/onbuild/Dockerfile
# 
# You can build and run this with:
# docker build -t augustoauth .
# docker run -d --name myauthtest --env-file <full path to environment file> -p 5000:5000 augustoauth
#
# Get debugging logs with:
# docker logs myauthtest
# docker exec myauthtest cat augustdebug.txt
#
# The environment file should look like this (variable names required, values come from you and August)
# CLIENTID=12345678-9012-3456-7890-123456789012
# APIKEY=a1b2c3d4-e5a1-b2c3-d4e5-a1b2c3d4e5a1
# APISEC=thisISaBigSecretStringThatYouShouldProtect0=
# AUTHCALL=http://localhost:30368/callback
#
# Note that AUTHCALL must match one of the callbacks you gave to August when you requested API keys.
# CLIENTID, APIKEY, and APISEC all come from August
