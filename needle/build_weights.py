import sys
import needle.cli

if __name__ == "__main__":
    sys.argv = [
        "needle",
        "build",
        "checkpoints/needle2.pkl",
        "--lora", "adapter.pkl",
        "--out", "weights.cact"
    ]
    print("[NEEDLE]: Building model weights")
    needle.cli.main()