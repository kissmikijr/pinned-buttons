# Pinned Buttons

An implementation for the Riot Games pinned buttons application.

To create your own slack application you can use the `pinned-buttons-app-manifest.yaml` file.

You need to provide the following environment variables for the app:

```
MONGO_DB_CONNECTION_STRING=<a mongo db connection string>
PINNED_BUTTONS_SLACK_BOT_TOKEN=<the bot token of the slack app you  created>
PINNED_BUTTONS_SLACK_APP_TOKEN=<the app token of the slack app you  created>
```

# Development

create a `.env` file in the root of the repository.
Provide the environemnet variables for the app.
