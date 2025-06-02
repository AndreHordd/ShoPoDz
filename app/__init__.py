from flask import Flask, jsonify
import click

def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object("app.config.Config")

    # ----- DB helper -----
    from app.utils.db import get_db, close_db
    app.teardown_appcontext(close_db)

    # CLI: flask ping-db
    @app.cli.command("ping-db")
    def ping_db():
        try:
            with get_db().cursor() as cur:
                cur.execute("SELECT 1")
            click.echo("✓  DB connection OK")
        except Exception as err:
            click.echo(f"✗  DB connection FAILED: {err}")

    # HTTP: /db-health
    @app.route("/db-health")
    def db_health():
        try:
            with get_db().cursor() as cur:
                cur.execute("SELECT 1")
            return jsonify(status="success", message="DB OK")
        except Exception as err:
            return jsonify(status="error", message=str(err)), 500

    # ----- Blueprints -----
    from app.views.common import bp as common_bp
    app.register_blueprint(common_bp)

    return app
