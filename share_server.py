import time
import sys
from pyngrok import ngrok

def share():
    try:
        ngrok.set_auth_token("37IlOuQMvHelIL4P4h8idgehLbp_3YB22psQGfzCmevZKwByA")
        # Open a HTTP tunnel on the default port 5000
        # <NgrokTunnel: "http://<public_sub>.ngrok.io" -> "http://localhost:5000">
        public_url = ngrok.connect(5000, domain="unplenteous-gracelyn-nonoligarchical.ngrok-free.dev").public_url
        print(f"URL: {public_url}")
        sys.stdout.flush()
    except Exception as e:
        print(f"Error: {e}")
        return

    # Keep the process alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping...")
        ngrok.kill()

if __name__ == "__main__":
    share()
