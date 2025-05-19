import unittest
from src.api.scryfall import fetch_card_details

class TestScryfallAPI(unittest.TestCase):

    def test_fetch_card_details_valid(self):
        card_name = "Black Lotus"
        result = fetch_card_details(card_name)
        self.assertIsInstance(result, dict)
        self.assertIn('name', result)
        self.assertEqual(result['name'], card_name)

    def test_fetch_card_details_invalid(self):
        card_name = "Nonexistent Card"
        result = fetch_card_details(card_name)
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()