import subprocess
import sys

def run(cmd):
    print("running:", " ".join(cmd))
    subprocess.check_call(cmd)

def main():
    python = sys.executable
    run([python, "manage.py", "makemigrations"])
    run([python, "manage.py", "migrate"])
    run([python, "scripts/init_admin.py"])
    run([python, "scripts/seed_demo_data.py"])
    print("demo initialization complete")

if __name__ == "__main__":
    main()
