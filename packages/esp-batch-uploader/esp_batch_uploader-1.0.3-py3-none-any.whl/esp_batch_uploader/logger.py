import logging
import datetime
import os
import csv

class CSVLogger:
    def __init__(self, csv_file_path):
        self.csv_file_path = csv_file_path
        self.fieldnames = ['timestamp', 'file', 'ip', 'status', 'message']
        
        # Create CSV file with headers if it doesn't exist
        if not os.path.exists(csv_file_path):
            with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=self.fieldnames)
                writer.writeheader()
    
    def log(self, file, ip, status, message):
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        with open(self.csv_file_path, 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.fieldnames)
            writer.writerow({
                'timestamp': timestamp,
                'file': file,
                'ip': ip,
                'status': status,
                'message': message
            })

def setup_logger(verbose=False):
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    logs_dir = os.path.join(os.getcwd(), 'logs')
    os.makedirs(logs_dir, exist_ok=True)

    traceback_log = os.path.join(logs_dir, f"traceback-file-transfer-{timestamp}.txt")
    status_log = os.path.join(logs_dir, f"status-file-transfer-{timestamp}.txt")
    summary_csv = os.path.join(logs_dir, f"summary-{timestamp}.csv")

    # File-only logging for the main logger
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
        handlers=[
            logging.FileHandler(traceback_log, encoding='utf-8')
        ]
    )

    # Status logger to file + console
    status_logger = logging.getLogger("StatusLogger")
    status_logger.setLevel(logging.INFO)
    status_logger.propagate = False

    # File handler
    status_file_handler = logging.FileHandler(status_log, encoding='utf-8')
    status_file_handler.setLevel(logging.INFO)
    status_file_handler.setFormatter(logging.Formatter("%(asctime)s [STATUS] %(message)s"))
    status_logger.addHandler(status_file_handler)

    # Stream handler (console output)
    status_stream_handler = logging.StreamHandler()
    status_stream_handler.setLevel(logging.INFO)
    status_stream_handler.setFormatter(logging.Formatter("[STATUS] %(message)s"))
    status_logger.addHandler(status_stream_handler)

    # CSV logger
    csv_logger = CSVLogger(summary_csv)

    return logging.getLogger("ESP32BatchServer"), status_logger, csv_logger

# Example usage:
if __name__ == "__main__":
    main_logger, status_logger, csv_logger = setup_logger()
    
    # Example of using the CSV logger
    csv_logger.log("test_file.bin", "192.168.1.100", "SUCCESS", "File transferred successfully")
    csv_logger.log("config.json", "192.168.1.101", "FAILED", "Connection timeout")
    
    # Regular logging still works
    main_logger.info("This goes to the traceback log file")
    status_logger.info("This goes to status log and console")