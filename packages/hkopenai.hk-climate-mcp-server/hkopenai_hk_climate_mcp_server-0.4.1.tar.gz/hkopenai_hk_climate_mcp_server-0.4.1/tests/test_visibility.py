import unittest
from unittest.mock import patch, MagicMock
from hkopenai.hk_climate_mcp_server.tools.visibility import get_visibility_data

class TestVisibilityTools(unittest.TestCase):
    @patch("requests.get")
    def test_get_visibility_data(self, mock_get):
        example_json = {
            "fields": ["Date time", "Automatic Weather Station", "10 minute mean visibility"],
            "data": [
                ["202506231320", "Central", "35 km"],
                ["202506231320", "Chek Lap Kok", "50 km"]
            ]
        }
        mock_response = MagicMock()
        mock_response.json.return_value = example_json
        mock_get.return_value = mock_response

        result = get_visibility_data()
        self.assertEqual(result["fields"], example_json["fields"])
        self.assertEqual(result["data"], example_json["data"])
        mock_get.assert_called_once_with(
            "https://data.weather.gov.hk/weatherAPI/opendata/opendata.php?dataType=LTMV&lang=en&rformat=json"
        )

if __name__ == "__main__":
    unittest.main()
