import argparse
import os
import sys

# Import ProxymanEntry only needed if we add type hints later, not for runtime
# from dai_tracker.proxyman_entry import ProxymanEntry
from trace_shrink.proxyman_log_reader import ProxymanLogV2Reader

MAX_BODY_LINES = 5


def main():
    parser = argparse.ArgumentParser(
        description="List entries from a Proxyman log file and show response body snippets."
    )
    parser.add_argument(
        "logfile", help="Path to the .proxymanlog or .proxymanlogv2 file"
    )
    parser.add_argument(
        "-n",
        "--num_lines",
        type=int,
        default=MAX_BODY_LINES,
        help=f"Number of response body lines to display (default: {MAX_BODY_LINES})",
    )

    args = parser.parse_args()

    log_file_path = args.logfile
    max_lines = args.num_lines

    if not os.path.exists(log_file_path):
        print(f"Error: Log file not found: {log_file_path}", file=sys.stderr)
        sys.exit(1)

    try:
        print(f"Processing log file: {log_file_path}\n")
        reader = ProxymanLogV2Reader(log_file_path)
    except (FileNotFoundError, ValueError, RuntimeError) as e:
        print(f"Error initializing log reader: {e}", file=sys.stderr)
        sys.exit(1)

    # Get the list of filenames from the index
    entry_filenames = reader.list_entries()

    if not entry_filenames:
        print("No request entries found in the log file.")
        sys.exit(0)

    print(
        f"Found {len(entry_filenames)} entries. Displaying first {max_lines} lines of response body:\n"
    )

    processed_count = 0
    error_count = 0
    # Iterate through filenames (which are the entry identifiers)
    for entry_id in entry_filenames:
        print(f"--- Entry: {entry_id} ---")
        # Get the ProxymanEntry object directly using the entry_id (filename)
        entry_obj = reader.get_entry(entry_id)  # Use the new parameter name

        if entry_obj is None:
            # get_entry prints its own errors/warnings
            print("  Error: Could not retrieve or parse content for this entry.")
            error_count += 1
            continue

        # Now we already have the ProxymanEntry object
        try:
            # Directly use methods of the ProxymanEntry object
            response_body_text = entry_obj.get_body_as_text("response")

            if response_body_text:
                lines = response_body_text.splitlines()
                print("  Response Body Snippet:")
                for i, line in enumerate(lines):
                    if i >= max_lines:
                        print(
                            f"  ... (truncated - {len(lines) - max_lines} more lines)"
                        )
                        break
                    print(f"  {line}")
            else:
                if entry_obj.data.get("response", {}).get("bodyData") is not None:
                    print("  Response body found but could not be decoded as text.")
                else:
                    print("  No response body data found.")
            processed_count += 1
        except Exception as e:
            # Catch potential errors during body processing
            print(f"  Error processing body data for {entry_id}: {e}")
            error_count += 1
        print("-" * (len(entry_id) + 14))  # Separator line
        print()  # Blank line for readability

    print(f"\nFinished processing.")
    print(f"Successfully displayed snippets for: {processed_count} entries.")
    if error_count > 0:
        print(f"Encountered errors retrieving/processing: {error_count} entries.")


if __name__ == "__main__":
    main()
