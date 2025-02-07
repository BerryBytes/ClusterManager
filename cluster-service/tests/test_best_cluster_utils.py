import unittest
from utils.best_cluster_utils import get_best_cluster

class TestDataSelection(unittest.TestCase):

    def test_get_best_cluster_single_entry(self):
        data = {
            'test1.yaml': {
                'CPU': 50,
                'MEMORY': 70
            }
        }

        expected_result = {
            'test1.yaml': {
                'best_cpu': 50,
                'best_memory': 70
            }
        }
        result = get_best_cluster(data)
        self.assertEqual(result, expected_result)

    def test_get_best_cluster_multiple_entries(self):
        data = {
            'test1.yaml': {
                'CPU': 80,
                'MEMORY': 90
            },
            'test2.yaml': {
                'CPU': 70,
                'MEMORY': 60
            },
            'test3.yaml': {
                'CPU': 50,
                'MEMORY': 70
            }
        }
        expected_result = {
            'test3.yaml': {
                'best_cpu': 50,
                'best_memory': 70
            }
        }
        result = get_best_cluster(data)
        self.assertEqual(result, expected_result)

    def test_get_best_cluster_no_data_below_threshold(self):
        data = {
            'test1.yaml': {
                'CPU': 90,
                'MEMORY': 85
            },
            'test2.yaml': {
                'CPU': 95,
                'MEMORY': 75
            }
        }
        expected_result = {}
        result = get_best_cluster(data)
        self.assertEqual(result, expected_result)

    def test_get_best_cluster_with_notification(self):
        data = {
            'test1.yaml': {
                'CPU': 80,
                'MEMORY': 70
            },
            'test2.yaml': {
                'CPU': 90,
                'MEMORY': 60
            },
            'test3.yaml': {
                'CPU': 50,
                'MEMORY': 70
            }
        }
        expected_result = {
            'test3.yaml': {
                'best_cpu': 50,
                'best_memory': 70
            }
        }
        result = get_best_cluster(data)
        self.assertEqual(result, expected_result)

    def test_get_best_cluster_with_notification1(self):
        data = {
            'test1.yaml': {
                'CPU': 80,
                'MEMORY': 10
            },
            'test2.yaml': {
                'CPU': 10,
                'MEMORY': 90
            },
        }
        expected_result = {
            
        }
        result = get_best_cluster(data)
        print("ACTUAL RESULT :: ",result)
        self.assertEqual(result, expected_result)    



        # Check if the notification was sent
        # Implement your own assertions or mocks for the notification functionality

if __name__ == '__main__':
    unittest.main()
