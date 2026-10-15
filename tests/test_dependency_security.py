"""Dependency-boundary regressions; these probes are not application endpoints."""

import io
import ntpath
import types
import unittest
from unittest.mock import patch

from flask import Flask, session
from jinja2 import Environment, select_autoescape
from jinja2.exceptions import SecurityError
from jinja2.sandbox import SandboxedEnvironment
from werkzeug import security
from werkzeug.datastructures import MultiDict
from werkzeug.exceptions import RequestEntityTooLarge
from werkzeug.http import parse_cookie
from werkzeug.wrappers import Request


class MemoryOnlyRequest(Request):
    def _get_file_stream(self, *args, **kwargs):
        # Rejected uploads stay in memory, including partially parsed files.
        return io.BytesIO()


class DependencySecurityTests(unittest.TestCase):
    def test_permanent_session_refresh_varies_on_cookie(self):
        probe = Flask(__name__)
        probe.config.update(SECRET_KEY="local-test-key", TESTING=True)

        @probe.route("/")
        def index():
            return "public page"

        client = probe.test_client()
        with client.session_transaction() as state:
            state.permanent = True
            state["account"] = "example"
        response = client.get("/")
        self.assertIn("Set-Cookie", response.headers)
        self.assertIn("Cookie", response.vary)

    def test_reading_only_session_keys_varies_on_cookie(self):
        probe = Flask(__name__)
        probe.config.update(SECRET_KEY="local-test-key", TESTING=True)

        @probe.route("/contains")
        def contains():
            return str("account" in session)

        @probe.route("/length")
        def length():
            return str(len(session))

        client = probe.test_client()
        with client.session_transaction() as state:
            state["account"] = "example"
        for path, expected in (("/contains", "True"), ("/length", "1")):
            with self.subTest(path=path):
                response = client.get(path)
                self.assertEqual(response.get_data(as_text=True), expected)
                self.assertIn("Cookie", response.vary)

    def test_multipart_rejects_excessive_field_and_file_parts(self):
        for files in (False, True):
            with self.subTest(files=files):
                values = MultiDict(
                    (str(i), (io.BytesIO(b"x"), "part.txt") if files else "x")
                    for i in range(1001)
                )
                with MemoryOnlyRequest.from_values(
                    method="POST", data=values, content_type="multipart/form-data"
                ) as request:
                    with self.assertRaises(RequestEntityTooLarge):
                        if files:
                            request.files
                        else:
                            request.form

    def test_normal_multipart_still_parses(self):
        with Request.from_values(
            method="POST",
            data={"name": "example", "upload": (io.BytesIO(b"hello"), "hello.txt")},
            content_type="multipart/form-data",
        ) as request:
            self.assertEqual(request.form["name"], "example")
            self.assertEqual(request.files["upload"].read(), b"hello")

    def test_nameless_cookie_cannot_shadow_host_cookie(self):
        cookies = parse_cookie("=__Host-token=bad; __Host-token=good")
        self.assertEqual(cookies["__Host-token"], "good")

    def test_xmlattr_rejects_attribute_delimiters(self):
        env = Environment(autoescape=select_autoescape(default=True))
        template = env.from_string("<div{{ attrs|xmlattr }}></div>")
        for key in ("x onmouseover", "x/onmouseover", "x>onmouseover", "x=onmouseover"):
            with self.subTest(key=key):
                with self.assertRaises(ValueError):
                    template.render(attrs={key: "value"})
        self.assertEqual(
            template.render(attrs={"title": 'a"b'}),
            '<div title="a&#34;b"></div>',
        )

    def test_sandbox_blocks_attr_and_indirect_format_access(self):
        env = SandboxedEnvironment()
        env.filters["invoke"] = lambda value, callback: callback(value)
        probes = (
            "{{ 0|invoke('{0.__class__.__name__}'|attr('format')) }}",
            "{{ 0|invoke('{0.__class__.__name__}'.format) }}",
        )
        for source in probes:
            with self.subTest(source=source):
                with self.assertRaises(SecurityError):
                    env.from_string(source).render()
        self.assertEqual(env.from_string("{{ '{0}'.format(42) }}").render(), "42")
        self.assertEqual(
            env.from_string("{{ ('{0}'|attr('format'))(42) }}").render(), "42"
        )

    def test_windows_safe_join_rejects_device_variants(self):
        # Exercise the Windows branch without opening device files.
        windows_os = types.SimpleNamespace(name="nt", path=ntpath)
        with patch.object(security, "os", windows_os), patch.object(
            security, "_os_alt_seps", ["\\"]
        ):
            for name in ("NUL", "folder/NUL", "CON.txt", "AUX ", "folder/NUL:"):
                with self.subTest(name=name):
                    self.assertIsNone(security.safe_join("static", name))
            self.assertEqual(
                security.safe_join("static", "css/site.css"), "static/css/site.css"
            )


if __name__ == "__main__":
    unittest.main()
