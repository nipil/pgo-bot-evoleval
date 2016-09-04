# pgo-bot-evoleval

Evaluate evolutions from PokemonGo-bot data


# How to use

Run `evoleval.py` python script, providing the path to your PokemonGo-bot installation :

	python evoleval.py ~/git/PokemonGo-bot

You will get a bunch of files appearing in the current folder with the extension `.adoc`. Run Asciidoctor to generate nice html reports from these :

	asciidoctor *.adoc

Open these `.html` files in you browser and get the information !


# Pre-requisites

## Do once :

* install required package `asciidoctor`
* install required package `virtualenv`
* clone [PokemonGo-bot](https://github.com/PokemonGoF/PokemonGo-Bot)
* go inside pgo-bot directory, run `./setup.sh -i`

Refer to that project documentation if you have any problem.

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

Modifying `pokecli.py` ensures that the bot does not run and does not do any actions, except connecting to the account, getting inventory and stuff, and disconnecting. That way, the bot does not do any action, no catching, no walking, nothing.

## Refresh data

Every time you want to get your fresh profile, launch modified PokemonGo-Bot :

* run `./run.sh`
* press `Ctrl+C` when you see the line `Press any button or wait 20 seconds to continue`
