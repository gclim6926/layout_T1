import re
from datetime import datetime


class UDPLogParser:
    """UDP 로그 파일을 파싱하는 클래스 (애니메이션 전용)

    - 로그 포맷 예: [2025-08-19 11:40:34.358]10.10.10.1, 3600, DigitalTwin, 2, OHT, V00001, 1, 0, 0000, 1, 100050, 0, 100051, ...
    - 대괄호 [] 안의 시간 문자열을 추출하고, 쉼표로 분리된 11번째 필드(Current Address)를 정수로 파싱합니다.
    - 파싱 결과는 시간 오름차순으로 정렬됩니다.
    """

    def __init__(self, log_file: str = 'output_udp_data.log') -> None:
        self.log_file = log_file
        self.parsed_data = []

    def parse_log(self) -> bool:
        """로그를 파싱하여 self.parsed_data에 {timestamp, current_address, time_str}를 채웁니다."""
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            for line in lines:
                line = line.strip()
                if not line:
                    continue

                # 시간 정보 추출: [YYYY-MM-DD HH:MM:SS.mmm]
                time_match = re.search(r'\[([^\]]+)\]', line)
                if not time_match:
                    continue

                time_str = time_match.group(1)

                # 쉼표로 구분된 필드들로 분리
                parts = line.split(',')

                # Current Address는 11번째 필드 (인덱스 10)
                if len(parts) >= 11:
                    current_addr_str = parts[10].strip()
                    if current_addr_str.isdigit():
                        current_addr = int(current_addr_str)
                    else:
                        continue
                else:
                    continue

                # 시간을 datetime 객체로 변환
                try:
                    timestamp = datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S.%f')
                except ValueError:
                    try:
                        timestamp = datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')
                    except ValueError:
                        continue

                self.parsed_data.append({
                    'timestamp': timestamp,
                    'current_address': current_addr,
                    'time_str': time_str
                })

            # 시간순 정렬
            self.parsed_data.sort(key=lambda x: x['timestamp'])

            print(f"✅ UDP 로그 파싱 완료: {len(self.parsed_data)} 개 엔트리")
            return True

        except Exception as e:
            print(f"❌ UDP 로그 파싱 중 오류 발생: {str(e)}")
            return False

    def get_address_sequence(self):
        return [entry['current_address'] for entry in self.parsed_data]

    def get_time_sequence(self):
        return [entry['timestamp'] for entry in self.parsed_data]


