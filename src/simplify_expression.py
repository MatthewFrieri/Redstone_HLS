class SimplifyExpression:

    @classmethod
    def simplify(cls, minterms: list[str]) -> list[str]:
        """Return the simplest sum of prime implicants that is equivalent to the expression given by minterms.
        This process is described here https://en.wikipedia.org/wiki/Quine%E2%80%93McCluskey_algorithm."""
        # TODO minterms include dont cares?
        prime_implicants = cls._get_prime_implicants(minterms)
        chart = cls._build_prime_implicant_chart(prime_implicants, minterms)
        minimal_prime_implicants = cls._read_prime_implicant_chart(chart)
        return minimal_prime_implicants

    @classmethod
    def _get_prime_implicants(cls, minterms: list[str]) -> list[str]:
        """Return a list of the prime implicants from minterms. A prime implicant is a product term
        that can not be simplified any further by combining with other groups."""
        prime_implicants = []
        merged = [False] * len(minterms)

        for i in range(len(minterms)):
            for j in range(i + 1, len(minterms)):
                m1, m2 = minterms[i], minterms[j]

                # Check that two minterms can be merged
                if cls._check_dashes_align(m1, m2) and cls._check_minterm_distance(m1, m2):

                    merged_minterm = cls._merge_minterms(m1, m2)
                    if merged_minterm not in prime_implicants:
                        prime_implicants.append(merged_minterm)
                    merged[i] = True
                    merged[j] = True

        # All minterms that have not been merged are prime implicants
        for i in range(len(minterms)):
            if not merged[i] and minterms[i] not in prime_implicants:
                prime_implicants.append(minterms[i])

        # If no merges have taken place then all of the prime implicants have been found
        if sum(merged) == 0:
            return prime_implicants

        return cls._get_prime_implicants(prime_implicants)

    @staticmethod
    def _merge_minterms(m1: str, m2: str) -> str:
        """Return a minterm replacing differing bits from m1 and m2 with a dash."""
        merged = ""
        for i in range(len(m1)):
            if m1[i] == m2[i]:
                merged += m1[i]
            else:
                merged += "-"
        return merged

    @staticmethod
    def _check_dashes_align(m1: str, m2: str) -> bool:
        """Return True if the minterms have dashes at the same indices."""
        for i in range(len(m1)):
            bits = m1[i] + m2[i]
            if "-" in bits and bits != "--":
                return False
        return True

    @staticmethod
    def _check_minterm_distance(m1: str, m2: str) -> bool:
        """Return True if the minterms differ by exactly 1 bit. Assumes dashes allign so they can be ignored."""
        m1 = int(m1.replace("-", "0"), 2)
        m2 = int(m2.replace("-", "0"), 2)
        res = m1 ^ m2
        return res != 0 and (res & (res - 1)) == 0

    @classmethod
    def _build_prime_implicant_chart(cls, prime_implicants: list[str], minterms: list[str]) -> dict[str, str]:
        """Return a dictionary that maps prime implicants to a string of bits,
        where each bit at index i is 1 iff the prime implicant contains the minterm at index i."""

        chart = {prime_implicant: "" for prime_implicant in prime_implicants}
        for prime_implicant in chart:
            for minterm in minterms:
                if cls._prime_implicant_contains_minterm(prime_implicant, minterm):
                    chart[prime_implicant] += "1"
                else:
                    chart[prime_implicant] += "0"
        return chart

    @staticmethod
    def _prime_implicant_contains_minterm(prime_implicant: str, minterm: str) -> bool:
        """Return True if the prime implicant contains the minterm. Ex 1-0- contains 1001."""
        for i in range(len(prime_implicant)):
            if prime_implicant[i] != minterm[i] and prime_implicant[i] != "-":
                return False
        return True

    @classmethod
    def _read_prime_implicant_chart(cls, chart: dict[str, str]) -> list[str]:
        """Return the minimal needed prime implicants from the prime implicants chart."""

        n_minterms = len(list(chart.values())[0])
        minterm_coverages = [[] for _ in range(n_minterms)]

        for i in range(n_minterms):
            for prime_implicant, minterms in chart.items():
                if minterms[i] == "1":
                    minterm_coverages[i].append(prime_implicant)

        # Essential prime implicants can not be covered by other prime implicants
        essential_prime_implicants = []
        minterm_indices_to_drop = set()

        # Find which which rows and columns to remove
        for i, coverage in enumerate(minterm_coverages):
            if len(coverage) == 1:
                prime_implicant = coverage[0]
                essential_prime_implicants.append(prime_implicant)
                for i, minterm in enumerate(chart[prime_implicant]):
                    if minterm == "1":
                        minterm_indices_to_drop.add(i)

        # Remove rows with selected prime implicants, and minterms that they cover
        for prime_implicant in essential_prime_implicants:
            del chart[prime_implicant]
        for prime_implicant, minterms in chart.items():
            chart[prime_implicant] = cls.remove_minterms(minterms, minterm_indices_to_drop)

        # TODO now do Petricks Method
        # https://en.wikipedia.org/wiki/Petrick%27s_method
        return essential_prime_implicants

    @staticmethod
    def remove_minterms(minterm_mapping: str, minterm_indices_to_drop: set[int]) -> str:
        """Return minterm_mapping without the indices to drop."""
        res = ""
        for i in range(len(minterm_mapping)):
            if i not in minterm_indices_to_drop:
                res += minterm_mapping[i]
        return res
