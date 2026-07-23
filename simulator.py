import copy
import pandas as pd

from cache import Cache
class CacheSimulator:
    """
    Controls the complete cache simulation.

    Responsibilities
    ----------------
    - Create cache
    - Execute memory trace
    - Store simulation history
    - Calculate EMAT
    - Generate summary statistics
    """

    def __init__(
        self,
        cache_size: int,
        block_size: int = 4,
        replacement_policy: str = "LRU",
        write_policy: str = "Write Through",
        hit_time: int = 1,
        memory_access_time: int = 100,
    ):

        self.cache = Cache(
            size=cache_size,
            block_size=block_size,
            replacement_policy=replacement_policy,
            write_policy=write_policy,
        )

        self.hit_time = hit_time

        self.memory_access_time = memory_access_time

        # Stores every simulation step
        self.history = []

    # --------------------------------------------------
    # Simulation
    # --------------------------------------------------

    def run(self, trace):
        """
        Executes an entire memory access trace.
        """

        self.history.clear()

        self.cache.reset()

        for step_number, (address, operation) in enumerate(
            trace,
            start=1,
        ):

            result = self.cache.access(
                address,
                operation,
            )

            result["Step"] = step_number

            # Save cache snapshot after this access
            result["Cache Snapshot"] = copy.deepcopy(
                self.cache.get_cache_state()
            )

            self.history.append(result)

    # --------------------------------------------------
    # EMAT
    # --------------------------------------------------

    def calculate_emat(self):
        """
        Effective Memory Access Time

        EMAT =
        Hit Time +
        Miss Rate × Memory Access Time
        """

        miss_rate = self.cache.stats.miss_rate

        return round(
            self.hit_time +
            miss_rate * self.memory_access_time,
            2,
        )

    # --------------------------------------------------
    # Summary
    # --------------------------------------------------

    def summary(self):
        """
        Returns complete simulation summary.
        """

        stats = self.cache.statistics()

        config = self.cache.configuration()

        return {

            "Cache Size":
                config["Cache Size"],

            "Block Size":
                config["Block Size"],

            "Replacement Policy":
                config["Replacement Policy"],

            "Write Policy":
                config["Write Policy"],

            "Hits":
                stats["Hits"],

            "Misses":
                stats["Misses"],

            "Total Accesses":
                stats["Total Accesses"],

            "Hit Rate":
                stats["Hit Rate"],

            "Miss Rate":
                stats["Miss Rate"],

            "Memory Writes":
                stats["Memory Writes"],

            "Cache Usage":
                config["Cache Usage"],

            "Occupancy (%)":
                config["Occupancy (%)"],

            "Hit Time":
                self.hit_time,

            "Memory Access Time":
                self.memory_access_time,

            "EMAT":
                self.calculate_emat(),
        }

    # --------------------------------------------------
    # Cache Information
    # --------------------------------------------------

    def cache_state(self):
        """
        Returns current cache contents.
        """

        return self.cache.get_cache_state()

    # --------------------------------------------------
    # DataFrames
    # --------------------------------------------------

    def history_dataframe(self):
        """
        Returns the complete simulation history as a DataFrame.

        Excludes the "Cache Snapshot" field: it's a nested list of
        dicts per row (used only in the step-by-step expanders),
        and mixing int/str "Stored Block" values inside it breaks
        Arrow serialization when Streamlit renders the table.
        """

        records = [
            {
                key: value
                for key, value in record.items()
                if key != "Cache Snapshot"
            }
            for record in self.history
        ]

        return pd.DataFrame(records)

    def cache_dataframe(self):
        """
        Returns current cache state as a DataFrame.
        """

        return pd.DataFrame(
            self.cache.get_cache_state()
        )

    def configuration_dataframe(self):
        """
        Returns cache configuration as a DataFrame.
        """

        config = self.cache.configuration()

        return pd.DataFrame(
            {
                "Parameter": config.keys(),
                "Value": [str(v) for v in config.values()],
            }
        )

    def summary_dataframe(self):
        """
        Returns simulation summary as a DataFrame.
        """

        summary = self.summary()

        return pd.DataFrame(
            {
                "Metric": summary.keys(),
                "Value": [str(v) for v in summary.values()],
            }
        )

    # --------------------------------------------------
    # Report Export
    # --------------------------------------------------

    def export_history_csv(self):
        """
        Returns simulation history as CSV.
        Used by Streamlit download button.
        """

        return self.history_dataframe().to_csv(
            index=False
        )

    def export_summary_csv(self):
        """
        Returns summary as CSV.
        """

        return self.summary_dataframe().to_csv(
            index=False
        )

    # --------------------------------------------------
    # Accessors
    # --------------------------------------------------

    def get_history(self):
        """
        Returns simulation history.
        """

        return self.history

    def get_summary(self):
        """
        Returns summary dictionary.
        """

        return self.summary()

    def get_configuration(self):
        """
        Returns configuration dictionary.
        """

        return self.cache.configuration()

    # --------------------------------------------------
    # Reset
    # --------------------------------------------------

    def reset(self):
        """
        Clears simulator state.
        """

        self.history.clear()

        self.cache.reset()

    # --------------------------------------------------
    # String Representation
    # --------------------------------------------------

    def __str__(self):
        """
        Pretty print simulation summary.
        Useful for debugging.
        """

        summary = self.summary()

        output = []

        output.append("=" * 60)
        output.append("Simulation Summary")
        output.append("=" * 60)

        for key, value in summary.items():

            output.append(
                f"{key:<25}: {value}"
            )

        return "\n".join(output)
