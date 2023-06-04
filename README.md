## Adding a new region

1. Add a new github environment for the region, and add a secret called SLACKBOT_ENV_VARS using the format below.
2. Add a new slack app for the region, using the mainfest file below; install the app in the region's workspace. You will need the signing secret and bot token.
3. Add a new env file for the region in the `env` directory
- The env file should be named `env-<region>.yml`
- Look up the region's slack workspace id in the app installation section of `api.slack.com`
- Look up the user ids for users who will be allowed to use `/paxmate say` by viewing their profile in slack and choosing "Copy Member ID"
- Look up the channel ids for the 1st F and 3rd F channels
- You can use the same spreadsheet id, or create a new one. If you create a new one, ensure that 
f3-carpex@appspot.gserviceaccount.com has edit access to the sheet.
4. Add a new deployment file for the region in the `.github/workflows` directory
5. Add AO Reference information to the AO Reference sheet in the spreadsheet (for data workflow)
6. Update dashboard

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
The Pipfile supports development with `pipenv` for each component individually.

SLACKBOT_ENV_VARS example:
```
SLACK_BOT_TOKEN=xoxb-<>,SLACK_SIGNING_SECRET=donotshare,COCKROACH_CONNECTION_STRING=cockroachdb://<USERNAME>:<PASSWORD>@f3-bot-5101.5xj.cockroachlabs.cloud:26257/defaultdb?sslmode=verify-full&sslrootcert=./root.crt
```

# Note the passing of sslrootcert as a connection string parameter. This is required for the CockroachDB Python driver to connect to the database.

Slack App Manifest

```
display_information:
  name: Paxmate NEWREGIONNAME
  description: Build backblasts and track your workouts!
  background_color: "#000000"
features:
  bot_user:
    display_name: paxmate-NEWREGIONNAME
    always_online: false
  slash_commands:
    - command: /backblast
      url: https://us-east1-f3-carpex.cloudfunctions.net/slackbot-NEWREGIONNAME
      description: Quick Backblast Builder
      should_escape: false
    - command: /paxmate
      url: https://us-east1-f3-carpex.cloudfunctions.net/slackbot-NEWREGIONNAME
      description: Post a message as paxmate
      usage_hint: say [message]
      should_escape: false
oauth_config:
  scopes:
    bot:
      - channels:join
      - channels:read
      - chat:write
      - commands
      - users:read
      - chat:write.customize
settings:
  interactivity:
    is_enabled: true
    request_url: https://us-east1-f3-carpex.cloudfunctions.net/slackbot-NEWREGIONNAME
  org_deploy_enabled: false
  socket_mode_enabled: false
  token_rotation_enabled: false
```