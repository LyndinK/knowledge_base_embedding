from rdflib import Literal, RDF, URIRef, RDFS
import rdflib
import os
from pathlib import Path
from .config import Config
from .log import Log
from typing import List


log = Log.get_logger()


class KBReificationInterface:
    """
    An interface to add metainformation to the given graph about
    external entities such as embeddings or images
    """

    @classmethod
    def enrich(cls,
               graph: rdflib.Graph,
               emb_path: str,
               has_id_name: URIRef,
               entity_type: URIRef,
               img_path: str = "") -> rdflib.Graph:
        """
        :param graph: a graph to reify
        :param emb_path: a path to embeddings folder
        :param has_id_name: a predicate which leads to reified entity is
        :param entity_type: a typed of entities to reify
        :param img_path: a path to images folder
        :return: a reified graph
        """

        # list of entity ids
        entity_ids = []
        # list of entities
        entities = []

        # select entity ids and entities
        for s, p, o in graph.triples((None, RDF.type, entity_type)):
            entity = s
            for s_, p_, o_ in graph.triples((entity, has_id_name, None)):
                entity_ids.append(o_.value)
                entities.append(entity)

        log.info("Reifying graph with embeddings")
        graph = cls._reify_with_external_entity(graph=graph,
                                                path=emb_path,
                                                entity_list=entities,
                                                entity_id_list=entity_ids,
                                                predicate=Config.HAS_EMBEDDING)

        # if images provided then enrich with images
        if img_path:
            log.info("Reifying graph with images")
            graph = cls._reify_with_external_entity(graph=graph,
                                                    path=img_path,
                                                    entity_list=entities,
                                                    entity_id_list=entity_ids,
                                                    predicate=Config.HAS_IMAGE)

        # add metadata about images and embeddings
        graph = cls._reify_with_metadata(graph)

        return graph

    @staticmethod
    def _reify_with_external_entity(graph: rdflib.Graph,
                                    path: str,
                                    entity_list: List[rdflib.URIRef],
                                    entity_id_list: List[int],
                                    predicate: rdflib.URIRef) -> rdflib.Graph:
        """
        A method to reify a graph entities with links to external objects
        :param graph: a graph to reify
        :param path: a path with external entities where names of files correspond with
            the names of entities to reify and both are integers
        :param entity_list: a list of entities to check whether they are eligible for reification
        :param entity_id_list: a list of entities ids. Each id corresponds to one in entity_list
        :param predicate: a URIRef - a predicate to use when creating a link between a reified entity
            and an external entity
        :return: reified graph
        """
        # list all external entities with correct names
        external_entities_ids = {int(Path(x).stem) for x in os.listdir(path) if Path(x).stem.isnumeric()}
        external_entities_names_dct = {int(Path(x).stem): x for x in os.listdir(path) if Path(x).stem.isnumeric()}

        for _id, entity in zip(entity_id_list, entity_list):
            if _id in external_entities_ids:
                graph.add((entity, predicate, Literal(external_entities_names_dct[_id])))

        return graph

    @staticmethod
    def _reify_with_metadata(graph: rdflib.Graph) -> rdflib.Graph:

        # add metadata about embeddings
        graph.add((Config.EMBEDDING, RDF.type, RDFS.Class))
        graph.add((Config.EMBEDDING, Config.LOCATED_AT, Config.EMBEDDING_LOCATION))

        # add metadata about images
        graph.add((Config.IMAGE, RDF.type, RDFS.Class))
        graph.add((Config.IMAGE, Config.LOCATED_AT, Config.IMAGE_LOCATION_GRAPH))

        return graph
