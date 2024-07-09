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
balance_api_url = "https://api.spectre-network.org/addresses"

class HashManager:
    def __init__(self):
        load_dotenv()
        self.hive_os_api_url = "https://api2.hiveos.farm/api/v2"
        self.hive_os_api_key = os.getenv("HIVE_OS_API_KEY")
        self.hive_farm_id = os.getenv("HIVE_OS_FARM_ID")
        self.start_time = datetime.utcnow()
        self.blocks_found = {}
        self.previous_status = {}
        self.tnn_enabled = False
        self.tnn_ip = ""
        self.bridge_metrics = {}
        self.advanced_view = False
        self.wallet_view = False
        self.wallets = {}
        self.wallet_balance = "N/A"

    def get_headers(self):
        return {
            "Authorization": f"Bearer {self.hive_os_api_key}",
            "Content-Type": "application/json"
        }

    def check_hive_workers(self):
        response = requests.get(f"{self.hive_os_api_url}/farms/{self.hive_farm_id}/workers", headers=self.get_headers())
        if response.status_code == 200:
            return response.json()
        else:
            console.print(f"Failed to fetch workers data from HiveOS: {response.status_code} {response.text}", style="bold red")
            return None

    def get_wallet_address(self, farm_id, wallet_id):
        response = requests.get(f"{self.hive_os_api_url}/farms/{farm_id}/wallets/{wallet_id}", headers=self.get_headers())
        if response.status_code == 200:
            data = response.json()
            return data.get("wal", "")
        else:
            console.print(f"Failed to fetch wallet address: {response.status_code} {response.text}", style="bold red")
            return ""

    def get_wallet_balance(self, wallet_address):
        response = requests.get(f"{balance_api_url}/{wallet_address}/balance")
        if response.status_code == 200:
            data = response.json()
            balance = data.get("balance", 0)
            balance = int(balance / 100000000)  # Convert to correct units and remove decimals
            return str(balance) + " [bold red]SPR[/bold red]"  # Add SPR in red next to it
        else:
            console.print(f"Failed to fetch wallet balance: {response.status_code} {response.text}", style="bold red")
            return "N/A"

    def format_timedelta(self, td):
        days = td.days
        hours, remainder = divmod(td.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        return f"{days}d {hours}h {minutes}m"

    def get_current_hashrate(self):
        response = requests.get(spectre_api_url)
        if response.status_code == 200:
            data = response.json()
            current_hashrate = data.get("hashrate", 0) * 1e6
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
            my_portion = (my_hashrate * 1e-3) / network_hashrate

        daily_network_reward = block_reward * 86400
        daily_my_reward = daily_network_reward * my_portion

        estimated_daily_usd = daily_my_reward * spr_price

        return estimated_daily_usd

    def get_bridge_metrics(self):
        if not self.tnn_enabled:
            return
        try:
            url = f"http://{self.tnn_ip}:2114/metrics"
            response = requests.get(url)
            if response.status_code == 200:
                try:
                    metrics = response.text
                    self.bridge_metrics = self.parse_metrics(metrics)
                except ValueError as e:
                    console.print(f"Error parsing bridge metrics: {e}")
                    console.print(f"Response content: {response.text}")
            else:
                console.print(f"Failed to fetch bridge metrics: {response.status_code} {response.text}", style="bold red")
        except Exception as e:
            console.print(f"Error fetching bridge metrics: {e}", style="bold red")

    def parse_metrics(self, metrics):
        data = {}
        for line in metrics.splitlines():
            if line.startswith("spr_blocks_mined{"):
                parts = line.split(",")
                worker_part = [p for p in parts if p.startswith('worker="')][0]
                worker_name = worker_part.split('=')[1].strip('"')
                worker_name = worker_name.split('}')[0].split('"')[0]
                blocks_count = int(line.split()[-1])
                data[worker_name] = {"blocks": blocks_count}
                if self.advanced_view:
                    console.print(f"Parsed {worker_name} with {blocks_count} blocks")
        return data

    def format_workers_data(self, workers_data):
        workers_list = []
        current_time = datetime.utcnow()
        total_hashrate = 0.0
        total_blocks_found = 0

        for worker in workers_data:
            miner_start_time = worker.get('stats', {}).get('miner_start_time', 0)
            if miner_start_time != 0:
                mining_time = current_time - datetime.utcfromtimestamp(miner_start_time)
                mining_time_str = self.format_timedelta(mining_time)
            else:
                mining_time_str = 'N/A'

            accepted_shares = 0
            hashrates = []
            if 'miners_summary' in worker and 'hashrates' in worker['miners_summary']:
                hashrates = worker['miners_summary']['hashrates']
                if len(hashrates) > 0:
                    shares = hashrates[0].get('shares', {})
                    accepted_shares = shares.get('accepted', 0)

            worker_name = worker.get('name', 'N/A')
            hashrate = 0.0
            if 'miners_summary' in worker and 'hashrates' in worker['miners_summary']:
                if len(hashrates) > 0:
                    hashrate = hashrates[0].get('hash', 0.0)

            miner = 'N/A'
            wallet = 'N/A'
            if 'flight_sheet' in worker:
                flight_sheet = worker['flight_sheet']
                if 'items' in flight_sheet and len(flight_sheet['items']) > 0:
                    miner = flight_sheet['items'][0].get('miner_alt', 'N/A')
                    wallet_id = flight_sheet['items'][0].get('wal_id', 'N/A')
                    if wallet_id not in self.wallets:
                        wallet_address = self.get_wallet_address(self.hive_farm_id, wallet_id)
                        self.wallets[wallet_id] = wallet_address
                        self.wallet_balance = self.get_wallet_balance(wallet_address)
                    wallet = self.wallets.get(wallet_id, 'N/A')

            total_hashrate += hashrate

            if miner == 'tnn-miner':
                if worker_name in self.bridge_metrics:
                    blocks_found = self.bridge_metrics[worker_name].get("blocks", 0)
                    if self.advanced_view:
                        console.print(f"Worker: {worker_name}, Blocks from Bridge: {blocks_found}")

                    if worker_name not in self.blocks_found:
                        self.blocks_found[worker_name] = blocks_found
                    elif blocks_found > self.blocks_found[worker_name]:
                        console.print(f"[bold green]{worker_name} has found a Block![/bold green]")
                        self.blocks_found[worker_name] = blocks_found
                else:
                    blocks_found = "[bold red]Enable TNN[/bold red]"
            else:
                blocks_found = accepted_shares
                if self.advanced_view:
                    console.print(f"Worker: {worker_name}, Blocks from Hive: {accepted_shares}")
                if worker_name not in self.blocks_found:
                    self.blocks_found[worker_name] = accepted_shares
                elif accepted_shares > self.blocks_found[worker_name]:
                    if worker_name not in self.bridge_metrics:
                        console.print(f"[bold green]{worker_name} has found a Block![/bold green]")
                    self.blocks_found[worker_name] = accepted_shares

            if isinstance(blocks_found, int):
                total_blocks_found += blocks_found

            status = "Online" if worker.get('status') == 'ok' or worker.get('stats', {}).get('online', False) else "Offline"
            style = ""
            if worker_name in self.previous_status and self.previous_status[worker_name] == "Online" and status == "Offline":
                style = "bold red"
            self.previous_status[worker_name] = status

            worker_info = {
                "Name": worker_name,
                "Status": status,
                "Temperature": worker.get('hardware_stats', {}).get('cputemp', ['N/A'])[0],
                "Algo": hashrates[0].get('algo', 'N/A') if len(hashrates) > 0 else 'N/A',
                "Miner": miner,
                "Hashrate": f"{hashrate:.2f}",
                "UpTime": mining_time_str,
                "Blocks": str(blocks_found),
                "Style": style
            }
            workers_list.append(worker_info)

        return workers_list

    def display_workers(self):
        if self.advanced_view:
            console.print("[cyan]Checking Workers...[/cyan]")
        self.get_bridge_metrics()  # Fetch bridge metrics first

        workers = []
        if self.hive_os_api_key and self.hive_farm_id:
            hive_workers = self.check_hive_workers()
            if hive_workers:
                hive_workers_list = self.format_workers_data(hive_workers['data'])
                workers.extend(hive_workers_list)

        # Filter out offline workers
        workers = [worker for worker in workers if worker["Status"] == "Online"]

        if workers:
            workers.sort(key=lambda x: x["Name"])  # Sort workers alphabetically by name

            if self.wallet_view:
                wallet_address = next(iter(self.wallets.values()), "N/A")
                wallet_balance = self.wallet_balance

                wallet_table = Table(show_header=False, box=box.SIMPLE)
                wallet_table.add_column("Wallet Address", style="green")
                wallet_table.add_column("SPR Balance", style="green")
                wallet_table.add_row(wallet_address, wallet_balance)

                console.print(wallet_table)

            table = Table(show_header=True, header_style="bold green", box=box.SIMPLE)
            table.add_column("Worker")
            table.add_column("Status", justify="center")
            table.add_column("Temp", justify="center")
            table.add_column("Algo", justify="center")
            table.add_column("Miner", justify="center")
            table.add_column("Hashrate", justify="center")
            table.add_column("UpTime", justify="center")
            table.add_column("Blocks", justify="center")

            total_hashrate = 0.0
            total_blocks_found = 0

            for index, worker in enumerate(workers):
                total_hashrate += float(worker["Hashrate"])
                if worker["Blocks"].isdigit():
                    total_blocks_found += int(worker["Blocks"])

                style = "on grey15" if index % 2 == 0 else ""
                if worker["Style"]:
                    style = worker["Style"]
                table.add_row(
                    worker["Name"],
                    worker["Status"],
                    str(worker["Temperature"]),
                    worker["Algo"],
                    worker["Miner"],
                    worker["Hashrate"],
                    worker["UpTime"],
                    worker["Blocks"],
                    style=style
                )

            console.print(table)
            network_hashrate = self.get_current_hashrate()
            spr_price = self.get_current_spr_price()
            block_reward = self.get_block_reward()
            estimated_daily_usd = self.calculate_estimated_rewards(network_hashrate, total_hashrate, block_reward, spr_price)

            summary_table = Table(show_header=False, box=box.SIMPLE)
            summary_table.add_column("Metric", style="white")
            summary_table.add_column("Value", style="green")
            summary_table.add_row("Network Hashrate", f"{network_hashrate:.2f} MH/s")
            summary_table.add_row("Estimated Daily Revenue", f"${estimated_daily_usd:.2f}")
            summary_table.add_row("", "")
            summary_table.add_row(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "")

            summary_table_right = Table(show_header=False, box=box.SIMPLE)
            summary_table_right.add_column("Metric", style="white")
            summary_table_right.add_column("Value", style="green")
            summary_table_right.add_row("Your Hashrate", f"{total_hashrate:.2f} KH/s")
            summary_table_right.add_row("Blocks Found So Far", str(total_blocks_found))
            summary_table_right.add_row("", "")
            summary_table_right.add_row("", "hashManager v1.1.1")

            console.print(Columns([summary_table, summary_table_right]))
        else:
            console.print("[bold red]No workers data found.[/bold red]")

    def run(self):
        self.check_tnn_miner()
        self.check_advanced_view()
        self.check_wallet_view()
        try:
            while True:
                self.display_workers()
                for i in range(30):
                    sys.stdout.write(f'\rLoading' + '.' * (i % 4))
                    sys.stdout.flush()
                    time.sleep(1)
                sys.stdout.write('\r' + ' ' * 10 + '\r')
                sys.stdout.flush()
        except KeyboardInterrupt:
            console.print("\nExiting...")

    def check_tnn_miner(self):
        while True:
            enable_tnn = console.input("[cyan]Do you want to enable TNN miner? (y/n): [/cyan]").strip().lower()
            if enable_tnn == 'y':
                console.print("[bold green]Ensure the node is synchronized and the bridge is running.[/bold green]")
                self.tnn_enabled = True
                while True:
                    tnn_ip = console.input("[cyan]Enter the IP address of the host running the node and bridge: [/cyan]").strip()
                    if self.is_valid_ip(tnn_ip):
                        self.tnn_ip = tnn_ip
                        return
                    else:
                        console.print("[bold red]Invalid IP address or node/bridge not reachable. Please enter a valid IP address.[/bold red]")
            elif enable_tnn == 'n':
                self.tnn_enabled = False
                return
            else:
                console.print("[bold red]Invalid input. Please enter 'y' or 'n'.")

    def is_valid_ip(self, ip):
        try:
            response = requests.get(f"http://{ip}:2114/metrics")
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False

    def check_advanced_view(self):
        while True:
            advanced_view = console.input("[cyan]Do you want to enable the advanced view? (y/n): [/cyan]").strip().lower()
            if advanced_view == 'y':
                self.advanced_view = True
                return
            elif advanced_view == 'n':
                self.advanced_view = False
                return
            else:
                console.print("[bold red]Invalid input. Please enter 'y' or 'n'.")

    def check_wallet_view(self):
        while True:
            wallet_view = console.input("[cyan]Do you want to enable wallet view? (y/n): [/cyan]").strip().lower()
            if wallet_view == 'y':
                self.wallet_view = True
                return
            elif wallet_view == 'n':
                self.wallet_view = False
                return
            else:
                console.print("[bold red]Invalid input. Please enter 'y' or 'n'.")

if __name__ == "__main__":
    manager = HashManager()
    manager.run()
