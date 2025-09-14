from sqlalchemy import event
from sqlalchemy.engine import Engine
import logging

# Configure logging
logger = logging.getLogger("sqlalchemy.events")

def setup_sqlalchemy_events():
    """Configure SQLAlchemy event listeners for debugging"""
    @event.listens_for(Engine, 'before_cursor_execute')
    def before_cursor_execute(conn, cursor, statement, params, context, executemany):
        conn.info.setdefault('query_start_time', []).append(time.time())
        logger.debug("SQL Query: %s", statement)
        if params:
            logger.debug("Parameters: %r", params)

    @event.listens_for(Engine, 'after_cursor_execute')
    def after_cursor_execute(conn, cursor, statement, params, context, executemany):
        total = time.time() - conn.info['query_start_time'].pop(-1)
        logger.debug("Query completed in %f seconds", total)

    @event.listens_for(Engine, 'handle_error')
    def handle_error(exception_context):
        logger.error("SQLAlchemy Error", exc_info=exception_context.original_exception)
        return False  # Let the exception propagate

# Import time module for timing queries
import time
