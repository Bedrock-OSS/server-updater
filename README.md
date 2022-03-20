# server-updater

A simple app to listen for bedrock-oss app changes and deploy them on the server. Is used with [query-endpoint-action](https://github.com/bedrock-oss/query-endpoint-action) to update processes from GitHub but should work with other clients. 

## How does it work?

As a general summary, server-updater runs as a process, and listens for update requests, then updates the respective process code and restarts it. 

The update process looks like this:
A client requests the `/deploy` endpoint with query arguments `id` (the id of the repo in the bedrock-oss org to update) and `secret` (a secret contained in a config file on the server to verify the request). The server responds with status code `202` and data `Deploying` while it begins updating the process. While deploying, all requests to `/deploy` will be given `202` (`Already deploying`). The client can query the process information and while deploying a `202` (`Processing`) will be returned. When the process is finished updating, a `200` (`Running`) is returned. If there is any error updating, a `500` (`Error {the error}`) is returned. 

Server side, a process is updated by:
- Stopping the process
- Delete the link from the web server to the `public` folder
- Running `git pull` in the project directory
- Starting the process, if it was running when deployed
- If config specifies a `public` folder, create a symlink. 

## Other requirements/setup

All processes managed by server-updater are expected to be systemctl processes with names beginning with `bedrock-oss:`. They are all expected to run in the `repos` folder relative to the updater script. 

## Contributing

Feel free to contribute however you want! A couple ideas are marked under issues. 
