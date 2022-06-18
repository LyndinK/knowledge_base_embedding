from src.kb import KB
from rdflib import Graph, Literal, RDF, URIRef, Namespace


def test_create_ttl_from_raw():
    ttl = r"C:\Users\kiril\Documents\python_scripts\rdf\raw_input_data\data.ttl"
    embeddings = r"C:\Users\kiril\Documents\python_scripts\rdf\raw_input_data\embeddings"
    images = r"C:\Users\kiril\Documents\python_scripts\rdf\raw_input_data\images"
    out_dir = r"C:\Users\kiril\Documents\python_scripts\rdf\transformed_input_data"

    kb_reader = KBIO()
    kb_reader.read_raw(data_ttl_path=ttl,
                       embeddings_dir_path=embeddings,
                       out_bk_path_dir=out_dir,
                       images_dir_path=images)


def test_read_existing_ttl():
    ttplus = r"C:\Users\kiril\Documents\python_scripts\rdf\transformed_input_data\kb.ttlplus"
    kb_reader = KBIO()
    kb_reader.read_ttlplus(ttplus)


def test_inheritance():
    ttplus = r"C:\Users\kiril\Documents\python_scripts\rdf\transformed_input_data\kb.ttlplus"
    kb = KB()
    kb.read_ttlplus(ttplus)


def test_select_similar():
    ttplus = r"C:\Users\kiril\Documents\python_scripts\rdf\transformed_input_data\kb.ttlplus"
    kb = KB()
    kb.read_ttlplus(ttplus)
    print(kb.select_similar(256689))


def test_enricher():
    ttl_no_embeddings = r"C:\Users\kiril\Documents\python_scripts\rdf\out\data_out_no_embeddings.ttl"
    embeddings = r"C:\Users\kiril\Documents\python_scripts\rdf\raw_input_data\embeddings"
    images = r"C:\Users\kiril\Documents\python_scripts\rdf\raw_input_data\images"
    out_dir = r"C:\Users\kiril\Documents\python_scripts\rdf\transformed_input_data"
    n_e = Namespace("http://example.org/word/")
    item = n_e.item
    has_article = n_e.has_article

    kb_reader = KB()
    kb_reader.read_raw(data_ttl_path=ttl_no_embeddings,
                       embeddings_dir_path=embeddings,
                       out_bk_path_dir=out_dir,
                       images_dir_path=images,
                       entity_to_enrich=item,
                       entity_predicate=has_article)

    print(kb_reader.select_similar(256689))


def test_enricher_ready():
    ttplus = r"C:\Users\kiril\Documents\python_scripts\rdf\transformed_input_data\kb.ttlplus"
    kb = KB()
    kb.read_ttlplus(ttplus)
    print(kb.select_similar(256689))


def test_print_image():
    ttplus = r"C:\Users\kiril\Documents\python_scripts\rdf\transformed_input_data\kb.ttlplus"
    kb = KB()
    kb.read_ttlplus(ttplus)
    print(kb.select_similar_image(256689))


test_enricher()
