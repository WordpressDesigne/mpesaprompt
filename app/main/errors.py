from flask import render_template, request, jsonify
from app import db
from app.main import main

@main.app_errorhandler(403)
def forbidden(error):
    """Handle 403 Forbidden errors."""
    if request.accept_mimetypes.accept_json and \
            not request.accept_mimetypes.accept_html:
        response = jsonify({'error': 'forbidden'})
        response.status_code = 403
        return response
    return render_template('errors/403.html'), 403

@main.app_errorhandler(404)
def page_not_found(error):
    """Handle 404 Not Found errors."""
    if request.accept_mimetypes.accept_json and \
            not request.accept_mimetypes.accept_html:
        response = jsonify({'error': 'not found'})
        response.status_code = 404
        return response
    return render_template('errors/404.html'), 404

@main.app_errorhandler(413)
def request_entity_too_large(error):
    """Handle 413 Request Entity Too Large errors."""
    if request.accept_mimetypes.accept_json and \
            not request.accept_mimetypes.accept_html:
        response = jsonify({'error': 'file too large'})
        response.status_code = 413
        return response
    return render_template('errors/413.html'), 413

@main.app_errorhandler(500)
def internal_server_error(error):
    """Handle 500 Internal Server errors."""
    db.session.rollback()
    if request.accept_mimetypes.accept_json and \
            not request.accept_mimetypes.accept_html:
        response = jsonify({'error': 'internal server error'})
        response.status_code = 500
        return response
    return render_template('errors/500.html'), 500

@main.app_errorhandler(503)
def service_unavailable(error):
    """Handle 503 Service Unavailable errors."""
    if request.accept_mimetypes.accept_json and \
            not request.accept_mimetypes.accept_html:
        response = jsonify({'error': 'service unavailable'})
        response.status_code = 503
        return response
    return render_template('errors/503.html'), 503

# Register error handlers
def init_app(app):
    """Register error handlers with the Flask app."""
    app.register_error_handler(403, forbidden)
    app.register_error_handler(404, page_not_found)
    app.register_error_handler(413, request_entity_too_large)
    app.register_error_handler(500, internal_server_error)
    app.register_error_handler(503, service_unavailable)
