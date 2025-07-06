# conductor.py
# Version 1.2 - Added GradleManager to the orchestra
# The main controller for the Syncphony Orchestra.
# The Conductor loads a "Symphony" (a master plan in JSON format),
# assembles the orchestra of Musician agents, and directs the entire
# performance by dispatching tasks and monitoring progress.

import sys
import json
import time
import multiprocessing

# We need to explicitly handle the case where this script is imported by a child process
# on Windows by using if __name__ == '__main__':
from musician import main as musician_main 

class Conductor:
    """
    Orchestrates the entire task execution process.
    """
    def __init__(self, symphony_path: str):
        self.symphony_path = symphony_path
        self.symphony = None
        self.task_states = {}  # Tracks the status of each task
        self.task_dependencies = {} # Stores the dependencies for each task

        # Create the communication channels
        self.task_queue = multiprocessing.Queue()
        self.reporting_queue = multiprocessing.Queue()
        
        # --- UPDATED ORCHESTRA ROSTER ---
        self.orchestra_composition = [
            "FileSystem",
            "CodeWriter",
            "ShellExecutor",
            "GradleManager"  # The new specialist joins the orchestra
        ]
        self.musician_processes = []

    def load_symphony(self):
        """Loads the master plan from the JSON file."""
        print("[Conductor]: Loading the Symphony...")
        try:
            with open(self.symphony_path, 'r') as f:
                self.symphony = json.load(f)
            for task_id, task_details in self.symphony.items():
                self.task_states[task_id] = "pending"
                self.task_dependencies[task_id] = task_details.get("dependencies", [])
            print("[Conductor]: Symphony loaded successfully.")
            return True
        except FileNotFoundError:
            print(f"[Conductor]: ERROR! Symphony file not found at {self.symphony_path}", file=sys.stderr)
            return False
        except json.JSONDecodeError as e:
            print(f"[Conductor]: ERROR! Invalid JSON in {self.symphony_path}: {e}", file=sys.stderr)
            return False

    def assemble_orchestra(self):
        """Launches the Musician processes."""
        print("[Conductor]: Assembling the Orchestra...")
        for role in self.orchestra_composition:
            process = multiprocessing.Process(
                target=musician_main,
                args=(role, self.task_queue, self.reporting_queue)
            )
            process.daemon = True
            process.start()
            self.musician_processes.append({"role": role, "process": process})
        print(f"[Conductor]: Orchestra assembled with {len(self.musician_processes)} Musicians.")

    def shutdown_orchestra(self):
        """Terminates all Musician processes."""
        print("[Conductor]: The performance has concluded. Shutting down the Orchestra.")
        for p_info in self.musician_processes:
            if p_info["process"].is_alive():
                p_info["process"].terminate()
                p_info["process"].join()

    def listen_for_reports(self):
        """Checks the reporting queue for any new messages from Musicians."""
        while not self.reporting_queue.empty():
            try:
                report_raw = self.reporting_queue.get_nowait() # Use non-blocking get
                report = json.loads(report_raw)
                task_id = report["task_id"]
                status = report["status"]
                progress = report["progress"]
                
                print(f"[Report]: Task '{task_id}' by {report['sender_role']} -> {status} ({progress}%)")

                if status == "failure":
                    print(f"[Conductor]: CRITICAL ERROR! Task '{task_id}' failed: {report['error_message']}", file=sys.stderr)
                    self.task_states[task_id] = "failed"
                elif status == "success":
                    self.task_states[task_id] = "completed"
            except Exception as e:
                print(f"[Conductor]: Error processing report: {e}", file=sys.stderr)


    def dispatch_tasks(self):
        """Finds and dispatches tasks whose dependencies are met."""
        for task_id, state in self.task_states.items():
            if state == "pending":
                dependencies = self.task_dependencies.get(task_id, [])
                # This print statement is very useful for debugging dependencies
                # print(f"[Conductor]: Checking dependencies for task '{task_id}': {dependencies}")
                
                deps_exist = all(dep_id in self.task_states for dep_id in dependencies)
                if not deps_exist:
                    continue

                deps_met = all(self.task_states.get(dep_id) == "completed" for dep_id in dependencies)
                
                if deps_met:
                    print(f"[Conductor]: >>> Dispatching task '{task_id}'...")
                    task_info = self.symphony[task_id]
                    message = {
                        "recipient_role": task_info["role"],
                        "task_id": task_id,
                        "action": task_info["action"],
                        "parameters": task_info["parameters"]
                    }
                    self.task_queue.put(json.dumps(message))
                    self.task_states[task_id] = "dispatched"

    def conduct(self):
        """The main loop for the Conductor."""
        if not self.load_symphony():
            return

        self.assemble_orchestra()
        print("\n[Conductor]: === Performance Starting ===\n")

        # Give musicians a moment to initialize
        time.sleep(1)

        start_time = time.time()
        while True:
            self.dispatch_tasks()
            self.listen_for_reports()

            if any(state == "failed" for state in self.task_states.values()):
                print("\n[Conductor]: A critical failure occurred. Halting the Symphony.", file=sys.stderr)
                break
            
            if all(state == "completed" for state in self.task_states.values()):
                print("\n[Conductor]: === The Symphony is complete. All tasks executed successfully. ===")
                break

            # Add a timeout to prevent an infinite loop if something goes wrong
            if time.time() - start_time > 300: # 5 minute timeout
                print("\n[Conductor]: ERROR! Performance timed out. Halting the Symphony.", file=sys.stderr)
                break

            time.sleep(1)

        self.shutdown_orchestra()

if __name__ == '__main__':
    multiprocessing.freeze_support()
    
    if len(sys.argv) < 2:
        print("Usage: python conductor.py <path_to_symphony.json>")
        sys.exit(1)
    
    symphony_file_path = sys.argv[1]
    conductor = Conductor(symphony_file_path)
    conductor.conduct()
