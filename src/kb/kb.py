from rdflib import Literal
from .log import Log
from .kbio import KBIO
from typing import List
from .config import Config
import matplotlib.pyplot as plt
import matplotlib.image as mpimg


log = Log.get_logger()


class KB(KBIO):
    """
    A class to represent the knowledge base
    """
    def __init__(self):
        KBIO.__init__(self)

    @property
    def graph(self):
        return self._graph

    def select_similar(self, entity_id: int, k_nearest: int = 10) -> List[int]:
        """
        A method to select k nearest to the entity with the given integer id
        :param entity_id: entity id whose closest neighbors we want
        :param k_nearest: a number of neighbors we want
        :return: a list of int ids of closest neighbors
        """
        # check whether entity with a given id exists
        entity = None
        for s, p, o in self._graph.triples((None, self._meta_dict['ENTITY_PREDICATE'], Literal(entity_id))):
            entity = s
        if not entity:
            log.warning(f"entity with id `{entity_id}` does not exist")
            return []

        # check whether it has an embedding
        emb = None
        for s, p, o in self._graph.triples((entity, Config.HAS_EMBEDDING, None)):
            emb = o
        if not emb:
            log.warning(f"entity with id `{entity_id}` does not have corresponding embeddings")
            return []

        # query search index and return results
        return self._index.get_nns_by_item(entity_id, k_nearest)

    def select_similar_image(self, entity_id: int, k_nearest: int = 10):

        similar_ids = self.select_similar(entity_id=entity_id, k_nearest=k_nearest)

        self._show_image(entity_id=entity_id, title=f"showing image with requested id `{entity_id}`")

        for enum, id_ in enumerate(similar_ids):
            self._show_image(entity_id=id_, title=f"showing neighbor photo. Rank: `{enum + 1}`, id: {id_}")

    def _show_image(self, entity_id: int, title: str):
        for s, p, o in self._graph.triples((None, self._meta_dict['ENTITY_PREDICATE'], Literal(entity_id))):
            entity = s

        # check whether it has an embedding
        img = None
        for s, p, o in self._graph.triples((entity, Config.HAS_IMAGE, None)):
            img = o
        if not img:
            log.warning(f"entity with id `{entity_id}` does not have corresponding images")
        else:
            # read image from archive
            name = f"{Config.IMAGES_FOLDER}/{img}"
            image = self._archive.open(name)
            img_array = mpimg.imread(image)

            # plot it with matplotlib
            plt.figure()
            plt.suptitle(title, fontsize=Config.FONTSIZE, fontweight='bold')
            plt.imshow(img_array)
