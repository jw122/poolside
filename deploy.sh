#!/bin/bash

export PYTHONPATH=/google/google_appengine/lib/:/google/google_appengine/lib/webapp2-2.5.2:/google/google_appengine/lib/webob-1.2.3

production_app=poolside-finance

cd /Users/jamesl/Dropbox/Poolside/poolside-finance;
echo "Deploying to Production"
echo "gcloud -q app deploy --project $production_app "
gcloud -q app deploy --project $production_app
echo "gcloud -q app deploy cron.yaml --project $production_app "
gcloud -q app deploy cron.yaml --project $production_app
