### Relevant APIs need to be enabled

- app engine function (https://console.developers.google.com/appengine)
- cloud task queues (`gcloud tasks queues create sheets-append`)

### OPPORTUNITIES TO EXCEL:

- add workspace column to output
- [DONE] add reporter column
- [DONE] add number of PAX selected to picker
- [DONE] add field for non-CARPEX PAX
- add a message showing totals for the day
- Change the message to come from the Q and/or the user posting
- If backblast length exceeds some amount, only post the full backblast in a thread
- Allow tagging users in backblast text itself
- [DONE] Special field for PAX not in slack (renamed the additional FNGs field)
- Enable editing of existing backblast messages from the current post

### Notes:

- The gcloud auth step in github actions _requires that the json service account credentials are base64 encoded_
  - Run `cat service_account_credentials.json | base64`
- Duplicate slack posts occur when there's a duplicate delivery of the message,
  which can result from a crash on the subscribing cloud function, for example
  when a session connection has expired.

### Development:

Use the `develop` branch for development.
The Pipfile supports development with `pipenv`.