import os
import sys
from core.agent_loop import AgentLoop

def main():
    config_path = os.path.join("config", "config.yaml")
    
    if not os.path.exists(config_path):
        print("❌ Config not found.")
        sys.exit(1)

    print("========================================")
    print("      JARVIS AUTONOMOUS AGENT v2.0      ")
    print("========================================")
    
    agent = AgentLoop(config_path)
    agent.run()

if __name__ == "__main__":
    main()
