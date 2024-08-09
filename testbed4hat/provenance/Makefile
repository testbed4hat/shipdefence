PROVCONVERT:=provconvert
PROVMAN:=provmanagement
PYPROVCONVERT:=prov-convert

OUTPUTS:=outputs

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

.PHONY: compile-templates provenance

compile-templates:
	$(PROVCONVERT) -templatebuilder templates/config.json
	cd $(OUTPUTS)/generated/java/templates; mvn clean install


$(OUTPUTS)/generated/bin/prov4serge: compile-templates

$(OUTPUTS)/provenance:
	mkdir -p $@

$(OUTPUTS)/provenance/wargame-lzind2c4.provn: $(OUTPUTS)/provenance $(OUTPUTS)/generated/bin/prov4serge csv/wargame-lzind2c4.csv
	$(OUTPUTS)/generated/bin/prov4serge -i csv/wargame-lzind2c4.csv -o $@


provenance: $(OUTPUTS)/provenance/wargame-lzind2c4.provn $(OUTPUTS)/provenance/wargame-lzind2c4.json $(OUTPUTS)/provenance/wargame-lzind2c4.pdf
