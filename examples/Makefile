DEF=en
ALL=de fr ja pt_br ru zh_cn zh_hk zh_tw
CMD=python ../evoleval.py ~/git/PokemonGo-Bot/

all: clean generate filter

clean:
	rm -Rf $(ALL) $(DEF)

generate:
	mkdir -p $(ALL) $(DEF)
	for L in $(ALL); do $(CMD) --locale $$L ; mv -f inventory-*.adoc $$L; asciidoctor $$L/*.adoc; done
	$(CMD) ; mv -f *.adoc $(DEF) ; asciidoctor $(DEF)/*.adoc

filter:
	find -type f -iname 'inventory-*'|grep -v 'test.*html' | xargs rm -v
