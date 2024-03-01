# Using [Bovine](https://bovine.readthedocs.io/en/latest/tutorials/server/)

View actor info
```sh
# Look up actor id (type application/activity+json) for a handle
curl https://mas.to/.well-known/webfinger?resource=acct:themilkman@mas.to | python -m json.tool
# Get the actor object
curl -H accept:application/activity+json https://mas.to/users/themilkman | python -mjson.tool
```

The actor object has a `preferredUsername` and a `publicKeyPem` to authenticate activities as coming from this actor.

URL examples:
```json
"following": "https://mstdn.social/users/santisbon/following",
"followers": "https://mstdn.social/users/santisbon/followers",
"inbox": "https://mstdn.social/users/santisbon/inbox",
"outbox": "https://mstdn.social/users/santisbon/outbox",
```