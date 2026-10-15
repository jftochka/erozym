"""Keep the declared, currently unused database packages compatible."""

import unittest

from flask import Flask
from flask_sqlalchemy import SQLAlchemy


class OptionalDatabaseCompatibilityTests(unittest.TestCase):
    def test_in_memory_model_round_trip(self):
        probe = Flask(__name__)
        probe.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        database = SQLAlchemy(probe)

        class Record(database.Model):
            id = database.Column(database.Integer, primary_key=True)
            name = database.Column(database.String(32), nullable=False)

        with probe.app_context():
            try:
                database.create_all()
                database.session.add(Record(name="example"))
                database.session.commit()
                stored = database.session.execute(database.select(Record)).scalar_one()
                self.assertEqual(stored.name, "example")
            finally:
                database.session.remove()
                database.drop_all()
                database.engine.dispose()


if __name__ == "__main__":
    unittest.main()
