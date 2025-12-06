"""

"""


class ListSplitter:
    """A utility class for splitting lists into chunks."""

    def __init__(self, chunk_size: int = 10) -> None:
        self.chunk_size = chunk_size

    def split(self, lst):
        """Split list into chunks of specified size."""
        return [lst[i:i + self.chunk_size] for i in range(0, len(lst), self.chunk_size)]

    def split_generator(self, lst):
        """Generator that yields chunks of the list (memory efficient)."""
        for i in range(0, len(lst), chunk_size):
            yield lst[i:i + chunk_size]

    def split_with_remainder(self, lst):
        """Split list and return remainder separately."""
        chunks = self.split(lst)
        if chunks and len(chunks[-1]) < self.chunk_size:
            remainder = chunks.pop()
            return chunks, remainder
        return chunks, []

    def split_with_padding(self, lst, padding_value=None):
        """Split list and pad last chunk if needed."""
        chunks = self.split(lst)
        if chunks and len(chunks[-1]) < self.chunk_size:
            chunks[-1].extend([padding_value] * (self.chunk_size - len(chunks[-1])))
        return chunks

    def get_chunk_info(self, lst):
        """Get information about the chunks that would be created."""
        total_chunks = (len(lst) + self.chunk_size - 1) // self.chunk_size
        full_chunks = len(lst) // self.chunk_size
        partial_chunk_size = len(lst) % self.chunk_size
        return {
            'total_chunks': total_chunks,
            'full_chunks': full_chunks,
            'partial_chunk_size': partial_chunk_size,
            'total_items': len(lst)
        }

# CODE DUMP

