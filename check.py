#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Data Integrity Checker - output.json 파일의 데이터 무결성을 검증하는 모듈
"""

import json
import logging
from datetime import datetime
from collections import defaultdict, Counter
from config import OUTPUT_FILE

class DataChecker:
    def __init__(self):
        self.addresses = []
        self.lines = []
        self.setup_logging()
    
    def setup_logging(self):
        """로깅 설정을 초기화합니다."""
        # 파일 핸들러 설정
        file_handler = logging.FileHandler('check.log', encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        
        # 콘솔 핸들러 설정
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        
        # 로거 설정
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        self.logger.info("=" * 50)
        self.logger.info("데이터 무결성 검사 시작")
        self.logger.info("=" * 50)
        
    def load_output_data(self):
        """output.json 파일을 읽어서 데이터를 로드합니다."""
        try:
            with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.addresses = data.get('addresses', [])
            self.lines = data.get('lines', [])
            
            print(f"✅ {OUTPUT_FILE} 파일을 성공적으로 로드했습니다.")
            print(f"📊 Addresses: {len(self.addresses)}개")
            print(f"📊 Lines: {len(self.lines)}개")
            
            # 상세 로그 정보 추가
            self.logger.info(f"데이터 로드 완료 - Addresses: {len(self.addresses)}개, Lines: {len(self.lines)}개")
            
            # Addresses 상세 정보 로깅
            if self.addresses:
                first_addr = self.addresses[0]
                last_addr = self.addresses[-1]
                self.logger.info(f"Addresses 범위: ID {first_addr.get('id')} ~ {last_addr.get('id')}")
                self.logger.info(f"첫 번째 Address: {first_addr.get('name')} at ({first_addr.get('pos', {}).get('x')}, {first_addr.get('pos', {}).get('y')}, {first_addr.get('pos', {}).get('z')})")
                self.logger.info(f"마지막 Address: {last_addr.get('name')} at ({last_addr.get('pos', {}).get('x')}, {last_addr.get('pos', {}).get('y')}, {last_addr.get('pos', {}).get('z')})")
            
            # Lines 상세 정보 로깅
            if self.lines:
                first_line = self.lines[0]
                last_line = self.lines[-1]
                self.logger.info(f"Lines 범위: ID {first_line.get('id')} ~ {last_line.get('id')}")
                self.logger.info(f"첫 번째 Line: {first_line.get('name')} ({first_line.get('fromAddress')} -> {first_line.get('toAddress')})")
                self.logger.info(f"마지막 Line: {last_line.get('name')} ({last_line.get('fromAddress')} -> {last_line.get('toAddress')})")
            
            return True
            
        except Exception as e:
            error_msg = f"데이터 로드 중 오류 발생: {str(e)}"
            print(f"❌ {error_msg}")
            self.logger.error(error_msg)
            return False
    
    def check_and_report_duplicate_addresses(self):
        """Addresses의 중복을 체크하고 Error로 보고합니다."""
        print("\n🔍 Addresses 중복 검사 중...")
        self.logger.info("Addresses 중복 검사 시작")
        
        has_errors = False
        
        # ID 중복 체크 및 보고
        seen_ids = {}
        duplicate_ids_list = []
        
        for addr in self.addresses:
            addr_id = addr.get('id')
            if addr_id not in seen_ids:
                seen_ids[addr_id] = [addr]
            else:
                seen_ids[addr_id].append(addr)
                duplicate_ids_list.append(addr_id)
        
        if duplicate_ids_list:
            has_errors = True
            print(f"❌ ERROR: 중복된 Address ID 발견: {len(set(duplicate_ids_list))}개")
            self.logger.error(f"중복된 Address ID 발견: {len(set(duplicate_ids_list))}개")
            
            for dup_id in set(duplicate_ids_list):
                addresses_with_id = seen_ids[dup_id]
                print(f"\n🔴 중복된 Address ID {dup_id}:")
                self.logger.error(f"=== 중복된 Address ID {dup_id} ===")
                
                for i, addr in enumerate(addresses_with_id):
                    addr_info = f"  {i+1}. Name: {addr.get('name')}, Pos: ({addr.get('pos', {}).get('x')}, {addr.get('pos', {}).get('y')}, {addr.get('pos', {}).get('z')})"
                    print(addr_info)
                    self.logger.error(addr_info)
        else:
            print("✅ Address ID 중복 없음")
            self.logger.info("Address ID 중복 없음")
        
        # name 중복 체크 및 보고
        seen_names = {}
        duplicate_names_list = []
        
        for addr in self.addresses:
            addr_name = addr.get('name')
            if addr_name not in seen_names:
                seen_names[addr_name] = [addr]
            else:
                seen_names[addr_name].append(addr)
                duplicate_names_list.append(addr_name)
        
        if duplicate_names_list:
            has_errors = True
            print(f"❌ ERROR: 중복된 Address name 발견: {len(set(duplicate_names_list))}개")
            self.logger.error(f"중복된 Address name 발견: {len(set(duplicate_names_list))}개")
            
            for dup_name in set(duplicate_names_list):
                addresses_with_name = seen_names[dup_name]
                print(f"\n🔴 중복된 Address name '{dup_name}':")
                self.logger.error(f"=== 중복된 Address name '{dup_name}' ===")
                
                for i, addr in enumerate(addresses_with_name):
                    addr_info = f"  {i+1}. ID: {addr.get('id')}, Pos: ({addr.get('pos', {}).get('x')}, {addr.get('pos', {}).get('y')}, {addr.get('pos', {}).get('z')})"
                    print(addr_info)
                    self.logger.error(addr_info)
        else:
            print("✅ Address name 중복 없음")
            self.logger.info("Address name 중복 없음")
        
        # position 중복 체크 및 보고
        seen_positions = {}
        duplicate_positions_list = []
        
        for addr in self.addresses:
            pos = addr.get('pos', {})
            pos_str = f"({pos.get('x')}, {pos.get('y')}, {pos.get('z')})"
            
            if pos_str not in seen_positions:
                seen_positions[pos_str] = [addr]
            else:
                seen_positions[pos_str].append(addr)
                duplicate_positions_list.append(pos_str)
        
        if duplicate_positions_list:
            has_errors = True
            print(f"❌ ERROR: 중복된 Address position 발견: {len(set(duplicate_positions_list))}개 위치")
            self.logger.error(f"중복된 Address position 발견: {len(set(duplicate_positions_list))}개 위치")
            
            for pos_str in set(duplicate_positions_list):
                addresses_at_pos = seen_positions[pos_str]
                print(f"\n🔴 위치 {pos_str}에 있는 중복 Addresses ({len(addresses_at_pos)}개):")
                self.logger.error(f"=== 위치 {pos_str}에 있는 중복 Addresses ({len(addresses_at_pos)}개) ===")
                
                for i, addr in enumerate(addresses_at_pos):
                    addr_info = f"  {i+1}. ID: {addr.get('id')}, Name: {addr.get('name')}"
                    print(addr_info)
                    self.logger.error(addr_info)
        else:
            print("✅ Address position 중복 없음")
            self.logger.info("Address position 중복 없음")
        
        if has_errors:
            print("❌ Addresses 중복 오류 발견!")
            self.logger.error("Addresses 중복 오류 발견!")
        else:
            print("✅ Addresses 중복 없음")
            self.logger.info("Addresses 중복 없음")
        
        return not has_errors
    
    def check_and_report_duplicate_lines(self):
        """Lines의 중복을 체크하고 Error로 보고합니다."""
        print("\n🔍 Lines 중복 검사 중...")
        self.logger.info("Lines 중복 검사 시작")
        
        has_errors = False
        
        # ID 중복 체크 및 보고
        seen_ids = {}
        duplicate_line_ids_list = []
        
        for line in self.lines:
            line_id = line.get('id')
            if line_id not in seen_ids:
                seen_ids[line_id] = [line]
            else:
                seen_ids[line_id].append(line)
                duplicate_line_ids_list.append(line_id)
        
        if duplicate_line_ids_list:
            has_errors = True
            print(f"❌ ERROR: 중복된 Line ID 발견: {len(set(duplicate_line_ids_list))}개")
            self.logger.error(f"중복된 Line ID 발견: {len(set(duplicate_line_ids_list))}개")
            
            for dup_id in set(duplicate_line_ids_list):
                lines_with_id = seen_ids[dup_id]
                print(f"\n🔴 중복된 Line ID {dup_id}:")
                self.logger.error(f"=== 중복된 Line ID {dup_id} ===")
                
                for i, line in enumerate(lines_with_id):
                    line_info = f"  {i+1}. Name: {line.get('name')}, From: {line.get('fromAddress')}, To: {line.get('toAddress')}"
                    print(line_info)
                    self.logger.error(line_info)
        else:
            print("✅ Line ID 중복 없음")
            self.logger.info("Line ID 중복 없음")
        
        # name 중복 체크 및 보고
        seen_names = {}
        duplicate_line_names_list = []
        
        for line in self.lines:
            line_name = line.get('name')
            if line_name not in seen_names:
                seen_names[line_name] = [line]
            else:
                seen_names[line_name].append(line)
                duplicate_line_names_list.append(line_name)
        
        if duplicate_line_names_list:
            has_errors = True
            print(f"❌ ERROR: 중복된 Line name 발견: {len(set(duplicate_line_names_list))}개")
            self.logger.error(f"중복된 Line name 발견: {len(set(duplicate_line_names_list))}개")
            
            for dup_name in set(duplicate_line_names_list):
                lines_with_name = seen_names[dup_name]
                print(f"\n🔴 중복된 Line name '{dup_name}':")
                self.logger.error(f"=== 중복된 Line name '{dup_name}' ===")
                
                for i, line in enumerate(lines_with_name):
                    line_info = f"  {i+1}. ID: {line.get('id')}, From: {line.get('fromAddress')}, To: {line.get('toAddress')}"
                    print(line_info)
                    self.logger.error(line_info)
        else:
            print("✅ Line name 중복 없음")
            self.logger.info("Line name 중복 없음")
        
        if has_errors:
            print("❌ Lines 중복 오류 발견!")
            self.logger.error("Lines 중복 오류 발견!")
        else:
            print("✅ Lines 중복 없음")
            self.logger.info("Lines 중복 없음")
        
        return not has_errors
    
    def check_and_report_line_overlaps(self):
        """Lines가 겹치는 경우를 찾고 Error로 보고합니다."""
        print("\n🔍 Lines 겹침 검사 중...")
        self.logger.info("Lines 겹침 검사 시작")
        
        overlaps = []
        
        for i, line1 in enumerate(self.lines):
            for j, line2 in enumerate(self.lines[i+1:], i+1):
                # line1의 연결 정보
                line1_from = line1.get('fromAddress')
                line1_to = line1.get('toAddress')
                
                # line2의 연결 정보
                line2_from = line2.get('fromAddress')
                line2_to = line2.get('toAddress')
                
                # 겹침 조건 확인:
                # 1. 동일한 연결: (from1, to1) == (from2, to2)
                # 2. 역방향 연결: (from1, to1) == (to2, from2)
                is_identical = (line1_from == line2_from and line1_to == line2_to)
                is_reverse = (line1_from == line2_to and line1_to == line2_from)
                
                if is_identical or is_reverse:
                    overlap_type = "동일한 연결" if is_identical else "역방향 연결"
                    overlaps.append({
                        'line1': {
                            'id': line1.get('id'),
                            'name': line1.get('name'),
                            'from': line1_from,
                            'to': line1_to
                        },
                        'line2': {
                            'id': line2.get('id'),
                            'name': line2.get('name'),
                            'from': line2_from,
                            'to': line2_to
                        },
                        'type': overlap_type
                    })
        
        if overlaps:
            print(f"❌ ERROR: 겹치는 Lines 발견: {len(overlaps)}개")
            self.logger.error(f"겹치는 Lines 발견: {len(overlaps)}개")
            
            # 모든 겹침 정보를 로그에 저장
            self.logger.error(f"=== 겹침 상세 정보 ===")
            for i, overlap in enumerate(overlaps):
                overlap_detail = f"겹침 {i+1} ({overlap['type']}): Line1(ID={overlap['line1']['id']}, Name={overlap['line1']['name']}, From={overlap['line1']['from']}, To={overlap['line1']['to']}) vs Line2(ID={overlap['line2']['id']}, Name={overlap['line2']['name']}, From={overlap['line2']['from']}, To={overlap['line2']['to']})"
                self.logger.error(overlap_detail)
            
            # 화면에는 처음 5개만 출력
            for i, overlap in enumerate(overlaps[:5]):
                print(f"   🔴 겹침 {i+1} ({overlap['type']}):")
                print(f"     Line1: ID={overlap['line1']['id']}, Name={overlap['line1']['name']}")
                print(f"            From={overlap['line1']['from']}, To={overlap['line1']['to']}")
                print(f"     Line2: ID={overlap['line2']['id']}, Name={overlap['line2']['name']}")
                print(f"            From={overlap['line2']['from']}, To={overlap['line2']['to']}")
            
            if len(overlaps) > 5:
                print(f"     ... 및 {len(overlaps) - 5}개 더")
                self.logger.error(f"화면 출력 제한으로 인해 {len(overlaps) - 5}개 겹침 정보는 로그 파일에서 확인 가능")
        else:
            print("✅ Lines 겹침 없음")
            self.logger.info("Lines 겹침 없음")
        
        return len(overlaps) == 0
    
    def remove_overlapping_lines(self):
        """겹치는 라인을 삭제합니다."""
        print("\n🗑️ 겹치는 Lines 삭제 중...")
        self.logger.info("겹치는 Lines 삭제 시작")
        
        original_count = len(self.lines)
        lines_to_remove = set()
        
        # 겹치는 라인 찾기
        for i, line1 in enumerate(self.lines):
            if i in lines_to_remove:  # 이미 삭제 대상인 경우 스킵
                continue
                
            for j, line2 in enumerate(self.lines[i+1:], i+1):
                if j in lines_to_remove:  # 이미 삭제 대상인 경우 스킵
                    continue
                    
                # line1의 연결 정보
                line1_from = line1.get('fromAddress')
                line1_to = line1.get('toAddress')
                
                # line2의 연결 정보
                line2_from = line2.get('fromAddress')
                line2_to = line2.get('toAddress')
                
                # 겹침 조건 확인
                is_identical = (line1_from == line2_from and line1_to == line2_to)
                is_reverse = (line1_from == line2_to and line1_to == line2_from)
                
                if is_identical or is_reverse:
                    # 나중에 나온 라인(line2)을 삭제 대상으로 추가
                    lines_to_remove.add(j)
                    
                    overlap_type = "동일한 연결" if is_identical else "역방향 연결"
                    self.logger.info(f"겹침 발견 및 삭제 대상 추가: Line1(ID={line1.get('id')}, Name={line1.get('name')}) vs Line2(ID={line2.get('id')}, Name={line2.get('name')}) - {overlap_type}")
        
        # 삭제할 라인 정보 로깅
        if lines_to_remove:
            self.logger.info(f"=== 삭제 대상 Lines 정보 ===")
            for idx in sorted(lines_to_remove):
                line = self.lines[idx]
                delete_info = f"삭제 대상: ID={line.get('id')}, Name={line.get('name')}, From={line.get('fromAddress')}, To={line.get('toAddress')}"
                self.logger.info(delete_info)
        
        # 겹치는 라인 삭제 (역순으로 삭제하여 인덱스 변화 방지)
        for idx in sorted(lines_to_remove, reverse=True):
            removed_line = self.lines.pop(idx)
            print(f"   🗑️ 삭제된 Line: ID={removed_line.get('id')}, Name={removed_line.get('name')}")
            print(f"      From={removed_line.get('fromAddress')}, To={removed_line.get('toAddress')}")
        
        removed_count = len(lines_to_remove)
        remaining_count = len(self.lines)
        
        print(f"✅ 겹치는 Lines 삭제 완료:")
        print(f"   원본 Lines 수: {original_count}개")
        print(f"   삭제된 Lines 수: {removed_count}개")
        print(f"   남은 Lines 수: {remaining_count}개")
        
        self.logger.info(f"겹치는 Lines 삭제 완료 - 원본: {original_count}개, 삭제: {removed_count}개, 남은: {remaining_count}개")
        
        return removed_count > 0
    
    def find_highly_connected_addresses(self):
        """4개 이상 연결된 address를 찾아서 출력합니다."""
        print("\n🔍 고연결 Addresses 검사 중...")
        self.logger.info("고연결 Addresses 검사 시작")
        
        # 각 address의 연결 횟수 계산
        address_connections = defaultdict(int)
        
        for line in self.lines:
            from_addr = line.get('fromAddress')
            to_addr = line.get('toAddress')
            
            if from_addr:
                address_connections[from_addr] += 1
            if to_addr:
                address_connections[to_addr] += 1
        
        # 4개 이상 연결된 address 찾기
        highly_connected = {addr_id: count for addr_id, count in address_connections.items() if count >= 4}
        
        if highly_connected:
            print(f"📊 4개 이상 연결된 Addresses: {len(highly_connected)}개")
            self.logger.info(f"4개 이상 연결된 Addresses: {len(highly_connected)}개")
            
            # 연결 횟수별로 정렬
            sorted_connected = sorted(highly_connected.items(), key=lambda x: x[1], reverse=True)
            
            # 모든 고연결 주소 정보를 로그에 저장
            self.logger.info(f"=== 고연결 Addresses 상세 정보 ===")
            for addr_id, connection_count in sorted_connected:
                addr_info = next((addr for addr in self.addresses if addr.get('id') == addr_id), None)
                if addr_info:
                    pos = addr_info.get('pos', {})
                    addr_detail = f"고연결 Address: ID={addr_id}, Name={addr_info.get('name')}, Position=({pos.get('x')}, {pos.get('y')}, {pos.get('z')}), 연결수={connection_count}"
                    self.logger.info(addr_detail)
                else:
                    self.logger.warning(f"고연결 Address 정보 없음: ID={addr_id}, 연결수={connection_count}")
            
            # 화면에는 상위 10개만 출력
            for addr_id, connection_count in sorted_connected[:10]:
                addr_info = next((addr for addr in self.addresses if addr.get('id') == addr_id), None)
                if addr_info:
                    pos = addr_info.get('pos', {})
                    print(f"   Address ID={addr_id}, Name={addr_info.get('name')}")
                    print(f"      Position: ({pos.get('x')}, {pos.get('y')}, {pos.get('z')})")
                    print(f"      연결 수: {connection_count}개")
                else:
                    print(f"   Address ID={addr_id} (정보 없음)")
                    print(f"      연결 수: {connection_count}개")
            
            if len(sorted_connected) > 10:
                print(f"   ... 및 {len(sorted_connected) - 10}개 더")
                self.logger.info(f"화면 출력 제한으로 인해 {len(sorted_connected) - 10}개 고연결 주소 정보는 로그 파일에서 확인 가능")
        else:
            print("✅ 4개 이상 연결된 Address 없음")
            self.logger.info("4개 이상 연결된 Address 없음")
        
        return highly_connected
    
    def save_cleaned_data(self):
        """정리된 데이터를 output.json 파일에 저장합니다."""
        output_data = {
            "addresses": self.addresses,
            "lines": self.lines
        }
        
        try:
            with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ 정리된 데이터가 {OUTPUT_FILE} 파일에 저장되었습니다.")
            self.logger.info(f"정리된 데이터가 {OUTPUT_FILE} 파일에 저장됨")
            return True
            
        except Exception as e:
            error_msg = f"파일 저장 중 오류 발생: {str(e)}"
            print(f"❌ {error_msg}")
            self.logger.error(error_msg)
            return False
    
    def save_layout_data(self):
        """최종 데이터를 layout.json 파일에 저장합니다."""
        layout_data = {
            "addresses": self.addresses,
            "lines": self.lines
        }
        
        try:
            with open('layout.json', 'w', encoding='utf-8') as f:
                json.dump(layout_data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ 최종 데이터가 layout.json 파일에 저장되었습니다.")
            self.logger.info(f"최종 데이터가 layout.json 파일에 저장됨 - Addresses: {len(self.addresses)}개, Lines: {len(self.lines)}개")
            return True
            
        except Exception as e:
            error_msg = f"layout.json 파일 저장 중 오류 발생: {str(e)}"
            print(f"❌ {error_msg}")
            self.logger.error(error_msg)
            return False
    
    def run_all_checks(self):
        """모든 검증을 실행합니다."""
        print("🚀 데이터 무결성 검사를 시작합니다...")
        
        if not self.load_output_data():
            return False
        
        # 1. Addresses 중복 검사 및 보고
        address_check = self.check_and_report_duplicate_addresses()
        
        # 2. Lines 중복 검사 및 보고
        line_check = self.check_and_report_duplicate_lines()
        
        # 3. Lines 겹침 검사 및 보고
        overlap_check = self.check_and_report_line_overlaps()
        
        # 4. 겹치는 라인 삭제
        overlap_removed = self.remove_overlapping_lines()
        
        # 5. 고연결 Addresses 검사
        highly_connected = self.find_highly_connected_addresses()
        
        # 6. layout.json 저장
        print("\n📊 최종 데이터 저장 중...")
        layout_save_success = self.save_layout_data()
        
        # 결과 요약
        print("\n📋 검사 결과 요약:")
        print(f"   Addresses 중복 검사: {'✅ 통과' if address_check else '❌ 오류 발견'}")
        print(f"   Lines 중복 검사: {'✅ 통과' if line_check else '❌ 오류 발견'}")
        print(f"   Lines 겹침 검사: {'✅ 통과' if overlap_check else '❌ 오류 발견'}")
        print(f"   겹치는 Lines 삭제: {'✅ 삭제됨' if overlap_removed else '✅ 삭제할 항목 없음'}")
        print(f"   고연결 Addresses: {len(highly_connected)}개 발견")
        print(f"   Layout 저장: {'✅ 성공' if layout_save_success else '❌ 실패'}")
        
        # 상세 요약을 로그에 저장
        self.logger.info("=== 최종 검사 결과 요약 ===")
        self.logger.info(f"Addresses 중복 검사: {'통과' if address_check else '오류 발견'}")
        self.logger.info(f"Lines 중복 검사: {'통과' if line_check else '오류 발견'}")
        self.logger.info(f"Lines 겹침 검사: {'통과' if overlap_check else '오류 발견'}")
        self.logger.info(f"겹치는 Lines 삭제: {'삭제됨' if overlap_removed else '삭제할 항목 없음'}")
        self.logger.info(f"고연결 Addresses 발견: {len(highly_connected)}개")
        self.logger.info(f"Layout 저장: {'성공' if layout_save_success else '실패'}")
        
        overall_success = address_check and line_check and overlap_check and layout_save_success
        
        if overall_success:
            print("\n🎉 모든 검사가 통과되었습니다!")
            self.logger.info("모든 검사 완료 - 성공")
        else:
            print("\n⚠️ 일부 검사에서 오류가 발견되었습니다.")
            self.logger.warning("일부 검사에서 오류 발견")
        
        self.logger.info("=" * 50)
        self.logger.info("데이터 무결성 검사 종료")
        self.logger.info("=" * 50)
        
        return overall_success

def check_data_integrity():
    """데이터 무결성 검사를 실행하는 함수"""
    checker = DataChecker()
    return checker.run_all_checks()

def main():
    """메인 실행 함수"""
    check_data_integrity()

if __name__ == "__main__":
    main() 