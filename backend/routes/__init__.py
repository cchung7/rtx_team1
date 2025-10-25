from flask import Blueprint

def register_blueprints(app):
    # Import here to avoid circular imports
    from .index import bp as index_bp
    from .health import bp as health_bp
    from .counties import bp as counties_bp
    from .historical import bp as historical_bp
    from .predict import bp as predict_bp
    from .refresh import bp as refresh_bp
    from .model_metrics import bp as metrics_bp
    from .categories import bp as categories_bp
    from .errors import register_error_handlers

    app.register_blueprint(index_bp)
    app.register_blueprint(health_bp, url_prefix="/api")
    app.register_blueprint(counties_bp, url_prefix="/api")
    app.register_blueprint(historical_bp, url_prefix="/api")
    app.register_blueprint(predict_bp, url_prefix="/api")
    app.register_blueprint(refresh_bp, url_prefix="/api")
    app.register_blueprint(metrics_bp, url_prefix="/api")
    app.register_blueprint(categories_bp, url_prefix="/api")

    register_error_handlers(app)
