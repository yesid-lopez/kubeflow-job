from kfp.components import OutputPath

def download_data(path_taxonomy: OutputPath("txt")):
    import urllib.request

    print("Starting download")
    GOOGLE_TAXONOMY_URL = "https://www.google.com/basepages/producttype/taxonomy.en-US.txt"
    taxonomy_paths = []
    for line in urllib.request.urlopen(GOOGLE_TAXONOMY_URL):
        taxonomy_paths.append(line.decode('utf-8').strip())

    taxonomy_paths = taxonomy_paths[1:]
    print(path_taxonomy)
    with open(path_taxonomy, 'w') as writer:
        writer.write("\n".join(taxonomy_paths))

    print("Data has been downloaded")
