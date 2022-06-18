from annoy import AnnoyIndex
import numpy as np
import os
from rdflib import Graph, URIRef, Literal
import pickle
from .log import Log
from .config import Config
import shutil
from zipfile import ZipFile
from .kb_reification_interface import KBReificationInterface
from pathlib import Path
from io import BytesIO
from random import randint


log = Log.get_logger()


class KBIO(KBReificationInterface):
    """
    A class to perform all IO related operations for knowledge base
    """
    def __init__(self):
        self._graph = None
        self._index = None
        self._tmp_dir = None
        self._archive = None
        self._meta_dict = dict()

    def read_raw(self,
                 data_ttl_path: str,
                 embeddings_dir_path: str,
                 out_bk_path_dir: str,
                 entity_to_enrich: URIRef,
                 entity_predicate: URIRef,
                 images_dir_path: str = ""):
        """
        A method to read raw directories and make a knowledge bae of it
        :param out_bk_path_dir: out path to save the knowledge base
        :param data_ttl_path: a path to .ttl RDF file
        :param embeddings_dir_path: a path to embeddings directory. Each embedding should be
            a .npy numpy file containing a single array. A name of .npy file should match its
            source entity
        :param entity_to_enrich: an rdflib.URIRef pointing to entity class we would enrich with info
            about embeddings
        :param entity_predicate: an rdflib.URIRef pointing to entity id predicate we would enrich with info
            about embeddings
        :param images_dir_path:  optional, a path to images directory. A name of image file should match
            its source entity
        :return:
        """
        # read turtle file and make a graph
        self._read_ttl_file(data_ttl_path=data_ttl_path)

        # remember entity class and it's predicate to metadata dictionary
        self._meta_dict['ENTITY'] = entity_to_enrich
        self._meta_dict['ENTITY_PREDICATE'] = entity_predicate

        # enrich graph with metadata info about embeddings
        self._graph = self.enrich(graph=self._graph,
                                  emb_path=embeddings_dir_path,
                                  has_id_name=entity_predicate,
                                  entity_type=entity_to_enrich,
                                  img_path=images_dir_path)

        # read embeddings and build search index
        self._build_annoy_index(embeddings_dir_path=embeddings_dir_path)

        # write loaded info to disk
        self._write_ttlplus(out_path=out_bk_path_dir,
                            img_path=images_dir_path)

    def read_ttlplus(self, ttlplus_path: str):
        """
        A method to read existing ttlplus file
        :param ttlplus_path: a path to .ttlplus file
        """
        log.info(f"reading file {ttlplus_path}")
        self._archive = ZipFile(ttlplus_path, 'r')

        # read graph
        self._graph = self._archive.open('graph.p')
        self._graph = pickle.load(self._graph)

        # read metadict
        self._meta_dict = self._archive.open('metadict.p')
        self._meta_dict = pickle.load(self._meta_dict)

        # read index, we will need temp folder for that
        self._tmp_dir = os.path.join(os.path.dirname(ttlplus_path), f'_tmp_kb_{str(randint(100, 999))}')
        if os.path.exists(self._tmp_dir):
            shutil.rmtree(self._tmp_dir)
        os.mkdir(self._tmp_dir)
        log.info(f"creating tmp dir {self._tmp_dir}")
        self._archive.extract('kb_index.ann', path=self._tmp_dir)
        self._index = AnnoyIndex(self._meta_dict['VECTOR_LENGTH'], Config.INDEX_METRIC)
        self._index.load(os.path.join(self._tmp_dir, 'kb_index.ann'))

    def _write_ttlplus(self, out_path: str, img_path: str = ""):
        """
        A method to write kb files to disk
        :param out_path: a path where to write .ttlplus file
        :param img_path: a path where images located
        :return:
        """
        # make temp directory to write annoy file
        self._tmp_dir = os.path.join(out_path, f'_tmp_kb_{str(randint(100, 999))}')
        if os.path.exists(self._tmp_dir):
            shutil.rmtree(self._tmp_dir)
        os.mkdir(self._tmp_dir)
        log.info(f"creating tmp directory: {self._tmp_dir}")

        # save index to folder
        self._index.save(os.path.join(self._tmp_dir, 'kb_index.ann'))
        log.info(f"saving index to tmp directory")

        # serialize graph
        with open(os.path.join(self._tmp_dir, 'graph.p'), 'wb') as f:
            pickle.dump(self._graph, f)
        log.info(f"saving serialized graph to tmp directory")

        # serialize metadata dictionary
        buffer_meta_dict = BytesIO()
        pickle.dump(self._meta_dict, buffer_meta_dict)

        # create archive
        log.info(f"saving knowledge base contents to the archive five")
        with ZipFile(os.path.join(out_path, 'kb.ttlplus'), 'w') as zip_file:
            # add index, metadict and graph to it
            zip_file.write(os.path.join(self._tmp_dir, 'graph.p'), arcname='graph.p')
            zip_file.write(os.path.join(self._tmp_dir, 'kb_index.ann'), arcname='kb_index.ann')
            zip_file.writestr('metadict.p', buffer_meta_dict.getvalue())
            # add images
            if img_path:
                log.info(f"adding provided images to the knowledge base")
                log.info(f"please stand by, this may take a while")
                for image in os.listdir(img_path):
                    zip_file.write(os.path.join(img_path, image),
                                   arcname=os.path.join(Config.IMAGES_FOLDER, image))
        log.info(f"permanent knowledge base archive file successfully created")

        # set archive in case if we need to access images
        self._archive = ZipFile(os.path.join(out_path, 'kb.ttlplus'), 'r')

    def _read_ttl_file(self, data_ttl_path: str):
        """
        A method to read RDF data
        :param data_ttl_path: a path to ttl file
        """
        log.info(f"reading ttl file: {data_ttl_path}")
        self._graph = Graph()
        self._graph.parse(data_ttl_path, format="ttl")
        log.info("done reading ttl file")

    def _build_annoy_index(self,
                           embeddings_dir_path: str):
        """
        A method to read embeddings and build search index
        :param embeddings_dir_path: a path to directory with .npy vectors
        """
        log.info(f"reading embedding directory: {embeddings_dir_path}")
        # read directory
        files = [x for x in os.listdir(embeddings_dir_path) if Path(x).stem.isnumeric()]
        names = [int(Path(x).stem) for x in os.listdir(embeddings_dir_path) if Path(x).stem.isnumeric()]
        # read one vector to determine the required size for index
        sample_vector = np.load(os.path.join(embeddings_dir_path, files[0]))

        # we need to remember this permanently in order to reconstruct index later
        self._meta_dict['VECTOR_LENGTH'] = len(sample_vector)
        # and add this info to the graph
        self._graph.add((Config.EMBEDDING, Config.HAS_LENGTH, Literal(len(sample_vector))))

        self._index = AnnoyIndex(self._meta_dict['VECTOR_LENGTH'], Config.INDEX_METRIC)

        log.info(f"adding vectors to search index")
        for file, name in zip(files, names):
            # filename without extension. Will be a key for searching
            vector = np.load(os.path.join(embeddings_dir_path, file))
            # add vector along with its key
            self._index.add_item(name, vector)

        self._index.build(Config.N_TREES)
        log.info("search index built successfully")

    def __del__(self):
        # do need this step to overcome a glitch
        # will get permission error unless there are no links to index
        # this is probably due to the fact that .ann file is mmapped into memory
        # as a part of Annoy optimisation
        self._index = None
        if self._tmp_dir:
            if os.path.exists(self._tmp_dir):
                log.info(f"performing cleanup, removing {self._tmp_dir}")
                shutil.rmtree(self._tmp_dir)
        if self._archive:
            self._archive.close()
