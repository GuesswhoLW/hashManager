# hashManager

hashManager is a Python script designed to manage and monitor your HiveOS mining farm. It provides real-time information about your workers, network hashrate, block rewards, and estimated daily profits. Currently, this script works with the [Spectre Network](https://github.com/spectre-project), built specifically for the Spectre Miner, but it also works while using TTN miner.

## Features

- Fetches and displays detailed information about your HiveOS workers.
- Monitors network hashrate, $SPR price, and block rewards from Spectre Network API.
- Calculates and displays estimated daily revenue in USD.
- Provides a summary of your farm's performance and block rewards.
- Option to enable advanced view for detailed logging and debugging.
- Option to view wallet address and balance.
- Displays current time and script version.
- Automatically updates the display at regular intervals.

## Requirements

- Python 3.6+
- HiveOS account with API access
- Spectre Network API access
- [Rich](https://github.com/Textualize/rich) for enhanced console output
- [python-dotenv](https://github.com/theskumar/python-dotenv) for managing environment variables

## Installation

### On Hive OS or Linux

1. Clone the repository:
   ```sh
   git clone https://github.com/GuesswhoLW/hashmanager.git
   cd hashmanager
   
2. Install the required Python packages:
   ```sh
   pip install -r requirements.txt

3. Create a .env file in the project directory:
   ```sh
   nano .env
  
4. Add your HiveOS API key and Farm ID to the .env file:
    ```sh
    HIVE_OS_API_KEY=your_hive_os_api_key
    HIVE_OS_FARM_ID=your_hive_os_farm_id    
    
7. Run the script:
   ```sh
   python hashManager.py

### On Windows WSL

1. Install Windows Subsystem for Linux (WSL) and set up a Linux distribution (e.g., Ubuntu). Follow the instructions from the [official WSL documentation](https://docs.microsoft.com/en-us/windows/wsl/install).
   
2. Open your WSL terminal and clone the repository:
   ```sh
   git clone https://github.com/GuesswhoLW/hashmanager.git
   cd hashmanager

3. Install Python and pip if not already installed:
   ```sh
   sudo apt update
   sudo apt install python3 python3-pip

3. Install the required Python packages:
   ```sh
   pip3 install -r requirements.txt
  
4. Create a `.env` file in the project directory and add:
    ```sh
    nano .env  

5. Add your HiveOS API key and Farm ID to the .env file:
   ```sh
   HIVE_OS_API_KEY=your_hive_os_api_key
   HIVE_OS_FARM_ID=your_hive_os_farm_id

6. Create a .gitignore file to ensure the .env file is not uploaded to GitHub:
   ```sh
   nano .gitignore

7. Add the following line to the .gitignore file:
    ```sh
    .env

## Usage

1. Run the script:
   ```sh
   python3 hashManager.py

## Example

  Here's a sample interaction with the script:

  ![image](https://github.com/GuesswhoLW/hashManager/assets/174736759/f055bd53-e36f-4fad-8f42-8fc250d91e9d)

## Notes

  - Ensure that the required Python libraries are installed using the requirements.txt file.
  - If using Hive OS credentials, create a `.env` file with your Hive OS API key and farm ID.
  - If you have trouble finding your farm ID check this [script](https://github.com/GuesswhoLW/showHiveFarmID)
  - Ensure your node is synchronized and the bridge is running when enabling the bridge.
  - If using spectre-miner by [BynaryExpr](https://github.com/BinaryExpr), name your workers without symbols like ``_`` or ``-``.

## To Do

  Future integration with MMPOS to expand compatibility and provide additional mining management options.
  
## Contributing

  Contributions are welcome! Please submit a pull request, open an issue or contact me on discord @GuesswhoLW to discuss your ideas.

## License

  This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Support
  If you find this small project helpful and would like to support my work and future projects, feel free to donate a cup of coffee to my Spectre wallet:
  ```sh
    spectre:qr7nl6z8nc8gmagarmzrnaw90xu2xxzzn8qtg2wql967njendf5eqeqdnmhuc
