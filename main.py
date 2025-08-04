#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Layout Graph Visualizer - 메인 실행 파일
"""

from visualize import LayoutVisualizer
from generate import generate_data
from addLine_endpoint import add_endpoint_lines
from check import check_data_integrity

def main():
    """메인 실행 함수"""
    print("🚀 Layout Graph Visualizer 시작")
    
    # 1. 데이터 생성
    print("\n📊 1단계: 데이터 생성")
    if not generate_data():
        print("❌ 데이터 생성 실패로 프로그램을 종료합니다.")
        return
    
    # 2. Endpoint 연결
    print("\n📊 2단계: Endpoint 연결")
    if not add_endpoint_lines():
        print("❌ Endpoint 연결 실패로 프로그램을 종료합니다.")
        return
    
    # 3. 데이터 체크
    print("\n📊 3단계: 데이터 무결성 검사")
    check_data_integrity()
    
    # 4. 시각화
    print("\n📊 4단계: 시각화")
    visualizer = LayoutVisualizer()
    visualizer.create_visualizations()

if __name__ == "__main__":
    main() 