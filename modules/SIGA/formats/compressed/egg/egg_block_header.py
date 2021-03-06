# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

from pkg_resources import parse_version
from modules.SIGA.kaitaistruct import __version__ as ks_version, KaitaiStruct, KaitaiStream, BytesIO


if parse_version(ks_version) < parse_version('0.7'):
    raise Exception("Incompatible Kaitai Struct Python API: 0.7 or later is required, but you have %s" % (ks_version))

class fm_EggBlockHeader(KaitaiStruct):
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.signature = self._io.read_u4le()
        self.compress_method = self._io.read_u2le()
        self.uncompress_size = self._io.read_u4le()
        self.compress_size = self._io.read_u4le()
        self.crc32 = self._io.read_u4le()
        self.end_of_block_header = self._io.read_u4le()
        self.compressed_data = self._io.read_bytes(self.compress_size)


