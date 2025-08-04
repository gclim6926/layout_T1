# 파일 경로 설정
LAYOUT_FILE = 'layout.json'
INPUT_FILE = 'input.json'
OUTPUT_FILE = 'output.json'

# 시각화 크기 설정
VISUALIZATION_WIDTH = 1920
VISUALIZATION_HEIGHT = 1080

# Z값 설정
Z_VALUES = {
    'z6022': 6022.0,
    'z4822': 4822.0
}

# Z값별 색상 설정
Z_COLORS = {
    6022.0: '#ff4444',  # 빨간색
    4822.0: '#4444ff',  # 파란색
    'other': '#44ff44',  # 녹색
    'default': '#888888'  # 회색
}

# 노드 크기 설정
NODE_SIZE = 3

# 시각화 설정
VISUALIZATION_CONFIG = {
    'line_width': 1,
    'hover_mode': 'closest',
    'marker_border_color': None,
    'marker_border_width': 0,
    'legend_position': {
        'yanchor': 'top',
        'y': 0.99,
        'xanchor': 'left',
        'x': 0.01
    }
}

# 시각화 모드 ('z6022', 'x6022', 'both')
VISUALIZATION_MODE = 'both'

# 겹쳐서 보이기 설정
#OVERLAP_VISUALIZATION = True
OVERLAP_VISUALIZATION = False

# 데이터 생성 설정
RANDOM_INTERVAL = [54.0, 58.0, 61.0, 64.0]
ADDRESS_ID_START = 100001
LINE_ID_START = 200001

