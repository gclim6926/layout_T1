import json
import os
import re
import webbrowser
from pathlib import Path
from typing import Optional
import plotly.graph_objects as go
import plotly.io as pio
from collections import defaultdict
from config_3D import (
    LAYOUT_FILE, OUTPUT_FILE,
    VISUALIZATION_WIDTH, VISUALIZATION_HEIGHT, VISUALIZATION_MODE, NODE_SIZE,
    OVERLAP_VISUALIZATION
)
from config import OHT_FRAME_INTERVAL_MS as OHT_FRAME_INTERVAL_MS_3D
from config import OHT_FRAME_STRIDE, OHT_TARGET_DURATION_SEC

# Z값 설정 (3D 시각화 전용)
Z_VALUES = {
    'z6022': 6022.0,
    'z4822': 4822.0,
    'z0': 0.0
}

# Z값별 색상 설정 (3D 시각화 전용)
Z_COLORS = {
    6022.0: '#ff4444',  # 빨간색
    4822.0: '#4444ff',  # 파란색
    0.0: '#ffff44',     # 노란색
    'other': '#44ff44',  # 녹색
    'default': '#888888'  # 회색
}

# 시각화 설정 (3D 시각화 전용)
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

pio.renderers.default = "browser"

# 대량 포인트 샘플링 한도 (성능 최적화)
MAX_3D_ADDRESSES = 50000
MAX_3D_STATIONS = 10000
MAX_OHT_FRAMES_3D = 1500

class LayoutVisualizer3D:
    def __init__(self, layout_file=OUTPUT_FILE, selected_components=None, selected_layers=None, 
                 overlap_mode=False, visualization_mode='overlap'):
        self.layout_file = layout_file
        self.selected_components = selected_components or ['addresses', 'lines', 'stations']  # 기본값: 모든 컴포넌트
        self.selected_layers = selected_layers or ['z6022', 'z4822']  # 기본값: z6022, z4822
        self.overlap_mode = overlap_mode  # True: 겹쳐서 보이기, False: 분리해서 보이기
        self.visualization_mode = visualization_mode  # 'z6022', 'z4822', 'z0', 'overlap', 'multiple'
        
        self.addresses = []
        self.lines = []
        self.stations = []
        self.address_map = {}
        
        # 선택된 Z값들을 실제 Z 좌표로 변환
        self.selected_z_values = []
        for layer in self.selected_layers:
            if layer == 'z6022':
                self.selected_z_values.append(Z_VALUES['z6022'])
            elif layer == 'z4822':
                self.selected_z_values.append(Z_VALUES['z4822'])
            elif layer == 'z0':
                self.selected_z_values.append(Z_VALUES['z0'])

    def _sample_list(self, items, max_count):
        """항목 수가 max_count를 초과하면 균일 간격 다운샘플링"""
        if not items:
            return items
        n = len(items)
        if n <= max_count:
            return items
        step = max(1, n // max_count)
        return items[::step]
    
    def load_layout_data(self):
        """layout.json 파일을 읽어서 데이터를 로드합니다."""
        try:
            with open(self.layout_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.addresses = data.get('addresses', [])
            self.lines = data.get('lines', [])
            self.stations = data.get('stations', [])
            # 주소 맵 구성: address 코드 -> (x, y, z)
            try:
                self.address_map = {
                    int(addr.get('address')): (
                        addr['pos']['x'], addr['pos']['y'], addr['pos']['z']
                    ) for addr in self.addresses if 'address' in addr and 'pos' in addr
                }
            except Exception:
                # 일부 데이터는 address가 문자열일 수 있으니 보정
                self.address_map = {}
                for addr in self.addresses:
                    if 'address' in addr and 'pos' in addr:
                        try:
                            key = int(addr['address'])
                        except Exception:
                            continue
                        self.address_map[key] = (addr['pos']['x'], addr['pos']['y'], addr['pos']['z'])
            
            print(f"✅ {self.layout_file} 파일을 성공적으로 로드했습니다.")
            print(f"📊 Addresses: {len(self.addresses)}개, Lines: {len(self.lines)}개, Stations: {len(self.stations)}개")
            return True
            
        except Exception as e:
            print(f"❌ 데이터 로드 중 오류 발생: {str(e)}")
            return False
    
    def get_color_by_z(self, z):
        """Z값에 따른 색상 반환"""
        if z == Z_VALUES['z6022']:
            return Z_COLORS[Z_VALUES['z6022']]
        elif z == Z_VALUES['z4822']:
            return Z_COLORS[Z_VALUES['z4822']]
        elif z == Z_VALUES['z0']:
            return Z_COLORS[Z_VALUES['z0']]
        else:
            return Z_COLORS['default']
    
    def filter_data_by_z(self, z_value, include=True):
        """Z값에 따라 데이터 필터링"""
        if include:
            filtered_addresses = [a for a in self.addresses if a['pos']['z'] == z_value]
            filtered_lines = [l for l in self.lines if l['fromPos']['z'] == z_value and l['toPos']['z'] == z_value]
            filtered_stations = [s for s in self.stations if s['pos']['z'] == z_value]
        else:
            filtered_addresses = [a for a in self.addresses if a['pos']['z'] != z_value]
            filtered_lines = [l for l in self.lines if l['fromPos']['z'] != z_value and l['toPos']['z'] != z_value]
            filtered_stations = [s for s in self.stations if s['pos']['z'] != z_value]
        
        return filtered_addresses, filtered_lines, filtered_stations
    
    def _get_line_style(self, z1, z2):
        """라인의 두 Z값에 따라 (color, width) 반환"""
        if (z1 == Z_VALUES['z4822'] and z2 == Z_VALUES['z6022']) or (z1 == Z_VALUES['z6022'] and z2 == Z_VALUES['z4822']):
            return '#000000', 2
        if z1 == Z_VALUES['z6022'] or z2 == Z_VALUES['z6022']:
            return Z_COLORS[Z_VALUES['z6022']], VISUALIZATION_CONFIG['line_width']
        if z1 == Z_VALUES['z4822'] or z2 == Z_VALUES['z4822']:
            return Z_COLORS[Z_VALUES['z4822']], VISUALIZATION_CONFIG['line_width']
        if z1 == Z_VALUES['z0'] or z2 == Z_VALUES['z0']:
            return Z_COLORS[Z_VALUES['z0']], VISUALIZATION_CONFIG['line_width']
        return Z_COLORS['other'], VISUALIZATION_CONFIG['line_width']

    def _add_merged_line_traces(self, fig, lines):
        """여러 라인을 색상/스타일별로 병합하여 최소한의 트레이스로 추가"""
        if not lines:
            return
        groups = {}
        for line in lines:
            if 'fromPos' not in line or 'toPos' not in line:
                continue
            z1, z2 = line['fromPos']['z'], line['toPos']['z']
            color, width = self._get_line_style(z1, z2)
            key = (color, width)
            if key not in groups:
                groups[key] = {'x': [], 'y': [], 'z': []}
            groups[key]['x'].extend([line['fromPos']['x'], line['toPos']['x'], None])
            groups[key]['y'].extend([line['fromPos']['y'], line['toPos']['y'], None])
            groups[key]['z'].extend([line['fromPos']['z'], line['toPos']['z'], None])
        for (color, width), coords in groups.items():
            fig.add_trace(go.Scatter3d(
                x=coords['x'], y=coords['y'], z=coords['z'],
                mode='lines',
                line=dict(color=color, width=width),
                showlegend=False,
                hoverinfo='skip'
            ))

    # ============================
    # OHT 애니메이션 관련 기능
    # ============================
    def _parse_udp_log_current_addresses(self, log_file: str):
        """output_udp_data.log에서 (time_str, current_address:int) 리스트를 추출
        - 현재 파일 포맷: [TIME]IP:..., ..., <Current>,0,<Next>, ...
        - 레거시 포맷: Time:..., Current Address: ... 도 지원
        """
        if not os.path.exists(log_file):
            print(f"⚠️ UDP 로그 파일을 찾을 수 없습니다: {log_file}")
            return []
        entries = []
        square_time = re.compile(r'^\s*\[([^\]]+)\]')
        curr_zero_next = re.compile(r',\s*(\d{5,})\s*,\s*0\s*,\s*\d{5,}\s*,')
        legacy_time = re.compile(r'Time\s*:\s*([^,]+)')
        legacy_curr = re.compile(r'Current Address\s*:\s*(\d+)')
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    time_str = None
                    curr_addr = None
                    m1 = square_time.search(line)
                    if m1:
                        time_str = m1.group(1).strip()
                    m2 = curr_zero_next.search(line)
                    if m2:
                        try:
                            curr_addr = int(m2.group(1))
                        except Exception:
                            curr_addr = None
                    if time_str is None:
                        m3 = legacy_time.search(line)
                        if m3:
                            time_str = m3.group(1).strip()
                    if curr_addr is None:
                        m4 = legacy_curr.search(line)
                        if m4:
                            try:
                                curr_addr = int(m4.group(1))
                            except Exception:
                                curr_addr = None
                    if time_str is not None and curr_addr is not None:
                        entries.append((time_str, curr_addr))
        except Exception as e:
            print(f"⚠️ UDP 로그 파싱 오류: {e}")
            return []
        if not entries:
            print("⚠️ UDP 로그에서 유효한 항목을 찾지 못했습니다.")
        return entries

    def _build_oht_positions(self, udp_log_path: str):
        """UDP 로그를 좌표 시퀀스로 변환: [(x,y,z)]"""
        parsed = self._parse_udp_log_current_addresses(udp_log_path)
        positions = []
        for _, addr_code in parsed:
            pos = self.address_map.get(addr_code)
            if pos:
                positions.append(pos)
        print(f"🎥 OHT 프레임 수: {len(positions)}")
        return positions

    def _attach_oht_animation(self, fig, positions, frame_duration_ms: int = None):
        if frame_duration_ms is None:
            frame_duration_ms = OHT_FRAME_INTERVAL_MS_3D
        """주어진 fig에 OHT 애니메이션 트레이스와 프레임을 추가"""
        if not positions:
            print("⚠️ OHT 애니메이션에 사용할 좌표가 없습니다.")
            return

        # 초기 위치
        x0, y0, z0 = positions[0]
        oht_trace_index = len(fig.data)
        fig.add_trace(go.Scatter3d(
            x=[x0], y=[y0], z=[z0],
            mode='markers',
            marker=dict(size=NODE_SIZE + 4, color='#00FFFF', symbol='circle', opacity=1.0),
            name='OHT',
            showlegend=True
        ))

        # 프레임 stride/상한으로 성능 최적화
        frames = []
        if positions and len(positions) > MAX_OHT_FRAMES_3D:
            from math import ceil
            step = max(1, ceil(len(positions) / MAX_OHT_FRAMES_3D))
            positions = positions[::step]
        # 목표 재생 시간 기반 stride 추가 적용
        if positions:
            try:
                target_frames = max(1, int((OHT_TARGET_DURATION_SEC * 1000) / max(1, OHT_FRAME_INTERVAL_MS_3D)))
                if len(positions) > target_frames:
                    from math import ceil
                    dyn_stride = max(1, ceil(len(positions) / target_frames))
                    positions = positions[::dyn_stride]
            except Exception:
                pass
        if positions and OHT_FRAME_STRIDE > 1:
            positions = positions[::OHT_FRAME_STRIDE]
        for i, (x, y, z) in enumerate(positions):
            frames.append(go.Frame(
                data=[go.Scatter3d(x=[x], y=[y], z=[z])],
                traces=[oht_trace_index],
                name=f"frame_{i}"
            ))
        fig.frames = frames

        # 애니메이션 컨트롤 추가
        fig.update_layout(
            updatemenus=[
                dict(
                    type='buttons',
                    showactive=False,
                    y=0,
                    x=0,
                    xanchor='left',
                    yanchor='bottom',
                    buttons=[
                        dict(
                            label='Play',
                            method='animate',
                            args=[
                                None,
                                {
                                    'frame': {'duration': frame_duration_ms, 'redraw': False},
                                    'transition': {'duration': 0},
                                    'fromcurrent': True,
                                    'mode': 'immediate',
                                    'repeat': True
                                }
                            ]
                        ),
                        dict(
                            label='Pause',
                            method='animate',
                            args=[[None], {'frame': {'duration': 0, 'redraw': False}, 'mode': 'immediate'}]
                        )
                    ]
                )
            ],
            sliders=[
                dict(
                    active=0,
                    steps=[dict(method='animate',
                                args=[[f"frame_{i}"], {'mode': 'immediate', 'frame': {'duration': 0, 'redraw': False}, 'transition': {'duration': 0}}],
                                label=str(i)) for i in range(len(frames))]
                )
            ]
        )

    def _show_figure(self, fig, filename_prefix: str = "3d_layout"):
        """애니메이션 자동 재생을 위해 HTML로 저장 후 브라우저로 오픈"""
        try:
            html = pio.to_html(fig, include_plotlyjs='cdn', auto_play=True)
            out_path = Path.cwd() / f"{filename_prefix}.html"
            with open(out_path, 'w', encoding='utf-8') as f:
                f.write(html)
            webbrowser.open(f"file://{out_path}")
        except Exception as e:
            print(f"⚠️ HTML 저장/오픈 중 오류: {e}. 기본 show()로 대체합니다.")
            fig.show()

    def _is_oht_selected(self) -> bool:
        comps = [c.lower() for c in (self.selected_components or [])]
        return ('ohts' in comps) or ('oht' in comps)
    
    
    
    def create_3d_visualization(self, addresses, lines, title, stations=None):
        """3D 시각화 생성"""
        fig = go.Figure()

        # 3D 선 그리기 (Lines 컴포넌트가 선택된 경우에만)
        if 'lines' in self.selected_components and lines:
            self._add_merged_line_traces(fig, lines)

        # 3D 점 그리기 (Addresses 컴포넌트가 선택된 경우에만)
        if 'addresses' in self.selected_components and addresses:
            sampled_addresses = self._sample_list(addresses, MAX_3D_ADDRESSES)
            x_coords = [addr['pos']['x'] for addr in sampled_addresses]
            y_coords = [addr['pos']['y'] for addr in sampled_addresses]
            z_coords = [addr['pos']['z'] for addr in sampled_addresses]
            colors = [self.get_color_by_z(addr['pos']['z']) for addr in sampled_addresses]
            ids = [addr['id'] for addr in sampled_addresses]
            names = [addr['name'] for addr in sampled_addresses]

            fig.add_trace(go.Scatter3d(
                x=x_coords,
                y=y_coords,
                z=z_coords,
                mode='markers',
                marker=dict(
                    size=NODE_SIZE,
                    color=colors,
                    line=dict(
                        color=VISUALIZATION_CONFIG['marker_border_color'],
                        width=VISUALIZATION_CONFIG['marker_border_width']
                    ),
                    opacity=0.8
                ),
                name='Addresses',
                showlegend=True,
                hovertemplate=f'<b>{title}</b><br>ID: %{{text}}<br>Name: %{{customdata}}<br>X: %{{x}}<br>Y: %{{y}}<br>Z: %{{z}}<extra></extra>',
                text=ids,
                customdata=names
            ))

        # 3D Stations 그리기 (Stations 컴포넌트가 선택된 경우에만)
        if 'stations' in self.selected_components and stations:
            sampled_stations = self._sample_list(stations, MAX_3D_STATIONS)
            x_coords = [station['pos']['x'] for station in sampled_stations]
            y_coords = [station['pos']['y'] for station in sampled_stations]
            z_coords = [station['pos']['z'] for station in sampled_stations]
            ids = [station['id'] for station in sampled_stations]
            names = [station['name'] for station in sampled_stations]
            ports = [station['port'] for station in sampled_stations]

            fig.add_trace(go.Scatter3d(
                x=x_coords,
                y=y_coords,
                z=z_coords,
                mode='markers',
                marker=dict(
                    size=NODE_SIZE + 2,  # Stations는 Addresses보다 약간 크게
                    color='#FFD700',  # 금색
                    symbol='diamond',  # 다이아몬드 모양
                    line=dict(
                        color='#FF8C00',  # 진한 주황색 테두리
                        width=1
                    ),
                    opacity=0.9
                ),
                name='Stations',
                showlegend=True,
                hovertemplate=f'<b>Station</b><br>ID: %{{text}}<br>Name: %{{customdata[0]}}<br>Port: %{{customdata[1]}}<br>X: %{{x}}<br>Y: %{{y}}<br>Z: %{{z}}<extra></extra>',
                text=ids,
                customdata=list(zip(names, ports))
            ))

        # 3D 레이아웃 설정
        fig.update_layout(
            title=title,
            width=VISUALIZATION_WIDTH,
            height=VISUALIZATION_HEIGHT,
            showlegend=True,
            hovermode=VISUALIZATION_CONFIG['hover_mode'],
            legend=VISUALIZATION_CONFIG['legend_position'],
            paper_bgcolor='white',
            plot_bgcolor='white',
            uirevision='oht_keep_view',
            scene=dict(
                bgcolor='white',
                xaxis=dict(
                    title='X 좌표',
                    showgrid=True,
                    gridcolor='lightgray',
                    zeroline=True,
                    zerolinecolor='black'
                ),
                yaxis=dict(
                    title='Y 좌표',
                    showgrid=True,
                    gridcolor='lightgray',
                    zeroline=True,
                    zerolinecolor='black'
                ),
                zaxis=dict(
                    title='Z 좌표',
                    showgrid=True,
                    gridcolor='lightgray',
                    zeroline=True,
                    zerolinecolor='black'
                ),
                camera=dict(
                    eye=dict(x=1.5, y=1.5, z=1.5),
                    center=dict(x=0, y=0, z=0)
                ),
                aspectmode='data'
            )
        )

        return fig
    
    def create_3d_visualization_by_layer(self, addresses, lines, title, stations=None):
        """Z 레이어별로 3D 시각화 생성"""
        fig = go.Figure()

        # Z 레이어별로 데이터 분리
        z_layers = {}
        for addr in addresses:
            z = addr['pos']['z']
            if z not in z_layers:
                z_layers[z] = {'addresses': [], 'lines': []}
            z_layers[z]['addresses'].append(addr)
        
        for line in lines:
            z1, z2 = line['fromPos']['z'], line['toPos']['z']
            # Z 레이어가 다른 경우 두 레이어 모두에 추가
            for z in [z1, z2]:
                if z not in z_layers:
                    z_layers[z] = {'addresses': [], 'lines': []}
                z_layers[z]['lines'].append(line)

        # Stations를 Z 레이어별로 분리
        if stations:
            for station in stations:
                z = station['pos']['z']
                if z not in z_layers:
                    z_layers[z] = {'addresses': [], 'lines': [], 'stations': []}
                elif 'stations' not in z_layers[z]:
                    z_layers[z]['stations'] = []
                z_layers[z]['stations'].append(station)

        # 각 Z 레이어별로 시각화
        for z, data in sorted(z_layers.items()):
            layer_addresses = data['addresses']
            layer_lines = data['lines']
            layer_stations = data.get('stations', [])
            
            # Addresses 컴포넌트가 선택된 경우에만 표시
            if 'addresses' in self.selected_components and layer_addresses:
                x_coords = [addr['pos']['x'] for addr in layer_addresses]
                y_coords = [addr['pos']['y'] for addr in layer_addresses]
                z_coords = [addr['pos']['z'] for addr in layer_addresses]
                colors = [self.get_color_by_z(addr['pos']['z']) for addr in layer_addresses]
                ids = [addr['id'] for addr in layer_addresses]
                names = [addr['name'] for addr in layer_addresses]

                fig.add_trace(go.Scatter3d(
                    x=x_coords,
                    y=y_coords,
                    z=z_coords,
                    mode='markers',
                    marker=dict(
                        size=NODE_SIZE,
                        color=colors,
                        line=dict(
                            color=VISUALIZATION_CONFIG['marker_border_color'],
                            width=VISUALIZATION_CONFIG['marker_border_width']
                        ),
                        opacity=0.8
                    ),
                    name=f'Addresses Z={z}',
                    showlegend=True,
                    hovertemplate=f'<b>Z={z}</b><br>ID: %{{text}}<br>Name: %{{customdata}}<br>X: %{{x}}<br>Y: %{{y}}<br>Z: %{{z}}<extra></extra>',
                    text=ids,
                    customdata=names
                ))

            # Stations 컴포넌트가 선택된 경우에만 표시
            if 'stations' in self.selected_components and layer_stations:
                x_coords = [station['pos']['x'] for station in layer_stations]
                y_coords = [station['pos']['y'] for station in layer_stations]
                z_coords = [station['pos']['z'] for station in layer_stations]
                ids = [station['id'] for station in layer_stations]
                names = [station['name'] for station in layer_stations]
                ports = [station['port'] for station in layer_stations]

                fig.add_trace(go.Scatter3d(
                    x=x_coords,
                    y=y_coords,
                    z=z_coords,
                    mode='markers',
                    marker=dict(
                        size=NODE_SIZE + 2,  # Stations는 Addresses보다 약간 크게
                        color='#FFD700',  # 금색
                        symbol='diamond',  # 다이아몬드 모양
                        line=dict(
                            color='#FF8C00',  # 진한 주황색 테두리
                            width=2
                        ),
                        opacity=0.9
                    ),
                    name=f'Stations Z={z}',
                    showlegend=True,
                    hovertemplate=f'<b>Station Z={z}</b><br>ID: %{{text}}<br>Name: %{{customdata[0]}}<br>Port: %{{customdata[1]}}<br>X: %{{x}}<br>Y: %{{y}}<br>Z: %{{z}}<extra></extra>',
                    text=ids,
                    customdata=list(zip(names, ports))
                ))

            # Lines 컴포넌트가 선택된 경우에만 표시
            if 'lines' in self.selected_components and layer_lines:
                self._add_merged_line_traces(fig, layer_lines)

        # 3D 레이아웃 설정
        fig.update_layout(
            title=title,
            width=VISUALIZATION_WIDTH,
            height=VISUALIZATION_HEIGHT,
            showlegend=True,
            hovermode=VISUALIZATION_CONFIG['hover_mode'],
            legend=VISUALIZATION_CONFIG['legend_position'],
            paper_bgcolor='white',
            plot_bgcolor='white',
            scene=dict(
                bgcolor='white',
                xaxis=dict(
                    title='X 좌표',
                    showgrid=True,
                    gridcolor='lightgray',
                    zeroline=True,
                    zerolinecolor='black'
                ),
                yaxis=dict(
                    title='Y 좌표',
                    showgrid=True,
                    gridcolor='lightgray',
                    zeroline=True,
                    zerolinecolor='black'
                ),
                zaxis=dict(
                    title='Z 좌표',
                    showgrid=True,
                    gridcolor='lightgray',
                    zeroline=True,
                    zerolinecolor='black'
                ),
                camera=dict(
                    eye=dict(x=1.5, y=1.5, z=1.5),
                    center=dict(x=0, y=0, z=0)
                ),
                aspectmode='data'
            )
        )

        return fig
    
    def print_statistics(self, data_list, title, data_type):
        """통계 정보 출력"""
        print(f"\n📊 {title} 통계:")
        print(f"   총 {data_type} 수: {len(data_list)}")
        
        if data_list:
            if data_type == 'addresses':
                z_counts = defaultdict(int)
                for addr in data_list:
                    z_counts[addr['pos']['z']] += 1
                print("   Z값별 분포:")
                for z, count in sorted(z_counts.items()):
                    print(f"     Z={z}: {count}개")
            elif data_type == 'stations':
                z_counts = defaultdict(int)
                for station in data_list:
                    z_counts[station['pos']['z']] += 1
                print("   Z값별 Stations 분포:")
                for z, count in sorted(z_counts.items()):
                    print(f"     Z={z}: {count}개")
            else:  # lines
                z_counts = defaultdict(int)
                for line in data_list:
                    z1, z2 = line['fromPos']['z'], line['toPos']['z']
                    z_key = f"{z1}→{z2}"
                    z_counts[z_key] += 1
                print("   Z값 연결 분포:")
                for z_key, count in sorted(z_counts.items()):
                    print(f"     {z_key}: {count}개")
    
    def create_3d_visualizations(self):
        """전체 3D 시각화 생성"""
        print("🚀 3D 시각화를 시작합니다...")
        print(f"🔍 선택된 컴포넌트: {self.selected_components}")
        print(f"🔍 선택된 레이어: {self.selected_layers}")
        print(f"🔍 선택된 Z값: {self.selected_z_values}")
        print(f"🔍 Overlap 모드: {self.overlap_mode}")
        print(f"🔍 시각화 모드: {self.visualization_mode}")
        
        if not self.load_layout_data():
            print("❌ 데이터 로드 실패")
            return False

        # 전체 데이터 통계 출력
        self.print_statistics(self.addresses, "전체 Addresses", "addresses")
        self.print_statistics(self.lines, "전체 Lines", "lines")
        self.print_statistics(self.stations, "전체 Stations", "stations")

        # 선택된 Z값에 따라 데이터 필터링
        filtered_data = {}
        for z_value in self.selected_z_values:
            addresses, lines, stations = self.filter_data_by_z(z_value, include=True)
            filtered_data[z_value] = {
                'addresses': addresses,
                'lines': lines,
                'stations': stations
            }
            print(f"\n🔍 Z={z_value} 데이터:")
            print(f"   Addresses: {len(addresses)}개")
            print(f"   Lines: {len(lines)}개")
            print(f"   Stations: {len(stations)}개")

        # Layer Filter와 Overlap 모드에 따른 시각화 생성
        if self.overlap_mode:
            # Overlap 모드: 모든 선택된 레이어를 하나의 창에 겹쳐서 표시
            print(f"\n🔄 Overlap 모드: 1개의 창으로 겹쳐서 출력")
            
            all_addresses = []
            all_lines = []
            all_stations = []
            
            for z_value in self.selected_z_values:
                data = filtered_data[z_value]
                all_addresses.extend(data['addresses'])
                all_lines.extend(data['lines'])
                all_stations.extend(data['stations'])
            
            # 선택된 컴포넌트에 따라 데이터 필터링
            overlap_addresses = all_addresses if 'addresses' in self.selected_components else []
            # 라인은 선택된 레이어 집합에 양 끝 Z가 모두 포함될 때만 표시 (교차 레이어 라인 처리)
            if 'lines' in self.selected_components:
                selected_z_set = set(self.selected_z_values)
                overlap_lines = [
                    l for l in self.lines
                    if 'fromPos' in l and 'toPos' in l
                    and l['fromPos']['z'] in selected_z_set
                    and l['toPos']['z'] in selected_z_set
                ]
            else:
                overlap_lines = []
            overlap_stations = all_stations if 'stations' in self.selected_components else []
            
            print(f"🔍 Overlap 모드에서 사용할 데이터:")
            print(f"   Addresses: {len(overlap_addresses)}개 (선택됨: {'addresses' in self.selected_components})")
            print(f"   Lines: {len(overlap_lines)}개 (선택됨: {'lines' in self.selected_components})")
            print(f"   Stations: {len(overlap_stations)}개 (선택됨: {'stations' in self.selected_components})")
            
            if overlap_addresses or overlap_lines or overlap_stations:
                fig_overlap = self.create_3d_visualization_by_layer(overlap_addresses, overlap_lines, "3D Layout Visualization - Overlap Mode", overlap_stations)
                # OHT 애니메이션이 선택된 경우 로그 기반 프레임 부착
                if self._is_oht_selected():
                    udp_log_path = 'output_udp_data.log'
                    positions = self._build_oht_positions(udp_log_path)
                    self._attach_oht_animation(fig_overlap, positions)
                self._show_figure(fig_overlap, filename_prefix="3d_overlap")
                print("✅ Overlap 3D 시각화 창이 열렸습니다.")
            else:
                print("⚠️ 선택된 컴포넌트에 해당하는 데이터가 없습니다.")
                
        else:
            # 개별 모드: 각 선택된 레이어를 별도 창으로 표시
            print(f"\n🔍 개별 모드: 각 레이어별로 독립된 창으로 출력")
            
            for i, z_value in enumerate(self.selected_z_values):
                data = filtered_data[z_value]
                
                if data['addresses'] or data['lines'] or data['stations']:
                    print(f"🔄 Z={z_value} 시각화 창을 생성합니다...")
                    
                    # 선택된 컴포넌트에 따라 데이터 필터링
                    layer_addresses = data['addresses'] if 'addresses' in self.selected_components else []
                    layer_lines = data['lines'] if 'lines' in self.selected_components else []
                    layer_stations = data['stations'] if 'stations' in self.selected_components else []
                    
                    if z_value == Z_VALUES['z6022']:
                        title = f"3D Layout Visualization - Z6022 (빨간색)"
                    elif z_value == Z_VALUES['z4822']:
                        title = f"3D Layout Visualization - Z4822 (파란색)"
                    elif z_value == Z_VALUES['z0']:
                        title = f"3D Layout Visualization - Z0 (노란색)"
                    else:
                        title = f"3D Layout Visualization - Z={z_value}"
                    
                    fig_individual = self.create_3d_visualization(layer_addresses, layer_lines, title, layer_stations)
                    if self._is_oht_selected():
                        udp_log_path = 'output_udp_data.log'
                        positions = self._build_oht_positions(udp_log_path)
                        # 해당 레이어 포인트만 사용하도록 필터
                        if positions:
                            target_z = z_value
                            positions = [p for p in positions if abs(p[2] - target_z) < 1e-6]
                        self._attach_oht_animation(fig_individual, positions)
                    self._show_figure(fig_individual, filename_prefix=f"3d_layer_{int(z_value)}")
                    print(f"✅ Z={z_value} 시각화 창이 열렸습니다. (창 {i+1}/{len(self.selected_z_values)})")
                    
                else:
                    print(f"⚠️ Z={z_value}에 해당하는 데이터가 없습니다.")

        print("✅ 3D 시각화가 완료되었습니다!")
        return True

def main():
    """메인 실행 함수"""
    visualizer = LayoutVisualizer3D(
        selected_layers=['z6022', 'z4822'],
        overlap_mode=True,
        selected_components=['addresses', 'lines', 'stations']
    )
    visualizer.create_3d_visualizations()

if __name__ == "__main__":
    main() 