import argparse
from .selector import list_and_select_backend, check_authentication, setup_authentication


def main():
    """Main CLI entry point."""
    
    parser = argparse.ArgumentParser(
        description="QHRF Backend Selector - Interactive IBM Quantum backend selection"
    )
    parser.add_argument(
        "--check-auth", 
        action="store_true",
        help="Check if IBM Quantum authentication is working"
    )
    parser.add_argument(
        "--setup-auth",
        action="store_true", 
        help="Show authentication setup instructions"
    )
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 1.0.0"
    )
    
    args = parser.parse_args()
    
    if args.check_auth:
        check_authentication()
    elif args.setup_auth:
        setup_authentication()
    else:
        # Default: run interactive backend selection
        print("🧪 QHRF Backend Selector")
        print("="*40)
        
        if check_authentication():
            service, backend = list_and_select_backend()
            if service and backend:
                print("\n✅ Backend selection complete!")
                print("🚀 Ready for QHRF experiments!")
            else:
                print("\n❌ No backend selected")
        else:
            print("\nPlease authenticate first before selecting backends.")


if __name__ == "__main__":
    main()