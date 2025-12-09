from flask import Flask, render_template, request, jsonify
from werkzeug.middleware.proxy_fix import ProxyFix
import logging

from soup.config import logger
from soup.game import SoupFlow


# Configuration
class Config:
    HOST = "0.0.0.0"
    PORT = 42345
    MIN_CONTENT_LENGTH = 5
    IGNORED_LOG_PATTERNS = ['post /update', 'get /update']


# Custom Flask app with game state
class SoupWebApp(Flask):
    def __init__(self, import_name):
        super().__init__(import_name)
        self.soup_flow = SoupFlow()


# Logging filter to reduce noise
class IgnoreHeartbeatFilter(logging.Filter):
    def filter(self, record):
        msg = record.getMessage().lower()
        return not any(pattern in msg for pattern in Config.IGNORED_LOG_PATTERNS)


# Initialize Flask app
app = SoupWebApp(__name__)

# Configure proxy headers for deployment behind reverse proxy
app.wsgi_app = ProxyFix(
    app.wsgi_app,
    x_for=1,
    x_proto=1,
    x_host=1,
    x_port=1,
    x_prefix=1
)

# Apply logging filter
logging.getLogger('werkzeug').addFilter(IgnoreHeartbeatFilter())


# Helper functions
def get_current_soup_question():
    """Extract current soup question safely"""
    current_soup = app.soup_flow.game_state.get("current_soup")
    return current_soup['question'] if current_soup else None


def get_new_chats(client_game_id, client_chat_id):
    """Get new chat messages based on client state"""
    server_game_id = app.soup_flow.game_state["game_id"]
    
    # If game changed, send all chat history
    if client_game_id != server_game_id:
        return app.soup_flow.chat_history
    
    # Otherwise, send only new messages
    total_chats = len(app.soup_flow.chat_history)
    if client_chat_id < total_chats:
        return app.soup_flow.chat_history[client_chat_id:]
    
    return []


def create_response(code=0, msg="", **kwargs):
    """Create standardized JSON response"""
    response = {"code": code, "msg": msg}
    response.update(kwargs)
    return jsonify(response)


def validate_request(required_fields):
    """Validate request has required fields"""
    if not request.json:
        return False, "Invalid JSON"
    
    for field in required_fields:
        if field not in request.json:
            return False, f"Missing field: {field}"
    
    return True, None


# Routes
@app.route("/")
def index():
    """Serve main page"""
    return render_template("index.html")


@app.route("/update", methods=["POST"])
def handle_update():
    """Handle game state polling"""
    # Validate request
    is_valid, error = validate_request(['cmd'])
    if not is_valid:
        return create_response(1, error)
    
    req = request.json
    cmd = req['cmd'].strip().lower()
    
    if cmd != "get_info":
        return create_response(1, "Invalid command")
    
    # Get new chat messages
    client_game_id = req.get('game_id', -1)
    client_chat_id = req.get('chat_id', 0)
    new_chats = get_new_chats(client_game_id, client_chat_id)
    
    # Build response
    return create_response(
        msg="Info renewed",
        ai_running=app.soup_flow.ai_running,
        game_id=app.soup_flow.game_state["game_id"],
        current_soup=get_current_soup_question(),
        new_chats=new_chats
    )


@app.route("/cmd", methods=["POST"])
def handle_command():
    """Handle game commands"""
    # Validate request
    is_valid, error = validate_request(['cmd'])
    if not is_valid:
        return create_response(1, error)
    
    req = request.json
    cmd = req['cmd'].strip().lower()
    
    logger.info(f"Command received: {cmd} - {req.get('content', '')[:50]}")
    
    # Handle new game command (allowed even when AI is running)
    if cmd == "new_game":
        if app.soup_flow.ai_running:
            return create_response(1, "AI is processing. Please wait.")
        
        app.soup_flow.start_new_game()
        return create_response(
            msg="New game started",
            soup_question=get_current_soup_question()
        )
    
    # Check if game is running for other commands
    if not app.soup_flow.game_state.get("running", False):
        return create_response(1, "No game is running. Start a new game first.")
    
    # Check if AI is busy
    if app.soup_flow.ai_running:
        return create_response(1, "AI is processing. Please wait.")
    
    # Handle end game command
    if cmd == "end_game":
        app.soup_flow.end_game()
        return create_response(msg="Game ended")
    
    # Handle ask/answer commands
    if cmd.startswith("ask") or cmd.startswith("ans"):
        # Validate content
        content = req.get('content', '').strip()
        if len(content) < Config.MIN_CONTENT_LENGTH:
            return create_response(1, f"Content too short (minimum {Config.MIN_CONTENT_LENGTH} characters)")
        
        # Route to appropriate handler
        if cmd.startswith("ask"):
            result = app.soup_flow.handle_ask(req)
        else:
            result = app.soup_flow.handle_answer(req)
        
        return jsonify(result)
    
    # Unknown command
    return create_response(1, f"Unknown command: {cmd}")


# Error handlers
@app.errorhandler(404)
def not_found(error):
    return create_response(1, "Endpoint not found"), 404


@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal error: {error}")
    return create_response(1, "Internal server error"), 500


# Run server
if __name__ == "__main__":
    logger.info(f"Starting Kame Soup server on {Config.HOST}:{Config.PORT}")
    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=False  # Set to True for development
    )