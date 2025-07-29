import threading
import time
import inspect
from flask import Flask, jsonify, request

class DataUpdater:
    def __init__(self, var_names, host='127.0.0.1', port=5000):
        # Get the caller's global variables
        caller_globals = inspect.currentframe().f_back.f_globals
        self.watchers = {}  # Maps variable names to getter/setter lambdas
        self.types = {}     # Maps variable names to their types
        for name in var_names:
            if name not in caller_globals:
                raise KeyError(f"Global variable '{name}' not found in caller globals")
            # Store getter and setter for each variable
            self.watchers[name] = (
                lambda n=name: caller_globals[n],
                lambda v, n=name: caller_globals.__setitem__(n, v)
            )
            self.types[name] = type(caller_globals[name])
        # Initialize data dictionary with current values
        self.data = {name: getter() for name, (getter, _) in self.watchers.items()}

        self.app = Flask(__name__)  # Create Flask app
        self.host = host
        self.port = port
        self._setup_routes()        # Set up HTTP routes
        self._server_thread = None  # Thread for running the server

    def _setup_routes(self):
        # Serve the index.html file at the root
        @self.app.route('/')
        def index():
            return self._default_html()

        # Endpoint to get current data as JSON
        @self.app.route('/data', methods=['GET'])
        def get_data():
            return jsonify(self.data)

        # Endpoint to update data via POST
        @self.app.route('/data', methods=['POST'])
        def post_data():
            req = request.json or {}
            for name, val in req.items():
                if name in self.watchers:
                    try:
                        # Convert value to correct type and update variable
                        typed_val = self.types[name](eval(val))
                        _, setter = self.watchers[name]
                        setter(typed_val)
                    except Exception as e:
                        print(f"Failed to convert {val} to {self.types[name]}: {e}")
            return jsonify(status='ok')

    def start_server(self):
        # Start the Flask server in a separate thread
        if self._server_thread is None:
            self._server_thread = threading.Thread(
                target=self.app.run,
                kwargs={
                    'host': self.host,
                    'port': self.port,
                    'debug': False,
                    'use_reloader': False
                }
            )
            self._server_thread.start()
            print(f"Server running at http://{self.host}:{self.port}")

    def update(self):
        # Refresh the data dictionary with current variable values
        for name, (getter, _) in self.watchers.items():
            self.data[name] = getter()

    def stop(self):
        # Placeholder for stopping the server (not implemented)
        pass

    def _default_html(self):
        # Returns a default HTML page for the web interface
        return """
<!DOCTYPE html>
<html>
<head>
  <title>Data Updater</title>
  <style>
    body { font-family: sans-serif; padding: 2rem; }
    label { display: block; margin-top: 1rem; }
    input { margin-left: 0.5rem; }
    button { margin-top: 1rem; margin-right: 0.5rem; }
  </style>
</head>
<body>
  <h1>Monitor and Update Variables</h1>
  <form id="data-form"></form>
  <button onclick="submitData()">Submit</button>
  <button onclick="fetchData()">Refresh</button>

  <script>
    // Fetches data from the server and populates the form
    async function fetchData() {
      const res = await fetch('/data');
      const data = await res.json();
      const form = document.getElementById('data-form');
      form.innerHTML = '';
      for (const key in data) {
        const label = document.createElement('label');
        label.textContent = key;
        const input = document.createElement('input');
        input.name = key;
        input.value = data[key];
        label.appendChild(input);
        form.appendChild(label);
      }
    }

    // Sends updated data to the server
    async function submitData() {
      const inputs = document.querySelectorAll('#data-form input');
      const payload = {};
      inputs.forEach(input => payload[input.name] = input.value);
      await fetch('/data', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
    }

    fetchData(); // Initial fetch on page load
  </script>
</body>
</html>
        """

# -----------------------
# Example usage
# -----------------------
if __name__ == '__main__':
    x = 10
    message = 'hello'
    arr = ["1",2]
    print(type(arr))

    # Create DataUpdater to monitor variables x, message, and arr
    updater = DataUpdater(['x', 'message','arr'])
    updater.start_server()

    try:
        while True:
            x += 5
            print(x)
            print(message)
            print(arr)
            updater.update()  # Update the server with new variable values
            time.sleep(1)
    except KeyboardInterrupt:
        updater.stop()  # Stop the server on Ctrl+C