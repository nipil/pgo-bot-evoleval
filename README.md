# OBSOLETE

This repository has been archived and will not be updated anymore.

# pgo-bot-evoleval

Evaluate evolutions from PokemonGo-bot data


# How to use

Run `evoleval.py` python script, providing the path to your PokemonGo-bot installation :

	python evoleval.py ~/git/PokemonGo-bot

You will get a bunch of files appearing in the current folder with the extension `.adoc`. Run Asciidoctor to generate nice html reports from these :

	asciidoctor *.adoc

Open these `.html` files in you browser and get the information !

# Customize

Look at the command-line `--help` to see what is available.

Most importantly, you can (should ?) configure the duration it takes to evolve a pokemon *on the device used to do the batch of evolutions*. That duration must equal the **animation time + the time spent in menus** needed to start the next one. As an example, on my phone, the full cycle requires 26 seconds, which is used as a default for the `--evolve-time` parameter (in seconds)

You can select the languate used for the *names of the pokemons* : use the `--locale` with one of the accepted values to select desired language (english is selected by default)

And if Niantic ever changes the duration of the Lucky Egg, you may configure it using the `--egg-time` parameter (in minutes)

# Prerequisites

## Do once :

* install required package `asciidoctor`
* install required package `virtualenv`
* clone [PokemonGo-bot](https://github.com/PokemonGoF/PokemonGo-Bot)
* go inside pgo-bot directory, run `./setup.sh -i`

Refer to that project documentation if you have any problem.

Deactivate sleep schedule so that you don't wait when getting your data :

* edit `config/config.json`
* find the section named `"sleep_schedule"`
* edit the `"enable"` line just below it
* replace `true` with `false`

## Do every once in a while (get PokemonGo-bot updates)

* go inside pgo-bot directory
* run `git reset --hard`
* run `./setup.sh -u`
* open `pokecli.py` with a text editor
* search for text : `bot = start_bot`
* add the following text after that line `return`
* warning: respect text alignement, and use spaces, not tabs

Text before modification.

    while not finished:
        try:
            bot = initialize(config)
            bot = start_bot(bot, config)
            config_changed = check_mod(config_file)

Text after modification

    while not finished:
        try:
            bot = initialize(config)
            bot = start_bot(bot, config)
            return
            config_changed = check_mod(config_file)

Modifying `pokecli.py` ensures that the bot does not run and **does not do any actions**, except connecting to the account, getting inventory and stuff, and disconnecting. That way, the bot does not do any action, **no catching, no walking, nothing is done**.

## Refresh data

Every time you want to get your fresh profile, launch modified PokemonGo-Bot :

* run `./run.sh`
* press `Ctrl+C` when you see the line `Press any button or wait 20 seconds to continue`
