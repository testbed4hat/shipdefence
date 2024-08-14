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

.PHONY: compile-templates

compile-templates:
	$(PROVCONVERT) -templatebuilder templates/config.json
	cd $(OUTPUTS)/generated/java/templates; mvn clean install


$(OUTPUTS)/generated/bin/prov4serge: compile-templates

$(OUTPUTS)/provenance:
	mkdir -p $@

$(OUTPUTS)/provenance/wargame-lzmnr7lj.provn: $(OUTPUTS)/provenance $(OUTPUTS)/generated/bin/prov4serge csv/wargame-lzmnr7lj.csv
	$(OUTPUTS)/generated/bin/prov4serge -i csv/wargame-lzmnr7lj.csv -o $@


provenance: $(OUTPUTS)/provenance/wargame-lzmnr7lj.provn $(OUTPUTS)/provenance/wargame-lzmnr7lj.json $(OUTPUTS)/provenance/wargame-lzmnr7lj.pdf
