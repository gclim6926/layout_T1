#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IntraBay 정보를 읽어서 stations를 생성하는 모듈
"""

import json
import pandas as pd
import math
import random
from typing import List, Dict, Tuple
from config import EQUIPMENTS, STATION_ID_START, STATION_Y_INTERVAL

class IntraBayStationGenerator:
    def __init__(self):
        self.input_file = "input.json"
        self.output_file = "output.json"
        self.format_file = "format.json"
        
        # IntraBay 데이터
        self.z6022_intra_bay = []
        self.z4822_intra_bay = []
        
        # Station 생성 관련
        self.current_station_id = STATION_ID_START
        self.station_boundary = []
        self.selected_boundaries = []
        self.generated_stations = []
        
    def load_intra_bay_data(self) -> bool:
        """input.json에서 IntraBay 정보를 로드합니다."""
        try:
            with open(self.input_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Z6022 IntraBay 데이터 로드
            z6022_data = data.get('z6022', {})
            self.z6022_intra_bay = z6022_data.get('local_loop', [])
            
            # Z4822 IntraBay 데이터 로드
            z4822_data = data.get('z4822', {})
            self.z4822_intra_bay = z4822_data.get('local_loop', [])
            
            print(f"✅ IntraBay 데이터 로드 완료")
            print(f"📊 Z6022 IntraBay: {len(self.z6022_intra_bay)}개")
            print(f"📊 Z4822 IntraBay: {len(self.z4822_intra_bay)}개")
            
            return True
            
        except Exception as e:
            print(f"❌ IntraBay 데이터 로드 중 오류 발생: {str(e)}")
            return False
    
    def create_station_boundaries(self) -> bool:
        """IntraBay 좌표를 기반으로 station_boundary를 생성합니다."""
        print("\n🔍 Station boundary 생성 중...")
        
        # Z6022 IntraBay 처리
        for line in self.z6022_intra_bay:
            if len(line) == 2:
                start_point = line[0]
                end_point = line[1]
                
                # 3차원 좌표로 변환 (Z=6022.0)
                start_3d = [start_point[0], start_point[1], 6022.0]
                end_3d = [end_point[0], end_point[1], 6022.0]
                
                # Y값을 100 간격으로 나누기
                boundaries = self._divide_line_by_interval(start_3d, end_3d, 100)
                self.station_boundary.extend(boundaries)
        
        # Z4822 IntraBay 처리
        for line in self.z4822_intra_bay:
            if len(line) == 2:
                start_point = line[0]
                end_point = line[1]
                
                # 3차원 좌표로 변환 (Z=4822.0)
                start_3d = [start_point[0], start_point[1], 4822.0]
                end_3d = [end_point[0], end_point[1], 4822.0]
                
                # Y값을 100 간격으로 나누기
                boundaries = self._divide_line_by_interval(start_3d, end_3d, 100)
                self.station_boundary.extend(boundaries)
        
        print(f"📊 생성된 station_boundary: {len(self.station_boundary)}개")
        
        # EQUIPMENTS 수와 비교
        if len(self.station_boundary) < EQUIPMENTS:
            print(f"❌ 에러: station_boundary({len(self.station_boundary)}) < EQUIPMENTS({EQUIPMENTS})")
            print("   충분한 station_boundary가 생성되지 않았습니다.")
            return False
        
        return True
    
    def _divide_line_by_interval(self, start_3d: List[float], end_3d: List[float], interval: float) -> List[Tuple[List[float], List[float]]]:
        """선을 주어진 간격으로 나누어 boundary를 생성합니다."""
        boundaries = []
        
        x1, y1, z1 = start_3d
        x2, y2, z2 = end_3d
        
        # Y값을 interval 간격으로 나누기
        y_diff = abs(y2 - y1)
        num_divisions = max(1, int(y_diff / interval))
        
        for i in range(num_divisions):
            # 시작점 계산
            ratio_start = i / num_divisions
            y_start = y1 + ratio_start * (y2 - y1)
            start_boundary = [x1, y_start, z1]
            
            # 끝점 계산
            ratio_end = (i + 1) / num_divisions
            y_end = y1 + ratio_end * (y2 - y1)
            end_boundary = [x2, y_end, z2]
            
            boundaries.append((start_boundary, end_boundary))
        
        return boundaries
    
    def select_random_boundaries(self) -> bool:
        """station_boundary에서 랜덤하게 EQUIPMENTS 수만큼 선택합니다."""
        print(f"\n🎲 {EQUIPMENTS}개의 station_boundary 랜덤 선택 중...")
        
        if len(self.station_boundary) < EQUIPMENTS:
            print(f"❌ 에러: 선택 가능한 boundary가 부족합니다.")
            return False
        
        # 중복 없이 랜덤 선택
        self.selected_boundaries = random.sample(self.station_boundary, EQUIPMENTS)
        print(f"✅ {len(self.selected_boundaries)}개의 boundary 선택 완료")
        
        return True
    
    def generate_stations(self) -> bool:
        """선택된 boundary에 대해 stations를 생성합니다."""
        print(f"\n🏗️ Stations 생성 중...")
        
        for i, (start_boundary, end_boundary) in enumerate(self.selected_boundaries):
            # boundary의 중앙점 계산
            center_x = (start_boundary[0] + end_boundary[0]) / 2
            center_z = (start_boundary[2] + end_boundary[2]) / 2
            
            # Y값 범위 계산
            y_min = min(start_boundary[1], end_boundary[1])
            y_max = max(start_boundary[1], end_boundary[1])
            
            # 3개의 station 생성 (Y값만 20 간격)
            for j in range(3):
                y_pos = y_min + (j + 1) * STATION_Y_INTERVAL
                
                # Y 범위를 벗어나지 않도록 조정
                if y_pos > y_max:
                    y_pos = y_max - (2 - j) * STATION_Y_INTERVAL
                
                # Station 객체 생성
                station = self._create_station_object(center_x, y_pos, center_z)
                self.generated_stations.append(station)
        
        print(f"✅ 총 {len(self.generated_stations)}개의 stations 생성 완료")
        return True
    
    def _create_station_object(self, x: float, y: float, z: float) -> Dict:
        """개별 station 객체를 생성합니다."""
        # ID 생성
        station_id = self.current_station_id
        self.current_station_id += 1
        
        # Name 생성 (ID의 뒤 5자리)
        id_str = str(station_id)
        name_suffix = id_str[-5:] if len(id_str) >= 5 else id_str.zfill(5)
        name = f"Station{name_suffix}"
        
        # Port 계산
        id_last_5 = int(name_suffix)
        device_num = (id_last_5 // 3) + 1
        port_num = (id_last_5 % 3) + 1
        port = f"DEVICE{device_num}_{port_num}"
        
        station = {
            "id": station_id,
            "name": name,
            "type": "1",
            "port": port,
            "pos": {
                "x": round(x, 1),
                "y": round(y, 1),
                "z": round(z, 1)
            }
        }
        
        return station
    
    def update_output_json(self) -> bool:
        """생성된 stations를 output.json에 추가합니다."""
        try:
            # 기존 output.json 읽기
            with open(self.output_file, 'r', encoding='utf-8') as f:
                output_data = json.load(f)
            
            # stations 키가 없으면 생성
            if 'stations' not in output_data:
                output_data['stations'] = []
            
            # 기존 stations에 새로 생성된 stations 추가
            output_data['stations'].extend(self.generated_stations)
            
            # output.json에 저장
            with open(self.output_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ {len(self.generated_stations)}개의 stations를 {self.output_file}에 추가했습니다.")
            print(f"📊 총 stations 수: {len(output_data['stations'])}개")
            
            return True
            
        except Exception as e:
            print(f"❌ output.json 업데이트 중 오류 발생: {str(e)}")
            return False
    
    def run(self) -> bool:
        """전체 프로세스를 실행합니다."""
        print("🚀 IntraBay Station Generator 시작")
        
        # 1단계: IntraBay 데이터 로드
        if not self.load_intra_bay_data():
            return False
        
        # 2단계: Station boundary 생성
        if not self.create_station_boundaries():
            return False
        
        # 3단계: 랜덤 boundary 선택
        if not self.select_random_boundaries():
            return False
        
        # 4단계: Stations 생성
        if not self.generate_stations():
            return False
        
        # 5단계: output.json 업데이트
        if not self.update_output_json():
            return False
        
        print("\n🎉 IntraBay Station Generator 완료!")
        return True

def main():
    """메인 실행 함수"""
    generator = IntraBayStationGenerator()
    success = generator.run()
    
    if success:
        print("✅ 모든 작업이 성공적으로 완료되었습니다.")
    else:
        print("❌ 작업 중 오류가 발생했습니다.")

if __name__ == "__main__":
    main()

def add_intra_bay_stations():
    """IntraBay stations를 생성하는 함수 (app.py에서 호출용)"""
    try:
        generator = IntraBayStationGenerator()
        success = generator.run()
        
        if success:
            print("✅ IntraBay stations 생성 완료")
            return True
        else:
            print("❌ IntraBay stations 생성 실패")
            return False
            
    except Exception as e:
        print(f"❌ IntraBay stations 생성 중 오류 발생: {str(e)}")
        return False
