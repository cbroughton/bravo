from ampoule import AMPChild
import ampoule.pool

from twisted.protocols.amp import Command, Integer, String

from bravo.chunk import Chunk
from bravo.ibravo import ITerrainGenerator
from bravo.plugin import retrieve_plugins

class MakeChunk(Command):
    arguments = [
        ("x", Integer()),
        ("z", Integer()),
        ("seed", Integer()),
        ("generators", String()),
    ]
    response = [
        ("blocks", String()),
        ("metadata", String()),
        ("skylight", String()),
        ("blocklight", String()),
        ("heightmap", String()),
    ]
    errors = {
        Exception: "Exception",
    }

class Slave(AMPChild):
    """
    Process-based peon for processing and populating.
    """

    def make_chunk(self, x, z, seed, generators):
        """
        Create a chunk using the given parameters.
        """

        plugins = retrieve_plugins(ITerrainGenerator)
        stages = [plugins[g] for g in generators.split(",")]

        chunk = Chunk(x, z)

        for stage in stages:
            stage.populate(chunk, seed)

        return {
            "blocks": "".join(chr(i) for i in chunk.blocks.ravel()),
            "metadata": "".join(chr(i) for i in chunk.metadata.ravel()),
            "skylight": "".join(chr(i) for i in chunk.skylight.ravel()),
            "blocklight": "".join(chr(i) for i in chunk.blocklight.ravel()),
            "heightmap": "".join(chr(i) for i in chunk.heightmap.ravel()),
        }

    MakeChunk.responder(make_chunk)

ampoule.pool.pp = ampoule.pool.ProcessPool(
    ampChild=Slave,
)
