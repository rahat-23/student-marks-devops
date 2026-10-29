import json
import threading
import unittest
from http.server import ThreadingHTTPServer
from urllib.error import HTTPError
from urllib.request import urlopen

from app import AppHandler, classify_marks, grade_result


class BusinessLogicTests(unittest.TestCase):
    def test_pass_boundary(self):
        self.assertEqual(classify_marks(50), "Pass")

    def test_fail_boundary(self):
        self.assertEqual(classify_marks(49), "Fail")

    def test_reject_out_of_range(self):
        code, body = grade_result("120")
        self.assertEqual(code, 400)
        self.assertIn("error", body)


class HTTPTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), AppHandler)
        cls.port = cls.server.server_address[1]
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=3)

    def get(self, route):
        try:
            with urlopen(f"http://127.0.0.1:{self.port}{route}", timeout=3) as response:
                return response.status, json.load(response)
        except HTTPError as error:
            return error.code, json.loads(error.read().decode("utf-8"))

    def test_health(self):
        code, body = self.get("/health")
        self.assertEqual((code, body), (200, {"status": "ok"}))

    def test_grade_api(self):
        code, body = self.get("/grade?marks=85")
        self.assertEqual((code, body), (200, {"marks": 85, "result": "Pass"}))

    def test_bad_input(self):
        code, body = self.get("/grade?marks=wrong")
        self.assertEqual(code, 400)
        self.assertIn("error", body)


if __name__ == "__main__":
    unittest.main()
