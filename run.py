


# Run a test server.
from disxss import app
from disxss import db_utils
db_utils.init_db()

db_utils.populate_db()

app.run(host='0.0.0.0', port=8080, debug=True)
