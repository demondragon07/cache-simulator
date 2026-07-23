from dataclasses import dataclass
from enum import Enum
from collections import deque


class ReplacementPolicy(Enum):
    """Supported cache replacement policies."""

    LRU = "LRU"
    FIFO = "FIFO"


class WritePolicy(Enum):
    """Supported cache write policies."""

    WRITE_THROUGH = "Write Through"
    WRITE_BACK = "Write Back"


@dataclass
class CacheBlock:
    """
    Represents one cache line.
    """

    tag: int | None = None
    valid: bool = False
    dirty: bool = False


class Statistics:
    """
    Stores cache performance statistics.
    """

    def __init__(self):

        self.hits = 0
        self.misses = 0
        self.memory_writes = 0

    @property
    def total_accesses(self):

        return self.hits + self.misses

    @property
    def hit_rate(self):

        if self.total_accesses == 0:
            return 0.0

        return self.hits / self.total_accesses

    @property
    def miss_rate(self):

        return 1.0 - self.hit_rate


class Cache:
    """
    Cache Simulator

    Supports:
    - LRU Replacement
    - FIFO Replacement
    - Write Through
    - Write Back
    - Dirty Bit
    - Block Size Mapping
    """

    def __init__(
        self,
        size: int,
        block_size: int = 4,
        replacement_policy: str = "LRU",
        write_policy: str = "Write Through",
    ):

        self.size = size

        self.block_size = block_size

        self.blocks = [
            CacheBlock()
            for _ in range(size)
        ]

        self.stats = Statistics()

        self.replacement_policy = ReplacementPolicy(
            replacement_policy
        )

        if write_policy == "Write Through":

            self.write_policy = WritePolicy.WRITE_THROUGH

        else:

            self.write_policy = WritePolicy.WRITE_BACK

        # Used for LRU
        self.lru_order = []

        # Used for FIFO
        self.fifo_queue = deque()

    # --------------------------------------------------
    # Address Mapping
    # --------------------------------------------------

    def get_block_number(self, address: int):
        """
        Converts a memory address into a block number.

        Example:
        Block Size = 4

        Address 0-3   -> Block 0
        Address 4-7   -> Block 1
        Address 8-11  -> Block 2
        """

        return address // self.block_size

    # --------------------------------------------------
    # Helper Methods
    # --------------------------------------------------

    def find_block(self, block_number: int):
        """
        Returns cache line containing the block.
        """

        for index, block in enumerate(self.blocks):

            if block.valid and block.tag == block_number:

                return index

        return None

    def find_empty_line(self):
        """
        Returns first empty cache line.
        """

        for index, block in enumerate(self.blocks):

            if not block.valid:

                return index

        return None

    def update_replacement_policy(self, line: int):
        """
        Updates FIFO/LRU data structures.
        """

        if self.replacement_policy == ReplacementPolicy.FIFO:

            if line not in self.fifo_queue:

                self.fifo_queue.append(line)

            return

        # LRU

        if line in self.lru_order:

            self.lru_order.remove(line)

        self.lru_order.append(line)

    def select_victim(self):
        """
        Returns cache line to evict.
        """

        if self.replacement_policy == ReplacementPolicy.FIFO:

            return self.fifo_queue.popleft()

        return self.lru_order.pop(0)

    def cache_usage(self):
        """
        Returns number of occupied cache lines.
        """

        used = 0

        for block in self.blocks:

            if block.valid:

                used += 1

        return used

    def occupancy(self):
        """
        Returns cache occupancy percentage.
        """

        return round(
            (self.cache_usage() / self.size) * 100,
            2
        )

    # --------------------------------------------------
    # Hit Processing
    # --------------------------------------------------

    def process_hit(
        self,
        line: int,
        operation: str
    ):
        """
        Handles cache hit.
        """

        self.stats.hits += 1

        cache_block = self.blocks[line]

        action = "Cache Hit"

        if operation == "Write":

            if self.write_policy == WritePolicy.WRITE_BACK:

                cache_block.dirty = True

                action = (
                    "Write hit. "
                    "Dirty bit set."
                )

            else:

                self.stats.memory_writes += 1

                action = (
                    "Write hit. "
                    "Memory updated immediately."
                )

        else:

            action = "Read hit."

        self.update_replacement_policy(line)

        return action
        # --------------------------------------------------
    # Miss Processing
    # --------------------------------------------------

    def process_miss(
        self,
        block_number: int,
        operation: str
    ):
        """
        Handles cache miss.
        """

        self.stats.misses += 1

        line = self.find_empty_line()

        action = ""

        # Cache Full -> Select victim
        if line is None:

            line = self.select_victim()

            victim = self.blocks[line]

            # Write dirty block back to memory
            if victim.dirty:

                self.stats.memory_writes += 1

                action += (
                    f"Dirty Block {victim.tag} "
                    f"written back to memory. "
                )

            action += (
                f"Evicted Block {victim.tag} "
                f"from Line {line}. "
            )

        cache_block = self.blocks[line]

        cache_block.tag = block_number
        cache_block.valid = True
        cache_block.dirty = False

        if operation == "Write":

            if self.write_policy == WritePolicy.WRITE_BACK:

                cache_block.dirty = True

                action += (
                    f"Loaded Block {block_number} "
                    f"into Line {line}. "
                    f"Dirty bit set."
                )

            else:

                self.stats.memory_writes += 1

                action += (
                    f"Loaded Block {block_number} "
                    f"into Line {line}. "
                    f"Memory updated immediately."
                )

        else:

            action += (
                f"Loaded Block {block_number} "
                f"into Line {line}."
            )

        self.update_replacement_policy(line)

        return line, action

    # --------------------------------------------------
    # Main Access Function
    # --------------------------------------------------

    def access(
        self,
        address: int,
        operation: str
    ):
        """
        Simulates one memory access.

        Parameters
        ----------
        address : Memory address
        operation : "Read" or "Write"

        Returns
        -------
        Dictionary containing step information.
        """

        block_number = self.get_block_number(address)

        line = self.find_block(block_number)

        # ----------------------------
        # Cache Hit
        # ----------------------------

        if line is not None:

            action = self.process_hit(
                line,
                operation
            )

            return {
                "Address": address,
                "Block": block_number,
                "Operation": operation,
                "Result": "Hit",
                "Cache Line": line,
                "Action": action,
            }

        # ----------------------------
        # Cache Miss
        # ----------------------------

        line, action = self.process_miss(
            block_number,
            operation
        )

        return {
            "Address": address,
            "Block": block_number,
            "Operation": operation,
            "Result": "Miss",
            "Cache Line": line,
            "Action": action,
        }
        # --------------------------------------------------
    # Cache State
    # --------------------------------------------------

    def get_cache_state(self):
        """
        Returns the current state of all cache lines.
        Used by the Streamlit UI to display the cache.
        """

        state = []

        for line, block in enumerate(self.blocks):

            state.append(
                {
                    "Cache Line": line,
                    "Stored Block": (
                        str(block.tag)
                        if block.valid
                        else "-"
                    ),
                    "Valid": block.valid,
                    "Dirty": block.dirty,
                }
            )

        return state

    # --------------------------------------------------
    # Configuration
    # --------------------------------------------------

    def configuration(self):
        """
        Returns the cache configuration.
        """

        return {
            "Cache Size": self.size,
            "Block Size": self.block_size,
            "Replacement Policy": self.replacement_policy.value,
            "Write Policy": self.write_policy.value,
            "Cache Usage": self.cache_usage(),
            "Occupancy (%)": self.occupancy(),
        }

    # --------------------------------------------------
    # Statistics
    # --------------------------------------------------

    def statistics(self):
        """
        Returns cache performance statistics.
        """

        return {
            "Hits": self.stats.hits,
            "Misses": self.stats.misses,
            "Total Accesses": self.stats.total_accesses,
            "Hit Rate": round(self.stats.hit_rate * 100, 2),
            "Miss Rate": round(self.stats.miss_rate * 100, 2),
            "Memory Writes": self.stats.memory_writes,
        }

    # --------------------------------------------------
    # Reset Cache
    # --------------------------------------------------

    def reset(self):
        """
        Clears cache contents and statistics.
        """

        self.blocks = [
            CacheBlock()
            for _ in range(self.size)
        ]

        self.stats = Statistics()

        self.lru_order.clear()

        self.fifo_queue.clear()

    # --------------------------------------------------
    # String Representation
    # --------------------------------------------------

    def __str__(self):
        """
        Pretty print cache contents.
        Useful for debugging.
        """

        output = []

        output.append("=" * 55)
        output.append("Cache State")
        output.append("=" * 55)

        for line, block in enumerate(self.blocks):

            output.append(
                f"Line {line:<2} | "
                f"Block: {str(block.tag):<5} | "
                f"Valid: {block.valid} | "
                f"Dirty: {block.dirty}"
            )

        return "\n".join(output)
    