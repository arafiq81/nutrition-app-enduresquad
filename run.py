from app import create_app
import logging

app = create_app()

# Enable detailed logging
logging.basicConfig(level=logging.DEBUG)

if __name__ == '__main__':
    print("\n" + "="*60)
    print("Starting Ironman Nutrition Bot")
    print("="*60)
    print("\nAccess the app from:")
    print("  - On this Pi: http://localhost:5000")
    print("  - From your phone: http://<Pi-IP-Address>:5000")
    print("\nPress Ctrl+C to stop the server")
    print("="*60 + "\n")
    
    try:
        app.run(
            host='0.0.0.0',
            port=5000, 
            debug=True
        )
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
