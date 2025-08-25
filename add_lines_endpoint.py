
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
import pandas as pd
import numpy as np
import math
from typing import List, Tuple, Set, Dict
from config import OUTPUT_FILE

class EndpointConnector:
    def __init__(self):
        self.addresses_df = None
        self.lines_df = None
        self.current_line_id = None
        
    def load_output_data(self):
        """output.json 파일을 pandas DataFrame으로 읽어서 addresses와 lines를 로드합니다."""
        try:
            with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # addresses를 DataFrame으로 변환
            addresses_data = data.get('addresses', [])
            self.addresses_df = pd.DataFrame(addresses_data)
            
            # lines를 DataFrame으로 변환
            lines_data = data.get('lines', [])
            self.lines_df = pd.DataFrame(lines_data)
            
            # 기존 line들의 최대 ID를 찾아서 다음 ID부터 시작
            max_line_id = 200000  # 기본 시작점
            if not self.lines_df.empty:
                max_line_id = max(max_line_id, self.lines_df['id'].max())
            
            self.current_line_id = max_line_id + 1
            
            print(f"✅ {OUTPUT_FILE} 파일을 성공적으로 로드했습니다.")
            print(f"📊 Addresses: {len(self.addresses_df)}개")
            print(f"📊 Lines: {len(self.lines_df)}개")
            print(f"📊 새로운 Line ID 시작점: {self.current_line_id}")
            return True
            
        except Exception as e:
            print(f"❌ 데이터 로드 중 오류 발생: {str(e)}")
            return False
    
    def find_unused_addresses(self):
        """line의 toAddress와 fromAddress에 한 번도 사용되지 않은 unused address를 찾습니다."""
        print("\n🔍 Unused addresses 찾는 중...")
        
        # 모든 address ID 목록
        all_address_ids = set(self.addresses_df['id'].tolist())
        
        # lines에서 사용되는 address ID들
        used_address_ids = set()
        if not self.lines_df.empty:
            used_address_ids.update(self.lines_df['fromAddress'].tolist())
            used_address_ids.update(self.lines_df['toAddress'].tolist())
        
        # 사용되지 않은 address ID들
        unused_address_ids = all_address_ids - used_address_ids
        
        # unused addresses DataFrame 생성
        unused_addresses_df = self.addresses_df[self.addresses_df['id'].isin(unused_address_ids)]
        
        print(f"📊 Unused addresses: {len(unused_addresses_df)}개")
        return unused_addresses_df
    
    def calculate_distance(self, pos1: Dict, pos2: Dict) -> float:
        """두 좌표 간의 거리를 계산합니다."""
        x1, y1, z1 = pos1.get('x', 0), pos1.get('y', 0), pos1.get('z', 0)
        x2, y2, z2 = pos2.get('x', 0), pos2.get('y', 0), pos2.get('z', 0)
        
        return math.sqrt((x2 - x1)**2 + (y2 - y1)**2 + (z2 - z1)**2)
    
    def find_nearest_addresses(self, source_address: Dict, count: int = 2, exclude_address_ids: Set[int] = None) -> List[Tuple[Dict, float]]:
        """source_address와 가장 가까운 address들을 찾습니다."""
        if exclude_address_ids is None:
            exclude_address_ids = set()
        
        source_pos = source_address.get('pos', {})
        source_id = source_address.get('id')
        distances = []
        
        for _, address_row in self.addresses_df.iterrows():
            address = address_row.to_dict()
            address_id = address.get('id')
            
            # 자기 자신은 제외
            if address_id == source_id:
                continue
            
            # 제외할 address들도 제외
            if address_id in exclude_address_ids:
                continue
            
            address_pos = address.get('pos', {})
            distance = self.calculate_distance(source_pos, address_pos)
            distances.append((address, distance))
        
        # 거리순으로 정렬하고 상위 count개 반환
        distances.sort(key=lambda x: x[1])
        return distances[:count]
    
    def is_line_exists(self, from_address_id: int, to_address_id: int) -> bool:
        """두 address 간의 line이 이미 존재하는지 확인합니다."""
        if self.lines_df.empty:
            return False
        
        # 동일한 연결 또는 역방향 연결 확인
        condition = (
            ((self.lines_df['fromAddress'] == from_address_id) & (self.lines_df['toAddress'] == to_address_id)) |
            ((self.lines_df['fromAddress'] == to_address_id) & (self.lines_df['toAddress'] == from_address_id))
        )
        
        return self.lines_df[condition].shape[0] > 0
    
    def connect_unused_addresses(self):
        """사용되지 않은 address들을 가장 가까운 두 개의 address와 연결합니다."""
        print("\n📊 사용되지 않은 address 연결 중...")
        
        unused_addresses_df = self.find_unused_addresses()
        
        if unused_addresses_df.empty:
            print("✅ 사용되지 않은 address가 없습니다.")
            return 0
        
        new_lines = []
        connected_count = 0
        
        for _, unused_address_row in unused_addresses_df.iterrows():
            unused_address = unused_address_row.to_dict()
            
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
                    new_lines.append(line1)
                    self.current_line_id += 1
                    connected_count += 1
                    print(f"  ✅ {unused_address.get('id')} → {addr1.get('id')} 연결 (거리: {dist1:.2f})")
                else:
                    print(f"  ⚠️ {unused_address.get('id')} → {addr1.get('id')} 연결 스킵 (이미 존재)")
                
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
                    new_lines.append(line2)
                    self.current_line_id += 1
                    connected_count += 1
                    print(f"  ✅ {unused_address.get('id')} → {addr2.get('id')} 연결 (거리: {dist2:.2f})")
                else:
                    print(f"  ⚠️ {unused_address.get('id')} → {addr2.get('id')} 연결 스킵 (이미 존재)")
        
        # 새로운 lines를 DataFrame에 추가
        if new_lines:
            new_lines_df = pd.DataFrame(new_lines)
            self.lines_df = pd.concat([self.lines_df, new_lines_df], ignore_index=True)
            print(f"✅ {len(new_lines)}개의 새로운 lines가 추가되었습니다.")
        
        return connected_count
    
    def find_endpoint_addresses(self):
        """line의 toAddress와 fromAddress에서 한 번만 사용된 address를 찾습니다."""
        print("\n🔍 Endpoint addresses 찾는 중...")
        
        if self.lines_df.empty:
            return pd.DataFrame()
        
        # 각 address의 사용 횟수 계산
        from_address_counts = self.lines_df['fromAddress'].value_counts()
        to_address_counts = self.lines_df['toAddress'].value_counts()
        
        # 모든 address의 총 사용 횟수 계산
        all_address_counts = from_address_counts.add(to_address_counts, fill_value=0)
        
        # 한 번만 사용된 address들 찾기
        endpoint_address_ids = all_address_counts[all_address_counts == 1].index.tolist()
        
        # endpoint addresses DataFrame 생성
        endpoint_addresses_df = self.addresses_df[self.addresses_df['id'].isin(endpoint_address_ids)]
        
        print(f"📊 Endpoint addresses: {len(endpoint_addresses_df)}개")
        return endpoint_addresses_df
    
    def find_nearest_non_overlapping_address(self, source_address: Dict) -> Tuple[Dict, float]:
        """겹치지 않는 가장 가까운 address를 찾습니다."""
        source_pos = source_address.get('pos', {})
        source_id = source_address.get('id')
        
        # 현재 address가 연결된 address들 찾기
        connected_address_ids = set()
        if not self.lines_df.empty:
            # fromAddress로 연결된 것들
            from_connections = self.lines_df[self.lines_df['fromAddress'] == source_id]['toAddress'].tolist()
            connected_address_ids.update(from_connections)
            
            # toAddress로 연결된 것들
            to_connections = self.lines_df[self.lines_df['toAddress'] == source_id]['fromAddress'].tolist()
            connected_address_ids.update(to_connections)
        
        # 자기 자신도 제외
        connected_address_ids.add(source_id)
        
        # 가장 가까운 address 찾기 (연결되지 않은 것들 중에서)
        nearest_address = None
        min_distance = float('inf')
        
        for _, address_row in self.addresses_df.iterrows():
            address = address_row.to_dict()
            address_id = address.get('id')
            
            # 이미 연결된 address는 제외
            if address_id in connected_address_ids:
                continue
            
            address_pos = address.get('pos', {})
            distance = self.calculate_distance(source_pos, address_pos)
            
            if distance < min_distance:
                min_distance = distance
                nearest_address = address
        
        return nearest_address, min_distance if nearest_address else float('inf')
    
    def connect_endpoints(self):
        """Endpoint address들을 가장 가까운 address와 연결합니다."""
        print("\n📊 Endpoint 연결 중...")
        
        endpoint_addresses_df = self.find_endpoint_addresses()
        
        if endpoint_addresses_df.empty:
            print("✅ Endpoint address가 없습니다.")
            return 0
        
        new_lines = []
        connected_count = 0
        
        for _, endpoint_address_row in endpoint_addresses_df.iterrows():
            endpoint_address = endpoint_address_row.to_dict()
            
            # 겹치지 않는 가장 가까운 address 찾기
            nearest_address, distance = self.find_nearest_non_overlapping_address(endpoint_address)
            
            if nearest_address and distance != float('inf'):
                # line이 겹치지 않는지 확인
                if not self.is_line_exists(endpoint_address.get('id'), nearest_address.get('id')):
                    line = {
                        "id": self.current_line_id,
                        "name": f"LINE_{endpoint_address.get('id')}_{nearest_address.get('id')}",
                        "fromAddress": endpoint_address.get('id'),
                        "toAddress": nearest_address.get('id'),
                        "fromPos": endpoint_address.get('pos'),
                        "toPos": nearest_address.get('pos'),
                        "curve": False
                    }
                    new_lines.append(line)
                    self.current_line_id += 1
                    connected_count += 1
                    print(f"  ✅ {endpoint_address.get('id')} → {nearest_address.get('id')} 연결 (거리: {distance:.2f})")
                else:
                    print(f"  ⚠️ {endpoint_address.get('id')} → {nearest_address.get('id')} 연결 스킵 (이미 존재)")
            else:
                print(f"  ❌ {endpoint_address.get('id')}에 연결할 수 있는 address를 찾을 수 없습니다.")
        
        # 새로운 lines를 DataFrame에 추가
        if new_lines:
            new_lines_df = pd.DataFrame(new_lines)
            self.lines_df = pd.concat([self.lines_df, new_lines_df], ignore_index=True)
            print(f"✅ {len(new_lines)}개의 새로운 lines가 추가되었습니다.")
        
        return connected_count
    
    def save_output_json(self):
        """수정된 데이터를 output.json 파일에 저장합니다."""
        try:
            # DataFrame을 JSON 형식으로 변환
            addresses_list = self.addresses_df.to_dict('records')
            lines_list = self.lines_df.to_dict('records')
            
            output_data = {
                'addresses': addresses_list,
                'lines': lines_list
            }
            
            with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ {OUTPUT_FILE} 파일에 데이터가 저장되었습니다.")
            print(f"📊 총 Addresses: {len(addresses_list)}개")
            print(f"📊 총 Lines: {len(lines_list)}개")
            return True
            
        except Exception as e:
            print(f"❌ 파일 저장 중 오류 발생: {str(e)}")
            return False
    
    def run(self):
        """전체 프로세스를 실행합니다."""
        print("🚀 Endpoint 연결 프로세스를 시작합니다...")
        
        # 1. 데이터 로드
        if not self.load_output_data():
            return False
        
        # 2. 사용되지 않은 address 연결
        print("\n🔄 1단계: 사용되지 않은 address 처리")
        unused_connected = self.connect_unused_addresses()
        print(f"✅ 사용되지 않은 address 연결 완료: {unused_connected}개")
        
        # 3. 데이터 저장
        if not self.save_output_json():
            return False
        
        # 4. 데이터 다시 로드 (새로운 lines 포함)
        if not self.load_output_data():
            return False
        
        # 5. Endpoint address 연결
        print("\n🔄 2단계: endpoint address 처리")
        endpoint_connected = self.connect_endpoints()
        print(f"✅ Endpoint 연결 완료: {endpoint_connected}개")
        
        # 6. 최종 데이터 저장
        if not self.save_output_json():
            return False
        
        print("🎉 모든 작업이 완료되었습니다!")
        return True

def add_endpoint_lines():
    """Endpoint 연결 함수"""
    connector = EndpointConnector()
    return connector.run()

def main():
    """메인 함수"""
    add_endpoint_lines()

if __name__ == "__main__":
    main()