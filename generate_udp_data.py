#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UDP 데이터를 생성하는 모듈
output.json의 addresses와 lines 정보를 기반으로 경로를 생성하고
UDP 로그 데이터를 output_udp_data.log 파일에 저장합니다.
"""

import json
import random
from datetime import datetime
import math
from config import *

class UDPDataGenerator:
    def __init__(self):
        self.output_data = None
        self.address_graph = {}
        self.address_coords = {}
        
    def load_output_data(self):
        """output.json 파일을 로드합니다."""
        try:
            with open('output.json', 'r', encoding='utf-8') as f:
                self.output_data = json.load(f)
            return True
        except Exception as e:
            print(f"output.json 로드 실패: {e}")
            return False
    
    def build_address_graph(self):
        """주소 간 연결 관계를 그래프로 구성합니다."""
        if not self.output_data or 'lines' not in self.output_data:
            print("lines 데이터가 없습니다.")
            return False
        
        # 주소 좌표 정보 수집
        if 'addresses' in self.output_data:
            for addr in self.output_data['addresses']:
                if 'address' in addr and 'pos' in addr and 'x' in addr['pos'] and 'y' in addr['pos']:
                    self.address_coords[addr['address']] = (addr['pos']['x'], addr['pos']['y'])
        
        # 라인 정보로 그래프 구성
        for line in self.output_data['lines']:
            if 'fromAddress' in line and 'toAddress' in line:
                from_addr = line['fromAddress']
                to_addr = line['toAddress']
                
                if from_addr not in self.address_graph:
                    self.address_graph[from_addr] = []
                if to_addr not in self.address_graph:
                    self.address_graph[to_addr] = []
                    
                self.address_graph[from_addr].append(to_addr)
                self.address_graph[to_addr].append(from_addr)
        
        return True
    
    def calculate_distance(self, addr1, addr2):
        """두 주소 간의 유클리드 거리를 계산합니다."""
        if addr1 not in self.address_coords or addr2 not in self.address_coords:
            return float('inf')
        
        x1, y1 = self.address_coords[addr1]
        x2, y2 = self.address_coords[addr2]
        return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    
    def find_shortest_path(self, start_addr, destination_addr):
        """BFS를 사용하여 최단 경로를 찾습니다."""
        if start_addr == destination_addr:
            return [start_addr]
            
        if start_addr not in self.address_graph or destination_addr not in self.address_graph:
            return None
            
        # BFS로 최단 경로 찾기
        queue = [(start_addr, [start_addr])]
        visited = set()
        
        while queue:
            current, path = queue.pop(0)
            
            if current == destination_addr:
                return path
                
            if current in visited:
                continue
                
            visited.add(current)
            
            # 연결된 주소들을 확인
            for next_addr in self.address_graph[current]:
                if next_addr not in visited:
                    new_path = path + [next_addr]
                    queue.append((next_addr, new_path))
        
        return None
    
    def generate_udp_log_entry(self, timestamp, current_addr, next_addr, destination_addr):
        """UDP 로그 엔트리를 생성합니다."""
        ts_str = datetime.fromtimestamp(timestamp / 1000).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        log_entry = (
            f"[{ts_str}]"
            f"IP:{UDP_IP}, "
            f"Port={UDP_PORT}, "
            f"Descrption:{UDP_DESCRIPTION}, "
            f"Message={UDP_MESSAGE},"
            f"{UDP_MCP},"
            f"{UDP_VEHICLE},"
            f"{UDP_STATE},"
            f"{UDP_PRODUCT},"
            f"{UDP_ERROR_CODE},"
            f"{UDP_COMM_STATE},"
            f"{current_addr},"
            f"{UDP_DISTANCE},"
            f"{next_addr},"
            f"{UDP_RUN_CYCLE},"
            f"{UDP_RUN_CYCLE_INTERVAL},"
            f"{UDP_CARRIER},"
            f"{destination_addr},"
            f"{UDP_EM_STATE},"
            f"{UDP_GROUP_ID},"
            f" ,"
            f"{UDP_RETURN_PRIORITY},"
            f"{UDP_JOB_DETAIL},"
            f"{UDP_MOVE_DISTANCE}"
        )
        return log_entry
    
    def generate_path_data(self, start_address, destination_address):
        """시작 주소에서 목적지 주소까지의 경로 데이터를 생성합니다."""
        if start_address == destination_address:
            return []
        
        # BFS로 최단 경로 찾기
        shortest_path = self.find_shortest_path(start_address, destination_address)
        
        if not shortest_path:
            return []
        
        # 경로 데이터 생성
        path_data = []
        timestamp = int(datetime.now().timestamp() * 1000)
        
        for i in range(len(shortest_path) - 1):
            current_addr = shortest_path[i]
            next_addr = shortest_path[i + 1]
            
            # UDP 로그 엔트리 생성
            log_entry = self.generate_udp_log_entry(timestamp, current_addr, next_addr, destination_address)
            path_data.append(log_entry)
            
            # 시간 증가 (config에서 정의된 범위 사용)
            try:
                increment_min = int(UDP_TIME_INCREMENT_MIN_MS)
                increment_max = int(UDP_TIME_INCREMENT_MAX_MS)
            except Exception:
                increment_min = 500
                increment_max = 1000
            if increment_min > increment_max:
                increment_min, increment_max = increment_max, increment_min
            timestamp += random.randint(increment_min, increment_max)
        
        return path_data
    
    def run(self, start_address=None, destination_address=None):
        """UDP 데이터 생성을 실행합니다."""
        # 기본값 설정
        if start_address is None:
            start_address = UDP_START_ADDRESS
        if destination_address is None:
            destination_address = UDP_DESTINATION_ADDRESS
        
        # output.json 로드
        if not self.load_output_data():
            return False
        
        # 주소 그래프 구성
        if not self.build_address_graph():
            return False
        
        # 경로 데이터 생성
        path_data = self.generate_path_data(start_address, destination_address)
        
        if not path_data:
            return False
        
        # 로그 파일에 저장
        try:
            with open('output_udp_data.log', 'w', encoding='utf-8') as f:
                for entry in path_data:
                    f.write(entry + '\n')
            
            print(f"UDP 데이터 생성 완료: {len(path_data)} 개 엔트리")
            return True
            
        except Exception as e:
            print(f"로그 파일 저장 실패: {e}")
            return False

def generate_udp_data(start_address=None, destination_address=None):
    """UDP 데이터 생성을 위한 래퍼 함수"""
    generator = UDPDataGenerator()
    return generator.run(start_address, destination_address)

if __name__ == "__main__":
    generate_udp_data()
