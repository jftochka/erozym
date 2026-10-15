"""Application compatibility checks using the in-process Flask client."""

import unittest

from main import app


PAGES = ["/","/contacts","/e-pidtrymka","/vacancy","/ukrainska-mova-i-literatura","/angliyska-mova","/mathematika","/istoriya-ukrainy","/fizika","/himiya","/biologia","/geografia","/404","/tarifs"]
STATIC_CSS = "/static/css/styles.css"


class ApplicationCompatibilityTests(unittest.TestCase):
    def setUp(self):
        self.old_testing = app.config["TESTING"]
        app.config["TESTING"] = True
        self.client = app.test_client()

    def tearDown(self):
        app.config["TESTING"] = self.old_testing

    def test_all_existing_pages_render_and_head(self):
        for path in PAGES:
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.mimetype, "text/html")
                self.assertIn(b"<html", response.data.lower())
                self.assertNotIn("Set-Cookie", response.headers)
                head = self.client.head(path)
                self.assertEqual(head.status_code, 200)
                self.assertEqual(head.data, b"")

    def test_existing_pages_reject_post(self):
        for path in PAGES:
            with self.subTest(path=path):
                response = self.client.post(path, data={"name": "example"})
                self.assertEqual(response.status_code, 405)

    def test_request_bodies_do_not_enter_form_parser(self):
        boundary = "dependency-review"
        body = "".join(
            f'--{boundary}\r\nContent-Disposition: form-data; name="f{i}"\r\n\r\nx\r\n'
            for i in range(1001)
        ) + f"--{boundary}--\r\n"
        for path in PAGES:
            with self.subTest(path=path):
                ordinary = self.client.get(path)
                response = self.client.open(
                    path, method="GET", data=body.encode(),
                    content_type=f"multipart/form-data; boundary={boundary}",
                )
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.data, ordinary.data)

    def test_all_templates_compile(self):
        for name in app.jinja_env.list_templates():
            with self.subTest(template=name):
                app.jinja_env.get_template(name)

    def test_static_css_and_conditional_request(self):
        with self.client.get(STATIC_CSS) as response:
            self.assertEqual(response.status_code, 200)
            self.assertTrue(response.data)
            etag = response.headers["ETag"]
        with self.client.get(STATIC_CSS, headers={"If-None-Match": etag}) as response:
            self.assertEqual(response.status_code, 304)

    def test_missing_page_and_static_traversal_return_404(self):
        for path in ("/missing-dependency-review-page", "/static/../main.py",
                     "/static/%2e%2e/main.py"):
            with self.subTest(path=path):
                self.assertEqual(self.client.get(path).status_code, 404)


if __name__ == "__main__":
    unittest.main()
