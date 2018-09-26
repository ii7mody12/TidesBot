# TidesBot
My personal discord bot.

To run the bot you need you to get a token, which is explained [here](https://github.com/reactiflux/discord-irc/wiki/Creating-a-discord-bot-&-getting-a-token).
Once you do that, create a token.json file that looks like like the token_template.json file.
```

## Commands
!help: List all the command categories

### General
!Purge x user(optional): Deletes x amount of messages. Optionally you can delete the messages of a certain user.
reloadmodules: Reloads all modules. This happens globally, so it's restricted to owner only.
!load x: Loads a module. Owner only.
!unload x: Unloads a module. Owner only.
!Choose a b c...: Choose one of the options given.
!say x: The bot states whatever is typed.

### Music
!join: Joins the voice channel the user is in.
!leave:** Leaves the voice channel.
!play x:** Plays the link given, or searches youtube for whatever is typed. Can also play twitch streams.
!playlist x:**  Queues the songs in the playlist given.
!stop:** Stops playing whatever is currently playing. You have to be in the voice channel.
!pause:** Pauses whatever is currently playing. You have to be in the voice channel.
!resume:** Resumes whatever was playing.
!currentSong:** States whatever is currently playing.
!skip:** Vote to skip the current song. Whoever queued the song can skip the vote instantly.
!clearQueue:** Clears the song queue.
!queue:** List the next 5 songs.
!volume x.x:** Change the volume. Must be a value between 1 and 100.

### User
!addrole a b c d....:** Add (a) role(s) that users can assigned themselves to.
!removerole a b c d....:** Remove (a) role(s) that users could assign themselves to.
