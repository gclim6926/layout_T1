import json
import os
import re
import webbrowser
from pathlib import Path
from typing import Optional
import plotly.graph_objects as go
import plotly.io as pio
from collections import defaultdict
from config import NODE_SIZE as CFG_NODE_SIZE
from config import OHT_FRAME_INTERVAL_MS as OHT_FRAME_INTERVAL_MS_2D
from config import OHT_FRAME_STRIDE, OHT_TARGET_DURATION_SEC, USE_JS_RESTYLE_ANIMATION, USE_WEBGL_2D

# Z값 설정 (2D 시각화 전용)
Z_VALUES = {
    'z6022': 6022.0,
    'z4822': 4822.0,
    'z0': 0.0
}

# Z값별 색상 설정 (2D 시각화 전용)
Z_COLORS = {
    6022.0: '#ff4444',  # 빨간색
    4822.0: '#4444ff',  # 파란색
    0.0: '#ffff44',     # 노란색
    'other': '#44ff44',  # 녹색
    'default': '#888888'  # 회색
}

# 시각화 설정 (2D 시각화 전용)
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

# 대량 포인트 샘플링 한도 (성능 최적화)
MAX_2D_ADDRESSES = 20000
MAX_2D_STATIONS = 5000

pio.renderers.default = "browser"

class LayoutVisualizer:
    def __init__(self, layout_file=None, visualization_mode='overlap', overlap_visualization=False, 
                 visualization_width=1920, visualization_height=1080, node_size=3, selected_z_values=None, selected_components=None):
        if layout_file is None:
            layout_file = 'output.json'  # 기본값
        self.layout_file = layout_file
        self.visualization_mode = visualization_mode
        self.overlap_visualization = overlap_visualization
        self.visualization_width = visualization_width
        self.visualization_height = visualization_height
        self.node_size = node_size
        self.selected_z_values = selected_z_values or []
        self.addresses = []
        self.lines = []
        self.stations = []
        self.address_coords = {}  # 주소별 좌표 정보
        self.enable_oht = False
        self.selected_components = selected_components or ['addresses', 'lines', 'stations']
        
    def _sample_list(self, items, max_count):
        """항목 수가 max_count를 초과하면 균일 간격으로 다운샘플링"""
        if not items:
            return items
        n = len(items)
        if n <= max_count:
            return items
        # 상한을 넘지 않도록 ceil 기반 간격 사용
        from math import ceil
        step = max(1, ceil(n / max_count))
        return items[::step]

    def load_layout_data(self):
        """layout.json 파일을 읽어서 데이터를 로드합니다."""
        try:
            with open(self.layout_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.addresses = data.get('addresses', [])
            self.lines = data.get('lines', [])
            self.stations = data.get('stations', [])
            
            # 주소별 좌표 정보 생성
            for addr in self.addresses:
                if 'address' in addr and 'pos' in addr:
                    self.address_coords[addr['address']] = addr['pos']
            
            print(f"✅ {self.layout_file} 파일을 성공적으로 로드했습니다.")
            print(f"📊 Addresses: {len(self.addresses)}개, Lines: {len(self.lines)}개, Stations: {len(self.stations)}개")
            return True
            
        except Exception as e:
            print(f"❌ 데이터 로드 중 오류 발생: {str(e)}")
            return False
    
    def get_address_position(self, address):
        """주소에 해당하는 좌표를 반환합니다."""
        return self.address_coords.get(address)
    
    
    
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

    # ============================
    # OHT 애니메이션 (2D)
    # ============================
    def enable_oht_animation(self, enable=True):
        self.enable_oht = enable

    def _parse_udp_log_current_addresses(self, log_file: str):
        if not os.path.exists(log_file):
            return []
        entries = []
        square_time = re.compile(r'^\s*\[([^\]]+)\]')
        curr_zero_next = re.compile(r',\s*(\d{5,})\s*,\s*0\s*,\s*\d{5,}\s*,')
        legacy_time = re.compile(r'Time\s*:\s*([^,]+)')
        legacy_curr = re.compile(r'Current Address\s*:\s*(\d+)')
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
        return entries

    def _build_oht_positions(self, udp_log_path: str, target_z: Optional[float] = None):
        parsed = self._parse_udp_log_current_addresses(udp_log_path)
        positions = []
        for _, addr_code in parsed:
            pos = self.address_coords.get(addr_code)
            if not pos:
                continue
            if (target_z is None) or (abs(pos['z'] - target_z) < 1e-6):
                positions.append((pos['x'], pos['y']))
        return positions
    
    def filter_data_by_z(self, z_value, include=True):
        """Z값에 따라 데이터 필터링"""
        if include:
            filtered_addresses = [a for a in self.addresses if a['pos']['z'] == z_value]
            filtered_lines = [l for l in self.lines if l['fromPos']['z'] == z_value or l['toPos']['z'] == z_value]
            filtered_stations = [s for s in self.stations if s['pos']['z'] == z_value]
        else:
            filtered_addresses = [a for a in self.addresses if a['pos']['z'] != z_value]
            filtered_lines = [l for l in self.lines if l['fromPos']['z'] != z_value and l['toPos']['z'] != z_value]
            filtered_stations = [s for s in self.stations if s['pos']['z'] != z_value]
        
        return filtered_addresses, filtered_lines, filtered_stations
    
    def create_visualization(self, addresses, lines, title, stations=None, target_z: Optional[float] = None):
        """시각화 생성"""
        fig = go.Figure()

        # 선 그리기 (색상별 병합하여 트레이스 수 최소화)
        if lines and ('lines' in self.selected_components):
            def get_line_color(z1, z2):
                if z1 == Z_VALUES['z6022'] or z2 == Z_VALUES['z6022']:
                    return Z_COLORS[Z_VALUES['z6022']]
                if z1 == Z_VALUES['z4822'] or z2 == Z_VALUES['z4822']:
                    return Z_COLORS[Z_VALUES['z4822']]
                if z1 == Z_VALUES['z0'] or z2 == Z_VALUES['z0']:
                    return Z_COLORS[Z_VALUES['z0']]
                return Z_COLORS['other']

            groups = {}
            for line in lines:
                if 'fromPos' not in line or 'toPos' not in line:
                    continue
                z1, z2 = line['fromPos']['z'], line['toPos']['z']
                color = get_line_color(z1, z2)
                if color not in groups:
                    groups[color] = {'x': [], 'y': []}
                groups[color]['x'].extend([line['fromPos']['x'], line['toPos']['x'], None])
                groups[color]['y'].extend([line['fromPos']['y'], line['toPos']['y'], None])

            for color, coords in groups.items():
                if USE_WEBGL_2D:
                    fig.add_trace(go.Scattergl(
                        x=coords['x'], y=coords['y'],
                        mode='lines',
                        line=dict(color=color, width=VISUALIZATION_CONFIG['line_width']),
                        showlegend=False,
                        hoverinfo='skip'
                    ))
                else:
                    fig.add_trace(go.Scatter(
                        x=coords['x'], y=coords['y'],
                        mode='lines',
                        line=dict(color=color, width=VISUALIZATION_CONFIG['line_width']),
                        showlegend=False,
                        hoverinfo='skip'
                    ))

        # 점 그리기 (Addresses) - 대량일 경우 샘플링
        if addresses and ('addresses' in self.selected_components):
            sampled_addresses = self._sample_list(addresses, MAX_2D_ADDRESSES)
            x_coords = [addr['pos']['x'] for addr in sampled_addresses]
            y_coords = [addr['pos']['y'] for addr in sampled_addresses]
            colors = [self.get_color_by_z(addr['pos']['z']) for addr in sampled_addresses]
            ids = [addr['id'] for addr in sampled_addresses]

            if USE_WEBGL_2D:
                fig.add_trace(go.Scattergl(
                    x=x_coords,
                    y=y_coords,
                    mode='markers',
                    marker=dict(
                        size=self.node_size,
                        color=colors
                    ),
                    name='Addresses',
                    showlegend=True,
                    hoverinfo='skip',
                    text=ids
                ))
            else:
                fig.add_trace(go.Scatter(
                    x=x_coords,
                    y=y_coords,
                    mode='markers',
                    marker=dict(
                        size=self.node_size,
                        color=colors,
                        line=dict(
                            color=VISUALIZATION_CONFIG['marker_border_color'],
                            width=VISUALIZATION_CONFIG['marker_border_width']
                        )
                    ),
                    name='Addresses',
                    showlegend=True,
                    hovertemplate=f'<b>{title}</b><br>ID: %{{text}}<br>X: %{{x}}<br>Y: %{{y}}<extra></extra>',
                    text=ids
                ))

        # Stations 그리기 - 대량일 경우 샘플링
        if stations and ('stations' in self.selected_components):
            sampled_stations = self._sample_list(stations, MAX_2D_STATIONS)
            x_coords = [station['pos']['x'] for station in sampled_stations]
            y_coords = [station['pos']['y'] for station in sampled_stations]
            ids = [station['id'] for station in sampled_stations]
            names = [station['name'] for station in sampled_stations]
            ports = [station['port'] for station in sampled_stations]

            if USE_WEBGL_2D:
                fig.add_trace(go.Scattergl(
                    x=x_coords,
                    y=y_coords,
                    mode='markers',
                    marker=dict(
                        size=self.node_size+1,
                        color='#FFD700',
                        symbol='diamond'
                    ),
                    name='Stations',
                    showlegend=True,
                    hoverinfo='skip',
                    text=ids
                ))
            else:
                fig.add_trace(go.Scatter(
                    x=x_coords,
                    y=y_coords,
                    mode='markers',
                    marker=dict(
                        size=self.node_size+1,  # Stations는 Addresses보다 약간 크게
                        color='#FFD700',  # 금색
                        symbol='diamond',  # 다이아몬드 모양
                        line=dict(
                            color='#FF8C00',  # 진한 주황색 테두리
                            width=1
                        )
                    ),
                    name='Stations',
                    showlegend=True,
                    hovertemplate=f'<b>Station</b><br>ID: %{{text}}<br>Name: %{{customdata[0]}}<br>Port: %{{customdata[1]}}<br>X: %{{x}}<br>Y: %{{y}}<extra></extra>',
                    text=ids,
                    customdata=list(zip(names, ports))
                ))

        # 레이아웃 설정
        fig.update_layout(
            title=title,
            width=self.visualization_width,
            height=self.visualization_height,
            showlegend=True,
            hovermode=VISUALIZATION_CONFIG['hover_mode'],
            legend=VISUALIZATION_CONFIG['legend_position'],
            plot_bgcolor='white',
            xaxis=dict(title='X 좌표', showgrid=True, gridcolor='lightgray'),
            yaxis=dict(title='Y 좌표', showgrid=True, gridcolor='lightgray'),
            uirevision='oht_keep_view'
        )

        # OHT 애니메이션 트레이스 추가 (선택적)
        if self.enable_oht:
            # Overlap에서는 target_z=None, 개별 모드에서는 해당 z만 필터링
            positions = self._build_oht_positions('output_udp_data.log', target_z)
            # 프레임 수 상한/목표 길이에 따른 stride 적용
            MAX_OHT_FRAMES_2D = 1000
            if positions and len(positions) > MAX_OHT_FRAMES_2D:
                from math import ceil
                step = max(1, ceil(len(positions) / MAX_OHT_FRAMES_2D))
                positions = positions[::step]
            if positions:
                # 목표 재생 시간 기반 stride 추가 계산
                try:
                    target_frames = max(1, int((OHT_TARGET_DURATION_SEC * 1000) / max(1, OHT_FRAME_INTERVAL_MS_2D)))
                    if len(positions) > target_frames:
                        from math import ceil
                        dyn_stride = max(1, ceil(len(positions) / target_frames))
                        positions = positions[::dyn_stride]
                except Exception:
                    pass
                # 프레임 stride 적용 (더 빠르게 보이도록)
                if OHT_FRAME_STRIDE > 1:
                    positions = positions[::OHT_FRAME_STRIDE]
                x0, y0 = positions[0]
                oht_trace_index = len(fig.data)
                if USE_WEBGL_2D:
                    fig.add_trace(go.Scattergl(
                        x=[x0], y=[y0], mode='markers',
                        marker=dict(size=(self.node_size + 2) * 2, color='#00AAAA'),
                        name='OHT', showlegend=True
                    ))
                else:
                    fig.add_trace(go.Scatter(
                        x=[x0], y=[y0], mode='markers',
                        marker=dict(size=(self.node_size + 2) * 2, color='#00AAAA'),
                        name='OHT', showlegend=True
                    ))
                if USE_JS_RESTYLE_ANIMATION:
                    # JS 타이머로 마지막 트레이스 좌표만 업데이트 (모든 프레임 표현에 유리)
                    try:
                        import json as _json
                        coords_js = _json.dumps(positions)
                        div_id = f"oht2d_div"
                        post_script = f"""
                        var gd = document.getElementById('{div_id}');
                        var coords = {coords_js};
                        var i = 0;
                        function step(){{
                          if(!gd || !gd.data || gd.data.length===0) {{ setTimeout(step, {OHT_FRAME_INTERVAL_MS_2D}); return; }}
                          var p = coords[i % coords.length];
                          Plotly.restyle(gd, {{x: [[p[0]]], y: [[p[1]]]}}, [gd.data.length-1]);
                          i++;
                          setTimeout(step, {OHT_FRAME_INTERVAL_MS_2D});
                        }}
                        step();
                        """
                        fig._post_script = post_script
                        fig._div_id = div_id
                    except Exception:
                        pass
                else:
                    frames = []
                    for i, (x, y) in enumerate(positions):
                        frames.append(go.Frame(data=[go.Scatter(x=[x], y=[y])], traces=[oht_trace_index], name=f"frame_{i}"))
                    fig.frames = frames
                    fig.update_layout(
                        updatemenus=[dict(type='buttons', showactive=False, y=0, x=0,
                                          buttons=[
                                              dict(label='Play', method='animate',
                                                   args=[None, {'frame': {'duration': OHT_FRAME_INTERVAL_MS_2D, 'redraw': False}, 'transition': {'duration': 0}, 'fromcurrent': True, 'mode': 'immediate', 'repeat': True}]),
                                              dict(label='Pause', method='animate', args=[[None], {'frame': {'duration': 0, 'redraw': False}, 'mode': 'immediate'}])
                                          ])],
                        sliders=[dict(active=0, steps=[dict(method='animate', args=[[f"frame_{i}"], {'mode': 'immediate', 'frame': {'duration': 0, 'redraw': False}, 'transition': {'duration': 0}}], label=str(i)) for i in range(len(frames))])]
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
    
    def create_visualizations(self):
        """전체 시각화 생성"""
        print("🚀 시각화를 시작합니다...")
        
        if not self.load_layout_data():
            return False

        self.print_statistics(self.addresses, "전체 Addresses", "addresses")
        self.print_statistics(self.lines, "전체 Lines", "lines")
        self.print_statistics(self.stations, "전체 Stations", "stations")

        addresses_z6022, lines_z6022, stations_z6022 = self.filter_data_by_z(Z_VALUES['z6022'], include=True)
        addresses_z4822, lines_z4822, stations_z4822 = self.filter_data_by_z(Z_VALUES['z4822'], include=True)
        addresses_z0, lines_z0, stations_z0 = self.filter_data_by_z(Z_VALUES['z0'], include=True)

        # 선택된 레이어만 반영하여 표시
        selected_labels = self.selected_z_values or []  # ['z6022','z4822',...]
        if not selected_labels:
            print("⚠️ 선택된 레이어가 없습니다. 출력 생략")
            return False

        # 선택된 레이어 데이터만 수집
        filtered_by_layer = []  # (label, z_value, addresses, lines, stations)
        for label in selected_labels:
            if label not in Z_VALUES:
                continue
            z_val = Z_VALUES[label]
            a, l, s = self.filter_data_by_z(z_val, include=True)
            filtered_by_layer.append((label, z_val, a, l, s))

        if self.overlap_visualization:
            # 하나의 창에 선택된 레이어를 겹쳐서 표시
            all_a, all_l, all_s = [], [], []
            for _, _, a, l, s in filtered_by_layer:
                all_a.extend(a)
                all_l.extend(l)
                all_s.extend(s)
            self.enable_oht = True
            title = "Layout Visualization - Overlap (" + ", ".join(lbl.upper() for lbl, _, _, _, _ in filtered_by_layer) + ")"
            fig_overlap = self.create_visualization(all_a, all_l, title, all_s, target_z=None)
            self._show_figure(fig_overlap, filename_prefix='2d_overlap')
        else:
            # 선택된 각 레이어를 별도 창으로 표시
            for label, z_val, a, l, s in filtered_by_layer:
                if not (a or l or s):
                    continue
                self.enable_oht = True
                fig_ind = self.create_visualization(a, l, f"Layout Visualization - {label.upper()}", s, target_z=z_val)
                self._show_figure(fig_ind, filename_prefix=f"2d_{label}")

        print("✅ 시각화가 완료되었습니다!")
        return True

    def _show_figure(self, fig, filename_prefix: str = "2d_layout"):
        try:
            div_id = getattr(fig, '_div_id', f"{filename_prefix}_div")
            post_script = getattr(fig, '_post_script', None)
            html = pio.to_html(fig, include_plotlyjs='cdn', auto_play=not bool(post_script), full_html=True, div_id=div_id, post_script=post_script)
            out_path = Path.cwd() / f"{filename_prefix}.html"
            with open(out_path, 'w', encoding='utf-8') as f:
                f.write(html)
            webbrowser.open(f"file://{out_path}")
        except Exception:
            fig.show()