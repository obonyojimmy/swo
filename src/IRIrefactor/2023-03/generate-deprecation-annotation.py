# Read in a list of IRIs + labels and generate deprecation annotation for all of them.
# output as SPARQL update code (deprecation-annotation.ru)
#
# The resulting ru file can be run in Robot as follows
# java -jar build/robot.jar query --input swo-refactored.owl --update deprecation-annotation.ru  --output swo-completed.owl
#
# This presumes all are instances (not classes or properties)
#

infile = open("efo-iri-label.txt", "r")
outfile = open("deprecation-annotation.ru", "w")

outfile.write("prefix oboInOwl: <http://www.geneontology.org/formats/oboInOwl#>\n")
outfile.write("prefix obo: <http://purl.obolibrary.org/obo/>\n")
outfile.write("prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>\n")
outfile.write("prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>\n")
outfile.write("prefix owl: <http://www.w3.org/2002/07/owl#>\n")
outfile.write("prefix efo: <http://www.ebi.ac.uk/efo/>\n")
outfile.write("prefix efoswo: <http://www.ebi.ac.uk/efo/swo/>\n")
outfile.write("prefix swo: <http://www.ebi.ac.uk/swo/>\n")
outfile.write("\n")
outfile.write("INSERT {\n")

# There are 115 cases where the base ID had to be changed as it matched an
# already-extant "swo" ID. To make sure the "replaced by" is correct, use the
# mapping file originally used for refactoring the IRIs to provide the correct mapping values.
sharedIds = {}
with open("refactor-efo-swo-mappings.csv") as f:
    for line in f:
       (key, val) = line.strip().split(",", 1)
       sharedIds[key] = val

counter = 0

for line in infile:
  #print(line)
  if "http://www.ebi.ac.uk/efo/swo/" in line:
    parts = line.split(",")
    modified = parts[0].replace("http://www.ebi.ac.uk/efo/swo/", "efoswo:").strip()
    updatedIRI = sharedIds.get(parts[0].strip()).replace("http://www.ebi.ac.uk/swo/", "swo:").strip()
    # place class as child of ObsoleteClass only if it is a class - in this run, they are not classes.
    # outfile.write(modified + " rdfs:subClassOf oboInOwl:ObsoleteClass .\n")
    # place as an instance of ObsoleteClass
    outfile.write(modified + " rdf:type oboInOwl:ObsoleteClass, owl:NamedIndividual .\n")
    # Update the label
    outfile.write(modified + " rdfs:label \"obsolete " + parts[1].strip() + "\"@en .\n" )
    # add deprecated boolean
    outfile.write(modified + " owl:deprecated true .\n")
    # suggest replacement
    outfile.write(modified + " obo:IAO_0100001 " + updatedIRI + " .\n")
    # term tracker item
    outfile.write(modified + " obo:IAO_0000233 'https://github.com/allysonlister/swo/issues/59' .\n")
    # add human-readable reason for obsolescence
    outfile.write(modified + " rdfs:comment \"AL 2023-03-05: Improperly created IRI (with 'efo' in the IRI) replaced by the correct form for SWO IRIs.\"@en .\n")
    outfile.write("\n")
    counter += 1
  else:
    print("no match to efo-swo IRI found in swo:" + line)

outfile.write("}")
outfile.write("WHERE { }")

print("Number of IRIs processed: " + str(counter))

infile.close()
outfile.close()
