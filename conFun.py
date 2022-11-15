
from ast import parse
import json,http.client,urllib.parse

connection = http.client.HTTPSConnection('parseapi.back4app.com', 443)
params = urllib.parse.urlencode({"where":json.dumps({
       "objectId": "h7i5diCpZ8"
     })})
connection.connect()

connection.request('GET', '/parse/classes/FirstClass?%s' % params, '', {
       "X-Parse-Application-Id": "fI2nXFCZqUDYpWU4WjmArSjrngmM3eZInw0nTRAS",
       "X-Parse-REST-API-Key": "JTyGVxAinbo1EkLhWOx3NTlk7KNk7nMscP0YGgtv"
     })
result = json.loads(connection.getresponse().read())
print (result)