# Layout Graph Visualizer

레이아웃 그래프 시각화 시스템 - 복잡한 레이아웃 데이터를 처리하고 시각화하는 Python 기반 도구입니다.

## 📋 목차

- [프로젝트 개요](#-프로젝트-개요)
- [주요 기능](#-주요-기능)
- [시스템 구조](#-시스템-구조)
- [설치 및 실행](#-설치-및-실행)
- [사용법](#-사용법)
- [파일 구조](#-파일-구조)
- [기술 스택](#-기술-스택)
- [데이터 형식](#-데이터-형식)
- [출력 결과](#-출력-결과)
- [기여하기](#-기여하기)
- [라이선스](#-라이선스)

## 🎯 프로젝트 개요

Layout Graph Visualizer는 복잡한 레이아웃 데이터를 처리하고 시각화하는 종합적인 시스템입니다. 4단계 처리 파이프라인을 통해 데이터 생성부터 시각화까지 모든 과정을 자동화합니다.

### 핵심 특징
- **4단계 자동화 파이프라인**: 데이터 생성 → 연결 → 검증 → 시각화
- **다층 레이아웃 지원**: Z6022, Z4822 레이어 분리 처리
- **데이터 무결성 검증**: 중복 제거, 겹침 검사, 고연결 분석
- **인터랙티브 시각화**: Plotly 기반 동적 그래프 생성
- **상세한 로깅**: 모든 처리 과정의 상세한 기록

## 🚀 주요 기능

### 1. 데이터 생성 (`generate.py`)
- **입력 데이터 처리**: `input.json`에서 InterBay, IntraBay, add_points 데이터 추출
- **주소 생성**: 고유 ID를 가진 주소점들 생성
- **연결선 생성**: 주소점들을 연결하는 라인 생성
- **다층 지원**: Z6022, Z4822 레이어별 데이터 처리

### 2. Endpoint 연결 (`addLine_endpoint.py`)
- **미사용 주소 탐지**: 연결되지 않은 주소점 식별
- **자동 연결**: 가장 가까운 주소점과 자동 연결
- **연결 규칙**:
  - 0번 사용된 주소 → 2개 연결 생성
  - 1번 사용된 주소 → 1개 추가 연결 (기존과 다른 연결)

### 3. 데이터 무결성 검사 (`check.py`)
- **중복 검사 및 제거**: ID, name, position 중복 제거
- **겹침 라인 검사**: 동일/역방향 연결 라인 제거
- **고연결 분석**: 4개 이상 연결된 주소점 식별
- **상세 로깅**: 모든 검사 과정을 `check.log`에 기록

### 4. 시각화 (`visualize.py`)
- **인터랙티브 그래프**: Plotly 기반 동적 시각화
- **다층 표시**: Z6022, Z4822 레이어 분리/통합 표시
- **통계 정보**: 주소점 및 연결선 분포 통계
- **호버 정보**: 마우스 오버 시 상세 정보 표시

## 🏗️ 시스템 구조

```
Layout Graph Visualizer
├── 📊 1단계: 데이터 생성 (generate.py)
│   ├── input.json 읽기
│   ├── 주소점 생성 (Addresses)
│   └── 연결선 생성 (Lines)
│
├── 🔗 2단계: Endpoint 연결 (addLine_endpoint.py)
│   ├── 미사용 주소 탐지
│   ├── 자동 연결 생성
│   └── output.json 업데이트
│
├── 🔍 3단계: 데이터 검증 (check.py)
│   ├── 중복 제거
│   ├── 겹침 라인 제거
│   ├── 고연결 분석
│   └── layout.json 생성
│
└── 📈 4단계: 시각화 (visualize.py)
    ├── 데이터 로드
    ├── 통계 분석
    └── 인터랙티브 그래프 생성
```

## ⚙️ 설치 및 실행

### 요구사항
- Python 3.8+
- pip

### 설치
```bash
# 저장소 클론
git clone https://github.com/your-username/layout-graph-visualizer.git
cd layout-graph-visualizer

# 가상환경 생성 (선택사항)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install plotly
```

### 실행
```bash
# 전체 파이프라인 실행
python main.py

# 개별 모듈 실행
python generate.py      # 데이터 생성만
python visualize.py     # 시각화만
python check.py         # 데이터 검증만
```

## 📖 사용법

### 1. 입력 데이터 준비
`input.json` 파일에 레이아웃 데이터를 준비합니다:

```json
{
  "Z6022": {
    "X_lines": [[[x1, y1], [x2, y2]], ...],
    "Y_lines": [[[x1, y1], [x2, y2]], ...],
    "add_points": {
      "y_lines_mid": [[x, y], ...],
      "layer_connect_point": [[x, y], ...],
      "pair_line_connect": [[x, y], ...]
    }
  },
  "Z4822": {
    // Z4822 레이어 데이터
  }
}
```

### 2. 설정 파일 수정
`config.py`에서 시각화 옵션을 조정할 수 있습니다:

```python
# 시각화 모드
VISUALIZATION_MODE = 'both'  # 'z6022', 'x6022', 'both'

# 겹쳐서 보이기
OVERLAP_VISUALIZATION = False

# 시각화 크기
VISUALIZATION_WIDTH = 1920
VISUALIZATION_HEIGHT = 1080
```

### 3. 실행 및 결과 확인
```bash
python main.py
```

실행 후 생성되는 파일들:
- `output.json`: 중간 처리 결과
- `layout.json`: 최종 정리된 데이터
- `check.log`: 상세한 처리 로그
- 브라우저에서 시각화 그래프 표시

## 📁 파일 구조

```
layout-graph-visualizer/
├── 📄 main.py                 # 메인 실행 파일 (38줄)
├── 📄 generate.py             # 데이터 생성 모듈 (716줄)
├── 📄 addLine_endpoint.py     # Endpoint 연결 모듈 (273줄)
├── 📄 check.py               # 데이터 검증 모듈 (489줄)
├── 📄 visualize.py           # 시각화 모듈 (195줄)
├── 📄 config.py              # 설정 파일 (52줄)
├── 📄 input.json             # 입력 데이터 (282줄)
├── 📄 output.json            # 중간 결과 파일
├── 📄 layout.json            # 최종 결과 파일
├── 📄 check.log              # 처리 로그 파일
└── 📄 README.md              # 프로젝트 문서
```

## 🛠️ 기술 스택

### 핵심 기술
- **Python 3.8+**: 메인 프로그래밍 언어
- **Plotly**: 인터랙티브 시각화 라이브러리
- **JSON**: 데이터 직렬화 및 저장
- **Logging**: 상세한 처리 로그

### 주요 라이브러리
```python
import json          # JSON 데이터 처리
import plotly.graph_objects as go  # 시각화
import logging       # 로깅 시스템
from collections import defaultdict, Counter  # 데이터 구조
from typing import List, Dict, Tuple  # 타입 힌트
```

## 📊 데이터 형식

### 입력 데이터 (`input.json`)
```json
{
  "Z6022": {
    "X_lines": [[[x1, y1], [x2, y2]], ...],
    "Y_lines": [[[x1, y1], [x2, y2]], ...],
    "add_points": {
      "y_lines_mid": [[x, y], ...],
      "layer_connect_point": [[x, y], ...],
      "pair_line_connect": [[x, y], ...]
    }
  }
}
```

### 출력 데이터 (`layout.json`)
```json
{
  "addresses": [
    {
      "id": 100001,
      "name": "ADDR_100001",
      "pos": {"x": 4500.0, "y": 5550.0, "z": 6022}
    }
  ],
  "lines": [
    {
      "id": 200001,
      "name": "LINE_100001_100002",
      "fromAddress": 100001,
      "toAddress": 100002,
      "fromPos": {"x": 4500.0, "y": 5550.0, "z": 6022},
      "toPos": {"x": 4564.0, "y": 5550.0, "z": 6022}
    }
  ]
}
```

## 📈 출력 결과

### 처리 통계 예시
```
📊 전체 Addresses 통계:
   총 addresses 수: 7222
   Z값별 분포:
     Z=4822: 5007개
     Z=6022: 2215개

📊 전체 Lines 통계:
   총 lines 수: 7753
   Z값 연결 분포:
     4822→4822: 5418개
     6022→6022: 2335개
```

### 시각화 결과
- **인터랙티브 그래프**: 마우스 오버, 줌, 팬 기능
- **다층 표시**: Z6022(빨간색), Z4822(파란색) 구분
- **통계 정보**: 주소점 및 연결선 분포
- **호버 정보**: 상세한 데이터 정보 표시

## 🔧 고급 설정

### 시각화 모드
```python
# config.py에서 설정
VISUALIZATION_MODE = 'both'  # 'z6022', 'x6022', 'both'
OVERLAP_VISUALIZATION = False  # True: 겹쳐서 표시, False: 분리 표시
```

### 데이터 검증 옵션
```python
# check.py에서 설정
# 고연결 주소점 기준 (기본값: 4개 이상)
HIGHLY_CONNECTED_THRESHOLD = 4
```

### 로깅 레벨
```python
# check.py에서 설정
logging.basicConfig(level=logging.INFO)  # DEBUG, INFO, WARNING, ERROR
```

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### 기여 가이드라인
- 코드 스타일: PEP 8 준수
- 문서화: 함수 및 클래스에 docstring 작성
- 테스트: 새로운 기능에 대한 테스트 코드 작성
- 로깅: 중요한 처리 과정에 로그 추가

## 📝 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 `LICENSE` 파일을 참조하세요.

## 📞 문의

프로젝트에 대한 문의사항이나 버그 리포트는 GitHub Issues를 통해 제출해 주세요.

---

**Layout Graph Visualizer** - 복잡한 레이아웃 데이터의 시각화 솔루션 