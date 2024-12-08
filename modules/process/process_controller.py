from modules.process.process_service import ProcessService
from datetime import datetime
from pathlib import Path


class ProcesssController:
    def __init__(self, config, view=None, app_module=None):
        self.view = view
        self.config = config
        self.service = ProcessService(config)

    def get_all_processes(self):
        pids = self.service.get_all_processes()  # PID 리스트 가져오기
        data = []
        for pid in pids:
            try:
                name = self.service.get_process_name(pid)
                if name == "":
                    name = "-"
                else:
                    name = name.rsplit('\\', 1)[-1]
                data.append({'pid': pid, 'name': name})
            except Exception as e:
                print(f"Can't Access: {e}")
                continue
        return data

    def get_detail_process_info(self, pid):
        # 반환값 초기화
        detail_info = []

        if pid is None:
            print("PID is None.")
            return detail_info

        try:
            pid = int(pid)
            name = self.service.get_process_name(pid)
            if name == "":
                name = "-"
            else:
                name = name.rsplit('\\', 1)[-1]
            username = self.service.get_process_owner(pid)
            cpu_usage = self.service.get_current_cpu_usage(pid)
            formatted_cpu_usage = f"{cpu_usage:.1f} %"
            memory = self.service.get_virtual_mem_usage(pid) / (1024 * 1024)
            formatted_memory = f"{memory:.1f} MB"
            detail_info.append(
                {
                    "name": name,
                    "pid": pid,
                    "username": username,
                    "cpu_usage": formatted_cpu_usage,
                    "memory": formatted_memory,
                }
            )
        except Exception as e:
            print(f"Error: {e}")
            return []

        return detail_info

    def get_all_history_processes(self):
        pids = self.service.get_all_processes()  # PID 리스트 가져오기
        data = []

        for pid in pids:
            try:
                name = self.service.get_process_name(pid)
                name = name.rsplit('\\', 1)[-1] if name else "-"

                try:
                    username = self.service.get_process_owner(pid)
                except Exception as e:
                    print(f"username error : {e}")
                    username = "N/A"

                data.append(
                    {
                        'pid': pid,
                        'name': name,
                        'username': username,
                    }
                )
            except Exception as e:
                print(f"Error processing PID {pid}: {e}")
                continue
        return data

    def get_detail_history_process_info(self, pid):
        if not pid:  # PID가 유효하지 않으면 반환
            print("Invalid PID")
            return
        detail_info = []

        try:
            process_name = self.service.get_process_name(pid)
            if process_name == "":
                process_name = "-"
            else:
                process_name = process_name.rsplit('\\', 1)[-1]

            username = self.service.get_process_owner(pid)
            start_time = "-"
            end_time = "-"

            process_data = []
            current_day = datetime.now().strftime("%Y-%m-%d")
            folder = Path(f"./log/history/{current_day}")
            if not folder.exists():
                print(
                    f"Error: The folder '{folder}' does not exist or is not a directory."
                )
                return
            file_name = process_name.split(".exe")[0] + ".txt"
            file_path = folder / file_name
            if not file_path.exists() or not file_path.is_file():
                print(
                    f"Error: The file '{file_name}' does not exist in the folder '{folder}'."
                )
                return

            with file_path.open("r", encoding="utf-8") as file:
                lines = file.read().strip().split("-----------------------\n")
                for block in lines:
                    if block.strip():  # 빈 블록 제외
                        process = {}
                        for line in block.strip().split("\n"):
                            if ": " in line:
                                key, value = line.split(": ", 1)
                                process[key] = value
                            else:
                                print(
                                    f"Warning: Skipping invalid line: {line}"
                                )
                        process_data.append(process)

            last_log = process_data[-1]
            start_time = last_log.get("Start Time", "N/A")
            end_time = last_log.get("End Time", "N/A")

            detail_info.append(
                {
                    "name": process_name,
                    "pid": pid,
                    "start_time": start_time,
                    "end_time": end_time,
                    "username": username,
                }
            )
        except Exception as e:
            print(f"Error: {e}")
            return []

        return detail_info

    def get_process_name(self, pid):
        return self.service.get_process_name(pid)

    def get_process_modules(self, pid):
        data = self.service.get_process_modules(pid)
        return data

    def show_all_network_packets(self):
        return self.service.show_network_packets()

    def show_network_packets(self):
        data = self.service.show_network_packets()
        detail_info = []
        try:
            for entry in data:
                pid = entry.get('pid')
                if pid is not None:
                    process_name = entry.get('process')
                    if process_name == "":
                        process_name = "-"

                    username = self.service.get_process_owner(pid)
                    detail_info.append(
                        {
                            "name": process_name,
                            "pid": pid,
                            "username": username,
                        }
                    )
        except Exception as e:
            print(f"Error : {e}")
        return detail_info

    def block_porcess_traffic(self, pid):
        self.service.block_process_traffic(pid)
