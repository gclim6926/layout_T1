#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate Input - input.json을 읽어서 addresses와 lines를 생성하는 모듈
"""

import json
import random
import math
from typing import List, Dict, Tuple
from config import (
    INPUT_FILE, OUTPUT_FILE, 
    RANDOM_INTERVAL, ADDRESS_ID_START, LINE_ID_START
)

class InputGenerator:
    def __init__(self):
        self.z6022_central_loop = []
        self.z6022_local_loop = []
        self.z6022_local_loop_for_layer = []
        self.z4822_central_loop = []
        self.z4822_local_loop = []
        self.z4822_local_loop_for_layer = []
        
        # z6022 offset 데이터
        self.z6022_offset_cord_edge_top = []
        self.z6022_offset_cord_edge_bottom = []
        self.z6022_offset_edge_top = []
        self.z6022_offset_edge_bottom = []
        
        # z4822 offset 데이터
        self.z4822_offset_cord_edge_top = []
        self.z4822_offset_cord_edge_bottom = []
        self.z4822_offset_edge_top = []
        self.z4822_offset_edge_bottom = []
        
        # shortcut 데이터
        self.z6022_shortcut_local_loop = []
        self.z4822_shortcut_local_loop = []
        self.z6022_shortcut_central_loop = []
        self.z4822_shortcut_central_loop = []
        
        # connect_point 데이터
        self.z6022_connect_point_connection_points = []
        self.z4822_connect_point_connection_points = []
        
        # pair_line_connect 데이터
        self.z6022_pair_line_connect = []
        self.z4822_pair_line_connect = []
        
        # LAYER_CONNECT_POINT 데이터
        self.layer_connect_points_z0_4822 = []
        self.layer_connect_points_z4822_6022 = []
        
        self.addresses = []
        self.lines = []
        self.current_address_id = ADDRESS_ID_START
        self.current_line_id = LINE_ID_START
        
    def load_input_data(self):
        """input.json 파일을 읽어서 z6022, z4822, offset 데이터를 로드합니다."""
        try:
            with open(INPUT_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # z6022 데이터 로드
            z6022_data = data.get('z6022', {})
            self.z6022_central_loop = z6022_data.get('central_loop', [])
            self.z6022_local_loop = z6022_data.get('local_loop', [])
            self.z6022_local_loop_for_layer = z6022_data.get('local_loop_for_layer', [])
            
            # z6022의 offset_cord 데이터 로드
            z6022_offset_cord = z6022_data.get('offset_cord', {})
            self.z6022_offset_cord_edge_top = z6022_offset_cord.get('edge_top', [])
            self.z6022_offset_cord_edge_bottom = z6022_offset_cord.get('edge_bottom', [])
            
            # z6022의 offset 데이터 로드 
            z6022_offset = z6022_data.get('offset', {})
            self.z6022_offset_edge_top = z6022_offset.get('edge_top', [])
            self.z6022_offset_edge_bottom = z6022_offset.get('edge_bottom', [])
            
            # z4822 데이터 로드
            z4822_data = data.get('z4822', {})
            self.z4822_central_loop = z4822_data.get('central_loop', [])
            self.z4822_local_loop = z4822_data.get('local_loop', [])
            self.z4822_local_loop_for_layer = z4822_data.get('local_loop_for_layer', [])
            
            # z4822의 offset_cord 데이터 로드
            z4822_offset_cord = z4822_data.get('offset_cord', {})
            self.z4822_offset_cord_edge_top = z4822_offset_cord.get('edge_top', [])
            self.z4822_offset_cord_edge_bottom = z4822_offset_cord.get('edge_bottom', [])
            
            # z4822의 offset 데이터 로드
            z4822_offset = z4822_data.get('offset', {})
            self.z4822_offset_edge_top = z4822_offset.get('edge_top', [])
            self.z4822_offset_edge_bottom = z4822_offset.get('edge_bottom', [])
            
            # z6022의 shortcut 데이터 로드
            z6022_shortcut = z6022_data.get('shortcut', {})
            self.z6022_shortcut_local_loop = z6022_shortcut.get('shortcut_local_loop', [])
            self.z6022_shortcut_central_loop = z6022_shortcut.get('shortcut_central_loop', [])
            
            # z4822의 shortcut 데이터 로드
            z4822_shortcut = z4822_data.get('shortcut', {})
            self.z4822_shortcut_local_loop = z4822_shortcut.get('shortcut_local_loop', [])
            self.z4822_shortcut_central_loop = z4822_shortcut.get('shortcut_central_loop', [])
            
            # LAYER_CONNECT_POINT 데이터 로드
            layer_connect_point_data = data.get('layer_crossover', {})
            self.layer_connect_points_z0_4822 = layer_connect_point_data.get('z0-4822', [])
            self.layer_connect_points_z4822_6022 = layer_connect_point_data.get('z4822-6022', [])
            
            print(f"✅ {INPUT_FILE} 파일을 성공적으로 로드했습니다.")
            print(f"📊 z6022 central_loop: {len(self.z6022_central_loop)}개")
            print(f"📊 z6022 local_loop: {len(self.z6022_local_loop)}개")
            print(f"📊 z6022 local_loop_for_layer: {len(self.z6022_local_loop_for_layer)}개")
            print(f"📊 z4822 central_loop: {len(self.z4822_central_loop)}개")
            print(f"📊 z4822 local_loop: {len(self.z4822_local_loop)}개")
            print(f"📊 z4822 local_loop_for_layer: {len(self.z4822_local_loop_for_layer)}개")
            print(f"📊 layer_crossover z0-4822: {len(self.layer_connect_points_z0_4822)}개")
            print(f"📊 layer_crossover z4822-6022: {len(self.layer_connect_points_z4822_6022)}개")
            
            # z6022의 layer_connect_point 데이터 로드
            z6022_shortcut = z6022_data.get('shortcut', {})
            self.z6022_connect_point_connection_points = z6022_shortcut.get('shortcut_for_layer', [])
            
            # z4822의 layer_connect_point 데이터 로드
            z4822_shortcut = z4822_data.get('shortcut', {})
            self.z4822_connect_point_connection_points = z4822_shortcut.get('shortcut_for_layer', [])
            
            # z6022의 pair_line_connect 데이터 로드
            z6022_shortcut = z6022_data.get('shortcut', {})
            self.z6022_pair_line_connect = z6022_shortcut.get('shortcut_local_loop', [])
            
            # z4822의 pair_line_connect 데이터 로드
            z4822_shortcut = z4822_data.get('shortcut', {})
            self.z4822_pair_line_connect = z4822_shortcut.get('shortcut_local_loop', [])
            
            print(f"✅ {INPUT_FILE} 파일을 성공적으로 로드했습니다.")
            print(f"📊 z6022 central_loop: {len(self.z6022_central_loop)}개")
            print(f"📊 z6022 local_loop: {len(self.z6022_local_loop)}개")
            print(f"📊 z4822 central_loop: {len(self.z4822_central_loop)}개")
            print(f"📊 z4822 local_loop: {len(self.z4822_local_loop)}개")
            print(f"📊 z6022 offset_cord edge_bottom: {len(self.z6022_offset_cord_edge_bottom)}개")
            print(f"📊 z6022 offset edge_top: {len(self.z6022_offset_edge_top)}개")
            print(f"📊 z6022 offset edge_bottom: {len(self.z6022_offset_edge_bottom)}개")
            print(f"📊 z4822 offset_cord edge_top: {len(self.z4822_offset_cord_edge_top)}개")
            print(f"📊 z4822 offset_cord edge_bottom: {len(self.z4822_offset_cord_edge_bottom)}개")
            print(f"📊 z4822 offset edge_top: {len(self.z4822_offset_edge_top)}개")
            print(f"📊 z4822 offset edge_bottom: {len(self.z4822_offset_edge_bottom)}개")
            print(f"📊 z6022 shortcut_local_loop: {len(self.z6022_shortcut_local_loop)}개")
            print(f"📊 z6022 shortcut_central_loop: {len(self.z6022_shortcut_central_loop)}개")
            print(f"📊 z6022 shortcut_for_layer: {len(self.z6022_connect_point_connection_points)}개")
            print(f"📊 z6022 shortcut_local_loop: {len(self.z6022_pair_line_connect)}개")
            print(f"📊 z4822 shortcut_local_loop: {len(self.z4822_shortcut_local_loop)}개")
            print(f"📊 z4822 shortcut_central_loop: {len(self.z4822_shortcut_central_loop)}개")
            print(f"📊 z4822 shortcut_for_layer: {len(self.z4822_connect_point_connection_points)}개")
            print(f"📊 z4822 shortcut_local_loop: {len(self.z4822_pair_line_connect)}개")
            return True
            
        except Exception as e:
            print(f"❌ 데이터 로드 중 오류 발생: {str(e)}")
            return False
    
    def generate_addresses_on_line(self, start_point: List[float], end_point: List[float], z_value: int) -> List[Dict]:
        """직선 위에 RANDOM_INTERVAL 간격으로 addresses를 생성합니다."""
        addresses = []
        
        x1, y1 = start_point[0], start_point[1]
        x2, y2 = end_point[0], end_point[1]
        
        # 직선의 길이 계산
        length = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        
        # 시작점 추가
        start_address = {
            "id": self.current_address_id,
            "address": self.current_address_id,
            "name": f"ADDR_{self.current_address_id}",
            "pos": {"x": round(x1, 1), "y": round(y1, 1), "z": z_value}
        }
        addresses.append(start_address)
        self.current_address_id += 1
        
        # 간격으로 포인트 생성
        current_pos = 0
        while current_pos < length:
            interval = random.choice(RANDOM_INTERVAL)
            current_pos += interval
            
            if current_pos < length:  # 끝점 제외
                ratio = current_pos / length
                x = x1 + ratio * (x2 - x1)
                y = y1 + ratio * (y2 - y1)
                
                address = {
                    "id": self.current_address_id,
                    "address": self.current_address_id,
                    "name": f"ADDR_{self.current_address_id}",
                    "pos": {"x": round(x, 1), "y": round(y, 1), "z": z_value}
                }
                addresses.append(address)
                self.current_address_id += 1
        
        # 끝점 추가
        end_address = {
            "id": self.current_address_id,
            "address": self.current_address_id,
            "name": f"ADDR_{self.current_address_id}",
            "pos": {"x": round(x2, 1), "y": round(y2, 1), "z": z_value}
        }
        addresses.append(end_address)
        self.current_address_id += 1
        
        return addresses
    
    def generate_addresses_from_offset(self, base_coords: List[List[float]], offsets: List[List[float]], z_value: int) -> List[Dict]:
        """offset_cord 좌표에 offset만큼 움직인 좌표를 생성합니다. (2차원 좌표 전용)"""
        addresses = []
        
        for base_coord in base_coords:
            # 2차원 좌표 처리 (모든 좌표가 2차원으로 변경됨)
            base_x, base_y = base_coord
            
            for offset in offsets:
                # 2차원 offset 처리 (모든 offset이 2차원으로 변경됨)
                if len(offset) == 2:
                    offset_x, offset_y = offset
                else:
                    # 1차원 offset인 경우 y=0으로 처리
                    offset_x = offset[0]
                    offset_y = 0.0
                
                # offset 적용
                final_x = base_x + offset_x
                final_y = base_y + offset_y
                final_z = z_value  # 고정된 z 값 사용
                
                address = {
                    "id": self.current_address_id,
                    "address": self.current_address_id,
                    "name": f"ADDR_{self.current_address_id}",
                    "pos": {"x": round(final_x, 1), "y": round(final_y, 1), "z": final_z}
                }
                addresses.append(address)
                self.current_address_id += 1
        
        return addresses
    
    def generate_lines_from_addresses(self, addresses: List[Dict]) -> List[Dict]:
        """addresses를 순차적으로 연결하는 lines를 생성합니다."""
        lines = []
        
        if len(addresses) < 2:
            return lines
        
        for i in range(len(addresses) - 1):
            current_addr = addresses[i]
            next_addr = addresses[i + 1]
            
            line = {
                "id": self.current_line_id,
                "name": f"LINE_{current_addr['id']}_{next_addr['id']}",
                "fromAddress": current_addr['id'],
                "toAddress": next_addr['id'],
                "fromPos": current_addr['pos'],
                "toPos": next_addr['pos'],
                "curve": False
            }
            lines.append(line)
            self.current_line_id += 1
        
        return lines
    
    def process_z6022_data(self):
        """z6022 데이터 처리"""
        print("📊 z6022 데이터 처리 중...")
        
        # InterBay 처리
        for line in self.z6022_central_loop:
            if len(line) == 2:
                addresses = self.generate_addresses_on_line(line[0], line[1], 6022.0)
                self.addresses.extend(addresses)
                
                if len(addresses) > 1:
                    lines = self.generate_lines_from_addresses(addresses)
                    self.lines.extend(lines)
        
        # IntraBay 처리
        for line in self.z6022_local_loop:
            if len(line) == 2:
                addresses = self.generate_addresses_on_line(line[0], line[1], 6022.0)
                self.addresses.extend(addresses)
                
                if len(addresses) > 1:
                    lines = self.generate_lines_from_addresses(addresses)
                    self.lines.extend(lines)
        
        # local_loop_for_layer 처리
        if hasattr(self, 'z6022_local_loop_for_layer') and self.z6022_local_loop_for_layer:
            print(f"   📍 z6022 local_loop_for_layer: {len(self.z6022_local_loop_for_layer)}개")
            for line in self.z6022_local_loop_for_layer:
                if len(line) == 2:
                    addresses = self.generate_addresses_on_line(line[0], line[1], 6022.0)
                    self.addresses.extend(addresses)
                    
                    if len(addresses) > 1:
                        lines = self.generate_lines_from_addresses(addresses)
                        self.lines.extend(lines)
            print(f"         local_loop_for_layer 생성된 addresses: {len(self.z6022_local_loop_for_layer)}개")
    
    def process_z4822_data(self):
        """z4822 데이터 처리"""
        print("📊 z4822 데이터 처리 중...")
        
        # InterBay 처리
        for line in self.z4822_central_loop:
            if len(line) == 2:
                addresses = self.generate_addresses_on_line(line[0], line[1], 4822.0)
                self.addresses.extend(addresses)
                
                if len(addresses) > 1:
                    lines = self.generate_lines_from_addresses(addresses)
                    self.lines.extend(lines)
        
        # IntraBay 처리
        for line in self.z4822_local_loop:
            if len(line) == 2:
                addresses = self.generate_addresses_on_line(line[0], line[1], 4822.0)
                self.addresses.extend(addresses)
                
                if len(addresses) > 1:
                    lines = self.generate_lines_from_addresses(addresses)
                    self.lines.extend(lines)
        
        # local_loop_for_layer 처리
        if hasattr(self, 'z4822_local_loop_for_layer') and self.z4822_local_loop_for_layer:
            print(f"   📍 z4822 local_loop_for_layer: {len(self.z4822_local_loop_for_layer)}개")
            for line in self.z4822_local_loop_for_layer:
                if len(line) == 2:
                    addresses = self.generate_addresses_on_line(line[0], line[1], 4822.0)
                    self.addresses.extend(addresses)
                    
                    if len(addresses) > 1:
                        lines = self.generate_lines_from_addresses(addresses)
                        self.lines.extend(lines)
            print(f"         local_loop_for_layer 생성된 addresses: {len(self.z4822_local_loop_for_layer)}개")
    
    def process_offset_data(self):
        """offset 데이터 처리 - z6022와 z4822의 각 offset_cord를 시작점으로 하여 offset을 적용한 addresses와 lines 생성"""
        print("📊 offset 데이터 처리 중...")
        
        # z6022 offset 데이터 처리
        print("   📍 z6022 offset 데이터 처리:")
        
        # z6022 edge_top 처리
        if self.z6022_offset_cord_edge_top and self.z6022_offset_edge_top:
            print(f"      📍 edge_top: {len(self.z6022_offset_cord_edge_top)}개 시작점, {len(self.z6022_offset_edge_top)}개 offset")
            
            for i, base_coord in enumerate(self.z6022_offset_cord_edge_top):
                # 2차원 좌표 처리 (모든 좌표가 2차원으로 변경됨)
                base_x, base_y = base_coord
                print(f"         시작점 {i+1}: [{base_x}, {base_y}]")
                
                # 이 시작점에 모든 offset을 적용하여 addresses 생성
                addresses_for_this_base = []
                
                for j, offset in enumerate(self.z6022_offset_edge_top):
                    # 2차원 offset 처리 (모든 offset이 2차원으로 변경됨)
                    if len(offset) == 2:
                        offset_x, offset_y = offset
                    else:
                        # 1차원 offset인 경우 y=0으로 처리
                        offset_x = offset[0]
                        offset_y = 0.0
                    
                    # offset 적용
                    final_x = base_x + offset_x
                    final_y = base_y + offset_y
                    final_z = 6022.0  # z6022 레벨 고정
                    
                    address = {
                        "id": self.current_address_id,
                        "address": self.current_address_id,
                        "name": f"ADDR_{self.current_address_id}",
                        "pos": {"x": round(final_x, 1), "y": round(final_y, 1), "z": final_z}
                    }
                    addresses_for_this_base.append(address)
                    self.current_address_id += 1
                
                # 이 시작점에서 생성된 addresses를 전체 addresses에 추가
                self.addresses.extend(addresses_for_this_base)
                
                # 이 시작점의 addresses를 순차적으로 연결하는 lines 생성
                if len(addresses_for_this_base) > 1:
                    lines_for_this_base = self.generate_lines_from_addresses(addresses_for_this_base)
                    self.lines.extend(lines_for_this_base)
                    print(f"            생성된 addresses: {len(addresses_for_this_base)}개, lines: {len(lines_for_this_base)}개")
        
        # z6022 edge_bottom 처리
        if self.z6022_offset_cord_edge_bottom and self.z6022_offset_edge_bottom:
            print(f"      📍 edge_bottom: {len(self.z6022_offset_cord_edge_bottom)}개 시작점, {len(self.z6022_offset_edge_bottom)}개 offset")
            
            for i, base_coord in enumerate(self.z6022_offset_cord_edge_bottom):
                # 2차원 좌표 처리 (모든 좌표가 2차원으로 변경됨)
                base_x, base_y = base_coord
                print(f"         시작점 {i+1}: [{base_x}, {base_y}]")
                
                # 이 시작점에 모든 offset을 적용하여 addresses 생성
                addresses_for_this_base = []
                
                for j, offset in enumerate(self.z6022_offset_edge_bottom):
                    # 2차원 offset 처리 (모든 offset이 2차원으로 변경됨)
                    if len(offset) == 2:
                        offset_x, offset_y = offset
                    else:
                        # 1차원 offset인 경우 y=0으로 처리
                        offset_x = offset[0]
                        offset_y = 0.0
                    
                    # offset 적용
                    final_x = base_x + offset_x
                    final_y = base_y + offset_y
                    final_z = 6022.0  # z6022 레벨 고정
                    
                    address = {
                        "id": self.current_address_id,
                        "address": self.current_address_id,
                        "name": f"ADDR_{self.current_address_id}",
                        "pos": {"x": round(final_x, 1), "y": round(final_y, 1), "z": final_z}
                    }
                    addresses_for_this_base.append(address)
                    self.current_address_id += 1
                
                # 이 시작점에서 생성된 addresses를 전체 addresses에 추가
                self.addresses.extend(addresses_for_this_base)
                
                # 이 시작점의 addresses를 순차적으로 연결하는 lines 생성
                if len(addresses_for_this_base) > 1:
                    lines_for_this_base = self.generate_lines_from_addresses(addresses_for_this_base)
                    self.lines.extend(lines_for_this_base)
                    print(f"            생성된 addresses: {len(addresses_for_this_base)}개, lines: {len(lines_for_this_base)}개")
        
        # z4822 offset 데이터 처리
        print("   📍 z4822 offset 데이터 처리:")
        
        # z4822 edge_top 처리
        if self.z4822_offset_cord_edge_top and self.z4822_offset_edge_top:
            print(f"      📍 edge_top: {len(self.z4822_offset_cord_edge_top)}개 시작점, {len(self.z4822_offset_edge_top)}개 offset")
            
            for i, base_coord in enumerate(self.z4822_offset_cord_edge_top):
                # 2차원 좌표 처리 (모든 좌표가 2차원으로 변경됨)
                base_x, base_y = base_coord
                print(f"         시작점 {i+1}: [{base_x}, {base_y}]")
                
                # 이 시작점에 모든 offset을 적용하여 addresses 생성
                addresses_for_this_base = []
                
                for j, offset in enumerate(self.z4822_offset_edge_top):
                    # 2차원 offset 처리 (모든 offset이 2차원으로 변경됨)
                    if len(offset) == 2:
                        offset_x, offset_y = offset
                    else:
                        # 1차원 offset인 경우 y=0으로 처리
                        offset_x = offset[0]
                        offset_y = 0.0
                    
                    # offset 적용
                    final_x = base_x + offset_x
                    final_y = base_y + offset_y
                    final_z = 4822.0  # z4822 레벨 고정
                    
                    address = {
                        "id": self.current_address_id,
                        "address": self.current_address_id,
                        "name": f"ADDR_{self.current_address_id}",
                        "pos": {"x": round(final_x, 1), "y": round(final_y, 1), "z": final_z}
                    }
                    addresses_for_this_base.append(address)
                    self.current_address_id += 1
                
                # 이 시작점에서 생성된 addresses를 전체 addresses에 추가
                self.addresses.extend(addresses_for_this_base)
                
                # 이 시작점의 addresses를 순차적으로 연결하는 lines 생성
                if len(addresses_for_this_base) > 1:
                    lines_for_this_base = self.generate_lines_from_addresses(addresses_for_this_base)
                    self.lines.extend(lines_for_this_base)
                    print(f"            생성된 addresses: {len(addresses_for_this_base)}개, lines: {len(lines_for_this_base)}개")
        
        # z4822 edge_bottom 처리
        if self.z4822_offset_cord_edge_bottom and self.z4822_offset_edge_bottom:
            print(f"      📍 edge_bottom: {len(self.z4822_offset_cord_edge_bottom)}개 시작점, {len(self.z4822_offset_edge_bottom)}개 offset")
            
            for i, base_coord in enumerate(self.z4822_offset_cord_edge_bottom):
                # 2차원 좌표 처리 (모든 좌표가 2차원으로 변경됨)
                base_x, base_y = base_coord
                print(f"         시작점 {i+1}: [{base_x}, {base_y}]")
                
                # 이 시작점에 모든 offset을 적용하여 addresses 생성
                addresses_for_this_base = []
                
                for j, offset in enumerate(self.z4822_offset_edge_bottom):
                    # 2차원 offset 처리 (모든 offset이 2차원으로 변경됨)
                    if len(offset) == 2:
                        offset_x, offset_y = offset
                    else:
                        # 1차원 offset인 경우 y=0으로 처리
                        offset_x = offset[0]
                        offset_y = 0.0
                    
                    # offset 적용
                    final_x = base_x + offset_x
                    final_y = base_y + offset_y
                    final_z = 4822.0  # z4822 레벨 고정
                    
                    address = {
                        "id": self.current_address_id,
                        "address": self.current_address_id,
                        "name": f"ADDR_{self.current_address_id}",
                        "pos": {"x": round(final_x, 1), "y": round(final_y, 1), "z": final_z}
                    }
                    addresses_for_this_base.append(address)
                    self.current_address_id += 1
                
                # 이 시작점에서 생성된 addresses를 전체 addresses에 추가
                self.addresses.extend(addresses_for_this_base)
                
                # 이 시작점의 addresses를 순차적으로 연결하는 lines 생성
                if len(addresses_for_this_base) > 1:
                    lines_for_this_base = self.generate_lines_from_addresses(addresses_for_this_base)
                    self.lines.extend(lines_for_this_base)
                    print(f"            생성된 addresses: {len(addresses_for_this_base)}개, lines: {len(lines_for_this_base)}개")
    
    def process_shortcut_data(self):
        """shortcut 데이터 처리 - 모든 좌표를 addresses에 추가"""
        print("📊 shortcut 데이터 처리 중...")
        
        # z6022 shortcut_local_loop 처리
        if self.z6022_shortcut_local_loop:
            print(f"   📍 z6022 shortcut_local_loop: {len(self.z6022_shortcut_local_loop)}개")
            
            for i, point in enumerate(self.z6022_shortcut_local_loop):
                # 2D/3D 좌표 처리
                if len(point) == 2:  # 2D 좌표
                    x, y = point
                    z = 6022.0
                else:  # 3D 좌표
                    x, y, z = point[0], point[1], point[2]
                
                print(f"      포인트 {i+1}: [{x}, {y}, {z}]")
                
                address = {
                    "id": self.current_address_id,
                    "address": self.current_address_id,
                    "name": f"ADDR_{self.current_address_id}",
                    "pos": {"x": round(x, 1), "y": round(y, 1), "z": z}
                }
                self.addresses.append(address)
                self.current_address_id += 1
            
            print(f"         생성된 addresses: {len(self.z6022_shortcut_local_loop)}개")
        
        # z6022 shortcut_central_loop 처리
        if self.z6022_shortcut_central_loop:
            print(f"   📍 z6022 shortcut_central_loop: {len(self.z6022_shortcut_central_loop)}개")
            
            for i, point in enumerate(self.z6022_shortcut_central_loop):
                # 2D/3D 좌표 처리
                if len(point) == 2:  # 2D 좌표
                    x, y = point
                    z = 6022.0
                else:  # 3D 좌표
                    x, y, z = point[0], point[1], point[2]
                
                print(f"      포인트 {i+1}: [{x}, {y}, {z}]")
                
                address = {
                    "id": self.current_address_id,
                    "address": self.current_address_id,
                    "name": f"ADDR_{self.current_address_id}",
                    "pos": {"x": round(x, 1), "y": round(y, 1), "z": z}
                }
                self.addresses.append(address)
                self.current_address_id += 1
            
            print(f"         생성된 addresses: {len(self.z6022_shortcut_central_loop)}개")
        
        # z4822 shortcut_local_loop 처리
        if self.z4822_shortcut_local_loop:
            print(f"   📍 z4822 shortcut_local_loop: {len(self.z4822_shortcut_local_loop)}개")
            
            for i, point in enumerate(self.z4822_shortcut_local_loop):
                # 2D/3D 좌표 처리
                if len(point) == 2:  # 2D 좌표
                    x, y = point
                    z = 4822.0
                else:  # 3D 좌표
                    x, y, z = point[0], point[1], point[2]
                
                print(f"      포인트 {i+1}: [{x}, {y}, {z}]")
                
                address = {
                    "id": self.current_address_id,
                    "address": self.current_address_id,
                    "name": f"ADDR_{self.current_address_id}",
                    "pos": {"x": round(x, 1), "y": round(y, 1), "z": z}
                }
                self.addresses.append(address)
                self.current_address_id += 1
            
            print(f"         생성된 addresses: {len(self.z4822_shortcut_local_loop)}개")
        
        # z4822 shortcut_central_loop 처리
        if self.z4822_shortcut_central_loop:
            print(f"   📍 z4822 shortcut_central_loop: {len(self.z4822_shortcut_central_loop)}개")
            
            for i, point in enumerate(self.z4822_shortcut_central_loop):
                # 2D/3D 좌표 처리
                if len(point) == 2:  # 2D 좌표
                    x, y = point
                    z = 4822.0
                else:  # 3D 좌표
                    x, y, z = point[0], point[1], point[2]
                
                print(f"      포인트 {i+1}: [{x}, {y}, {z}]")
                
                address = {
                    "id": self.current_address_id,
                    "address": self.current_address_id,
                    "name": f"ADDR_{self.current_address_id}",
                    "pos": {"x": round(x, 1), "y": round(y, 1), "z": z}
                }
                self.addresses.append(address)
                self.current_address_id += 1
            
            print(f"         생성된 addresses: {len(self.z4822_shortcut_central_loop)}개")
    
    def process_shortcut_for_layer_data(self):
        """shortcut_for_layer 데이터 처리 - 모든 좌표를 addresses에 추가"""
        print("📊 shortcut_for_layer 데이터 처리 중...")
        
        # z6022 shortcut_for_layer 처리
        if self.z6022_connect_point_connection_points:
            print(f"   📍 z6022 shortcut_for_layer: {len(self.z6022_connect_point_connection_points)}개")
            
            for i, point in enumerate(self.z6022_connect_point_connection_points):
                # 2차원 좌표 처리
                if len(point) == 2:
                    x, y = point
                    z = 6022.0
                else:
                    x, y, z = point[0], point[1], point[2]
                
                address = {
                    "id": self.current_address_id,
                    "address": self.current_address_id,
                    "name": f"ADDR_{self.current_address_id}",
                    "pos": {"x": round(x, 1), "y": round(y, 1), "z": z}
                }
                self.addresses.append(address)
                self.current_address_id += 1
            
            print(f"         생성된 addresses: {len(self.z6022_connect_point_connection_points)}개")
        
        # z4822 shortcut_for_layer 처리
        if self.z4822_connect_point_connection_points:
            print(f"   📍 z4822 shortcut_for_layer: {len(self.z4822_connect_point_connection_points)}개")
            
            for i, point in enumerate(self.z4822_connect_point_connection_points):
                # 2차원 좌표 처리
                if len(point) == 2:
                    x, y = point
                    z = 4822.0
                else:
                    x, y, z = point[0], point[1], point[2]
                
                address = {
                    "id": self.current_address_id,
                    "address": self.current_address_id,
                    "name": f"ADDR_{self.current_address_id}",
                    "pos": {"x": round(x, 1), "y": round(y, 1), "z": z}
                }
                self.addresses.append(address)
                self.current_address_id += 1
            
            print(f"         생성된 addresses: {len(self.z4822_connect_point_connection_points)}개")
    
    
    
    def process_layer_crossover_data(self):
        """layer_crossover 데이터를 처리하여 addresses와 lines를 생성합니다."""
        print("\n🔗 layer_crossover 데이터 처리 중...")
        
        if self.layer_connect_points_z0_4822:
            print(f"   📍 z0-4822 연결점: {len(self.layer_connect_points_z0_4822)}개")
            
            for i, connection in enumerate(self.layer_connect_points_z0_4822):
                # 3차원 좌표 처리
                if len(connection) == 2 and len(connection[0]) == 3 and len(connection[1]) == 3:
                    start_point = connection[0]
                    end_point = connection[1]
                    
                    # 시작점 주소 생성
                    start_address = {
                        "id": self.current_address_id,
                        "address": self.current_address_id,
                        "name": f"ADDR_{self.current_address_id}",
                        "pos": {"x": round(start_point[0], 1), "y": round(start_point[1], 1), "z": start_point[2]}
                    }
                    self.addresses.append(start_address)
                    start_id = self.current_address_id
                    self.current_address_id += 1
                    
                    # 끝점 주소 생성
                    end_address = {
                        "id": self.current_address_id,
                        "address": self.current_address_id,
                        "name": f"ADDR_{self.current_address_id}",
                        "pos": {"x": round(end_point[0], 1), "y": round(end_point[1], 1), "z": end_point[2]}
                    }
                    self.addresses.append(end_address)
                    end_id = self.current_address_id
                    self.current_address_id += 1
                    
                    # 연결선 생성
                    line = {
                        "id": self.current_line_id,
                        "name": f"LINE_{self.current_line_id}",
                        "fromAddress": start_id,
                        "toAddress": end_id,
                        "fromPos": {"x": round(start_point[0], 1), "y": round(start_point[1], 1), "z": start_point[2]},
                        "toPos": {"x": round(end_point[0], 1), "y": round(end_point[1], 1), "z": end_point[2]}
                    }
                    self.lines.append(line)
                    self.current_line_id += 1
                    
                    if (i + 1) % 10 == 0:
                        print(f"      {i + 1}/{len(self.layer_connect_points_z0_4822)} 처리 완료")
            
            print(f"         z0-4822 생성된 주소: {len(self.layer_connect_points_z0_4822) * 2}개")
            print(f"         z0-4822 생성된 연결선: {len(self.layer_connect_points_z0_4822)}개")
        
        if self.layer_connect_points_z4822_6022:
            print(f"   📍 z4822-6022 연결점: {len(self.layer_connect_points_z4822_6022)}개")
            
            for i, connection in enumerate(self.layer_connect_points_z4822_6022):
                # 3차원 좌표 처리
                if len(connection) == 2 and len(connection[0]) == 3 and len(connection[1]) == 3:
                    start_point = connection[0]
                    end_point = connection[1]
                    
                    # 시작점 주소 생성
                    start_address = {
                        "id": self.current_address_id,
                        "address": self.current_address_id,
                        "name": f"ADDR_{self.current_address_id}",
                        "pos": {"x": round(start_point[0], 1), "y": round(start_point[1], 1), "z": start_point[2]}
                    }
                    self.addresses.append(start_address)
                    start_id = self.current_address_id
                    self.current_address_id += 1
                    
                    # 끝점 주소 생성
                    end_address = {
                        "id": self.current_address_id,
                        "address": self.current_address_id,
                        "name": f"ADDR_{self.current_address_id}",
                        "pos": {"x": round(end_point[0], 1), "y": round(end_point[1], 1), "z": end_point[2]}
                    }
                    self.addresses.append(end_address)
                    end_id = self.current_address_id
                    self.current_address_id += 1
                    
                    # 연결선 생성
                    line = {
                        "id": self.current_line_id,
                        "name": f"LINE_{self.current_line_id}",
                        "fromAddress": start_id,
                        "toAddress": end_id,
                        "fromPos": {"x": round(start_point[0], 1), "y": round(start_point[1], 1), "z": start_point[2]},
                        "toPos": {"x": round(end_point[0], 1), "y": round(end_point[1], 1), "z": end_point[2]}
                    }
                    self.lines.append(line)
                    self.current_line_id += 1
                    
                    if (i + 1) % 10 == 0:
                        print(f"      {i + 1}/{len(self.layer_connect_points_z4822_6022)} 처리 완료")
            
            print(f"         z4822-6022 생성된 주소: {len(self.layer_connect_points_z4822_6022) * 2}개")
            print(f"         z4822-6022 생성된 연결선: {len(self.layer_connect_points_z4822_6022)}개")
        
        total_connections = len(self.layer_connect_points_z0_4822) + len(self.layer_connect_points_z4822_6022)
        if total_connections > 0:
            print(f"✅ layer_crossover 데이터 처리 완료:")
            print(f"   총 연결점: {total_connections}개")
            print(f"   총 생성된 주소: {total_connections * 2}개")
            print(f"   총 생성된 연결선: {total_connections}개")
        else:
            print("⚠️ layer_crossover 데이터가 없습니다.")
    
    def generate_data(self):
        """데이터를 생성합니다."""
        print("🚀 데이터 생성을 시작합니다...")
        
        # layer_crossover 데이터 처리 (가장 먼저 실행)
        self.process_layer_crossover_data()
        
        # z6022 데이터 처리
        self.process_z6022_data()
        
        # z4822 데이터 처리
        self.process_z4822_data()
        
        # shortcut_for_layer 데이터 처리
        self.process_shortcut_for_layer_data()
        
        # 모든 shortcut 데이터 처리 (local_loop + central_loop)
        self.process_shortcut_data()
        
        print(f"✅ 데이터 생성 완료:")
        print(f"   📍 Addresses: {len(self.addresses)}개")
        print(f"   📏 Lines: {len(self.lines)}개")
    
    def save_output(self):
        """생성된 데이터를 output.json 파일로 저장합니다."""
        output_data = {"addresses": self.addresses, "lines": self.lines}
        
        try:
            with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ {OUTPUT_FILE} 파일로 저장되었습니다.")
            return True
            
        except Exception as e:
            print(f"❌ 파일 저장 중 오류 발생: {str(e)}")
            return False
    
    def run(self):
        """전체 프로세스를 실행합니다."""
        if not self.load_input_data():
            return False
        
        self.generate_data()
        
        if not self.save_output():
            return False
        
        print("🎉 모든 작업이 완료되었습니다!")
        return True

def generate_data():
    """데이터 생성을 실행하는 함수"""
    generator = InputGenerator()
    return generator.run()

def main():
    """메인 실행 함수"""
    generate_data()

if __name__ == "__main__":
    main()
