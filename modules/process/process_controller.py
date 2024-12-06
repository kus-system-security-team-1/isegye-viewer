from modules.process.process_service import ProcessService

# from modules.process.process_view import ProcessWindow


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
            memory = self.service.get_virtual_mem_usage(pid) / 1024

            detail_info.append(
                {
                    "name": name,
                    "pid": pid,
                    "username": username,
                    "cpu_usage": cpu_usage,
                    "memory": memory,
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
