from dataclasses import dataclass
from rdflib import Graph, Literal, RDF, URIRef, Namespace


@dataclass(frozen=True)
class Config:

    # [system]
    # logging level. Possible values: DEBUG, INFO, WARNING, ERROR, CRITICAL
    LOG_LEVEL = 'INFO'
    # images location
    IMAGES_FOLDER = 'images'

    # [search index]
    # Number of trees to use in Annoy index
    # The bigger thins number - the greater index precision
    N_TREES = 10
    # Similarity metric to use. Possible values: "angular", "euclidean", "manhattan", "hamming", or "dot"'
    INDEX_METRIC = 'angular'

    # [graph metadata]
    # default namespace for kb metadata
    NAMESPACE = Namespace("http://knowledge.base/")
    # default predicate for pointing at embedding
    HAS_EMBEDDING = NAMESPACE.has_embedding
    # default predicate for pointing at image
    HAS_IMAGE = NAMESPACE.has_image
    # embedding class
    EMBEDDING = NAMESPACE.embedding
    # image class
    IMAGE = NAMESPACE.image
    # predicate to specify location
    LOCATED_AT = NAMESPACE.located_at
    # embedding location
    EMBEDDING_LOCATION = Literal('AnnoyIndex')
    # images location (the one specified in graph)
    IMAGE_LOCATION_GRAPH = Literal(IMAGES_FOLDER)
    # embedding length predicate
    HAS_LENGTH = NAMESPACE.has_length

    # [output]
    # fontsize to show labels on images
    FONTSIZE = 14
