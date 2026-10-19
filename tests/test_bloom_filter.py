import unittest

from bloom_filter import BloomFilter, normalize_email


class BloomFilterTests(unittest.TestCase):
    def test_empty_filter_excludes_any_query(self):
        bloom = BloomFilter(256, 4)
        self.assertFalse(bloom.check("x@example.com")["possibly_present"])

    def test_inserted_items_have_no_false_negatives(self):
        bloom = BloomFilter(10_000, 7)
        values = [f"person-{i}@example.com" for i in range(250)]
        for value in values:
            bloom.add(value)
        self.assertTrue(all(bloom.check(value)["possibly_present"] for value in values))

    def test_repeated_insertion_does_not_clear_bits(self):
        bloom = BloomFilter(256, 5)
        first = bloom.add("demo@example.com")
        set_bits = bloom.set_bits
        second = bloom.add("demo@example.com")
        self.assertGreaterEqual(len(first["changed_positions"]), 1)
        self.assertEqual(second["changed_positions"], [])
        self.assertEqual(bloom.set_bits, set_bits)

    def test_positions_are_deterministic_after_normalization(self):
        bloom = BloomFilter(997, 7)
        self.assertEqual(bloom.positions("  USER@EXAMPLE.COM "), bloom.positions("user@example.com"))

    def test_positions_stay_in_bounds(self):
        bloom = BloomFilter(37, 7)
        self.assertTrue(all(0 <= position < 37 for position in bloom.positions("x@example.com")))

    def test_overlapping_positions_are_handled(self):
        bloom = BloomFilter(1, 7)
        trace = bloom.add("x@example.com")
        self.assertEqual(trace["positions"], [0] * 7)
        self.assertEqual(trace["changed_positions"], [0])
        self.assertEqual(bloom.set_bits, 1)

    def test_bit_array_length_matches_capacity(self):
        bloom = BloomFilter(11, 3)
        self.assertEqual(len(bloom.bit_array()), 11)
        with self.assertRaises(IndexError):
            bloom._get_bit(11)

    def test_invalid_parameters_rejected(self):
        with self.assertRaises(ValueError):
            BloomFilter(0, 7)
        with self.assertRaises(ValueError):
            BloomFilter(10, 0)

    def test_normalization(self):
        self.assertEqual(normalize_email("  USER@Example.COM "), "user@example.com")

    def test_false_positive_is_possible_and_detected_if_found(self):
        bloom = BloomFilter(64, 5)
        inserted = {f"member-{i}@example.com" for i in range(12)}
        for email in inserted:
            bloom.add(email)
        found = next((f"nonmember-{i}@example.org" for i in range(1000) if bloom.check(f"nonmember-{i}@example.org")["possibly_present"]), None)
        if found is not None:
            self.assertNotIn(found, inserted)
            self.assertTrue(all(bloom.check(found)["bit_values"]))
        # A false positive is probabilistic, so the test remains valid if none appears in the bounded search.


if __name__ == "__main__":
    unittest.main()
