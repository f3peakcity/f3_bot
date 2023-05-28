# Local Development

Set up an environment with application default credentials that will support include the spreadsheet scope to allow local development similar to what the cloud function will support.

```
gcloud auth application-default login --scopes=https://www.googleapis.com/auth/spreadsheets,openid,https://www.googleapis.com/auth/userinfo.email,https://www.googleapis.com/auth/cloud-platform
 gcloud auth application-default set-quota-project f3-carpex
 ```

# Github Action Permissions

I followed this setup: https://github.com/google-github-actions/auth#setup