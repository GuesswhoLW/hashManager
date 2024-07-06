import os
import requests
from dotenv import load_dotenv
from datetime import datetime, timedelta
import time
import sys
from rich.console import Console
from rich.table import Table
from rich import box
from rich.columns import Columns

console = Console()
spectre_api_url = "https://api.spectre-network.org/info/hashrate"
spr_price_api_url = "https://api.spectre-network.org/info/price"
block_reward_api_url = "https://api.spectre-network.org/info/blockreward"

class HiveOSManager:
    def __init__(self):
        load_dotenv()
        self.hive_os_api_url = "https://api2.hiveos.farm/api/v2"
        self.hive_os_api_key = os.getenv("HIVE_OS_API_KEY")
        self.farm_id = os.getenv("HIVE_OS_FARM_ID")
        self.start_time = datetime.utcnow()
        self.blocks_found = {}
        self.previous_status = {}

    def get_headers(self):
        return {
            "Authorization": f"Bearer {self.hive_os_api_key}",
            "Content-Type": "application/json"
        }

    def check_workers(self):
        response = requests.get(f"{self.hive_os_api_url}/farms/{self.farm_id}/workers", headers=self.get_headers())
        if response.status_code == 200:
            return response.json()
        else:
            console.print(f"Failed to fetch workers data: {response.status_code} {response.text}", style="bold red")
            return None

    def format_timedelta(self, td):
        days = td.days
        hours, remainder = divmod(td.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        return f"{days}d {hours}h {minutes}m"

    def get_current_hashrate(self):
        response = requests.get(spectre_api_url)
        if response.status_code == 200:
            data = response.json()
            current_hashrate = data.get("hashrate", 0) * 1e6  # Convert from TH to MH
            return current_hashrate
        else:
            console.print(f"Failed to fetch hashrate data: {response.status_code} {response.text}", style="bold red")
            return 0

    def get_current_spr_price(self):
        response = requests.get(spr_price_api_url)
        if response.status_code == 200:
            data = response.json()
            current_price = data.get("price", 0)
            return current_price
        else:
            console.print(f"Failed to fetch SPR price data: {response.status_code} {response.text}", style="bold red")
            return 0

    def get_block_reward(self):
        response = requests.get(block_reward_api_url)
        if response.status_code == 200:
            data = response.json()
            return data.get("blockreward", 0)
        else:
            console.print(f"Failed to fetch block reward data: {response.status_code} {response.text}", style="bold red")
            return 0

    def calculate_estimated_rewards(self, network_hashrate, my_hashrate, block_reward, spr_price):
        if network_hashrate == 0:
            my_portion = 0
        else:
            my_portion = (my_hashrate * 1e-3) / network_hashrate  # Convert my_hashrate from KH/s to MH/s for comparison

        daily_network_reward = block_reward * 86400  # Correct total SPR mined per day
        daily_my_reward = daily_network_reward * my_portion

        estimated_daily_usd = daily_my_reward * spr_price

        return estimated_daily_usd

    def format_workers_data(self, workers_data):
        workers_list = []
        current_time = datetime.utcnow()
        total_hashrate = 0.0
        total_blocks_found = 0

        for worker in workers_data['data']:
            miner_start_time = worker['stats'].get('miner_start_time', 0)
            if miner_start_time != 0:
                mining_time = current_time - datetime.utcfromtimestamp(miner_start_time)
                mining_time_str = self.format_timedelta(mining_time)
            else:
                mining_time_str = 'N/A'

            accepted_shares = worker['miners_summary']['hashrates'][0]['shares'].get('accepted', 0) if 'miners_summary' in worker and 'hashrates' in worker['miners_summary'] and len(worker['miners_summary']['hashrates']) > 0 else 0

            worker_name = worker.get('name', 'N/A')
            hashrate = worker['miners_summary']['hashrates'][0]['hash'] if 'miners_summary' in worker and 'hashrates' in worker['miners_summary'] and len(worker['miners_summary']['hashrates']) > 0 else 0.0

            total_hashrate += hashrate
            total_blocks_found += accepted_shares

            if worker_name not in self.blocks_found:
                self.blocks_found[worker_name] = accepted_shares
            elif accepted_shares > self.blocks_found[worker_name]:
                console.print(f"[bold green]{worker_name} has found a Block![/bold green]")
                self.blocks_found[worker_name] = accepted_shares

            status = "Online" if worker['stats'].get('online', False) else "Offline"
            style = ""
            if worker_name in self.previous_status and self.previous_status[worker_name] == "Online" and status == "Offline":
                style = "bold red"
            self.previous_status[worker_name] = status

            worker_info = {
                "Name": worker_name,
                "Status": status,
                "Temperature": worker['hardware_stats']['cputemp'][0] if 'hardware_stats' in worker and 'cputemp' in worker['hardware_stats'] else 'N/A',
                "Algo": worker['miners_summary']['hashrates'][0]['algo'] if 'miners_summary' in worker and 'hashrates' in worker['miners_summary'] and len(worker['miners_summary']['hashrates']) > 0 else 'N/A',
                "Coin": worker['miners_summary']['hashrates'][0]['coin'] if 'miners_summary' in worker and 'hashrates' in worker['miners_summary'] and len(worker['miners_summary']['hashrates']) > 0 else 'N/A',
                "Hashrate": hashrate,
                "UpTime": mining_time_str,
                "Blocks": accepted_shares,
                "Style": style
            }
            workers_list.append(worker_info)

        summary_info = {
            "Name": "Total",
            "Status": "",
            "Temperature": "",
            "Algo": "",
            "Coin": "",
            "Hashrate": f"{total_hashrate:.2f} KH/s",
            "UpTime": "",
            "Blocks": total_blocks_found
        }

        return workers_list, summary_info

    def display_workers(self):
        console.print("[cyan]Checking Workers...[/cyan]")
        workers = self.check_workers()
        network_hashrate = self.get_current_hashrate()
        spr_price = self.get_current_spr_price()
        block_reward = self.get_block_reward()
        if workers:
            workers_list, summary_info = self.format_workers_data(workers)
            table = Table(show_header=True, header_style="bold green", box=box.SIMPLE)
            table.add_column("Name")
            table.add_column("Status", justify="center")
            table.add_column("Temp", justify="center")
            table.add_column("Algo", justify="center")
            table.add_column("Coin", justify="center")
            table.add_column("Hashrate", justify="center")
            table.add_column("UpTime", justify="center")
            table.add_column("Blocks", justify="center")

            for index, worker in enumerate(workers_list):
                style = "on grey15" if index % 2 == 0 else ""
                if worker["Style"]:
                    style = worker["Style"]
                table.add_row(
                    worker["Name"],
                    worker["Status"],
                    str(worker["Temperature"]),
                    worker["Algo"],
                    worker["Coin"],
                    str(worker["Hashrate"]),
                    worker["UpTime"],
                    str(worker["Blocks"]),
                    style=style
                )

            console.print(table)
            estimated_daily_usd = self.calculate_estimated_rewards(network_hashrate, float(summary_info["Hashrate"].replace(" KH/s", "")), block_reward, spr_price)

            # Creating a stylized summary table without headers
            summary_table = Table(show_header=False, box=box.SIMPLE)
            summary_table.add_column("Metric", style="white")
            summary_table.add_column("Value", style="cyan")
            summary_table.add_row("Network Hashrate", f"{network_hashrate:.2f} MH/s")
            summary_table.add_row("Estimated Daily Revenue", f"${estimated_daily_usd:.2f}")

            # Duplicate the summary table
            summary_table_right = Table(show_header=False, box=box.SIMPLE)
            summary_table_right.add_column("Metric", style="white")
            summary_table_right.add_column("Value", style="cyan")
            summary_table_right.add_row("Your Hashrate", summary_info["Hashrate"])
            summary_table_right.add_row("Blocks Found So Far", str(summary_info["Blocks"]))

            # Display both summary tables side by side
            console.print(Columns([summary_table, summary_table_right]))
        else:
            console.print("[bold red]No workers data found.[/bold red]")

    def run(self):
        try:
            while True:
                self.display_workers()
                for i in range(30):
                    sys.stdout.write('\r' + 'Loading' + '.' * (i % 4))
                    sys.stdout.flush()
                    time.sleep(1)
                sys.stdout.write('\r' + ' ' * 10 + '\r')
                sys.stdout.flush()
        except KeyboardInterrupt:
            console.print("\nExiting...")

if __name__ == "__main__":
    manager = HiveOSManager()
    manager.run()
