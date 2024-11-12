PROVCONVERT:=provconvert
PROVMAN:=provmanagement
PYPROVCONVERT:=prov-convert

OUTPUTS:=outputs

GAME_ID:=wargame-lzudwjdd
TEMPLATE_INPUTS:=$(wildcard templates/*.provn) $(wildcard templates/*.json)

# Generic rules to convert PROV-N to TTL or to SVG/PDF formats
%.json: %.provn
	$(PROVCONVERT) -infile $< -outfile $@

%.ttl: %.provn
	$(PROVCONVERT) -infile $< -outfile $@

%.svg: %.json
	$(PYPROVCONVERT) -f svg $< $@

%.pdf: %.json
	$(PYPROVCONVERT) -f pdf $< $@

%.png: %.json
	$(PYPROVCONVERT) -f png $< $@

.PHONY: provenance clean test

$(OUTPUTS)/generated/bin/prov4serge: $(TEMPLATE_INPUTS)
	$(PROVCONVERT) -templatebuilder templates/config.json
	cd $(OUTPUTS)/generated/java/templates; mvn clean install

$(OUTPUTS)/provenance:
	mkdir -p $@

$(OUTPUTS)/provenance/$(GAME_ID).provn: $(OUTPUTS)/provenance $(OUTPUTS)/generated/bin/prov4serge csv/$(GAME_ID).csv
	$(OUTPUTS)/generated/bin/prov4serge -i csv/$(GAME_ID).csv -o $@


provenance: $(OUTPUTS)/provenance/$(GAME_ID).provn $(OUTPUTS)/provenance/$(GAME_ID).json $(OUTPUTS)/provenance/$(GAME_ID).pdf

clean:
	rm -rf $(OUTPUTS)/provenance/*

test:
	@echo $(TEMPLATE_INPUTS)