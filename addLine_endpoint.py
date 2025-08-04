
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Add Line Endpoint - output.json을 읽어서 endpoint를 찾고 연결하는 모듈
새로운 처리방식:
1. output.json 읽기
2. line의 toAddress 또는 fromAddress에 한번도 사용되지 않은 address는 가장 가까운 다른 두 점과 새롭게 line을 추가한다. 만약, line을 추가할때 겹친다면 추가하지 않는다.
3. 추가한 데이터를 output.json에 업데이트 한다.
4. 다시 output.json을 읽는다.
5. line의 toAddress 또는 fromAddress에서 한 번만 사용된 address에 대해서, 가장 가까운 address와 line을 추가한다. 만약, line을 추가할때 겹친다면 추가하지 않는다.
6. 추가한 데이터를 output.json에 업데이트 한다.
"""

import json
import math
from typing import List, Dict, Tuple, Set
from config import OUTPUT_FILE

class EndpointConnector:
    def __init__(self):
        self.addresses = []
        self.lines = []
        self.address_usage_count = {}  # 각 address의 사용 횟수
        self.unused_addresses = []  # 한 번도 사용되지 않은 addresses
        self.endpoint_addresses = []  # 한 번만 사용된 addresses (endpoints)
        self.new_lines = []  # 새로 생성될 lines
        self.current_line_id = None  # 새로운 line ID 시작점 (로드 후 설정)
        
    def load_output_data(self):
        """output.json 파일을 읽어서 addresses와 lines를 로드합니다."""
        try:
            with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.addresses = data.get('addresses', [])
            self.lines = data.get('lines', [])
            
            # 기존 line들의 최대 ID를 찾아서 다음 ID부터 시작
            max_line_id = 200000  # 기본 시작점
            for line in self.lines:
                line_id = line.get('id', 0)
                if line_id > max_line_id:
                    max_line_id = line_id
            
            self.current_line_id = max_line_id + 1
            
            print(f"✅ {OUTPUT_FILE} 파일을 성공적으로 로드했습니다.")
            print(f"📊 Addresses: {len(self.addresses)}개")
            print(f"📊 Lines: {len(self.lines)}개")
            print(f"📊 새로운 Line ID 시작점: {self.current_line_id}")
            return True
            
        except Exception as e:
            print(f"❌ 데이터 로드 중 오류 발생: {str(e)}")
            return False
    
    def analyze_address_usage(self):
        """각 address의 사용 횟수를 분석합니다."""
        # 사용 횟수 초기화
        for address in self.addresses:
            self.address_usage_count[address.get('id')] = 0
        
        # lines에서 address 사용 횟수 계산
        for line in self.lines:
            from_addr = line.get('fromAddress')
            to_addr = line.get('toAddress')
            
            if from_addr in self.address_usage_count:
                self.address_usage_count[from_addr] += 1
            if to_addr in self.address_usage_count:
                self.address_usage_count[to_addr] += 1
        
        # 사용되지 않은 address와 endpoint address 분류
        self.unused_addresses = []
        self.endpoint_addresses = []
        
        for address in self.addresses:
            addr_id = address.get('id')
            usage_count = self.address_usage_count.get(addr_id, 0)
            
            if usage_count == 0:
                self.unused_addresses.append(address)
            elif usage_count == 1:
                self.endpoint_addresses.append(address)
        
        print(f"📊 사용되지 않은 addresses: {len(self.unused_addresses)}개")
        print(f"📊 Endpoint addresses: {len(self.endpoint_addresses)}개")
    
    def calculate_distance(self, pos1: Dict, pos2: Dict) -> float:
        """두 좌표 간의 거리를 계산합니다."""
        x1, y1, z1 = pos1.get('x', 0), pos1.get('y', 0), pos1.get('z', 0)
        x2, y2, z2 = pos2.get('x', 0), pos2.get('y', 0), pos2.get('z', 0)
        
        return math.sqrt((x2 - x1)**2 + (y2 - y1)**2 + (z2 - z1)**2)
    
    def find_nearest_addresses(self, source_address: Dict, count: int = 2, exclude_addresses: Set[int] = None) -> List[Tuple[Dict, float]]:
        """source_address와 가장 가까운 address들을 찾습니다."""
        if exclude_addresses is None:
            exclude_addresses = set()
        
        source_pos = source_address.get('pos', {})
        source_id = source_address.get('id')
        distances = []
        
        for address in self.addresses:
            # 자기 자신은 제외
            if address.get('id') == source_id:
                continue
            
            # 제외할 address들도 제외
            if address.get('id') in exclude_addresses:
                continue
            
            address_pos = address.get('pos', {})
            distance = self.calculate_distance(source_pos, address_pos)
            distances.append((address, distance))
        
        # 거리순으로 정렬하고 상위 count개 반환
        distances.sort(key=lambda x: x[1])
        return distances[:count]
    
    def is_line_exists(self, from_address_id: int, to_address_id: int) -> bool:
        """두 address 간의 line이 이미 존재하는지 확인합니다."""
        for line in self.lines + self.new_lines:
            line_from = line.get('fromAddress')
            line_to = line.get('toAddress')
            
            # 동일한 연결 또는 역방향 연결 확인
            if (line_from == from_address_id and line_to == to_address_id) or \
               (line_from == to_address_id and line_to == from_address_id):
                return True
        
        return False
    
    def connect_unused_addresses(self):
        """사용되지 않은 address들을 가장 가까운 두 개의 address와 연결합니다."""
        print("📊 사용되지 않은 address 연결 중...")
        
        for i, unused_address in enumerate(self.unused_addresses):
            # 가장 가까운 두 개의 address 찾기
            nearest_addresses = self.find_nearest_addresses(unused_address, 2)
            
            if len(nearest_addresses) >= 2:
                addr1, dist1 = nearest_addresses[0]
                addr2, dist2 = nearest_addresses[1]
                
                # 첫 번째 연결 (겹치지 않는 경우만)
                if not self.is_line_exists(unused_address.get('id'), addr1.get('id')):
                    line1 = {
                        "id": self.current_line_id,
                        "name": f"LINE_{unused_address.get('id')}_{addr1.get('id')}",
                        "fromAddress": unused_address.get('id'),
                        "toAddress": addr1.get('id'),
                        "fromPos": unused_address.get('pos'),
                        "toPos": addr1.get('pos'),
                        "curve": False
                    }
                    self.new_lines.append(line1)
                    self.current_line_id += 1
                
                # 두 번째 연결 (겹치지 않는 경우만)
                if not self.is_line_exists(unused_address.get('id'), addr2.get('id')):
                    line2 = {
                        "id": self.current_line_id,
                        "name": f"LINE_{unused_address.get('id')}_{addr2.get('id')}",
                        "fromAddress": unused_address.get('id'),
                        "toAddress": addr2.get('id'),
                        "fromPos": unused_address.get('pos'),
                        "toPos": addr2.get('pos'),
                        "curve": False
                    }
                    self.new_lines.append(line2)
                    self.current_line_id += 1
                
                # 처음 3개만 상세 정보 출력
                if i < 3:
                    unused_pos = unused_address.get('pos', {})
                    addr1_pos = addr1.get('pos', {})
                    addr2_pos = addr2.get('pos', {})
                    print(f"   Unused Address {i+1}: ID={unused_address.get('id')}")
                    print(f"      위치: ({unused_pos.get('x')}, {unused_pos.get('y')}, {unused_pos.get('z')})")
                    print(f"      연결1: -> ID={addr1.get('id')} (거리: {dist1:.2f})")
                    print(f"      위치: ({addr1_pos.get('x')}, {addr1_pos.get('y')}, {addr1_pos.get('z')})")
                    print(f"      연결2: -> ID={addr2.get('id')} (거리: {dist2:.2f})")
                    print(f"      위치: ({addr2_pos.get('x')}, {addr2_pos.get('y')}, {addr2_pos.get('z')})")
        
        if len(self.unused_addresses) > 3:
            print(f"   ... 및 {len(self.unused_addresses) - 3}개 더 연결됨")
        
        print(f"✅ 사용되지 않은 address 연결 완료: {len(self.unused_addresses)}개")
    
    def find_existing_connections(self, address_id: int) -> Set[int]:
        """address가 기존에 연결된 모든 address들을 찾습니다."""
        connected_addresses = set()
        
        for line in self.lines + self.new_lines:
            line_from = line.get('fromAddress')
            line_to = line.get('toAddress')
            
            if line_from == address_id:
                connected_addresses.add(line_to)
            elif line_to == address_id:
                connected_addresses.add(line_from)
        
        return connected_addresses
    
    def connect_endpoints(self):
        """endpoint들을 기존 line과 겹치지 않는 가장 가까운 address와 연결합니다."""
        print("📊 Endpoint 연결 중...")
        
        for i, endpoint in enumerate(self.endpoint_addresses):
            endpoint_id = endpoint.get('id')
            
            # 기존에 연결된 address들 찾기
            connected_addresses = self.find_existing_connections(endpoint_id)
            
            # 기존 연결을 제외한 가장 가까운 address 찾기
            nearest_addresses = self.find_nearest_addresses(endpoint, 1, connected_addresses)
            
            if nearest_addresses:
                nearest_address, distance = nearest_addresses[0]
                
                # 겹치지 않는 경우만 연결
                if not self.is_line_exists(endpoint_id, nearest_address.get('id')):
                    new_line = {
                        "id": self.current_line_id,
                        "name": f"LINE_{endpoint_id}_{nearest_address.get('id')}",
                        "fromAddress": endpoint_id,
                        "toAddress": nearest_address.get('id'),
                        "fromPos": endpoint.get('pos'),
                        "toPos": nearest_address.get('pos'),
                        "curve": False
                    }
                    
                    self.new_lines.append(new_line)
                    self.current_line_id += 1
                    
                    # 처음 3개만 상세 정보 출력
                    if i < 3:
                        endpoint_pos = endpoint.get('pos', {})
                        nearest_pos = nearest_address.get('pos', {})
                        print(f"   Endpoint {i+1}: ID={endpoint_id}")
                        print(f"      위치: ({endpoint_pos.get('x')}, {endpoint_pos.get('y')}, {endpoint_pos.get('z')})")
                        print(f"      기존 연결 제외: {len(connected_addresses)}개")
                        print(f"      새로운 연결: -> ID={nearest_address.get('id')} (거리: {distance:.2f})")
                        print(f"      위치: ({nearest_pos.get('x')}, {nearest_pos.get('y')}, {nearest_pos.get('z')})")
        
        if len(self.endpoint_addresses) > 3:
            print(f"   ... 및 {len(self.endpoint_addresses) - 3}개 더 연결됨")
        
        print(f"✅ Endpoint 연결 완료: {len(self.endpoint_addresses)}개")
    
    def save_output_json(self):
        """기존 output.json에 새로운 lines를 추가하여 저장합니다."""
        # 기존 lines에 새로운 lines 추가
        all_lines = self.lines + self.new_lines
        
        output_data = {
            "addresses": self.addresses,
            "lines": all_lines
        }
        
        try:
            with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ {OUTPUT_FILE} 파일에 새로운 lines가 추가되어 저장되었습니다.")
            print(f"📊 총 Addresses: {len(self.addresses)}개")
            print(f"📊 총 Lines: {len(all_lines)}개 (기존 {len(self.lines)}개 + 새로운 {len(self.new_lines)}개)")
            return True
            
        except Exception as e:
            print(f"❌ 파일 저장 중 오류 발생: {str(e)}")
            return False
    
    def process_unused_addresses(self):
        """1단계: 사용되지 않은 address 처리"""
        print("\n🔄 1단계: 사용되지 않은 address 처리")
        
        # 1. output.json 읽기
        if not self.load_output_data():
            return False
        
        # 2. address 사용 횟수 분석
        self.analyze_address_usage()
        
        # 3. 사용되지 않은 address들을 가장 가까운 두 개의 address와 연결
        self.connect_unused_addresses()
        
        # 4. 추가한 데이터를 output.json에 업데이트
        if not self.save_output_json():
            return False
        
        return True
    
    def process_endpoint_addresses(self):
        """2단계: endpoint address 처리"""
        print("\n🔄 2단계: endpoint address 처리")
        
        # 1. 다시 output.json을 읽기
        if not self.load_output_data():
            return False
        
        # 2. address 사용 횟수 분석
        self.analyze_address_usage()
        
        # 3. endpoint address들을 가장 가까운 address와 연결
        self.connect_endpoints()
        
        # 4. 추가한 데이터를 output.json에 업데이트
        if not self.save_output_json():
            return False
        
        return True
    
    def run(self):
        """전체 프로세스를 실행합니다."""
        print("🚀 Endpoint 연결 프로세스를 시작합니다...")
        
        # 1단계: 사용되지 않은 address 처리
        if not self.process_unused_addresses():
            return False
        
        # 2단계: endpoint address 처리
        if not self.process_endpoint_addresses():
            return False
        
        print("🎉 모든 작업이 완료되었습니다!")
        return True

def add_endpoint_lines():
    """endpoint 연결을 실행하는 함수"""
    connector = EndpointConnector()
    return connector.run()

def main():
    """메인 실행 함수"""
    add_endpoint_lines()

if __name__ == "__main__":
    main()