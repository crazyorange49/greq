import csv
import os 

class DataCollector:
    FILE_PATH = "LLM_Experimental/Training_Data.csv"




    def write_data(self, data, mode='a'):
        """Writes data to a CSV file.

        Args:
            data (list of dict): The data to write to the CSV file.
            mode (str): The file mode, 'a' for append and 'w' for write. Default is 'a'.
        """
        if not data[0]["message"].startswith("/") or data[0]["message"].startswith("!") or "http" not in data[0]["message"] or len(data[0]["message"]) > 0:
            with open(self.FILE_PATH, mode, newline='') as csvfile:
                if data:
                    fieldnames = data[0].keys()
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    if mode == 'w':
                        writer.writeheader()
                    writer.writerows(data)
    
    def on_data_received(self, new_data):
        """Callback function to handle new data.

        Args:
            new_data (list of dict): The new data to be written to the CSV file.
        """
        channel = new_data.channel.id
        user = new_data.author.name
        message = new_data.content
        new_data = {'channel': channel, 'user': user, 'message': message}
        self.write_data(self, new_data)

