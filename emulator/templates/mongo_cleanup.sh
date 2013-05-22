#!/usr/bin/env bash

mongo db --eval "
        db.getCollection('rftable').drop();
        db.getCollection('rfconfig').drop();
        db.getCollection('rfstats').drop();
        db.getCollection('rfclient<->rfserver').drop();
        db.getCollection('rfserver<->rfproxy').drop();
    "

service mongodb restart

echo "SCRIPTFINISHED"
