import sys
import needle.cli

if __name__ == "__main__":
    sys.argv = [
        "needle",
        "finetune",
        "needle.dataset.jsonl",
        "--epochs", "10",
        "--out", "adapter.pkl"
    ]
    print("[NEEDLE]: Building model checkpoint")
    needle.cli.main()