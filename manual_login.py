from bypass_login import run_headless_login
if __name__ == "__main__":
    print("========================================")
    print("      MANUAL LOGIN HELPER               ")
    print("========================================")
    print("A Chrome window will open.")
    print("Please log in to Webull inside that window.")
    print("Wait until this window says SUCCESS.")
    print("========================================")
    success = run_headless_login("","")
    if success:
        print("\nLogin Successful! You can close this window and restart the server.")
    else:
        print("\nLogin Failed. Please try again.")
    input("Press Enter to exit...")
