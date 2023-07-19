import gzip
import bz2
import lzma
import lz4.frame
import zstandard as zstd


class Compressor:
	
	@staticmethod
	def deflate(data, compression_mode):
		"""
		Compresses the given data using the specified compression mode.
	
		Args:
			data: The data to be compressed.
			compression_mode: The compression mode to be used. Possible values are 'gzip', 'bzip2', 'lzma', 'lz4', 'zstd', and 'none'.
	
		Returns:
			The compressed data.
		"""
		if compression_mode == 'gzip':
			return gzip.compress(data)
		elif compression_mode == 'bzip2':
			return bz2.compress(data)
		elif compression_mode == 'lzma':
			return lzma.compress(data)
		elif compression_mode == 'lz4':
			return lz4.frame.compress(data)
		elif compression_mode == 'zstd':
			return zstd.compress(data)
		elif compression_mode == 'none':
			return data
		else:
			raise ValueError("Invalid compression mode. Supported modes are 'gzip', 'bzip2', 'lzma', 'lz4', 'zstd', and 'none'.")
	
	@staticmethod
	def inflate(compressed_data, compression_mode):
		"""
		Decompresses the given compressed data using the specified compression mode.
	
		Args:
			compressed_data: The compressed data to be decompressed.
			compression_mode: The compression mode that was used for compression. Possible values are 'gzip', 'bzip2', 'lzma', 'lz4', 'zstd', and 'none'.
	
		Returns:
			The decompressed data.
		"""
		if compression_mode == 'gzip':
			return gzip.decompress(compressed_data)
		elif compression_mode == 'bzip2':
			return bz2.decompress(compressed_data)
		elif compression_mode == 'lzma':
			return lzma.decompress(compressed_data)
		elif compression_mode == 'lz4':
			return lz4.frame.decompress(compressed_data)
		elif compression_mode == 'zstd':
			return zstd.decompress(compressed_data)
		elif compression_mode == 'none':
			return compressed_data
		else:
			raise ValueError("Invalid compression mode. Supported modes are 'gzip', 'bzip2', 'lzma', 'lz4', 'zstd', and 'none'.")
